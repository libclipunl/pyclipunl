# coding=utf-8
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import urlparse
import cookielib
import sys

SERVER = "https://clip.unl.pt"
LOGIN = "/utente/eu"
ALUNO = "/utente/eu/aluno"
ANO_LECTIVO = ALUNO + "/ano_lectivo"
UNIDADES = ANO_LECTIVO + "/unidades"
DOCUMENTOS = UNIDADES + "/unidade_curricular/actividade/documentos"

ENCODING = "iso-8859-1"

REQ_COUNT = 0
URL_DEBUG = False

PARAMS = {
    "unit": unicode("unidade", ENCODING),
    "cu_unit": unicode("unidade_curricular", ENCODING),
    "year": unicode("ano_lectivo", ENCODING),
    "period": unicode("per\xedodo_lectivo", ENCODING),
    "period_type": unicode("tipo_de_per\xedodo_lectivo", ENCODING),
    "student": unicode("aluno", ENCODING),
    "doctype": unicode("tipo_de_documento_de_unidade", ENCODING)
}

DOC_TYPES = {
    "0ac": unicode("Acetatos", "utf-8"),
    "1e": unicode("Problemas", "utf-8"),
    "2tr": unicode("Protocolos", "utf-8"),
    "3sm": unicode("Seminários", "utf-8"),
    "ex": unicode("Exames", "utf-8"),
    "t": unicode("Testes", "utf-8"),
    "ta": unicode("Textos de Apoio", "utf-8"),
    "xot": unicode("Outros", "utf-8")
}

class ClipUNLException(Exception):
    pass

class NotLoggedIn(ClipUNLException):
    pass

class InexistentYear(ClipUNLException):
    pass

class PageChanged(ClipUNLException):
    pass

class InvalidDocumentType(ClipUNLException):
    def __init__(self, doctype):
        self.value = doctype

    def __str__(self):
        return repr(self.value)

def get_soup(url, data=None):
    if URL_DEBUG:
        global REQ_COUNT
        REQ_COUNT = REQ_COUNT + 1
        print "[%02d] URL: %s%s " % (REQ_COUNT, SERVER, url)

    data_ = None
    if data != None:
        data_ = urllib.urlencode(data)

    html = urllib2.urlopen(SERVER + url, data_).read().decode(ENCODING)
    soup = BeautifulSoup(html)

    return soup

class ClipUNL:

    class Document:
        _cu = None
        _name = None
        _url = None
        _date = None
        _size = None
        _teacher = None

        def __init__(self, cu, name, url, date, size, teacher):
            self._cu = cu
            self._name = name
            self._url = url
            self._date = date
            self._size = size
            self._teacher = teacher

        def __str__(self):
            return "%s (by %s, created at %s)" % (self._name, self._teacher, self._date)

    class CurricularUnit:
        _student = None
        _url = None
        _name = None
        
        _id = None
        _year = None
        _period = None
        _period_type = None

        _documents = {}

        def __init__(self, student, name, url):
            self._student = student
            self._name = name
            self._url = url
            self._get_url_data(url)
        
        def get_student(self):
            return self._student

        def get_name(self):
            return self._name
        
        # FIXME: Cache document requests
        def get_documents(self, doctype=None):
            ret = []
            assert len(ret) == 0
            if doctype is None:
                for doctype_ in DOC_TYPES.keys():
                    ret = ret + self._get_documents(doctype_)

            else:
                ret = self._get_documents(doctype)
            
            return ret

        def _get_url_data(self, url):
            query = urlparse.urlparse(SERVER + url).query
            params = urlparse.parse_qs(query)

            self._id = params[PARAMS["unit"]][0]
            self._year = params[PARAMS["year"]][0]
            self._period = params[PARAMS["period"]][0]
            self._period_type = params[PARAMS["period_type"]][0]

        def _get_documents(self, doctype):
            docs = []

            data = urllib.urlencode({
                PARAMS["cu_unit"].encode(ENCODING): self._id,
                PARAMS["year"].encode(ENCODING): self._year,
                PARAMS["period"].encode(ENCODING): self._period,
                PARAMS["period_type"].encode(ENCODING): self._period_type,
                PARAMS["doctype"].encode(ENCODING): doctype,
                PARAMS["student"].encode(ENCODING): self._student.get_id()
            })
            url = DOCUMENTOS + "?" + data
            soup = get_soup(url)
            
            # FIXME: find better way to get all table rows
            all_imgs = soup.findAll("img", {"src" : "/imagem/geral/download.gif"})
            for img in all_imgs:
                anchor = img.parent.parent

                row = anchor.parent.parent
                all_td = row.findAll("td")

                docs.append(ClipUNL.Document(
                    self,
                    all_td[0].text,
                    anchor["href"],
                    all_td[2].text,
                    all_td[3].text,
                    all_td[4].text
                ))

            return docs
           
    class Person:
        _name = None
        _url = None
        _id = None
        _years = None

        def __init__(self, url, name):
            self._name = name
            self._url = url
            self._id = self._get_id(url)

        def get_name(self):
            return self._name
        
        def get_years(self):
            if self._years is None:
                self._years = self._get_years()

            return self._years.keys()

        def get_year(self, year):
            if self._years is None:
                self._years = self._get_years()
            
            year_data = self._years[year]
            if len(year_data) == 0:
                year_data = self._get_CUs(year)

            self._years[year] = year_data
            return year_data

        def get_id(self):
            return self._id

        def _get_id(self, url):
            query = urlparse.urlparse(SERVER + url).query
            params = urlparse.parse_qs(query)
            return params[PARAMS["student"]][0]

        def _get_CUs(self, year):
            data = urllib.urlencode({
                PARAMS["student"]: self._id,
                PARAMS["year"]: year
            })
            url = UNIDADES + "?" + data

            soup = get_soup(url)

            all_tables = soup.findAll("table", {"cellpadding" : "3"})
            uc_table = all_tables[2]

            all_anchors = uc_table.findAll("a")
            cus = []
            for anchor in all_anchors:
                cu_name = anchor.text
                href = anchor["href"]
                cus.append(ClipUNL.CurricularUnit(self, anchor.text, anchor["href"]))

            return cus

        def _get_years(self):
            data = urllib.urlencode({PARAMS["student"] : self._id})
            url = ANO_LECTIVO + "?" + data

            soup = get_soup(url)

            all_tables = soup.findAll("table", {"cellpadding" : "3"})
            years = {}
            if len(all_tables) == 2:
                # We got ourselves the list of all years
                # (if there is more than one year)
                years_table = all_tables[-1]
                years_anchors = years_table.findAll("a")
                for year in years_anchors:
                    href = year["href"]
                    query = urlparse.urlparse(SERVER + href).query
                    params = urlparse.parse_qs(query)
                    year = params["ano_lectivo"][0]
                    years[year] = []

            else:
                # There's only one year. Discover which year is it
                years_table = all_tables[1]
                years_anchors = years_table.findAll("a")
                year_text = years_anchors[0].text
                year = int(year_text.split("/")[0]) + 1
                years = { unicode(year) : [] }

            return years

    _logged_in = None
    _full_name = None

    _alunos = None

    def __init__(self):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

    def login(self, user, password):
        self._alunos = None
        self.logged_in = self._login(LOGIN, user, password)

    def is_logged_in(self):
        return self.logged_in

    def get_full_name(self):
        if self._full_name is None:
            raise ClipExceptNotLoggedIn()

        return self._full_name

    def get_alunos(self):
        if self._alunos is None:
            self._alunos = self._get_alunos()

        return self._alunos

    def _get_full_name(self, soup):
        all_strong = soup.findAll("strong")
        if (len(all_strong) == 1):
            return all_strong[0].text
        else:
            return False

    def _login(self, url, user, password):
        soup = get_soup(url, {
            "identificador": user,
            "senha": password
        })

        # Check if it is possible to get a full name
        self._full_name = self._get_full_name(soup)
        if (not self._full_name):
            return False

        return True

    def _get_alunos(self):
        soup = get_soup(ALUNO)
       
        all_tables = soup.body.findAll("table", {"cellpadding": "3"})
        if len(all_tables) != 1:
            self.error = True
            return False

        anchors = all_tables[0].findAll("a")

        if len(anchors) <= 0:
            self.error = True
            return None
        
        alunos = []
        for anchor in anchors:
            alunos.append(
                self.Person(anchor["href"], anchor.text)
            )

        return alunos


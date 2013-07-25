# coding=utf-8
"""
ClipUNL python scrapper library
Copyright (c) 2013 David Miguel de Araújo Serrano

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
"""
from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import urlparse
import cookielib

SERVER = "https://clip.unl.pt"
LOGIN = "/utente/eu"
ALUNO = "/utente/eu/aluno"
ANO_LECTIVO = ALUNO + "/ano_lectivo"
UNIDADES = ANO_LECTIVO + "/unidades"
DOCUMENTOS = UNIDADES + "/unidade_curricular/actividade/documentos"

ENCODING = "iso-8859-1"

#REQ_COUNT = 0
#URL_DEBUG = False

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
    """
    A ClipUNL exception. Every exception raised by ClipUNL
    are direct subclasses of this class
    """
    pass

class NotLoggedIn(ClipUNLException):
    """
    This exception is raised whenever an operation fails
    and login is required
    """
    pass

class InexistentYear(ClipUNLException):
    """
    Raised when there's no data for a specified year
    """
    def __init__(self, year):
        ClipUNLException.__init__(self)
        self.value = year

    def __str__(self):
        return repr(self.year)

class PageChanged(ClipUNLException):
    """
    Raised when the CLIP UNL webpage layout gets changed
    """
    pass

class InvalidDocumentType(ClipUNLException):
    """
    Raised when asking for documents which type is not
    listed on ClipUNL.DOC_TYPES
    """
    def __init__(self, doctype):
        ClipUNLException.__init__(self)
        self.value = doctype

    def __str__(self):
        return repr(self.value)

def _get_soup(url, data=None):
    """
    Give an URL, we'll return you a soup
    """
    #if URL_DEBUG:
    #    global REQ_COUNT
    #    REQ_COUNT = REQ_COUNT + 1
    #    print "[%02d] URL: %s%s " % (REQ_COUNT, SERVER, url)

    data_ = None
    if data != None:
        data_ = urllib.urlencode(data)

    html = urllib2.urlopen(SERVER + url, data_).read().decode(ENCODING)
    soup = BeautifulSoup(html)

    return soup

def _get_qs_param(url, param):
    """
    Extract parameter from the url's query string
    """
    query = urlparse.urlparse(SERVER + url).query
    params = urlparse.parse_qs(query)
    return params[param][0]

def _get_full_name(soup):
    """
    Given a soup originated from a CLIP UNL page, extract
    the user's full name. If the user is not logged in
    (and therefore impossible to get his/her name),
    this function returns False
    """
    all_strong = soup.findAll("strong")
    if (len(all_strong) == 1):
        return all_strong[0].text
    else:
        return False

class ClipUNL:
    """
    ClipUNL library.

    All the magic happens here.
    The first thing you must do before calling any other method
    is the login method.
    """

    class Document:
        """
        Describes a ClipUNL document.
        """
        _c_unit = None
        _name = None
        _url = None
        _date = None
        _size = None
        _teacher = None

        def __init__(self, c_unit,
                name, url, date, size, teacher):

            self._cunit = c_unit
            self._name = name
            self._url = url
            self._date = date
            self._size = size
            self._teacher = teacher

        def __str__(self):
            return unicode(self)

        def __unicode__(self):
            return "%s (by %s, created at %s)" % \
                (self._name, self._teacher, self._date)

        def get_curricular_unit(self):
            """
            Returns the curricular unit (a ClipUNL.CurricularUnit
            object) associated with this document.
            """
            return self._c_unit

        def get_name(self):
            return self._name

        def get_url(self):
            return self._url

        def get_size(self):
            return self._size

        def get_teacher(self):
            return self._teacher

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

        def __str__(self):
            return unicode(self)

        def __unicode__(self):
            return "%s (%s)" % (self.get_name(), self.get_year())
        
        def get_student(self):
            return self._student

        def get_name(self):
            return self._name

        def get_year(self):
            return self._year
        
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
            soup = _get_soup(url)
            
            # FIXME: find better way to get all table rows
            all_imgs = soup.findAll("img",
                    {"src" : "/imagem/geral/download.gif"})
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
            self._id = _get_qs_param(url, PARAMS["student"])

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
                year_data = self._get_curricular_units(year)

            self._years[year] = year_data
            return year_data

        def get_id(self):
            return self._id

        def get_url(self):
            return self._url


        def _get_curricular_units(self, year):
            data = urllib.urlencode({
                PARAMS["student"]: self._id,
                PARAMS["year"]: year
            })
            url = UNIDADES + "?" + data

            soup = _get_soup(url)

            all_tables = soup.findAll("table", {"cellpadding" : "3"})
            uc_table = all_tables[2]

            all_anchors = uc_table.findAll("a")
            cus = []
            for anchor in all_anchors:
                cu_name = anchor.text
                href = anchor["href"]
                cus.append(ClipUNL.CurricularUnit(self,
                    cu_name, href))

            return cus

        def _get_years(self):
            data = urllib.urlencode({PARAMS["student"] : self._id})
            url = ANO_LECTIVO + "?" + data

            soup = _get_soup(url)

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
        cjar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cjar))
        urllib2.install_opener(opener)

    def login(self, user, password):
        self._alunos = None
        self._logged_in = self._login(LOGIN, user, password)

    def is_logged_in(self):
        return self._logged_in

    def get_full_name(self):
        if self._full_name is None:
            raise NotLoggedIn()

        return self._full_name

    def get_alunos(self):
        if self._alunos is None:
            self._alunos = self._get_alunos()

        return self._alunos

    def _login(self, url, user, password):
        soup = _get_soup(url, {
            "identificador": user,
            "senha": password
        })

        # Check if it is possible to get a full name
        self._full_name = _get_full_name(soup)
        if (not self._full_name):
            return False

        return True

    def _get_alunos(self):
        soup = _get_soup(ALUNO)
       
        all_tables = soup.body.findAll("table", {"cellpadding": "3"})
        if len(all_tables) != 1:
            raise PageChanged()

        anchors = all_tables[0].findAll("a")

        if len(anchors) <= 0:
            raise PageChanged()
        
        alunos = []
        for anchor in anchors:
            alunos.append(
                self.Person(anchor["href"], anchor.text)
            )

        return alunos

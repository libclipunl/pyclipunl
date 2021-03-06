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
from bs4 import BeautifulSoup
import urllib
import urllib2
import urlparse
import cookielib

VERSION = "0.0.7"

SERVER = unicode("https://clip.unl.pt")
OBJECTO = unicode("/objecto")
LOGIN = unicode("/utente/eu")
ALUNO = unicode("/utente/eu/aluno")
ANO_LECTIVO = ALUNO + unicode("/ano_lectivo")
UNIDADES = ANO_LECTIVO + unicode("/unidades")
DOCUMENTOS = UNIDADES + \
        unicode("/unidade_curricular/actividade/documentos")
DL_IMAGE = unicode("/imagem/geral/download.gif")

ENCODING = "iso-8859-1"

#REQ_COUNT = 0
#URL_DEBUG = True

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

class NetworkError(ClipUNLException):
    """
    Raised when a network error.
    """
    def __init__(self, urlexcept):
        ClipUNLException.__init__(self)
        self.value = urlexcept

    def __str__(self):
        return str(self.value)

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
    
    try:
        html = urllib2.urlopen(SERVER + url, data_).read()
    except urllib2.URLError as urlexcept:
        raise NetworkError(urlexcept)

    soup = BeautifulSoup(html, from_encoding = ENCODING)

    return soup

def _get_qs_param(url, param):
    """
    Extract parameter from the url's query string
    """
    query = urlparse.urlparse(SERVER + url).query
    params = urlparse.parse_qs(query)
    return unicode(params[param][0])

def _get_full_name(soup):
    """
    Given a soup originated from a CLIP UNL page, extract
    the user's full name. If the user is not logged in
    (and therefore impossible to get his/her name),
    this function returns False
    """
    all_strong = soup.find_all("strong")
    return unicode(all_strong[0].text) \
            if (len(all_strong) == 1) else False

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
        _oid = None
        _c_unit = None
        _name = None
        _url = None
        _doctype = None
        _date = None
        _size = None
        _teacher = None

        def __init__(self, c_unit,
                name, url, doctype, date, size, teacher):
    
            self._c_unit = c_unit
            self._name = name
            self._doctype = doctype
            self._date = date
            self._size = size
            self._teacher = teacher

            self._get_url_data(url)

        def __str__(self):
            return unicode(self)

        def __unicode__(self):
            return "%s (by %s, created at %s)" % \
                (self.get_name(), self.get_teacher(), self.get_date())

        def get_curricular_unit(self):
            """
            Returns the curricular unit (a ClipUNL.CurricularUnit
            object) associated with this document.
            """
            return self._c_unit

        def get_name(self):
            """Returns the document's name"""
            return self._name

        def get_oid(self):
            """Returns the document's object ID"""
            return self._oid

        def get_url(self):
            """Returns the document's url"""
            return self._url

        def get_doctype(self):
            """Returns the document's doctype"""
            return self._doctype

        def get_doctype_desc(self):
            """Returns the printable document's doctype"""
            return DOC_TYPES[self.get_doctype()]

        def get_size(self):
            """Returns the string describing the document's size"""
            return self._size

        def get_teacher(self):
            """
            Returns the name of the teacher who uploaded
            the document
            """
            return self._teacher
        
        def get_date(self):
            """
            Returns the creation date of the document
            """
            return self._date

        def _get_url_data(self, url):
            """
            Extracts extra data contained in the url.
            This method is called once on the object initializer,
            and shouldn't be called.
            """
            oid = _get_qs_param(url, "oid")
            quoted_name = urllib.quote(self.get_name().encode("utf-8"))
            self._url = "%s%s?oid=%s&oin=%s" % \
                    (SERVER, OBJECTO, oid, quoted_name)
            self._oid = oid

    class CurricularUnit:
        """
        A class describing a curricular unit (more commonly known as a
        class, or subject)
        """
        
        _person = None
        _url = None
        _name = None
        
        _id = None
        _year = None
        _period = None
        _period_type = None

        _documents = {}
        _doctypes = None

        def __init__(self, person, name, url):
            self._person = person
            self._name = name
            self._url = url

            self._documents = {}
            self._doctypes = None

            self._get_url_data(url)

        def __str__(self):
            return unicode(self)

        def __unicode__(self):
            return "%s (%s)" % (self.get_name(), self.get_year())

        def get_id(self):
            """Returns the curricular unit's id"""
            assert(isinstance(self._id, unicode))
            return self._id
        
        def get_person(self):
            """Returns the student (person) who attends this class"""
            assert(isinstance(self._person, ClipUNL.Person))
            return self._person

        def get_name(self):
            """Returns the curricular unit's name"""
            assert(isinstance(self._name, unicode))
            return self._name

        def get_year(self):
            """Returns the curricular unit's year (as in, edition)"""
            assert(isinstance(self._year, unicode))
            return self._year

        def get_period(self):
            """Returns the curricular unit's period code"""
            assert(isinstance(self._period, unicode))
            return self._period

        def get_period_type(self):
            """Returns the curricular unit's period type code"""
            assert(isinstance(self._period_type, unicode))
            return self._period_type
        
        def get_documents(self, doctype=None):
            """
            Returns the curricular unit's associated documents.
            If doctype isn't specified, then all documents (of all types)
            will be returned.

            Valid document types are listed on ClipUNL.DOC_TYPES.keys().
            
            An array of ClipUNL.ClipUNL.Document objects will be returned.
            """
            return [self._get_documents(doctype_)
                    for (doctype_, count)
                    in self.get_doctypes.iteritems()
                    if count > 0] if doctype is None else \
                            self._get_documents(doctype)

        def get_doctypes(self):
            """
            Returns a dictonary, on which the keys are the available document
            types and the values are the count of those documents
            """

            doctypes = self._doctypes
            if doctypes is None:
                doctypes = {}
            else:
                return doctypes

            data = urllib.urlencode({
                PARAMS["cu_unit"].encode(ENCODING): self.get_id(),
                PARAMS["year"].encode(ENCODING): self.get_year(),
                PARAMS["period"].encode(ENCODING): self.get_period(),
                PARAMS["period_type"].encode(ENCODING): self.get_period_type(),
                PARAMS["student"].encode(ENCODING): self.get_person().get_id()
            })
            url = DOCUMENTOS + "?" + data
            soup = _get_soup(url)
            if soup.text == '':
                return {}

            all_tables = soup.find_all("table", {"cellpadding" : "3"})
            
            doc_types_table = all_tables[3]
            anchors = doc_types_table.find_all("a")

            # Leave it be, because the functional way would be messier...
            for anchor in anchors:
                text = anchor.text
                number = text[text.find("(")+1:text.find(")")]
                url = unicode(anchor.get("href"))

                doctype = _get_qs_param(url, PARAMS["doctype"])
                doctypes[doctype] = int(number)

            self._doctypes = doctypes
            return doctypes

        def _get_url_data(self, url):
            """Extracts data from a given URL"""
            query = urlparse.urlparse((SERVER + url)).query

            unit = PARAMS["unit"]
            year = PARAMS["year"]
            period = PARAMS["period"]
            period_type = PARAMS["period_type"]

            params = urlparse.parse_qs(query)

            try:
                self._id = params[unit][0]
                self._year = params[year][0]
                self._period = params[period][0]
                self._period_type = params[period_type][0]
            except Exception:
                raise PageChanged()

        def _get_documents(self, doctype):
            """
            Retrieve documents of a specified doctype.
            Please don't use this method. Use get_documents() instead.
            """
            docs = self._documents.get(doctype)
            if not docs is None:
                return docs
            else:
                docs = []

            data = urllib.urlencode({
                PARAMS["cu_unit"].encode(ENCODING): self.get_id(),
                PARAMS["year"].encode(ENCODING): self.get_year(),
                PARAMS["period"].encode(ENCODING): self.get_period(),
                PARAMS["period_type"].encode(ENCODING): self.get_period_type(),
                PARAMS["doctype"].encode(ENCODING): doctype,
                PARAMS["student"].encode(ENCODING): self.get_person().get_id()
            })
            url = DOCUMENTOS + "?" + data
            soup = _get_soup(url)
            if soup.text == '':
                return []
            
            # We get ourselves the table that suits our needs
            file_table = soup.find_all("table", {"cellpadding" : "2",
                "cellspacing" : "2", "border" : "0"})[0]
            
            # Then, get all its rows. Note that each row must have the
            # download gif image
            rows = [elem for elem in file_table.find_all("tr")
                    if len(elem.find_all("img", {"src" : DL_IMAGE})) == 1]
            
            # Finally transform all those rows into Document objects 
            docs = [ClipUNL.Document(
                    self,
                    all_td[0].text,
                    anchor["href"],
                    doctype,
                    all_td[2].text,
                    all_td[3].text,
                    all_td[4].text)
                    
                    for all_td, anchor
                    in [(row.find_all("td"), row.find_all("a")[0])
                        for row in rows]]

            # Gotta love list comprehensions
            # What programming Scala can do to a sane man...

            self._documents[doctype] = docs
            return docs
           
    class Person:
        """
        A class describing a Person.
        On Clip UNL a user can be many persons.
        """
        _role = None
        _url = None
        _id = None
        _years = None

        def __init__(self, url, role):
            assert(isinstance(url, unicode))
            assert(isinstance(role, unicode))

            self._role = role
            self._url = url
            self._id = _get_qs_param(url, PARAMS["student"])

        def __str__(self):
            return unicode(self)

        def __unicode__(self):
            return "%s (id: %s)" % (self.get_role(), self.get_id())

        def get_role(self):
            """
            Returns the person's role. 
            """
            assert(isinstance(self._role, unicode))
            return self._role
        
        def get_years(self):
            """
            Returns an array containing all the registered
            years for this person.
            """
            if self._years is None:
                self._years = self._get_years()

            return self._years.keys()

        def get_year(self, year):
            """
            Returns a list of CurricularUnit objects, that
            were lectured during a specified year.

            If there aren't curricular units for a specified
            year, the InexistentYear exception will be raised.
            """
            assert(isinstance(year, unicode))
            if self._years is None:
                self._years = self._get_years()
            
            if not year in self._years.keys():
                raise InexistentYear(year)

            year_data = self._years[year]
            if len(year_data) == 0:
                year_data = self._get_curricular_units(year)

            self._years[year] = year_data
            return year_data

        def get_id(self):
            """Returns the person's id"""
            assert(isinstance(self._id, unicode))
            return self._id

        def get_url(self):
            """Returns the person's Clip UNL URL"""
            assert(isinstance(self._url, unicode))
            return self._url

        def _get_curricular_units(self, year):
            """
            Get's a list of curricular units for a specified year.
            Please don't use this method. Use get_year() instead.
            """
            assert(isinstance(year, unicode))

            data = urllib.urlencode({
                PARAMS["student"]: self._id,
                PARAMS["year"]: year
            })
            url = UNIDADES + "?" + data

            soup = _get_soup(url)
            if soup.text == "":
                return []

            all_tables = soup.find_all("table", {"cellpadding" : "3"})
            uc_table = all_tables[2]

            all_anchors = uc_table.find_all("a")

            return [ClipUNL.CurricularUnit(self, cu_name, href)
                    for (cu_name, href)
                    in [(unicode(anchor.text), unicode(anchor["href"]))
                        for anchor in all_anchors]]


        def _get_years(self):
            """
            Returns a list of all the years this person is registered to.
            Please don't use this method. Use get_years instead.
            """
            data = urllib.urlencode({PARAMS["student"] : self._id})
            url = ALUNO + "?" + data

            soup = _get_soup(url)
            if soup.text == "":
                return {}

            all_tables = soup.find_all("table", {"cellpadding" : "3"})
            try:
                year_table = [elem for elem in all_tables
                        # using startswith because of the ortographic agreement...
                        if elem.find_all("a")[0].text.startswith("Ano")][0]

                anchors = year_table.find_all("a")[1:]
                if len(anchors) == 0:
                    raise PageChanged()

                years = {}
                for anchor in anchors:
                    href = anchor["href"]
                    query = urlparse.urlparse(SERVER + href).query
                    params = urlparse.parse_qs(query)
                    year = params[PARAMS["year"]][0]
                    years[year] = []

                return years


            except IndexError:
                raise PageChanged()

    _logged_in = None
    _full_name = None

    _people = None

    def __init__(self):
        cookiejar = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
        urllib2.install_opener(opener)

        self._cookiejar = cookiejar

    def login(self, user, password):
        """
        Logs into CLIP.

        This must be the first call to be made, before any other
        method call on an instance of a ClipUNL class.

        The NotLoggedIn exception will be raised if other
        methods are used, whithout loggin in first.

        Returns True is the login is successful, False otherwise.
        """
        self._people = None
        self._logged_in = self._login(LOGIN, user, password)

    def is_logged_in(self):
        """
        Checks if the user has logged in successfully.
        """
        return self._logged_in

    def get_full_name(self):
        """
        Returns the users full name
        """
        if self._full_name is None:
            raise NotLoggedIn()

        return self._full_name

    def get_people(self):
        """
        Returns the list of people this user represents.

        A user can be a masters student, while he/she
        has completed his/her baccalaureate.

        There's only support for students at the moment.
        """
        if not self.is_logged_in():
            raise NotLoggedIn()

        if self._people is None:
            self._people = self._get_people()

        return self._people

    def get_cookiejar(self):
        """
        Returns the cookie jar in use.
        """
        return self._cookiejar

    def _login(self, url, user, password):
        """
        Does the actual login on the system, with a provided
        user and password.

        Please don't use this method. Use login instead.
        """
        assert(isinstance(url, unicode))
        assert(isinstance(user, unicode))
        assert(isinstance(password, unicode))

        soup = _get_soup(url, {
            "identificador": user,
            "senha": password
        })

        # Check if it is possible to get a full name
        self._full_name = _get_full_name(soup)
        if (not self._full_name):
            return False

        return True

    def _get_people(self):
        """
        Returns a list of people represented by this user.
        Please don't use this method. Use get_people instead.
        """
        soup = _get_soup(LOGIN)
        if soup.text == '':
            return []
       
        all_tables = soup.body.find_all("table", {"cellpadding": "3"})
        try:
            aluno_table = [elem for elem in all_tables \
                if unicode(elem.find_all("a")[0].text) == unicode("Aluno")][0]

            anchors = aluno_table.find_all("a")[1:]
            if len(anchors) == 0:
                raise PageChanged()

            return [self.Person(unicode(anchor["href"]),
                unicode(anchor.text)) \
                for anchor in anchors]

        except IndexError:
            raise PageChanged()


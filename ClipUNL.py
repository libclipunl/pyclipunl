from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import urlparse
import cookielib

SERVER = "https://clip.unl.pt"
LOGIN = SERVER + "/utente/eu"
ALUNO = SERVER + "/utente/eu/aluno"
ANO_LECTIVO = ALUNO + "/ano_lectivo"
UNIDADES = ANO_LECTIVO + "/unidades"

class ClipUNL:

    class CurricularUnit:
        def __init__(self, student_id, year):
            self._load(year)

        def _load(self):
            pass

    class Person:
        name = ""
        url = ""
        id = ""
        years = {}

        def __init__(self, url, name):
            self.name = name
            self.url = url
            self.id = self._get_id(url)
            self._loadyears()
            self._loadCUs()

        def _get_id(self, url):
            query = urlparse.urlparse(SERVER + url).query
            params = urlparse.parse_qs(query)
            return params["aluno"][0]

        def _loadCU(self, year):
            data = urllib.urlencode({
                "aluno": self.id,
                "ano_lectivo": year
            })
            url = UNIDADES + "?" + data

            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup(html)

            all_tables = soup.findAll("table", {"cellpadding" : "3"})
            uc_table = all_tables[2]

            all_anchors = uc_table.findAll("a")
            for anchor in all_anchors:
                print anchor.text


        def _loadCUs(self):
            for year in self.years:
                self._loadCU(year)

        def _loadyears(self):
            data = urllib.urlencode({"aluno" : self.id})
            url = ANO_LECTIVO + "?" + data
            print "URL: " + url

            html = urllib2.urlopen(url).read()
            soup = BeautifulSoup(html)

            all_tables = soup.findAll("table", {"cellpadding" : "3"})
            self.years = {}
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
                    self.years[year] = []

            else:
                # There's only one year. Discover which year is it
                years_table = all_tables[1]
                years_anchors = years_table.findAll("a")
                year_text = years_anchors[0].text
                year = int(year_text.split("/")[0]) + 1
                self.years[unicode(year)] = []

    logged_in = False
    error = False
    full_name = ""

    alunos = []

    def __init__(self, user, password):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        self.logged_in = self._login(user, password)

    def _get_full_name(self, soup):
        all_strong = soup.findAll("strong")
        if (len(all_strong) == 1):
            return all_strong[0].text
        else:
            return False

    def _login(self, user, password):
        data = urllib.urlencode({
            "identificador": user,
            "senha": password
        })

        html = urllib2.urlopen(ALUNO, data).read()
        soup = BeautifulSoup(html)

        # Check if it is possible to get a full name
        self.full_name = self._get_full_name(soup)
        if (not self.full_name):
            return False

        all_tables = soup.body.findAll("table", {"cellpadding": "3"})
        if len(all_tables) != 1:
            self.error = True
            return False

        anchors = all_tables[0].findAll("a")

        if len(anchors) <= 0:
            self.error = True
            return False

        for anchor in anchors:
            self.alunos.append(
                self.Person(anchor["href"], anchor.text)
            )

        return True


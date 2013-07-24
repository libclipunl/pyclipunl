from BeautifulSoup import BeautifulSoup
import urllib
import urllib2
import cookielib

class ClipUNL:

    SERVER="https://clip.unl.pt"
    LOGIN="/utente/eu"

    logged_in = False
    error = False
    full_name = ""

    student_ids = []

    def __init__(self, user, password):
        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        urllib2.install_opener(opener)

        self.logged_in = self._login(user, password)


    def _login(self, user, password):
        data = urllib.urlencode({
            "identificador": user,
            "senha": password
        })

        html = urllib2.urlopen(self.SERVER + self.LOGIN, data).read()
        soup = BeautifulSoup(html)

        all_strong = soup.findAll("strong")
        if (len(all_strong) == 1):
            self.full_name = all_strong[0].text
        else:
            return False

        return True

    def _load_data():
        all_tables = soup.body.findAll("table", {"cellpadding": "3"})

        # Find table with Aluno as its heading
        for table in all_tables:
            anchors = table.findAll("a")
            if (len(anchors) > 0 and anchors[0].text == "Aluno"):
                break

        if len(anchor) <= 1:
            self.error = True
            return False

        for anchor in anchors[1:]:
            self.student_ids.append({
                "url" : anchor["href"],
                "name" : anchor.text
            })
        
        return True


from ClipUNL import ClipUNL
import json

f = open("login.json")
data = json.load(f)
f.close()

clip = ClipUNL()
clip.login(data["login"], data["password"])

if clip.is_logged_in():
    print "Welcome %s" % (clip.get_full_name(),)
    alunos = clip.get_alunos()
    for person in alunos:
        years = person.get_years()
        print "\t%s (%d year[s])" % (person.get_name(), len(years))

        for year in years:
            year_cus = person.get_year(year)
            print "\t\t%s" % (year,)
            for cu in year_cus:
                print "\t\t\t%s" % (cu.get_name())
else:
    print "You failed to login"


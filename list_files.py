#!/usr/bin/env python2

from ClipUNL import ClipUNL
from ClipUNL import DOC_TYPES
import json
import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

f = open("config.json")
data = json.load(f)
f.close()

clip = ClipUNL()
clip.login(data["login"], data["password"])

if clip.is_logged_in():
    print ("Welcome %s") % (clip.get_full_name(),)
    alunos = clip.get_alunos()
    for person in alunos:
        years = person.get_years()
        print "%s (%d year[s])" % (person.get_name(), len(years))

        for year in years:
            year_cus = person.get_year(year)
            print "  %s Curricular Units:" % (year,)
            for cu in year_cus:
                print "    %s" % (cu,)
                for doctype in DOC_TYPES.keys():
                    docs = cu.get_documents(doctype)
                    n = len(docs)
                    if n > 0:
                        print "      [%s] (%d):" % (DOC_TYPES[doctype], n)
                        for doc in docs:
                            print "        * %s" % (doc,)

else:
    print "You failed to login"


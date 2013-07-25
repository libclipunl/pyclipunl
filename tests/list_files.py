#!/usr/bin/env python2
# coding=utf-8
"""
CLIP UNL file listing 

This file is part of the ClipUNL python scrapper library
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

from ClipUNL import ClipUNL
from ClipUNL import DOC_TYPES
import json
import sys
import codecs

CONF_FILE = "config.json"

def main():
    """The main entry point"""
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

    conf_file = open(CONF_FILE)
    conf = json.load(conf_file)
    conf_file.close()

    clip = ClipUNL()
    clip.login(conf["login"], conf["password"])

    if clip.is_logged_in():
        print ("Welcome %s") % (clip.get_full_name(),)
        people = clip.get_people()
        for person in people:
            years = person.get_years()
            print "%s (%d year[s])" % (person.get_role(), len(years))

            for year in years:
                year_cus = person.get_year(year)
                print "  %s Curricular Units:" % (year,)
                for c_unit in year_cus:
                    print "    %s" % (c_unit,)
                    for doctype in DOC_TYPES.keys():
                        docs = c_unit.get_documents(doctype)
                        docs_len = len(docs)
                        if docs_len > 0:
                            print "      [%s] (%d):" % (DOC_TYPES[doctype],
                                    docs_len)
                            for doc in docs:
                                print "        * %s" % (doc,)

    else:
        print "You failed to login"

if __name__ == "__main__":
    main()

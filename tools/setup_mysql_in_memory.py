#!/usr/bin/python
# -*- coding: utf-8  -*-
"""

Script to read an xml dump of Wikipedia and write it to an SQL table 

find the dumps here: 

https://dumps.wikimedia.org/dewiki/latest/

""" 

import MySQLdb
import spellcheck
import wikipedia as pywikibot
import pagegenerators
import BlacklistChecker
import sys
import xmlreader
from spellcheck_wordlist import BlacklistSpellchecker

# xml_dump = "../data/dewiki-latest-pages-articles.xml.bz2"
# table = "hroest.countedwords_20151029"
xml_dump = sys.argv[1]
table = sys.argv[2]

print "Working with file", xml_dump
print "Working with table", table

sp = BlacklistSpellchecker()
wikidump = xmlreader.XmlDump(xml_dump)
gen = wikidump.parse()

res = {}
for i, page in enumerate(gen):
    if not page.ns == '0': 
        continue

    if i % 100 == 0:
        print i, page.title, "unique words", len(res)

    prepare = [ [page.id, p.encode('utf8')] for p in sp.spellcheck_blacklist(page.text, {}, return_for_db=True)]
    for p in prepare:
        tmp = res.get( p[1], 0)
        res[ p[1] ] = tmp+1

db = MySQLdb.connect(read_default_file="~/.my.cnf.hroest")
db.autocommit(True)
cursor = db.cursor()

cursor.execute( """create table %s (
    occurence int,
    smallword varchar(255)
) ENGINE = MYISAM; """ % table)

insert_table = "insert into %s" % table
for k,v in res.iteritems():
    tmp = cursor.execute( insert_table + " (occurence, smallword) values (%s,%s)", (v,k) )


cursor.execute( """alter table %s add index(occurence) """ % table)
cursor.execute( """alter table %s add index(smallword) """ % table)

"""
File "setup_mysql_in_memory.py", line 59, in <module>
cursor.execute( ""alter table %s add index(occurence) "" % table)
         File "/usr/lib/python2.7/dist-packages/MySQLdb/cursors.py", line 174, in execute
             self.errorhandler(self, exc, value)
               File "/usr/lib/python2.7/dist-packages/MySQLdb/connections.py", line 36, in defaulterrorhandler
                   raise errorclass, errorvalue
                   _mysql_exceptions.ProgrammingError: (1064, "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near 'insert into wikiwords.countedwords_20160111 add index(occurence)' at line 1")



"""

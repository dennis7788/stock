# -*- coding: utf-8 -*-  
import MySQLdb

def connectTODB():
    db = MySQLdb.connect(host="192.168.1.108", user="dennisf", passwd="dennis", db="finance",charset="utf8")
    db.autocommit(1)
    cursor = db.cursor()

    return cursor
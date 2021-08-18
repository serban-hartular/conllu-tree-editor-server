import sqlite3
from sqlite3 import Error, Connection
import datetime

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    return conn

def execute(conn : Connection, command : str):
    try:
        c = conn.cursor()
        c.execute(command)
    except Error as e:
        print(e)


create_table_sql = """
    CREATE TABLE IF NOT EXISTS sentences (
	id integer PRIMARY KEY,
	conllu text NOT NULL,
	meta text,
	tstamp text,
	ip text,
	is_conllu_correct int,
	is_conllu_complete int,
	ellipsis_type text,
	comment text
    );
    """

def insert_sentence(conn, conllu : str,
                   meta='', tstamp='', ip='', is_conllu_correct=1, is_conllu_complete=1,
                   ellipsis_type='', comment='', sentence_src = ''):
    # """
    # :param conn:
    # :param project:
    # :return: project id
    # """
    if not tstamp:
        tstamp = str(datetime.datetime.now())
    if not ip:
        ip = 'localhost'
        
    sql = ''' INSERT INTO sentences(conllu,meta,tstamp,ip,is_conllu_correct,is_conllu_complete,ellipsis_type,comment,sentence_src)
              VALUES(?,?,?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    [conllu, ellipsis_type, comment, sentence_src] = \
        [s.encode('utf8') for s in [conllu, ellipsis_type, comment, sentence_src]]
    # print(conllu)
    cur.execute(sql, (conllu,
                      meta,tstamp,ip,is_conllu_correct,is_conllu_complete,ellipsis_type,comment,sentence_src))
    conn.commit()
    return cur.lastrowid

def fetch_sentence(conn : Connection, id : int = None):
    sql_str = "SELECT * FROM sentences"
    if id: sql_str += " WHERE id=?"
    cur = conn.cursor()
    cur.execute(sql_str, (id,) if id else ())
    rows = cur.fetchall()
    return rows

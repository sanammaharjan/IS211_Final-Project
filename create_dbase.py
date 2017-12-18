import sqlite3
def db_connection():
    try:
        con = sqlite3.connect('blog.db')
        file = open('schema.sql','r')
        query = file.read()
        con.executescript(query)
        con.commit()

    except sqlite3.Error, e:
        if con:
            con.rollback()
        print 'There is error %s:' %e.args[0]
        # sys.exit(1)

    finally:
        if con:
            con.close()

if __name__ == '__main__':
    db_connection()
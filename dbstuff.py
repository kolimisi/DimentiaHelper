
import sqlite3 as sql

conn = sql.connect('hackathon.db')
print "Opened database successfully";

conn.execute('CREATE TABLE visitors (name TEXT, relation TEXT, info TEXT)')
print("Table created successfully");
#conn.close()




import sqlite3 as sql

name = "Zac Reid"
relation = "Grandson"
info = "In grad school at Wright State"

conn = sql.connect('hackathon.db')
cur = conn.cursor()
cur.execute("INSERT INTO visitors (name,relation,info) VALUES (?,?,?)",(name,relation,info) )
conn.commit()
conn.close()






import sqlite3 as sql

con = sql.connect("hackathon.db")
con.row_factory = sql.Row

name = "Zac Reid"
cur = con.cursor()
cur.execute("select * from visitors where name = '{}'".format(name))

rows = cur.fetchall();
print(rows)





import sqlite3 as sql

conn = sqlite3.connect('database.db')
print "Opened database successfully";

conn.execute('CREATE TABLE students (name TEXT, addr TEXT, city TEXT, pin TEXT)')
print "Table created successfully";
conn.close()
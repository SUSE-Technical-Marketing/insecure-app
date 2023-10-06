#!/usr/bin/env python
# Initialize the database.

# Define the database type
dbtype='sqlite3'

# In the future we can use other types
if dbtype == 'sqlite3':
  import sqlite3
  conn = sqlite3.connect('database.db')

# Execute the SQL statements in the schema file
with open('static/schema.sql') as file:
    conn.executescript(file.read())


cursor = conn.cursor()

# We instert some default values
cursor.execute("INSERT INTO photos (title, description, url) VALUES (?, ?, ?)", ('Mountain Views', 'A sea of mountains', 'mountains.jpg')

cursor.execute("INSERT INTO photos (title, description, url) VALUES (?, ?, ?)", ('Sandy Beach', 'The picture of a sandy beach', 'beach.jpg')

conn.commit()
conn.close()

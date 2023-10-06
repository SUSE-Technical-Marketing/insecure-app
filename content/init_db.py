#!/usr/bin/env python
# Initialize the database.
import yaml 
import os


config_settings=['ADMIN_USER','IMAGES_LOCATION','APP_NAME','DB_FILE']
version=''
# read the config file
if 'CONFIG_FILE' in os.environ:
  config_file = os.environ['CONFIG_FILE']
else:
  config_file = 'myconf.yml'

with open('version', 'r') as file:
  version = file.readlines()[0]


with open(config_file, 'r') as file:
  cfg = yaml.safe_load(file)

if cfg['DB_TYPE'] == 'sqlite3':
  import sqlite3
  connection = sqlite3.connect('database.db')
  cursor = connection.cursor()
  # Execute the SQL statements in the schema file
  with open('static/schema.' + cfg['DB_TYPE'] + '.sql') as file:
    connection.executescript(file.read())
  # We insert some default values
  cursor.execute("INSERT INTO photos (title, description, url) VALUES (?, ?, ?)",
            ('Mountain Views', 'A sea of mountains', 'mountains.jpg')
            )
  cursor.execute("INSERT INTO photos (title, description, url) VALUES (?, ?, ?)",
            ('Sandy Beach', 'The picture of a sandy beach', 'beach.jpg')
            )

elif cfg['DB_TYPE'] == 'mysql':
  import MySQLdb
  connection = MySQLdb.connect(cfg['DB_HOST'],cfg['DB_USER'],cfg['DB_PWD'])
  cursor = connection.cursor()
  cursor.execute("DROP DATABASE IF EXISTS photos;")
  cursor.execute("CREATE DATABASE photos;")
  cursor.execute("USE photos;")
  cursor.execute("DROP USER 'myadmin';")
  cursor.execute("CREATE USER 'myadmin'@'%' IDENTIFIED BY 'mypasswd';")
  cursor.execute("GRANT ALL PRIVILEGES ON *.* TO 'myadmin';")
  # Execute the SQL statements in the schema file
  with open('static/schema.' + cfg['DB_TYPE'] + '.sql') as file:
    cursor.execute(' '.join(file.readlines()))
  # We insert some default values
  cursor.execute("INSERT INTO photos (title, description, url) VALUES (%s, %s, %s)",
            ('Mountain Views', 'A sea of mountains', 'mountains.jpg')
            )
  cursor.execute("INSERT INTO photos (title, description, url) VALUES (%s, %s, %s)",
            ('Sandy Beach', 'The picture of a sandy beach', 'beach.jpg')
            )

connection.commit()
connection.close()



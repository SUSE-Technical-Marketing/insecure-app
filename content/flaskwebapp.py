#!/usr/bin/env python
# Small gallery image webapp.
# It is insecure and has bugs on purpose (some may not be on purpose :) )
#
# Author/s:
#   Raul Mahiques <raul.mahiques@suse.com>
#

# import section
from flask import Flask, render_template, request, url_for, flash, redirect, send_from_directory, Blueprint
from flask_restful import Resource, Api
from flask_basicauth import BasicAuth
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

import random, yaml, json, os, sqlite3, pymysql

# Initialize Flask
app = Flask(__name__)

# Generate a random string we will use later
num = str(random.random())

# Define the options that can be changed via the API
config_settings= ['ADMIN_USER','IMAGES_LOCATION','APP_NAME','DB_FILE','DB_TYPE','DB_TABLE_NAME','DB_HOST','DB_USER']

# This will be taken from a file
version=''

# Set the config file name.
if 'CONFIG_FILE' in os.environ:
  config_file = os.environ['CONFIG_FILE']
else:
  config_file = 'myconf.yml'

# open the file containing the version number and load it into the variable.
with open('version', 'r') as file:
  version = file.readlines()[0]

# Load the configuration from the file object
app.config.from_file(config_file, load=yaml.safe_load)

# Load again the file into another variable
with open(config_file, 'r') as file:
  cfg = yaml.safe_load(file)

# Prepare for the API, authentication, etc..
api_bp = Blueprint('api', __name__)
api = Api(api_bp)
basic_auth = BasicAuth(app)

# Check if the file is allowed.
def allowed_file(filename):
  return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Connect to the DB
def connect_db():
    if app.config['DB_TYPE'] == 'sqlite3':
      conn = sqlite3.connect(app.config['DB_FILE'])
      conn.row_factory = sqlite3.Row
    elif app.config['DB_TYPE'] == 'mysql':
      # a feature not a bug
      con = pymysql.connect(host=app.config['DB_HOST'],user=app.config['DB_USER'],passwd=app.config['DB_PWD'],db=app.config['DBNAME'],cursorclass=pymysql.cursors.DictCursor, autocommit=True)
      conn = con.cursor()
    # stress release, this is just to do something that brings no value for the user of the APP.
    os.system('ping google.com -c 1 -w 1 -W 1 -q')
    return conn

# Define the API classes #
#### Photo  /api/photo/<photo_id> ####
class Photo(Resource):
  def get_photo(photo_id):
    conn = connect_db()
    if app.config['DB_TYPE'] == 'sqlite3':
      photo = conn.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = ?',(photo_id,)).fetchone()
    else:
      conn.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = %s',(photo_id,))
      photo = conn.fetchone()
    conn.close()
    if photo is None:
  	  abort(404)
    return photo

  def edit_entry(id, title, description, image=None):
    conn = connect_db()
    # Write the image file/s to a directory
    if image.filename != '' and allowed_file(image.filename):
      image_path = num + '_' + secure_filename(image.filename)
      image.save( app.config['IMAGES_LOCATION'] + image_path )
      if app.config['DB_TYPE'] == 'sqlite3':
        conn.execute('UPDATE ' + app.config['DB_TABLE_NAME'] + ' SET title = ?, description = ?, url = ?'
                ' WHERE id = ?',
                (title, description, image_path, id))
      else:
        conn.execute('UPDATE ' + app.config['DB_TABLE_NAME'] + ' SET title = %s, description = %s, url = %s'
                ' WHERE id = %s',
                (title, description, image_path, id))
    else:
      if app.config['DB_TYPE'] == 'sqlite3':
        conn.execute('UPDATE ' + app.config['DB_TABLE_NAME'] + ' SET title = ?, description = ?'
                ' WHERE id = ?',
                (title, description, id))
        conn.commit()
      else:
        conn.execute('UPDATE ' + app.config['DB_TABLE_NAME'] + ' SET title = %s, description = %s'
                ' WHERE id = %s',
                (title, description, id))
    conn.close()
    return id, 201

  def del_entry(id):
    photo = Photo.get_photo(id)
    if photo['url'] is not None:
      os.remove(app.config['IMAGES_LOCATION'] + photo['url'])
    conn = connect_db()
    if app.config['DB_TYPE'] == 'sqlite3':
      conn.execute('DELETE FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = ?', (id,))
      conn.commit()
    else:
      conn.execute('DELETE FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = %s', (id,))
    conn.close()
    return '', 204
    
  def get(self, photo_id):
    conn = connect_db()
    if app.config['DB_TYPE'] == 'sqlite3':
      photo = conn.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = ?',(photo_id,)).fetchone()
    else:
      conn.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME'] + ' WHERE id = %s',(photo_id,))
      photo = conn.fetchone()
    conn.close()
    if photo is None:
  	  abort(404)
    a={}    
    for i in photo.keys():
      a[i] = photo[i]
    return a
   
  def post(self, photo_id):
    print(request)
    for i in ['title','description','url']:
      if request.form[i]:
        print(i + " " + request.form[i])


#### Photos  /api/photos ####
class Photos(Resource):    
  # Returns a list of photos
  def get_photos():
    conn = connect_db()
    if app.config['DB_TYPE'] == 'sqlite3':
      conn.row_factory = sqlite3.Row
      c = conn.cursor()
      photos = c.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME']).fetchall()
    else:
      conn.execute('SELECT * FROM ' + app.config['DB_TABLE_NAME'])
      photos = conn.fetchall()
    conn.close()
    return photos

  # Inserts an entry in the DB
  def insert_entry(title, description, image=None):
  	# Establish connection to DB
    conn = connect_db()
    # Save the image file/s to a directory
    if image !=None and image.filename != '' and allowed_file(image.filename):
      image_path = num + '_' + secure_filename(image.filename)
      image.save( app.config['IMAGES_LOCATION'] + image_path )
      if app.config['DB_TYPE'] == 'sqlite3':
        conn.execute('INSERT INTO ' + app.config['DB_TABLE_NAME'] + ' (title, description, url) VALUES (?, ?, ?)',
                        (title, description, image_path ))
      else:
        conn.execute('INSERT INTO ' + app.config['DB_TABLE_NAME'] + ' (title, description, url) VALUES (%s, %s, %s)',
                        (title, description, image_path))

    else:
      if app.config['DB_TYPE'] == 'sqlite3':
        conn.execute('INSERT INTO ' + app.config['DB_TABLE_NAME'] + ' (title, description) VALUES (?, ?)',
                        (title, description ))
        conn.commit()
      else:
        conn.execute('INSERT INTO ' + app.config['DB_TABLE_NAME'] + ' (title, description) VALUES (%s, %s)',
                        (title, description ))
    conn.close()
    return '', 201

  def get(self):
    a=[]
    for u in Photos.get_photos():
      e = {}
      for i in u.keys():
        e[i] = u[i]
      a.append(e)
    return a

#### Settings  /api/settings ####
class Settings(Resource):
  def get(self):
    cfg = {}
    with open(config_file, 'r') as file:
      for i in yaml.safe_load(file).items():
        if i[0] in config_settings:
          cfg[i[0]] = i[1] 
    return cfg
  def post(self):
    with open(config_file, 'r') as file:
      cfg = yaml.safe_load(file)
    for i in request.form:
      if i in config_settings:
        cfg[i] = request.form[i]
        app.config[i] = request.form[i]
    with open(config_file, 'w') as file:
      yaml.dump(cfg,file)
    

#########################################################################################################

# create the API resources
api.add_resource(Photo, '/api/photo/<photo_id>', methods=('GET', 'DEL', 'POST'))
api.add_resource(Photos, '/api/photos', methods=('GET', 'POST'))
api.add_resource(Settings, '/api/settings', methods=('GET', 'POST'))
app.register_blueprint(api_bp)

# Define the website routes
@app.route('/')
def index():
  photos = Photos.get_photos()
  return render_template('index.html', photos=photos, app_name=app.config['APP_NAME'], images_location=app.config['IMAGES_LOCATION'])

@app.route('/settings', methods=('GET', 'POST'))
@basic_auth.required
def settings():
  with open(config_file, 'r') as file:
    cfg = yaml.safe_load(file)
  if request.method == 'POST':
    for i in config_settings:
      cfg[i] = request.form[i]    
      app.config[i] = request.form[i] 
    with open(config_file, 'w') as file:
      yaml.dump(cfg,file)
  return render_template('settings.html', cfg=cfg, config_settings=config_settings )

@app.route('/about')
def about():
  return render_template('about.html',version=version, app_name=app.config['APP_NAME'])

@app.route('/<int:photo_id>')
def photo(photo_id):
  photo = Photo.get_photo(photo_id)
  return render_template('photo.html', photo=photo, images_location=app.config['IMAGES_LOCATION'])

@app.route('/create', methods=('GET', 'POST'))
def create():
  if request.method == 'POST':
    title = request.form['title']
    description = request.form['description']
    image = request.files['image']
    if not title:
      flash('Title is required!')
    else:
      Photos.insert_entry(title, description, image)      
      return redirect(url_for('index'))
  return render_template('create.html')
 
@app.route('/<int:id>/edit', methods=('GET', 'POST')) 
def edit(id):
  photo = Photo.get_photo(id)
  if request.method == 'POST':
    title = request.form['title']
    description = request.form['description']
    image = request.files['image']   
    if not title:
      flash('Title is required!')
    else:
      conn = connect_db()
      Photo.edit_entry(id, title, description, image)
      return redirect(url_for('index'))

  return render_template('edit.html', photo=photo, images_location=app.config['IMAGES_LOCATION'] )  
  
@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    photo = Photo.get_photo(id)
    Photo.del_entry(id)
    flash('"{}" was successfully deleted!'.format(photo['title']))
    return redirect(url_for('index'))



@app.route( '/' + app.config['IMAGES_LOCATION'] + '<filename>')
def upload(filename):
    return send_from_directory(app.config['IMAGES_LOCATION'], filename)

# Start #
if __name__ == '__main__':
    print("This is version: " + version)
    app.run(host='0.0.0.0', port=app.config['PORT'])

  

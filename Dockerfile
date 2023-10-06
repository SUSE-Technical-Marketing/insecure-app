FROM registry.opensuse.org/opensuse/bci/python:latest
WORKDIR /home/
USER root
RUN mkdir static templates images
COPY content/images/ images/
COPY content/flaskwebapp.py .
COPY content/static/ static/
COPY content/templates/ templates/
COPY content/database.db .
COPY content/init_db.py .
COPY content/tests.sh .
COPY content/myconf.yml .

COPY content/testimage.png images/
COPY version .
RUN zypper install -y python python3-Flask python3-Flask-Admin python3-pyaml python3-Werkzeug python3-Flask-HTTPAuth python3-pycryptodomex python3-pip python311-pipx system-user-nobody python3-Flask-RESTful python3-Flask-Login python3-Flask-Testing python3-mysql-connector-python python3-PyMySQL iputils python3-mysqlclient jq vim
RUN pip install --break-system-packages Flask-BasicAuth
RUN chmod 1777 images/ ; chown nobody:nobody database.db myconf.yml ; chmod 0755 tests.sh
# This app needs real power!
#USER nobody
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=flaskwebapp
# From my laptop to production, storage is not a problem
ENV FLASK_DEBUG=true
EXPOSE 5000
ENTRYPOINT [ "python3", "flaskwebapp.py" ]

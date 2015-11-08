# Deployment on Ubuntu 14.04

Create a new Ubuntu user

`adduser metpetdb`

Add the new user to the sudoers file

`gpasswd -a metpetdb sudo`

Log in as the newly created user and then continue with the following steps

```
sudo apt-get update
sudo apt-get upgrade
```

Install some packages we will need later

```
sudo apt-get install git python3.4-dev libpq-dev libxml2-dev libproj-dev libgeos-dev libgdal-dev python3-psycopg2 python-virtualenv virtualenvwrapper nginx
```

### Install PostgreSQL

```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

sudo apt-get update && sudo apt-get upgrade

sudo apt-get install postgresql
```

### Install PostGIS

```
sudo add-apt-repository ppa:ubuntugis/ubuntugis-unstable
sudo apt-get update
sudo apt-get install postgis
```

### Set up PostgreSQL

##### Initial setup

`sudo -i -u postgres`

You will be asked for your normal user password and then will be given a shell prompt for the postgres user.

Create a new role by typing `createuser --interactive`. This will open an interactive shell which will ask you a few questions about the new role. That interaction should loook like this:

```
Enter name of role to add: metpetdb
Shall the new role be a superuser? (y/n) n
Shall the new role be allowed to create databases? (y/n) y
Shall the new role be allowed to create more new roles? (y/n) n
```

##### PostGIS template setup

```
createdb -E UTF8 template_postgis

psql -d template_postgis -f /usr/share/postgresql/9.4/contrib/postgis-2.1/postgis.sql

psql -d template_postgis -f /usr/share/postgresql/9.4/contrib/postgis-2.1/spatial_ref_sys.sql

psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
```

##### Database creation

Create two new databases which are based on the PostGIS template we created earlier: the first database is the legacy database we will use for data migration, and the second one is the database which will be used by the new API.

```
createdb metpetdb_legacy -T template_postgis
createdb metpetdb -T template_postgis
```

##### Alter database ownership from the `postgres` role to `metpetdb`

Ensure you are still logged in as the `postgres` user and the type `psql` to enter the shell and do the following:

```
ALTER ROLE metpetdb WITH PASSWORD <password>;

ALTER DATABASE metpetdb_legacy OWNER TO metpetdb;
ALTER DATABASE metpetdb OWNER TO metpetdb;

\c metpetdb_legacy;
ALTER view geography_columns OWNER TO metpetdb;
ALTER table spatial_ref_sys OWNER TO metpetdb;

\c metpetdb;
ALTER view geography_columns OWNER TO metpetdb;
ALTER table spatial_ref_sys OWNER TO metpetdb;

​\q​

```

#### Codebase setup

​Press Ctrl+D to logout as the `postgres` user.
​

Checkout the API code and create a new virtualenv:

```
git clone --recursive https://github.com/kristallizer/metpetdb_drf_api.git api

mkvirtualenv api --python=/usr/bin/python3
```

Use a SQL data dump of the current database to populate the legacy database, and then run a migration available in the API repository.

```
cat metpetdb_oct24_2013_clean.dmp | psql -d metpetdb_legacy -U metpetdb
​cd api/metpetdb_api/
cat legacy_db_migration.sql | psql -d metpetdb_legacy -U metpetdb
```

Install required packages:
```
pip install -r requirements/staging.txt
```

Create a file containing the required environment variables. Here's a sample:

```
HOST_NAME=http://localhost:8000
API_SETTINGS='settings.staging'

SECRET_KEY=<some random string>
# Email server settings
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=username@gmail.com
EMAIL_HOST_PASSWORD=password
EMAIL_PORT=587

# Database settings
DB_NAME=metpetdb
DB_USERNAME=metpetdb
DB_PASSWORD=<db password>
DB_HOST=localhost
TEST_DB_NAME=metpetdb_test

LEGACY_DB_NAME=metpetdb_legacy
LEGACY_DB_USERNAME=metpetdb
LEGACY_DB_PASSWORD=<db password>
LEGACY_DB_HOST=localhost
```

# Database migration

```
python manage.py migrate
python manage.py migrate_legacy_users
python manage.py migrate_legacy_samples
```

# Server setup

Collect all the static files into a single directory

```
python manage.py collectstatic
```

### Nginx

```
sudo rm /etc/nginx/sites-available/default
sudo vi /etc/nginx/sites-available/metpetdb
```

Create a file `/home/metpetdb/.virtualenvs/api/gunicorn_config.py` and the following:

```
command = '/home/metpetdb/.virtualenvs/api/bin/gunicorn'
pythonpath = '/home/metpetdb/.virtualenvs/api/bin/python'
bind = '127.0.0.1:8001'
workers = 5
user = 'metpetdb'
```

Run

```
echo "alias start_api='/home/metpetdb/.virtualenvs/api/bin/gunicorn -c /home/metpetdb/.virtualenvs/api/gunicorn_config.py --pythonpath /home/metpetdb/api/metpetdb_api metpetdb_api.wsgi:application&'" >> ~/.bashrc

source ~/.bashrc
```

Copy the following into `/etc/nginx/sites-available/metpetdb`

```
server {
    listen 80;
    server_name <server IP>;

    access_log off;

    location /api/static/ {
        alias /home/metpetdb/api/metpetdb_api/static/;
    }

    location /api/ {
                proxy_pass http://127.0.0.1:8001;
                proxy_set_header Host $host;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /static/ {
        alias /home/metpetdb/ui/static/;
    }

    # frontend setup
    location / {
        proxy_pass http://127.0.0.1:8000/;
    }
}
```

Restart nginx and serve the app
```
cd /etc/nginx/sites-available/
sudo ln -s ../sites-available/metpetdb
sudo service nginx restart

cd /home/metpetdb/api/metpetdb_api
start_api
```

Press Ctrl+C to exit the gunicorn log

You can now access the API at <serverIP>/api/

# TODO
Use [Supervisor](http://supervisord.org/) or Ubuntu's own [Upstart](http://upstart.ubuntu.com/) to automatically start server process on boot or when they get killed.

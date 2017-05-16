#!/bin/bash
# MetPetDB API installation script for Ubuntu 16.04

line_skip="----------------------------------------------"
metpetdb_user="metpetdb"
install_path="/home/$metpetdb_user/api"
gunicorn_config="/home/$metpetdb_user/.virtualenvs/api/gunicorn_config.py"

# Ensure user runs script as root
ensure_root(){
    if [ $EUID -ne 0 ]; then
        echo "Please rerun as root"
        exit 1;
    fi
}

create_db_user(){
    # create the metpetdb user if it does not already exist
    id -u $metpetdb_user &> /dev/null
    if [ $? == 0 ] ; then
        printf "User $metpetdb_user already exists.\nSkipping this step.\n\n"
    else
        adduser $metpetdb_user
    fi
}

add_sudoer(){
    gpasswd -a $metpetdb_user sudo 
}

section_break(){
    printf "%s\n\n" $line_skip
}

update_system_packages(){
    sudo -u $metpetdb_user sh -c "sudo apt-get update"
    sudo -u $metpetdb_user sh -c "sudo apt-get upgrade -y" 
}

install_required_packages(){
    sudo -u $metpetdb_user bash -c "sudo apt-get install python-pip git python3-dev libpq-dev \
    libxml2-dev libproj-dev libgeos-dev libgdal-dev python3-psycopg2 \
    vim python-virtualenv virtualenvwrapper nginx -y"
}

install_postgres(){
    sudo -u $metpetdb_user sh -c "sudo sh -c 'echo \"deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main\" > /etc/apt/sources.list.d/pgdg.list'"
    sudo -u $metpetdb_user sh -c "wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -"
    sudo -u $metpetdb_user sh -c "sudo apt-get update && sudo apt-get upgrade -y"
    sudo -u $metpetdb_user sh -c "sudo apt-get install postgresql -y"
}

setup_postgres(){
    user_exists="$(sudo -u postgres sh -c "psql postgres -tAc \"SELECT 1 FROM pg_roles WHERE rolname='$metpetdb_user'\"")"
    if [ "$user_exists" == "1" ]; then
        printf "Role $metpetdb_user already exists. Skipping this step.\n"
    else
        sudo -u postgres sh -c "createuser -S -d -R $metpetdb_user" && printf "\nSuccessfully setup PostgreSQL.\n"
    fi
}

install_postgis(){
    sudo -u $metpetdb_user sh -c "sudo apt-get update"
    sudo -u $metpetdb_user sh -c "sudo apt-get install postgis -y"
}

create_template_postgis(){
    template_exists="$(sudo -u postgres sh -c "psql postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='template_postgis'\"")"
    if [ "$template_exists" == "1" ]; then
        printf "\n\nTemplate_postgis database exists. Skipping this step.\n"
    else 
        sudo -u postgres sh -c "createdb -E UTF8 template_postgis" 
    fi
}

create_database(){
    database_name="$1"
    database_exists="$(sudo -u postgres sh -c "psql postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='$database_name'\"")"
    if [ "$database_exists" == "1" ]; then
        printf "\n\n$database_name database exists. Skipping this step.\n"
    else 
        sudo -u postgres sh -c "createdb $database_name" 
    fi
}

create_database_template(){
    database_name="$1"
    database_exists="$(sudo -u postgres sh -c "psql postgres -tAc \"SELECT 1 FROM pg_database WHERE datname='$database_name'\"")"
    if [ "$database_exists" == "1" ]; then
        printf "\n\n$database_name database exists. Skipping this step.\n"
    else 
        sudo -u postgres sh -c "createdb $database_name -T template_postgis" 
    fi
}

run_postgis_scripts(){
    {
        psql_version="$(psql --version)"             # get the entire version string
        psql_version="${psql_version%\.*}"           # strip off the minor version
        psql_version="${psql_version##*[[:space:]]}" # strip off front
       
        postgis_path="$(ls -d /usr/share/postgresql/$psql_version/contrib/postgis*)"
       
        sudo -u postgres sh -c "psql -d template_postgis -f $postgis_path/postgis.sql"
        sudo -u postgres sh -c "psql -d template_postgis -f $postgis_path/spatial_ref_sys.sql"
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\""
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\""
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\""
    } &> /dev/null
}

set_postgres_password(){
    while true
    do
      printf "Enter a PostgreSQL password for the metpetdb user: "
      read -s postgres_password
      printf "\nConfirm PostgreSQL password for the metpetdb user: "
      read -s confirm_password
      #confirm password matches      
      if [ "$postgres_password" == "$confirm_password" ]; then
        break
      fi
      printf "\n\nPasswords do not match. Try again.\n\n"
    done
    
    sudo -u postgres sh -c "psql -c \"ALTER ROLE $metpetdb_user WITH PASSWORD '$postgres_password'\""
}

download_github_repo(){
    if [ ! -d "$install_path" ]; then 
        sudo -Hiu $metpetdb_user sh -c "git clone --recursive https://github.com/metpetdb/api_v2.git $install_path"
    else 
        printf "$install_path already exists. Skipping this step.\n"
    fi
}

setup_virtualenv(){
    sudo -Hiu $metpetdb_user bash -c "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh;
                                      mkvirtualenv api --python=/usr/bin/python3"
}
change_legacy_ownership(){
    sudo -u postgres sh -c "psql -c 'ALTER DATABASE metpetdb_legacy OWNER TO metpetdb;'"
    sudo -u postgres sh -c "psql -c 'ALTER DATABASE metpetdb OWNER TO metpetdb;'"
    sudo -u postgres sh -c "psql -d metpetdb_legacy -c 'ALTER view geography_columns OWNER TO metpetdb;'"
    sudo -u postgres sh -c "psql -d metpetdb_legacy -c 'ALTER view geometry_columns OWNER TO metpetdb;'"
    sudo -u postgres sh -c "psql -d metpetdb_legacy -c 'ALTER table spatial_ref_sys OWNER TO metpetdb;'"
}

install_pip_packages(){
    sudo -Hiu $metpetdb_user bash -c "~/.virtualenvs/api/bin/pip install -r $install_path/metpetdb_api/requirements/staging.txt"
}

create_api_config(){
    secret_key=$(date | md5sum | head -c 32) # generate a random 32 character/number secret key
    sudo -Hiu $metpetdb_user sh -c "printf \"HOST_NAME=http://localhost:8000\n
API_SETTINGS='settings.staging'\n\n
SECRET_KEY=$secret_key\n
# Email server settings\n
EMAIL_USE_TLS=True\n
EMAIL_HOST=smtp.gmail.com\n
EMAIL_HOST_USER=username@gmail.com\n
EMAIL_HOST_PASSWORD=password\n
EMAIL_PORT=587\n
FRONT_END_URL=metpetdb.com\n\n

# Database settings\n
DB_NAME=metpetdb\n
DB_USERNAME=$metpetdb_user\n
DB_PASSWORD=$postgres_password\n
DB_HOST=localhost\n
TEST_DB_NAME=metpetdb_test\n\n
LEGACY_DB_NAME=metpetdb_legacy\n
LEGACY_DB_USERNAME=$metpetdb_user\n
LEGACY_DB_PASSWORD=$postgres_password\n
LEGACY_DB_HOST=localhost\" 
                                 > $install_path/metpetdb_api/api.env"
}

migrate_legacy_data(){
    while true
    do
      printf "Path to legacy data dump (Enter to skip): "
      read dump_path
      if [ -z "${dump_path// }" ]; then
          echo 'Skipping legacy database population'
          break
      elif [ ! -f "$dump_path" ]; then      # ensure data dump exists
        echo "No such file $dump_path. Try again." 
      else
          printf "Populating database...\n$line_skip\n"
          cat $dump_path | sudo -u $metpetdb_user sh -c "psql -d metpetdb_legacy -U $metpetdb_user"
          cat $install_path/metpetdb_api/legacy_db_migration.sql | sudo -u $metpetdb_user sh -c "psql -d metpetdb_legacy -U $metpetdb_user"
          break
      fi
    done
}

failure(){
    echo "$1"
    exit 1
}

soft_failure(){
    echo "$1"
}

migrate(){
    migrate_name="$1"
    sudo -Hiu $metpetdb_user bash -c "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh;
                                cd $install_path/metpetdb_api/;
                                workon api; 
                                python manage.py $migrate_name"
}

collect_static(){
    sudo -Hiu $metpetdb_user bash -c "source /usr/share/virtualenvwrapper/virtualenvwrapper.sh;
                                cd $install_path/metpetdb_api/;
                                workon api; 
                                echo 'yes' | python manage.py collectstatic"
}

database_migrations(){
    sudo -u postgres sh -c "psql -c 'ALTER ROLE $metpetdb_user SUPERUSER;'"
    migrate "migrate"
    sudo -u postgres sh -c "psql -c 'ALTER ROLE $metpetdb_user NOSUPERUSER;'"
    printf "Finished migrating schema\n\n"

    printf "Migrate legacy data? (y/n): "

    read migrate_data_res
    if [ "$migrate_data_res" = "y" ]; then
        printf "Migrating legacy users\n\n"
        migrate "migrate_legacy_users" || failure "Failed to migrate legacy users"
        printf "Finished migrating legacy users\n\n"
                                        
        printf "Migrating legacy samples\n\n"
        migrate "migrate_legacy_samples" || failure "Failed to migrate legacy samples"
        printf "Finished migrating legacy samples\n\n"
                                        
        printf "Migrating legacy chemical analyses\n\n"
        migrate "migrate_legacy_chemical_analyses" || failure "Failed to migrate legacy chemical analyses"
        printf "Finished migrating legacy chemical analyses\n\n"
    else
        printf "\n\nSkipping legacy migrations\n\n"
    fi
                                    
    printf "\n\nCollecting static \n$line_skip\n\n"
    collect_static || failure "Failed to collect static"
    printf "Finished collecting static\n$line_skip\n\n"
}

setup_gunicorn(){
      sudo -Hiu $metpetdb_user sh -c "printf \"command = '/home/$metpetdb_user/.virtualenvs/api/bin/gunicorn'\n
pythonpath = '/home/$metpetdb_user/.virtualenvs/api/bin/python'\n
bind = '127.0.0.1:8001'\n
workers = 5\n
user = '$metpetdb_user'\n\" 
                         > $gunicorn_config" 
}

add_start_api(){
    sudo -Hiu $metpetdb_user sh -c "printf \"\nstart_api(){\n
        cd /home/metpetdb/api/metpetdb_api\n
        /home/metpetdb/.virtualenvs/api/bin/gunicorn -c /home/metpetdb/.virtualenvs/api/gunicorn_config.py --pythonpath /home/metpetdb/api/metpetdb_api metpetdb_api.wsgi:application&\n
        cd -\n
}\" >> ~/.bashrc"
}

add_redeploy_api(){
    sudo -Hiu $metpetdb_user sh -c "printf \"\nredeploy_api(){\n
    cd\n
    if [ -d \"$install_path\" ]; then\n
        mv \"$install_path\" \"/home/$metpetdb_user/old_api\"\n
    fi\n
    git clone --recursive https://github.com/metpetdb/api_v2.git $install_path\n
    cp /home/$metpetdb_user/old_api/metpetdb_api/api.env $install_path/metpetdb_api\n
    cd -\n
}\" >> ~/.bashrc"
}

add_metpetdb_site(){
    # Get external ip address of this machine
    ip_address=$(curl -s http://whatismyip.akamai.com/)
    printf "server {
    listen 80;
    server_name $ip_address;

    access_log off;

    location /api/static/ {
        alias /home/$metpetdb_user/api/metpetdb_api/static/;
    }

    location /api/ {
                proxy_pass http://127.0.0.1:8001;
                proxy_set_header Host \$host;
                proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    location /static/ {
        alias /home/$metpetdb_user/ui/static/;
    }

    # frontend setup
    location / {
        proxy_pass http://127.0.0.1:8000/;
    }
}" > /etc/nginx/sites-available/metpetdb
    # enable site
    if [ ! -L /etc/nginx/sites-enabled/metpetdb ]; then
      sudo ln -s /etc/nginx/sites-available/metpetdb /etc/nginx/sites-enabled/metpetdb  
    fi
}

rm_default_site(){
    # remove the default nginx site
    if [ -L /etc/nginx/sites-available/default ]; then 
      sudo rm /etc/nginx/sites-available/default
    fi
    # remove from enabled sites
    if [ -f /etc/nginx/sites-enabled/default ]; then 
      sudo rm /etc/nginx/sites-enabled/default
    fi
}

setup_nginx(){
  printf "Setup Nginx? (y/n): "
  read confirm_nginx
  if [ "$confirm_nginx" = "y" ]; then
  
    rm_default_site   # remove the nginx default site 
    setup_gunicorn    # initialize gunicorn.py
    add_start_api     # add start_api command to metpetdb user .bashrc
    add_redeploy_api  # add redeploy_api command to metpetdb user .bashrc
    add_metpetdb_site # add the metpetdb site to the nginx config
    
    service nginx restart
  else
    printf "Skipping Nginx setup\n"
  fi
}

######################################################################

main(){
    ensure_root

    printf "\n\nMetPetDB setup started\n"
    section_break

    echo "Creating $metpetdb_user user."
    create_db_user || failure "Failed to add user $metpetdb_user"
    printf "\n\nUser $metpetdb_user created successfully\n"
    section_break
    
    echo "Adding $metpetdb_user to the sudoers file."
    add_sudoer || failure "Failed to add user $metpetdb_user to sudoers"
    printf "Successfully added $metpetdb_user to sudoers\n"
    section_break
    
    printf "Updating system packages ( this may take a while )\n\n"
    update_system_packages || soft_failure "Failed to update system packages"
    printf "Successfully updated system packages\n"
    section_break
    
    printf "Installing required packages...\n\n"
    install_required_packages || failure "Failed to install required packages"
    printf "\nSuccessfully installed required packages.\n"
    section_break
    
    printf "Installing PostgreSQL\n\n"
    install_postgres || failure "Failed to install postgres"
    printf "\nSuccessfully installed PostgreSQL.\n"
    section_break
    
    printf "\n\nInstalling PostGIS\n\n"
    install_postgis || failure "Failed to install postgis"
    printf "\nSuccessfully installed PostGIS.\n"
    section_break
    
    printf "Setting up PostgreSQL \n\n"
    setup_postgres || failure "Failed to setup postgres"
    section_break

    printf "Setting up PostGIS templates \n\n"
    echo "Creating template_postgis database"
    create_template_postgis || failure "Failed to create PostGIS template"
    printf "Running postgis scripts\n"
    run_postgis_scripts || failure "Postgis setup scripts failed"
    printf "Finished setting up PostGIS templates \n"
    section_break

    printf "Creating metpetdb databases \n\n"
    echo "Creating metpetdb_legacy database"
    create_database_template "metpetdb_legacy" || failure "Failed to create metpetdb_legacy database"
    printf "\n\nSuccessfully created metpetdb_legacy database.\n\n"
    echo "Creating metpetdb database"
    create_database "metpetdb" || failure "Failed to create metpetdb database"
    printf "\n\nSuccessfully created metpetdb database.\n\n"
    section_break

    set_postgres_password || failure "Failed to set postgres password for metpetdb user."
    printf "Password updated successfully\n"
    section_break

    printf "Changing legacy ownership to metpetdb\n\n"
    change_legacy_ownership || failure "Failed to change legacy ownership"
    printf "Successfully updated legacy ownership.\n"
    section_break

    printf "Setting up codebase\n\n"
    echo "Downloading codebase from github..."
    download_github_repo || failure "Failed to setup git repo"
    printf "Successfully setup git repo.\n"
    section_break

    printf "Creating the api virtual environment\n\n"
    setup_virtualenv || failure "Failed to create virtual environment"
    printf "\n\nSuccessfully created api virtual env\n"
    section_break

    printf "Installing required Python packages to api virtual environment"
    install_pip_packages
    printf "\n\nSuccessfully installed required python packages to api virtual environment\n"
    section_break

    printf "Creating config file\n"
    create_api_config || failure "FAILED to create config file"
    printf "Successfully created config file\n"
    section_break
    
    printf "Populating database from data_dump\n$line_skip\n\n"
    migrate_legacy_data || failure "FAILED to import from dump"
    printf "\n\nLegacy database population completed\n"
    section_break
   
    printf "Starting database migration\n" || failure "FAILED to perform migrations"
    database_migrations
    section_break
    
    printf "Setting up Nginx\n" || failure "Nginx setup failed"
    setup_nginx
    section_break
    
    printf "Setup of MetPetDB API completed\n\n"
    exit 0
}

main

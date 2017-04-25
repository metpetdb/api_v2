#!/bin/bash
# MetPetDB API installation script for Ubuntu 16.04

line_skip="----------------------------------------------"
metpetdb_user="metpetdb"
install_path="/home/$metpetdb_user/api"

###################################################
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
    python-virtualenv virtualenvwrapper nginx -y"
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
    # TODO get exact versions of postgres and postgis
    {
        sudo -u postgres sh -c "psql -d template_postgis -f /usr/share/postgresql/9.6/contrib/postgis-2.3/postgis.sql"
        sudo -u postgres sh -c "psql -d template_postgis -f /usr/share/postgresql/9.6/contrib/postgis-2.3/spatial_ref_sys.sql"
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON geometry_columns TO PUBLIC;\""
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON geography_columns TO PUBLIC;\""
        sudo -u postgres sh -c "psql -d template_postgis -c \"GRANT ALL ON spatial_ref_sys TO PUBLIC;\""
    } &> /dev/null
}

set_postgres_password(){
    read postgres_password
    sudo -u postgres sh -c "psql -c \"ALTER ROLE $metpetdb_user WITH PASSWORD '$postgres_password'\""
}

download_github_repo(){
    if [ ! -d "$install_path" ]; then 
        sudo -Hiu $metpetdb_user sh -c "git clone --recursive https://github.com/kristallizer/metpetdb_drf_api.git $install_path"
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
    sudo -Hiu $metpetdb_user sh -c "printf \"HOST_NAME=http://localhost:8000\n
API_SETTINGS='settings.staging'\n\n
SECRET_KEY=<some random string>\n
# Email server settings\n
EMAIL_USE_TLS=True\n
EMAIL_HOST=smtp.gmail.com\n
EMAIL_HOST_USER=username@gmail.com\n
EMAIL_HOST_PASSWORD=password\n
EMAIL_PORT=587\n\n
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
    read dump_path
    if [ -z "${dump_path// }" ]; then 
        echo 'Skipping legacy database population'
    else
        # try to read data dump TODO error checking
        printf "Populating database...\n$line_skip\n"
        cat $dump_path | sudo -u $metpetdb_user sh -c "psql -d metpetdb_legacy -U $metpetdb_user"
        cat $install_path/metpetdb_api/legacy_db_migration.sql | sudo -u $metpetdb_user sh -c "psql -d metpetdb_legacy -U $metpetdb_user"
    fi
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
    migrate "collectstatic" || failure "Failed to collect static"
    printf "Finished collecting static\n$line_skip\n\n"
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

    printf "Enter a PostgreSQL password for the metpetdb user: "
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
    printf "Successfully setup git repo"
    section_break

    # Create the virtual environment
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
    printf "Path to legacy data dump (Enter to skip): "
    migrate_legacy_data || "FAILED to import from dump"
    printf "\n\nLegacy database population completed"
    section_break
   
    printf "Starting database migration\n"
    database_migrations
    
    printf "Setup of MetPetDB API completed\n\n"
    exit 0
}

main
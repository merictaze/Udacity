# Project 5

## Info
* IP: 52.27.208.130, SSH-PORT: 2200
* WebApp URL: http://52.27.208.130/
* Installed linux packages:
  * apache2
  * python-pip
  * libapache2-mod-wsgi
  * git
  * postgresql
* Installed python packages:
  * dict2xml == 1.3
  * Flask == 0.10.1
  * httplib2 == 0.9.1
  * SQLAlchemy == 0.8.4
  * google_api_python_client == 1.4.1
  * Requests == 2.7.0

## Linux Server Setup
1. Create a new user named grader

    ```
    adduser grader
    ```
1. Give the grader the permission of sudo

    ```
    gpasswd -a grader sudo
    Adding user grader to group sudo
    
    grep sudo /etc/group
    sudo:x:27:grader
    ```
1. Disable direct root login via ssh

    ```
    vim /etc/ssh/sshd_config
    # PermitRootLogin no

    export PUBLICKEY=`cat ~/.ssh/authorized_keys`
    # switch new user
    su grader

    mkdir ~/.ssh
    echo $PUBLICKEY >> ~/.ssh/authorized_keys

    # new user is ready, restart ssh after updates
    sudo service ssh restart
    ```
1. Update all currently installed packages

    ```
    # doesn't actually install new versions of software.
    # downloads the package lists from the repositories and 
    # "updates" them to get information on the newest versions
    # of packages and their dependencies. An update should 
    # always be performed before an upgrade or dist-upgrade.
    sudo apt-get update

    # upgrades all installed packages
    sudo apt-get upgrade

    # will do the same job which is done by apt-get upgrade,
    # plus it will also intelligently handle the 
    # dependencies, so it might remove obsolete packages or
    # add new ones.
    sudo apt-get dist-upgrade
    ```
1. Change the SSH port from 22 to 2200

    ```
    # update "Port 22"
    sudo vim /etc/ssh/sshd_config
    # restart the service
    sudo service ssh restart
    # verify the port
    ssh -i ~/.ssh/udacity_key.rsa grader@$server -p 2200
    ```

1. Configure the Uncomplicated Firewall (UFW) to only allow incoming connections for SSH (port 2200), HTTP (port 80), and NTP (port 123)

    ```
     # enable UFW
     sudo ufw enable
     # list rules
     sudo ufw status
     # allow ssh port
     sudo ufw allow 2200
     # close everything else
     sudo ufw default deny
     # allow HTTP and NTP
     sudo ufw allow 80
     sudo ufw allow 123
     # xcheck
     sudo ufw status
    ```
1. Configure the local timezone to UTC

    ```
    sudo dpkg-reconfigure tzdata
    cat /etc/timezone
    Etc/UTC
    ```
1. Install and configure Apache to serve a Python mod_wsgi application

    ```
    # install apache, and check $server on your browser
    sudo apt-get install apache2
    
    # install mod-wsgi
    sudo apt-get install libapache2-mod-wsgi
    # enable mod-wsgi
    sudo a2enmod wsgi

    # create a test project
    cd /var/www
    sudo mkdir App
    cd App
    sudo mkdir static templates
    sudo vim application.py
    ```

    content of ```application.py```
    ```
    from flask import Flask
    app = Flask(__name__)
    @app.route("/")
    def hello():
        return "Hello World!"
    if __name__ == "__main__":
        app.run()
    ```

    ```
    # install flask in a virtual environment
    sudo apt-get install python-pip
    sudo pip install virtualenv
    sudo virtualenv venv
    source venv/bin/activate
    sudo pip install Flask
    sudo python application.py
    deactivate
    
    # Configure and Enable a New Virtual Host
    sudo vim /etc/apache2/sites-available/App.conf
    ```
    
    content of ```App.conf```
    ```
    <VirtualHost *:80>
            WSGIScriptAlias / /var/www/App/application.wsgi
            <Directory /var/www/App>
                Order allow,deny
                Allow from all
            </Directory>
            Alias /static /var/www/App/static
            <Directory /var/www/App/static/>
                Order allow,deny
                Allow from all
            </Directory>
            ErrorLog ${APACHE_LOG_DIR}/error.log
            LogLevel warn
            CustomLog ${APACHE_LOG_DIR}/access.log combined
    </VirtualHost>
    ```

    ```
    # enable the virtual host
    sudo a2ensite App
    # deactivate the default hosts
    sudo ls /etc/apache2/sites-available/
    000-default.conf  App.conf  default-ssl.conf
    sudo a2dissite 000-default

    sudo vim /var/www/App/application.wsgi
    ```
    
    content of ```application.wsgi```
    ```
    #!/usr/bin/python
    import sys
    import logging
    logging.basicConfig(stream=sys.stderr)
    sys.path.insert(0,"/var/www/App")
    from application import app as application
    ````

    ```
    # restart apache
    sudo service apache2 restart
    # check  $server on your browser
    ```
1. Install and configure PostgreSQL:

    ```
    sudo apt-get install postgresql
    # if you want to set postgres user password
    sudo -u postgres psql postgres
    postgres=# \password postgres
    postgres-# \q
    ```
    1. Do not allow remote connections

        ```
        # version might be different
        sudo vim /etc/postgresql/9.3/main/pg_hba.conf
        # remove comments from the following lines
        local   all             postgres                                peer
        local   all             all                                     peer
        host    all             all             127.0.0.1/32            md5
        host    all             all             ::1/128                 md5
        ```
    1. Create a new user named catalog that has limited permissions to your catalog application database

        ```
        # http://www.postgresql.org/docs/9.2/static/app-createuser.html
        sudo su postgres -c 'createuser -dRS catalog'
        sudo su postgres -c 'createdb catalog'
        sudo psql -U postgres -h localhost -d catalog -c 'grant all privileges on database catalog to catalog'
        ```
1. Install git, clone and setup your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. 

    ```
    sudo apt-get install git
    cd
    git clone https://github.com/merictaze/Udacity.git
    sudo cp -r ~/Udacity/Nanodegree-FullStack/Project3/vagrant/catalog/* /var/www/App
    # fix the errors
    # install missing packages with apt-get and pip install
    # set db path to "/var/www/App/catalog.db"
    sudo vim /var/log/apache2/error.log
    sudo service apache2 restart
    
    # update google&facebook Authorized JavaScript origins / redirect URIs
    # if you have oauth login
    ```
1. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser!

    ```
    # remove "Options Indexes" or add "Options -Indexes"
    sudo vim /etc/apache2/apache2.conf 
    ```

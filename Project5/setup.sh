# add new user and give sudo access
adduser grader
gpasswd -a grader sudo

# update the system
apt-get update
sudo apt-get upgrade
sudo apt-get dist-upgrade

# install the necessary softwares
apt-get -qqy apache2
apt-get -qqy python-pip
apt-get -qqy libapache2-mod-wsgi
apt-get -qqy postgresql
apt-get -qqy git

# install python packages
pip install virtualenv
pip install bleach
pip install oauth2client
pip install requests
pip install httplib2
pip install dict2xml
pip install flask-seasurf

# disable all ports except SSH, HTTP and NTP
ufw enable
ufw allow 2200
ufw default deny
ufw allow 80
ufw allow 123

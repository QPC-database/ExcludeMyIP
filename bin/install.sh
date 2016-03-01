#!/bin/bash
# Installs ExcludeMyIP and all dependencies on a fresh Ubuntu 14.04.

# Abort on any error:
set -e

SERVER_IP=45.33.20.51
# You need to fill in this value:
EMAIL_CONFIG='[smtp.gmail.com]:587    user@gmail.com:password'

if [ -z `which sudo` ]; then
	echo 'Installing sudo...';
	apt-get update;
	apt-get install sudo -y;
fi

if [ -z "$LC_ALL" ]; then
	echo 'Setting locale to avoid Perl warnings "Setting locale failed."...'
	locale-gen en_US.UTF-8
	sudo su -c "echo -e 'LANG=en_US.UTF-8\nLC_ALL=en_US.UTF-8' > /etc/default/locale"
	echo 'Shell restart required. Please log out and back in, then execute the script again.'
	exit
fi

sudo apt-get update
sudo apt-get upgrade -y

echo 'Setting time zone to Vienna...'
sudo su -c 'echo "Europe/Vienna" > /etc/timezone'
sudo dpkg-reconfigure -f noninteractive tzdata

echo 'Installing git...'
sudo apt-get install git-core -y

echo 'Creating application user...'
sudo groupadd --system webapps
sudo useradd --system --gid webapps --shell /bin/bash emi
sudo mkdir -p /home/emi
sudo chown emi /home/emi

echo 'Adding GitHub to known hosts...'
sudo su -c "mkdir .ssh; ssh-keyscan -H github.com >> .ssh/known_hosts ; chmod 600 .ssh/known_hosts" - emi

echo 'Cloning the repository...'
sudo su -c "git clone https://github.com/mherrmann/ExcludeMyIP.git src" - emi
sudo su -c 'cd src/ ; git checkout live' - emi

echo 'Generating Django secret key...'
sudo apt-get install pwgen
secret_key=`pwgen -s -y 50 1`
echo 'SECRET_KEY = """$secret_key"""' > /home/emi/src/emi/secret_key.py
chown emi:webapps /home/emi/src/emi/secret_key.py
chmod 400 /home/emi/src/emi/secret_key.py

echo 'Setting up bash profile for user emi...'
sudo su -c "ln -sf /home/emi/src/conf/.bashrc /home/emi/.bashrc" - emi
sudo su -c "ln -sf /home/emi/src/conf/.bash_profile /home/emi/.bash_profile" - emi

echo 'Installing Postfix...'
sudo debconf-set-selections <<< "postfix postfix/mailname string emi"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Internet Site'"
sudo apt-get install postfix mailutils libsasl2-2 ca-certificates libsasl2-modules -y

echo 'Configuring Postfix...'
sudo ln -sf /home/emi/src/conf/postfix/main.cf /etc/postfix/main.cf
sudo su -c "echo $EMAIL_CONFIG > /home/emi/src/conf/postfix/sasl_passwd" - emi
sudo ln -sf /home/emi/src/conf/postfix/sasl_passwd /etc/postfix/sasl_passwd
sudo su -c "echo -e 'emi' > /etc/mailname"
sudo chown postfix /etc/mailname
sudo chmod 400 /etc/postfix/sasl_passwd
sudo chown postfix /etc/postfix/
sudo chown postfix /etc/postfix/sasl_passwd
sudo postmap /etc/postfix/sasl_passwd
sudo /etc/init.d/postfix reload

echo 'Installing pyvenv...'
sudo apt-get install python-pip -y
sudo pip install virtualenv

echo 'Installing Python dependencies...'
sudo apt-get install python-dev libffi-dev libssl-dev -y
sudo su -c 'cd src/ ; python /usr/local/lib/python2.7/dist-packages/virtualenv.py venv ; source venv/bin/activate ; pip install -r requirements.txt' - emi

echo 'Migrating database...'
sudo su -c 'cd src/ ; source venv/bin/activate ; python manage.py migrate' - emi

echo 'Collecting static files...'
su -c 'cd src/ ; source venv/bin/activate ; python manage.py collectstatic --noinput' - emi

echo 'Creating log file dir...'
sudo su -c 'cd src/ ; mkdir -p logs' - emi

echo 'Installing Supervisor...'
sudo apt-get install supervisor -y

echo 'Configuring Supervisor...'
sudo ln -s /home/emi/src/conf/supervisor/gunicorn.conf /etc/supervisor/conf.d/emi-gunicorn.conf

echo 'Updating Supervisor...'
sudo supervisorctl reread
sudo supervisorctl update

echo 'Installing Lets Encrypt...'
git clone https://github.com/letsencrypt/letsencrypt

echo 'Generating SSL certificates...'
sudo letsencrypt/letsencrypt-auto --standalone --non-interactive --email michael@herrmann.io --agree-tos auth -d www.excludemyip.com -d excludemyip.com

echo 'Uninstalling Lets Encrypt...'
rm -rf letsencrypt

echo 'Installing Nginx...'
sudo apt-get install nginx -y

echo 'Configuring Nginx...'
sudo mkdir /etc/nginx/includes
sudo su -c "echo 'set \$SERVER_IP $SERVER_IP;' > /etc/nginx/includes/emi-ip"
sudo ln -s /home/emi/src/conf/nginx /etc/nginx/sites-available/emi
sudo ln -s /etc/nginx/sites-available/emi /etc/nginx/sites-enabled/emi
sudo rm /etc/nginx/sites-enabled/default

echo 'Starting Nginx...'
sudo service nginx start

echo 'Setting up some shortcuts...'
sudo su -c 'ln -s /home/emi/src/bin/shell.sh /home/emi/shell.sh' - emi
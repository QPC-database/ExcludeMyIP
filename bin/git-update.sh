#!/bin/bash

# Stop web server:
sudo service nginx stop
sudo supervisorctl stop emi-gunicorn

echo 'Web server stopped at '`date`'.'

# Update:
su -c 'cd src/ ; git pull' - emi
su -c 'cd src/ ; source venv/bin/activate ; pip install -r requirements.txt | grep -v "^Requirement already satisfied"' - emi
su -c 'cd src/ ; source venv/bin/activate ; python manage.py migrate' - emi
su -c 'cd src/ ; source venv/bin/activate ; python manage.py collectstatic --noinput' - emi

# Start web server again:
sudo supervisorctl start emi-gunicorn
sudo service nginx start

echo 'Web server came back online at '`date`'.'
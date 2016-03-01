#!/bin/bash

NAME="emi"
DJANGODIR=/home/emi/src/
SOCKFILE=/home/emi/src/run/gunicorn.sock
USER=emi
GROUP=webapps
NUM_WORKERS=3
DJANGO_WSGI_MODULE=emi.wsgi

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source venv/bin/activate
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves
# (do not use --daemon)
exec venv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --bind=unix:$SOCKFILE \
  --log-level=debug \
  --log-file=-
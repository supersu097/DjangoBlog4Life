NAME="DjangoBlog4Life"
DJANGODIR=/home/www/DjangoBlog4Life-private #Django project directory
USER=www # the user to run as
GROUP=www # the group to run as
NUM_WORKERS=5 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=DjangoBlog4Life.settings_prod # which settings file should Django use
DJANGO_WSGI_MODULE=DjangoBlog4Life.wsgi # WSGI module name
TIMEOUT=120
echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
#source /home/server/python/env/djangoblog/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH


# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
nohup gunicorn  ${DJANGO_WSGI_MODULE}:application \
--name $NAME \
--workers $NUM_WORKERS \
--timeout $TIMEOUT \
--preload \
--user=$USER --group=$GROUP \
--log-level=debug \
--log-file=- &

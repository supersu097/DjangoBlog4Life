ps -ef |grep unicorn |grep -v grep |awk '{print $2}' |xargs kill -9
bash gunicorn_start.sh

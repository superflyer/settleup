kill `ps -f -u root | grep 'settleup' | grep -v grep | egrep -o 'root +[0-9]+' | egrep -o [0-9]+`
nohup python src/settleup-api.py 1>> logs/webserver.log 2>> logs/webserver.err &

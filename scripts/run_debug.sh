killa ()
{
    ps ax | grep $* | awk '{print $1}' | xargs kill 2>/dev/null
}
start ()
{
    /var/rabbitmq_server-2.2.0/sbin/rabbitmq-server&
    sleep 1
    python manage.py celeryd -B&
    memcached&
    python manage.py runserver 0.0.0.0:8000
    #sudo searchd&
}
stop ()
{
    killa celeryd
    /var/rabbitmq_server-2.2.0/sbin/rabbitmqctl -q stop
    killa runserver
    killall memcached
    #killall searchd
}
case "$1" in
    start)
        start
    ;;
    stop)
        stop
    ;;
    restart)
        stop
        sleep 1
        start        
    ;;
    *)
        echo $0 "{start|stop|restart}"
    ;;
esac


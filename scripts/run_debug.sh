killa ()
{
    ps ax | grep $* | awk '{print $1}' | xargs kill 2>/dev/null
}

case "$1" in
    start)
        python manage.py runserver 0.0.0.0:8000&
        /var/rabbitmq_server-2.2.0/sbin/rabbitmq-server&
        python manage.py celeryd&
        memcached&
        #sudo searchd&
    ;;
    stop)
        killa celeryd
        /var/rabbitmq_server-2.2.0/sbin/rabbitmqctl -q stop
        killa runserver
        killall memcached
        #killall searchd
    ;;
    *)
        echo $0 "{start|stop}"
    ;;
esac


#!/usr/bin/bash
#droid4control linux controller startup, started by /etc/rc.local
# vt /etc/rc.local  logi suunamise kohta /root/d4c/appd.log
exec 0</dev/null
exec>>/tmp/appd.log 2>&1


APPCFG=/root/d4c/appcfg.sh

##### USING env variables ######

#ID=000101100000
#APP=/root/d4c/main_monitor.py # controller application
#IOMBA=1 # modbus address of io card it5888 inside the controller

# the env variables below should be pretty stable
#RESCUE=/root/d4c/main_rescue.py
#HOSTNAME=d4c_controller
#VPNON=/root/d4c/vpnon
#CHKTIME=/root/d4c/chk_time.sh
#CHKCONN=/root/d4c/conn_restore.sh
#LOG=/root/d4c/appd.log
#TOUT=1000 # timeout to power cut or reboot in case of no connectivity
#SQLDIR=/root/d4c
########################

cd /root/d4c
if [ -x $APPCFG ];then
    . $APPCFG
    vars=`cat $APPCFG | grep -v "^#" | grep "=" | cut -d"=" -f1`
    for variable in $vars
    do
        export $variable
    done
    (echo; echo $0 start; env) # >> $LOG
else
    echo MISSING $APPCFG...
    exit 1
fi

(echo; echo -n "$0 start "; date) #>> $LOG

if [ ! -x $VPNON ]; then
    echo $0 reports MISSING $VPNON #>> $LOG
    echo MISSING $VPNON...
    sleep 5
    exit 1
fi


if [ -x $CHKCONN ]; then
    num=0
    echo $0 waiting for connectivity... #>> $LOG
    while [ $num -lt 8 ]; do
        num=`expr $num + 1`
        echo conn try $num # >> $LOG
        if $CHKCONN
        then
            echo "${0}: connectivity established" #>> $LOG
            break # get out of loop
        fi
        sleep 5
    done

    if ! $CHKCONN # this starts vpn if conn ok (first try must be ok)
    then
        echo "${0}: continuing without connectivity..." #>> $LOG
    else # conn ok
      if $CHKTIME; then
        ./wr_time.sh  # writes hw clock if exists. use also once a day via crontab
      fi
    fi
else
   echo $0 reports MISSING $CHKCONN #>> $LOG
   #echo $0 reports MISSING $CHKCONN
   sleep 5
fi

########### endless loop  to keep app, rescue app, vpn running #################################

while true
do
  (echo; echo -n "${APP} restart at "; date) # >> $LOG
  if ! python $APP # >> $LOG 2>&1  # only errors to log file. avoiding +x bit possible error
  then
    (echo; echo -n "${RESCUE} start!!! "; date) #>> $LOG
    python $RESCUE # >> $LOG 2>&1
  fi
  # vpn will be started if both py apps fail
  $VPNON   # start vpn in case of application failure. does not restart, if already running
  sleep 20 # limit the number of log records
done

### END ###



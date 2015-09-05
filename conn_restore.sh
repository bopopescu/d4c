#!/usr/bin/bash
#droid4control 2015
#FIXME / pane lock /tmp, ps nr

exec 0</dev/null
exec>>/root/d4c/appd.log 2>&1 # nii stdout kui stderr, symlink /tmp/appd.log

testrun() { # test anything given as parameters for success
    $* > /dev/null
    local status=$?
    echo $status
}


fullstop() { # stop py application and reset 5V power
    msg="appd.sh: stopping python and cold rebooting via 5V (mba ${1}) reset NOW!"
    echo $msg
    sync
    sleep 5
    
    killall -TERM python # stop app to avoid modbus collision
    sleep 1
    killall -KILL python
    sleep 5
    python mb.py $1 277 0009 # toitekatkestuse imp pikkus
    python mb.py $1 999 feed # toide maha
    reboot # igaks juhuks kui eelmisega mingi jama
    }

conn() {
    local LOG=/root/d4c/usb_debug.log
    echo $0 trying to restore connectivity...
    # WARNING - lsusb may hang with usb chip problems!
    /usr/bin/lsusb & # kaivitame
    sleep 10
    if [ `/usr/local/bin/ps1 lsusb | wc -l` -gt 0 ]; then # hangs!
        echo lsusb hanging... debug output will follow...
        killall -KILL lsusb
        (echo;date) >> $LOG
        dmesg >> $LOG# eraldi logisse
        ps -eo pid,tid,class,rtprio,ni,pri,psr,pcpu,stat,wchan:14,comm >> $LOG
        strace -tt lsusb & >> $LOG # this will hang as well
        sleep 15
        killall -KILL lsusb
        (echo; echo) >> $LOG
        fullstop $IOMBA  # go no further
    else
        LSUSB=`/usr/bin/lsusb`
        #echo LSUSB ok
        echo "$LSUSB" # debug
    fi

    if [ `echo "$LSUSB" | grep WLAN | wc -l` -gt 0 ]; then # adapter olemas
        if [ `/usr/local/bin/ps1 wpa | wc -l` -eq 0 ]; then # WiFi veel ei toota
            echo $0 starting RTL wlan on device wlan0...  # >> $LOG
            if ip link set wlan0 up
            then
              #wpa_supplicant -Dwext -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf &
              wpa_supplicant -B -c/etc/wpa_supplicant/wpa_supplicant.conf -iwlan0
	      sleep 5 # kui ei pane taustale siis kylmub siia wlan puhul!
            else
              echo $0 failed to set wlan0 up
            fi
        fi
        dhcpcd wlan0
        #sleep 5
    elif [ `dmesg | tail -333 | grep cdc_ether | grep eth1 | tail -1 | grep -v unregister | wc -l` -gt 0 ]; then # USB tethering
      echo $0 starting USB tethering on device eth1... # >> $LOG
      ip link set eth1 up # saab ka ilma
      dhcpcd eth1
      #sleep 5
    elif [ `ip addr | grep eth0 | grep -v NO-CARRIER | wc -l` -gt 0 ]; then # ethernet LAN
      echo $0 starting LAN on device eth0... # >> $LOG
      dhcpcd eth0 # et igal pool ja alati vorku saaks
      ip addr add 10.0.0.111/24 broadcast 10.0.0.255 dev eth0 # staatiline igaks juhuks arvuti kylgepistmiseks

    else
        echo "$0 could not find any device (from wlan0, eth1, eth0) to connect..." # >> $LOG
    fi
    }


########### MAIN #######################

failcount=/tmp/conn_restore.failcount  # /tmp ei ole flash

. /root/d4c/appcfg.sh # setting common variables
cd $SQLDIR

if [ ! -f mb.py -o ! -f minimalmodbus.py ]; then
   echo MISSING mb.py or minimalmodbus.py!
   echo $0 reports MISSING mb.py or minimalmodbus.py # >> $LOG
fi

if [ ! -f $VPNON ]; then
   echo MISSING $VPNON!
   #echo $0 reports MISSING $VPNON # >> $LOG
   sync
   exit 1
fi

if [ ! -f $failcount ]; then
   echo 0 > $failcount
fi

#echo starting to ping


upp=`cat /proc/uptime | cut -d"." -f1`

if [ `testrun ping -c1 $PING_IP1` -gt 0 -a `testrun ping -c1 $PING_IP2` -gt 0 ]; then # kumbki ei vasta
    conn # first try to restore
    sleep 1
    if [ `testrun ping -c1 $PING_IP1` -gt 0 -a `testrun ping -c1 $PING_IP2` -gt 0 ]; then
        conn # one retry
        sleep 1
        if [ `testrun ping -c1 $PING_IP1` -gt 0 -a `testrun ping -c1 $PING_IP2` -gt 0 ]; then
            fcount=`cat $failcount | head -1`
            if [ $upp -gt $TOUT -a $fcount -gt $MAXCONNFAIL ];then
                fullstop $IOMBA # mbus address of 5v feeding io board as parameter
            else
                fcount=`expr $fcount + 1`
                msg="connectivity lost but uptime ${upp} or ping failcount $fcount too low to reboot... limits $TOUT and $MAXCONNFAIL"
                echo $msg
                echo $fcount > $failcount
                exit 1
            fi
        fi
    fi
else # conn ok on first try
    echo conn ok
    if [ `date +%s` -lt 1430983028 ]; then
        if [ ! -x $CHKTIME ]; then
            echo $0 reporting MISSING $CHKTIME
        else
            if [ $upp -gt 100 ]; then
                $CHKTIME &
            fi
        fi
    fi
    echo 0 > $failcount

    if [ $upp -lt $TOUT ]; then
        $VPNON # start vpn together with every reboot, after the connectivity established
    fi
fi
exit 0

## END ###

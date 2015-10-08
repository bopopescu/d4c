#!/usr/bin/sh
#test time once a day
# 7 7 * * * /root/d4c/chk_time.sh

#####
if /usr/bin/tty -s ; then
    echo "${0} interactive shell, using stdout"
else
    exec 0</dev/null
    exec>>/root/d4c/appd.log 2>&1
fi
####


TIMEOK=0

if [ `/usr/local/bin/ps1 ntpd | wc -l` -gt 0 ]; then
    killall -TERM ntpd
    echo old ntpd process killed...
fi

/usr/bin/ntpd -gq &  # will hang with no connection
sleep 10

if [ `/usr/local/bin/ps1 ntpd | wc -l` -eq 0 ]; then # ntpd finished, time should be correct
    TIMEOK=1
    #echo ntpd success...
    if [ `date +%s` -gt 1430983028 ]; then # double checking
        if [ ! "$RTC" = "0" ]; then
            /usr/bin/hwclock -w &
            echo time written into RTC
            exit 0
        else
	    echo no RTC $RTC to write...
	fi
    else
        echo still wrong time...
        exit 1
    fi
    exit 0
else
    killall -TERM ntpd
    if ntpdate 212.47.200.1
    then
       echo ntpdate 212.47.200.1 worked
       exit 0
    else
       echo got no time... chk connectivity.
       exit 1
    fi
fi

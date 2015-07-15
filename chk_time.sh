#!/usr/bin/sh
#test time once a day
# 7 7 * * * /root/d4c/chk_time.sh

exec 0</dev/null
exec>>/tmp/appd.log 2>&1

TIMEOK=0

if [ `/usr/local/bin/ps1 ntpd | wc -l` -gt 0 ]; then
    killall -TERM ntpd
    echo old ntpd process killed...
fi

/usr/bin/ntpd -gq &  # will hang with no connection
sleep 10

if [ `ps1 ntpd | wc -l` -eq 0 ]; then # ntpd finished, time should be correct
    TIMEOK=1
    #echo ntpd success...
    if [ `date +%s` -gt 1430983028 ]; then # double checking
        if test -e /dev/rtc0; then
            /usr/bin/hwclock -w &
            echo time written into RTC
            exit 0
        fi
    else
        echo still wrong time...
        exit 1
    fi
    exit 0
else
    echo got no time...
    exit 1
fi

#!/usr/bin/bash
#####
if /usr/bin/tty -s ; then
    echo "${0} interactive shell, using stdout"
else
    exec 0</dev/null
    exec>>/root/d4c/appd.log 2>&1
fi
####

cd /root/d4c

# try to restart vpn and eventually restart if no appd is present
if [ `/usr/local/bin/ps1 appd | grep -v chk | wc -l` -eq 0 ]; then # no appd.sh proc
    echo $0 found NO appd process...
    if [ `tail -2 appd.log | grep "found NO appd process" | wc -l` -eq 0 ]; then # something still going on

        if [ `/usr/local/bin/ps1 vpn | grep inactive | wc -l` -gt 0 ]; then
            echo replacing temporary vpn with permanent one. killing old vpn...
            /root/d4c/vpnoff
            sleep 2
        fi
        
        if [ `/usr/local/bin/ps1 vpn | wc -l` -eq 0 ]; then # no vpn
            echo starting vpn. checking time...
            /root/d4c/chk_time.sh
            sleep 1
            echo starting permanent vpn...
            openvpn --cd /etc/openvpn --daemon --config itvilla.conf
            # should also send ip and apver error to monitoring!
        fi

    else # nothing happening since last few executions
        if [ `tail -5 appd.log | grep "found NO appd process" | wc -l` -gt 1 ]; then # no appd suring several checks
            echo $0 going to power cut NOW
            sync
            python mb.py 1 277 9
            python mb.py 1 999 feed
            echo "### REBOOTING #####"
            #reboot # just in case python fails or mba different
        fi
    fi
else
    echo appd ok
fi



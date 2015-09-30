#!/usr/bin/bash
exec 0</dev/null
exec>>/root/d4c/appd.log 2>&1

# try to restart vpn and eventually restart if no appd is present
if [ `/root/d4c/ps1 appd | wc -l` -eq 0 ]; then # no appd.sh proc
    echo $0 found NO appd process...
    if [ `tail -2 appd.log | grep "found NO appd process" | wc -l` -eq 0 ]; then # something still going on
     
        if [ `/root/d4c/ps1 vpn | wc -l` -gt 0 ]; then
            echo replacing temporary vpn with permanent one. killing old vpn...
            /root/d4c/vpnoff
            sleep 2
        else
            echo checking time...
            /root/d4c/chk_time.sh
            sleep 1
            echo starting vpn...
            openvpn --cd /etc/openvpn --daemon --config itvilla.conf
        fi
        
    else # nothing happening since last few executions
        if [ `tail -5 appd.log | grep "found NO appd process" | wc -l` -gt 1 ]; then # no appd suring several checks
            echo $0 going to power cut NOW
            sync
            python mb.py 1 277 9
            python mb.py 1 999 feed
            reboot # just in case python fails or mba different
        fi
    fi
fi



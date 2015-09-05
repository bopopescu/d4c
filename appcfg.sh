#this is the configuration file  to be read by appd.sh started by local.rc
ID=000101100000
APP=/root/d4c/main_monitor.py # controller application
IOMBA=1 
# previous is modbus address of io card it5888 inside the controller

# the env variables below should be pretty stable
RESCUE=/root/d4c/main_rescue.py
HOSTNAME=d4c_controller
VPNON=/root/d4c/vpnon
CHKTIME=/root/d4c/chk_time.sh
CHKCONN=/root/d4c/conn_restore.sh
LOG=/root/d4c/appd.log # tee seda /tmp kaudu!
TOUT=1000 
# previous is min required uptime to power cut or reboot in case of no connectivity
MAXCONNFAIL=5
# no reboot below previous $CHKCONN tries
SQLDIR=/root/d4c
MAXCONNFAIL=5
PING_IP1=208.67.222.222
PING_IP2=8.8.8.8
PING_VPN=10.200.0.1
MONIP=46.183.73.35
MONPORT=44445


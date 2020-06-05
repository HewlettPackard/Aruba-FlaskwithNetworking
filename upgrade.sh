spinner()
{
local pid=$1
local delay=0.1
local spinstr='|/-\'
echo "$pid" > "/tmp/.spinner.pid"
echo ""
printf " $2 "
while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
local temp=${spinstr#?}
printf " [%c]  " "$spinstr"
local spinstr=$temp${spinstr%"$temp"}
sleep $delay
printf "\b\b\b\b\b\b"
done
printf "    \b\b\b\b"
}

tput reset
tput civis

echo "########## Carius release 1.41 upgrade ##########"
echo "Ensure that you have an active Internet connection with an acceptable speed (at least 10Mbps recommended)"
# First step is to check whether you are logged in as root
# and which Ubuntu version is running. Carius requires 18.04 or later

if [[ `id -u` != 0 ]]; then
echo "Must be root to run script"
exit
fi

wget -q --spider http://google.com

if [ $? -eq 0 ]; then
echo "There is an active Internet connection"
else
echo "Offline. Check your Internet connection"
exit
fi

UbuntuRelease=$(lsb_release -rs)

if [ "`echo "${UbuntuRelease} < 18.04" | bc`" -eq 1 ]; then
echo "System requirement is Ubuntu LTS 18.04 or higher"
exit
else
IFS=':' read -r var1 var2 <<< "$(lsb_release -d)"
echo "Upgrading to Carius version 1.41 on $var2"
fi

# Second step is to upgrade and update Ubuntu

add-apt-repository universe -y  > /dev/null
(dpkg --configure -a > /dev/null) & spinner $! "Verify DPKG consistency....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq upgrade  &>/dev/null) & spinner $! "Upgrading the system to ensure that it is up to date....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq update  &>/dev/null) & spinner $! "Updating the system to ensure that it is up to date....."


# Run the Python upgrade script. This updates the database and sets the software release in the globalvars

python3 ./bash/upgrade.py

(pip3 install --default-timeout=100 pyshark > /dev/null) & spinner $! "Installing Pyshark....."
(pip3 install --default-timeout=100 netmiko > /dev/null) & spinner $! "Installing Python3 netmiko library....."

echo ""
echo " Upgrade the app"


if [ ! -d "/var/www/html/log" ]; then
mkdir /var/www/html/log
fi

touch /var/www/html/log/cleanup.log
touch /var/www/html/log/topology.log
touch /var/www/html/log/ztp.log
touch /var/www/html/log/listener.log

chmod 777 /var/www/html/log/

service carius stop

rm -f /var/www/html/bash/initztp.cfg > /dev/null
cp ./bash/listener.sh /var/www/html/bash/listener.sh > /dev/null
cp ./bash/listener.py /var/www/html/bash/listener.py > /dev/null
rm -f /var/www/html/bash/trace.pcap > /dev/null
cp ./bash/trackerclasses.py /var/www/html/bash/trackerclasses.py > /dev/null
cp ./bash/trackers.py /var/www/html/bash/trackers.py > /dev/null
cp ./bash/ztpclasses.py /var/www/html/bash/ztpclasses.py > /dev/null
cp ./classes/classes.py /var/www/html/classes/classes.py > /dev/null
cp ./classes/infoblox.py /var/www/html/classes/infoblox.py > /dev/null
cp ./classes/phpipam.py /var/www/html/classes/phpipam.py > /dev/null
cp ./classes/sysadmin.py /var/www/html/classes/sysadmin.py > /dev/null
cp ./classes/ztp.py /var/www/html/classes/ztp.py > /dev/null
cp ./static/ztpdevice.js /var/www/html/static/ztpdevice.js > /dev/null
rm -f /var/www/html/static/ztpprofile.js > /dev/null
rm -f /var/www/html/templates/ztpprofile.html > /dev/null
cp ./templates/navbar.html /var/www/html/templates/navbar.html > /dev/null
cp ./templates/sysconf.html /var/www/html/templates/sysconf.html > /dev/null
cp ./templates/syslog.html /var/www/html/templates/syslog.html > /dev/null
cp ./templates/ztpdevice.html /var/www/html/templates/ztpdevice.html > /dev/null
cp ./templates/ztplog.html /var/www/html/templates/ztplog.html > /dev/null
cp ./views/auth.py /var/www/html/views/auth.py > /dev/null
cp ./views/ztp.py /var/www/html/views/ztp.py > /dev/null
cp ./bash/defaultztp.cfg /var/www/html/bash/defaultztp.cfg > /dev/null
cp ./bash/mgmtztp.cfg /var/www/html/bash/mgmtztp.cfg > /dev/null
cp ./bash/upgrade.py /var/www/html/bash/upgrade.py > /dev/null
cp ./bash/ztpdhcp6k.cfg /home/tftpboot/ztpdhcp6k.cfg > /dev/null
cp ./bash/ztpdhcp8k.cfg /home/tftpboot/ztpdhcp8k.cfg > /dev/null
cp ./templates/showztpdevice.html /var/www/html/templates/showztpdevice.html > /dev/null
cp ./bash/topologyclasses.py /var/www/html/bash/topologyclasses.py > /dev/null
cp ./classes/arubaoscx.py /var/www/html/classes/arubaoscx.py > /dev/null
cp ./classes/classes.py /var/www/html/classes/classes.py > /dev/null
cp ./classes/switch.py /var/www/html/classes/switch.py > /dev/null
cp ./templates/showcxdevice.html /var/www/html/templates/showcxdevice.html > /dev/null
cp ./__init__.py /var/www/html/__init__.py > /dev/null 

cp ./bash/cleanupclasses.py /var/www/html/bash/cleanupclasses.py > /dev/null
cp ./classes/arubaoscx.py /var/www/html/classes/arubaoscx.py > /dev/null
cp ./classes/arubaosswitch.py /var/www/html/arubaosswitch.py > /dev/null
cp ./classes/clearpass.py /var/www/html/classes/clearpass.py > /dev/null
cp ./classes/mobility.py /var/www/html/classes/mobility.py > /dev/null
cp ./classes/switch.py /var/www/html/classes/switch.py > /dev/null
cp ./classes/sysadmin.py /var/www/html/classes/sysadmin.py > /dev/null
cp ./classes/topology.py /var/www/html/classes/topology.py > /dev/null
cp ./classes/trackers.py /var/www/html/classes/trackers.py > /dev/null
cp ./install.sh /var/www/html/install.sh > /dev/null
cp ./static/clearpass.js /var/www/html/static/clearpass.js > /dev/null
cp ./static/deviceinfo.js /var/www/html/static/deviceinfo.js > /dev/null
cp ./static/interfaceinfo.js /var/www/html/static/interfaceinfo.js > /dev/null
cp ./static/linechart.js /var/www/html/static/linechart.js > /dev/null
cp ./static/switch.js /var/www/html/static/switch.js > /dev/null
cp ./static/sysconf.js /var/www/html/static/sysconf.js > /dev/null
cp ./static/updatedeviceinfo.js /var/www/html/static/updatedeviceinfo.js > /dev/null
cp ./templates/clearpass.html /var/www/html/templates/clearpass.html > /dev/null
cp ./templates/dhcptracker.html /var/www/html/templates/dhcptracker.html > /dev/null
cp ./templates/monitorprocess.html /var/www/html/templates/monitorprocess.html > /dev/null
cp ./templates/showcxdevice.html /var/www/html/templates/showcxdevice.html > /dev/null
cp ./templates/snmptracker.html /var/www/html/templates/snmptracker.html > /dev/null
cp ./templates/switch.html /var/www/html/templates/switch.html > /dev/null
cp ./templates/syslog.html /var/www/html/templates/syslog.html > /dev/null
cp ./templates/sysmon.html /var/www/html/templates/sysmon.html > /dev/null
cp ./templates/ztpdevice.html /var/www/html/templates/ztpdevice.html > /dev/null
cp ./templates/cpendpoints.html /var/www/html/templates/cpendpoints.html > /dev/null
cp ./templates/cpservices.html /var/www/html/templates/cpservices.html > /dev/null
cp ./templates/cptrusts.html /var/www/html/templates/cptrusts.html > /dev/null
cp ./views/deviceview.py /var/www/html/views/deviceview.py > /dev/null
cp ./views/sysadmin.py /var/www/html/views/sysadmin.py > /dev/null
cp ./views/topo.py /var/www/html/views/topo.py > /dev/null
cp ./views/devices.py /var/www/html/views/devices.py > /dev/null

chmod 777 /var/www/html/bash/listener.sh
chmod 777 /var/www/html/bash/ztp.sh

dos2unix -q /var/www/html/bash/listener.sh >/dev/null
dos2unix -q /var/www/html/bash/ztp.sh >/dev/null

service carius start

echo " ######### Carius upgrade to version 1.41 completed ##########"
echo " Navigate with your browser to http://a.b.c.d:8080   where a.b.c.d is the IP address of the Carius server"

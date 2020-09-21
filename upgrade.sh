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

echo "########## Carius release 2.1 upgrade ##########"
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
echo "Upgrading to Carius version 2.1 on $var2"
fi

# Second step is to upgrade and update Ubuntu

add-apt-repository universe -y  > /dev/null
(dpkg --configure -a > /dev/null) & spinner $! "Verify DPKG consistency....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq upgrade  &>/dev/null) & spinner $! "Upgrading the system to ensure that it is up to date....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq update  &>/dev/null) & spinner $! "Updating the system to ensure that it is up to date....."

(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install libsasl2-dev &> /dev/null) & spinner $! "Installing Cyrus Simple Authentication Service Layer....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install python-dev &> /dev/null) & spinner $! "Installing Python extension library....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install libldap2-dev &> /dev/null) & spinner $! "Installing LDAP library....."


# Run the Python upgrade script. This updates the database and sets the software release in the globalvars


(pip3 install --default-timeout=100 pyshark > /dev/null) & spinner $! "Installing Pyshark....."
(pip3 install --default-timeout=100 netmiko > /dev/null) & spinner $! "Installing Python3 netmiko library....."
(pip3 install --default-timeout=100 websockets > /dev/null) & spinner $! "Installing Python3 websockets library....."
(pip3 install --default-timeout=100 ldap3 > /dev/null) & spinner $! "Installing Python LDAP3 library....."


if [ ! -d "/var/www/html/log" ]; then
mkdir /var/www/html/log
fi

touch /var/www/html/log/cleanup.log
touch /var/www/html/log/topology.log
touch /var/www/html/log/ztp.log
touch /var/www/html/log/listener.log
touch /var/www/html/log/telemetry.log

chmod 777 /var/www/html/log/

service carius stop

echo ""
echo " Upgrading the app"

rm -f /var/www/html/bash/initztp.cfg > /dev/null
rm -f /var/www/html/bash/trace.pcap > /dev/null
rm -f /var/www/html/static/ztpprofile.js > /dev/null
rm -f /var/www/html/templates/ztpprofile.html > /dev/null


cp ./__init__.py /var/www/html/__init__.py  > /dev/null
cp ./startapp.sh /var/www/html/startapp.sh  > /dev/null
cp ./views/ /var/www/html/ -r > /dev/null
cp ./static/ /var/www/html/ -r > /dev/null
cp ./templates/ /var/www/html/ -r > /dev/null
cp ./classes/ /var/www/html/ -r > /dev/null
cp ./bash/ /var/www/html/ -r > /dev/null
cp ./bash/ztpdhcp6k.cfg /home/tftpboot/ztpdhcp6k.cfg > /dev/null
cp ./bash/ztpdhcp8k.cfg /home/tftpboot/ztpdhcp8k.cfg > /dev/null

if [ ! -d "/var/www/html/images" ]; then
mkdir /var/www/html/images
fi
chmod 777 /var/www/html/images/
chmod 777 /var/www/html/images

chmod 777 /var/www/html/bash/listener.sh
chmod 777 /var/www/html/bash/ztp.sh
chmod 777 /var/www/html/bash/telemetry.sh

dos2unix -q /var/www/html/bash/listener.sh >/dev/null
dos2unix -q /var/www/html/bash/ztp.sh >/dev/null
dos2unix -q /var/www/html/bash/telemetry.sh >/dev/null
dos2unix -q /var/www/html/startapp.sh >/dev/null


python3 ./bash/upgrade.py


service carius start

echo " ######### Carius upgrade to version 2.1 completed ##########"
echo " Navigate with your browser to http://a.b.c.d:8080   where a.b.c.d is the IP address of the Carius server"

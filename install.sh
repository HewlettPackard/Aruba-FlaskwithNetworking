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



echo "########## CommPass 3.0 Installation ##########"
echo "Ensure that you have an active Internet connection with an acceptable speed (at least 10Mbps recommended)"
# First step is to check whether you are logged in as root
# and which Ubuntu version is running. CommPass requires Ubuntu 18.04 or later

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


if [ "`echo "${UbuntuRelease} < 18.04" | bc`" -eq 1  ]; then
echo "System requirement is Ubuntu LTS 18.04 or higher"
exit
else
IFS=':' read -r var1 var2 <<< "$(lsb_release -d)"
echo "Installing CommPass on $var2"
fi

# Second step is to upgrade and update Ubuntu

add-apt-repository universe -y  > /dev/null
(dpkg --configure -a > /dev/null) & spinner $! "Verify DPKG consistency....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq upgrade  &>/dev/null) & spinner $! "Upgrading the system to ensure that it is up to date....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq update  &>/dev/null) & spinner $! "Updating the system to ensure that it is up to date....."


# Next is to install all the dependencies

(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install net-tools  &>/dev/null) & spinner $! "Installing Net tools....."
# (DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install nodejs  &>/dev/null) & spinner $! "Installing node.js....."
# (DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install npm  &>/dev/null) & spinner $! "Installing node.js package manager....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install dos2unix  &>/dev/null) & spinner $! "Installing Dos2Unix....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install tshark  &>/dev/null) & spinner $! "Installing Tshark....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install apache2 &> /dev/null) & spinner $! "Installing Apache2....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install tftpd-hpa &> /dev/null) & spinner $! "Installing TFTP Daemon....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install mysql-server &> /dev/null) & spinner $! "Installing Mysql Server....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install mysql-client &> /dev/null) & spinner $! "Installing Mysql Client....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install libsasl2-dev &> /dev/null) & spinner $! "Installing Cyrus Simple Authentication Service Layer....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install python-dev &> /dev/null) & spinner $! "Installing Python extension library....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 install libldap2-dev &> /dev/null) & spinner $! "Installing LDAP library....."


if ! [ -x "$(command -v python3)" ]; then
echo 'Error: Python is not installed or it is the incorrect command. CommPass requires the   python3   command' >&2
exit 1
fi

# Create tftp folder

if [ ! -d "/home/tftpboot" ]; then
mkdir /home/tftpboot
fi

chmod -R 777 /home/tftpboot
chown -R tftp /home/tftpboot

# Create the configuration file for TFTP

cat > /etc/default/tftpd-hpa  << ENDOFFILE
# /etc/default/tftpd-hpa
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/home/tftpboot"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure"
ENDOFFILE

# Restart TFTP daemon

service tftpd-hpa restart

# Install the Python modules

(DEBIAN_FRONTEND=noninteractive apt-get -y install -qq -o=Dpkg::Use-Pty=0 python3-pip &> /dev/null) & spinner $! "Installing Python3 PIP....."

(pip3 install --default-timeout=100 requests > /dev/null) & spinner $! "Installing Python3 requests library....."
(pip3 install --default-timeout=100 pygal > /dev/null) & spinner $! "Installing Python3 pygal library....."
(pip3 install --default-timeout=100 flask> /dev/null) & spinner $! "Installing Python3 flask library....."
(pip3 install --default-timeout=100 flask-bootstrap > /dev/null) & spinner $! "Installing Python3 flask bootstrap library....."
(pip3 install --default-timeout=100 flask-login > /dev/null) & spinner $! "Installing Python3 flask login library....."
(pip3 install --default-timeout=100 pyopenssl > /dev/null) & spinner $! "Installing Python3 OpenSSL library....."
(pip3 install --default-timeout=100 pycryptodome > /dev/null) & spinner $! "Installing Python3 pycryptodome library....."
(pip3 install --default-timeout=100 pymysql > /dev/null) & spinner $! "Installing Python3 pymysql library....."
(pip3 install --default-timeout=100 schedule > /dev/null) & spinner $! "Installing Python3 schedule library....."
(pip3 install --default-timeout=100 pyshark > /dev/null) & spinner $! "Installing Python3 pyshark library....."
(pip3 install --default-timeout=100 psutil > /dev/null) & spinner $! "Installing Python3 psutil library....."
(pip3 install --default-timeout=100 paramiko > /dev/null) & spinner $! "Installing Python3 paramiko library....."
(pip3 install --default-timeout=100 netmiko > /dev/null) & spinner $! "Installing Python3 netmiko library....."
(pip3 install --default-timeout=100 waitress > /dev/null) & spinner $! "Installing Python3 waitress library....."
(pip3 install --default-timeout=100 websockets > /dev/null) & spinner $! "Installing Python3 websockets library....."
(pip3 install --default-timeout=100 ldap3 > /dev/null) & spinner $! "Installing Python LDAP3 library....."

# Mysql user, database and table structure creation
# Depending on the Mysql version, the structure is different

varA=($(echo $(mysql -uroot -e "select version();") | tr ')' '\n'))
varB=($(echo "${varA[1]}" | tr '-' '\n'))
varC=($(echo "${varB[0]}" | tr '.' '\n'))
mysqlversion=${varC[0]}${varC[1]}

echo ""
echo ""
echo " Configure the database"
if [[ "$mysqlversion" < "80" ]] ;
then
 mysql -uroot < ./doc/mysqltable57.txt
else
 mysql -uroot < ./doc/mysqltable80.txt
fi

if [ ! -d "/var/www/html" ]; then
mkdir /var/www/html
fi

echo " Installing the app"
cp ./__init__.py /var/www/html/__init__.py  > /dev/null
cp ./startapp.sh /var/www/html/startapp.sh  > /dev/null
cp ./uninstall.sh /var/www/html/uninstall.sh  > /dev/null
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

echo " Configuring the app"

# activeInterface=$(route | grep '^default' | grep -o '[^ ]*$')
# cat > /var/www/html/bash/globals.json  << ENDOFFILE
# {"idle_timeout": "3000", "pcap_location": "/var/www/html/bash/trace.pcap", "retain_dhcp": "15", "retain_snmp": "15", "retain_ztplog": "5", "retain_listenerlog": "5", "retain_cleanuplog": "5", "retain_topologylog": "5","retain_syslog": "15","retain_telemetrylog": "5","secret_key": "ArubaRocks!!!!!!", "appPath": "/var/www/html/", "softwareRelease": "2.2", "sysInfo": "","activeInterface":"$activeInterface","ztppassword":"ztpinit","landingpage":"/","authsource":"local"}
# ENDOFFILE
chmod 777 /var/www/html/bash/listener.sh
chmod 777 /var/www/html/bash/cleanup.sh
chmod 777 /var/www/html/bash/topology.sh
chmod 777 /var/www/html/bash/ztp.sh
chmod 777 /var/www/html/bash/telemetry.sh
chmod 777 /var/www/html/bash/device-upgrade.sh
chmod 777 /var/www/html/bash/data-collector.sh


if [ ! -d "/var/www/html/log" ]; then
mkdir /var/www/html/log
fi

touch /var/www/html/log/cleanup.log
touch /var/www/html/log/topology.log
touch /var/www/html/log/ztp.log
touch /var/www/html/log/listener.log
touch /var/www/html/log/telemetry.log
touch /var/www/html/log/device-upgrade.log
touch /var/www/html/log/data-collector.log
touch /var/www/html/log/device-upgrade.log
touch /var/www/html/log/system.log

chmod 777 /var/www/html/log/

dos2unix -q /var/www/html/startapp.sh >/dev/null
dos2unix -q /var/www/html/bash/listener.sh >/dev/null
dos2unix -q /var/www/html/bash/cleanup.sh >/dev/null
dos2unix -q /var/www/html/bash/topology.sh >/dev/null
dos2unix -q /var/www/html/bash/ztp.sh >/dev/null
dos2unix -q /var/www/html/bash/telemetry.sh >/dev/null
dos2unix -q /var/www/html/bash/device-upgrade.sh >/dev/null
chmod 777 /var/www/html/startapp.sh
chmod +x /var/www/html/startapp.sh

tput cnorm

# Final step is to automatically start the startapp.sh when the system boots

cat > /etc/systemd/system/CommPass.service  << ENDOFFILE
[Unit]
Description=CommPass
After=mysql.service
[Service]
Type=simple
WorkingDirectory=/var/www/html
ExecStart=/var/www/html/startapp.sh
[Install]
WantedBy=default.target
ENDOFFILE

chmod 664 /etc/systemd/system/CommPass.service
systemctl daemon-reload &> /dev/null
systemctl enable CommPass.service &> /dev/null
systemctl start CommPass.service &> /dev/null

echo " ######### CommPass release 3.0 installation completed ##########"
echo " Navigate with your browser to http://a.b.c.d:8080   where a.b.c.d is the IP address of the CommPass server"
echo " The default login credentials are:"
echo " Username:  admin"
echo " There is no password, you are prompted to change the admin password after login as admin user"
echo ""

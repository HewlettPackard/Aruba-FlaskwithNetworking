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



echo "########## Uninstall CommPass 3.0 ##########"
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


IFS=':' read -r var1 var2 <<< "$(lsb_release -d)"
echo "Uninstalling CommPass from $var2"


# Uninstall the Python modules












(pip3 uninstall -y --default-timeout=100 paramiko > /dev/null) & spinner $! "Uninstalling Python3 paramiko library....."
(pip3 uninstall -y --default-timeout=100 netmiko > /dev/null) & spinner $! "Uninstalling Python3 netmiko library....."
(pip3 uninstall -y --default-timeout=100 waitress > /dev/null) & spinner $! "Uninstalling Python3 waitress library....."
(pip3 uninstall -y --default-timeout=100 websockets > /dev/null) & spinner $! "Uninstalling Python3 websockets library....."
(pip3 uninstall -y --default-timeout=100 ldap3 > /dev/null) & spinner $! "Uninstalling Python LDAP3 library....."
(pip3 uninstall -y --default-timeout=100 schedule > /dev/null) & spinner $! "Uninstalling Python3 schedule library....."
(pip3 uninstall -y --default-timeout=100 psutil > /dev/null) & spinner $! "Uninstalling Python3 psutil library....."
(pip3 uninstall -y --default-timeout=100 pyshark > /dev/null) & spinner $! "Uninstalling Python3 pyshark library....."
(pip3 uninstall -y --default-timeout=100 pymysql > /dev/null) & spinner $! "Uninstalling Python3 pymysql library....."
(pip3 uninstall -y --default-timeout=100 pycryptodome > /dev/null) & spinner $! "Uninstalling Python3 pycryptodome library....."
(pip3 uninstall -y --default-timeout=100 pyopenssl > /dev/null) & spinner $! "Uninstalling Python3 OpenSSL library....."
(pip3 uninstall -y --default-timeout=100 flask-login > /dev/null) & spinner $! "Uninstalling Python3 flask login library....."
(pip3 uninstall -y --default-timeout=100 flask-bootstrap > /dev/null) & spinner $! "Uninstalling Python3 flask bootstrap library....."
(pip3 uninstall -y --default-timeout=100 flask> /dev/null) & spinner $! "Uninstalling Python3 flask library....."
(pip3 uninstall -y --default-timeout=100 pygal > /dev/null) & spinner $! "Uninstalling Python3 pygal library....."
(pip3 uninstall -y --default-timeout=100 requests > /dev/null) & spinner $! "Uninstalling Python3 requests library....."
(DEBIAN_FRONTEND=noninteractive apt-get -y purge -qq -o=Dpkg::Use-Pty=0 python3-pip &> /dev/null) & spinner $! "Uninstalling Python3 PIP....."

rm -R /var/www/html/*  > /dev/null

rm /etc/systemd/system/CommPass.service
systemctl daemon-reload &> /dev/null


echo ""
echo ""
echo " Remove the database"
mysql -uroot < ./doc/uninstallmysql.txt


# Next is to uninstall all the dependencies

(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge net-tools  &>/dev/null) & spinner $! "Uninstalling Net tools....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge dos2unix  &>/dev/null) & spinner $! "Uninstalling Dos2Unix....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge tshark  &>/dev/null) & spinner $! "Uninstalling Tshark....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge apache2 &> /dev/null) & spinner $! "Uninstalling Apache2....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge tftpd-hpa &> /dev/null) & spinner $! "Uninstalling TFTP Daemon....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge mysql-server &> /dev/null) & spinner $! "Uninstalling Mysql Server....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge mysql-client &> /dev/null) & spinner $! "Uninstalling Mysql Client....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge libsasl2-dev &> /dev/null) & spinner $! "Uninstalling Cyrus Simple Authentication Service Layer....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge python-dev &> /dev/null) & spinner $! "Uninstalling Python extension library....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq -y -o=Dpkg::Use-Pty=0 purge libldap2-dev &> /dev/null) & spinner $! "Uninstalling LDAP library....."
(DEBIAN_FRONTEND=noninteractive apt -qq -y -o=Dpkg::Use-Pty=0 autoremove &> /dev/null) & spinner $! "Remove dependencies....."


# Remove tftp folder

if [  -d "/home/tftpboot" ]; then
rm -R /home/tftpboot
fi

tput cnorm

echo " ######### CommPass release 3.0 uninstallation completed ##########"

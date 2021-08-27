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
echo "Upgrading to Carius version 2.3 on $var2"
fi

# Second step is to upgrade and update Ubuntu

add-apt-repository universe -y  > /dev/null
(dpkg --configure -a > /dev/null) & spinner $! "Verify DPKG consistency....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq upgrade  &>/dev/null) & spinner $! "Upgrading the system to ensure that it is up to date....."
(DEBIAN_FRONTEND=noninteractive apt-get -qq update  &>/dev/null) & spinner $! "Updating the system to ensure that it is up to date....."


service carius stop

echo ""
echo " Upgrading the app"


python3 ./bash/upgrade.py

service carius start

echo " ######### Carius upgrade to version 2.3 completed ##########"
echo " Navigate with your browser to http://a.b.c.d:8080   where a.b.c.d is the IP address of the Carius server"

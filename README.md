# Aruba Networks app that allows you to:
- Monitor AOS-CX, AOS-Switch, ClearPass and Mobility controllers
- Telemetry with AOS-CX (Websockets)
- Perform Zero Touch Provisioning on AOS-CX switches
- Simple topology view
- SNMP, Syslog and DHCP tracker
- Role Based Access Control
- And more...

Supported Operating System is Ubuntu LTS 18.x, 19.x or 20.x

Installation instructions:
Have a default Ubuntu installation, 4 GB RAM, 2 CPU

Login into your Ubuntu host as root

Clone the repository into your home folder:

git clone https://github.com/HewlettPackard/Aruba-FlaskwithNetworking.git

cd Aruba-FlaskwithNetworking

chmod 777 ./install.sh    or      chmod +x ./upgrade.sh

Run the ./install.sh script

If you are already running version 1.2 or 1.3, you can upgrade the app:

chmod 777 ./upgrade.sh      or     chmod +x ./upgrade.sh

Run the ./upgrade.sh script
#!/bin/bash

BASTION_IP=$(cat bastion_data.json | jq -r '.elastic_ip')

ssh -i "key_dohmh_nyc.pem" ubuntu@$BASTION_IP << EOF

sudo adduser ely --gecos " , , , " --disabled-password
echo "ely:ely" | sudo chpasswd
sudo usermod -aG sudo ely

sudo adduser eddie --gecos " , , , " --disabled-password
echo "eddie:eddie" | sudo chpasswd
sudo usermod -aG sudo eddie

sudo adduser karla --gecos " , , , " --disabled-password
echo "karla:karla" | sudo chpasswd
sudo usermod -aG sudo karla

sudo adduser leo --gecos " , , , " --disabled-password
echo "leo:leo" | sudo chpasswd
sudo usermod -aG sudo leo

sudo adduser mathus --gecos " , , , " --disabled-password
echo "mathus:mathus" | sudo chpasswd
sudo usermod -aG sudo mathus

sudo adduser liliana --gecos " , , , " --disabled-password
echo "liliana:liliana" | sudo chpasswd
sudo usermod -aG sudo liliana

sudo sed -i 's|#PubkeyAuthentication yes|PubkeyAuthentication yes|g' /etc/ssh/sshd_config
sudo sed -i 's|PasswordAuthentication no|PasswordAuthentication yes|g' /etc/ssh/sshd_config

sudo service sshd restart

EOF

ssh-copy-id -f -i './authorized_keys/public_key_ely.pub' ely@$BASTION_IP
ssh-copy-id -f -i './authorized_keys/public_key_eddie.pub' eddie@$BASTION_IP
ssh-copy-id -f -i './authorized_keys/public_key_karla.pub' karla@$BASTION_IP
ssh-copy-id -f -i './authorized_keys/public_key_leo.pub' leo@$BASTION_IP
ssh-copy-id -f -i './authorized_keys/public_key_mathus.pub' mathus@$BASTION_IP
ssh-copy-id -f -i './authorized_keys/public_key_liliana.pub' liliana@$BASTION_IP

ssh -i "key_dohmh_nyc.pem" ubuntu@$BASTION_IP << EOF

sudo sed -i 's|PasswordAuthentication yes|PasswordAuthentication no|g' /etc/ssh/sshd_config

sudo service sshd restart

EOF

# Copying the pem file into the bastion.
scp -i ./key_dohmh_nyc.pem key_dohmh_nyc.pem ubuntu@$BASTION_IP:/home/ubuntu/key_dohmh_nyc.pem


#ssh -i "key_dohmh_nyc.pem" ubuntu@$BASTION_IP << EOF
#ssh -i "key_dohmh_nyc.pem" ubuntu@$BASTION_IP << EOF
#sudo apt-get update
#sudo apt install postgresql-client-common
#sudo apt-get install postgresql-client

#psql -h hostname -p portNumber -U userName dbName -W

#EOF
#EOF

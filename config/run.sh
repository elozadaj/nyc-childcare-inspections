#!/bin/bash

rm -rf key_dohmh_nyc.pem

#Creating EC2 key pairs.
echo 'Executing createKeyPair.py ...'
python createKeyPair.py
echo 'createKeyPair.py executed successfully'

chmod 400 key_dohmh_nyc.pem

echo 'Executing createAWSResources.py ...'
python createAWSResources.py
echo 'createAWSResources.py executed successfully'

./addAuthorizedUsers.sh

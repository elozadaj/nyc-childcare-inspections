#!/bin/bash

#Creating EC2 key pairs.
echo 'Executing createKeyPair.py ...'
python createKeyPair.py
echo 'createKeyPair.py executed successfully'

chmod 400 key-dohmh-nyc.pem

echo 'Executing createAWSResources.py ...'
python createAWSResources.py
echo 'createAWSResources.py executed successfully'

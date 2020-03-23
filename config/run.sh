#!/bin/bash

#Creating EC2 key pairs.
python createKeyPair.py
echo 'createKeyPair.py executed successfully'

chmod 400 ec2-keypair.pem

python createAWSResources.py
echo 'createAWSResources.py executed successfully'
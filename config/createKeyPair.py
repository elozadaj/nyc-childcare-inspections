import boto3
from botocore.exceptions import ClientError

KEY_NAME = 'key-dohmh-nyc'
ec2 = boto3.client('ec2')

try:
    keyPair = ec2.create_key_pair(KeyName = KEY_NAME)
except ClientError as error:
	if error.response['Error']['Code'] == 'InvalidKeyPair.Duplicate':
		response = ec2.delete_key_pair(KeyName = KEY_NAME)
		keyPair = ec2.create_key_pair(KeyName = KEY_NAME)
	else:
	    sys.exit('Unknown error!')
except:
	sys.exit('Unknown error!')

privateKey = str(keyPair['KeyMaterial'])

try:
    pemFile = open('key-dohmh-nyc.pem','w')
    pemFile.write(privateKey)
except:
	print('Couldn\'t write to ec2-keypair.pem')
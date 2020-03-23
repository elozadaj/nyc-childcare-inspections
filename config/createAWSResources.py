import boto3

KEY_NAME = 'ec2-keypair'

BASTION_AMI = 'ami-0e01ce4ee18447327' # Amazon Linux 2 AMI
BASTION_TYPE = 't2.micro'

ec2 = boto3.resource('ec2')

# Create bastion
bastion = ec2.create_instances(
    ImageId = BASTION_AMI,
    MinCount = 1,
    MaxCount = 1,
    InstanceType = BASTION_TYPE,
    KeyName = KEY_NAME
)

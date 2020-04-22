import boto3
import json
import sys

ec2 = boto3.resource('ec2')
client = boto3.client('ec2')
rds_client = boto3.client('rds')

###############################################################################
# Create VPC
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "vpc_dohmh_nyc"}])
vpc.wait_until_available()

print("VPC created ...")

###############################################################################
# Create private subnet
public_subnet = vpc.create_subnet(CidrBlock='10.0.0.0/24')
private_subnet = vpc.create_subnet(
    CidrBlock='10.0.1.0/24',
    AvailabilityZone='us-east-2a'
)

print("Public and private subnets created ...")

###############################################################################
# Create and attach internet gateway to VPC
internet_gateway = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

# Create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=internet_gateway.id
)

# Associate the route table with the public subnet
route_table.associate_with_subnet(SubnetId=public_subnet.id)
route_table.associate_with_subnet(SubnetId=private_subnet.id)

print("Public subnet reachable from external network  ...")

###############################################################################
# Create security groups

public_sec_group = ec2.create_security_group(
    GroupName='public_dohmh_nyc',
    Description='Public security group allowing incoming traffic',
    VpcId=vpc.id)

public_sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

private_sec_group = ec2.create_security_group(
    GroupName='private_dohmh_nyc',
    Description='Private security group',
    VpcId=vpc.id)

private_sec_group.authorize_ingress(
    IpPermissions=[
        {
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22,
            'UserIdGroupPairs': [{ 'GroupId': public_sec_group.id }],
        }
    ]
)

print("Security groups created ...")

###############################################################################
# Create bastion

#BASTION_AMI = 'ami-0e01ce4ee18447327' # Amazon Linux 2 AMI
BASTION_AMI = 'ami-0fc20dd1da406780b' # Ubuntu AMI
BASTION_TYPE = 't2.micro'
KEY_NAME = 'key_dohmh_nyc'

ec2_instances = ec2.create_instances(
    ImageId = BASTION_AMI,
    MinCount = 1,
    MaxCount = 1,
    InstanceType = BASTION_TYPE,
    KeyName = KEY_NAME,
    NetworkInterfaces=[{
    	'SubnetId': public_subnet.id,
    	'DeviceIndex': 0,
    	'AssociatePublicIpAddress': True,
    	'Groups': [public_sec_group.group_id]
    	}]
)

bastion = ec2_instances[0]
bastion.wait_until_running()
print("Bastion created ...")

###############################################################################
# Create private ec2 instance

ec2_instances = ec2.create_instances(
    ImageId = BASTION_AMI,
    MinCount = 1,
    MaxCount = 1,
    InstanceType = BASTION_TYPE,
    KeyName = KEY_NAME,
    NetworkInterfaces=[{
    	'SubnetId': private_subnet.id,
    	'DeviceIndex': 0,
    	'AssociatePublicIpAddress': False,
    	'Groups': [private_sec_group.group_id]
    	}]
)

private_ec2 = ec2_instances[0]
private_ec2.wait_until_running()
print("Private ec2 created ...")

###############################################################################
# Create AWS PostgreSQL database

another_private_subnet = vpc.create_subnet(
    CidrBlock='10.0.2.0/24',
    AvailabilityZone='us-east-2b'
)

rds_client.create_db_subnet_group(
    DBSubnetGroupName='dbsubnetgroup_dohmh_nyc',
    DBSubnetGroupDescription='Private database subnet group for dohmh_nyc database',
    SubnetIds=[private_subnet.id, another_private_subnet.id]
)

private_db = rds_client.create_db_instance(
    DBName='db_dohmh_nyc',
    DBInstanceIdentifier='DohmhNYC',
    AllocatedStorage=20,
    DBInstanceClass='db.t2.micro',
    Engine='postgres',
    MasterUsername='dohmh_nyc',
    MasterUserPassword='dohmh_nyc',
    VpcSecurityGroupIds=[
        private_sec_group.group_id,
    ],
    AvailabilityZone='us-east-2b',
    DBSubnetGroupName='dbsubnetgroup_dohmh_nyc',
    BackupRetentionPeriod=0,
    Port=5432,
    MultiAZ=False,
    EngineVersion='11.6',
    AutoMinorVersionUpgrade=False,
    LicenseModel='postgresql-license',
    PubliclyAccessible=True,
    Tags=[
        {
            'Key': 'description',
            'Value': 'Database for storing data for dohmh_nyc project'
        },
    ],
    StorageType='gp2',
    StorageEncrypted=False,
    CopyTagsToSnapshot=False,
    MonitoringInterval=0,
    EnableIAMDatabaseAuthentication=False,
    EnablePerformanceInsights=False,
    DeletionProtection=False,
    MaxAllocatedStorage=1000
)

print("Private database created ...")

###############################################################################
# Create and attach an elastic IP to the bastion

elastic_ip = client.allocate_address(Domain='vpc')
response = client.associate_address(
    AllocationId=elastic_ip['AllocationId'],
    InstanceId=bastion.id
)

print(private_db)
print('###############################################################################')
print(private_db['DBInstance'])
# TODO: WAIT UNTIL READY (DB)

###############################################################################
# Write aws data into a json file
try:
    data_dict = {
        'elastic_ip': elastic_ip['PublicIp'],
        'private_db_endpoint': private_db['DBInstance']['Endpoint']
    }
    with open('bastion_data.json', 'w') as file:
        json.dump(data_dict, file)
except (OSError, ValueError):  # file does not exist or is empty/invalid
    sys.exit('Error while saving bastion elastic ip into bastion_data.json')

print("Elastic IP created and associated to bastion")

###############################################################################

print("All AWS resources were created ...")

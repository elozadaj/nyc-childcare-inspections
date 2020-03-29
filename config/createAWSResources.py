import boto3

ec2 = boto3.resource('ec2')


# Create VPC
vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc.create_tags(Tags=[{"Key": "Name", "Value": "vpc-dohmh-nyc"}])
vpc.wait_until_available()

print("VPC created ...")

# Create and attach internet gateway to VPC
internet_gateway = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)

print("Internet gateway created and associated with VPC ...")

# Create a route table and a public route
route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=internet_gateway.id
)
print("Route table created and associated with Internet Gateway...")


# Create private subnet
private_subnet = vpc.create_subnet(CidrBlock='10.0.0.0/24')

# Create public subnet
public_subnet = vpc.create_subnet(CidrBlock='10.0.1.0/24')

# Associate the route table with the public subnet
route_table.associate_with_subnet(SubnetId=public_subnet.id)

print("Public and private subnets created ...")

# Create security groups

private_sec_group = ec2.create_security_group(
    GroupName='private_dohmh_nyc',
    Description='Private security group',
    VpcId=vpc.id)

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

print("Security groups created ...")


# Create bastion
BASTION_AMI = 'ami-0e01ce4ee18447327' # Amazon Linux 2 AMI
BASTION_TYPE = 't2.micro'
KEY_NAME = 'key-dohmh-nyc'

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

# Create and attach an elastic IP to the bastion
client = boto3.client('ec2')

elastic_ip = client.allocate_address(Domain='vpc')
response = client.associate_address(
    AllocationId=elastic_ip['AllocationId'],
    InstanceId=bastion.id
)

print("Elastic IP created and associated to bastion")

print("All AWS resources were created ...")

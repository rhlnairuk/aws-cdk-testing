# my_server_setup.py

from aws_cdk import aws_ec2 as ec2, aws_rds as rds, aws_elasticloadbalancingv2 as elbv2
from aws_cdk import Stack
from constructs import Construct
from aws_cdk import App

web_server_user_data = ec2.UserData.for_linux()
web_server_user_data.add_commands(
    "echo 'Configuring as web server'",
    "# Add application server specific setup commands here",
)

app_server_user_data = ec2.UserData.for_linux()
app_server_user_data.add_commands(
    "echo 'Configuring as app server'",
    "# Add application server specific setup commands here",
)

class NetworkingStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        env_type = self.node.try_get_context('env_type')
        resource_prefix = self.node.try_get_context(env_type)['resourcePrefix']

    # Create a VPC
        self.vpc = ec2.Vpc(
            self, f"{resource_prefix}VPC",
            max_azs=3,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="PrivateSubnetWithNat",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="IsolatedSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )
        # Import the existing VPC
        #vpc = ec2.Vpc.from_lookup(self, "VPC", vpc_name="devEnv01")

class DevStack(Stack):
    def __init__(self, scope: Construct, id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        env_type = self.node.try_get_context('env_type')
        resource_prefix = self.node.try_get_context(env_type)['resourcePrefix']
        # Create an Application Load Balancer
        alb = elbv2.ApplicationLoadBalancer(
            self, f"{resource_prefix}ALB",
            vpc=vpc,
            internet_facing=True
        )

        # Create an EC2 instance for the web server
        web_server = ec2.Instance(
            self, f"{resource_prefix}WebServers",
            user_data = web_server_user_data,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            vpc_subnets={'subnet_type': ec2.SubnetType.PUBLIC}
        )

        # Create an EC2 instance for the application server
        app_server = ec2.Instance(
            self, f"{resource_prefix}AppServers",
            user_data = app_server_user_data,
            instance_type=ec2.InstanceType("t3.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux2(),
            vpc=vpc,
            vpc_subnets={'subnet_type': ec2.SubnetType.PRIVATE_WITH_EGRESS}
        )

        # Create an RDS instance
        db = rds.DatabaseInstance(
            self, f"{resource_prefix}DatabaseServers",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_15_2),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets={'subnet_type': ec2.SubnetType.PRIVATE_ISOLATED}
        )
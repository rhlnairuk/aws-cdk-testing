#!/usr/bin/env python3
from os import environ
from aws_cdk import App
from dev_setup_stacks import NetworkingStack, DevStack
import aws_cdk as cdk

app = App()
if "CDK_DEPLOY_ACCOUNT" in environ:
    env_default = cdk.Environment(region="us-east-1", account=environ['CDK_DEPLOY_ACCOUNT'])
else:
    env_default = cdk.Environment(region="us-east-1")
# DevStack(app, "DevStack",
#         env=cdk.Environment(region="us-east-1")
NetworkStack = NetworkingStack(app, "NetworkingStack", env=env_default)
DevStack = DevStack(app, "DevStack", env=env_default, vpc=NetworkStack.vpc)
DevStack.add_dependency(NetworkStack)
# If you don't specify 'env', this stack will be environment-agnostic.
# Account/Region-dependent features and context lookups will not work,
# but a single synthesized template can be deployed anywhere.

# Uncomment the next line to specialize this stack for the AWS Account
# and Region that are implied by the current CLI configuration.

# env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region=os.getenv('CDK_DEFAULT_REGION')),

# Uncomment the next line if you know exactly what Account and Region you
# want to deploy the stack to. */

# env=cdk.Environment(account='123456789012', region='us-east-1'),

# For more information, see https://docs.aws.amazon.com/cdk/latest/guide/environments.html


app.synth()

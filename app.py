#!/usr/bin/env python3
import os
import subprocess

import aws_cdk as cdk
from aws_cdk import Aspects

from src.aspects.check_ssh_open_aspects import CheckSshOpenAspect
from src.aspects.display_construct_path import DisplayConstructPathAspect
from src.config import load_config
from src.stacks import NetworkStack

app = cdk.App()

# Suppress VPC availabilityZones list-token warning (SecurityGroupStack uses from_vpc_attributes)
app.node.set_context(
    "@aws-cdk/aws-ec2:vpcAttributeIsListTokenavailabilityZones",
    True,
)

env_name = os.getenv("ENV", "dev")
config = load_config(env_name)
env = cdk.Environment(
    account=os.getenv("CDK_DEFAULT_ACCOUNT"),
    region=os.getenv("CDK_DEFAULT_REGION"),
)

NetworkStack(
    app,
    f"{config.tags['project']}-{env_name}",
    config=config,
    env=env,
)

Aspects.of(app).add(DisplayConstructPathAspect())
Aspects.of(app).add(CheckSshOpenAspect())

if os.getenv("CDK_DEPLOY"):
    subprocess.run(["cdk", "deploy", "--require-approval", "never"], check=True)
else:
    app.synth()

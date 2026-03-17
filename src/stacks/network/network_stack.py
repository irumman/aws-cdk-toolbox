import aws_cdk as cdk
from aws_cdk import Stack, Tags
from constructs import Construct

from src.config import AppConfig

from .security_group_stack import SecurityGroupStack
from .vpc_stack import VpcStack


class NetworkStack(Stack):
    """Root stack containing VpcStack and SecurityGroupStack as nested stacks."""

    def __init__(self, scope: Construct, construct_id: str, config: AppConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for key, value in config.tags.items():
            Tags.of(self).add(key, value)

        vpc_nested = VpcStack(self, "VpcStack", config=config)
        SecurityGroupStack(
            self,
            "SecurityGroupStack",
            config=config,
            vpc_id=vpc_nested.vpc.vpc_id,
            availability_zones=cdk.Fn.join(",", vpc_nested.vpc.availability_zones),
            availability_zones_count=config.vpc.max_azs,
        ).add_dependency(vpc_nested)

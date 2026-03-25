import aws_cdk as cdk
from aws_cdk import Tags
from constructs import Construct

from src.config import AppConfig

from .security_group_stack import SecurityGroupStack
from .vpc_stack import VpcStack


class NetworkStack(cdk.NestedStack):
    """Nested stack containing VpcStack and SecurityGroupStack; exposes VPC attributes for parent."""

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

        # Expose VPC tokens as attributes so ProjectStack can pass them to AlbStack.
        # CDK automatically converts these cross-nested-stack references into
        # CloudFormation Outputs on this stack and GetAtt references in the parent.
        # Note: avoid 'availability_zones' — that name is reserved by the CDK base class.
        self.vpc_id: str = vpc_nested.vpc.vpc_id
        self.vpc_availability_zones: str = cdk.Fn.join(",", vpc_nested.vpc.availability_zones)
        self.public_subnet_ids: str = cdk.Fn.join(
            ",", [s.subnet_id for s in vpc_nested.vpc.public_subnets]
        )

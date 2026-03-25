import aws_cdk as cdk
from aws_cdk import Stack, Tags
from constructs import Construct

from src.config import AppConfig
from src.stacks.load_balancer import AlbStack
from src.stacks.network import NetworkStack


class ProjectStack(Stack):
    """Root stack that nests NetworkStack and, optionally, AlbStack."""

    def __init__(self, scope: Construct, construct_id: str, config: AppConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for key, value in config.tags.items():
            Tags.of(self).add(key, value)

        network_stack = NetworkStack(self, "NetworkStack", config=config)

        if config.load_balancer.application.enabled:
            alb_name = f"{config.tags['project']}-{config.tags['environment']}"
            alb_stack = AlbStack(
                self,
                "AlbStack",
                config=config,
                alb_name=alb_name,
                vpc_id=network_stack.vpc_id,
                availability_zones=network_stack.vpc_availability_zones,
                availability_zones_count=config.vpc.max_azs,
                public_subnet_ids=network_stack.public_subnet_ids,
            )
            alb_stack.add_dependency(network_stack)

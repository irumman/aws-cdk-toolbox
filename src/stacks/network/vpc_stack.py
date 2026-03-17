import aws_cdk as cdk
from aws_cdk import Tags, aws_ec2 as ec2
from constructs import Construct

from src.config import AppConfig


class VpcStack(cdk.NestedStack):

    def __init__(self, scope: Construct, construct_id: str, config: AppConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        for key, value in config.tags.items():
            Tags.of(self).add(key, value)

        subnet_configuration = []

        if config.vpc.public_subnet.enabled:
            subnet_configuration.append(
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=config.vpc.public_subnet.cidr_mask,
                )
            )

        if config.vpc.private_subnet.enabled:
            subnet_configuration.append(
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=config.vpc.private_subnet.cidr_mask,
                )
            )

        self.vpc = ec2.Vpc(
            self,
            "Vpc",
            vpc_name=config.vpc.name,
            ip_addresses=ec2.IpAddresses.cidr(config.vpc.cidr),
            max_azs=config.vpc.max_azs,
            nat_gateways=config.vpc.nat_gateways,
            subnet_configuration=subnet_configuration,
        )
        cdk.CfnOutput(self, "VpcId", value=self.vpc.vpc_id, description="VPC ID")
        cdk.CfnOutput(
            self,
            "AvailabilityZones",
            value=cdk.Fn.join(",", self.vpc.availability_zones),
            description="Comma-separated availability zones",
        )

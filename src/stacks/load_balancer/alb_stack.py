import aws_cdk as cdk
from aws_cdk import Tags, aws_ec2 as ec2, aws_elasticloadbalancingv2 as elbv2
from constructs import Construct

from src.config import AppConfig


class AlbStack(cdk.NestedStack):
    """Nested stack that creates an internet-facing Application Load Balancer in public subnets."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: AppConfig,
        alb_name: str,
        vpc_id: str,
        availability_zones: str,
        availability_zones_count: int,
        public_subnet_ids: str,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            parameters={
                "VpcId": vpc_id,
                "AvailabilityZones": availability_zones,
                "PublicSubnetIds": public_subnet_ids,
            },
            **kwargs,
        )

        for key, value in config.tags.items():
            Tags.of(self).add(key, value)

        vpc_id_param = cdk.CfnParameter(self, "VpcId", type="String")
        az_param = cdk.CfnParameter(self, "AvailabilityZones", type="String")
        public_subnet_ids_param = cdk.CfnParameter(self, "PublicSubnetIds", type="String")

        az_list = cdk.Fn.import_list_value(az_param.value_as_string, availability_zones_count)

        vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "Vpc",
            vpc_id=vpc_id_param.value_as_string,
            availability_zones=az_list,
        )

        subnets = []
        for i in range(availability_zones_count):
            subnet_id = cdk.Fn.select(
                i, cdk.Fn.split(",", public_subnet_ids_param.value_as_string)
            )
            az = cdk.Fn.select(i, az_list)
            subnets.append(
                ec2.Subnet.from_subnet_attributes(
                    self,
                    f"PublicSubnet{i}",
                    subnet_id=subnet_id,
                    availability_zone=az,
                )
            )

        self.alb = elbv2.ApplicationLoadBalancer(
            self,
            "Alb",
            load_balancer_name=alb_name,
            vpc=vpc,
            internet_facing=True,
            vpc_subnets=ec2.SubnetSelection(subnets=subnets),
        )

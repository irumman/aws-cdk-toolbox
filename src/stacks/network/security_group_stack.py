import aws_cdk as cdk
from aws_cdk import Tags, aws_ec2 as ec2
from constructs import Construct

from src.config import AppConfig, SecurityGroupIngressRuleConfig


def _port_from_rule(rule: SecurityGroupIngressRuleConfig) -> ec2.Port:
    """Build CDK Port from ingress rule config."""
    if rule.protocol == "tcp":
        if rule.from_port == rule.to_port:
            return ec2.Port.tcp(rule.from_port)
        return ec2.Port.tcp_range(rule.from_port, rule.to_port)
    if rule.protocol == "udp":
        if rule.from_port == rule.to_port:
            return ec2.Port.udp(rule.from_port)
        return ec2.Port.udp_range(rule.from_port, rule.to_port)
    if rule.protocol == "icmp":
        return ec2.Port.icmp_ping()
    raise ValueError(f"Unsupported protocol: {rule.protocol}")


class SecurityGroupStack(cdk.NestedStack):
    """Creates security groups in a VPC with ingress rules from config."""

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        config: AppConfig,
        vpc_id: str,
        availability_zones: str,
        availability_zones_count: int,
        **kwargs,
    ) -> None:
        super().__init__(
            scope,
            construct_id,
            parameters={
                "VpcId": vpc_id,
                "AvailabilityZones": availability_zones,
            },
            **kwargs,
        )

        for key, value in config.tags.items():
            Tags.of(self).add(key, value)

        vpc_id_param = cdk.CfnParameter(self, "VpcId", type="String")
        az_param = cdk.CfnParameter(self, "AvailabilityZones", type="String")

        # Fn.importListValue tells CDK this is a proper list (not an opaque list token)
        # which suppresses the fromVpcAttributes availabilityZones warning
        az_list = cdk.Fn.import_list_value(az_param.value_as_string, availability_zones_count)

        vpc = ec2.Vpc.from_vpc_attributes(
            self,
            "Vpc",
            vpc_id=vpc_id_param.value_as_string,
            availability_zones=az_list,
        )

        self.security_groups: list[ec2.SecurityGroup] = []

        for i, sg_config in enumerate(config.security_groups):
            sg = ec2.SecurityGroup(
                self,
                f"SecurityGroup{i}",
                security_group_name=sg_config.name,
                description=sg_config.description or f"Security group: {sg_config.name}",
                vpc=vpc,
                allow_all_outbound=True,
            )
            self.security_groups.append(sg)

            for rule in sg_config.ingress_rules:
                peer = ec2.Peer.ipv4(rule.cidr)
                port = _port_from_rule(rule)
                sg.add_ingress_rule(peer, port, rule.description)

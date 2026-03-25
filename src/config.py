from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel
from pydantic_settings import BaseSettings


class SubnetConfig(BaseModel):
    enabled: bool = False
    cidr_mask: int = 24


class VpcConfig(BaseModel):
    name: str = ""
    cidr: str = ""
    max_azs: int = 2
    nat_gateways: int = 0
    public_subnet: SubnetConfig = SubnetConfig(enabled=True, cidr_mask=24)
    private_subnet: SubnetConfig = SubnetConfig(enabled=False, cidr_mask=24)


class SecurityGroupIngressRuleConfig(BaseModel):
    """Config for a single security group ingress rule."""

    from_port: int
    to_port: int
    protocol: str = "tcp"  # tcp, udp, icmp
    cidr: str  # e.g. "10.0.0.0/8" or "0.0.0.0/0"
    description: str | None = None


class SecurityGroupConfig(BaseModel):
    """Config for a security group (name, description, and ingress rules)."""

    name: str
    description: str | None = None
    ingress_rules: list[SecurityGroupIngressRuleConfig] = []


class ApplicationLoadBalancerConfig(BaseModel):
    enabled: bool = False


class LoadBalancerConfig(BaseModel):
    application: ApplicationLoadBalancerConfig = ApplicationLoadBalancerConfig()


class AppConfig(BaseSettings):
    tags: dict[str, str] = {}
    vpc: VpcConfig = VpcConfig()
    security_groups: list[SecurityGroupConfig] = []
    load_balancer: LoadBalancerConfig = LoadBalancerConfig()

    model_config = {"env_nested_delimiter": "__"}


def load_config(env: str) -> AppConfig:
    config_path = Path(__file__).parent.parent / "config" / f"{env}.yaml"
    with open(config_path) as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}
    return AppConfig(**data)

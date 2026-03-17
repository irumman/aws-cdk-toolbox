import jsii
from aws_cdk import (
    IAspect,
    Stack,
    aws_ec2 as ec2,
    Annotations
)


@jsii.implements(IAspect)
class CheckSshOpenAspect:
    def visit(self, node):
        if isinstance(node, ec2.CfnSecurityGroup):
            # Stack.of(node).resolve() converts the JSII proxy into a plain Python list of dicts
            rules = Stack.of(node).resolve(node.security_group_ingress)

            if not rules:
                return

            for rule in rules:
                if (
                    rule.get("ipProtocol") == "tcp"
                    and rule.get("fromPort") <= 22 <= rule.get("toPort")
                    and rule.get("cidrIp") == "0.0.0.0/0"
                ):
                    Annotations.of(node).add_error(
                        "Security Group allows SSH (port 22) from 0.0.0.0/0. "
                        "This is a violation of security policy."
                    )

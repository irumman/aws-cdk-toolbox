import jsii
from aws_cdk import IAspect


@jsii.implements(IAspect)
class DisplayConstructPathAspect:
    """Aspect that prints each construct's path and class name during synthesis."""

    def visit(self, construct_visited) -> None:
        path = construct_visited.node.path
        class_name = construct_visited.__class__.__name__
        print(f"{path} - {class_name}")

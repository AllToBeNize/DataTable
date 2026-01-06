from collections.abc import Iterable
from dt.core.schema.containers.base import Container


class ArrayContainer(Container):
    def validate(self, value) -> bool:
        if not isinstance(value, Iterable) or isinstance(value, (str, bytes)):
            return False
        return all(self.value_type.validate_value(v) for v in value)

    def default(self):
        return []

    def to_repr(self) -> dict:
        return {
            "container": "array",
            "value": self.value_type.to_repr(),
        }

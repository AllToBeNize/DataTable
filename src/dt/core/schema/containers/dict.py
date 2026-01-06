from dt.core.schema.containers.base import Container


class DictContainer(Container):
    def validate(self, value) -> bool:
        if not isinstance(value, dict):
            return False
        return all(self.value_type.validate_value(v) for v in value.values())

    def default(self):
        return {}

    def to_repr(self) -> dict:
        return {
            "container": "dict",
            "value": self.value_type.to_repr(),
        }

from dt.core.schema.containers.base import Container
from dt.core.schema.types.base import BaseType


class DictContainer(Container):
    def __init__(self, value_type: BaseType, key_type: BaseType | None = None):
        super().__init__(value_type)
        self.key_type = key_type

    def validate(self, value) -> bool:
        if not isinstance(value, dict):
            return False

        for k, v in value.items():
            if self.key_type and not self.key_type.validate_value(k):
                return False
            if not self.value_type.validate_value(v):
                return False

        return True

    def default(self):
        return {}

    def to_repr(self) -> dict:
        data = {
            "container": "dict",
            "value": self.value_type.to_repr(),
        }
        if self.key_type:
            data["key"] = self.key_type.to_repr()
        return data

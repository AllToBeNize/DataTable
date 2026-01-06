from dt.core.schema.types.base import BaseType


class EnumType(BaseType):
    def __init__(self, name: str, values: list[str]):
        if not values:
            raise ValueError("EnumType values cannot be empty")

        self.name = name
        self.values = list(values)
        self._value_set = set(values)

    def validate_value(self, value) -> bool:
        return value in self._value_set

    def default_value(self):
        # 默认取第一个，保证稳定
        return self.values[0]

    def to_repr(self) -> dict:
        return {
            "type": "enum",
            "name": self.name,
            "values": self.values,
        }

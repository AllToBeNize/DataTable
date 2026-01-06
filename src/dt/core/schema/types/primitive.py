from dt.core.schema.types import BaseType


class IntType(BaseType):
    def __init__(self, min_value: int | None = None, max_value: int | None = None):
        self.min_value = min_value
        self.max_value = max_value

    def validate_value(self, value) -> bool:
        if not isinstance(value, int):
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def default_value(self):
        if self.min_value is not None:
            return self.min_value
        return 0

    def to_repr(self):
        return {
            "type": "int",
            "min": self.min_value,
            "max": self.max_value,
        }


class FloatType(BaseType):
    def __init__(self, min_value: float | None = None, max_value: float | None = None):
        self.min_value = min_value
        self.max_value = max_value

    def validate_value(self, value) -> bool:
        if not isinstance(value, (int, float)):
            return False
        if self.min_value is not None and value < self.min_value:
            return False
        if self.max_value is not None and value > self.max_value:
            return False
        return True

    def default_value(self):
        if self.min_value is not None:
            return float(self.min_value)
        return 0.0

    def to_repr(self):
        return {
            "type": "float",
            "min": self.min_value,
            "max": self.max_value,
        }


class BoolType(BaseType):
    def validate_value(self, value) -> bool:
        return isinstance(value, bool)

    def default_value(self):
        return False

    def to_repr(self):
        return {"type": "bool"}


class StringType(BaseType):
    def __init__(
        self,
        min_length: int | None = None,
        max_length: int | None = None,
        allow_empty: bool = True,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.allow_empty = allow_empty

    def validate_value(self, value) -> bool:
        if not isinstance(value, str):
            return False

        length = len(value)
        if not self.allow_empty and length == 0:
            return False
        if self.min_length is not None and length < self.min_length:
            return False
        if self.max_length is not None and length > self.max_length:
            return False

        return True

    def default_value(self):
        if not self.allow_empty and self.min_length:
            return " " * self.min_length
        return ""

    def to_repr(self):
        return {
            "type": "string",
            "min_length": self.min_length,
            "max_length": self.max_length,
            "allow_empty": self.allow_empty,
        }

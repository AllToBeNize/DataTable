from dt.core.schema.types.base import BaseType
from dt.core.schema.registry import SchemaRegistry


class StructType(BaseType):
    def __init__(self, schema_name: str):
        self.schema_name = schema_name

    def _get_schema(self):
        schema = SchemaRegistry.get(self.schema_name)
        if schema is None:
            raise KeyError(f"Schema not found: {self.schema_name}")
        return schema

    def validate_value(self, value) -> bool:
        return self._get_schema().validate(value)

    def default_value(self):
        return self._get_schema().default()

    def to_repr(self) -> dict:
        return {
            "type": "struct",
            "schema": self.schema_name,
        }

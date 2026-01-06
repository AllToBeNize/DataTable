# dt/core/schema/types/struct.py

from dt.core.schema.types.base import BaseType
from dt.core.schema.registry import SchemaRegistry


class StructType(BaseType):
    """
    StructType = 引用 Schema 的「值类型」
    """
    def __init__(self, schema_name: str):
        self.schema_name = schema_name
        self._schema_cache = None

    def _get_schema(self):
        if self._schema_cache is None:
            schema = SchemaRegistry.get(self.schema_name)
            if schema is None:
                raise KeyError(f"Schema not found: {self.schema_name}")
            self._schema_cache = schema
        return self._schema_cache

    def validate_value(self, value) -> bool:
        return self._get_schema().validate_struct(value)

    def default_value(self):
        return self._get_schema().default_struct()

    def to_repr(self) -> dict:
        return {
            "type": "struct",
            "schema": self.schema_name,
        }

    def __repr__(self):
        return f"StructType({self.schema_name})"

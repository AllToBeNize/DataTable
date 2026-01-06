import copy
from typing import Any

from dt.core.schema.registry import SchemaRegistry


class Row:
    """
    Row = Schema + Data + History
    """

    def __init__(self, schema_name: str, data: dict | None = None):
        self.schema_name = schema_name

        self._data: dict = data or {}

        # 历史栈
        self._undo_stack: list[dict] = []
        self._redo_stack: list[dict] = []

        self._sync_with_schema()

    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    @property
    def schema(self):
        schema = SchemaRegistry.get(self.schema_name)
        if schema is None:
            raise KeyError(f"Schema not found: {self.schema_name}")
        return schema

    def _sync_with_schema(self):
        """
        schema 变化时的数据对齐（不进入历史）
        """
        self._data = self.schema.migrate(self._data)

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def _push_undo(self):
        self._undo_stack.append(copy.deepcopy(self._data))
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False

        self._redo_stack.append(copy.deepcopy(self._data))
        self._data = self._undo_stack.pop()
        self._sync_with_schema()
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False

        self._undo_stack.append(copy.deepcopy(self._data))
        self._data = self._redo_stack.pop()
        self._sync_with_schema()
        return True

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self) -> bool:
        self._sync_with_schema()
        return self.schema.validate(self._data)

    # ------------------------------------------------------------------
    # Data access
    # ------------------------------------------------------------------

    def get(self, field_name: str, default: Any = None) -> Any:
        self._sync_with_schema()
        return self._data.get(field_name, default)

    def set(self, field_name: str, value: Any):
        self._sync_with_schema()

        fields = self.schema.fields()
        if field_name not in fields:
            raise KeyError(f"Field not in schema: {field_name}")

        field = fields[field_name]
        if not field.validate(value):
            raise ValueError(f"Invalid value for field '{field_name}': {value}")

        # 用户修改 → 进历史
        self._push_undo()
        self._data[field_name] = value

    # ------------------------------------------------------------------
    # Bulk
    # ------------------------------------------------------------------

    def update(self, values: dict):
        """
        批量修改（视为一次用户操作）
        """
        self._sync_with_schema()
        self._push_undo()

        fields = self.schema.fields()
        for name, value in values.items():
            if name not in fields:
                raise KeyError(f"Field not in schema: {name}")
            if not fields[name].validate(value):
                raise ValueError(f"Invalid value for field '{name}': {value}")
            self._data[name] = value

    # ------------------------------------------------------------------
    # Serialize
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        self._sync_with_schema()
        return copy.deepcopy(self._data)

    # ------------------------------------------------------------------
    # Debug
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Row schema={self.schema_name} "
            f"data={self._data} "
            f"undo={len(self._undo_stack)} "
            f"redo={len(self._redo_stack)}>"
        )

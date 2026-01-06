from __future__ import annotations

from typing import Dict, List, Any

from dt.core.schema.field import Field
from dt.core.schema.registry import SchemaRegistry


class FieldVersion:
    """
    一个字段在某一时刻的定义快照
    """
    def __init__(self, field: Field):
        self.field = field
        self.name = field.name
        self.type = field.type
        self.default = field.default

    def default_value(self):
        if callable(self.default):
            return self.default()
        return self.default


class FieldHistory:
    """
    一个字段的完整演化历史
    """
    def __init__(self, field: Field):
        self.versions: List[FieldVersion] = [FieldVersion(field)]

    @property
    def current(self) -> FieldVersion:
        return self.versions[-1]

    def add_version(self, field: Field):
        self.versions.append(FieldVersion(field))


class Schema:
    """
    Schema = Struct 定义 + 演化能力
    """

    def __init__(self, name: str):
        self.name = name

        # 当前字段名 -> FieldHistory
        self._fields: Dict[str, FieldHistory] = {}

        # 历史字段名 -> 当前字段名
        self._rename_map: Dict[str, str] = {}

        SchemaRegistry.register(self)

    # ------------------------------------------------------------------
    # 字段定义 API
    # ------------------------------------------------------------------

    def add_field(self, field: Field):
        if field.name in self._fields:
            raise KeyError(f"Field already exists: {field.name}")

        self._fields[field.name] = FieldHistory(field)

    def remove_field(self, name: str):
        name = self._resolve_name(name)
        if name not in self._fields:
            raise KeyError(f"Field not found: {name}")
        del self._fields[name]

    def rename_field(self, old_name: str, new_name: str):
        old_name = self._resolve_name(old_name)

        if old_name not in self._fields:
            raise KeyError(f"Field not found: {old_name}")
        if new_name in self._fields:
            raise KeyError(f"Field already exists: {new_name}")

        history = self._fields.pop(old_name)
        self._fields[new_name] = history
        self._rename_map[old_name] = new_name

        current = history.current.field
        renamed = current.clone(name=new_name)
        history.add_version(renamed)

    def change_field_type(self, name: str, new_type):
        name = self._resolve_name(name)

        if name not in self._fields:
            raise KeyError(f"Field not found: {name}")

        history = self._fields[name]
        current = history.current.field

        changed = current.clone(type=new_type)
        history.add_version(changed)

    # ------------------------------------------------------------------
    # Struct 语义（StructType 使用）
    # ------------------------------------------------------------------

    def validate(self, value: Any) -> bool:
        if not isinstance(value, dict):
            return False

        for name, history in self._fields.items():
            if name not in value:
                return False
            if not history.current.field.validate(value[name]):
                return False

        return True

    def default(self) -> dict:
        return {
            name: history.current.default_value()
            for name, history in self._fields.items()
        }

    # ------------------------------------------------------------------
    # Migration（核心能力）
    # ------------------------------------------------------------------

    def migrate(self, data: dict) -> dict:
        """
        将旧 schema 数据迁移到当前 schema
        """
        if not isinstance(data, dict):
            return self.default()

        result = {}

        # 1. 处理当前 schema 的字段
        for name, history in self._fields.items():
            value = None

            # 直接命中
            if name in data:
                value = data[name]
            else:
                # 尝试历史名字
                for old_name, new_name in self._rename_map.items():
                    if new_name == name and old_name in data:
                        value = data[old_name]
                        break

            # 类型校验 / 失败回退
            if value is not None and history.current.field.validate(value):
                result[name] = value
            else:
                result[name] = history.current.default_value()

        return result

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _resolve_name(self, name: str) -> str:
        while name in self._rename_map:
            name = self._rename_map[name]
        return name

    def fields(self) -> Dict[str, Field]:
        return {
            name: history.current.field
            for name, history in self._fields.items()
        }

    def field_history(self, name: str) -> List[FieldVersion]:
        name = self._resolve_name(name)
        return list(self._fields[name].versions)

    def __repr__(self):
        return f"<Schema {self.name} fields={list(self._fields.keys())}>"

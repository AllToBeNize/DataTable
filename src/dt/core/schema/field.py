from typing import Any, Callable
from dt.core.schema.containers.base import Container


class FieldSnapshot:
    def __init__(
        self,
        name,
        type_,
        container,
        default_value,
        default_factory,
    ):
        self.name = name
        self.type = type_
        self.container = container
        self.default_value = default_value
        self.default_factory = default_factory

    def to_repr(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.to_repr(),
            "container": self.container.to_repr() if self.container else None,
            "default": self.default_value,
            "has_default_factory": self.default_factory is not None,
        }


class Field:
    def __init__(
        self,
        name,
        type_,
        container=None,
        default=None,
        default_factory=None,
    ):
        self.name = name
        self.type = type_
        self.container = container

        self.default_value = default
        self.default_factory = default_factory

        # 历史版本（按时间顺序）
        self.history: list[FieldSnapshot] = []

    # ---------- 基础能力 ----------

    def default(self):
        if self.default_factory:
            return self.default_factory()
        return self.default_value

    def validate(self, value) -> bool:
        if self.container:
            return self.container.validate(value)
        return self.type.validate_value(value)

    # ---------- 历史记录 ----------

    def _snapshot(self):
        """保存当前状态到历史"""
        snap = FieldSnapshot(
            name=self.name,
            type_=self.type,
            container=self.container,
            default_value=self.default_value,
            default_factory=self.default_factory,
        )
        self.history.append(snap)

    # ---------- 结构演化操作 ----------

    def rename(self, new_name: str):
        if new_name == self.name:
            return

        self._snapshot()
        self.name = new_name

    def change_type(
        self,
        new_type,
        new_container=None,
        new_default=None,
        new_default_factory=None,
    ):
        self._snapshot()

        self.type = new_type
        self.container = new_container
        self.default_value = new_default
        self.default_factory = new_default_factory

    # ---------- 元信息 ----------

    def to_repr(self) -> dict:
        return {
            "name": self.name,
            "type": self.type.to_repr(),
            "container": self.container.to_repr() if self.container else None,
            "default": self.default_value,
            "history": [h.to_repr() for h in self.history],
        }

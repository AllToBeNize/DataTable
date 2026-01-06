from typing import Dict, List
from dt.core.schema.field import Field


class Schema:
    """
    描述一行数据的结构定义

    - Schema 是 Field 的容器
    - 所有结构演化操作从 Schema 进入
    - 历史记录由 Field 自己维护
    """

    def __init__(self):
        self._fields: Dict[str, Field] = {}
        self._field_order: List[str] = []

    # ------------------------------------------------------------------
    # 基础访问
    # ------------------------------------------------------------------

    @property
    def fields(self) -> Dict[str, Field]:
        return self._fields

    def get_field(self, name: str) -> Field:
        if name not in self._fields:
            raise KeyError(f"Field '{name}' does not exist")
        return self._fields[name]

    def has_field(self, name: str) -> bool:
        return name in self._fields

    # ------------------------------------------------------------------
    # 结构管理
    # ------------------------------------------------------------------

    def add_field(self, field: Field):
        """
        添加新字段
        """
        if field.name in self._fields:
            raise KeyError(f"Field '{field.name}' already exists")

        self._fields[field.name] = field
        self._field_order.append(field.name)

    def remove_field(self, name: str):
        """
        移除字段（不做历史保存）
        """
        if name not in self._fields:
            raise KeyError(f"Field '{name}' does not exist")

        del self._fields[name]
        self._field_order.remove(name)

    # ------------------------------------------------------------------
    # 结构演化
    # ------------------------------------------------------------------

    def rename_field(self, old_name: str, new_name: str):
        """
        字段改名（保持 Field 身份不变）
        """
        if old_name not in self._fields:
            raise KeyError(f"Field '{old_name}' does not exist")

        if new_name in self._fields:
            raise KeyError(f"Field '{new_name}' already exists")

        field = self._fields.pop(old_name)

        # Field 自身记录历史
        field.rename(new_name)

        self._fields[new_name] = field

        idx = self._field_order.index(old_name)
        self._field_order[idx] = new_name

    def change_field_type(
        self,
        name: str,
        new_type,
        new_container=None,
        new_default=None,
        new_default_factory=None,
    ):
        """
        修改字段类型 / 容器 / 默认值
        """
        if name not in self._fields:
            raise KeyError(f"Field '{name}' does not exist")

        field = self._fields[name]
        field.change_type(
            new_type=new_type,
            new_container=new_container,
            new_default=new_default,
            new_default_factory=new_default_factory,
        )

    # ------------------------------------------------------------------
    # 结构描述
    # ------------------------------------------------------------------

    def to_repr(self) -> dict:
        """
        用于编辑器 / 序列化 / diff 的结构描述
        """
        return {
            "fields": [
                self._fields[name].to_repr()
                for name in self._field_order
            ]
        }

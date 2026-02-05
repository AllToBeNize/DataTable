from typing import Any, Optional
from enum import Enum
from .base import SchemeBase


class ContainerType(str, Enum):
	SINGLE = "single"
	ARRAY = "array"
	MAP = "map"


class FieldDefinition(SchemeBase):
	type: str
	container: ContainerType = ContainerType.SINGLE
	key_type: Optional[str] = None  # 仅当 container 为 map 时使用
	default_value: Any = None

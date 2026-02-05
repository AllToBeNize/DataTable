from typing import List
from .base import SchemeBase


class EnumDefinition(SchemeBase):
	values: List[str] = []

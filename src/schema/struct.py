from typing import List
from .base import SchemeBase
from .field import FieldDefinition


class StructDefinition(SchemeBase):
	fields: List[FieldDefinition] = []

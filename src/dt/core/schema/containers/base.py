from abc import ABC, abstractmethod
from dt.core.schema.types.base import BaseType


class Container(ABC):
    def __init__(self, value_type: BaseType):
        self.value_type = value_type

    @abstractmethod
    def validate(self, value) -> bool:
        pass

    @abstractmethod
    def default(self):
        pass

    @abstractmethod
    def to_repr(self) -> dict:
        pass

from abc import ABC, abstractmethod


class BaseType(ABC):
    @abstractmethod
    def validate_value(self, value) -> bool:
        pass

    @abstractmethod
    def default_value(self):
        pass

    @abstractmethod
    def to_repr(self) -> dict:
        pass

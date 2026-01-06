from threading import RLock
from typing import Dict, Optional


class SchemaRegistry:
    _schemas: Dict[str, object] = {}
    _lock = RLock()

    @classmethod
    def register(cls, name: str, schema) -> None:
        if not name:
            raise ValueError("Schema name cannot be empty")

        with cls._lock:
            cls._schemas[name] = schema

    @classmethod
    def get(cls, name: str) -> Optional[object]:
        if not name:
            return None

        with cls._lock:
            return cls._schemas.get(name)

    @classmethod
    def unregister(cls, name: str) -> None:
        with cls._lock:
            cls._schemas.pop(name, None)

    @classmethod
    def clear(cls) -> None:
        with cls._lock:
            cls._schemas.clear()

    @classmethod
    def all(cls) -> Dict[str, object]:
        with cls._lock:
            return dict(cls._schemas)

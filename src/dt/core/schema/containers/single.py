from dt.core.schema.containers.base import Container


class SingleContainer(Container):
    def validate(self, value) -> bool:
        return self.value_type.validate_value(value)

    def default(self):
        return self.value_type.default_value()

    def to_repr(self) -> dict:
        return {
            "container": "single",
            "value": self.value_type.to_repr(),
        }

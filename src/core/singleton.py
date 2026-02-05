import threading


class Singleton(type):

	_instances = {}
	_lock = threading.Lock()

	@property
	def instance(cls):
		if cls not in cls._instances:
			with cls._lock:
				if cls not in cls._instances:
					cls._instances[cls] = super().__call__()
		return cls._instances[cls]

	def __call__(cls, *args, **kwargs):
		return cls.instance

	def clear_instance(cls):
		with cls._lock:
			if cls in cls._instances:
				del cls._instances[cls]

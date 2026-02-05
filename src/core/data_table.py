from typing import Dict, Any
from src.schema.table import TableDefinition


class RowData:
	def __init__(self):
		# 存储用户实际填写的数值
		self.values: Dict[str, Any] = {}
		# 记录哪些字段被手动覆盖了
		self.overridden: Dict[str, bool] = {}


class DataTable:
	def __init__(self, definition: TableDefinition):
		self.meta: TableDefinition = definition
		self.rows: Dict[str, RowData] = {}
		# 内部计数器，用于生成 NewRow_N
		self._row_counter = 0

	def _generate_unique_id(self) -> str:
		"""生成不重复的 NewRow_N 格式 ID"""
		while True:
			candidate = f"NewRow_{self._row_counter}"
			self._row_counter += 1
			if candidate not in self.rows:
				return candidate

	def get_cell(self, row_id: str, field_name: str) -> Any:
		"""读取单元格数据：优先返回覆盖值，否则返回 Schema 默认值"""
		row = self.rows.get(row_id)
		if row and row.overridden.get(field_name):
			return row.values[field_name]

		# 延迟导入避免循环引用
		from src.core.type_manager import TypeManager

		return TypeManager.instance.get_default_value(self.meta.struct_name, field_name)

	def _set_internal(self, row_id: str, field_name: str, val: Any, is_ov: bool):
		"""核心设值逻辑，由 Command 调用"""
		if row_id not in self.rows:
			self.rows[row_id] = RowData()

		row = self.rows[row_id]
		row.values[field_name] = val
		row.overridden[field_name] = is_ov

	def _add_row_internal(self, row_id: str):
		"""核心增行逻辑，由 Command 调用"""
		if row_id not in self.rows:
			self.rows[row_id] = RowData()

	def _remove_row_internal(self, row_id: str):
		"""核心删行逻辑，由 Command 调用"""
		if row_id in self.rows:
			del self.rows[row_id]

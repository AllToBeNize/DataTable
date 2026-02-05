from typing import Dict, Any
from src.schema.table import TableDefinition


class RowData:
	def __init__(self) -> None:
		self.values: Dict[str, Any] = {}
		self.overridden: Dict[str, bool] = {}


class DataTable:
	def __init__(self, definition: TableDefinition) -> None:
		self.meta: TableDefinition = definition
		self.rows: Dict[str, RowData] = {}
		self._row_counter: int = 0

	def _generate_unique_id(self) -> str:
		while True:
			candidate = f"NewRow_{self._row_counter}"
			self._row_counter += 1
			if candidate not in self.rows:
				return candidate

	def get_cell(self, row_id: str, field_name: str) -> Any:
		row = self.rows.get(row_id)
		if row and row.overridden.get(field_name):
			return row.values[field_name]

		# 延迟导入，防止循环引用
		from src.core.type_manager import TypeManager

		return TypeManager.instance.get_default_value(self.meta.struct_name, field_name)

	def _set_internal(self, row_id: str, field_name: str, val: Any, is_ov: bool) -> None:
		if row_id not in self.rows:
			self.rows[row_id] = RowData()
		row = self.rows[row_id]
		row.values[field_name] = val
		row.overridden[field_name] = is_ov

	def _add_row_internal(self, row_id: str) -> None:
		if row_id not in self.rows:
			self.rows[row_id] = RowData()

	def _remove_row_internal(self, row_id: str) -> None:
		if row_id in self.rows:
			del self.rows[row_id]

	def _rename_row_internal(self, old_id: str, new_id: str) -> None:
		if old_id not in self.rows or new_id in self.rows:
			return
		new_rows: Dict[str, RowData] = {}
		for k, v in self.rows.items():
			if k == old_id:
				new_rows[new_id] = v
			else:
				new_rows[k] = v
		self.rows = new_rows

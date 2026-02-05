import copy
from typing import Dict, Any, Optional, Union
from src.core.singleton import Singleton
from src.core.history_manager import HistoryManager, EditCommand, AddRowCommand, DeleteRowCommand, RenameRowCommand
from src.schema import StructDefinition, EnumDefinition, TableDefinition


class TypeManager(metaclass=Singleton):
	def __init__(self) -> None:
		self.struct_defs: Dict[str, StructDefinition] = {}
		self.enum_defs: Dict[str, EnumDefinition] = {}
		# 运行时动态确定类型，不再依赖头部 import
		self.tables: Dict[str, Any] = {}

	def register_schema(self, definition: Union[StructDefinition, EnumDefinition]) -> None:
		if isinstance(definition, StructDefinition):
			self.struct_defs[definition.name] = definition
		elif isinstance(definition, EnumDefinition):
			self.enum_defs[definition.name] = definition

	def create_table_instance(self, table_def: TableDefinition) -> Any:
		from src.core.data_table import DataTable

		instance = DataTable(definition=table_def)
		self.tables[table_def.name] = instance
		return instance

	def get_default_value(self, struct_name: str, field_name: str) -> Any:
		struct = self.struct_defs.get(struct_name)
		if not struct:
			return None
		for f in struct.fields:
			if f.name == field_name:
				return copy.deepcopy(f.default_value)
		return None

	def request_add_row(self, table_name: str) -> Optional[str]:
		table = self.tables.get(table_name)
		if not table:
			return None
		new_id = table._generate_unique_id()
		cmd = AddRowCommand(table, new_id)
		HistoryManager.instance.push_and_execute(cmd)
		from src.core.project_context import ProjectContext

		ProjectContext.instance.mark_dirty()
		return new_id

	def request_delete_row(self, table_name: str, row_id: str) -> None:
		table = self.tables.get(table_name)
		if not table or row_id not in table.rows:
			return
		cmd = DeleteRowCommand(table, row_id)
		HistoryManager.instance.push_and_execute(cmd)
		from src.core.project_context import ProjectContext

		ProjectContext.instance.mark_dirty()

	def request_rename_row(self, table_name: str, old_id: str, new_id: str) -> bool:
		table = self.tables.get(table_name)
		if not table or old_id not in table.rows or new_id in table.rows:
			return False
		cmd = RenameRowCommand(table, old_id, new_id)
		HistoryManager.instance.push_and_execute(cmd)
		from src.core.project_context import ProjectContext

		ProjectContext.instance.mark_dirty()
		return True

	def request_edit(self, table_name: str, row_id: str, field_name: str, new_val: Any) -> None:
		table = self.tables.get(table_name)
		if not table:
			return
		old_val = table.get_cell(row_id, field_name)
		row = table.rows.get(row_id)
		old_ov = row.overridden.get(field_name, False) if row else False
		cmd = EditCommand(table, row_id, field_name, old_val, old_ov, new_val, True)
		HistoryManager.instance.push_and_execute(cmd)
		from src.core.project_context import ProjectContext

		ProjectContext.instance.mark_dirty()

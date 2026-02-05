import copy
from typing import Dict, Any, Optional
from src.core.data_table import DataTable
from src.core.singleton import Singleton
from src.core.history_manager import HistoryManager, EditCommand, AddRowCommand
from src.schema import StructDefinition, EnumDefinition, TableDefinition


class TypeManager(metaclass=Singleton):
	def __init__(self):
		self.struct_defs: Dict[str, StructDefinition] = {}
		self.enum_defs: Dict[str, EnumDefinition] = {}
		self.tables: Dict[str, DataTable] = {}

	def register_schema(self, definition):
		if isinstance(definition, StructDefinition):
			self.struct_defs[definition.name] = definition
		elif isinstance(definition, EnumDefinition):
			self.enum_defs[definition.name] = definition

	def create_table_instance(self, table_def: TableDefinition):
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
		"""请求添加行：由 TypeManager 协调生成 ID 并压入历史栈"""
		table = self.tables.get(table_name)
		if not table:
			return None

		new_id = table._generate_unique_id()
		cmd = AddRowCommand(table, new_id)
		HistoryManager.instance.push_and_execute(cmd)

		# 联动 ProjectContext 标记脏数据
		from src.core.project_context import ProjectContext

		ProjectContext.instance.mark_dirty()
		return new_id

	def request_edit(self, table_name: str, row_id: str, field_name: str, new_val: Any):
		"""请求修改数据：由 TypeManager 协调旧值镜像并压入历史栈"""
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

import os
import json
from typing import Optional, List, Type, Any
from src.core.singleton import Singleton
from src.core.type_manager import TypeManager

# 导入你提供的 Pydantic 模型
from src.schema.enum import EnumDefinition
from src.schema.struct import StructDefinition
from src.schema.table import TableDefinition


class ProjectContext(metaclass=Singleton):
	def __init__(self) -> None:
		self.project_root: Optional[str] = None
		self.is_dirty: bool = False

	def open_project(self, root_path: str) -> None:
		self.project_root = os.path.abspath(root_path)

		# 1. 按照依赖顺序加载：Enum -> Struct -> Table
		# 使用 Pydantic 的 model_validate (Pydantic V2)
		self._load_config("enums.json", EnumDefinition)
		self._load_config("structs.json", StructDefinition)
		self._load_config("tables.json", TableDefinition)

		# 2. 加载增量数据
		self._load_workspace_data()

		self.is_dirty = False
		print(f"🚀 项目加载成功: {self.project_root}")

	def _load_config(self, filename: str, model_class: Type[Any]) -> None:
		"""利用 Pydantic 自动递归解析 JSON 列表"""
		tm = TypeManager.instance
		path = os.path.join(self.project_root, "config", filename)

		if not os.path.exists(path):
			return

		with open(path, "r", encoding="utf-8") as f:
			raw_data = json.load(f)

		for item in raw_data:
			# Pydantic 核心魔法：自动将 dict 转换为强类型对象，处理所有嵌套 FieldDefinition
			obj = model_class.model_validate(item)

			if isinstance(obj, TableDefinition):
				tm.create_table_instance(obj)
			else:
				tm.register_schema(obj)

	def _load_workspace_data(self) -> None:
		workspace_dir = os.path.join(self.project_root, "workspace")
		if not os.path.exists(workspace_dir):
			return

		tm = TypeManager.instance
		for table_name, table in tm.tables.items():
			path = os.path.join(workspace_dir, f"{table_name}.json")
			if not os.path.exists(path):
				continue

			with open(path, "r", encoding="utf-8") as f:
				content = json.load(f)
				for rid, row_dict in content.items():
					table._add_row_internal(rid)
					table.rows[rid].values = row_dict.get("values", {})
					table.rows[rid].overridden = row_dict.get("overridden", {})

	def save_project(self) -> None:
		if not self.project_root:
			return
		workspace_dir = os.path.join(self.project_root, "workspace")
		os.makedirs(workspace_dir, exist_ok=True)

		tm = TypeManager.instance
		for table_name, table in tm.tables.items():
			file_path = os.path.join(workspace_dir, f"{table_name}.json")
			# 序列化为增量字典
			save_bundle = {rid: {"values": r.values, "overridden": r.overridden} for rid, r in table.rows.items()}
			with open(file_path, "w", encoding="utf-8") as f:
				json.dump(save_bundle, f, indent=4, ensure_ascii=False)
		self.is_dirty = False

	def export_project(self, target_dir: Optional[str] = None) -> List[str]:
		from src.generators.json_exporter import JsonExporter

		export_path = target_dir or os.path.join(self.project_root, "export")
		return JsonExporter.export_all(export_path)

	def mark_dirty(self) -> None:
		self.is_dirty = True

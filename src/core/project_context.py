import os
import json
from typing import Optional
from src.core.singleton import Singleton
from src.core.type_manager import TypeManager
from src.schema import StructDefinition, EnumDefinition, TableDefinition


class ProjectContext(metaclass=Singleton):
	def __init__(self):
		self.project_root: Optional[str] = None
		self.config_path: str = ""
		self.workspace_path: str = ""
		self.is_dirty: bool = False  # 标记是否有未保存的修改

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		if exc_type is None and self.is_dirty:
			self.save_project()

	def open_project(self, root_path: str):
		"""初始化项目路径并加载所有数据"""
		self.project_root = root_path
		self.config_path = os.path.join(root_path, "config")
		self.workspace_path = os.path.join(root_path, "workspace")

		for p in [self.config_path, self.workspace_path]:
			if not os.path.exists(p):
				os.makedirs(p, exist_ok=True)

		self._reload_all_metadata()
		self._reload_all_data()
		self.is_dirty = False
		print(f"Project context initialized at: {root_path}")

	def _reload_all_metadata(self):
		"""从 config 目录加载所有的定义"""
		# 加载枚举
		self._load_json_to_manager(os.path.join(self.config_path, "enums.json"), EnumDefinition)
		# 加载结构体
		self._load_json_to_manager(os.path.join(self.config_path, "structs.json"), StructDefinition)
		# 加载表定义
		self._load_json_to_manager(os.path.join(self.config_path, "tables.json"), TableDefinition, is_table=True)

	def _load_json_to_manager(self, path, schema_cls, is_table=False):
		if not os.path.exists(path):
			return
		with open(path, "r", encoding="utf-8") as f:
			items = json.load(f)
			for item in items:
				obj = schema_cls(**item)
				if is_table:
					# 创建内存 Table 实例
					TypeManager.instance.create_table_instance(obj)
				else:
					# 注册元数据
					TypeManager.instance.register_schema(obj)

	def _reload_all_data(self):
		"""从 workspace 加载行数据"""
		for table_name, table in TypeManager.instance.tables.items():
			data_file = os.path.join(self.workspace_path, f"{table_name}.json")
			if os.path.exists(data_file):
				with open(data_file, "r", encoding="utf-8") as f:
					rows_dict = json.load(f)
					for rid_str, content in rows_dict.items():
						rid = int(rid_str)
						for f_name, val in content.get("values", {}).items():
							is_ov = content.get("overridden", {}).get(f_name, False)
							table._set_internal(rid, f_name, val, is_ov)

	def save_project(self):
		"""持久化到硬盘"""
		if not self.workspace_path:
			return

		for name, table in TypeManager.instance.tables.items():
			save_path = os.path.join(self.workspace_path, f"{name}.json")
			data_to_save = {}
			for rid, rdata in table.rows.items():
				data_to_save[rid] = {"values": rdata.values, "overridden": rdata.overridden}
			with open(save_path, "w", encoding="utf-8") as f:
				json.dump(data_to_save, f, indent=4, ensure_ascii=False)

		self.is_dirty = False
		print("Project saved to disk.")

	def mark_dirty(self):
		self.is_dirty = True

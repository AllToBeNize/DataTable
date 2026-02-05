import json
import os
import copy
from typing import List, Dict, Any
from src.core.type_manager import TypeManager


class JsonExporter:
	@staticmethod
	def export_all(export_dir: str) -> List[str]:
		"""将所有表的数据补全为全量 JSON 导出"""
		if not os.path.exists(export_dir):
			os.makedirs(export_dir, exist_ok=True)

		tm = TypeManager.instance
		exported_files: List[str] = []

		for table_name, table in tm.tables.items():
			# 找到该表对应的结构体定义
			struct_def = tm.struct_defs.get(table.meta.struct_name)
			if not struct_def:
				continue

			final_data: List[Dict[str, Any]] = []

			# 按照插入顺序遍历 rows
			for rid, row_data in table.rows.items():
				# 1. 基础行对象，包含主键
				complete_row: Dict[str, Any] = {"ID": rid}

				# 2. 遍历 Schema 定义，决定取覆盖值还是默认值
				for field in struct_def.fields:
					f_name = field.name

					if f_name in row_data.overridden and row_data.overridden[f_name]:
						# 覆盖值：由于我们存储时已经处理了嵌套，这里直接 deepcopy 即可
						complete_row[f_name] = copy.deepcopy(row_data.values[f_name])
					else:
						# 补全值：从 TypeManager 获取该字段的 Schema 默认值
						# 注意：即使是嵌套结构体，tm.get_default_value 也会返回完整的 dict 默认值
						complete_row[f_name] = tm.get_default_value(struct_def.name, f_name)

				final_data.append(complete_row)

			# 3. 写入全量文件
			output_path = os.path.join(export_dir, f"{table_name}.json")
			with open(output_path, "w", encoding="utf-8") as f:
				json.dump(final_data, f, indent=4, ensure_ascii=False)

			exported_files.append(output_path)
			print(f"[Exporter] 已生成全量表: {output_path}")

		return exported_files

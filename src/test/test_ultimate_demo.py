import os
import json
import shutil
from src.core import ProjectContext, TypeManager, HistoryManager


def setup_advanced_config(root: str):
	"""验证结构体作为容器内容，以及枚举字段"""
	config_path = os.path.join(root, "config")
	os.makedirs(config_path, exist_ok=True)

	# 1. 枚举定义
	enums = [{"name": "QualityType", "items": [{"name": "Common", "value": 0}, {"name": "Epic", "value": 1}]}]

	# 2. 结构体定义
	structs = [
		{"name": "Vec3", "fields": [{"name": "x", "type": "float", "default_value": 0.0}, {"name": "y", "type": "float", "default_value": 0.0}]},
		{
			"name": "Hero",
			"fields": [
				# SINGLE + ENUM
				{"name": "Quality", "type": "QualityType", "default_value": 0},
				# ARRAY + STRUCT (结构体数组)
				{"name": "PathPoints", "type": "Vec3", "container": "array", "default_value": [{"x": 0.0, "y": 0.0}]},
				# MAP + STRUCT (结构体字典)
				{"name": "EquipOffsets", "type": "Vec3", "container": "map", "key_type": "string", "default_value": {"Head": {"x": 0.0, "y": 5.0}}},
			],
		},
	]

	tables = [{"name": "HeroTable", "struct_name": "Hero"}]

	with open(os.path.join(config_path, "enums.json"), "w") as f:
		json.dump(enums, f)
	with open(os.path.join(config_path, "structs.json"), "w") as f:
		json.dump(structs, f)
	with open(os.path.join(config_path, "tables.json"), "w") as f:
		json.dump(tables, f)


def run_test():
	test_root = os.path.abspath("./test_data")
	if os.path.exists(test_root):
		shutil.rmtree(test_root)
	setup_advanced_config(test_root)

	ctx = ProjectContext.instance
	ctx.open_project(test_root)
	tm = TypeManager.instance
	hm = HistoryManager.instance

	print(">>> [测试 1] 验证结构体容器的默认值读取")
	rid = tm.request_add_row("HeroTable")
	path = tm.tables["HeroTable"].get_cell(rid, "PathPoints")
	offsets = tm.tables["HeroTable"].get_cell(rid, "EquipOffsets")
	print(f"默认 PathPoints (Array<Struct>): {path}")
	print(f"默认 EquipOffsets (Map<String, Struct>): {offsets}")

	print("\n>>> [测试 2] 编辑结构体容器并验证 History")
	# 修改结构体数组
	new_path = [{"x": 1.1, "y": 1.1}, {"x": 2.2, "y": 2.2}]
	tm.request_edit("HeroTable", rid, "PathPoints", new_path)

	# 撤销修改
	hm.undo()
	print(f"撤销后 PathPoints: {tm.tables['HeroTable'].get_cell(rid, 'PathPoints')}")

	# 重做修改
	hm.redo()
	print(f"重做后 PathPoints: {tm.tables['HeroTable'].get_cell(rid, 'PathPoints')}")

	print("\n>>> [测试 3] 全量导出验证 (包含 Enum 和 结构体容器)")
	export_dir = os.path.join(test_root, "export")
	ctx.export_project(export_dir)

	with open(os.path.join(export_dir, "HeroTable.json"), "r", encoding="utf-8") as f:
		data = json.load(f)
		print("\n最终全量补全导出结果:")
		print(json.dumps(data, indent=4, ensure_ascii=False))

	# 断言检查
	r = data[0]
	assert len(r["PathPoints"]) == 2, "结构体数组长度错误"
	assert r["Quality"] == 0, "嵌套枚举默认值补全错误"
	assert r["EquipOffsets"]["Head"]["y"] == 5.0, "结构体 Map 补全错误"

	print("\n✅ 结构体容器与 History 验证全部通过！")


if __name__ == "__main__":
	run_test()

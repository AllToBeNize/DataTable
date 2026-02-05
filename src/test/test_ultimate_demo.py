import os
import json
import shutil
from src.core import ProjectContext, TypeManager, HistoryManager


def setup_test_config(root: str):
	"""准备包含嵌套结构、枚举和容器的配置"""
	config_path = os.path.join(root, "config")
	os.makedirs(config_path, exist_ok=True)

	structs = [
		{"name": "Vec3", "fields": [{"name": "x", "type": "float", "default_value": 0.0}, {"name": "y", "type": "float", "default_value": 0.0}]},
		{
			"name": "Hero",
			"fields": [
				{"name": "Name", "type": "string", "default_value": "NewHero"},
				{"name": "Pos", "type": "Vec3", "default_value": {"x": 1.0, "y": 1.0}},
				{"name": "Tags", "type": "string", "container": "array", "default_value": ["Normal"]},
			],
		},
	]
	tables = [{"name": "HeroTable", "struct_name": "Hero"}]

	with open(os.path.join(config_path, "structs.json"), "w") as f:
		json.dump(structs, f)
	with open(os.path.join(config_path, "tables.json"), "w") as f:
		json.dump(tables, f)


def run_history_test():
	test_root = os.path.abspath("./history_test_project")
	if os.path.exists(test_root):
		shutil.rmtree(test_root)
	setup_test_config(test_root)

	ctx = ProjectContext.instance
	ctx.open_project(test_root)
	tm = TypeManager.instance
	hm = HistoryManager.instance

	print("=== [测试 1: 修改与撤销] ===")
	rid = tm.request_add_row("HeroTable")  # NewRow_0
	tm.request_edit("HeroTable", rid, "Name", "Saber")
	print(f"修改后 Name: {tm.tables['HeroTable'].get_cell(rid, 'Name')}")  # Saber

	hm.undo()
	print(f"撤销修改后 Name: {tm.tables['HeroTable'].get_cell(rid, 'Name')}")  # NewHero (默认值)

	hm.redo()
	print(f"重做修改后 Name: {tm.tables['HeroTable'].get_cell(rid, 'Name')}")  # Saber

	print("\n=== [测试 2: 重命名与撤销] ===")
	old_id = rid
	new_id = "Hero_001"
	tm.request_rename_row("HeroTable", old_id, new_id)
	print(f"重命名后，旧 ID 是否存在: {old_id in tm.tables['HeroTable'].rows}")  # False

	hm.undo()
	print(f"撤销重命名，旧 ID 是否恢复: {old_id in tm.tables['HeroTable'].rows}")  # True
	print(f"撤销重命名，数据是否还在: {tm.tables['HeroTable'].get_cell(old_id, 'Name')}")  # Saber

	print("\n=== [测试 3: 复杂嵌套修改还原] ===")
	# 重新命名回来以便后续测试
	hm.redo()
	tm.request_edit("HeroTable", new_id, "Pos", {"x": 99.9, "y": 99.9})
	print(f"修改 Pos 为: {tm.tables['HeroTable'].get_cell(new_id, 'Pos')}")

	hm.undo()
	print(f"撤销 Pos 修改，恢复为: {tm.tables['HeroTable'].get_cell(new_id, 'Pos')}")  # {'x': 1.0, 'y': 1.0}

	print("\n=== [测试 4: 删除行与撤销 (最关键)] ===")
	# 当前 new_id 有覆盖数据 Name="Saber"
	tm.request_delete_row("HeroTable", new_id)
	print(f"删除后行数: {len(tm.tables['HeroTable'].rows)}")  # 0

	hm.undo()
	print(f"撤销删除后行数: {len(tm.tables['HeroTable'].rows)}")  # 1
	print(f"撤销删除后，覆盖数据 'Saber' 是否找回: {tm.tables['HeroTable'].get_cell(new_id, 'Name')}")  # Saber

	print("\n=== [测试 5: 最终导出一致性验证] ===")
	# 为了验证导出，我们再随便改点东西
	tm.request_edit("HeroTable", new_id, "Tags", ["Leader", "Gold"])

	export_dir = os.path.join(test_root, "export")
	ctx.export_project(export_dir)

	with open(os.path.join(export_dir, "HeroTable.json"), "r", encoding="utf-8") as f:
		data = json.load(f)
		print("\n最终导出全量数据:")
		print(json.dumps(data, indent=4, ensure_ascii=False))

	# 断言验证最终状态
	assert data[0]["ID"] == "Hero_001"
	assert data[0]["Name"] == "Saber"
	assert data[0]["Tags"] == ["Leader", "Gold"]

	print("\n✅ HistoryManager 压力测试全部通过！")


if __name__ == "__main__":
	run_history_test()

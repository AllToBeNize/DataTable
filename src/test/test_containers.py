import os
# import json
from src.core import ProjectContext, TypeManager, HistoryManager


def run_test():
	test_root = os.path.join(os.getcwd(), "test_container_project")

	# 1. 加载项目
	ctx = ProjectContext.instance
	ctx.open_project(test_root)
	tm = TypeManager.instance
	table = tm.tables.get("ItemTable")

	if not table:
		print("错误：请先创建目录并放入上述 JSON 文件")
		return

	# 2. 添加一行并检查初始容器数据
	row_id = tm.request_add_row("ItemTable")
	print(f"--- 初始行 {row_id} 加载 ---")

	# 测试 Array 默认值
	tags = table.get_cell(row_id, "Tags")
	print(f"Array (Tags) 默认值: {tags}")  # 应该是 ["Quest", "Tradeable"]

	# 测试 Map 默认值 (嵌套结构体)
	attr_map = table.get_cell(row_id, "AttrMap")
	print(f"Map (AttrMap) 默认值: {attr_map}")  # 应该是 {'HP': {'Value': 100, 'IsPercent': False}}

	# 3. 修改 Map 数据
	print("\n--- 修改 Map 数据 ---")
	# 模拟 UI 操作：拷贝出来，修改，塞回去
	new_map = attr_map.copy()
	new_map["ATK"] = {"Value": 50, "IsPercent": True}
	tm.request_edit("ItemTable", row_id, "AttrMap", new_map)

	print(f"修改后 AttrMap: {table.get_cell(row_id, 'AttrMap')}")

	# 4. 修改 Array 数据
	print("\n--- 修改 Array 数据 ---")
	new_tags = tags + ["Legendary_Only"]
	tm.request_edit("ItemTable", row_id, "Tags", new_tags)
	print(f"修改后 Tags: {table.get_cell(row_id, 'Tags')}")

	# 5. 验证撤销对容器的影响
	print("\n--- 测试 Undo ---")
	HistoryManager.instance.undo()  # 撤销 Tags 修改
	print(f"Undo 后 Tags: {table.get_cell(row_id, 'Tags')}")  # 应回到初始

	HistoryManager.instance.undo()  # 撤销 AttrMap 修改
	print(f"再次 Undo 后 AttrMap: {table.get_cell(row_id, 'AttrMap')}")  # 应回到初始

	# 6. 保存测试
	ctx.mark_dirty()
	ctx.save_project()
	print("\n测试完成,检查 workspace/ItemTable.json")


if __name__ == "__main__":
	run_test()

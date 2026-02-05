from __future__ import annotations
import copy
from typing import List, Any, Optional, TYPE_CHECKING
from src.core.singleton import Singleton

if TYPE_CHECKING:
	from src.core.data_table import DataTable, RowData


class Command:
	def execute(self) -> None:
		raise NotImplementedError

	def undo(self) -> None:
		raise NotImplementedError


class EditCommand(Command):
	def __init__(self, table: DataTable, row_id: str, f_name: str, old_val: Any, old_ov: bool, new_val: Any, new_ov: bool) -> None:
		self.table: DataTable = table
		self.row_id: str = row_id
		self.f_name: str = f_name
		self.old_val: Any = copy.deepcopy(old_val)
		self.old_ov: bool = old_ov
		self.new_val: Any = copy.deepcopy(new_val)
		self.new_ov: bool = new_ov

	def execute(self) -> None:
		self.table._set_internal(self.row_id, self.f_name, self.new_val, self.new_ov)

	def undo(self) -> None:
		self.table._set_internal(self.row_id, self.f_name, self.old_val, self.old_ov)


class AddRowCommand(Command):
	def __init__(self, table: DataTable, row_id: str) -> None:
		self.table: DataTable = table
		self.row_id: str = row_id

	def execute(self) -> None:
		self.table._add_row_internal(self.row_id)

	def undo(self) -> None:
		self.table._remove_row_internal(self.row_id)


class DeleteRowCommand(Command):
	def __init__(self, table: DataTable, row_id: str) -> None:
		self.table: DataTable = table
		self.row_id: str = row_id
		# 备份 RowData 对象本身
		self.backup_row_data: Optional[RowData] = copy.deepcopy(table.rows.get(row_id))

	def execute(self) -> None:
		self.table._remove_row_internal(self.row_id)

	def undo(self) -> None:
		if self.backup_row_data:
			self.table.rows[self.row_id] = copy.deepcopy(self.backup_row_data)


class RenameRowCommand(Command):
	def __init__(self, table: DataTable, old_id: str, new_id: str) -> None:
		self.table: DataTable = table
		self.old_id: str = old_id
		self.new_id: str = new_id

	def execute(self) -> None:
		self.table._rename_row_internal(self.old_id, self.new_id)

	def undo(self) -> None:
		self.table._rename_row_internal(self.new_id, self.old_id)


class HistoryManager(metaclass=Singleton):
	def __init__(self, max_depth: int = 100) -> None:
		self.undo_stack: List[Command] = []
		self.redo_stack: List[Command] = []
		self.max_depth: int = max_depth

	def push_and_execute(self, cmd: Command) -> None:
		cmd.execute()
		self.undo_stack.append(cmd)
		self.redo_stack.clear()
		if len(self.undo_stack) > self.max_depth:
			self.undo_stack.pop(0)

	def undo(self) -> None:
		if self.undo_stack:
			cmd = self.undo_stack.pop()
			cmd.undo()
			self.redo_stack.append(cmd)

	def redo(self) -> None:
		if self.redo_stack:
			cmd = self.redo_stack.pop()
			cmd.execute()
			self.undo_stack.append(cmd)

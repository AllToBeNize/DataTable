import copy
from typing import List, Any
from src.core.data_table import DataTable
from src.core.singleton import Singleton


class Command:
	def execute(self):
		raise NotImplementedError

	def undo(self):
		raise NotImplementedError


class EditCommand(Command):
	def __init__(self, table: DataTable, row_id: str, f_name: str, old_val: Any, old_ov: bool, new_val: Any, new_ov: bool):
		self.table = table
		self.row_id = row_id
		self.f_name = f_name
		self.old_val = copy.deepcopy(old_val)
		self.old_ov = old_ov
		self.new_val = copy.deepcopy(new_val)
		self.new_ov = new_ov

	def execute(self):
		self.table._set_internal(self.row_id, self.f_name, self.new_val, self.new_ov)

	def undo(self):
		self.table._set_internal(self.row_id, self.f_name, self.old_val, self.old_ov)


class AddRowCommand(Command):
	def __init__(self, table: DataTable, row_id: str):
		self.table = table
		self.row_id = row_id

	def execute(self):
		self.table._add_row_internal(self.row_id)

	def undo(self):
		self.table._remove_row_internal(self.row_id)


class HistoryManager(metaclass=Singleton):
	def __init__(self, max_depth=100):
		self.undo_stack: List[Command] = []
		self.redo_stack: List[Command] = []
		self.max_depth = max_depth

	def push_and_execute(self, cmd: Command):
		cmd.execute()
		self.undo_stack.append(cmd)
		self.redo_stack.clear()
		if len(self.undo_stack) > self.max_depth:
			self.undo_stack.pop(0)

	def undo(self):
		if self.undo_stack:
			cmd = self.undo_stack.pop()
			cmd.undo()
			self.redo_stack.append(cmd)

	def redo(self):
		if self.redo_stack:
			cmd = self.redo_stack.pop()
			cmd.execute()
			self.undo_stack.append(cmd)

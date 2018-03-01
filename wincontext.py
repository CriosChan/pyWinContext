#! /usr/bin/python3

import regutils as reg

import time
import re

import ctypes
myappid = 'VodBox.pyWinContext.1.0' # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

import os
import argparse

parser = argparse.ArgumentParser(description='Manager for Context Menu commands in Windows')
parser.add_argument('-c', '--config', dest='config', default='%appdata%\\pyWinContext', help='Directory for Config and Local Storage')

configLoc = parser.parse_args().config
print(configLoc)

class ComModes:
    BAT, List = range(2)

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import app
import command

class WinContextApp(QMainWindow, app.Ui_MainWindow):
	def __init__(self, direct):
		super(self.__class__, self).__init__()
		self.direct = direct
		self.setupUi(self)
		self.initUI()

	def initUI(self):
		app_icon = QtGui.QIcon()
		app_icon.addFile('images/icon_16.png', QtCore.QSize(16,16))
		app_icon.addFile('images/icon_24.png', QtCore.QSize(24,24))
		app_icon.addFile('images/icon_32.png', QtCore.QSize(32,32))
		app_icon.addFile('images/icon_48.png', QtCore.QSize(48,48))
		app_icon.addFile('images/icon.png', QtCore.QSize(256,256))
		self.setWindowIcon(app_icon)
		self.statusBar().showMessage('Ready')
		self.setWindowTitle('pyWinContext')
		fts = reg.get_file_types()
		types = {}
		types["Other"] = []
		for type in fts:
			p = re.compile('(.+?)\/.+')
			if "perceived-type" in fts[type] and not fts[type]["perceived-type"].capitalize() in types:
				types[fts[type]["perceived-type"].capitalize()] = []
				types[fts[type]["perceived-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "perceived-type" in fts[type]:
				types[fts[type]["perceived-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and fts[type]["content-type"].capitalize() in types:
				types[fts[type]["content-type"].capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and p.match(fts[type]["content-type"]) and p.match(fts[type]["content-type"]).group(1).capitalize() in types:
				types[p.match(fts[type]["content-type"]).group(1).capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			elif "content-type" in fts[type] and p.match(fts[type]["content-type"]):
				types[p.match(fts[type]["content-type"]).group(1).capitalize()] = []
				types[p.match(fts[type]["content-type"]).group(1).capitalize()].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
			else:
				types["Other"].append({"filetype": type,
					"content-type": fts[type]["content-type"] if "content-type" in fts[type] else ""})
		increment = 0
		for type in types:
			item_0 = QTreeWidgetItem(self.treeWidget_2)
			item_0.setCheckState(0, QtCore.Qt.Unchecked)
			item_0.numEnabled = 0
			item_0.setText(0, type)
			item_0.setText(1, "")
			for file in types[type]:
				item_1 = QTreeWidgetItem(item_0)
				item_1.setCheckState(0, QtCore.Qt.Unchecked)
				item_1.setText(0, file["filetype"])
				item_1.setText(1, file["content-type"])
		self.treeWidget.setSortingEnabled(False)
		self.treeWidget_2.setSortingEnabled(True)
		self.treeWidget_2.sortItems(0, 0)
		self.treeWidget.sortItems(0, 0)
		self.treeWidget_2.itemChanged.connect(self.files_change)
		self.treeWidget.itemChanged.connect(self.left_bar_change)
		self.lineEdit.textChanged.connect(self.name_change)
		self.lineEdit_2.textChanged.connect(self.desc_change)
		self.treeWidget_2.resizeColumnToContents(0)
		self.treeWidget_2.setDisabled(True)
		self.treeWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
		self.lineEdit_4.textChanged.connect(self.search_change)
		self.pushButton_2.clicked.connect(self.group_button)
		self.pushButton_3.clicked.connect(self.action_button)
		self.pushButton_6.clicked.connect(self.open_command)
		self.pushButton_7.clicked.connect(self.remove_selection)
		self.treeWidget.itemSelectionChanged.connect(self.action_select)
		self.comboBox.currentIndexChanged.connect(self.after_change)
		self.pushButton.clicked.connect(self.add_custom_filetype)
		self.show()

	def search_change(self, text):
		for i in range(0, self.treeWidget_2.topLevelItemCount()):
			for x in range(0, self.treeWidget_2.topLevelItem(i).childCount()):
				if not (text in self.treeWidget_2.topLevelItem(i).child(x).text(0)
					or text in self.treeWidget_2.topLevelItem(i).child(x).text(1)):
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(True)
				else:
					self.treeWidget_2.topLevelItem(i).child(x).setHidden(False)

	def add_to_selected(self, filetype):
		for item in self.treeWidget.selectedItems():
			if item.isCommand and not filetype in item.filetypes:
				item.filetypes.append(filetype)
				
	def remove_from_selected(self, filetype):
		for item in self.treeWidget.selectedItems():
			if item.isCommand:
				try:
					item.filetypes.remove(filetype)
				except:
					pass
					
	def files_change(self, data):
		parent = data.parent()
		if data.childCount() > 0 and data.checkState(0) != QtCore.Qt.PartiallyChecked:
			checkState = data.checkState(0)
			for childIdx in range(0, data.childCount()):
				oldState = data.treeWidget().blockSignals(True)
				data.child(childIdx).setCheckState(0, checkState)
				for item in self.treeWidget.selectedItems():
					if checkState == QtCore.Qt.Checked:
						self.add_to_selected(data.child(childIdx).text(0))
					elif checkState == QtCore.Qt.Unchecked:
						self.remove_from_selected(data.child(childIdx).text(0))
				data.treeWidget().blockSignals(oldState)
		elif parent != None and type(parent) is QTreeWidgetItem:
			oldState = data.treeWidget().blockSignals(True)
			numEnabled = 0
			for childIdx in range(0, parent.childCount()):
				if data.isSelected() and parent.child(childIdx) != data and parent.child(childIdx).isSelected():
					parent.child(childIdx).setCheckState(0, data.checkState(0))
				if parent.child(childIdx).checkState(0) == QtCore.Qt.Checked:
					numEnabled += 1
					self.add_to_selected(parent.child(childIdx).text(0))
				elif parent.child(childIdx).checkState(0) == QtCore.Qt.PartiallyChecked:
					numEnabled += 0.1
				elif parent.child(childIdx).checkState(0) == QtCore.Qt.Unchecked:
					self.remove_from_selected(parent.child(childIdx).text(0))
			if numEnabled == parent.childCount():
				parent.setCheckState(0, QtCore.Qt.Checked)
			elif numEnabled > 0:
				parent.setCheckState(0, QtCore.Qt.PartiallyChecked)
			else:
				parent.setCheckState(0, QtCore.Qt.Unchecked)
			data.treeWidget().blockSignals(oldState)
			
	def left_bar_change(self, data):
		items = self.treeWidget.selectedItems()
		selected = len(items)
		if selected == 1:
			oldState = self.formLayout.blockSignals(True)
			self.lineEdit.setText(items[0].text(0))
			self.lineEdit_2.setText(items[0].text(1))
			self.formLayout.blockSignals(oldState)
			
	def name_change(self, text):
		items = self.treeWidget.selectedItems()
		oldState = self.treeWidget.blockSignals(True)
		items[0].setText(0, text)
		self.treeWidget.blockSignals(oldState)
		
	def desc_change(self, text):
		items = self.treeWidget.selectedItems()
		oldState = self.treeWidget.blockSignals(True)
		items[0].setText(1, text)
		self.treeWidget.blockSignals(oldState)
		
	def com_change(self, text):
		items = self.treeWidget.selectedItems()
		items[0].command = text
			
	def add_group(self, name, desc):
		itemGroup = QTreeWidgetItem(self.treeWidget)
		itemGroup.setBackground(0, QtGui.QColor(176, 234, 253))
		itemGroup.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled)
		itemGroup.isCommand = False
		itemGroup.setText(0, name)
		itemGroup.setText(1, desc)
		self.treeWidget.editItem(itemGroup, 0)
	
	def add_command(self, name, desc):
		itemCommand = QTreeWidgetItem(self.treeWidget)
		itemCommand.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled)
		itemCommand.isCommand = True
		itemCommand.filetypes = []
		itemCommand.command = ""
		itemCommand.commandMode = ComModes.BAT
		itemCommand.before = None
		itemCommand.after = None
		itemCommand.setText(0, name)
		itemCommand.setText(1, desc)
		self.treeWidget.setCurrentItem(itemCommand)
		self.treeWidget.editItem(itemCommand, 0)
	
	def group_button(self):
		self.add_group("Group", "Group Description")
		
	def action_button(self):
		self.add_command("Action", "Action Description")
		
	def remove_selection(self):
		items = self.treeWidget.selectedItems()
		for item in items:
			(item.parent() or self.treeWidget.invisibleRootItem()).removeChild(item)
		
	def action_select(self):
		items = self.treeWidget.selectedItems()
		selected = len(items)
		itemCount = 0
		results = {}
		containsCommand = False
		for x in range(0, len(items)):
			if items[x].isCommand:
				containsCommand = True
				itemCount += 1
				for topIdx in range(0, self.treeWidget_2.topLevelItemCount()):
					top = self.treeWidget_2.topLevelItem(topIdx)
					for childIdx in range(0, top.childCount()):
						if top.child(childIdx).text(0) in items[x].filetypes:
							results[top.child(childIdx).text(0)] = results[top.child(childIdx).text(0)] + 1 if top.child(childIdx).text(0) in results else 1
						if x + 1 == len(items):
							oldState = self.treeWidget_2.blockSignals(True)
							if top.child(childIdx).text(0) in results and results[top.child(childIdx).text(0)] == itemCount:
								top.child(childIdx).setCheckState(0, QtCore.Qt.Checked)
							elif top.child(childIdx).text(0) in results:
								top.child(childIdx).setCheckState(0, QtCore.Qt.PartiallyChecked)
							else:
								top.child(childIdx).setCheckState(0, QtCore.Qt.Unchecked)
							self.treeWidget_2.blockSignals(oldState)
		for topIdx in range(0, self.treeWidget_2.topLevelItemCount()):
			self.treeWidget_2.topLevelItem(topIdx).child(0).emitDataChanged()
		if selected == 1 and items[0].isCommand:
			self.treeWidget_2.setDisabled(False)
			oldState = self.formLayout.blockSignals(True)
			self.label.setEnabled(True)
			self.lineEdit.setEnabled(True)
			self.lineEdit.setText(items[0].text(0))
			self.label_2.setEnabled(True)
			self.lineEdit_2.setEnabled(True)
			self.lineEdit_2.setText(items[0].text(1))
			self.label_3.setEnabled(True)
			self.pushButton_6.setEnabled(True)
			oldComboState = self.comboBox.blockSignals(True)
			self.comboBox.clear()
			model = QtGui.QStandardItemModel(self.comboBox)
			self.comboBox.setEnabled(True)
			self.label_5.setEnabled(True)
			self.comboBox.setModel(model)
			model.appendRow(QtGui.QStandardItem("None"))
			tree = self.get_full_tree(self.treeWidget)
			for item in tree:
				if item is not items[0]:
					conflict = self.has_conflict(items[0], item)
					self.comboBox.addItem(self.item_to_string(item), userData= item if not conflict else None)
					model.item(self.comboBox.count()-1, 0).setEnabled(not conflict)
					if item is items[0].after:
						self.comboBox.setCurrentIndex(self.comboBox.count()-1)
			self.comboBox.blockSignals(oldComboState)
			self.formLayout.blockSignals(oldState)
		else:
			disable = True if selected == 0 or not containsCommand else False
			self.treeWidget_2.setDisabled(disable)
			self.label.setEnabled(False)
			self.lineEdit.setEnabled(False)
			self.label_2.setEnabled(False)
			self.lineEdit_2.setEnabled(False)
			self.label_3.setEnabled(False)
			self.pushButton_6.setEnabled(False)
			self.comboBox.setEnabled(False)
			self.label_5.setEnabled(False)
			
			
	def open_command(self):
		self.setEnabled(False)
		item = self.treeWidget.selectedItems()[0]
		dialog = CommandDialog(item)
		dialog.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		dialog.exec_()
		self.setEnabled(True)
		
	def after_change(self, index):
		self.treeWidget.selectedItems()[0].after = self.comboBox.currentData()
		
	def has_conflict(self, item, checkItem):
		afterItem = checkItem.after
		while afterItem != None and afterItem != item:
			afterItem = afterItem.after
		if afterItem != None:
			return True
			
		return False
		
	def get_full_tree(self, tree):
		result = []
		for topIdx in range(0, tree.topLevelItemCount()):
			top = tree.topLevelItem(topIdx)
			if top.isCommand:
				result.append(top)
			else:
				result += self.get_sub_tree(top)
		return result
				
	def get_sub_tree(self, item):
		result = []
		for childIdx in range(0, item.childCount()):
			sub = item.child(childIdx)
			if sub.isCommand:
				result.append(sub)
			else:
				result += self.get_sub_tree(sub)
		return result
		
	def item_to_string(self, item):
		text = item.text(0)
		parent = item.parent()
		while parent != None:
			text = parent.text(0) + "\\" + text
			parent = parent.parent()
		return text
		
	def add_custom_filetype(self):
		if not hasattr(self, "custom"):
			custom = QTreeWidgetItem(self.treeWidget_2)
			custom.setText(0, "Custom")
			custom.setCheckState(0, QtCore.Qt.Unchecked)
			self.treeWidget_2.addTopLevelItem(custom)
			self.custom = custom
		filetype = self.lineEdit_5.text()
		filetype = filetype if filetype.startswith(".") else "." + filetype
		newItem = QTreeWidgetItem(self.custom)
		newItem.setText(0, filetype)
		newItem.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
		newItem.setCheckState(0, QtCore.Qt.Unchecked)
		self.custom.addChild(newItem)
			
class CommandDialog(QDialog, command.Ui_Command):
	def __init__(self, widget):
		super(self.__class__, self).__init__()
		self.setupUi(self)
		self.action = widget
		self.initUI()
		
	def save(self):
		if self.action.commandMode == ComModes.BAT:
			self.action.path = self.path
		else:
			self.action.commands = []
			for x in range(self.listWidget.count()):
				self.action.commands.append(self.listWidget.item(x).text())
		
	def initUI(self):
		app_icon = QtGui.QIcon()
		app_icon.addFile('images/icon_16.png', QtCore.QSize(16,16))
		app_icon.addFile('images/icon_24.png', QtCore.QSize(24,24))
		app_icon.addFile('images/icon_32.png', QtCore.QSize(32,32))
		app_icon.addFile('images/icon_48.png', QtCore.QSize(48,48))
		app_icon.addFile('images/icon.png', QtCore.QSize(256,256))
		self.setWindowIcon(app_icon)
		#self.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint);
		self.radioButton.toggled.connect(self.radio_change)
		self.accepted.connect(self.save)
		self.radio_change(self.action.commandMode == ComModes.BAT)
		self.command_select()
		self.path = (self.action.path if hasattr(self.action, "path") else None)
		self.pushButton.clicked.connect(self.get_file)
		self.pushButton_2.clicked.connect(self.add_command)
		self.pushButton_3.clicked.connect(self.remove_command)
		self.pushButton_4.clicked.connect(self.move_up)
		self.pushButton_5.clicked.connect(self.move_down)
		self.listWidget.itemSelectionChanged.connect(self.command_select)
		
	def radio_change(self, state):
		oldState = self.blockSignals(True)
		self.listWidget.setEnabled(not state)
		self.pushButton_2.setEnabled(not state)
		self.pushButton_3.setEnabled(not state)
		self.pushButton_4.setEnabled(not state)
		self.pushButton_5.setEnabled(not state)
		self.pushButton.setEnabled(state)
		self.label.setEnabled(state)
		self.action.commandMode = (ComModes.BAT if state else ComModes.List)
		self.radioButton.setChecked(state)
		self.radioButton_2.setChecked(not state)
		self.blockSignals(oldState)
		
	def resizeEvent(self, event):
		if self.path != None:
			fMetrics = QtGui.QFontMetricsF(QtGui.QFont())
			self.label.setText(fMetrics.elidedText(self.path, QtCore.Qt.ElideRight, self.label.width() - 15))
		
	def get_file(self):
		file = QFileDialog()
		file.setAttribute(QtCore.Qt.WA_DeleteOnClose)
		file.setFileMode(QFileDialog.ExistingFile)
		self.path = file.getOpenFileUrl(filter="Windows Batch File (*.bat)")[0].toLocalFile()
		fMetrics = QtGui.QFontMetricsF(QtGui.QFont())
		self.label.setText(fMetrics.elidedText(self.path, QtCore.Qt.ElideRight, self.label.width() - 15))
		
	def add_command(self):
		itemCommand = QListWidgetItem(self.listWidget)
		itemCommand.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsDragEnabled)
		itemCommand.command = ""
		itemCommand.setText("<empty>")
		self.listWidget.setCurrentItem(itemCommand)
		self.listWidget.editItem(itemCommand)
		
	def remove_command(self):
		for item in self.listWidget.selectedItems():
			self.listWidget.takeItem(self.listWidget.row(item))
			
	def move_up(self):
		count = self.listWidget.count()
		items = [None] * count
		for item in self.listWidget.selectedItems():
			items[self.listWidget.row(item)] = item
		prev = None
		for x in range(0, len(items)):
			item = items[x]
			if item == None:
				if prev != None:
					self.listWidget.insertItem(x - 1, prev)
					prev = None
				prev = self.listWidget.takeItem(x)
		if prev != None:
			self.listWidget.insertItem(count - 1, prev)
		
	def move_down(self):
		count = self.listWidget.count()
		items = [None] * count
		for item in self.listWidget.selectedItems():
			items[self.listWidget.row(item)] = item
		prev = None
		for x in range(len(items) - 1, -1, -1):
			item = items[x]
			if item == None:
				if prev != None:
					self.listWidget.insertItem(x + 1, prev)
					prev = None
				prev = self.listWidget.takeItem(x)
		if prev != None:
			self.listWidget.insertItem(0, prev)
		
	def command_select(self):
		option = False
		if len(self.listWidget.selectedItems()) > 0:
			option = True
		self.pushButton_3.setEnabled(option)
		self.pushButton_4.setEnabled(option)
		self.pushButton_5.setEnabled(option)

def main(direct):
	app = QApplication(sys.argv)
	ui = WinContextApp(direct)
	ui.show()
	app.exec_()


if __name__ == '__main__':
	main(False)
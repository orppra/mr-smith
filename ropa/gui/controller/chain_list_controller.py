# ropa
# Copyright (C) 2017-2018 orppra

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import pyperclip

from PyQt4 import QtCore as qc

from list_widget_controller import ListWidgetController
from ropa.gadget import (
    GadgetBlock,
    ScriptBlock
)
from ropa.services import ExportService
from ropa.ui import HTMLDelegate


class ChainListController(ListWidgetController):
    def __init__(self, app, widget):
        super(ChainListController, self).__init__(app, widget)
        self.widget.setDragEnabled(True)
        self.widget.setAcceptDrops(True)
        self.widget.setDropIndicatorShown(True)
        self.widget.setItemDelegate(
            HTMLDelegate(self.widget))

        self.control = False
        self.shift = False
        self.widget.keyPressEvent = self.key_press_event
        self.widget.keyReleaseEvent = self.key_release_event

    def key_press_event(self, e):
        if e.key() == qc.Qt.Key_Control:
            self.control = True

        if e.key() == qc.Qt.Key_Shift:
            self.shift = True

        index = self.widget.selectedIndexes()[0].row()

        self.navigation_key_events(e)

        if e.key() == qc.Qt.Key_Delete or e.key() == qc.Qt.Key_Backspace:
            self.delete_item(index)

        if e.key() == qc.Qt.Key_C:
            if not self.control:
                self.toggle_comments(index)
            else:
                self.copy_item(index)

        if e.key() == qc.Qt.Key_O:
            self.insert_script_block(index)

        self.merge_key_events(e)

    def key_release_event(self, e):
        if e.key() == qc.Qt.Key_Control:
            self.control = False

        if e.key() == qc.Qt.Key_Shift:
            self.shift = False

    def copy_item(self, index):
        self.save_block(index)
        exporter = ExportService(self.app)
        item = self.get_item(index)
        block = self.retrieve_block(item)
        pyperclip.copy(exporter.export_block(block))

    def delete_item(self, index):
        self.widget.takeItem(index)

    def get_blocks(self):
        blocks = []
        for index in range(self.widget.count()):
            self.save_block(index)
            item = self.widget.item(index)
            block = self.retrieve_block(item)
            blocks.append(block)
        return blocks

    def insert_item(self, index, item):
        self.widget.insertItem(index, item)

    def insert_script_block(self, index):
        block = ScriptBlock('# TODO: INSERT CODE')
        item = self.create_script_item(block)
        if self.shift:
            self.insert_item(index, item)
        else:
            self.insert_item(index + 1, item)

    def merge(self, index, b1, b2):
        if b1.get_name() != 'GadgetBlock':
            return

        if b2.get_name() != 'GadgetBlock':
            return

        block = b1.merge(b2)
        item_merged = self.create_item(block)

        self.delete_item(index)
        self.delete_item(index)
        self.insert_item(index, item_merged)
        self.widget.setCurrentRow(index)

    def merge_down(self, index):
        if index == self.widget.count() - 1:
            return

        self.save_block(index)
        self.save_block(index + 1)

        item = self.get_item(index)
        item_below = self.get_item(index + 1)

        block = self.retrieve_block(item)
        block_below = self.retrieve_block(item_below)

        self.merge(index, block, block_below)

    def merge_key_events(self, e):
        if e.key() == qc.Qt.Key_N:
            self.merge_down(self.widget.selectedIndexes()[0].row())
        if e.key() == qc.Qt.Key_M:
            self.merge_up(self.widget.selectedIndexes()[0].row())
        if e.key() == qc.Qt.Key_L:
            self.split(self.widget.selectedIndexes()[0].row())

    def merge_up(self, index):
        if index == 0:
            return

        self.save_block(index)
        self.save_block(index - 1)

        item = self.get_item(index)
        item_above = self.get_item(index - 1)

        block = self.retrieve_block(item)
        block_above = self.retrieve_block(item_above)

        self.merge(index - 1, block_above, block)

    def navigation_key_events(self, e):
        if e.key() == qc.Qt.Key_Up or e.key() == qc.Qt.Key_K:
            index = self.widget.currentRow()
            if index == 0:
                return
            if self.control:
                item = self.widget.takeItem(index)
                self.widget.insertItem(index - 1, item)
            self.widget.setCurrentRow(index - 1)
        if e.key() == qc.Qt.Key_Down or e.key() == qc.Qt.Key_J:
            index = self.widget.currentRow()
            if index == self.widget.count() - 1:
                return
            if self.control:
                item = self.widget.takeItem(index)
                self.widget.insertItem(index + 1, item)
            self.widget.setCurrentRow(index + 1)

    def save_block(self, index):
        item = self.get_item(index)
        block = self.retrieve_block(item)

        # need to manually set because it only changes on
        # the surface
        text = str(item.data(qc.Qt.DisplayRole).toPyObject())
        if block.get_name() == 'GadgetBlock':
            if block.is_showing_comments():
                block.set_comments(text)
        else:
            block.set_text(text)

    def split(self, index):
        item = self.get_item(index)
        block = item.data(qc.Qt.UserRole).toPyObject()

        if block.get_name() != 'GadgetBlock':
            return

        gadgets = block.get_gadgets()

        self.delete_item(index)

        for i in range(len(gadgets) - 1, -1, -1):
            gadget = gadgets[i]
            item = self.create_item(GadgetBlock([gadget],
                                                block.get_comments()))
            self.insert_item(index, item)

        self.widget.setCurrentRow(index)

    def toggle_comments(self, index):
        item = self.get_item(index)
        block = self.retrieve_block(item)

        if block.get_name() != 'GadgetBlock':
            return

        if block.is_showing_comments():
            self.save_block(index)

        block.toggle_show_comments()

        self.delete_item(index)
        self.insert_item(index, self.create_item(block))
        self.widget.setCurrentRow(index)

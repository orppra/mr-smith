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

from PyQt4 import QtCore as qc

from list_widget_controller import ListWidgetController
from ropa.ui import HTMLDelegate


class ChainListController(ListWidgetController):
    def __init__(self, widget):
        super(ChainListController, self).__init__(widget)
        self.widget.setDragEnabled(True)
        self.widget.setAcceptDrops(True)
        self.widget.setDropIndicatorShown(True)
        self.widget.setItemDelegate(
            HTMLDelegate(self.widget))

        self.control = False
        self.widget.keyPressEvent = self.key_press_event
        self.widget.keyReleaseEvent = self.key_release_event

    def key_press_event(self, e):
        if e.key() == qc.Qt.Key_Control:
            self.control = True
        if e.key() == qc.Qt.Key_Up:
            index = self.widget.currentRow()
            if index == 0:
                return
            if self.control:
                item = self.widget.takeItem(index)
                self.widget.insertItem(index - 1, item)
            self.widget.setCurrentRow(index - 1)
        if e.key() == qc.Qt.Key_Down:
            index = self.widget.currentRow()
            if index == self.widget.count() - 1:
                return
            if self.control:
                item = self.widget.takeItem(index)
                self.widget.insertItem(index + 1, item)
            self.widget.setCurrentRow(index + 1)
        if e.key() == qc.Qt.Key_Delete or e.key() == qc.Qt.Key_Backspace:
            self.delete_item()
        if e.key() == qc.Qt.Key_C:
            self.toggle_comments()

    def key_release_event(self, e):
        if e.key() == qc.Qt.Key_Control:
            self.control = False

    def delete_item(self):
        self.widget.takeItem(self.widget.selectedIndexes()[0].row())

    def toggle_comments(self):
        for i in self.widget.selectedIndexes():
            item = self.get_item(i.row())
            gadget = item.data(qc.Qt.UserRole).toPyObject()

            # need to manually set the comments because it only changes on
            # the surface
            if gadget.is_showing_comments():
                comments = str(item.data(qc.Qt.DisplayRole).toPyObject())
                gadget.set_comments(comments)

            item.setData(qc.Qt.UserRole, gadget)
            item.setData(qc.Qt.DisplayRole, gadget.content())
            item.setFlags(item.flags() ^ qc.Qt.ItemIsEditable)

import os
import sys

from PySide2 import QtCore, QtWidgets

from .pak_reader import PakReader

FOLDER = QtWidgets.QFileIconProvider.Folder
FILE = QtWidgets.QFileIconProvider.File
ICON_PROVIDER = QtWidgets.QFileIconProvider()


class TreeView(QtWidgets.QTreeWidget):
    def __init__(self):
        super(TreeView, self).__init__()
        self.root_path = self.get_root_path()
        self.itemDoubleClicked.connect(self.add_pak_content_to_item)
        self.setHeaderHidden(True)

        # Creates tree view items
        items = []
        for fname in os.listdir(self.root_path):
            fpath = os.path.join(self.root_path, fname)
            fileinfo = QtCore.QFileInfo(fpath)

            item = QtWidgets.QTreeWidgetItem([fname])
            item.setIcon(0, ICON_PROVIDER.icon(fileinfo))

            if os.path.isdir(fpath):
                self.add_childs_to_item(item, fpath)

            items.append(item)

        self.addTopLevelItems(items)

    def get_root_path(self) -> str:
        dialog = QtWidgets.QFileDialog()
        root_path = dialog.getExistingDirectory(self,
                                                "Florensia Root Folder",
                                                QtCore.QDir.rootPath())
        if not root_path:
            sys.exit(0)

        return root_path

    def get_path_for_item(
        self,
        item: QtWidgets.QTreeWidgetItem
    ) -> str:
        """Returns the absolute os path for given item."""
        path = []
        path.append(item.text(0))

        parent = item.parent()

        while parent is not None:
            path.insert(0, parent.text(0))
            parent = parent.parent()

        return os.path.join(self.root_path, *path)

    def add_pak_content_to_item(
        self,
        item: QtWidgets.QTreeWidgetItem,
        column: int
    ) -> None:
        """Adds content of pak file to treeview."""
        fpath = self.get_path_for_item(item)

        # Add .pak file content as childs
        if fpath.endswith(".pak") and item.childCount() == 0:
            reader = PakReader(fpath)

            children = []
            for fname in reader.filenames:
                child_item = QtWidgets.QTreeWidgetItem([fname])
                fileinfo = QtCore.QFileInfo(os.path.join(fpath, fname))
                child_item.setIcon(0, ICON_PROVIDER.icon(fileinfo))

                children.append(child_item)

            item.addChildren(children)

    def add_childs_to_item(
        self,
        toplevel_item: QtWidgets.QTreeWidgetItem,
        path: str
    ) -> None:
        """Adds directory children to toplevel item."""
        children = []
        for fname in os.listdir(path):
            fpath = os.path.join(path, fname)
            item = QtWidgets.QTreeWidgetItem([fname])

            # Icon
            fileinfo = QtCore.QFileInfo(fpath)
            item.setIcon(0, ICON_PROVIDER.icon(fileinfo))

            if os.path.isdir(fpath):
                self.add_childs_to_item(item, fpath)

            children.append(item)

        toplevel_item.addChildren(children)

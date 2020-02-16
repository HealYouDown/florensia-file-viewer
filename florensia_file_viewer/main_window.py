from PySide2 import QtWidgets
import os
from .preview_widget import PreviewWidget
from .treeview import TreeView


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setMinimumSize(800, 600)
        self.setWindowTitle("Florensia File Viewer")

        splitter = QtWidgets.QSplitter()
        self.setCentralWidget(splitter)

        # Treeview widget
        self.treeview = TreeView()
        splitter.addWidget(self.treeview)

        # Preview widget
        self.preview_widget = PreviewWidget()
        splitter.addWidget(self.preview_widget)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.treeview.itemClicked.connect(self.on_treeview_item_click)

    def on_treeview_item_click(
        self,
        item: QtWidgets.QTreeWidgetItem
    ) -> None:
        path = self.treeview.get_path_for_item(item)

        if os.path.isdir(path) or path.endswith(".pak"):
            return

        self.preview_widget.open_file_preview(path)

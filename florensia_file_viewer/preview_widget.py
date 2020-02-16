import codecs
import io
import json
import os
from typing import List

import xlsxwriter
from PIL import Image, ImageQt, UnidentifiedImageError
from PySide2 import QtCore, QtGui, QtWidgets

from .converter import bin2list, dat2list
from .pak_reader import PakReader

ICON_PROVIDER = QtWidgets.QFileIconProvider()


def get_text_from_bytes(byte_data: bytes) -> str:
    try:
        text_content = byte_data.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text_content = byte_data.decode("utf-16")
        except UnicodeDecodeError:
            text_content = byte_data.decode("utf-8",
                                            errors="ignore")

    return text_content


class TablePreview(QtWidgets.QTableWidget):
    def __init__(self, headers: List[str], body: List[dict]):
        super(TablePreview, self).__init__()
        self.headers = headers
        self.body = body

        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setColumnCount(len(headers))
        self.setRowCount(len(body))

        self.setHorizontalHeaderLabels(headers)

        for row, item_data in enumerate(body):
            for column, value in enumerate(item_data.values()):
                widget = QtWidgets.QTableWidgetItem()
                widget.setText(str(value))
                self.setItem(row, column, widget)


class TextPreview(QtWidgets.QPlainTextEdit):
    def __init__(self, text: str):
        super(TextPreview, self).__init__()
        self.setReadOnly(True)
        self.setPlainText(text)


class PreviewWidget(QtWidgets.QTabWidget):
    def __init__(self):
        super(PreviewWidget, self).__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(lambda index: self.removeTab(index))
        self.setUsesScrollButtons(True)
        self.setMovable(True)

        # Bind event
        shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        shortcut.activated.connect(self.on_save_request)

    def on_save_request(self) -> None:
        widget = self.currentWidget()
        fpath = widget.fpath
        filename = os.path.basename(fpath)

        dialog = QtWidgets.QFileDialog()
        if isinstance(widget, TablePreview):
            filters = "All Files (*.*);;JSON (*.json);;Excel (*.xlsx)"
        else:
            filters = "All Files (*.*)"

        save_fpath_tuple = dialog.getSaveFileName(None,
                                                  "Save File",
                                                  filename,
                                                  filters)

        save_fpath, namefilter = save_fpath_tuple
        requested_extension = save_fpath.split(".")[-1].lower()

        if save_fpath == "":  # save was cancled
            return

        if requested_extension == "json" and namefilter == "JSON (*.json)":
            with open(save_fpath, "w", encoding="utf-16") as sf:
                json.dump(widget.body, sf, indent=4, ensure_ascii=False)

        elif requested_extension == "xlsx" and namefilter == "Excel (*.xlsx)":
            wb = xlsxwriter.Workbook(save_fpath)
            sheet = wb.add_worksheet()

            # headers
            bold = wb.add_format({"bold": True})
            sheet.write_row(0, 0, widget.headers, bold)

            # content
            for index, row in enumerate(widget.body):
                sheet.write_row(index+1, 0, row.values())

            wb.close()

        else:  # save file "normally" - just copy content to other location
            try:
                with open(fpath, "rb") as fp:
                    with open(save_fpath, "wb") as sp:
                        sp.write(fp.read())
            except FileNotFoundError:  # pak file content was tried to save
                reader = PakReader(os.path.dirname(fpath))
                file_content = reader.read_content(filename)
                with open(save_fpath, "wb") as sp:
                    sp.write(file_content)

    def open_file_preview(
        self,
        fpath: str,
    ) -> None:
        fileinfo = QtCore.QFileInfo(fpath)
        extension = fileinfo.suffix()

        if os.path.dirname(fpath).endswith(".pak"):
            reader = PakReader(os.path.dirname(fpath))
            file_content = reader.read_content(fileinfo.fileName())
        else:
            with codecs.open(fpath, "rb") as fp:
                file_content = fp.read()

        if extension in ["xml", "ini", "txt"]:
            widget = TextPreview(get_text_from_bytes(file_content))

        elif extension in ["bin", "dat"]:
            if extension == "bin":
                with io.BytesIO(file_content) as fp:
                    data = bin2list(fp)
                widget = TablePreview(headers=data[0].keys(), body=data)
            elif extension == "dat":
                with io.StringIO(get_text_from_bytes(file_content)) as fp:
                    data = dat2list(fp)
                widget = TablePreview(headers=data[0].keys(), body=data)

        else:
            # try to convert data to image
            try:
                image = Image.open(io.BytesIO(file_content))
                self.qimage = ImageQt.ImageQt(image)
                self.pixmap = QtGui.QPixmap.fromImage(self.qimage)

                label = QtWidgets.QLabel()
                label.setPixmap(self.pixmap)

                widget = QtWidgets.QScrollArea()
                widget.setWidget(label)

            except UnidentifiedImageError:
                # Not supported for any preview
                widget_layout = QtWidgets.QHBoxLayout()
                widget_layout.setAlignment(QtCore.Qt.AlignCenter)
                widget = QtWidgets.QWidget()
                widget.setLayout(widget_layout)

                widget_layout.addWidget(QtWidgets.QLabel(
                    "No preview available."))

        widget.fpath = fpath
        self.insertTab(0,
                       widget,
                       ICON_PROVIDER.icon(fpath),
                       fileinfo.fileName())

        self.setCurrentIndex(0)

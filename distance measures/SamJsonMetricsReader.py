#!/usr/bin/env python3
"""DOESNT WORK"""

import sys
from PyQt5.QtCore import QCoreApplication, QFile, QIODevice, QTextStream
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QApplication

def read_json_files(folder_path):
    app = QApplication(sys.argv)

    # Create a QTextStream to capture console output
    stream = QTextStream(sys.stdout)
    stream.setAutoDetectUnicode(True)

    # Iterate through JSON files in the folder
    for filename in folder_path:
        json_file = QFile(filename)
        if json_file.open(QIODevice.ReadOnly | QIODevice.Text):
            json_data = json_file.readAll()
            json_doc = QJsonDocument.fromJson(json_data)
            json_object = json_doc.object()

            # Extract values (modify this part according to your JSON structure)
            property_names = []
            property_keys = []
            properties_array = json_object["properties"].toArray()
            for value in properties_array:
                obj = value.toObject()
                property_names.append(obj["PropertyName"].toString())
                property_keys.append(obj["key"].toString())

            # Print extracted values
            stream << f"File: {filename}\n"
            stream << f"Property Names: {property_names}\n"
            stream << f"Property Keys: {property_keys}\n\n"

            json_file.close()

    # Print to console
    sys.stdout.flush()

    
import os
from PyQt5 import QtWidgets

class CustomFileDialog(QtWidgets.QFileDialog):
    def __init__(self, *args):
        super().__init__(*args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtWidgets.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtWidgets.QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                files.append(os.path.join(str(self.directory().absolutePath()), str(i.data().toString())))
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles

# Example usage:
app = QtWidgets.QApplication([])
dialog = CustomFileDialog()
dialog.setWindowTitle("Select Files")
dialog.setNameFilter("*.json")
if dialog.exec_():
    selected_files = dialog.filesSelected()
    read_json_files(selected_files)
    for file_path in selected_files:
        print(file_path)

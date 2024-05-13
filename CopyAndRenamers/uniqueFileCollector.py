# -*- coding: utf-8 -*-
"""
Created on Mon May  6 13:43:53 2024

@author: rbj
"""
import os
import sys
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QPushButton

class FileCopyApp(QWidget):
    def __init__(self):
        super().__init__()

        # Initialize UI components
        self.init_ui()

    def init_ui(self):
        # Create buttons for folder selection
        self.source_button = QPushButton("Select Source Folder", self)
        self.source_button.clicked.connect(self.select_source_folder)

        self.target_button = QPushButton("Select Target Folder", self)
        self.target_button.clicked.connect(self.select_target_folder)

        # Initialize folder paths
        self.source_folder = None
        self.target_folder = None

        # Show the buttons
        self.source_button.move(20, 20)
        self.target_button.move(20, 60)

    def select_source_folder(self):
        self.source_folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        print(f"Source folder selected: {self.source_folder}")

    def select_target_folder(self):
        self.target_folder = QFileDialog.getExistingDirectory(self, "Select Target Folder")
        print(f"Target folder selected: {self.target_folder}")

        # Copy unique files from source to target folder
        if self.source_folder and self.target_folder:
            self.copy_unique_files()

    def copy_unique_files(self):
        unique_files = set()
        for root, _, files in os.walk(self.source_folder):
            for filename in files:
                source_path = os.path.join(root, filename)
                if os.path.isfile(source_path):
                    unique_files.add(filename)

        for filename in unique_files:
            source_file = os.path.join(self.source_folder, filename)
            target_file = os.path.join(self.target_folder, filename)
            shutil.copy2(source_file, target_file)
            print(f"File '{filename}' copied to target folder.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCopyApp()
    window.setGeometry(100, 100, 300, 120)
    window.setWindowTitle("File Copy Tool")
    window.show()
    sys.exit(app.exec_())


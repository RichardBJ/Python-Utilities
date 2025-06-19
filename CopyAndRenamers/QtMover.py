#!/usr/bin/env python3
#!/usr/bin/env python3
import sys
import os
import random
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QFileDialog, QLabel, 
                            QSpinBox, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt

class RandomFileCopier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        # Initialize variables
        self.source_dir = ""
        self.dest_dir = ""
        
    def initUI(self):
        self.setWindowTitle('Random File Copier')
        self.setGeometry(100, 100, 600, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Source directory selection
        source_layout = QHBoxLayout()
        self.source_label = QLabel('Source Directory: Not Selected')
        source_btn = QPushButton('Select Source')
        source_btn.clicked.connect(self.select_source)
        source_layout.addWidget(self.source_label)
        source_layout.addWidget(source_btn)
        layout.addLayout(source_layout)
        
        # Destination directory selection
        dest_layout = QHBoxLayout()
        self.dest_label = QLabel('Destination Directory: Not Selected')
        dest_btn = QPushButton('Select Destination')
        dest_btn.clicked.connect(self.select_destination)
        dest_layout.addWidget(self.dest_label)
        dest_layout.addWidget(dest_btn)
        layout.addLayout(dest_layout)
        
        # Number of files selection
        files_layout = QHBoxLayout()
        files_layout.addWidget(QLabel('Number of files to copy:'))
        self.num_files_spin = QSpinBox()
        self.num_files_spin.setRange(1, 999999)
        self.num_files_spin.setValue(1)
        files_layout.addWidget(self.num_files_spin)
        layout.addLayout(files_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Copy button
        copy_btn = QPushButton('Copy Files')
        copy_btn.clicked.connect(self.copy_files)
        layout.addWidget(copy_btn)
        
    def select_source(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if dir_path:
            self.source_dir = dir_path
            self.source_label.setText(f'Source Directory: {dir_path}')
            
    def select_destination(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if dir_path:
            self.dest_dir = dir_path
            self.dest_label.setText(f'Destination Directory: {dir_path}')
            
    def copy_files(self):
        if not self.source_dir or not self.dest_dir:
            QMessageBox.warning(self, 'Error', 'Please select both source and destination directories')
            return
            
        # Get list of files in source directory
        files = [f for f in os.listdir(self.source_dir) 
                if os.path.isfile(os.path.join(self.source_dir, f))]
        
        # Check if we have enough files
        num_files = min(self.num_files_spin.value(), len(files))
        if num_files == 0:
            QMessageBox.warning(self, 'Error', 'No files found in source directory')
            return
            
        # Randomly select files
        selected_files = random.sample(files, num_files)
        
        # Copy files with progress bar
        self.progress_bar.setMaximum(num_files)
        for i, file in enumerate(selected_files, 1):
            src_path = os.path.join(self.source_dir, file)
            dst_path = os.path.join(self.dest_dir, file)
            
            try:
                shutil.copy2(src_path, dst_path)
                self.progress_bar.setValue(i)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Error copying {file}: {str(e)}')
                return
                
        QMessageBox.information(self, 'Success', 
                              f'Successfully copied {num_files} files')
        self.progress_bar.setValue(0)

def main():
    app = QApplication(sys.argv)
    window = RandomFileCopier()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
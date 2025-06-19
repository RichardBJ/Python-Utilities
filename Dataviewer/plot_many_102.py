#!/usr/bin/env python3
#!/usr/bin/env python3
import sys
import os
import warnings
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, 
    QVBoxLayout, QWidget, QLabel
)
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Suppress Qt and Mesa warnings
os.environ["QT_LOGGING_RULES"] = "qt.qpa.xcb=false"
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"
os.environ["QT_QPA_PLATFORM"] = "xcb"
warnings.filterwarnings("ignore")

# Use Agg backend for matplotlib if no display is available
plt.switch_backend('Agg')

class ParquetPlotter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parquet File Plotter")
        self.setGeometry(100, 100, 400, 200)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create button
        self.button = QPushButton("Select Parquet Files")
        self.button.clicked.connect(self.select_files)
        layout.addWidget(self.button)

        # Add status label
        self.status_label = QLabel("Ready to process files...")
        layout.addWidget(self.status_label)

    def select_files(self):
        try:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Parquet Files",
                "",
                "Parquet Files (*.parquet)"
            )
            
            if files:
                self.process_files(files)
        except Exception as e:
            print(f"Error in file selection: {str(e)}")
            self.status_label.setText(f"Error in file selection: {str(e)}")

    def process_files(self, files):
        total_files = len(files)
        for index, file_path in enumerate(files, 1):
            try:
                # Update status
                self.status_label.setText(f"Processing file {index}/{total_files}: {Path(file_path).name}")
                QApplication.processEvents()  # Update GUI

                # Read parquet file
                df = pd.read_parquet(file_path)
                
                # Take first 1000 rows
                df = df.head(1000)

                # Create figure with two subplots
                fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                fig.suptitle(f'Plots for {Path(file_path).stem}')

                # Plot Channels
                ax1.plot(df['Time'], df['Channels'])
                ax1.set_title('Time vs Channels')
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Channels')
                ax1.grid(True)

                # Plot Noisy Current
                ax2.plot(df['Time'], df['Noisy Current'])
                ax2.set_title('Time vs Noisy Current')
                ax2.set_xlabel('Time')
                ax2.set_ylabel('Noisy Current')
                ax2.grid(True)

                # Adjust layout
                plt.tight_layout()

                # Save plot
                output_path = str(Path(file_path).with_suffix('.png'))
                plt.savefig(output_path, dpi=300, bbox_inches='tight')
                plt.close()

                self.status_label.setText(f"Saved {index}/{total_files}: {output_path}")
                QApplication.processEvents()

            except Exception as e:
                error_msg = f"Error processing file {index}/{total_files} - {Path(file_path).name}: {str(e)}"
                print(error_msg)
                self.status_label.setText(error_msg)
                QApplication.processEvents()

        self.status_label.setText(f"Completed processing {total_files} files")

def main():
    # Set the XDG_RUNTIME_DIR if not set
    if "XDG_RUNTIME_DIR" not in os.environ:
        runtime_dir = f"/tmp/runtime-{os.environ.get('USER', 'user')}"
        os.environ["XDG_RUNTIME_DIR"] = runtime_dir
        os.makedirs(runtime_dir, exist_ok=True)
        os.chmod(runtime_dir, 0o700)  # Set correct permissions

    app = QApplication(sys.argv)
    window = ParquetPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
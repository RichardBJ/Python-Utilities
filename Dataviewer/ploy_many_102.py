import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QVBoxLayout, QWidget
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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
        layout.addButton(self.button)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Parquet Files",
            "",
            "Parquet Files (*.parquet)"
        )
        
        if files:
            self.process_files(files)

    def process_files(self, files):
        for file_path in files:
            try:
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

            except Exception as e:
                print(f"Error processing {file_path}: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = ParquetPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
import sys
import json
import numpy as np
from scipy import stats
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFileDialog, QTextEdit
import os

def load_tfjs_model(model_path):
    with open(model_path, 'r') as f:
        model_json = json.load(f)
    return model_json

def extract_weights(model_json, model_dir):
    weights = []
    for group in model_json['weightsManifest']:
        for path in group['paths']:
            weight_path = os.path.join(model_dir, path)
            with open(weight_path, 'rb') as f:
                weights.append(np.frombuffer(f.read(), dtype=np.float32))
    return weights

def compare_models(model1_path, model2_path, significance_level=0.05):
    model1 = load_tfjs_model(model1_path)
    model2 = load_tfjs_model(model2_path)

    model1_dir = os.path.dirname(model1_path)
    model2_dir = os.path.dirname(model2_path)

    weights1 = extract_weights(model1, model1_dir)
    weights2 = extract_weights(model2, model2_dir)

    if len(weights1) != len(weights2):
        return False, f"Models have different number of weight arrays: {len(weights1)} vs {len(weights2)}"

    different_layers = []
    for i, (w1, w2) in enumerate(zip(weights1, weights2)):
        if w1.shape != w2.shape:
            different_layers.append(f"Layer {i}: Shape mismatch - {w1.shape} vs {w2.shape}")
            continue

        t_statistic, p_value = stats.ttest_ind(w1, w2)
        if p_value < significance_level:
            different_layers.append(f"Layer {i}: Significant difference (p-value: {p_value:.4f})")

    if different_layers:
        return False, "Models are significantly different:\n" + "\n".join(different_layers)
    else:
        return True, "Models are not significantly different"

class ModelComparisonApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('TensorFlow.js CNN Model Comparison')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # File selection
        file1_layout = QHBoxLayout()
        self.file1_label = QLabel('Model 1:')
        self.file1_button = QPushButton('Select File')
        self.file1_button.clicked.connect(lambda: self.select_file(1))
        file1_layout.addWidget(self.file1_label)
        file1_layout.addWidget(self.file1_button)

        file2_layout = QHBoxLayout()
        self.file2_label = QLabel('Model 2:')
        self.file2_button = QPushButton('Select File')
        self.file2_button.clicked.connect(lambda: self.select_file(2))
        file2_layout.addWidget(self.file2_label)
        file2_layout.addWidget(self.file2_button)

        # Compare button
        self.compare_button = QPushButton('Compare Models')
        self.compare_button.clicked.connect(self.compare_models)

        # Results display
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)

        layout.addLayout(file1_layout)
        layout.addLayout(file2_layout)
        layout.addWidget(self.compare_button)
        layout.addWidget(self.results_text)

        self.setLayout(layout)

        self.model1_path = ''
        self.model2_path = ''

    def select_file(self, file_num):
        file_path, _ = QFileDialog.getOpenFileName(self, f"Select Model {file_num}", "", "JSON Files (*.json)")
        if file_path:
            if file_num == 1:
                self.model1_path = file_path
                self.file1_label.setText(f'Model 1: {file_path}')
            else:
                self.model2_path = file_path
                self.file2_label.setText(f'Model 2: {file_path}')

    def compare_models(self):
        if not self.model1_path or not self.model2_path:
            self.results_text.setText("Please select both model files.")
            return

        try:
            are_similar, message = compare_models(self.model1_path, self.model2_path)
            self.results_text.setText(message)
        except Exception as e:
            self.results_text.setText(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ModelComparisonApp()
    ex.show()
    sys.exit(app.exec_())
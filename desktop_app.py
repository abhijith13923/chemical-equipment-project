import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QFileDialog, QTextEdit, QHBoxLayout
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

API_UPLOAD = "http://127.0.0.1:8000/api/equipment/upload/"
API_PDF = "http://127.0.0.1:8000/api/equipment/report/pdf/"

USERNAME = "admin"
PASSWORD = "chemicaladmin123"

class ChartCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def plot_metrics(self, metrics):
        self.ax.clear()
        labels = list(metrics.keys())
        values = list(metrics.values())
        self.ax.bar(labels, values)
        self.ax.set_title("Equipment Metrics")
        self.draw()


class EquipmentApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Equipment Analytics Desktop App")
        self.setFixedSize(800, 600)

        self.file_path = None
        self.upload_success = False        

        self.layout = QVBoxLayout()

        self.title = QLabel("Equipment Analytics System")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size:18px;font-weight:bold;")

        self.select_btn = QPushButton("Select CSV File")
        self.upload_btn = QPushButton("Upload & Analyze")
        self.pdf_btn = QPushButton("Download PDF Report")
        self.pdf_btn.setEnabled(False)        

        self.select_btn.clicked.connect(self.select_file)
        self.upload_btn.clicked.connect(self.upload_file)
        self.pdf_btn.clicked.connect(self.download_pdf)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.pdf_btn)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        self.chart = ChartCanvas()

        self.layout.addWidget(self.title)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.chart)
        self.layout.addWidget(self.output)

        self.setLayout(self.layout)

    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select CSV", "", "CSV Files (*.csv)")
        if file:
            self.file_path = file
            self.output.append(f"Selected file:\n{file}\n")

    def upload_file(self):
        if not self.file_path:
            self.output.append("Select a CSV file first.\n")
            return

        files = {'file': open(self.file_path, 'rb')}
        response = requests.post(
            API_UPLOAD,
            files=files,
            auth=(USERNAME, PASSWORD)
        )

        if response.status_code in (200, 201):
            data = response.json()

            self.upload_success = True         
            self.pdf_btn.setEnabled(True)      

            metrics = {
                "Flowrate": data["avg_flowrate"],
                "Pressure": data["avg_pressure"],
                "Temperature": data["avg_temperature"]
            }

            self.chart.plot_metrics(metrics)

            self.output.append("Upload Successful\n")
            self.output.append(f"Total Equipment: {data['total_equipment']}")
            self.output.append(f"Avg Flowrate: {data['avg_flowrate']}")
            self.output.append(f"Avg Pressure: {data['avg_pressure']}")
            self.output.append(f"Avg Temperature: {data['avg_temperature']}\n")
        else:
            self.output.append("Upload failed, due to invalid csv file.\n")

    def download_pdf(self):
        if not self.upload_success:            
            self.output.append("Please upload a CSV file before downloading the PDF.\n")
            return

        response = requests.get(
            API_PDF,
            auth=(USERNAME, PASSWORD)
        )

        if response.status_code in (200, 201):
            with open("Equipment_Report.pdf", "wb") as f:
                f.write(response.content)
            self.output.append("PDF report downloaded successfully.\n")
        else:
            self.output.append("PDF download failed.\n")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EquipmentApp()
    window.show()
    sys.exit(app.exec_())

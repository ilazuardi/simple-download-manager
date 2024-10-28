# gui/main_window.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QMessageBox, QDateTimeEdit, QCheckBox, QTextEdit
)
from PyQt5.QtCore import QDateTime, QTimer
from core.download_manager import DownloadManager
from core.video_detector import VideoDetector
from storage.sqlite_handler import SQLiteHandler

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = DownloadManager()
        self.video_detector = VideoDetector()
        self.db = SQLiteHandler()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # URL and filename inputs
        self.url_input = QLineEdit(self)
        self.url_input.setPlaceholderText("Enter URL")

        self.filename_input = QLineEdit(self)
        self.filename_input.setPlaceholderText("Enter filename (for files only)")

        # Video checkbox
        self.video_checkbox = QCheckBox("Is this a video?", self)

        # DateTime input for scheduling
        self.datetime_input = QDateTimeEdit(self)
        self.datetime_input.setDateTime(QDateTime.currentDateTime())
        self.datetime_input.setDisplayFormat("yyyy-MM-dd HH:mm:ss")

        # Download buttons
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.start_download)

        self.pause_button = QPushButton("Pause Download", self)
        self.pause_button.clicked.connect(self.pause_download)

        self.resume_button = QPushButton("Resume Download", self)
        self.resume_button.clicked.connect(self.resume_download)

        self.schedule_button = QPushButton("Schedule Download", self)
        self.schedule_button.clicked.connect(self.schedule_download)

        # Download history display
        self.history_view = QTextEdit(self)
        self.history_view.setReadOnly(True)

        # Add widgets to the layout
        layout.addWidget(QLabel("Open Download Manager"))
        layout.addWidget(self.url_input)
        layout.addWidget(self.filename_input)
        layout.addWidget(self.video_checkbox)
        layout.addWidget(QLabel("Schedule Download:"))
        layout.addWidget(self.datetime_input)
        layout.addWidget(self.download_button)
        layout.addWidget(self.pause_button)
        layout.addWidget(self.resume_button)
        layout.addWidget(self.schedule_button)
        layout.addWidget(QLabel("Download History:"))
        layout.addWidget(self.history_view)

        self.setLayout(layout)
        self.setWindowTitle("Open Download Manager")
        self.setGeometry(300, 300, 400, 400)
        self.show()

        # Load download history on startup
        self.refresh_history()

    def start_download(self):
        url = self.url_input.text()
        filename = self.filename_input.text()
        is_video = self.video_checkbox.isChecked()

        if is_video:
            try:
                self.video_detector.download_video(url)
                self.db.save_download(url, "Video", "Completed")
                self.refresh_history()
                QMessageBox.information(self, "Success", f"Downloaded video from: {url}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to download video: {e}")
        elif url and filename:
            try:
                self.manager.start_download(url, filename)
                self.db.save_download(url, filename, "In Progress")
                self.refresh_history()
                QMessageBox.information(self, "Success", f"Started downloading: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to start download: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please enter a valid URL and filename.")

    def pause_download(self):
        filename = self.filename_input.text()
        if filename:
            self.manager.pause_download(filename)
            self.db.update_status(filename, "Paused")
            self.refresh_history()
            QMessageBox.information(self, "Paused", f"Paused: {filename}")

    def resume_download(self):
        url = self.url_input.text()
        filename = self.filename_input.text()
        if filename:
            self.manager.resume_download(url, filename)
            self.db.update_status(filename, "In Progress")
            self.refresh_history()
            QMessageBox.information(self, "Resumed", f"Resumed: {filename}")

    def schedule_download(self):
        url = self.url_input.text()
        filename = self.filename_input.text()
        scheduled_time = self.datetime_input.dateTime().toPyDateTime()

        if url and filename:
            delay = (scheduled_time - QDateTime.currentDateTime().toPyDateTime()).total_seconds()
            if delay > 0:
                QTimer.singleShot(int(delay * 1000), lambda: self.start_download())
                QMessageBox.information(self, "Scheduled", f"Download scheduled for {scheduled_time}")
            else:
                QMessageBox.warning(self, "Warning", "Scheduled time must be in the future.")
        else:
            QMessageBox.warning(self, "Warning", "Please enter both URL and filename.")

    def refresh_history(self):
        """Refresh the download history view."""
        downloads = self.db.fetch_all_downloads()
        history = "\n".join([f"{d[1]} - {d[2]} - {d[3]}" for d in downloads])
        self.history_view.setText(history)

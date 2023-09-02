import os
import time
from calendar import isleap
from datetime import datetime
from pathlib import Path

from PIL import ExifTags, Image
from PyQt6 import uic
from PyQt6.QtCore import QStringListModel
from PyQt6.QtWidgets import QFileDialog, QMainWindow

from fotogenea.utils import ImageLoaderThread, update_exif_creation_date


class FotoGenea(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(Path(__file__).absolute().parent.resolve() / "ui/interface.ui", self)
        self.init_ui()

    def on_year_changed(self, year):
        if isleap(int(year)) and self.month.currentIndex() == 1:
            self.day.setMaximum(29)
        elif not isleap(int(year)) and self.month.currentIndex() == 1:
            self.day.setMaximum(28)

    def on_month_changed(self, month_index):
        if month_index == 1 and isleap(int(self.year.value())):
            self.day.setMaximum(self.month_days[self.month_names[month_index]] + 1)
        else:
            self.day.setMaximum(self.month_days[self.month_names[month_index]])

    def init_ui(self):
        self.setWindowTitle("Fotogenea")
        self.show()

        self.month_days = {
            "January": 31,
            "February": 28,
            "March": 31,
            "April": 30,
            "May": 31,
            "June": 30,
            "July": 31,
            "August": 31,
            "September": 30,
            "October": 31,
            "November": 30,
            "December": 31,
        }

        self.month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        self.month.setModel(QStringListModel(self.month_names))
        self.month.setCurrentIndex(0)
        # connect the image_clicked signal of the image grid to the show_file_details slot
        self.image_grid.image_clicked.connect(self.show_file_details)

        self.browse_button.clicked.connect(self.browse_folder)
        self.save_button.clicked.connect(self.update_exif_info)
        self.save_button.setEnabled(False)

        self.year.valueChanged.connect(self.on_year_changed)
        self.month.currentIndexChanged.connect(self.on_month_changed)

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select folder")
        if folder_path:
            self.loader_thread = ImageLoaderThread(folder_path)
            self.loader_thread.images_loaded.connect(self.image_grid.set_images)
            self.loader_thread.start()
            self.current_folder_label.setText(folder_path)

    def show_file_details(self, path):
        self.save_button.setEnabled(True)
        # Display the full path and creation date of the file in the file_details QLabel

        file_info = os.stat(path)
        file_size = file_info.st_size
        file_created = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime(file_info.st_ctime)
        )
        self.file_details.setText(
            f"Path: {path}\nSize: {file_size} bytes\nCreated: {file_created}"
        )
        self.selected_image = path
        image = Image.open(path)
        exif_data = image.getexif()
        for tag_id, value in exif_data.items():
            if ExifTags.TAGS.get(tag_id) == "DateTimeOriginal":
                print(f"Original Date and Time: {value}")

                exif_datetime = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")

                self.day.setValue(exif_datetime.day)
                self.month.setCurrentIndex(exif_datetime.month - 1)
                self.year.setValue(exif_datetime.year)
                self.hour.setValue(exif_datetime.hour)
                self.minutes.setValue(exif_datetime.minute)

    def update_exif_info(self):
        new_date_time_original = datetime(
            self.year.value(),
            self.month.currentIndex() + 1,
            self.day.value(),
            self.hour.value(),
            self.minutes.value(),
        )
        print(new_date_time_original)
        update_exif_creation_date(self.selected_image, new_date_time_original)

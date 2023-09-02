import os
from datetime import datetime
from pathlib import Path
from typing import Union

from PIL import Image
from PIL.ExifTags import TAGS
from PyQt6.QtCore import QThread, pyqtSignal


class ImageLoaderThread(QThread):
    images_loaded = pyqtSignal(list)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        images = [
            os.path.join(self.folder_path, file)
            for file in os.listdir(self.folder_path)
            if file.endswith(".jpg")
        ]
        self.images_loaded.emit(images)


def update_exif_creation_date(
    image_path: Union[str, Path],
    new_datetime: datetime,
    format: str = "%Y:%m:%d %H:%M:%S",
):
    """
    Update the DateTimeOriginal EXIF Tag to `new_datetime` using `format` as the date
    string representation.

    Args:
        image_path (Union[str, Path]): Path to the image.
        new_datetime (datetime): New datetime for the EXIF Tag
        format (str, optional): Date string format. Defaults to "%Y:%m:%d %H:%M:%S".
    """
    try:
        # Open the image using Pillow
        image = Image.open(image_path)
        exif_data = image.getexif()

        date_time_original_tag = None
        for k, v in TAGS.items():
            if v == "DateTimeOriginal":
                date_time_original_tag = k

        for k, v in exif_data.items():
            if k == date_time_original_tag:
                print(f"Value of current DateTimeOriginal: '{exif_data[k]}'")

        exif_data[date_time_original_tag] = new_datetime.strftime(format)

        image.save(image_path, exif=exif_data, quality=100)
    except Exception as e:
        print(f"Error updating EXIF DateTimeOriginal tag: {e}")

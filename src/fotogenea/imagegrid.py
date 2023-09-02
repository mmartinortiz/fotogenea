import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget


class ImageThumbnailWidget(QWidget):
    clicked = pyqtSignal()

    def __init__(self, image_path):
        super().__init__()

        self.image_path = image_path

        # Create the thumbnail label
        self.thumbnail_label = QLabel()
        self.thumbnail_label.setFixedSize(200, 200)
        # self.thumbnail_label.setScaledContents(True)

        # Create the file name label
        self.file_name_label = QLabel()

        # Create a layout and add the labels
        layout = QVBoxLayout()
        layout.addWidget(self.thumbnail_label)
        layout.addWidget(self.file_name_label)
        self.setLayout(layout)

        # Set the background color to white
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: white;")

        # Load and display the thumbnail
        self.load_thumbnail()

    def load_thumbnail(self):
        # Load the image thumbnail using QPixmap
        pixmap = QPixmap(self.image_path)
        self.thumbnail_label.setPixmap(
            pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
        )

        # Get the file name from the image path
        file_name = os.path.basename(self.image_path)
        self.file_name_label.setText(file_name)

    def mousePressEvent(self, event):
        # Emit the clicked signal when the widget is clicked
        self.clicked.emit()
        # Change the background color to grey
        self.setStyleSheet("background-color: grey;")

        print("click")


class ImageGrid(QWidget):
    image_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Set up layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.selected_image = None

    def resizeEvent(self, event):
        # self.update_column_count()
        pass

    def on_image_clicked(self, event, path):
        self.selected_image.setStyleSheet("")

    def set_images(self, images):
        self.clear_images()

        row = 0
        col = 0

        for image in images:
            thumbnail = ImageThumbnailWidget(image)

            self.layout.addWidget(thumbnail, row, col)

            thumbnail.mousePressEvent = (
                lambda event, path=image: self.image_clicked.emit(path)
            )

            col += 1
            if col == 4:
                row += 1
                col = 0

        # row = 0
        # col = 0
        # for image in images:
        #     pixmap = QPixmap(image)
        #     thumbnail = QLabel()
        #     thumbnail.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
        #     thumbnail.mousePressEvent = (
        #         lambda event, path=image: self.image_clicked.emit(path)
        #     )
        #     self.layout.addWidget(thumbnail, row, col)
        #     col += 1
        #     if col == 4:
        #     # if col == self.layout.columnCount():
        #         row += 1
        #         col = 0

    def clear_images(self):
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)

    def update_column_count(self):
        available_width = self.width()
        thumbnail_width = 200
        min_column_count = 1
        max_column_count = max(1, available_width // thumbnail_width)
        current_column_count = self.layout.columnCount()
        new_column_count = max(max_column_count, current_column_count)
        if new_column_count != current_column_count:
            self.layout.setColumnCount(new_column_count)
            self.layout.update()

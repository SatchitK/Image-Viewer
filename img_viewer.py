from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QGridLayout, QLineEdit, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt5.QtCore import Qt
import sys
import os

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Viewer')
        self.move(300, 300)
        self.resize(400, 200)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.raw_dir_button = QPushButton('Select Raw Images Directory')
        self.raw_dir_button.clicked.connect(self.select_raw_dir)
        self.layout.addWidget(self.raw_dir_button)

        self.labels_dir_button = QPushButton('Select Labels Directory')
        self.labels_dir_button.clicked.connect(self.select_labels_dir)
        self.layout.addWidget(self.labels_dir_button)

        self.predictions_dir_button = QPushButton('Select Predictions Directory')
        self.predictions_dir_button.clicked.connect(self.select_predictions_dir)
        self.layout.addWidget(self.predictions_dir_button)

        self.image_name_input = QLineEdit()
        self.image_name_input.returnPressed.connect(self.display_images)
        self.layout.addWidget(self.image_name_input)

        self.viewer_raw = ZoomableGraphicsView(self)
        self.viewer_labels = ZoomableGraphicsView(self)
        self.viewer_predictions = ZoomableGraphicsView(self)

        self.layout.addWidget(self.viewer_raw)
        self.layout.addWidget(self.viewer_labels)
        self.layout.addWidget(self.viewer_predictions)

    def select_raw_dir(self):
        self.raw_dir = QFileDialog.getExistingDirectory(self, 'Select Raw Images Directory')
        print("Selected raw images directory:", self.raw_dir)

    def select_labels_dir(self):
        self.labels_dir = QFileDialog.getExistingDirectory(self, 'Select Labels Directory')
        print("Selected labels directory:", self.labels_dir)

    def select_predictions_dir(self):
        self.predictions_dir = QFileDialog.getExistingDirectory(self, 'Select Predictions Directory')
        print("Selected predictions directory:", self.predictions_dir)

    def display_images(self):
        image_name = self.image_name_input.text()
        self.display_image(os.path.join(self.raw_dir, image_name), self.viewer_raw)
        self.display_image(os.path.join(self.labels_dir, image_name), self.viewer_labels, True)
        self.display_image(os.path.join(self.predictions_dir, image_name), self.viewer_predictions)

    def display_image(self, image_path, viewer, is_label=False):
        pixmap = QPixmap(image_path)
        
        if is_label:
            painter = QPainter(pixmap)
            pen = QPen()
            pen.setWidth(3)
            pen.setColor(QColor(255, 0, 0))
            painter.setPen(pen)

            base = os.path.splitext(image_path)[0]
            labels_path = f"{base}.txt"

            with open(labels_path, 'r') as f:
                for line in f:
                    _, x_center, y_center, width, height = map(float, line.split())
                    x_center *= pixmap.width()
                    y_center *= pixmap.height()
                    width *= pixmap.width()
                    height *= pixmap.height()
                    x_top_left = round(x_center - width / 2)
                    y_top_left = round(y_center - height / 2)
                    width = round(width)
                    height = round(height)

                    painter.drawRect(x_top_left, y_top_left, width, height)

            painter.end()

        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        scene.addItem(item)
        viewer.setScene(scene)

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def wheelEvent(self, event):
        factor = 1.15 ** (event.angleDelta().y() / 120)
        self.scale(factor, factor)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ImageViewer()
    ex.show()
    sys.exit(app.exec_())
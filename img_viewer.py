from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QMessageBox, QFileDialog, QLabel, QGridLayout, QLineEdit, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem
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
        self.raw_dir_label = QLabel()
        self.layout.addWidget(self.raw_dir_label)

        self.labels_dir_button = QPushButton('Select Labels Directory')
        self.labels_dir_button.clicked.connect(self.select_labels_dir)
        self.layout.addWidget(self.labels_dir_button)
        self.labels_dir_label = QLabel()
        self.layout.addWidget(self.labels_dir_label)

        self.predictions_dir_button = QPushButton('Select Predictions Directory')
        self.predictions_dir_button.clicked.connect(self.select_predictions_dir)
        self.layout.addWidget(self.predictions_dir_button)
        self.predictions_dir_label = QLabel()
        self.layout.addWidget(self.predictions_dir_label)

        self.image_name_input = QLineEdit()
        self.image_name_input.returnPressed.connect(self.display_images)
        self.layout.addWidget(self.image_name_input)

        self.viewer_raw_label = QLabel("Raw Image Below:")
        self.layout.addWidget(self.viewer_raw_label)
        self.viewer_raw = ZoomableGraphicsView(self)
        self.layout.addWidget(self.viewer_raw)

        self.viewer_labels_label = QLabel("Labeled Image Below:")
        self.layout.addWidget(self.viewer_labels_label)
        self.viewer_labels = ZoomableGraphicsView(self)
        self.layout.addWidget(self.viewer_labels)

        self.viewer_predictions_label = QLabel("Inference Prediction from Current Model:")
        self.layout.addWidget(self.viewer_predictions_label)
        self.viewer_predictions = ZoomableGraphicsView(self)
        self.layout.addWidget(self.viewer_predictions)

    def select_raw_dir(self):
        selected_dir = QFileDialog.getExistingDirectory(self, 'Select Raw Images Directory')
        if selected_dir:
            self.raw_dir = selected_dir
            display_text = "Selected Raw Images Directory: " + selected_dir
            self.raw_dir_label.setText(display_text)

    def select_labels_dir(self):
        selected_dir = QFileDialog.getExistingDirectory(self, 'Select Labels Directory')
        if selected_dir:
            self.labels_dir = selected_dir
            display_text = "Selected Labels Directory: " + selected_dir
            self.labels_dir_label.setText(display_text)

    def select_predictions_dir(self):
        selected_dir = QFileDialog.getExistingDirectory(self, 'Select Predictions Images Directory')
        if selected_dir:
            self.predictions_dir = selected_dir
            display_text = "Selected Predictions Images Directory: " + selected_dir
            self.predictions_dir_label.setText(display_text)

    def display_images(self):
        image_name = self.image_name_input.text()
        print("Displaying images for:", image_name)
        temp_name = image_name + '.png'
        temp_label = image_name + '.txt'
        if not os.path.exists(os.path.join(self.raw_dir, temp_name)):
            QMessageBox.warning(self, 'Error', 'Image not found in Raw Image folder')
            return
        elif not os.path.exists(os.path.join(self.labels_dir, temp_label)):
            QMessageBox.warning(self, 'Error', 'Image label not found in Labels folder')
            return
        elif not os.path.exists(os.path.join(self.predictions_dir, temp_name)):
            QMessageBox.warning(self, 'Error', 'Image not found in Predictions folder')
            return
        else:
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
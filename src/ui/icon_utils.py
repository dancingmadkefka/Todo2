from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor
from PySide6.QtCore import Qt
from PySide6.QtSvg import QSvgRenderer

def create_colored_icon(icon_path, base_color, background_color, icon_color=None):
    renderer = QSvgRenderer(icon_path)
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    
    if icon_color is None:
        icon_color = adjust_icon_color_for_theme(base_color, background_color)
    
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), icon_color)
    painter.end()
    
    return QIcon(pixmap)

def adjust_icon_color_for_theme(base_color, background_color):
    background_brightness = (background_color.red() * 299 + background_color.green() * 587 + background_color.blue() * 114) / 1000
    if background_brightness > 128:
        return QColor(60, 60, 60)  # Darker color for light backgrounds
    else:
        return QColor(200, 200, 200)  # Lighter color for dark backgrounds

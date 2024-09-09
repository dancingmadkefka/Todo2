from PySide6.QtGui import QColor

def adjust_icon_color_for_theme(base_color, background_color):
    # Calculate the luminance of the background color
    luminance = (0.299 * background_color.red() + 
                 0.587 * background_color.green() + 
                 0.114 * background_color.blue()) / 255

    if luminance > 0.5:
        # For light backgrounds, use a darker color
        return QColor(max(0, background_color.red() - 100),
                      max(0, background_color.green() - 100),
                      max(0, background_color.blue() - 100))
    else:
        # For dark backgrounds, use a lighter color
        return QColor(min(255, background_color.red() + 100),
                      min(255, background_color.green() + 100),
                      min(255, background_color.blue() + 100))

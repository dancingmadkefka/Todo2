from PySide6.QtGui import QColor

def adjust_icon_color_for_theme(base_color, background_color):
    base_hue = base_color.hue()
    base_saturation = base_color.saturation()
    base_value = base_color.value()
    
    bg_value = background_color.value()
    
    # Adjust saturation based on background brightness
    if bg_value > 128:
        # Dark icon on light background
        new_saturation = min(base_saturation * 1.2, 255)
        new_value = max(base_value * 0.8, 0)
    else:
        # Light icon on dark background
        new_saturation = max(base_saturation * 0.8, 0)
        new_value = min(base_value * 1.2, 255)
    
    # Ensure sufficient contrast
    contrast_threshold = 128
    if abs(new_value - bg_value) < contrast_threshold:
        new_value = bg_value + contrast_threshold if bg_value < 128 else bg_value - contrast_threshold
    
    return QColor.fromHsv(base_hue, new_saturation, new_value)

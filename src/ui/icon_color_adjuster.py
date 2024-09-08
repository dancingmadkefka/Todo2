from PySide6.QtGui import QColor

def adjust_icon_color_for_theme(base_color, background_color):
    base_hue = base_color.hue()
    base_saturation = base_color.saturation()
    base_value = base_color.value()
    
    bg_hue = background_color.hue()
    bg_saturation = background_color.saturation()
    bg_value = background_color.value()
    
    # Determine if the background is light or dark
    is_light_background = bg_value > 128
    
    # Adjust hue to be complementary to the background
    new_hue = (bg_hue + 180) % 360
    
    # Adjust saturation based on background saturation
    new_saturation = min(255, base_saturation + (255 - bg_saturation) // 2)
    
    # Adjust value (brightness) for contrast
    if is_light_background:
        new_value = min(base_value, bg_value - 50)  # Darker than background
    else:
        new_value = max(base_value, bg_value + 50)  # Lighter than background
    
    # Ensure sufficient contrast
    contrast_threshold = 128
    if abs(new_value - bg_value) < contrast_threshold:
        new_value = bg_value - contrast_threshold if is_light_background else bg_value + contrast_threshold
    
    # Clamp values to valid range
    new_value = max(0, min(255, new_value))
    
    return QColor.fromHsv(new_hue, new_saturation, new_value)

# Todo App UI/Styling Guide

This guide provides detailed information about the Todo App's user interface components, their styling, and how to modify them. The app's UI is built using PySide6 (Qt for Python) and styled using Qt Style Sheets (QSS), which is similar to CSS.

## Table of Contents

1. [Overview](#overview)
2. [Main UI Components](#main-ui-components)
3. [Styling with QSS](#styling-with-qss)
4. [Color Customization](#color-customization)
5. [Icons](#icons)
6. [Modifying UI Components](#modifying-ui-components)
7. [Adding New UI Elements](#adding-new-ui-elements)
8. [Best Practices](#best-practices)

## Overview

The Todo App's user interface is primarily defined in `src/ui/main_window.py`, with additional components in `src/ui/todo_list_widget.py` and `src/ui/task_widget.py`. The styling is controlled by two QSS files:

- `src/ui/styles.qss`: Contains the base styles for the application.
- `src/ui/user_colors.qss`: Contains user-customized color styles.

The main window consists of several key areas:

- Input area for adding new tasks
- Filtering and sorting options
- Task list displaying individual tasks
- Dialogs for editing tasks, managing categories, and customizing colors

## Main UI Components

1. **MainWindow** (QMainWindow)
   - The main application window containing all other components

2. **QLineEdit**
   - Used for task input

3. **QComboBox**
   - Used for priority selection, category selection, and filtering/sorting options

4. **QToolButton**
   - Used for setting due date and adding tasks

5. **QCalendarWidget**
   - Used for selecting due dates

6. **TodoListWidget** (QScrollArea)
   - Displays the list of tasks

7. **TaskWidget** (Custom QWidget)
   - Represents individual tasks in the list

8. **QLabel**
   - Used for displaying task details and labels

9. **QPushButton**
   - Used for various actions like adding tasks and customizing colors

10. **QDialog**
    - Used for editing tasks, managing categories, and customizing colors

## Styling with QSS

The app's styling is defined in two QSS files:

1. `src/ui/styles.qss`: This file contains the base styles for the application.
2. `src/ui/user_colors.qss`: This file contains user-customized color styles.

Here's an overview of how different components are styled:

```qss
/* Example from styles.qss */
QMainWindow {
    padding: 10px;
}

QPushButton {
    padding: 5px 10px;
    border-radius: 3px;
}

QLineEdit, QComboBox, QDateEdit {
    padding: 5px;
    border-radius: 3px;
    border: 1px solid #CCCCCC;
}

/* Example from user_colors.qss */
QWidget { background-color: #fffab0; }
QWidget { color: #070707; }
QLabel#subtext { color: #027000; }
QPushButton { background-color: #717171; }
QWidget#TaskWidget { background-color: #ffed29; }
QWidget#TaskWidget[completed="true"] { background-color: #4d4d4d; }
```

## Color Customization

The app allows users to customize colors for various UI elements. This is managed through the `ColorCustomizationDialog` class in `src/ui/color_dialog.py`. Users can customize the following elements:

- Background color
- Text color
- Subtext color
- Button color
- Task background color
- Completed task background color

When colors are customized, they are saved to the `user_colors.qss` file and applied to the UI.

## Icons

The app uses SVG icons for various UI elements. These icons are defined in the `resources.qrc` file and include:

- Edit icon
- Delete icon
- Add icon
- Calendar icon
- Check icon

The icons are colorized dynamically based on the current color scheme using the `create_colored_icon` method in the `MainWindow` class.

## Modifying UI Components

To modify the appearance of UI components, you'll need to edit the `src/ui/styles.qss` file or use the color customization dialog. Here are some common modifications:

1. **Changing Colors**:
   Use the built-in color customization dialog or modify the `user_colors.qss` file.

2. **Adjusting Sizes and Padding**:
   Modify `padding`, `margin`, `width`, `height`, or `font-size` properties in `styles.qss`.

   Example:
   ```qss
   QLineEdit, QComboBox, QDateEdit {
       padding: 8px;
       border-radius: 4px;
   }
   ```

3. **Changing Fonts**:
   Modify the `font-family`, `font-size`, or `font-weight` properties in `styles.qss`.

4. **Modifying Borders**:
   Adjust the `border`, `border-radius`, or individual border properties in `styles.qss`.

## Adding New UI Elements

When adding new UI elements:

1. Add the element to the appropriate Python file (e.g., `main_window.py` or `task_widget.py`).
2. If needed, add new style rules in `styles.qss` for the new elements.
3. For color customization, update the `ColorCustomizationDialog` class and the `save_colors` method to include the new element.

Example:
```python
# In main_window.py
new_label = QLabel("New Label")
new_label.setObjectName("customLabel")

# In styles.qss
QLabel#customLabel {
    font-weight: bold;
    color: #4a90e2;
}
```

## Best Practices

1. **Consistency**: Maintain a consistent look and feel throughout the app.
2. **Readability**: Use colors with good contrast for text and background.
3. **Responsiveness**: Ensure the UI looks good at different window sizes.
4. **Modularity**: Group related styles together in the QSS files.
5. **Comments**: Add comments in the QSS files to explain complex styles or groupings.
6. **Testing**: Always test UI changes on different platforms and screen sizes.
7. **Accessibility**: Consider color-blind users when choosing colors, and ensure proper contrast ratios.
8. **Icon Management**: When adding or modifying icons, update the `resources.qrc` file and recompile resources using `pyside6-rcc resources.qrc -o resources_rc.py`.
9. **Dynamic Styling**: Utilize the `load_and_apply_stylesheet` method in `MainWindow` to apply style changes dynamically.
10. **Color Customization**: Make use of the `ColorCustomizationDialog` for user-friendly color adjustments.

Remember to restart the application after making changes to the QSS files to see the effects. The app automatically loads both `styles.qss` and `user_colors.qss` on startup, combining them to create the final appearance.
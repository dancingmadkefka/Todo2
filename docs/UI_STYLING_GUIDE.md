# Todo App UI/Styling Guide

This guide provides detailed information about the Todo App's user interface components, their styling, and how to modify them. The app's UI is built using PySide6 (Qt for Python) and styled using Qt Style Sheets (QSS), which is similar to CSS.

## Table of Contents

1. [Overview](#overview)
2. [Main UI Components](#main-ui-components)
3. [Styling with QSS](#styling-with-qss)
4. [Color Scheme](#color-scheme)
5. [Fonts](#fonts)
6. [Modifying UI Components](#modifying-ui-components)
7. [Adding New UI Elements](#adding-new-ui-elements)
8. [Best Practices](#best-practices)

## Overview

The Todo App's user interface is defined in `ui/main_window.py`, and its styling is controlled by `ui/styles.qss`. The main window consists of several key areas:

- Input area for adding new tasks
- Filtering and sorting options
- Task list displaying individual tasks
- Dialogs for editing tasks and managing categories

## Main UI Components

1. **MainWindow** (QMainWindow)
   - The main application window containing all other components

2. **QLineEdit**
   - Used for task input

3. **QComboBox**
   - Used for priority selection, category selection, and filtering/sorting options

4. **QDateEdit**
   - Used for selecting due dates

5. **QPushButton**
   - Used for actions like adding tasks, editing, and deleting

6. **QListWidget** (TodoListWidget)
   - Displays the list of tasks

7. **TaskWidget** (Custom QWidget)
   - Represents individual tasks in the list

8. **QCheckBox**
   - Used for marking tasks as complete

9. **QLabel**
   - Used for displaying task details and priority labels

10. **QDialog** (TaskEditDialog, CategoryManageDialog)
    - Used for editing tasks and managing categories

## Styling with QSS

The app's styling is defined in `ui/styles.qss`. This file uses Qt Style Sheets (QSS) syntax, which is similar to CSS. Here's an overview of how different components are styled:

```qss
/* Global Styles */
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
    color: #333333;
    background-color: #f0f0f0;
}

/* Input Area Styles */
QLineEdit, QComboBox, QDateEdit {
    padding: 8px;
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
}

/* Button Styles */
QPushButton {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background-color: #4a90e2;
    color: #ffffff;
    font-weight: bold;
}

/* Task List Styles */
QListWidget {
    border: 1px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
}

/* Task Widget Styles */
TaskWidget {
    background-color: transparent;
    border-radius: 4px;
    border: 1px solid #eeeeee;
}

/* Priority Label Styles */
QLabel[class="priority-label"] {
    color: #ffffff;
    font-weight: bold;
    border-radius: 4px;
    padding: 2px 6px;
}

/* ... more styles ... */
```

## Color Scheme

The app uses a color scheme based on blue tones with accents. Here are the main colors used:

- Primary Blue: #4a90e2
- Background: #f0f0f0 (light gray)
- Text: #333333 (dark gray)
- Borders: #cccccc (light gray)
- Priority Colors:
  - Low: #28a745 (green)
  - Medium: #ffc107 (yellow)
  - High: #dc3545 (red)

## Fonts

The app primarily uses the 'Segoe UI' font, with Arial and sans-serif as fallbacks. The base font size is 14px.

## Modifying UI Components

To modify the appearance of UI components, you'll need to edit the `ui/styles.qss` file. Here are some common modifications:

1. **Changing Colors**:
   Find the relevant selector and modify the `color`, `background-color`, or `border-color` properties.

   Example: To change the primary button color:
   ```qss
   QPushButton {
       background-color: #00a86b;  /* Change to your desired color */
   }
   ```

2. **Adjusting Sizes**:
   Modify `padding`, `margin`, `width`, `height`, or `font-size` properties.

   Example: To make input fields larger:
   ```qss
   QLineEdit, QComboBox, QDateEdit {
       padding: 10px;  /* Increase padding */
       font-size: 16px;  /* Increase font size */
   }
   ```

3. **Changing Fonts**:
   Modify the `font-family`, `font-size`, or `font-weight` properties.

   Example: To change the global font:
   ```qss
   QWidget {
       font-family: 'Arial', sans-serif;
       font-size: 15px;
   }
   ```

4. **Modifying Borders**:
   Adjust the `border`, `border-radius`, or individual border properties.

   Example: To change task widget borders:
   ```qss
   TaskWidget {
       border: 2px solid #4a90e2;
       border-radius: 8px;
   }
   ```

## Adding New UI Elements

When adding new UI elements in `ui/main_window.py`, you can style them by:

1. Using existing styles if the new element is of the same type as an existing one.
2. Adding new style rules in `ui/styles.qss` for the new elements.
3. Setting object names or properties in Python and using them as selectors in QSS.

Example:
```python
# In ui/main_window.py
new_label = QLabel("New Label")
new_label.setObjectName("specialLabel")

# In ui/styles.qss
QLabel#specialLabel {
    color: #4a90e2;
    font-weight: bold;
}
```

## Best Practices

1. **Consistency**: Maintain a consistent look and feel throughout the app.
2. **Readability**: Use colors with good contrast for text and background.
3. **Responsiveness**: Ensure the UI looks good at different window sizes.
4. **Modularity**: Group related styles together in the QSS file.
5. **Comments**: Add comments in the QSS file to explain complex styles or groupings.
6. **Testing**: Always test UI changes on different platforms and screen sizes.
7. **Accessibility**: Consider color-blind users when choosing colors, and ensure proper contrast ratios.

Remember to restart the application after making changes to the QSS file to see the effects. If you're making frequent changes, you can implement a "hot reload" feature that reloads the stylesheet without restarting the app.
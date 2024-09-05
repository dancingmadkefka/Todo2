# Todo App

## Project Overview

This Todo App is a desktop application built using Python and PySide6 (Qt for Python). It provides a user-friendly interface for managing tasks, including features such as task creation, editing, deletion, filtering, and sorting. The app also supports task categories and priority levels.

## Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Clone this repository:
   ```
   git clone https://github.com/yourusername/todo-app.git
   cd todo-app
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the Todo App, execute the following command from the project root directory:

```
python src/main.py
```

## Project Structure

The project is organized as follows:

```
todo_app/
│
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   └── db_manager.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── task.py
│   ├── ui/
│   │   ├── icons/
│   │   │   ├── add.png
│   │   │   ├── categories.png
│   │   │   ├── delete.png
│   │   │   └── edit.png
│   │   │   └── app_icon.ico
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── styles.qss
│   ├── __init__.py
│   └── main.py
├── todo.db
└── README.md
```

### Key Components

1. `main.py`: The entry point of the application. It initializes the database, sets up the GUI, and runs the main event loop.

2. `database/db_manager.py`: Handles all database operations, including CRUD operations for tasks and categories.

3. `models/task.py`: Defines the Task data model used throughout the application.

4. `ui/main_window.py`: Contains the main window class and related widgets for the application's user interface.

5. `ui/styles.qss`: Defines the CSS-like styles for the application's UI components.

## Developer's Guide

### Main Application Flow

1. The application starts in `main.py`, which initializes the database and creates the main window.
2. The `MainWindow` class in `ui/main_window.py` sets up the user interface and handles user interactions.
3. Tasks are stored in an SQLite database (`todo.db`) and managed through the `DatabaseManager` class in `database/db_manager.py`.
4. The `Task` class in `models/task.py` represents individual tasks and provides methods for task manipulation.

### Key Classes and Their Responsibilities

1. `DatabaseManager` (in `db_manager.py`):
   - Handles all database operations (CRUD for tasks and categories)
   - Manages database connections and table creation

2. `Task` (in `task.py`):
   - Represents a single task with properties like title, description, due date, priority, etc.
   - Provides methods for task serialization and deserialization

3. `MainWindow` (in `main_window.py`):
   - Sets up the main application window and UI components
   - Handles user interactions and updates the UI accordingly
   - Manages task filtering and sorting

4. `TaskWidget` (in `main_window.py`):
   - Represents a single task in the UI
   - Handles task-specific interactions like marking as complete, editing, and deleting

5. `TodoListWidget` (in `main_window.py`):
   - Custom QListWidget for displaying tasks
   - Manages the list of TaskWidget items

6. `TaskEditDialog` (in `main_window.py`):
   - Dialog for editing task details

7. `CategoryManageDialog` (in `main_window.py`):
   - Dialog for managing categories (add, edit, delete)

### UI/Styling Guide

The application's user interface is styled using Qt Style Sheets (QSS), which is similar to CSS. The styles are defined in `ui/styles.qss`. Here's a guide to help you understand and modify the UI:

1. **Global Styles**: 
   - Font family, size, and colors are set for all QWidget instances
   - Background color for the main window is set to white

2. **Input Area Styles**:
   - Styles for QLineEdit, QComboBox, and QDateEdit (padding, border, border-radius)
   - Focus styles for input elements
   - Button styles (background color, hover and pressed states)

3. **Task List Styles**:
   - Styles for the QListWidget that displays tasks
   - Item padding and border styles

4. **Task Widget Styles**:
   - Styles for individual task widgets
   - Completed task styles (gray color and strike-through text)

5. **Priority Label Styles**:
   - Color-coded labels for different priority levels (Low: green, Medium: yellow, High: red)

6. **Scrollbar Styles**:
   - Custom scrollbar appearance

7. **Dialog Styles**:
   - Styles for QDialog (used in task editing and category management)

8. **Checkbox Styles**:
   - Custom checkbox appearance

To modify the UI:

- **Colors**: Look for color codes (e.g., #4a90e2) and change them to your desired colors
- **Sizes**: Adjust pixel values for padding, margins, and sizes
- **Fonts**: Modify font-family, font-size, and font-weight properties
- **Layout**: Adjust padding, margin, and border properties to change spacing and layout

Example: To change the primary button color, find this section in `styles.qss`:

```qss
QPushButton {
    background-color: #4a90e2;
}
```

And change the color code to your desired color:

```qss
QPushButton {
    background-color: #00a86b;
}
```

Remember to restart the application after making changes to the QSS file to see the effects.

## Extending the Application

To add new features or modify existing ones:

1. **New Task Properties**: Update the `Task` class in `models/task.py` and modify the database schema in `database/db_manager.py`.
2. **UI Changes**: Modify `ui/main_window.py` to add new widgets or change the layout. Update `ui/styles.qss` for styling.
3. **New Functionality**: Add new methods to `MainWindow` or create new dialog classes as needed.
4. **Database Changes**: Update `DatabaseManager` in `db_manager.py` to add new database operations.

Always ensure that changes are reflected across all relevant components (model, database, and UI) to maintain consistency.
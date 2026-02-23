# Routes Folder

This folder contains all the route handler files for the Flask application. Each file in this folder defines endpoints (routes) that the web application responds to. These routes connect URLs to Python functions, which process requests and return responses (such as HTML pages or JSON data). Routes are the backbone of any Flask web app, enabling user interaction and data manipulation.

## What is CRUD?
CRUD stands for **Create, Read, Update, and Delete**. These are the four basic operations for managing data in a web application:
- **Create**: Add new data (e.g., a new story)
- **Read**: Retrieve and display data (e.g., view stories)
- **Update**: Modify existing data (e.g., edit a story)
- **Delete**: Remove data (e.g., delete a story)

## story.py
The `story.py` file implements all CRUD operations for the "Story" feature of the app. Here's how each operation is handled:

- **Create**: The `/story/new` route allows users to create a new story. It displays a form and, upon submission, saves the new story to the database.
- **Read**: The `/story/list` route shows all stories, and `/story/<int:id>` displays a single story by its ID.
- **Update**: The `/story/edit/<int:id>` route lets users edit an existing story. It loads the story's data into a form, and updates the database when the form is submitted.
- **Delete**: The `/story/delete/<int:id>` route allows users to delete a story. It confirms the deletion and then removes the story from the database.

Each route uses Flask's decorators to map URLs to Python functions, and leverages forms and models to interact with the database. This structure makes it easy to manage stories and demonstrates the CRUD pattern in a real-world Flask application.

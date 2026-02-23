# Classes Folder

This folder contains core Python classes that define the data structure and forms used throughout the Flask application.

## data.py
The `data.py` file defines the **database models** for the app using SQLAlchemy. Models are Python classes that represent tables in the database. This file includes:

- **User model**: Represents users of the app, storing information like names, emails, Google IDs, profile images, and roles. It also links each user to the stories they have written.
- **Story model** (not shown above, but referenced): Represents stories created by users, with fields for title, content, author, and timestamps.
- **Authentication helpers**: Methods for validating Google login tokens and converting user data to dictionaries for easy use in the app.

These models are the foundation for storing and retrieving data in the application.

## forms.py
The `forms.py` file defines **web forms** using Flask-WTF and WTForms. Forms are used to collect user input in a structured way. This file includes:

- **StoryForm**: Lets users create or edit stories, with fields for the title and content.
- **ProfileForm**: Allows users to update their profile information, such as name, email, mobile number, and profile image.
- **ProfileImageForm**: A simple form for uploading a profile image.

These forms ensure that user input is validated and organized before being processed or saved to the database.

Together, `data.py` and `forms.py` provide the structure for both the data and the user interactions in the app.
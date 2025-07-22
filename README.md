# JD_legal

JD_legal is a Django REST Framework (DRF) API for managing transcription projects with role-based task assignment. It supports user registration, authentication, project creation, assignment management, and transcript uploads, with roles for admin, transcriber, and proofreader.

## Features

- **User Authentication**: JWT-based login, registration, and logout.
- **Role Management**: Users can be admins, transcribers, or proofreaders.
- **Project Management**: Create, update, list, and delete projects.
- **Assignment System**: Assign transcribers and proofreaders to projects (manual or auto-assign).
- **Transcript Uploads**: Upload and manage transcripts for assigned projects.
- **User & Project Summaries**: Get statistics on tasks and revenue.
- **Admin Panel**: Django admin for user and project management.
- **CORS Support**: Configurable origins for frontend integration.

## Setup

1. **Clone the repository**

   ```sh
   git clone <repo-url>
   cd JD_legal
   ```

2. **Create a virtual environment**

   ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```sh
    pip install -r requirements.txt
   ```
4. **Configure environment variables**
   Create a `.env` file in the project root with the following variables:
   ```env
   SECRET_KEY=your_secret_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,
    CORS_ALLOWED_ORIGINS=http://localhost:3000
    DATABASE_URL=sqlite:///db.sqlite3
   ```
5. **Run migrations**
   ```sh
   python manage.py migrate
   ```
6. **Create a superuser**
   ```sh
   python manage.py createsuperuser
   ```
7. **Run the development server**
   ```sh
   python manage.py runserver
   ```
8. **Access the API**
   Open your browser and go to `http://localhost:8000/api/` to access
   the API documentation and endpoints.

## API Documentation

The API is documented using Swagger. You can access it at `http://localhost:8000/api/docs/` after running the server.

## API Endpoints

### Authentication and User Management

Here's your API endpoint documentation formatted in Markdown:

---

# API Endpoints

## Authentication

* **`POST /api/auth/token/`**
    * Obtain JWT token (login).
* **`POST /api/auth/register/`**
    * Register a new user.
* **`POST /api/auth/logout/`**
    * Logout and blacklist refresh token.
* **`GET /api/auth/me`**
    * Get current user information.

## Users

* **`GET /api/auth/users/`**
    * List all users (Admin only).
* **`PATCH /api/auth/users/<id>/`**
    * Update user details (Admin only).
* **`DELETE /api/auth/users/<id>/`**
    * Deactivate user (Admin only).

## Projects

* **`POST /api/projects/create/`**
    * Create a new project (manual or auto-assign).
* **`GET /api/projects/`**
    * List all projects.
* **`GET /api/projects/<id>/`**
    * Get details for a specific project.
* **`PATCH /api/projects/<id>/update/`**
    * Update an existing project.
* **`DELETE /api/projects/<id>/delete/`**
    * Delete a project.

## Assignments

* **`GET /api/projects/assigned`**
    * List assignments for the current authenticated user.
* **`POST /api/assignments/create/`**
    * Assign a user to a project.

## Transcripts

* **`POST /api/transcripts/upload/`**
    * Upload a transcript file.
* **`GET /api/projects/<id>/transcripts/`**
    * List all transcripts associated with a specific project.
* **`POST /transcripts/<id>/mark-final/`**
    * Mark a transcript as final.

## User Summary

* **`GET /api/user/summary/`**
    * Get a summary of tasks and revenue for the current authenticated user.

---

Here's your project structure information formatted in Markdown, with a brief note on development:

-----

# Project Structure

Your Django project is organized into the following applications:

  * **`users/`**
      * Contains the custom user model, authentication views (e.g., login, registration, password management), and related user management logic.
  * **`scriptapp/`**
      * Houses the core business logic for your application, including:
          * Project management (creation, listing, updating, deleting projects).
          * Assignment handling (assigning users to projects, listing user assignments).
          * Transcript management (uploading, listing, marking as final).
  * **`core/`**
      * Holds utility functions, common decorators, abstract base models, and other shared logic that can be reused across different applications within your project.
  * **`transcription/`**
      * This is your main Django project directory, containing:
          * `settings.py`: Your project's core configuration.
          * `urls.py`: The root URL routing for your entire application.
          * `wsgi.py`: The entry point for WSGI-compatible web servers.
          * `asgi.py`: (Potentially) The entry point for ASGI-compatible web servers (if using WebSockets or async features).

-----



### Lint code

```sh
black .
```

See LICENSE for third-party assets. Main code is MIT licensed.

> For API usage examples, see API_collection/Transcription API.postman_collection.json.

## License

This project is licensed under the MIT License. See the

Here’s the full Markdown section for your `README.md` with the added instructions on how to create a new Django app:

---

## **🔹 Backend**
```md
# Backend - Django API

## 📌 Prerequisites
- Python 3.x installed
- Virtual environment (`venv`)
- PostgreSQL or SQLite (depending on your setup)

## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/your-repo.git
cd backend
```

### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # For Mac/Linux
venv\Scripts\activate  # For Windows
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

If you need to update the `requirements.txt` file with the current dependencies, run:
```sh
pip freeze > requirements.txt
```

### 4️⃣ Set Up Environment Variables (`.env`)
Create a `.env` file in the `backend/` directory and add:
```ini
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3  # Change if using PostgreSQL
```

### 5️⃣ Apply Migrations & Create Superuser
```sh
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # Follow prompts to create admin user
```

### 6️⃣ Run the Development Server
```sh
python manage.py runserver
```

## 🧱 Creating a New App
To create a new Django app within the project:

1. Run the `startapp` command:
    ```sh
    python manage.py startapp myapp
    ```

2. Add the app to `INSTALLED_APPS` in `settings.py`:
    ```python
    INSTALLED_APPS = [
        ...
        'myapp',
    ]
    ```

3. (Optional but recommended) Create `urls.py`, `serializers.py`, and structure your models and views.

4. Include app routes in the main `urls.py`:
    ```python
    path('api/myapp/', include('myapp.urls')),
    ```

5. Apply migrations as needed:
    ```sh
    python manage.py makemigrations
    python manage.py migrate
    ```

## 🔥 Available Commands
| Command | Description |
|---------|-------------|
| `python manage.py runserver` | Run the Django development server |
| `python manage.py createsuperuser` | Create an admin user |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py makemigrations` | Generate migration files |
| `python manage.py collectstatic` | Collect static files for production |
| `python manage.py shell` | Open Django shell for debugging |

## 🔗 API Documentation (Optional)
If using **DRF Browsable API**, access:
```
http://127.0.0.1:8000/api/
```
or use **Swagger/Postman** for testing API endpoints.

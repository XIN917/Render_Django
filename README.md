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

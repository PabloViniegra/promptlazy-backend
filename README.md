# 🧠 promptlazy-backend

PromptLazy Backend is a RESTful API built with FastAPI for prompt management and user authentication, leveraging OpenAI's GPT-4 for prompt optimization.

## Technologies Used
- Python 3.12+
- FastAPI
- SQLAlchemy
- OpenAI API
- PostgreSQL (or SQLite for development)
- Alembic
- Passlib (bcrypt)
- python-dotenv
- jose (JWT)

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/promptlazy-backend.git
cd promptlazy-backend/app
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Unix/Mac:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r ../requirements.txt
```

### 4. Set Environment Variables
Create a `.env` file in the `app/` directory with the following content:
```
OPENAI_API_KEY=your_openai_api_key
SECRET_KEY=your_secret_key
DATABASE_URL=sqlite:///./test.db  # Or your PostgreSQL URL
```

- `OPENAI_API_KEY`: Your OpenAI API key
- `SECRET_KEY`: Secret key for JWT
- `DATABASE_URL`: SQLAlchemy database URL

### 5. Run Database Migrations (if using Alembic/PostgreSQL)
> For SQLite, the database will be created automatically on first run.

### 6. Run the Application Locally
```bash
uvicorn app.main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

### 7. API Documentation
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

### 8. Database Versions with Alembic

Alembic is a control version system for relational databases.

#### Create a new migration

```bash
alembic revision --autogenerate -m "message"
```

#### Apply

```bash
alembic upgrade head
```


## Main Endpoints
- `POST /auth/register` — Register a new user
- `POST /auth/login` — User login
- `POST /auth/refresh` — Refresh JWT tokens
- `GET /auth/me` — Get current user info
- `GET /prompt/` — List user prompts
- `POST /prompt/improve` — Improve a prompt using GPT-4
- `PUT /prompt/{prompt_id}` — Regenerate a prompt
- `DELETE /prompt/{prompt_id}` — Delete a prompt
- `PATCH /prompt/{prompt_id}/favorite` — Toggle favorite status
- `GET /prompt/favorites` — List favorite prompts

## License
MIT

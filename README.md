# 📚 Sonic Library

Sonic Library is a modern, full-stack digital library platform built with FastAPI and Next.js. It allows users to browse books, write reviews, and receive AI-powered recommendations based on their reading history and preferences.

 

⸻

## ⚙️ Tech Stack

| Layer      | Tech                              |
|------------|-----------------------------------|
| Backend    | Python, FastAPI, SQLAlchemy       |
| Frontend   | React, Next.js 15 (App Router)    |
| AI Engine  | LangChain + OpenAI (or local LLMs)|
| Database   | PostgreSQL (via Docker)           |
| DevOps  | Docker, pre-commit, GitHub Actions, Pytest, ESLint |



⸻

## 🚀 Features
- 🔒 JWT-based authentication
- 📖 Book listing with genres and tags
- ✍️ User reviews and star ratings
- 🧠 AI-based book recommendation system
- 💻 Responsive UI with dark mode
- 🐳 Dockerized development environment
- ✅ Git hooks for linting and testing via pre-commit
- 📦 REST API documented with OpenAPI (Swagger)

⸻

## 📂 Project Structure

<pre>

```
sonic-library/
├── backend/                # FastAPI app
│   ├── app/
│   ├── alembic/            # DB migrations
│   └── tests/              # Pytest-based tests
├── frontend/               # Next.js 15 app
│   └── src/app/            # App Router pages
├── .github/                # PR & issue templates, CI config
├── docker-compose.yml
└── README.md
```

</pre>


⸻

## 🚀 Getting Started

### 📦 Requirements
	•	Docker & Docker Compose
	•	Python 3.10+
	•	Node.js 18+

⸻

## 🐳 Start with Docker

### Build and run everything
docker-compose up --build

Access the frontend at http://localhost:3000
Access the backend API docs at http://localhost:8000/docs

⸻

## 🧪 Run Tests

Backend tests (pytest):

cd backend
pytest

Frontend lint:

cd frontend
npm install
npm run lint



⸻

## 🧹 Pre-commit Hooks

### One-time setup
pre-commit install

### Run all hooks manually
pre-commit run --all-files

That’s looking super clean and professional, Leo! 🔥 Here’s the final section you can append to your README.md:

⸻

## 🧭 Next Steps
Check out the [Project board](https://github.com/leotonezi/sonic-library/projects) to see what’s coming next!
We’re actively working on new features like:
- User profile pages
- OAuth login
- Admin dashboard
- Genre-based book filters
- More AI enhancements

Stay tuned and feel free to contribute!

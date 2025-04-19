# 📝 Changelog

All notable changes to this project will be documented in this file.  
This project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] – 2025-04-19

### 🚀 Added
- Initial project structure with `backend/` (FastAPI) and `frontend/` (Next.js 15)
- PostgreSQL integration with Docker Compose
- User authentication with JWT (login, register)
- Fully functional book listing with search by title and genre
- Genre enum setup and genre dropdown in the frontend
- AI-powered book recommendation route using LangChain and OpenAI
- Client-side review submission and optimistic UI updates
- API integration between FastAPI and Next.js
- Review system: users can create, edit, and delete their own reviews
- Book detail page displays average rating
- ESLint, pre-commit hooks, and CI (GitHub Actions) for linting and tests
- `versioning.md` and version bumping script (`bump_version.py`)

---

### 🛠️ In Progress
- Restricting access to protected routes (auth required on all necessary endpoints)
- Admin-specific features (e.g., managing books or users)
- External book import integration (e.g., Google Books API)

---

⚠️ This is an early-stage pre-release. Expect breaking changes as the project evolves.
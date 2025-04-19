## [0.1.1](https://github.com/leotonezi/sonic-library/compare/v0.1.0...v0.1.1) (2025-04-19)


### Bug Fixes

* branch names ([0597a83](https://github.com/leotonezi/sonic-library/commit/0597a83d2f6a972a7e8ca01e340440b1d1a9916a))
* node version ([ee48280](https://github.com/leotonezi/sonic-library/commit/ee482804eb6447db1630853a2b9866350672bad3))
* release json file ([8c933ed](https://github.com/leotonezi/sonic-library/commit/8c933edcd48d98473e5c1301092a07704e49abb4))

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

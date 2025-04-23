## [0.1.2](https://github.com/leotonezi/sonic-library/compare/v0.1.1...v0.1.2) (2025-04-23)


### Bug Fixes

* env problems in CI ([dd6251a](https://github.com/leotonezi/sonic-library/commit/dd6251a1993a9ce4378919d9d04f1be59f49259d))
* test ([d9a0dc6](https://github.com/leotonezi/sonic-library/commit/d9a0dc64fb809f7701f0830bed43fc61a6ae7364))
* test ([b2155e6](https://github.com/leotonezi/sonic-library/commit/b2155e6aad274dd5b1995023a22ffaf921d67f10))
* test ([661d4bb](https://github.com/leotonezi/sonic-library/commit/661d4bb5f2b91a030484e66fcdec0ee0374c908d))
* test ([e8fbae3](https://github.com/leotonezi/sonic-library/commit/e8fbae38534a165933e21e75c8dd9fbdce9c587d))

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

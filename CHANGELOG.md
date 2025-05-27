# [0.4.0](https://github.com/leotonezi/sonic-library/compare/v0.3.0...v0.4.0) (2025-05-27)


### Bug Fixes

* migrations ([02582b8](https://github.com/leotonezi/sonic-library/commit/02582b840ffaee5622ccc115488ba2e372b8672c))
* pytest ([43f0348](https://github.com/leotonezi/sonic-library/commit/43f0348d9b23c1d433b846f8d66cdc2581e09a6a))
* pytest ([81ea06c](https://github.com/leotonezi/sonic-library/commit/81ea06c79d07bdae46d8f013886dcfef98f3c45b))


### Features

* add book creation to user-book logic ([009bc81](https://github.com/leotonezi/sonic-library/commit/009bc814d549dda6d1626c0d7498e747b66ef520))
* add more logic in user book relations ([2e369fc](https://github.com/leotonezi/sonic-library/commit/2e369fc466087c36c565c7f3a278747da43b41a2))
* add my library page ([f0dff2f](https://github.com/leotonezi/sonic-library/commit/f0dff2f5a30407ab5c0fa94ab1396abaa985c8e3))
* improve books/[id] page ([08804c8](https://github.com/leotonezi/sonic-library/commit/08804c8fbfb197c2bbefbd8b6fcc12bc9f289f8a))
* improve user-actions ([4b4e9bd](https://github.com/leotonezi/sonic-library/commit/4b4e9bd1cf71270f4aeea617c8993c84dfd6e7ab))
* improvements on books model ([e1f1070](https://github.com/leotonezi/sonic-library/commit/e1f107051cb8446ac95aaa55497fb2cc2ebdcee4))
* lots of changes ([589ff41](https://github.com/leotonezi/sonic-library/commit/589ff4113e131ce276f025126b1c0de11184db2c))

# [0.3.0](https://github.com/leotonezi/sonic-library/compare/v0.2.0...v0.3.0) (2025-05-03)


### Features

* add logging structure ([49ee954](https://github.com/leotonezi/sonic-library/commit/49ee954384dc6c6ea725a582c7d60f064a68eecc))
* add user profile page ([64fc0c8](https://github.com/leotonezi/sonic-library/commit/64fc0c8bae0a182f967d2ee570f030d052901737))

# [0.2.0](https://github.com/leotonezi/sonic-library/compare/v0.1.2...v0.2.0) (2025-04-28)


### Bug Fixes

* Authentication expiring ([b1da300](https://github.com/leotonezi/sonic-library/commit/b1da3004b52f3bc4134184d03e9c150fb1136de1))


### Features

* add signup page & auth logic ([d0b828e](https://github.com/leotonezi/sonic-library/commit/d0b828ea058248e1a8d4dd180d591ed499e97278))

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

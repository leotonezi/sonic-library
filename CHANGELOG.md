# [0.6.0](https://github.com/leotonezi/sonic-library/compare/v0.5.0...v0.6.0) (2025-07-18)


### Features

* add pagination && cursor configs ([b17a6ff](https://github.com/leotonezi/sonic-library/commit/b17a6ff51d3599fcd648ac85bbcc36e80735cc23))
* fix act ([4dfa0d9](https://github.com/leotonezi/sonic-library/commit/4dfa0d93a266703121c7a3680811ca1ff120bc58))
* improvement on recommendation service ([a22b8e7](https://github.com/leotonezi/sonic-library/commit/a22b8e737abf3b37927e2c3ac624e27f80d00165))

# [0.5.0](https://github.com/leotonezi/sonic-library/compare/v0.4.0...v0.5.0) (2025-07-06)


### Bug Fixes

* alembic env.py to use DATABASE_URL environment variable ([e9ba7b7](https://github.com/leotonezi/sonic-library/commit/e9ba7b7643d6314eb28454965dc177a60ba1e02b))
* auth redirect ([ab364d6](https://github.com/leotonezi/sonic-library/commit/ab364d617e769d3771657113b68626cbbb15b5d7))
* change release ci reference ([7a935bb](https://github.com/leotonezi/sonic-library/commit/7a935bb68f337f377f9532400c1baf813de6e9f6))
* change release ci reference ([80b9e96](https://github.com/leotonezi/sonic-library/commit/80b9e9682b7dd91d09dff264de7ec6120a36f862))
* gh actions ([0c42488](https://github.com/leotonezi/sonic-library/commit/0c4248840630753ad76d8251e9abc8e110883d3f))
* gh actions ([80aaaa1](https://github.com/leotonezi/sonic-library/commit/80aaaa14d9198c6202daccc38d8da173673b18e0))
* linting fixes on test_multi_user_interactions ([03a0cec](https://github.com/leotonezi/sonic-library/commit/03a0cecbd25dab1d4fd60ba618cee8763142558c))
* remove user caching to avoid SQLAlchemy session issues ([2f101cc](https://github.com/leotonezi/sonic-library/commit/2f101cc4a9cfeef3d1cf301d328e6548f38be8aa))
* resolve CI test database issues and environment variable conflicts ([fcbf3d0](https://github.com/leotonezi/sonic-library/commit/fcbf3d0d7eb5a1d0664c969ffb7695f78efbfcf8))
* set DATABASE_URL inline with alembic command ([702e244](https://github.com/leotonezi/sonic-library/commit/702e244f6edabe3893a6297dc02d42d15b6ba280))
* use alembic -x flag to pass database URL directly ([2e4617c](https://github.com/leotonezi/sonic-library/commit/2e4617cce1895a5f2f2ad03ed98d5a35d782e0ea))
* userBook state management ([7402b46](https://github.com/leotonezi/sonic-library/commit/7402b46447c06a917be5ce75af28ac8c1a01f83c))
* workflow and review fixes ([023d1fd](https://github.com/leotonezi/sonic-library/commit/023d1fd9ad9361d5a403ee10cedba07052eb973a))


### Features

* add book change status on my library ([9176381](https://github.com/leotonezi/sonic-library/commit/9176381e8e62dc883fa4c4664ce1ff8b5197582b))
* add filters to my library ([2a6364b](https://github.com/leotonezi/sonic-library/commit/2a6364bf99bed405a5a5f5722ff1a5bed19c6ed2))
* add link into book titles on my library ([1ac1f71](https://github.com/leotonezi/sonic-library/commit/1ac1f71fe2128c8c12db494ae6bab5663178c9d9))
* add mult user-review tests ([9a92b2d](https://github.com/leotonezi/sonic-library/commit/9a92b2d356153b7604dc0658c57ec475ff3c7057))
* add review structure on external book ([94af87e](https://github.com/leotonezi/sonic-library/commit/94af87e384edbb0d712a9a10b512de5b87b88a24))
* add user picture ([2c97d74](https://github.com/leotonezi/sonic-library/commit/2c97d74855331908e72cb4f85aea235385d0904e))
* add user picture ([69c3f56](https://github.com/leotonezi/sonic-library/commit/69c3f56f82ba1ca7713759169595b18d620758cb))
* improve pipeline ([20e70aa](https://github.com/leotonezi/sonic-library/commit/20e70aa221ae41d6b7cf22eab6dbc9e940a6d426))
* improve searchBar and genre ([de56146](https://github.com/leotonezi/sonic-library/commit/de561468a8cbf68c84543e6609d72d89a3871c17))
* refactor search books logic ([cf7f375](https://github.com/leotonezi/sonic-library/commit/cf7f375376b635eba2f257f0d3009f9fb399b6e1))
* remove unuseful nav options ([40e3bc0](https://github.com/leotonezi/sonic-library/commit/40e3bc0382b37381261be71188e7958b75c864c8))

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

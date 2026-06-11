# [0.7.0](https://github.com/leotonezi/sonic-library/compare/v0.6.0...v0.7.0) (2026-06-11)


### Bug Fixes

* add BACKEND_INTERNAL_URL to frontend-test service in docker-compose.test.yml ([46947b4](https://github.com/leotonezi/sonic-library/commit/46947b4e5d792ba707119ce302cd98ef9facda3c))
* add validation to google api ([f5613ee](https://github.com/leotonezi/sonic-library/commit/f5613eed3ad2ca8ab77a456e9f2c17b1869b7bde))
* **backend:** resolve 307 redirect on POST /reviews via Next.js proxy ([b1c4ea2](https://github.com/leotonezi/sonic-library/commit/b1c4ea2f6e30e4ee7297647b65b58894cb1fc927))
* centralize auth hydration in root layout, eliminate duplicate /users/me calls ([474e85a](https://github.com/leotonezi/sonic-library/commit/474e85a3e6d1d2b2cf1411d9c08a48b4df911625)), closes [#136](https://github.com/leotonezi/sonic-library/issues/136)
* change release ci reference ([93cccd1](https://github.com/leotonezi/sonic-library/commit/93cccd1b7b05ed7e4be3e37074b14294f2cd3662))
* change release ci reference ([12c3fed](https://github.com/leotonezi/sonic-library/commit/12c3fedd2abe2b44e7cf39de760a06e026d522dd))
* ci tests ([4787609](https://github.com/leotonezi/sonic-library/commit/478760998099057f1b5fad3e6f289e54b997143a))
* component ([fb90b62](https://github.com/leotonezi/sonic-library/commit/fb90b62c2c4946cd368c854a649b393220d14c3b))
* **e2e:** bypass Google Books in TESTING mode for stable e2e runs ([7da6b1c](https://github.com/leotonezi/sonic-library/commit/7da6b1c8e10e9ae6899ce3a3fb3e25a17d56c5a5))
* **e2e:** hydrate auth store on protected pages, fix duplicate email response ([edddc2f](https://github.com/leotonezi/sonic-library/commit/edddc2f5ecfc929ad989ecd0e281a6aed9dc662f))
* **e2e:** replace fragile waitForResponse(201) with toast assertion ([499ee76](https://github.com/leotonezi/sonic-library/commit/499ee76ca755d9895020315a898c7058544de696))
* **e2e:** skip flaky add-book spec pending root cause analysis ([aad10b2](https://github.com/leotonezi/sonic-library/commit/aad10b2c3ef4f2ff8ae6b11962f685619de4a415)), closes [#166](https://github.com/leotonezi/sonic-library/issues/166)
* **e2e:** switch testMatch to glob patterns, add testIgnore for fixtures ([4d18407](https://github.com/leotonezi/sonic-library/commit/4d18407ca264eb59b025b3996740871c6d7a4e8e))
* **e2e:** wait for popular books API response before asserting DOM ([84c5083](https://github.com/leotonezi/sonic-library/commit/84c5083ecdcae2e445c8f8ff93ec7411d96f5c2b))
* **frontend:** eliminate N+1 double-fetch on recommendations endpoint (closes [#140](https://github.com/leotonezi/sonic-library/issues/140)) ([c3d47cb](https://github.com/leotonezi/sonic-library/commit/c3d47cbd0dc0cbbf99445e6c961c08b67fb191bc))
* **frontend:** move NavBar to protected layout and add auth guards on library page (closes [#171](https://github.com/leotonezi/sonic-library/issues/171), [#172](https://github.com/leotonezi/sonic-library/issues/172)) ([d7e291f](https://github.com/leotonezi/sonic-library/commit/d7e291f38269f6602813cd4e3e78b2baa4f633c7)), closes [#143](https://github.com/leotonezi/sonic-library/issues/143)
* **frontend:** replace <a> tags with Next.js <Link> in library status filter tabs (closes [#151](https://github.com/leotonezi/sonic-library/issues/151)) ([8acb339](https://github.com/leotonezi/sonic-library/commit/8acb339900659e1db3103c99023653c0d10c506b))
* **frontend:** use getBackendUrl() in external book and library server components ([861ed31](https://github.com/leotonezi/sonic-library/commit/861ed3167e373d4ebcac9e7aa6eb0dc8f0d1aa13)), closes [#148](https://github.com/leotonezi/sonic-library/issues/148)
* github test ([7365035](https://github.com/leotonezi/sonic-library/commit/73650354d7621e16d466fb5a42fa39aa7bd99fca))
* github test2 ([06b0e09](https://github.com/leotonezi/sonic-library/commit/06b0e095ae28a4cbb199137d3e05505af964319b))
* github tests ([c48f03b](https://github.com/leotonezi/sonic-library/commit/c48f03b6efee1b452a04fbf895ca96cfa78d97b2))
* guard upload dir mkdir against read-only filesystem (Vercel) ([277a2df](https://github.com/leotonezi/sonic-library/commit/277a2df73936c00c34d6244af564c8363514f3a3))
* last features ([b7f7639](https://github.com/leotonezi/sonic-library/commit/b7f763989aae3893af4ef583ecf2468fa0ca863c))
* load .env.test only when TESTING=true, not by file existence ([02550f4](https://github.com/leotonezi/sonic-library/commit/02550f459d8a63fe770a82778674a2cc0d7fc13f))
* merge2 ([0dfee05](https://github.com/leotonezi/sonic-library/commit/0dfee05ee59110ad605eaac34ea70f9f185e01a1))
* pipeline gh actions ([b8b3bca](https://github.com/leotonezi/sonic-library/commit/b8b3bcafd166f901bfa26d6d7afb779b1b4a6605))
* proxy backend through Next.js to avoid Vercel WAF cross-origin block ([b45d4e0](https://github.com/leotonezi/sonic-library/commit/b45d4e0ff67254c2e2b202d33ceb4e4624945aaf))
* remove console.error from external book page, add Suspense E2E test ([0dfcd7b](https://github.com/leotonezi/sonic-library/commit/0dfcd7b691bbc7f6cb05d7b4511ddefb344d39a5))
* remove console.log calls and add no-console ESLint rule ([e8e276d](https://github.com/leotonezi/sonic-library/commit/e8e276dec574d253ca87d83483407cefef372244)), closes [#135](https://github.com/leotonezi/sonic-library/issues/135)
* remove main tags from child components and fix test mail config ([f5d67f8](https://github.com/leotonezi/sonic-library/commit/f5d67f8cc1c1f0897da8294b81c3da2ba3e0ecb4))
* rename merriwether to merriweather in layout.tsx ([30a1447](https://github.com/leotonezi/sonic-library/commit/30a14475e6f5f00ec889d6da8ad8fcc97c8a97d8))
* replace broken token-refresh queue and unsafe force-cache default ([1ef007b](https://github.com/leotonezi/sonic-library/commit/1ef007b95e1242be144e2ee9589a6a723f03d2f5))
* replace unsafe BookRecommendation casts with explicit field construction ([607b80c](https://github.com/leotonezi/sonic-library/commit/607b80c2e5f2f05112768577e1e4e1abba1c127c)), closes [#144](https://github.com/leotonezi/sonic-library/issues/144)
* replace unsafe tab cast with type guard, add invalid tab error state (closes [#145](https://github.com/leotonezi/sonic-library/issues/145)) ([aacbbe5](https://github.com/leotonezi/sonic-library/commit/aacbbe52424e4b107777df05f9f0f60a4131580d))
* resolve book page 401, image loading, add-book 307, and mail crashes ([147fede](https://github.com/leotonezi/sonic-library/commit/147fede0a01cee949b3114e7bab74212bb60c3e4))
* rewrite build-validator to faithfully mirror ci.yml ([8ad67d6](https://github.com/leotonezi/sonic-library/commit/8ad67d66d99be1846d171c61a4467ac7c1aaeb88))
* route all browser API calls through Next.js proxy to bypass Vercel WAF ([5b284a4](https://github.com/leotonezi/sonic-library/commit/5b284a4d3b30e93e549eb6055330f0a9a4ae52bd))
* server-side admin auth via is_admin on /users/me (closes [#134](https://github.com/leotonezi/sonic-library/issues/134)) ([022e996](https://github.com/leotonezi/sonic-library/commit/022e9968ca6c257d24a11aa69504367da079e671))
* skip file log handler when filesystem is read-only (Vercel) ([462b90c](https://github.com/leotonezi/sonic-library/commit/462b90c68e59e8e891834bce34899f5a3928f92a))
* tests ([37c6b71](https://github.com/leotonezi/sonic-library/commit/37c6b71ce64f989c3a1b14b05607f9622e173f7d))
* **types:** extend BookStatus narrowing to admin, pagination, and library page ([7629a36](https://github.com/leotonezi/sonic-library/commit/7629a360cf8ee2f90cb64e7d9d7e5b463a08a7f6))
* **types:** narrow BookStatus from string to union type across frontend ([77f3332](https://github.com/leotonezi/sonic-library/commit/77f333277a3cfab4db6ed34fac9839b7af5d38df)), closes [#143](https://github.com/leotonezi/sonic-library/issues/143)
* use BACKEND_INTERNAL_URL for Next.js proxy rewrite in Docker ([47a3dc2](https://github.com/leotonezi/sonic-library/commit/47a3dc240b7b652465da2eac1cf706bd536256d3))
* wrap useSearchParams in Suspense on admin page ([04a5239](https://github.com/leotonezi/sonic-library/commit/04a523961227602002ac976bb08c38a79886d155))
* wrap useSearchParams in Suspense on settings, login, library pages ([c68411c](https://github.com/leotonezi/sonic-library/commit/c68411cb6ce9972fbaa716b348aa719887b761fa))


### Features

* add build-validator agent for pre-PR CI/Vercel validation ([9d80b99](https://github.com/leotonezi/sonic-library/commit/9d80b9928d74096db1ea4bc82f246f681c9d76af))
* add new e2e test ([4a85629](https://github.com/leotonezi/sonic-library/commit/4a85629ed38a0abdc8bf4d586d9fa735955725fe))
* add playwright instead of cypress (macOS Sequoia support) ([638e34d](https://github.com/leotonezi/sonic-library/commit/638e34d5c1a5bf35e68f2054dae01f0166d89b40))
* add pr-creator sub-agent ([b43fc6a](https://github.com/leotonezi/sonic-library/commit/b43fc6a358d8c5e8922ea2012dd46480ca0cf343))
* add project-specific Claude Code sub-agents ([ff63d49](https://github.com/leotonezi/sonic-library/commit/ff63d49cc73df8b95e3f46b9b91056935711d907))
* add react-flow graph (mock connection data) ([06fbd59](https://github.com/leotonezi/sonic-library/commit/06fbd5934ee049b2cb80cefbf8e87e642856ce7a))
* add structural stuff for ralph loop development ([719da00](https://github.com/leotonezi/sonic-library/commit/719da007a2efcc45d80b37e9e5c9fb291057316e))
* add test info on md file ([80ac3ac](https://github.com/leotonezi/sonic-library/commit/80ac3ac163a4f76960327ab6f1e4b923be9a65e1))
* convert root page to server component redirect ([befec91](https://github.com/leotonezi/sonic-library/commit/befec917f89a1d6aba4049514a953562f7e5fc4b)), closes [#137](https://github.com/leotonezi/sonic-library/issues/137)
* enhancement on claude md files ([88b8242](https://github.com/leotonezi/sonic-library/commit/88b82424e4816546011a24847f57fe598b96de33))
* **frontend:** add error/loading segments and refactor book error handling (closes [#142](https://github.com/leotonezi/sonic-library/issues/142)) ([7f9f5d9](https://github.com/leotonezi/sonic-library/commit/7f9f5d9764865028dd3ba1bb0e5176b6fae7b6fb))
* **frontend:** stream reviews section via Suspense on book detail page ([927dd03](https://github.com/leotonezi/sonic-library/commit/927dd0302a3913ea315f81f9d32142763eaf8389)), closes [#141](https://github.com/leotonezi/sonic-library/issues/141)
* server-side auth gating via Next.js middleware ([#132](https://github.com/leotonezi/sonic-library/issues/132)) ([206a0a6](https://github.com/leotonezi/sonic-library/commit/206a0a60cb3eca3b5ef64f9baf0280901184aa66))
* US-001 - Add Redis service to Docker infrastructure ([86d8759](https://github.com/leotonezi/sonic-library/commit/86d8759a767d3803243492b3b2e25c3e2462ad51))
* US-001 - Admin access control — backend config and dependency ([8cac028](https://github.com/leotonezi/sonic-library/commit/8cac028f2555d8a60989a65b97d8079122787dbd))
* US-001 - Eager load Book.genres in recommendation service ([022e103](https://github.com/leotonezi/sonic-library/commit/022e10349873098c3ca550bd9fe8be6bd0575728))
* US-002 - Admin Pydantic schemas ([a29a923](https://github.com/leotonezi/sonic-library/commit/a29a923e338815e6bdec0c7f7105c81b110f3e55))
* US-002 - Eager load Review.book in review service ([13272ff](https://github.com/leotonezi/sonic-library/commit/13272ff42634696e096be91ea1e92fd55d2046d4))
* US-002 - Implement per-user rate limiter module ([5bbd9ba](https://github.com/leotonezi/sonic-library/commit/5bbd9bae4248bc64dae91a3a7e6f1db86e61d6ed))
* US-003 - Admin API — read endpoints for users ([634957c](https://github.com/leotonezi/sonic-library/commit/634957c1fab55e242137196f5345b6602d472d7b))
* US-003 - Apply per-user rate limiter to search-external endpoint ([2b46067](https://github.com/leotonezi/sonic-library/commit/2b4606792738b552873434387a9bf5677bb7eb79))
* US-003 - Eager load UserBook.book in user book service ([c8c73fd](https://github.com/leotonezi/sonic-library/commit/c8c73fd15ab51bc72435f981db8698d189b4dfd6))
* US-004 - Admin API — read endpoints for reviews, user-books, and stats ([720c0d3](https://github.com/leotonezi/sonic-library/commit/720c0d3055aa51bbb634f7a1745592592409abd4))
* US-004 - Fix N+1 queries in admin list endpoints ([76042a9](https://github.com/leotonezi/sonic-library/commit/76042a9d2e47e70f92878029065f57c7a862fcab))
* US-004 - Implement global rate limiter for recommendation service Google Books calls ([217d661](https://github.com/leotonezi/sonic-library/commit/217d6616161c66fbf21c574ab3056e05b302732e))
* US-005 - Admin API — write endpoints for users ([16893c4](https://github.com/leotonezi/sonic-library/commit/16893c457bec8d412eab747957df3d4a47bfa474))
* US-005 - Fix N+1 queries in admin detail and update endpoints ([4e3680f](https://github.com/leotonezi/sonic-library/commit/4e3680fece34a67c48677075a924041a4f6e35ac))
* US-005 - Implement circuit breaker class ([db0abeb](https://github.com/leotonezi/sonic-library/commit/db0abebe056294e8709cf8e1df0fc935acec1f2c))
* US-006 - Admin API — write endpoints for reviews and user-books ([18cfa26](https://github.com/leotonezi/sonic-library/commit/18cfa263d6aa5e76019074574be4ddd990520e16))
* US-006 - Apply circuit breaker to Google Books API with local fallback ([e88788b](https://github.com/leotonezi/sonic-library/commit/e88788bbc749331eef08b4b8aa960ba5ec1546ac))
* US-006 - Eager load Book.genres in book service edge cases ([bc66b83](https://github.com/leotonezi/sonic-library/commit/bc66b8343343b2ae37c43aa4ef7e4d4aaab7c036))
* US-007 - Add query performance regression tests ([7574b6b](https://github.com/leotonezi/sonic-library/commit/7574b6bb42a04d33bd71b9caa090ffb171c5cd4b))
* US-007 - Apply circuit breaker to OpenAI API with fallback message ([98494a5](https://github.com/leotonezi/sonic-library/commit/98494a57e7478c8c43300765f50b39d6e445a758))
* US-007 - Backend tests — admin auth and read endpoints ([0e08776](https://github.com/leotonezi/sonic-library/commit/0e0877642f04ccbbc8ad3323eb04df89a0cc55ee))
* US-008 - Backend tests — admin write endpoints ([51411ea](https://github.com/leotonezi/sonic-library/commit/51411ea1971f9a1a332d1e10085590ce6d182d31))
* US-008 - Frontend 429 rate limit toast notification ([6a6cf8e](https://github.com/leotonezi/sonic-library/commit/6a6cf8edfff187642bac7f0dafd723e69a87301c))
* US-009 - Frontend admin types and service ([9ab9ac7](https://github.com/leotonezi/sonic-library/commit/9ab9ac7a266549c53d7c8a6baf312348132b7e30))
* US-009 - Frontend degraded mode notices for search and recommendations ([610c3ac](https://github.com/leotonezi/sonic-library/commit/610c3ac1eb3ccdb3ac63dd559667823b2976f7c8))
* US-010 - Stats cards component ([3988078](https://github.com/leotonezi/sonic-library/commit/3988078ca8732ea070e2837e597d5e5aa54363eb))
* US-011 - Users table — basic table with search and pagination ([d18ce6e](https://github.com/leotonezi/sonic-library/commit/d18ce6e5861989db5e9b3cf0d925dc497c4f6ff1))


### Performance Improvements

* **e2e:** reduce CI test time with shared auth state and parallel workers ([f6d4f28](https://github.com/leotonezi/sonic-library/commit/f6d4f2893d2af3ac8fdc1dad5510f6939ce10158))

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

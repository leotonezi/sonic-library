# Frontend — Next.js

## Commands

```bash
npm install          # Install dependencies
npm run dev          # Development server (port 3000)
npm run build        # Production build
npm run lint         # Linting

# E2E tests
npm run cypress:open       # Interactive
npm run cypress:run        # Headless
npm run cypress:open:test  # Against test environment
```

## Tech Stack

- Next.js 15 (App Router)
- React 19
- Zustand 5 (state management)
- Tailwind CSS 4
- Cypress 15 (E2E testing)
- `@xyflow/react` (recommendation graph)

## Project Structure

```
frontend/
├── src/
│   ├── app/            # App Router pages
│   │   ├── (public)/   # Login, signup (no auth)
│   │   └── (protected)/ # Auth-required pages
│   ├── components/     # React components
│   ├── store/          # Zustand stores
│   ├── services/       # API communication
│   ├── lib/            # Utilities (api-client)
│   ├── types/          # TypeScript interfaces
│   ├── hooks/          # Custom React hooks
│   └── config.ts       # App configuration
└── cypress/            # E2E tests
    ├── e2e/            # Test specs
    ├── fixtures/       # Test data
    └── support/        # Custom commands
```

## Adding a New Page

1. Create page in `src/app/(protected)/` or `(public)/`
2. Add types in `src/types/`
3. Create API service in `src/services/`
4. Add Zustand store if needed in `src/store/`
5. Create components in `src/components/`

## Testing

- Test env uses `docker-compose.test.yml` (ports 3001/8001/5433)
- Fixtures in `cypress/fixtures/`
- Custom commands in `cypress/support/commands.ts`

## Troubleshooting

- **Build errors**: `rm -rf node_modules .next && npm install`
- **Auth issues**: Check cookies (HTTP-only, same-site), verify `FRONTEND_URL`

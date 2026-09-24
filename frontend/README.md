# SecureOps frontend

React and TypeScript operations console. The backend enforces all permissions; the UI provides Viewer read access, Engineer create/update controls, and Admin deletion/audit access.

```sh
npm ci
npm run dev
npm test
npm run lint
npm run build
```

The development proxy forwards `/api` and `/health` to `http://127.0.0.1:8000`. The default production configuration uses same-origin requests through Nginx. Copy `.env.example` only if a custom API origin is needed; Vite variables are public build-time configuration and must never contain secrets. If using a different production API origin, update Nginx `connect-src` and backend CORS accordingly.

The production image uses a Node build stage and unprivileged Nginx on port 8080. It resolves the backend by the Docker network name `backend:8000`, serves React routes through an SPA fallback, and exposes `/health` as the frontend probe. `/health/live` and `/health/ready` are proxied to the backend. TLS, HSTS, and authentication rate limits belong to the outer ingress.

Access tokens are held in memory; rotating refresh tokens are stored in browser local storage. Session restore and authenticated requests share a single in-flight token rotation, including React StrictMode initialization. Logout clears local credentials immediately and attempts server-side revocation. Browser tokens remain exposed to scripts on the origin; deployment must retain the restrictive CSP and avoid third-party scripts. Cross-tab simultaneous refresh is not coordinated; a rejected rotation requires signing in again.

Resource tables are paginated. Dashboard totals exhaust API pages, and active incidents include both open and investigating records. The Services page derives last deployment time from recorded deployments. Health status is the recorded service status, not a browser-issued health probe.

Tests cover token rotation/revocation, validation messages, route permissions, project edit payloads, registration, service visibility, and dashboard totals across API pages. Container verification should additionally exercise `/`, a nested SPA route, backend proxying, health checks, and non-root execution.

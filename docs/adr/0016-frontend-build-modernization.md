# Frontend Build Modernization with Vite

* Status: accepted
* Date: 2025-10-11

## Context and Problem Statement

The frontend previously relied on Create React App (CRA) and `react-scripts` for development and build tooling. CRA introduced a large dependency tree, frequent security advisories (notably via `webpack-dev-server` and `svgo`), and outdated TypeScript/Jest defaults that conflicted with our React 19 upgrade. We need a lighter-weight, actively maintained toolchain that reduces the dependency surface, resolves npm audit failures, and aligns with our Vitest testing stack.

## Decision Drivers

* Reduce the number of transitive dependencies and associated security alerts
* Provide faster local development with modern tooling (hot module replacement, incremental builds)
* Maintain compatibility with existing frontend code and testing approach
* Support modern TypeScript (>=5.9) and React 19 without manual overrides
* Keep configuration simple to limit maintenance overhead

## Considered Options

### Option 1: Continue using Create React App
- Pros:
  - No immediate migration effort
  - Familiar scripts already documented
- Cons:
  - Locked to outdated Webpack pipeline with known vulnerabilities
  - Slow rebuild times and limited configuration flexibility
  - React 19 support requires manual patches and additional polyfills

### Option 2: Migrate to Vite for development/build tooling (Chosen)
- Pros:
  - Minimal configuration with React support via official plugin
  - Significantly smaller dependency tree and faster hot reloads
  - Native compatibility with Vitest, enabling shared configuration
  - Built-in support for modern TypeScript and ES modules
- Cons:
  - Requires updating scripts, documentation, and environment variable handling
  - Necessitates retraining contributors familiar with CRA commands

### Option 3: Adopt Next.js or Remix
- Pros:
  - Batteries-included routing, SSR, and data fetching patterns
  - Strong community adoption
- Cons:
  - Introduces opinionated routing and SSR we do not need
  - Larger migration effort with higher ongoing maintenance cost
  - Adds complexity to a frontend that primarily surfaces backend-driven data

## Decision Outcome

Chosen option: **Option 2: Migrate to Vite for development/build tooling**

We replaced `react-scripts` with Vite and `@vitejs/plugin-react`, updated TypeScript to 5.9, and aligned Vitest configuration with the Vite entrypoint. The migration retains React 19 while reducing npm audit issues and overall dependency count.

## Consequences

### Positive
* npm audit warnings from CRA dependencies are resolved, shrinking the attack surface
* Faster local development cycle with instant hot module replacement
* Simplified TypeScript configuration that matches our Vitest workflow
* Clearer separation between runtime dependencies and dev-only tooling

### Negative
* Contributors must adopt new Vite-based commands (`npm run dev`, `npm run preview`)
* CI/CD scripts and infrastructure variables need validation to ensure they pass `VITE_API_URL`
* Additional documentation maintenance is required to reflect the new toolchain

### Risks and Mitigations
* **Risk:** Legacy deployments still exporting `REACT_APP_API_URL` may break.
  * **Mitigation:** Environment helpers continue to read both `VITE_API_URL` and the legacy variable, preserving compatibility.
* **Risk:** Unfamiliarity with Vite may slow down onboarding.
  * **Mitigation:** Updated README and ADR provide guidance; scripts retain `npm start` alias.
* **Risk:** Potential configuration drift between Vite and Vitest.
  * **Mitigation:** Centralize configuration inside `vite.config.ts` so build and test share the same settings.

## Links

* Related ADRs:
  * [0004-react-typescript-frontend.md](0004-react-typescript-frontend.md)
  * [0011-openapi-client-generation.md](0011-openapi-client-generation.md)
* References:
  * [Vite Documentation](https://vitejs.dev/)
  * [Vitest Documentation](https://vitest.dev/)

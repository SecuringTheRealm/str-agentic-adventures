---
applyTo: "**/*.ts,**/*.tsx"
---

# Project coding standards for TypeScript and React

Apply the [general coding guidelines](./general-coding.instructions.md) to all code.

## TypeScript Guidelines

- Use TypeScript for all new code
- Follow functional programming principles where possible
- Use interfaces for data structures and type definitions
- Prefer immutable data (const, readonly)
- Use optional chaining (?.) and nullish coalescing (??) operators

## React Guidelines

- Use functional components with hooks
- Follow the React hooks rules (no conditional hooks)
- Use React.FC type for components with children
- Keep components small and focused
- Use CSS modules for component styling
- Develop reusable components when possible

## Test-Coverage Guidelines

### Tools

- Use **Vitest** for unit tests
- Use **@testing-library/react** for component tests
- Use **Playwright** for browser end-to-end tests

### Coverage Policy

| Metric     | Minimum – new code | Minimum – overall |
| ---------- | ------------------ | ----------------- |
| Statements | 90 %               | 85 %              |
| Branches   | 90 %               | 85 %              |
| Functions  | 90 %               | 85 %              |
| Lines      | 90 %               | 85 %              |

- Enforce these thresholds in `vitest.config.ts`; CI must fail when unmet
- Reject merges that reduce overall coverage

### Test-Writing Rules

- Unit/component tests: put files in `__tests__/` or end with `.test.ts[x]`
- Playwright specs: place in `e2e/` and end with `.spec.ts`
- Prefer behavioural assertions; avoid snapshots unless output is static
- Mock external services and side-effects, not the unit under test
- Use **msw** for HTTP mocks in unit/component tests
- Do not commit `.only`, `.skip`, or focussed tests
- Keep tests deterministic; avoid real time, randomness, and live network calls

### Reporting

- Generate coverage in both `lcov` and `html` formats
- Upload the `lcov` report to the coverage service
- Exclude `coverage/` artefacts via `.gitignore`

## Linting and Formatting

- Use Biome for linting and formatting
- Ensure all linting and formatting rules pass before submitting code

## UI Theming Guidelines

### General Practices

- Use CSS variables for consistent and flexible theming across all components.
- Ensure responsiveness across all UI components to support various screen sizes and devices.

### Colour Usage in UI Components

- **Titles & Headlines**:

  - highlight titles, section headers, and primary call-to-action buttons.
  - Maintain consistent usage for visual hierarchy.

- **Backgrounds & Containers**:

  - Employ lighter shades of gray for backgrounds to provide clean, neutral spaces that enhance readability and contrast.
  - Utilize medium to dark shades of gray for subtle delineations, borders, or UI separators.

- **Interactive & Highlight Elements**:
  - Buttons, links, and interactive highlights should consistently use the same color to reinforce brand identity and clearly indicate actionable items.

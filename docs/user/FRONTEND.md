# Frontend Development Guide

For detailed frontend documentation, see [docs/user/FRONTEND.md](../docs/user/FRONTEND.md).

## Quick Start

```bash
cd frontend
npm ci --legacy-peer-deps
npm run dev
```

## Key Features

- Real-time chat with AI Dungeon Master
- D&D 5e character creation and management
- Campaign creation and management
- WebSocket support for multiplayer
- Dice rolling (backend-calculated)

## Tech Stack

- React 19 with TypeScript
- Vite for development and build
- CSS Modules for styling
- Axios for API calls
- Vitest for testing
- Playwright for E2E tests


## Features

- **Real-time Chat Interface**: Interactive messaging with the AI Dungeon Master
- **Character Sheet Management**: Complete D&D 5e character creation and display
- **Campaign Creation**: Tools for setting up new gaming campaigns
- **Dice Rolling Interface**: Visual dice rolling system (TODO: needs implementation)
- **Battle Map Display**: Visual representation of combat encounters
- **Image Gallery**: Display of AI-generated character portraits and scene artwork

## Architecture

- **React 19** with TypeScript for type safety
- **Vite** for development server and build tooling
- **CSS Modules** for component styling
- **REST API Integration** with Python backend
- **WebSocket Support** for real-time multiplayer communication

## Available Scripts

In the project directory, you can run:

### `npm run dev`

Runs the app in development mode using Vite.\
Open [http://127.0.0.1:5173](http://127.0.0.1:5173) to view it in the browser.

The page supports instant hot module replacement when you make edits.\
You will also see any lint errors in the console.

### `npm start`

Alias for `npm run dev` to ease the transition from previous Create React App tooling.

### `npm test`

Launches the unit test runner in interactive watch mode using Vitest.
See the section about [running tests](https://facebook.github.io/create-react-app/docs/running-tests) for more information.

### `npm run test:run`

Runs unit tests once without watch mode.

### `npm run test:e2e`

Runs end-to-end tests using Playwright. Tests the complete user journey including:
- Campaign creation flow
- Character creation and selection
- Game session interaction
- D&D 5e SRD compliance validation

### `npm run test:e2e:ui`

Runs E2E tests with interactive UI mode for debugging.

### `npm run test:e2e:debug`

Runs E2E tests in debug mode with browser visible.

### `npm run build`

Runs TypeScript type-checking followed by a production build powered by Vite.\
The optimized assets are emitted to the `dist` directory with hashed filenames.

### `npm run preview`

Serves the built assets locally to validate production output.

## Testing

### Unit Tests
- Uses **Vitest** for fast unit testing
- Component testing with React Testing Library
- Located in `src/**/*.test.tsx` files

### End-to-End Tests
- Uses **Playwright** for comprehensive E2E testing
- Tests located in `e2e/` directory
- Validates complete user workflows and D&D 5e compliance
- Automatic screenshot capture for documentation
- See [E2E Test Documentation](./e2e/README.md) for details

### Test Coverage
E2E tests validate key user stories from the Product Requirements Document:
1. Campaign creation with D&D settings
2. Character creation following D&D 5e SRD rules
3. AI Dungeon Master interaction
4. Dice rolling and skill checks
5. Combat encounters
6. Character progression and leveling

### TODO Items
- **Spell Management UI**: Add spell slot tracking, prepared spells, and casting interface for spellcasters
- **Advanced Inventory System**: Equipment slot management, magical item effects, weight/encumbrance tracking
- **Enhanced Character Sheet**: Spell save DC display, spell attack bonus, concentration tracking
- **Player Management Controls**: DM interface for managing multi-player sessions and player access
- **NPC Interaction Interface**: Advanced NPC personality display and interaction history
- **Combat Enhancement UI**: Spell effect visualization, area of effect displays, status effect tracking
- Complete dice rolling visualization system
- Add character progression UI components
- Implement campaign sharing interface
- Add accessibility features and keyboard navigation

### Backend Integration
The frontend expects the backend to be running on `http://localhost:8000` for local development. API endpoints are defined in `src/services/api.ts`.

## Related Documentation
- [Backend README](../backend/README.md)
- [Deployment Guide](../docs/deployment.md)

## Legacy Notes

The frontend previously used Create React App. The tooling has been modernized to use Vite for a smaller dependency footprint and faster builds. `REACT_APP_*` environment variables are still read for backwards compatibility, but new deployments should prefer the Vite-compatible `VITE_API_URL` variable.

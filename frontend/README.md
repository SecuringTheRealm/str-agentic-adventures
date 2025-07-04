# STR Agentic Adventures - Frontend

This is the React TypeScript frontend for the AI Dungeon Master application. It provides a modern, responsive user interface for interacting with the multi-agent AI system.

## Features

- **Real-time Chat Interface**: Interactive messaging with the AI Dungeon Master
- **Character Sheet Management**: Complete D&D 5e character creation and display
- **Campaign Creation**: Tools for setting up new gaming campaigns
- **Dice Rolling Interface**: Visual dice rolling system (TODO: needs implementation)
- **Battle Map Display**: Visual representation of combat encounters
- **Image Gallery**: Display of AI-generated character portraits and scene artwork

## Architecture

- **React 18** with TypeScript for type safety
- **CSS Modules** for component styling
- **REST API Integration** with Python backend
- **WebSocket Support** for real-time multiplayer communication

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

The page will reload if you make edits.\
You will also see any lint errors in the console.

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

Builds the app for production to the `build` folder.\
It correctly bundles React in production mode and optimizes the build for the best performance.

The build is minified and the filenames include the hashes.\
Your app is ready to be deployed!

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
- [Project Status Report](../docs/project_status_report.md)
- [Deployment Guide](../docs/deployment.md)

## Legacy Notes

This project was originally bootstrapped with [Create React App](https://github.com/facebook/create-react-app). The `npm run eject` command is available but not recommended unless you need advanced configuration customization.

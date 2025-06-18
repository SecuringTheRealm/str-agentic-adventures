# OpenAPI Client Generation for Frontend-Backend Integration

* Status: accepted
* Date: 2025-01-29

## Context and Problem Statement

The frontend application was manually implementing API calls to the FastAPI backend using fetch and duplicating type definitions in `frontend/src/services/api.ts`. This created several maintenance challenges:

1. **Type Duplication**: Frontend manually defined ~300 lines of TypeScript interfaces that duplicated backend Pydantic models
2. **Manual Synchronization**: When backend API changed, developers had to manually update frontend types and API calls
3. **Inconsistency Risk**: Manual updates could introduce discrepancies between frontend expectations and backend reality
4. **Maintenance Overhead**: Every API change required coordinated updates in both frontend and backend codebases

The FastAPI backend already generates OpenAPI schema automatically, but this was not being leveraged for frontend development.

## Decision Drivers

* **Single Source of Truth**: Eliminate duplication between frontend and backend type definitions
* **Automatic Synchronization**: Frontend should automatically reflect backend API changes
* **Type Safety**: Maintain strong TypeScript typing for all API interactions
* **Developer Productivity**: Reduce manual work required for API changes
* **Reliability**: Prevent frontend-backend type mismatches at runtime
* **Maintainability**: Simplify codebase maintenance for API-related changes

## Considered Options

* **Option 1: Continue Manual API Implementation**
    * Keep manually written fetch calls and type definitions in `frontend/src/services/api.ts`
    * Pros: 
      * Full control over API interface
      * No additional build dependencies
      * Familiar development pattern
    * Cons: 
      * High maintenance overhead
      * Risk of frontend-backend inconsistencies
      * Duplicated type definitions
      * Manual synchronization required

* **Option 2: Generate TypeScript Client from OpenAPI Schema**
    * Use `@openapitools/openapi-generator-cli` to generate complete TypeScript client from FastAPI OpenAPI schema
    * Pros: 
      * Single source of truth from backend schema
      * Automatic type synchronization
      * Generated documentation
      * Industry standard approach
      * Zero type duplication
    * Cons: 
      * Additional build dependency
      * Generated code may be less readable
      * Requires build step for API updates

* **Option 3: Use Alternative Code Generation Tools**
    * Consider tools like `swagger-codegen`, `openapi-typescript`, or custom scripts
    * Pros: 
      * Similar benefits to Option 2
      * Different toolchain options
    * Cons: 
      * Need to evaluate and compare tools
      * May have different trade-offs in generated code quality
      * Less standardized approach

## Decision Outcome

Chosen option: "Generate TypeScript Client from OpenAPI Schema"

Justification:
* **Eliminates Type Duplication**: Reduces frontend codebase by ~300 lines of manual type definitions
* **Automatic Synchronization**: `npm run generate:api` command updates frontend when backend changes
* **Industry Standard**: OpenAPI client generation is a well-established pattern
* **Type Safety**: Generated client provides complete TypeScript typing with validation
* **Documentation**: Auto-generated API documentation in `src/api-client/docs/`
* **FastAPI Integration**: Leverages FastAPI's built-in OpenAPI schema generation
* **Proven Tooling**: `@openapitools/openapi-generator-cli` is mature and widely used

## Consequences

### Positive
* **Zero Type Duplication**: Single source of truth from backend Pydantic models
* **Automatic Updates**: Frontend types automatically sync with backend API changes
* **Stronger Type Safety**: All API calls strongly typed with proper validation
* **Reduced Maintenance**: No manual updates required for API changes
* **Generated Documentation**: Complete API documentation automatically maintained
* **Build-time Validation**: API mismatches caught during frontend build process
* **Improved Developer Experience**: IDE autocomplete and type checking for all API calls

### Negative
* **Build Dependency**: Adds `@openapitools/openapi-generator-cli` as development dependency
* **Generated Code Complexity**: Generated client (~5000+ lines) less readable than manual implementation
* **Build Step Required**: API changes require running `npm run generate:api` command
* **Less Control**: Cannot customize generated API interface without modifying generation process
* **Tool Dependency**: Reliant on OpenAPI generator tool maintenance and updates

### Risks and Mitigations
* **Risk**: OpenAPI generator tool issues or breaking changes
  * **Mitigation**: Pin tool version in package.json, maintain compatibility layer in `api.ts`
* **Risk**: Generated code incompatibility with existing components
  * **Mitigation**: Preserve original implementation in `api-original.ts`, create adapter layer for backward compatibility
* **Risk**: Backend OpenAPI schema changes breaking frontend
  * **Mitigation**: Type checking in build process will catch incompatibilities, allowing gradual migration
* **Risk**: Team unfamiliarity with generated code debugging
  * **Mitigation**: Document usage patterns, maintain wrapper functions for common operations

## Links

* **Related ADRs**: 
  * [0004-react-typescript-frontend.md](0004-react-typescript-frontend.md) - Frontend architecture foundation
* **References**: 
  * [OpenAPI Generator CLI](https://openapi-generator.tech/docs/generators/typescript-fetch/)
  * [FastAPI OpenAPI Documentation](https://fastapi.tiangolo.com/tutorial/metadata/)
  * [Generated Client Documentation](../../frontend/src/api-client/docs/)
* **Implementation**: 
  * Generated client: `frontend/src/api-client/`
  * Usage documentation: `OPENAPI_CLIENT.md`
  * Generation script: `npm run generate:api`
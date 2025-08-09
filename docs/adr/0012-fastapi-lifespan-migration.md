# FastAPI Lifespan Event Handler Migration

* Status: accepted
* Date: 2025-01-09

## Context and Problem Statement

The FastAPI application was using deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators for application lifecycle management. These decorators were deprecated in FastAPI and generate deprecation warnings:

```
DeprecationWarning:
    on_event is deprecated, use lifespan event handlers instead.
    
    Read more about it in the
    [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
```

The application needed to migrate to the modern FastAPI lifespan approach to eliminate deprecation warnings, follow current best practices, and ensure future compatibility when the deprecated handlers are eventually removed.

## Decision Drivers

* **Future Compatibility**: Deprecated `on_event` handlers will be removed in future FastAPI versions
* **Code Quality**: Eliminate deprecation warnings in application logs
* **Best Practices**: Follow current FastAPI recommended patterns for lifecycle management
* **Maintainability**: Use supported, actively maintained API patterns
* **Developer Experience**: Reduce noise from deprecation warnings during development

## Considered Options

* Option 1: Keep using deprecated `on_event` handlers
    * Continue using existing `@app.on_event("startup")` and `@app.on_event("shutdown")` decorators
    * Pros: No code changes required, existing functionality preserved
    * Cons: Generates deprecation warnings, will break when FastAPI removes the feature, doesn't follow best practices

* Option 2: Migrate to FastAPI lifespan context manager
    * Replace deprecated handlers with modern `lifespan` parameter using `@asynccontextmanager`
    * Pros: Eliminates deprecation warnings, follows current best practices, future-proof, cleaner lifecycle management
    * Cons: Requires code restructuring, slight learning curve for team

* Option 3: Use third-party lifecycle management
    * Implement custom lifecycle management using external libraries
    * Pros: Maximum flexibility and control
    * Cons: Adds unnecessary complexity, external dependency, reinvents existing FastAPI functionality

## Decision Outcome

Chosen option: "Migrate to FastAPI lifespan context manager"

Justification:
* Eliminates deprecation warnings immediately
* Follows FastAPI's recommended best practices and modern patterns
* Ensures future compatibility when deprecated handlers are removed
* Provides cleaner, more explicit lifecycle management with startup and shutdown in one place
* Minimal code changes required with identical functionality
* No external dependencies or complex refactoring needed

## Consequences

### Positive
* Deprecation warnings eliminated from application logs
* Application follows current FastAPI best practices
* Future-proof against FastAPI API changes
* Cleaner lifecycle management with startup and shutdown logic co-located
* Better developer experience with no warning noise

### Negative
* Slight code restructuring required (though minimal)
* Team needs to understand the new lifespan pattern for future changes
* Different pattern from older FastAPI tutorials and examples

### Risks and Mitigations
* **Risk**: Team unfamiliarity with lifespan pattern
  * **Mitigation**: Document the change and reference FastAPI documentation
* **Risk**: Regression during migration
  * **Mitigation**: Preserve exact same startup logic, thorough testing

## Links

* Related ADRs: None directly related
* References: 
  * [FastAPI Lifespan Events Documentation](https://fastapi.tiangolo.com/advanced/events/)
  * [Python asynccontextmanager Documentation](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager)
* Superseded by: N/A
---
applyTo: "**/docs/**/*.md,**/*.md"
---

# Documentation Standards and Best Practices

Apply the [general coding guidelines](./general-coding.instructions.md) to all documentation.

## Documentation Organization

### Documentation Structure

- **ALWAYS use proper documentation paths** - Create new documentation in appropriate `docs/` subdirectories
- **NEVER create documentation in repository root** unless it's a standard file (README.md, LICENSE)
- Use the established folder structure:
  - `docs/adr/` - Architecture Decision Records
  - `docs/design/` - Design documents and architectural diagrams
  - `docs/specs/` - Technical specifications and requirements
  - `docs/user/` - User guides and documentation
  - `docs/reference/` - API references and technical references

### Avoid Documentation Duplication

- **ALWAYS check for existing documentation** before creating new files
- Update or append to existing documents instead of creating redundant files
- Link between related documents to maintain coherence
- Consolidate overlapping content into single authoritative sources

## File Naming Conventions

### General Documentation

- Use **snake_case** for general documentation files
- Use descriptive names that clearly indicate content
- Examples: `product_requirements_document.md`, `technical_specifications.md`
- Avoid abbreviations unless they are widely understood

### ADR-Specific Naming

- Follow the pattern: `NNNN-title-with-hyphens.md`
- NNNN must be the next sequential number from the ADR index
- Use lowercase letters and hyphens only in titles
- Keep titles brief but descriptive
- Examples: `0001-semantic-kernel-integration.md`, `0002-react-frontend-architecture.md`

### Specialized Documentation Types

- **API Documentation**: Use format like `api_reference.md` or `endpoint_documentation.md`
- **User Guides**: Use format like `user_guide.md` or `installation_guide.md`  
- **Design Documents**: Use format like `database_design.md` or `authentication_design.md`

## Content Standards

### Writing Guidelines

- **Use US English** for all documentation
- Write in clear, concise language accessible to the intended audience
- Use active voice when possible
- Define technical terms and acronyms on first use
- Include examples and code snippets where helpful

### Document Structure

- Start with a clear title and brief description
- Include a table of contents for longer documents
- Use consistent heading hierarchy (H1 for title, H2 for major sections, etc.)
- End with relevant links or references

### Technical Documentation

- Include version information and last updated dates
- Provide code examples with proper syntax highlighting
- Document prerequisites and dependencies
- Include troubleshooting sections for complex topics

## Markdown Best Practices

### Formatting Standards

- Use **bold** for emphasis and important concepts
- Use *italics* for terms being introduced or light emphasis
- Use `code blocks` for commands, file names, and inline code
- Use triple backticks with language specification for code blocks

### Linking and References

- Use relative links for internal documentation
- Include descriptive link text (not "click here" or bare URLs)
- Link to relevant ADRs, specifications, and related documents
- Maintain working links by checking them periodically

### Lists and Organization

- Use numbered lists for sequential steps or procedures
- Use bullet points for non-sequential items or feature lists
- Keep list items parallel in structure and tense
- Use consistent indentation for nested lists

## Specialized Documentation Types

### Architecture Decision Records (ADRs)

- Follow the established ADR template without modifications
- Include proper context, decision drivers, options considered, and consequences
- Link to related ADRs and update the ADR index
- Never modify accepted ADRs - create new ones to supersede if needed

### API Documentation

- Document all endpoints with examples
- Include request/response formats and status codes
- Provide authentication and error handling information
- Keep API docs synchronized with actual implementation

### User Documentation

- Write from the user's perspective
- Include step-by-step instructions with screenshots when helpful
- Test all documented procedures to ensure accuracy
- Organize by user workflows rather than system features

## Documentation Maintenance

### Keeping Documentation Current

- Update documentation as part of code changes
- Review and update documentation during refactoring
- Remove or archive obsolete documentation
- Maintain cross-references between related documents

### Review and Quality Control

- Review documentation for accuracy and clarity
- Check all links and code examples
- Ensure consistency with project standards
- Get feedback from actual users of the documentation

### Version Control

- Commit documentation changes with descriptive commit messages
- Include documentation updates in pull requests
- Tag documentation versions with major releases
- Maintain change logs for significant documentation updates

## Integration with Development Workflow

### Documentation in Pull Requests

- Include documentation updates in the same PR as code changes
- Update relevant ADRs when making architectural decisions
- Review documentation changes as carefully as code changes
- Ensure new features include appropriate documentation

### Automation and Tools

- Use linting tools for Markdown consistency
- Automate link checking where possible
- Generate API documentation from code when feasible
- Include documentation builds in CI/CD pipeline

### Collaboration

- Use clear commit messages for documentation changes
- Collaborate on documentation reviews
- Share documentation responsibilities across the team
- Create templates for common documentation types
# AI Security Analysis with CodeQL

This document explains the AI-aware security analysis configuration for the STR Agentic Adventures codebase.

## Overview

While CodeQL doesn't yet have dedicated query packs for AI/LLM-specific vulnerabilities like prompt injection, the `security-extended` and `security-and-quality` query suites provide comprehensive coverage for vulnerabilities that are particularly critical in AI agent systems.

## AI-Critical Security Queries

Our CodeQL configuration focuses on the following vulnerability classes that are especially important for AI applications:

### 1. Injection Attacks

**Why it matters for AI**: AI agents often construct commands, queries, or code based on user input, making injection attacks a primary concern.

- **CWE-078 (Command Injection)**: Detects OS command execution with user-controlled data
  - Risk: AI agents executing system commands based on user prompts
  - Example: `subprocess.run(user_input)` without validation

- **CWE-089 (SQL Injection)**: Identifies unsafe database query construction
  - Risk: AI-driven database queries containing user input
  - Example: Dynamic SQL from AI-generated content

- **CWE-094 (Code Injection)**: Finds `eval()` and `exec()` with untrusted input
  - Risk: AI systems evaluating or executing generated code
  - Example: `eval(ai_generated_code)` without sandboxing

- **CWE-079 (XSS)**: Detects unsanitized output in web contexts
  - Risk: AI-generated content displayed in web UIs
  - Example: Rendering AI responses without HTML escaping

- **CWE-117 (Log Injection)**: Identifies unsanitized input in logs
  - Risk: User prompts containing newlines or escape sequences
  - Example: Logging raw user prompts that could poison log analysis

- **CWE-022 (Path Injection)**: Detects file path manipulation
  - Risk: AI agents accessing files based on user input
  - Example: `open(f"data/{user_file}")` without path validation

- **CWE-400 (Regex Injection/ReDoS)**: Finds regex patterns vulnerable to catastrophic backtracking
  - Risk: AI systems validating user input with complex regexes
  - Example: User-controlled regex patterns causing DoS

### 2. Sensitive Data Exposure

**Why it matters for AI**: AI systems handle API keys, user data, and model outputs that may contain sensitive information.

- **CWE-798 (Hardcoded Credentials)**: Detects hardcoded secrets in code
  - Risk: Azure OpenAI API keys, database credentials in source
  - Example: `api_key = "sk-..."`

- **CWE-312/313 (Cleartext Storage)**: Identifies sensitive data stored without encryption
  - Risk: User prompts, AI responses, or credentials in logs/databases
  - Example: Logging full API keys or user conversations

- **CWE-532 (Sensitive Info in Logs)**: Detects logging of sensitive information
  - Risk: API keys, user PII, or system internals in application logs
  - Example: `logger.info(f"API key: {api_key}")`

### 3. Server-Side Request Forgery (SSRF)

**Why it matters for AI**: AI agents frequently make external HTTP requests based on generated content or user input.

- **CWE-918 (SSRF)**: Detects URL construction from user input
  - Risk: AI agents fetching URLs without validation
  - Example: `requests.get(ai_generated_url)` accessing internal services

### 4. Additional AI-Relevant Checks

- **CWE-502 (Deserialization)**: Unsafe loading of pickled objects
  - Risk: Loading AI model checkpoints or agent state from untrusted sources

- **CWE-601 (URL Redirect)**: Open redirect vulnerabilities
  - Risk: AI-generated redirects to malicious sites

- **CWE-730 (Resource Consumption)**: Uncontrolled resource usage
  - Risk: AI workloads consuming excessive CPU/memory/tokens

- **CWE-1236 (CSV Injection)**: Formula injection in spreadsheets
  - Risk: AI-generated CSV content containing formulas

## Current CodeQL Configuration

Our workflow (`.github/workflows/codeql.yml`) is configured to:

1. **Scan both Python and JavaScript/TypeScript**
   - Python: Backend AI agents and Azure OpenAI integration
   - JavaScript/TypeScript: Frontend handling AI responses

2. **Use `security-extended` query suite**
   - Runs 546 queries total (as of CodeQL 2.18.0)
   - Covers 196 CWE categories
   - Includes all queries above plus many more

3. **Use `security-and-quality` query suite**
   - Adds code quality checks that can prevent security issues
   - Detects maintainability issues that could lead to bugs

4. **Python-specific enhancements**
   - Loads `codeql/python-queries` pack
   - Includes async/await-specific checks (our backend uses asyncio)
   - Enhanced taint tracking for data flow analysis

5. **Path-focused scanning**
   - Prioritizes `backend/app/agents/` and `backend/app/plugins/`
   - Scans Azure OpenAI client and agent framework
   - Excludes build artifacts and migrations

## Triggers

- **Push**: Runs on commits to `main` and `develop` branches
- **Pull Request**: Runs on PRs targeting `main` and `develop`
- **Schedule**: Weekly scan every Monday at 6:00 AM UTC

## OWASP Top 10 for LLM Applications

While CodeQL doesn't yet have specific queries for the OWASP LLM Top 10, here's how our configuration addresses them:

| OWASP LLM Risk | CodeQL Coverage | Status |
|----------------|-----------------|--------|
| LLM01: Prompt Injection | Partial (log injection, code injection) | ⚠️ Manual review needed |
| LLM02: Insecure Output Handling | XSS, code injection, command injection | ✅ Covered |
| LLM03: Training Data Poisoning | Not applicable (using Azure OpenAI) | N/A |
| LLM04: Model Denial of Service | Resource consumption checks | ⚠️ Partial |
| LLM05: Supply Chain Vulnerabilities | Dependency scanning (separate tool) | ⚠️ Use Dependabot |
| LLM06: Sensitive Information Disclosure | Hardcoded creds, cleartext storage, logs | ✅ Covered |
| LLM07: Insecure Plugin Design | Code/command injection in plugins | ✅ Covered |
| LLM08: Excessive Agency | Not detectable via static analysis | ❌ Manual review |
| LLM09: Overreliance | Not detectable via static analysis | ❌ Manual review |
| LLM10: Model Theft | Not applicable (using Azure OpenAI) | N/A |

## Limitations and Recommendations

### Current Limitations

1. **No Prompt Injection Detection**: CodeQL doesn't have queries to detect prompt injection vulnerabilities. Consider:
   - Manual code review of agent prompt construction
   - Input validation for all user-provided prompts
   - Using tools like [Rebuff](https://github.com/protectai/rebuff) for runtime detection

2. **No LLM-Specific Data Flow**: CodeQL doesn't understand Azure AI Agents SDK data flows yet. Consider:
   - Manual review of agent tool registration
   - Audit all `create_function_tool()` calls
   - Ensure tool functions validate inputs

3. **No Semantic Analysis of AI Behavior**: Static analysis can't detect:
   - Agent giving excessive permissions
   - AI generating harmful content
   - Model inversion attacks
   - Adversarial inputs

### Recommendations

1. **Complement with Dynamic Analysis**
   - Add runtime monitoring for prompt injection attempts
   - Log and alert on suspicious AI behavior
   - Implement rate limiting on AI API calls

2. **Manual Security Reviews**
   - Review all agent instruction prompts for injection risks
   - Audit tool function implementations for proper validation
   - Check Azure API key rotation and storage practices

3. **Input Validation**
   - Validate all user input before passing to AI agents
   - Sanitize AI outputs before displaying to users
   - Implement allowlists for file paths, URLs, and commands

4. **Monitoring and Logging**
   - Log all AI interactions (sanitized)
   - Monitor for unusual token consumption
   - Alert on repeated API failures or rate limits

5. **Stay Updated**
   - Watch for new CodeQL queries for AI security
   - Monitor OWASP LLM Top 10 updates
   - Review Azure AI Agents SDK security advisories

## Resources

- [OWASP Top 10 for LLM Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [CodeQL Query Help for Python](https://codeql.github.com/codeql-query-help/python/)
- [CodeQL CWE Coverage](https://codeql.github.com/codeql-query-help/codeql-cwe-coverage/)
- [Azure AI Security Best Practices](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/security)
- [Prompt Injection Attacks Explained](https://simonwillison.net/2023/Apr/14/worst-that-can-happen/)

## Contributing

If you discover security vulnerabilities:

1. **Do not** create a public GitHub issue
2. Email security@securingtherealm.com with details
3. Include: vulnerability description, reproduction steps, potential impact
4. We'll acknowledge within 48 hours and work on a fix

For false positives or query improvements:
1. Review the CodeQL alert details
2. If it's a false positive, suppress with `# nosemgrep` or `# noqa`
3. Document why it's safe in a comment
4. Consider contributing improved queries to [github/codeql](https://github.com/github/codeql)

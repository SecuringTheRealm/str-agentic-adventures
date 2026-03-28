# Investigate FLUX.1-Kontext-pro for Character Portrait Consistency

* Status: proposed
* Date: 2026-03-27

## Context and Problem Statement

DALL-E 3 was retired in March 2026 and the project has migrated to gpt-image-1-mini for all image generation (battle maps via `CombatCartographerAgent`, character art via `ArtistAgent`, scene composition via plugins). The current `AzureOpenAIClient.generate_image()` method drives all visual output through a single Azure OpenAI deployment.

Character portrait consistency is an ongoing challenge: each gpt-image-1-mini call generates a new image from scratch with no reference to previous depictions of the same character. Players notice when their character's appearance shifts between sessions.

FLUX.1-Kontext-pro is now available in Azure AI Foundry. Unlike gpt-image-1-mini, it accepts reference images as input, enabling style-consistent outputs that can maintain a character's visual identity across multiple generations.

## Decision Drivers

* Need for visually consistent character portraits across sessions
* Cost efficiency at typical session volumes (2-6 images per session)
* DALL-E 3 retirement means we must evaluate the new generation of image models
* Azure AI Foundry availability simplifies procurement and deployment
* Content safety requirements for a game that includes combat imagery
* API compatibility with the existing `AzureOpenAIClient` abstraction

## Considered Options

* Option 1: gpt-image-1-mini as sole image model (current state)
    * Continue using the existing Azure OpenAI images API for all generation
    * Pros:
      * Already integrated and working (`AzureOpenAIClient.generate_image()`)
      * Low cost (~$0.011/image at medium quality, 1024x1024)
      * Built-in Azure OpenAI content filtering
      * Same API surface for battle maps and character art
      * No additional Azure resource provisioning needed
    * Cons:
      * No reference image support — every generation is independent
      * Character appearance varies between calls
      * Limited style control compared to dedicated image models

* Option 2: FLUX.1-Kontext-pro as supplementary portrait model
    * Deploy FLUX.1-Kontext-pro via Azure AI Foundry for character portraits; keep gpt-image-1-mini for battle maps and scene art
    * Pros:
      * Reference image input enables consistent character depictions
      * High-quality image output suitable for character art
      * Available through Azure AI Foundry (managed deployment)
      * Can store a "reference portrait" per character and pass it with each request
    * Cons:
      * Separate API and SDK — not the OpenAI images endpoint
      * No built-in content filtering; requires Azure AI Content Safety integration
      * Additional Azure resource cost (AI Foundry deployment + per-image pricing)
      * Pricing not yet confirmed at our volume; needs evaluation
      * Adds a second image generation path to maintain

* Option 3: FLUX.1-Kontext-pro as sole image model
    * Replace gpt-image-1-mini entirely with FLUX
    * Pros:
      * Single image model to maintain
      * Reference image capability for all generation types
    * Cons:
      * Battle maps and scene art do not benefit from reference images
      * Higher cost for non-portrait use cases
      * No built-in content safety for any generation
      * Larger migration effort with higher risk

## Decision Outcome

Chosen option: "FLUX.1-Kontext-pro as supplementary portrait model" (Option 2), with gpt-image-1-mini remaining the default.

Justification:
* Character portrait consistency is the primary pain point — battle maps and scene art do not need reference-based generation
* A dual-model approach keeps the existing, proven gpt-image-1-mini path for most generation while adding FLUX only where its reference image capability provides clear value
* Azure AI Foundry deployment means we stay within the Azure ecosystem, consistent with the project's Azure-first strategy (see ADR-0005)
* Cost impact is bounded because portrait generation is a small subset of total image generation (typically 1-2 per session vs 2-6 total)

## Consequences

### Positive
* Characters maintain visual consistency across sessions via stored reference portraits
* Players get a more immersive experience with recognisable character art
* Battle maps and scene art continue at current low cost via gpt-image-1-mini
* Reference portrait workflow can extend to NPCs and recurring villains

### Negative
* Two image generation code paths to maintain in `AzureOpenAIClient` or a new service layer
* Azure AI Content Safety must be integrated separately for FLUX outputs
* Additional Azure resource to provision, monitor, and budget for
* Team needs to learn Azure AI Foundry model deployment patterns

### Risks and Mitigations
* Risk: FLUX pricing at scale exceeds budget
  * Mitigation: Implement per-session image budget (already exists in `test_image_budget.py`); cap FLUX usage to portrait-only generation
* Risk: FLUX content filtering gap leads to inappropriate outputs
  * Mitigation: Route all FLUX outputs through Azure AI Content Safety before returning to the client; block and fall back to gpt-image-1-mini on rejection
* Risk: Azure AI Foundry access approval is delayed
  * Mitigation: gpt-image-1-mini remains fully functional as the default; FLUX is additive, not a dependency
* Risk: Reference image storage increases blob storage costs
  * Mitigation: Store one reference portrait per character (small PNG); negligible at expected player counts

## Next Steps

1. Apply for FLUX.1-Kontext-pro access in Azure AI Foundry
2. Provision a test deployment and run side-by-side quality comparisons (gpt-image-1-mini vs FLUX with reference)
3. Benchmark cost per image at medium and high quality settings
4. Prototype the reference portrait workflow: generate initial portrait with gpt-image-1-mini, store as reference, use FLUX for subsequent portraits
5. Integrate Azure AI Content Safety as a post-generation filter for FLUX outputs
6. Evaluate at session-realistic volumes (2-6 images/session, 1-2 portraits)

## Links

* Related ADRs: [ADR-0005 - Azure OpenAI Integration](0005-azure-openai-integration.md), [ADR-0018 - Azure AI Agents SDK Adoption](0018-azure-ai-agents-sdk-adoption.md)
* References:
  * [Azure AI Foundry Model Catalog](https://ai.azure.com/explore/models)
  * [FLUX.1-Kontext-pro on Azure AI Foundry](https://ai.azure.com/explore/models/FLUX.1-Kontext-pro/version/1/registry/azureml-community)
  * [Azure AI Content Safety](https://learn.microsoft.com/en-us/azure/ai-services/content-safety/)
  * Current image generation: `backend/app/azure_openai_client.py` (`generate_image` method)
  * GitHub issue: #407

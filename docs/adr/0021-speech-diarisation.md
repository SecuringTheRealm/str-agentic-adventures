# Add Speaker Diarisation for Voice-Based Gameplay

* Status: proposed
* Date: 2026-03-27

## Context and Problem Statement

Secure the Realm is a text-input D&D game where players type actions and dialogue. Adding voice-based gameplay would make sessions more natural and immersive, especially for groups playing together around a table. The system needs to not only transcribe speech in real-time but also identify which player is speaking so that actions and dialogue are attributed to the correct character.

Azure Speech Service provides speaker diarisation — the ability to distinguish and label different speakers in an audio stream — combined with real-time speech-to-text (STT). This enables a workflow where players speak naturally, and the system transcribes and routes each utterance to the correct player character.

## Decision Drivers

* Player experience: voice input is more natural than typing for tabletop RPG gameplay
* Multi-speaker requirement: a typical session has 3-6 players speaking in turns (and sometimes over each other)
* Real-time requirement: transcription must keep pace with conversation for interactive gameplay
* Azure-first architecture: the project already uses Azure OpenAI and Azure AI Foundry (see ADR-0005, ADR-0018)
* Cost sensitivity: speech processing is billed per audio hour; sessions typically run 2-4 hours
* Accessibility: text input must remain available as a fallback

## Considered Options

* Option 1: Azure Speech Service with speaker diarisation (TypeScript SDK, browser-side)
    * Use the Azure Speech SDK in the browser to capture audio, stream to Azure Speech Service, and receive diarised transcription results
    * Pros:
      * Native speaker diarisation support with real-time STT
      * TypeScript SDK available for browser integration
      * Speaker identification/enrollment API for consistent speaker labelling
      * Integrates with existing Azure subscription and managed identity patterns
      * Supports continuous recognition for long sessions
      * Word-level timestamps for precise attribution
    * Cons:
      * Requires speaker enrollment workflow (each player registers their voice)
      * Browser microphone access requires user permission and HTTPS
      * Background noise in group settings can degrade accuracy
      * Cost scales with audio hours (~$1/hour for real-time STT)
      * Similar-sounding speakers may be confused without enrollment

* Option 2: Whisper via Azure OpenAI (batch transcription, no diarisation)
    * Record audio segments, send to Whisper API for transcription
    * Pros:
      * Already integrated via Azure OpenAI
      * High transcription accuracy
      * Simple API (send audio, get text)
    * Cons:
      * No built-in speaker diarisation — all speech is a single transcript
      * Batch-oriented, not real-time streaming
      * Players would need to manually indicate who is speaking
      * Does not solve the multi-speaker attribution problem

* Option 3: Third-party diarisation service (e.g., AssemblyAI, Deepgram)
    * Use a non-Azure service for real-time diarisation
    * Pros:
      * Mature diarisation APIs with good accuracy
      * Some offer real-time streaming with speaker labels
    * Cons:
      * Adds a non-Azure dependency, breaking the Azure-first architecture
      * Additional vendor relationship and billing
      * Data leaves the Azure ecosystem (compliance concern)
      * No managed identity integration

## Decision Outcome

Chosen option: "Azure Speech Service with speaker diarisation" (Option 1)

Justification:
* Only option that provides both real-time STT and speaker diarisation in a single service
* Stays within the Azure ecosystem, consistent with the project's Azure-first strategy
* TypeScript SDK enables browser-side audio capture with server-side processing
* Speaker enrollment API allows reliable player identification once registered
* Cost is manageable at session volumes (2-4 hours/session, a few sessions per week)

## Architecture

### Data Flow

```
Browser (mic capture)
    |
    v
WebSocket stream ──> Backend (FastAPI)
    |                    |
    |                    v
    |              Azure Speech Service
    |              (real-time STT + diarisation)
    |                    |
    |                    v
    |              Diarised transcript
    |              { speaker_id, text, timestamp }
    |                    |
    |                    v
    |              Speaker-to-Character mapping
    |              (enrolled speaker → player character)
    |                    |
    v                    v
Frontend display    Game engine processing
(live transcript)   (attribute action to character)
```

### Key Components

1. **Browser Audio Capture**: Use `MediaRecorder` or Azure Speech SDK's `AudioConfig.fromMicrophoneInput()` to capture audio in the browser
2. **WebSocket Transport**: Stream audio chunks from browser to backend via the existing WebSocket infrastructure (see ADR-0017)
3. **Azure Speech Service Integration**: Backend creates a `SpeechRecognizer` with `ConversationTranscriber` for diarisation
4. **Speaker Enrollment**: One-time per-player voice enrollment via Azure Speaker Recognition API; maps voice profiles to player character IDs
5. **Transcript Router**: Maps diarised `speaker_id` labels to enrolled player characters and dispatches to the game engine
6. **Fallback**: Text input remains the default; voice is opt-in per session

### Speaker Enrollment Workflow

1. Player navigates to voice setup page
2. Player speaks a prompted phrase (30 seconds of speech required for enrollment)
3. System creates a voice profile via Azure Speaker Recognition API
4. Voice profile ID is stored against the player's character record
5. During gameplay, diarised speaker labels are matched against enrolled profiles

## Cost Considerations

| Component | Pricing | Estimated Session Cost |
|-----------|---------|----------------------|
| Real-time STT | ~$1.00/audio hour | $2-4 per session (2-4 hours) |
| Speaker Recognition | ~$1.00/1000 transactions | Negligible (enrollment + per-utterance verification) |
| WebSocket bandwidth | Included in App Service | No additional cost |

At 2 sessions/week, monthly cost estimate: $16-32 for speech processing. This is additive to existing Azure OpenAI costs.

## Requirements

* Real-time STT streaming with <2 second latency for interactive gameplay
* Speaker identification for 3-6 concurrent speakers
* Speaker enrollment workflow with voice profile storage
* Noise handling for group settings (echo cancellation, noise suppression)
* Graceful fallback to text input when voice is unavailable or degraded
* HTTPS required for browser microphone access (already in place for production)

## Consequences

### Positive
* More natural and immersive gameplay experience
* Players can focus on role-playing rather than typing
* Speaker attribution enables automatic action routing to correct characters
* Extends existing WebSocket infrastructure (ADR-0017) with a new channel type
* Voice transcripts provide a session log for the Scribe agent

### Negative
* Speaker enrollment adds friction to the onboarding flow
* Audio processing adds ongoing Azure costs ($16-32/month at expected volume)
* Browser microphone permission UX varies across browsers
* Backend complexity increases with audio streaming and speech service integration
* Testing requires audio fixtures and mocking of speech service responses

### Risks and Mitigations
* Risk: Background noise in group play degrades transcription accuracy
  * Mitigation: Use Azure Speech SDK's noise suppression; recommend push-to-talk as a fallback mode; allow manual correction of misattributed speech
* Risk: Similar-sounding speakers are confused by diarisation
  * Mitigation: Speaker enrollment with sufficient training audio (30s+); allow manual speaker correction in the UI; display confidence scores
* Risk: Latency exceeds interactive threshold (>2s)
  * Mitigation: Use continuous recognition mode (not batch); monitor latency via OpenTelemetry (ADR-0018 status update); fall back to text input if latency degrades
* Risk: Cost escalates with longer or more frequent sessions
  * Mitigation: Implement per-session audio budget; offer voice as a premium feature; monitor usage via Azure Cost Management
* Risk: Browser compatibility issues with microphone access
  * Mitigation: Feature-detect `MediaRecorder`/`getUserMedia`; show clear fallback messaging; text input always available

## Next Steps

1. Provision Azure Speech Service resource in the existing resource group
2. Prototype speaker enrollment workflow using Azure Speaker Recognition API
3. Implement browser-side audio capture with WebSocket streaming
4. Integrate `ConversationTranscriber` in the backend for diarised real-time STT
5. Build speaker-to-character mapping service
6. Design push-to-talk and continuous listening UI modes
7. Load-test with 4-6 concurrent speakers to validate accuracy and latency

## Links

* Related ADRs: [ADR-0005 - Azure OpenAI Integration](0005-azure-openai-integration.md), [ADR-0017 - Unified SDK with WebSocket Extension](0017-unified-sdk-websocket-extension.md), [ADR-0018 - Azure AI Agents SDK Adoption](0018-azure-ai-agents-sdk-adoption.md)
* References:
  * [Azure Speech Service — Get started with speech-to-text diarisation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-stt-diarization)
  * [Azure Speaker Recognition API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speaker-recognition-overview)
  * [Azure Speech SDK for JavaScript](https://learn.microsoft.com/en-us/javascript/api/microsoft-cognitiveservices-speech-sdk/)
  * [Azure Speech Service Pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/speech-services/)
  * GitHub issue: #404

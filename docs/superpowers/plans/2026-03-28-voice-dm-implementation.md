# Voice DM — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add real-time voice interaction with the AI Dungeon Master using Azure AI Foundry's GPT Realtime API via WebRTC, with Hybrid Campfire floor management for multiplayer.

**Architecture:** Backend mints ephemeral WebRTC tokens; browser connects directly to Foundry. DM speaks then yields floor. Text always appears alongside voice. Floor management via React context + WebSocket broadcast.

**Tech Stack:** Azure GPT Realtime API, WebRTC, React hooks, FastAPI, Bicep

---

### Task 1: Deploy gpt-realtime-mini Model to Foundry

**Files:**
- Modify: `infra/modules/ai-foundry.bicep`

- [ ] **Step 1: Add realtime model deployment to Bicep**

In `infra/modules/ai-foundry.bicep`, add after the `embeddingDeployment` resource:

```bicep
// gpt-realtime-mini — real-time voice for DM narration
resource realtimeDeployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: foundry
  name: 'gpt-realtime-mini'
  sku: {
    name: 'GlobalStandard'
    capacity: 1
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: 'gpt-realtime-mini'
      version: '2025-12-15'
    }
  }
  dependsOn: [embeddingDeployment]
}
```

- [ ] **Step 2: Validate Bicep**

Run: `az bicep build --file infra/main.bicep`
Expected: No errors

- [ ] **Step 3: Deploy the model**

```bash
azd provision --environment dev --no-prompt
```

Or if azd fails:
```bash
az deployment sub create \
  --location swedencentral \
  --template-file infra/main.bicep \
  --parameters environmentName=dev location=swedencentral resourceGroupName=str-dev-rg
```

- [ ] **Step 4: Verify deployment**

```bash
az cognitiveservices account deployment list \
  --name dev-foundry-h7bgqs75raq2c \
  --resource-group str-dev-rg \
  --query "[].{name:name, model:properties.model.name}" -o table
```

Expected: `gpt-realtime-mini` appears in the list

- [ ] **Step 5: Commit**

```bash
git add infra/modules/ai-foundry.bicep
git commit -m "infra: deploy gpt-realtime-mini for voice DM

Adds real-time audio model to Foundry resource in Sweden Central.
Used for WebRTC speech-to-speech DM interactions.

Refs #588, #591"
```

---

### Task 2: Backend Realtime Token Endpoint

**Files:**
- Create: `backend/app/api/routes/realtime.py`
- Modify: `backend/app/main.py` (register route)
- Test: `backend/tests/test_realtime_token.py`

- [ ] **Step 1: Write failing test**

```python
# backend/tests/test_realtime_token.py
"""Tests for the realtime voice token endpoint."""

import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient


def test_realtime_token_returns_401_without_configured_endpoint(client: TestClient) -> None:
    """Token endpoint should return 503 when Foundry is not configured."""
    with patch("app.api.routes.realtime.settings") as mock_settings:
        mock_settings.azure_openai_endpoint = ""
        response = client.get("/api/realtime/token")
        assert response.status_code == 503


def test_realtime_token_endpoint_exists(client: TestClient) -> None:
    """Token endpoint should be registered."""
    response = client.get("/api/realtime/token")
    # Will be 503 (not configured) or 200 — but not 404
    assert response.status_code != 404
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest backend/tests/test_realtime_token.py -v`
Expected: FAIL — route not found (404)

- [ ] **Step 3: Implement the token endpoint**

```python
# backend/app/api/routes/realtime.py
"""Realtime voice token endpoint for WebRTC connections."""

import logging

from fastapi import APIRouter, HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/realtime", tags=["realtime"])


@router.get("/token")
async def get_realtime_token() -> dict:
    """Mint an ephemeral WebRTC token for the Azure Foundry realtime API.

    The browser uses this token to establish a direct WebRTC connection
    to Azure without exposing permanent credentials.

    Returns:
        Dict with token, endpoint, deployment, and voice config.
    """
    if not settings.azure_openai_endpoint:
        raise HTTPException(
            status_code=503,
            detail="Azure OpenAI endpoint not configured",
        )

    try:
        import httpx
        from azure.identity import DefaultAzureCredential

        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")

        # Request ephemeral key from the realtime sessions endpoint
        endpoint = settings.azure_openai_endpoint.rstrip("/")
        url = f"{endpoint}/openai/v1/realtime/client_secrets"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {token.token}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-realtime-mini",
                    "voice": "ballad",
                },
                params={"api-version": "2024-10-21"},
            )
            response.raise_for_status()
            data = response.json()

        return {
            "token": data.get("client_secret", {}).get("value"),
            "endpoint": endpoint,
            "deployment": "gpt-realtime-mini",
            "voice": "ballad",
            "expires_at": data.get("client_secret", {}).get("expires_at"),
        }

    except Exception as e:
        logger.error("Failed to mint realtime token: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to create realtime session token",
        ) from e
```

- [ ] **Step 4: Register the route in main.py**

In `backend/app/main.py`, add the import and include:

```python
from app.api.routes.realtime import router as realtime_router

# Add with other router includes:
app.include_router(realtime_router, prefix="/api")
```

- [ ] **Step 5: Run tests**

Run: `uv run pytest backend/tests/test_realtime_token.py -v`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add backend/app/api/routes/realtime.py backend/app/main.py backend/tests/test_realtime_token.py
git commit -m "feat: add /api/realtime/token endpoint for WebRTC voice auth

Mints ephemeral tokens via Managed Identity for browser WebRTC
connections to Azure Foundry realtime API.

Refs #588, #590"
```

---

### Task 3: React Voice Hook — useRealtimeVoice

**Files:**
- Create: `frontend/src/hooks/useRealtimeVoice.ts`
- Test: `frontend/src/hooks/useRealtimeVoice.test.ts`

- [ ] **Step 1: Write failing test**

```tsx
// frontend/src/hooks/useRealtimeVoice.test.ts
import { renderHook, act } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useRealtimeVoice } from "./useRealtimeVoice";

// Mock fetch for token endpoint
globalThis.fetch = vi.fn();

describe("useRealtimeVoice", () => {
  it("starts in disconnected state", () => {
    const { result } = renderHook(() => useRealtimeVoice());
    expect(result.current.connectionState).toBe("disconnected");
    expect(result.current.isSpeaking).toBe(false);
    expect(result.current.isListening).toBe(false);
  });

  it("provides connect and disconnect methods", () => {
    const { result } = renderHook(() => useRealtimeVoice());
    expect(typeof result.current.connect).toBe("function");
    expect(typeof result.current.disconnect).toBe("function");
    expect(typeof result.current.setVoiceEnabled).toBe("function");
  });
});
```

- [ ] **Step 2: Implement the hook**

```tsx
// frontend/src/hooks/useRealtimeVoice.ts
import { useCallback, useRef, useState } from "react";

type ConnectionState = "disconnected" | "connecting" | "connected" | "error";

interface RealtimeVoiceState {
  connectionState: ConnectionState;
  isSpeaking: boolean; // DM is currently outputting audio
  isListening: boolean; // Mic is active (push-to-talk held)
  voiceEnabled: boolean;
  transcript: string; // Latest DM text transcript
  error: string | null;
}

interface UseRealtimeVoiceReturn extends RealtimeVoiceState {
  connect: () => Promise<void>;
  disconnect: () => void;
  startListening: () => void;
  stopListening: () => void;
  setVoiceEnabled: (enabled: boolean) => void;
  sendTextAsVoiceContext: (text: string) => void;
}

export function useRealtimeVoice(): UseRealtimeVoiceReturn {
  const [state, setState] = useState<RealtimeVoiceState>({
    connectionState: "disconnected",
    isSpeaking: false,
    isListening: false,
    voiceEnabled: false,
    transcript: "",
    error: null,
  });

  const pcRef = useRef<RTCPeerConnection | null>(null);
  const dcRef = useRef<RTCDataChannel | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const connect = useCallback(async () => {
    setState((s) => ({ ...s, connectionState: "connecting", error: null }));

    try {
      // 1. Get ephemeral token from backend
      const tokenRes = await fetch("/api/realtime/token");
      if (!tokenRes.ok) throw new Error("Failed to get realtime token");
      const { token, endpoint, deployment } = await tokenRes.json();

      // 2. Create WebRTC peer connection
      const pc = new RTCPeerConnection();
      pcRef.current = pc;

      // 3. Set up audio output
      const audio = new Audio();
      audio.autoplay = true;
      audioRef.current = audio;

      pc.ontrack = (event) => {
        audio.srcObject = event.streams[0];
      };

      // 4. Get user microphone (but don't send until push-to-talk)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      // Add track but start muted
      const audioTrack = stream.getAudioTracks()[0];
      audioTrack.enabled = false;
      pc.addTrack(audioTrack, stream);

      // 5. Create data channel for events
      const dc = pc.createDataChannel("oai-events");
      dcRef.current = dc;

      dc.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.type === "response.audio.delta") {
          setState((s) => ({ ...s, isSpeaking: true }));
        } else if (msg.type === "response.done") {
          setState((s) => ({ ...s, isSpeaking: false }));
        } else if (msg.type === "response.audio_transcript.delta") {
          setState((s) => ({
            ...s,
            transcript: s.transcript + (msg.delta || ""),
          }));
        }
      };

      // 6. Create offer and connect
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const baseUrl = endpoint.replace(/\/$/, "");
      const sdpRes = await fetch(
        `${baseUrl}/openai/v1/realtime?deployment=${deployment}&api-version=2024-10-21`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/sdp",
          },
          body: offer.sdp,
        },
      );

      const answer: RTCSessionDescriptionInit = {
        type: "answer" as RTCSdpType,
        sdp: await sdpRes.text(),
      };
      await pc.setRemoteDescription(answer);

      setState((s) => ({
        ...s,
        connectionState: "connected",
        voiceEnabled: true,
      }));
    } catch (err) {
      setState((s) => ({
        ...s,
        connectionState: "error",
        error: err instanceof Error ? err.message : "Connection failed",
      }));
    }
  }, []);

  const disconnect = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop());
    pcRef.current?.close();
    pcRef.current = null;
    dcRef.current = null;
    setState({
      connectionState: "disconnected",
      isSpeaking: false,
      isListening: false,
      voiceEnabled: false,
      transcript: "",
      error: null,
    });
  }, []);

  const startListening = useCallback(() => {
    const track = streamRef.current?.getAudioTracks()[0];
    if (track) {
      track.enabled = true;
      setState((s) => ({ ...s, isListening: true }));
    }
  }, []);

  const stopListening = useCallback(() => {
    const track = streamRef.current?.getAudioTracks()[0];
    if (track) {
      track.enabled = false;
      setState((s) => ({ ...s, isListening: false }));
    }
  }, []);

  const setVoiceEnabled = useCallback(
    (enabled: boolean) => {
      setState((s) => ({ ...s, voiceEnabled: enabled }));
      if (!enabled) disconnect();
    },
    [disconnect],
  );

  const sendTextAsVoiceContext = useCallback(
    (text: string) => {
      if (dcRef.current?.readyState === "open") {
        dcRef.current.send(
          JSON.stringify({
            type: "conversation.item.create",
            item: { type: "message", role: "user", content: [{ type: "input_text", text }] },
          }),
        );
        dcRef.current.send(JSON.stringify({ type: "response.create" }));
      }
    },
    [],
  );

  return {
    ...state,
    connect,
    disconnect,
    startListening,
    stopListening,
    setVoiceEnabled,
    sendTextAsVoiceContext,
  };
}
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && bun test:run -- useRealtimeVoice`
Expected: All pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/hooks/useRealtimeVoice.ts frontend/src/hooks/useRealtimeVoice.test.ts
git commit -m "feat: add useRealtimeVoice hook for WebRTC voice connection

Manages WebRTC lifecycle, push-to-talk mic control, audio playback,
and data channel events for real-time voice DM interaction.

Refs #588, #592"
```

---

### Task 4: Voice UI Components — MicButton, Indicator, FloorCard

**Files:**
- Create: `frontend/src/components/VoiceMicButton.tsx`
- Create: `frontend/src/components/VoiceMicButton.module.css`
- Create: `frontend/src/components/VoiceIndicator.tsx`
- Create: `frontend/src/components/VoiceIndicator.module.css`
- Create: `frontend/src/components/FloorRequestCard.tsx`
- Create: `frontend/src/components/FloorRequestCard.module.css`
- Create: `frontend/src/components/VoiceControls.tsx`
- Test: `frontend/src/components/VoiceMicButton.test.tsx`

- [ ] **Step 1: Write failing tests**

```tsx
// frontend/src/components/VoiceMicButton.test.tsx
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import VoiceMicButton from "./VoiceMicButton";

describe("VoiceMicButton", () => {
  it("renders mic button", () => {
    render(
      <VoiceMicButton
        isListening={false}
        disabled={false}
        onPressStart={() => {}}
        onPressEnd={() => {}}
      />,
    );
    expect(screen.getByRole("button", { name: /microphone/i })).toBeInTheDocument();
  });

  it("calls onPressStart on mousedown", () => {
    const onStart = vi.fn();
    render(
      <VoiceMicButton
        isListening={false}
        disabled={false}
        onPressStart={onStart}
        onPressEnd={() => {}}
      />,
    );
    fireEvent.mouseDown(screen.getByRole("button"));
    expect(onStart).toHaveBeenCalled();
  });

  it("shows active state when listening", () => {
    render(
      <VoiceMicButton
        isListening={true}
        disabled={false}
        onPressStart={() => {}}
        onPressEnd={() => {}}
      />,
    );
    const btn = screen.getByRole("button");
    expect(btn.getAttribute("data-listening")).toBe("true");
  });
});
```

- [ ] **Step 2: Implement VoiceMicButton**

```tsx
// frontend/src/components/VoiceMicButton.tsx
import type React from "react";
import { Mic } from "lucide-react";
import styles from "./VoiceMicButton.module.css";

interface VoiceMicButtonProps {
  isListening: boolean;
  disabled: boolean;
  onPressStart: () => void;
  onPressEnd: () => void;
}

const VoiceMicButton: React.FC<VoiceMicButtonProps> = ({
  isListening,
  disabled,
  onPressStart,
  onPressEnd,
}) => (
  <button
    type="button"
    className={`${styles.micButton} ${isListening ? styles.active : ""}`}
    onMouseDown={onPressStart}
    onMouseUp={onPressEnd}
    onMouseLeave={onPressEnd}
    onTouchStart={onPressStart}
    onTouchEnd={onPressEnd}
    disabled={disabled}
    data-listening={isListening}
    aria-label={isListening ? "Recording — release to send" : "Hold to speak (microphone)"}
  >
    <Mic size={18} />
  </button>
);

export default VoiceMicButton;
```

```css
/* frontend/src/components/VoiceMicButton.module.css */
.micButton {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid var(--tw-fantasy-text-muted);
  background: transparent;
  color: var(--tw-fantasy-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.micButton:hover:not(:disabled) {
  border-color: var(--tw-accent-gold);
  color: var(--tw-accent-gold);
}

.micButton.active {
  background: #dc2626;
  border-color: #dc2626;
  color: white;
  box-shadow: 0 0 16px rgba(220, 38, 38, 0.4);
  animation: pulse-ring 1.5s ease infinite;
}

.micButton:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

@keyframes pulse-ring {
  0%, 100% { box-shadow: 0 0 8px rgba(220, 38, 38, 0.3); }
  50% { box-shadow: 0 0 20px rgba(220, 38, 38, 0.6); }
}

@media (prefers-reduced-motion: reduce) {
  .micButton.active { animation: none; }
}
```

- [ ] **Step 3: Implement VoiceIndicator**

```tsx
// frontend/src/components/VoiceIndicator.tsx
import type React from "react";
import styles from "./VoiceIndicator.module.css";

interface VoiceIndicatorProps {
  isSpeaking: boolean;
}

const VoiceIndicator: React.FC<VoiceIndicatorProps> = ({ isSpeaking }) => {
  if (!isSpeaking) return null;

  return (
    <div className={styles.indicator} role="status" aria-label="Dungeon Master is speaking">
      <div className={styles.dot} />
      <span className={styles.label}>DM is speaking...</span>
      <div className={styles.waveform}>
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={`bar-${i}`} className={styles.bar} style={{ animationDelay: `${i * 0.1}s` }} />
        ))}
      </div>
    </div>
  );
};

export default VoiceIndicator;
```

```css
/* frontend/src/components/VoiceIndicator.module.css */
.indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.75rem;
  background: rgba(228, 187, 30, 0.1);
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.dot {
  width: 8px;
  height: 8px;
  background: var(--tw-accent-gold);
  border-radius: 50%;
  animation: pulse 1.5s ease infinite;
}

.label {
  color: var(--tw-accent-gold);
  font-size: 0.8rem;
  font-weight: 600;
}

.waveform {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 2px;
  height: 16px;
}

.bar {
  width: 2px;
  background: var(--tw-accent-gold);
  border-radius: 1px;
  animation: wave 0.8s ease-in-out infinite alternate;
}

@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
@keyframes wave { 0% { height: 4px; } 100% { height: 14px; } }

@media (prefers-reduced-motion: reduce) {
  .dot, .bar { animation: none; }
  .bar { height: 8px; }
}
```

- [ ] **Step 4: Implement FloorRequestCard**

```tsx
// frontend/src/components/FloorRequestCard.tsx
import type React from "react";
import { Button } from "@/components/ui/button";
import styles from "./FloorRequestCard.module.css";

interface FloorRequestCardProps {
  visible: boolean;
  onGrantFloor: () => void;
}

const FloorRequestCard: React.FC<FloorRequestCardProps> = ({
  visible,
  onGrantFloor,
}) => {
  if (!visible) return null;

  return (
    <div className={styles.card} role="alert" aria-label="Dungeon Master wants to speak">
      <div className={styles.icon}>✋</div>
      <div className={styles.text}>DM has something to say</div>
      <Button size="sm" variant="secondary" onClick={onGrantFloor}>
        Let them speak
      </Button>
    </div>
  );
};

export default FloorRequestCard;
```

```css
/* frontend/src/components/FloorRequestCard.module.css */
.card {
  background: rgba(228, 187, 30, 0.15);
  border: 1px solid rgba(228, 187, 30, 0.3);
  border-radius: 8px;
  padding: 0.75rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  animation: fadeIn 0.3s ease;
}

.icon { font-size: 1.5rem; }

.text {
  color: var(--tw-accent-gold);
  font-size: 0.85rem;
  font-weight: 600;
}

@keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }

@media (prefers-reduced-motion: reduce) {
  .card { animation: none; }
}
```

- [ ] **Step 5: Run tests**

Run: `cd frontend && bun test:run -- VoiceMicButton`
Expected: All pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/VoiceMicButton.tsx frontend/src/components/VoiceMicButton.module.css \
  frontend/src/components/VoiceMicButton.test.tsx \
  frontend/src/components/VoiceIndicator.tsx frontend/src/components/VoiceIndicator.module.css \
  frontend/src/components/FloorRequestCard.tsx frontend/src/components/FloorRequestCard.module.css
git commit -m "feat: add voice UI components — MicButton, VoiceIndicator, FloorRequestCard

Push-to-talk button with pulse animation, DM speaking indicator with
waveform, and floor management card for multiplayer respect.

Refs #588, #592, #595"
```

---

### Task 5: Integrate Voice into ChatBox and GameInterface

**Files:**
- Modify: `frontend/src/components/ChatBox.tsx`
- Modify: `frontend/src/components/GameInterface.tsx`
- Modify: `frontend/src/pages/GamePage.tsx`

- [ ] **Step 1: Add voice props to ChatBox**

```tsx
// In ChatBox.tsx, extend the props interface:
interface ChatBoxProps {
  messages: ChatMessage[];
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  streamingMessage?: string;
  suggestedActions?: string[];
  onSuggestedAction?: (action: string) => void;
  // Voice props
  voiceEnabled?: boolean;
  isSpeaking?: boolean;
  isListening?: boolean;
  onMicPressStart?: () => void;
  onMicPressEnd?: () => void;
}
```

- [ ] **Step 2: Add VoiceIndicator above messages and MicButton to input form**

```tsx
// Import new components:
import VoiceIndicator from "./VoiceIndicator";
import VoiceMicButton from "./VoiceMicButton";

// Add VoiceIndicator before the messages container:
{voiceEnabled && <VoiceIndicator isSpeaking={isSpeaking ?? false} />}

// Add VoiceMicButton before the text input in the form:
{voiceEnabled && onMicPressStart && onMicPressEnd && (
  <VoiceMicButton
    isListening={isListening ?? false}
    disabled={isLoading || (isSpeaking ?? false)}
    onPressStart={onMicPressStart}
    onPressEnd={onMicPressEnd}
  />
)}
```

- [ ] **Step 3: Wire voice into GameInterface**

```tsx
// In GameInterface.tsx, import and use the hook:
import { useRealtimeVoice } from "../hooks/useRealtimeVoice";
import FloorRequestCard from "./FloorRequestCard";

// Inside the component:
const voice = useRealtimeVoice();
const [dmWantsFloor, setDmWantsFloor] = useState(false);

// Pass voice props to ChatBox:
<ChatBox
  messages={messages}
  onSendMessage={handleSendMessage}
  isLoading={isLoading}
  streamingMessage={streamingMessage}
  suggestedActions={suggestedActions}
  voiceEnabled={voice.voiceEnabled}
  isSpeaking={voice.isSpeaking}
  isListening={voice.isListening}
  onMicPressStart={voice.startListening}
  onMicPressEnd={voice.stopListening}
/>

// Add FloorRequestCard to the side panel:
<FloorRequestCard
  visible={dmWantsFloor}
  onGrantFloor={() => {
    setDmWantsFloor(false);
    // Trigger DM to speak via data channel
  }}
/>

// Add voice toggle button in the controls area:
<Button
  variant={voice.voiceEnabled ? "default" : "outline"}
  size="sm"
  onClick={() => {
    if (voice.voiceEnabled) {
      voice.disconnect();
    } else {
      voice.connect();
    }
  }}
>
  {voice.voiceEnabled ? "🔊 Voice On" : "🔇 Voice Off"}
</Button>
```

- [ ] **Step 4: Run all frontend tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 5: Lint**

Run: `cd frontend && bunx biome check --write .`

- [ ] **Step 6: Commit**

```bash
git add frontend/src/components/ChatBox.tsx frontend/src/components/GameInterface.tsx
git commit -m "feat: integrate voice controls into ChatBox and GameInterface

- VoiceMicButton in chat input bar (push-to-talk)
- VoiceIndicator shows when DM is speaking
- FloorRequestCard in side panel for multiplayer floor management
- Voice toggle button in game controls

Refs #588, #593, #595"
```

---

### Task 6: Build, Deploy, and Test Voice End-to-End

**Files:** No code changes — deployment and testing

- [ ] **Step 1: Rebuild and push backend** (for the realtime token endpoint)

```bash
az acr build --registry acrh7bgqs75raq2c --image str-backend:latest \
  --platform linux/amd64 --file Dockerfile .

az containerapp update --name dev-backend --resource-group str-dev-rg \
  --image acrh7bgqs75raq2c.azurecr.io/str-backend:latest
```

- [ ] **Step 2: Build and deploy frontend**

```bash
cd frontend
VITE_API_URL="https://dev-backend.blacksea-b92bb5e4.swedencentral.azurecontainerapps.io/api" bunx --bun vite build

SWA_TOKEN=$(az staticwebapp secrets list --name dev-frontend-h7bgqs75raq2c --resource-group str-dev-rg --query "properties.apiKey" -o tsv)
npx @azure/static-web-apps-cli deploy frontend/build --deployment-token "$SWA_TOKEN" --env production
```

- [ ] **Step 3: Test voice flow in browser**

1. Open the deployed frontend
2. Select a campaign, create a character, enter the game
3. Click "Voice Off" → should become "Voice On" (browser asks for mic permission)
4. Hold the mic button → red pulse animation, waveform shows
5. Speak: "I look around the tavern" → release
6. DM should respond with voice audio AND text streaming simultaneously
7. "DM is speaking" indicator should show during response
8. After DM finishes → indicator disappears, mic re-enables

- [ ] **Step 4: Test text-only fallback**

1. With voice off, type a message → DM responds with text only (no audio)
2. Everything should work identically to before voice was added

- [ ] **Step 5: Push all changes**

```bash
git push origin main
```

- [ ] **Step 6: Update GitHub issues**

```bash
gh issue comment 588 -c "Voice DM implementation complete — WebRTC connection, push-to-talk, floor management, simultaneous text+voice streaming. Deployed to dev."
```

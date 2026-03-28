import { useCallback, useRef, useState } from "react";
import { getApiBaseUrl } from "../utils/urls";

type ConnectionState = "disconnected" | "connecting" | "connected" | "error";

interface RealtimeVoiceState {
  connectionState: ConnectionState;
  isSpeaking: boolean;
  isListening: boolean;
  voiceEnabled: boolean;
  transcript: string;
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
      const tokenRes = await fetch(`${getApiBaseUrl()}/api/realtime/token`);
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

      // 4. Get user microphone (start muted for push-to-talk)
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      const audioTrack = stream.getAudioTracks()[0];
      audioTrack.enabled = false;
      pc.addTrack(audioTrack, stream);

      // 5. Create data channel for events
      const dc = pc.createDataChannel("oai-events");
      dcRef.current = dc;

      dc.onopen = () => {
        // Configure session with DM system prompt
        dc.send(
          JSON.stringify({
            type: "session.update",
            session: {
              instructions:
                "You are a Dungeon Master for a D&D 5e game. Narrate scenes vividly, voice NPCs with distinct personalities, and respond to player actions. Be dramatic but concise. Always yield the floor after responding — wait for the player to speak next.",
              voice: "ballad",
              input_audio_transcription: { model: "whisper-1" },
              turn_detection: { type: "server_vad", silence_duration_ms: 800 },
            },
          })
        );
      };

      dc.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "response.audio_transcript.delta":
            setState((s) => ({
              ...s,
              transcript: s.transcript + (msg.delta || ""),
            }));
            break;
          case "response.audio_transcript.done":
            setState((s) => ({ ...s, isSpeaking: false }));
            break;
          case "response.created":
            setState((s) => ({ ...s, isSpeaking: true, transcript: "" }));
            break;
          case "response.done":
            setState((s) => ({ ...s, isSpeaking: false }));
            break;
          case "input_audio_buffer.speech_started":
            setState((s) => ({ ...s, isListening: true }));
            break;
          case "input_audio_buffer.speech_stopped":
            setState((s) => ({ ...s, isListening: false }));
            break;
        }
      };

      // 6. Create offer and connect via SDP exchange
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);

      const baseUrl = endpoint.replace(/\/$/, "");
      const sdpRes = await fetch(
        `${baseUrl}/openai/v1/realtime?deployment=${deployment}&api-version=2025-04-01-preview`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/sdp",
          },
          body: offer.sdp,
        }
      );

      if (!sdpRes.ok) throw new Error(`SDP exchange failed: ${sdpRes.status}`);

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
    streamRef.current?.getTracks().forEach((t) => {
      t.stop();
    });
    pcRef.current?.close();
    audioRef.current?.pause();
    pcRef.current = null;
    dcRef.current = null;
    audioRef.current = null;
    streamRef.current = null;
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
      if (!enabled) {
        disconnect();
      }
      setState((s) => ({ ...s, voiceEnabled: enabled }));
    },
    [disconnect]
  );

  const sendTextAsVoiceContext = useCallback((text: string) => {
    if (dcRef.current?.readyState === "open") {
      dcRef.current.send(
        JSON.stringify({
          type: "conversation.item.create",
          item: {
            type: "message",
            role: "user",
            content: [{ type: "input_text", text }],
          },
        })
      );
      dcRef.current.send(JSON.stringify({ type: "response.create" }));
    }
  }, []);

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

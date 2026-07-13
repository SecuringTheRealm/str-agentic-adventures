import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useRealtimeVoice } from "./useRealtimeVoice";

vi.mock("../services/voice", () => ({
  getRealtimeToken: vi.fn().mockResolvedValue({
    token: "ephemeral-secret",
    endpoint: "https://example.openai.azure.com",
    deployment: "gpt-realtime-mini",
    voice: "ballad",
    expires_at: null,
  }),
}));

class FakeDataChannel {
  onopen: (() => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  readyState = "open";
  send = vi.fn();
}

class FakeRTCPeerConnection {
  ontrack: ((event: unknown) => void) | null = null;
  addTrack = vi.fn();
  createDataChannel = vi.fn(() => new FakeDataChannel());
  createOffer = vi.fn().mockResolvedValue({ sdp: "fake-offer-sdp" });
  setLocalDescription = vi.fn().mockResolvedValue(undefined);
  setRemoteDescription = vi.fn().mockResolvedValue(undefined);
  close = vi.fn();
}

globalThis.RTCPeerConnection =
  FakeRTCPeerConnection as unknown as typeof RTCPeerConnection;

Object.defineProperty(globalThis.navigator, "mediaDevices", {
  value: {
    getUserMedia: vi.fn().mockResolvedValue({
      getAudioTracks: () => [{ enabled: true }],
      getTracks: () => [],
    }),
  },
  configurable: true,
});

globalThis.fetch = vi.fn().mockResolvedValue({
  ok: true,
  status: 200,
  text: () => Promise.resolve("fake-answer-sdp"),
});

describe("useRealtimeVoice", () => {
  it("starts in disconnected state", () => {
    const { result } = renderHook(() => useRealtimeVoice());
    expect(result.current.connectionState).toBe("disconnected");
    expect(result.current.isSpeaking).toBe(false);
    expect(result.current.isListening).toBe(false);
    expect(result.current.voiceEnabled).toBe(false);
  });

  it("provides connect and disconnect methods", () => {
    const { result } = renderHook(() => useRealtimeVoice());
    expect(typeof result.current.connect).toBe("function");
    expect(typeof result.current.disconnect).toBe("function");
    expect(typeof result.current.startListening).toBe("function");
    expect(typeof result.current.stopListening).toBe("function");
    expect(typeof result.current.setVoiceEnabled).toBe("function");
    expect(typeof result.current.sendTextAsVoiceContext).toBe("function");
  });

  it("has empty transcript initially", () => {
    const { result } = renderHook(() => useRealtimeVoice());
    expect(result.current.transcript).toBe("");
    expect(result.current.error).toBeNull();
  });

  it("connects using the GA realtime/calls endpoint with no api-version param", async () => {
    const { result } = renderHook(() => useRealtimeVoice());

    await act(async () => {
      await result.current.connect();
    });

    await waitFor(() => {
      expect(result.current.connectionState).toBe("connected");
    });

    expect(globalThis.fetch).toHaveBeenCalledWith(
      "https://example.openai.azure.com/openai/v1/realtime/calls",
      expect.objectContaining({
        method: "POST",
        headers: expect.objectContaining({
          Authorization: "Bearer ephemeral-secret",
          "Content-Type": "application/sdp",
        }),
      })
    );
    const [calledUrl] = (globalThis.fetch as ReturnType<typeof vi.fn>).mock
      .calls[0];
    expect(calledUrl).not.toContain("api-version");
    expect(calledUrl).not.toContain("deployment=");
  });
});

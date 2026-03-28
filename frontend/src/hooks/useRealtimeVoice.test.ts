import { renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { useRealtimeVoice } from "./useRealtimeVoice";

globalThis.fetch = vi.fn();

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
});

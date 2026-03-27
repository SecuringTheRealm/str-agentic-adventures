import { act, renderHook } from "@testing-library/react";
import { useMediaQuery } from "./useMediaQuery";

describe("useMediaQuery", () => {
  let listeners: Array<(event: MediaQueryListEvent) => void> = [];
  let currentMatches = false;

  beforeEach(() => {
    listeners = [];
    currentMatches = false;

    Object.defineProperty(window, "matchMedia", {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: currentMatches,
        media: query,
        onchange: null,
        addEventListener: vi.fn(
          (_event: string, cb: (e: MediaQueryListEvent) => void) => {
            listeners.push(cb);
          }
        ),
        removeEventListener: vi.fn(
          (_event: string, cb: (e: MediaQueryListEvent) => void) => {
            listeners = listeners.filter((l) => l !== cb);
          }
        ),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it("returns false by default when media query does not match", () => {
    currentMatches = false;
    const { result } = renderHook(() => useMediaQuery("(max-width: 768px)"));
    expect(result.current).toBe(false);
  });

  it("returns true when media query matches", () => {
    currentMatches = true;
    const { result } = renderHook(() => useMediaQuery("(max-width: 768px)"));
    expect(result.current).toBe(true);
  });

  it("responds to matchMedia changes", () => {
    currentMatches = false;
    const { result } = renderHook(() => useMediaQuery("(max-width: 768px)"));
    expect(result.current).toBe(false);

    act(() => {
      for (const listener of listeners) {
        listener({ matches: true } as MediaQueryListEvent);
      }
    });

    expect(result.current).toBe(true);
  });

  it("cleans up listener on unmount", () => {
    const { unmount } = renderHook(() => useMediaQuery("(max-width: 768px)"));
    expect(listeners.length).toBe(1);

    unmount();
    expect(listeners.length).toBe(0);
  });
});

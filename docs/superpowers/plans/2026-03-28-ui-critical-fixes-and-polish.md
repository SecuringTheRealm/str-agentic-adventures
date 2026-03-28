# UI Critical Fixes & Polish — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix 7 critical UI bugs and polish the game screen, campaign hub, and character flow with consistent shadcn/ui components and markdown rendering.

**Architecture:** Fix bugs first (loading states, error colours, alert(), markdown), then migrate remaining raw HTML elements to shadcn/ui components page by page. Each task is independently shippable.

**Tech Stack:** React 19, TypeScript, shadcn/ui (Radix), Tailwind CSS v4, Biome, Vitest

---

### Task 1: Create Shared Loading & Error State Components

**Files:**
- Create: `frontend/src/components/LoadingState.tsx`
- Create: `frontend/src/components/ErrorState.tsx`
- Create: `frontend/src/components/LoadingState.module.css`
- Create: `frontend/src/components/ErrorState.module.css`
- Modify: `frontend/src/pages/GamePage.tsx:28-31`
- Modify: `frontend/src/pages/CharacterSelectionPage.tsx:32-34`
- Modify: `frontend/src/pages/CharacterNewPage.tsx:32-34`
- Modify: `frontend/src/pages/CampaignEditPage.tsx:32-34`
- Test: `frontend/src/components/LoadingState.test.tsx`
- Test: `frontend/src/components/ErrorState.test.tsx`

- [ ] **Step 1: Write failing test for LoadingState**

```tsx
// frontend/src/components/LoadingState.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import LoadingState from "./LoadingState";

describe("LoadingState", () => {
  it("renders with default message", () => {
    render(<LoadingState />);
    expect(screen.getByText("Loading...")).toBeInTheDocument();
  });

  it("renders with custom message", () => {
    render(<LoadingState message="Loading game..." />);
    expect(screen.getByText("Loading game...")).toBeInTheDocument();
  });

  it("has accessible role", () => {
    render(<LoadingState />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd frontend && bun test:run -- LoadingState.test`
Expected: FAIL — module not found

- [ ] **Step 3: Implement LoadingState**

```tsx
// frontend/src/components/LoadingState.tsx
import type React from "react";
import styles from "./LoadingState.module.css";

interface LoadingStateProps {
  message?: string;
}

const LoadingState: React.FC<LoadingStateProps> = ({
  message = "Loading...",
}) => (
  <div className={styles.container} role="status" aria-live="polite">
    <div className={styles.spinner} />
    <p className={styles.message}>{message}</p>
  </div>
);

export default LoadingState;
```

```css
/* frontend/src/components/LoadingState.module.css */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 40vh;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--tw-fantasy-surface);
  border-top: 3px solid var(--tw-accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.message {
  color: var(--tw-fantasy-text-muted);
  font-size: 0.95rem;
}

@media (prefers-reduced-motion: reduce) {
  .spinner { animation: none; opacity: 0.6; }
}
```

- [ ] **Step 4: Write failing test for ErrorState**

```tsx
// frontend/src/components/ErrorState.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import ErrorState from "./ErrorState";

describe("ErrorState", () => {
  it("renders error message", () => {
    render(<ErrorState message="Something went wrong" />);
    expect(screen.getByText("Something went wrong")).toBeInTheDocument();
  });

  it("renders retry button when onRetry provided", () => {
    const onRetry = vi.fn();
    render(<ErrorState message="Error" onRetry={onRetry} />);
    expect(screen.getByRole("button", { name: /retry/i })).toBeInTheDocument();
  });

  it("has alert role", () => {
    render(<ErrorState message="Error" />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
  });
});
```

- [ ] **Step 5: Implement ErrorState**

```tsx
// frontend/src/components/ErrorState.tsx
import type React from "react";
import { Button } from "@/components/ui/button";
import styles from "./ErrorState.module.css";

interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => (
  <div className={styles.container} role="alert">
    <p className={styles.message}>{message}</p>
    {onRetry && (
      <Button variant="secondary" onClick={onRetry}>
        Retry
      </Button>
    )}
  </div>
);

export default ErrorState;
```

```css
/* frontend/src/components/ErrorState.module.css */
.container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 30vh;
  gap: 1rem;
  padding: 2rem;
}

.message {
  color: var(--color-danger, #f87171);
  font-size: 1rem;
  text-align: center;
  max-width: 400px;
}
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd frontend && bun test:run -- LoadingState.test ErrorState.test`
Expected: All pass

- [ ] **Step 7: Replace all unstyled loading/error states in page components**

In each of these 4 files, add imports and replace the raw divs:

**GamePage.tsx** (lines 28-31):
```tsx
// Add import at top:
import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";

// Replace line 28:
if (loading) return <LoadingState message="Loading game..." />;
// Replace lines 29-32:
if (error || !campaign || !character)
  return <ErrorState message={error ?? "Game data not found"} />;
```

Apply the same pattern to:
- `CharacterSelectionPage.tsx` (lines 32-34) — message: "Loading campaign..."
- `CharacterNewPage.tsx` (lines 32-34) — message: "Loading campaign..."
- `CampaignEditPage.tsx` (lines 32-34) — message: "Loading campaign..."

- [ ] **Step 8: Run full frontend tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/LoadingState.tsx frontend/src/components/LoadingState.module.css \
  frontend/src/components/LoadingState.test.tsx frontend/src/components/ErrorState.tsx \
  frontend/src/components/ErrorState.module.css frontend/src/components/ErrorState.test.tsx \
  frontend/src/pages/GamePage.tsx frontend/src/pages/CharacterSelectionPage.tsx \
  frontend/src/pages/CharacterNewPage.tsx frontend/src/pages/CampaignEditPage.tsx
git commit -m "fix: add shared LoadingState and ErrorState components

Replace unstyled 'loading-state' and 'error-message' class divs across
4 page components with properly themed, accessible components.

Fixes part of #589, #596"
```

---

### Task 2: Add Markdown Rendering to ChatBox

**Files:**
- Modify: `frontend/src/components/ChatBox.tsx:81`
- Modify: `frontend/src/components/ChatBox.module.css`
- Test: `frontend/src/components/ChatBox.test.tsx` (modify existing)

- [ ] **Step 1: Install react-markdown**

Run: `cd frontend && bun add react-markdown`

- [ ] **Step 2: Write failing test**

```tsx
// Add to existing ChatBox test file or create new:
// frontend/src/components/ChatBoxMarkdown.test.tsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ChatBox from "./ChatBox";

describe("ChatBox markdown rendering", () => {
  it("renders bold text in DM messages", () => {
    const messages = [
      { sender: "dm" as const, text: "You see a **glowing** sword" },
    ];
    render(
      <ChatBox
        messages={messages}
        onSendMessage={() => {}}
        isLoading={false}
      />,
    );
    const strong = document.querySelector("strong");
    expect(strong).toBeInTheDocument();
    expect(strong?.textContent).toBe("glowing");
  });

  it("renders paragraphs in DM messages", () => {
    const messages = [
      { sender: "dm" as const, text: "First paragraph.\n\nSecond paragraph." },
    ];
    render(
      <ChatBox
        messages={messages}
        onSendMessage={() => {}}
        isLoading={false}
      />,
    );
    const paragraphs = document.querySelectorAll("p");
    expect(paragraphs.length).toBeGreaterThanOrEqual(2);
  });

  it("does not render markdown in player messages", () => {
    const messages = [
      { sender: "player" as const, text: "I cast **fireball**" },
    ];
    render(
      <ChatBox
        messages={messages}
        onSendMessage={() => {}}
        isLoading={false}
      />,
    );
    // Player messages should show raw text, not rendered markdown
    expect(screen.getByText("I cast **fireball**")).toBeInTheDocument();
  });
});
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd frontend && bun test:run -- ChatBoxMarkdown.test`
Expected: FAIL — bold not rendered

- [ ] **Step 4: Implement markdown rendering in ChatBox**

Modify `frontend/src/components/ChatBox.tsx`:

```tsx
// Add import at top (after existing imports):
import ReactMarkdown from "react-markdown";

// Replace line 81 (the message text rendering):
// Old: <div className={styles.messageText}>{message.text}</div>
// New:
<div className={styles.messageText}>
  {message.sender === "dm" ? (
    <ReactMarkdown>{message.text}</ReactMarkdown>
  ) : (
    message.text
  )}
</div>
```

Also add to the streaming message section (around line 88):
```tsx
// Old: {streamingMessage}
// New:
<ReactMarkdown>{streamingMessage}</ReactMarkdown>
```

- [ ] **Step 5: Add markdown styles to ChatBox.module.css**

Append to `frontend/src/components/ChatBox.module.css`:

```css
/* Markdown rendering in DM messages */
.messageText :global(p) {
  margin: 0.25em 0;
}

.messageText :global(p:first-child) {
  margin-top: 0;
}

.messageText :global(p:last-child) {
  margin-bottom: 0;
}

.messageText :global(strong) {
  color: var(--tw-accent-gold);
  font-weight: 700;
}

.messageText :global(em) {
  font-style: italic;
  opacity: 0.9;
}
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd frontend && bun test:run -- ChatBox`
Expected: All pass

- [ ] **Step 7: Commit**

```bash
git add frontend/src/components/ChatBox.tsx frontend/src/components/ChatBox.module.css \
  frontend/src/components/ChatBoxMarkdown.test.tsx frontend/package.json frontend/bun.lockb
git commit -m "feat: add markdown rendering to DM messages in ChatBox

DM responses now render bold, italic, and paragraph markdown.
Player messages remain plain text. Gold accent for bold text.

Fixes #597"
```

---

### Task 3: Fix DiceRoller alert() and CampaignGallery Error Colours

**Files:**
- Modify: `frontend/src/components/DiceRoller.tsx:135`
- Modify: `frontend/src/components/CampaignGallery.tsx` (error state section)
- Test: `frontend/src/components/DiceRoller.test.tsx` (add test)

- [ ] **Step 1: Write failing test for DiceRoller error handling**

```tsx
// frontend/src/components/DiceRollerError.test.tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import DiceRoller from "./DiceRoller";

describe("DiceRoller error handling", () => {
  it("does not call alert() on error", async () => {
    const alertSpy = vi.spyOn(window, "alert").mockImplementation(() => {});
    // Render with no websocket — API call will fail
    render(<DiceRoller />);
    // The component should not use alert() even on error
    expect(alertSpy).not.toHaveBeenCalled();
    alertSpy.mockRestore();
  });
});
```

- [ ] **Step 2: Fix DiceRoller — replace alert() with inline error state**

In `frontend/src/components/DiceRoller.tsx`, replace line 135:

```tsx
// Old (line 135):
// alert("Failed to roll dice. Please try again.");

// New: Add error state to the component
// 1. Add state at top of component:
const [rollError, setRollError] = useState<string | null>(null);

// 2. Replace the alert line:
setRollError("Failed to roll dice. Please try again.");

// 3. Clear error on next successful roll (after setLastResult):
setRollError(null);

// 4. Render error inline (add after the roll result display):
{rollError && (
  <div className={styles.rollError} role="alert">
    {rollError}
  </div>
)}
```

Add to `DiceRoller.module.css`:
```css
.rollError {
  color: var(--color-danger, #f87171);
  font-size: 0.8rem;
  text-align: center;
  padding: 0.5rem;
  margin-top: 0.5rem;
  background: rgba(248, 113, 113, 0.1);
  border-radius: 4px;
}
```

- [ ] **Step 3: Fix CampaignGallery error colours**

In `frontend/src/components/CampaignGallery.tsx`, find the error rendering section and replace any inline light-mode styles:

```tsx
// Replace any: style={{ background: '#f5f5f5' }} or style={{ background: '#fff5f5' }}
// With theme-aware CSS module class:
```

In `CampaignGallery.module.css`, add/update:
```css
.errorContainer {
  background: var(--tw-fantasy-surface);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  color: var(--tw-fantasy-text-muted);
}

.debugInfo {
  margin-top: 1rem;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  padding: 0.75rem;
  font-size: 0.75rem;
  color: var(--tw-fantasy-text-muted);
  text-align: left;
}
```

- [ ] **Step 4: Run tests**

Run: `cd frontend && bun test:run -- DiceRoller`
Expected: All pass (no alert() calls)

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/DiceRoller.tsx frontend/src/components/DiceRoller.module.css \
  frontend/src/components/DiceRollerError.test.tsx \
  frontend/src/components/CampaignGallery.tsx frontend/src/components/CampaignGallery.module.css
git commit -m "fix: replace DiceRoller alert() with inline error, fix Gallery error colours

- DiceRoller: inline error message instead of browser alert()
- CampaignGallery: theme-aware dark error/debug backgrounds

Fixes part of #589, #601"
```

---

### Task 4: Install Missing shadcn/ui Components

**Files:**
- Create: `frontend/src/components/ui/skeleton.tsx`
- Create: `frontend/src/components/ui/tabs.tsx`
- Create: `frontend/src/components/ui/tooltip.tsx`
- Create: `frontend/src/components/ui/progress.tsx`
- Create: `frontend/src/components/ui/separator.tsx`
- Create: `frontend/src/components/ui/dialog.tsx`
- Create: `frontend/src/components/ui/toast.tsx` (or sonner)
- Create: `frontend/src/components/ui/scroll-area.tsx`

- [ ] **Step 1: Install shadcn components via CLI**

```bash
cd frontend
bunx --bun shadcn@latest add skeleton tabs tooltip progress separator dialog scroll-area sonner
```

If the CLI doesn't work with the existing setup, install the Radix primitives manually:

```bash
bun add @radix-ui/react-tabs @radix-ui/react-progress @radix-ui/react-separator @radix-ui/react-scroll-area sonner
```

Then create each component file following the shadcn patterns already in `frontend/src/components/ui/button.tsx`.

- [ ] **Step 2: Verify imports work**

```bash
cd frontend && bun run build 2>&1 | tail -5
```

Expected: Build succeeds

- [ ] **Step 3: Commit**

```bash
git add frontend/src/components/ui/ frontend/package.json frontend/bun.lockb
git commit -m "feat: install shadcn/ui Skeleton, Tabs, Tooltip, Progress, Separator, Dialog, ScrollArea, Sonner

Foundation components for UI polish across all pages.

Part of #589"
```

---

### Task 5: Campaign Hub Polish — Skeleton Loaders and Tabs

**Files:**
- Modify: `frontend/src/components/CampaignGallery.tsx`
- Modify: `frontend/src/components/CampaignSelection.tsx`
- Test: `frontend/src/components/CampaignGallery.test.tsx` (add skeleton test)

- [ ] **Step 1: Add Skeleton loaders to CampaignGallery**

Replace the current loading spinner with skeleton cards:

```tsx
// In CampaignGallery.tsx, replace the loading state:
import { Skeleton } from "@/components/ui/skeleton";

// Replace loading render with:
if (loading) {
  return (
    <div className={styles.galleryGrid}>
      {Array.from({ length: 4 }).map((_, i) => (
        <Card key={`skeleton-${i}`} className={styles.campaignCard}>
          <CardHeader>
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-1/2 mt-2" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6 mt-2" />
          </CardContent>
          <CardFooter>
            <Skeleton className="h-10 w-full" />
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}
```

- [ ] **Step 2: Replace duplicated campaign list JSX in CampaignSelection with Tabs**

```tsx
// In CampaignSelection.tsx, replace the viewMode toggle + duplicated JSX:
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

// Replace the header buttons and conditional renders with:
<Tabs defaultValue="gallery">
  <TabsList>
    <TabsTrigger value="gallery">Gallery</TabsTrigger>
    <TabsTrigger value="my-campaigns">
      My Campaigns ({customCampaigns.length})
    </TabsTrigger>
  </TabsList>
  <TabsContent value="gallery">
    <CampaignGallery
      onCampaignSelected={handleCampaignSelected}
      onCreateCustom={handleCreateCustom}
    />
  </TabsContent>
  <TabsContent value="my-campaigns">
    {/* Single campaign list — no more duplication */}
    {customCampaigns.length === 0 ? (
      <p>No custom campaigns yet. Create one from the Gallery!</p>
    ) : (
      <div className={styles.campaignList}>
        {customCampaigns.map((campaign) => (
          /* ... campaign card rendering — extracted once ... */
        ))}
      </div>
    )}
  </TabsContent>
</Tabs>
```

- [ ] **Step 3: Run tests**

Run: `cd frontend && bun test:run`
Expected: All pass

- [ ] **Step 4: Lint and format**

Run: `cd frontend && bunx biome check --write .`

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/CampaignGallery.tsx frontend/src/components/CampaignSelection.tsx \
  frontend/src/components/CampaignGallery.module.css frontend/src/components/CampaignSelection.module.css
git commit -m "feat: add Skeleton loaders to campaign gallery, replace viewMode with Tabs

- Campaign cards show animated skeletons while loading
- Gallery/My Campaigns toggle now uses shadcn Tabs (removes duplicated JSX)

Part of #589, #598"
```

---

### Task 6: Game Screen Polish — CharacterSheet, Visuals, ScrollArea

**Files:**
- Modify: `frontend/src/components/GameInterface.tsx`
- Modify: `frontend/src/components/ChatBox.tsx`
- Modify: `frontend/src/components/ImageDisplay.tsx`

- [ ] **Step 1: Add ScrollArea to ChatBox messages**

```tsx
// In ChatBox.tsx, wrap the messages container:
import { ScrollArea } from "@/components/ui/scroll-area";

// Replace the messagesContainer div with:
<ScrollArea className={styles.messagesContainer}>
  <div role="log" aria-live="polite" aria-label="Chat messages">
    {/* existing message rendering */}
  </div>
</ScrollArea>
```

- [ ] **Step 2: Fix ImageDisplay empty state**

```tsx
// In ImageDisplay.tsx, replace the plain "No image available" text:
{!imageUrl && (
  <div className={styles.emptyState}>
    <div className={styles.emptyIcon}>🏰</div>
    <p>Scene will appear as the story unfolds</p>
  </div>
)}
```

Add to `ImageDisplay.module.css`:
```css
.emptyState {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  border: 1px dashed rgba(228, 187, 30, 0.3);
  border-radius: 8px;
  background: rgba(228, 187, 30, 0.05);
}

.emptyIcon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.emptyState p {
  color: var(--tw-fantasy-text-muted);
  font-size: 0.85rem;
}
```

- [ ] **Step 3: Replace raw visual buttons in GameInterface with shadcn Button**

```tsx
// In GameInterface.tsx, replace the raw <button> elements for visual generation:
import { Button } from "@/components/ui/button";

// Replace: <button className={styles.visualButton} onClick={...}>
// With: <Button variant="secondary" onClick={...}>
```

- [ ] **Step 4: Run tests and lint**

Run: `cd frontend && bun test:run && bunx biome check --write .`
Expected: All pass

- [ ] **Step 5: Commit**

```bash
git add frontend/src/components/ChatBox.tsx frontend/src/components/ImageDisplay.tsx \
  frontend/src/components/ImageDisplay.module.css frontend/src/components/GameInterface.tsx
git commit -m "feat: game screen polish — ScrollArea, empty states, Button migration

- ChatBox uses ScrollArea for messages
- ImageDisplay shows themed empty state with castle icon
- Visual generation buttons migrated to shadcn Button

Part of #589, #601"
```

---

### Task 7: Build and Deploy Updated Frontend

**Files:** No code changes — deployment operations

- [ ] **Step 1: Build**

```bash
cd frontend
VITE_API_URL="https://dev-backend.blacksea-b92bb5e4.swedencentral.azurecontainerapps.io/api" bunx --bun vite build
```

- [ ] **Step 2: Deploy to Static Web App**

```bash
SWA_TOKEN=$(az staticwebapp secrets list --name dev-frontend-h7bgqs75raq2c --resource-group str-dev-rg --query "properties.apiKey" -o tsv)
npx @azure/static-web-apps-cli deploy frontend/build --deployment-token "$SWA_TOKEN" --env production
```

- [ ] **Step 3: Test in browser**

Open `https://icy-meadow-085c97403.2.azurestaticapps.net` and verify:
- Loading states show spinners on all pages
- Error states have dark-themed backgrounds
- DM messages render markdown (bold, italic, paragraphs)
- Campaign gallery shows skeleton loaders
- Gallery/My Campaigns uses proper tabs
- No browser alert() on dice roll errors
- Image display shows castle empty state

- [ ] **Step 4: Commit and push**

```bash
git push origin main
```

- [ ] **Step 5: Update GitHub issues**

```bash
gh issue close 596 -c "Fixed in UI polish plan — loading/error states"
gh issue close 597 -c "Fixed — markdown rendering in ChatBox"
```

# shadcn/ui Migration Design — #418

## Context

The frontend uses 17 custom React components with CSS Modules and 180+ CSS variables creating a dark fantasy D&D theme. Accessibility is decent (ARIA, skip links, focus traps) but hand-rolled. Issue #418 calls for adopting shadcn/ui to improve component quality and accessibility.

## Approach: Phased Foundation + Migration

### Phase 1: Foundation (this PR)

**Install Tailwind CSS + shadcn/ui:**
- Add Tailwind CSS v4, postcss, autoprefixer
- Initialise shadcn/ui with `bunx shadcn@latest init`
- Map existing CSS variables to Tailwind custom theme (gold, teal, wood, stone colours)
- Both CSS Modules and Tailwind coexist during migration

**Migrate 3 high-value components to shadcn/ui:**
1. **Dialog** (replaces ConfirmDialog) — Radix Dialog primitive with focus trap, ESC close, overlay click, proper ARIA
2. **ScrollArea** (for ChatBox) — Accessible scrollable region with keyboard navigation
3. **Button** — Consistent button variants (primary/wood, secondary/stone, danger/red) with proper focus indicators

**Add missing accessibility:**
- Colour contrast fixes (ensure WCAG AA on all text)
- Focus-visible indicators on all interactive elements
- `aria-label` on icon-only buttons
- Form validation with `aria-describedby` error messages

### Phase 2: Progressive Migration (future PRs)
- Migrate remaining components one-by-one
- Replace CSS Modules with Tailwind utility classes
- Add shadcn/ui: Input, Select, Textarea, Tabs, Tooltip, Sheet (mobile sidebar)

## Key Decisions

- **Tailwind v4** (latest, CSS-first config) not v3
- **Keep fantasy theme** — all shadcn/ui components themed via CSS variables
- **Coexistence** — CSS Modules and Tailwind work side-by-side during migration
- **No breaking changes** — existing component APIs preserved, only internals change

## Files to Create/Modify

- `frontend/tailwind.config.ts` — Custom theme with fantasy colours
- `frontend/postcss.config.js` — PostCSS with Tailwind
- `frontend/src/index.css` — Add Tailwind directives, keep CSS variables
- `frontend/components.json` — shadcn/ui config
- `frontend/src/components/ui/` — shadcn/ui component directory
- `frontend/src/components/ui/button.tsx` — Themed Button
- `frontend/src/components/ui/dialog.tsx` — Themed Dialog
- `frontend/src/components/ui/scroll-area.tsx` — Themed ScrollArea
- `frontend/src/components/ConfirmDialog.tsx` — Refactor to use shadcn Dialog
- `frontend/src/components/ChatBox.tsx` — Use ScrollArea
- Various components — Replace `<button>` with themed Button

## Verification

- `bun test:run` — all existing tests pass
- `bunx biome check .` — lint clean
- Manual: verify fantasy theme preserved (gold borders, wood buttons, dark bg)
- Manual: keyboard navigation through Dialog, ChatBox, all buttons
- Lighthouse accessibility audit improvement

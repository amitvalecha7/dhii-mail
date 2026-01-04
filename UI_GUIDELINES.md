# Liquid Glass UI Guidelines (Issue #54)

**Status**: DRAFT  
**Version**: 1.0.0  
**Last Updated**: 2026-01-04

---

## 1. The Design Philosophy: "Liquid Glass"

Dhii-Mail is not a collection of static pages. It is a **continuous stream of consciousness**. The UI should feel like looking through a pane of intelligent glass that rearranges itself to fit the user's intent.

### Core Principles
1.  **Immaterial Materiality**: Use blur (`backdrop-filter`) and translucency to provide context, not just opacity.
2.  **Physics, Not Animations**: Things don't just "appear"; they slide, spring, and grow.
3.  **Content is King**: The chrome (buttons, bars) should recede. The email/task/deal is the hero.

## 2. Color System

We use a semantic color system that adapts to Light/Dark modes automatically.

| Token | Light Mode | Dark Mode | Usage |
| :--- | :--- | :--- | :--- |
| `bg-glass` | `rgba(255, 255, 255, 0.7)` | `rgba(20, 20, 30, 0.7)` | Main Panels, Cards |
| `bg-base` | `#f8f9fa` | `#0f0f12` | App Background |
| `text-primary` | `#1a1a1a` | `#ffffff` | Headings, Body |
| `text-muted` | `#666666` | `#a0a0a0` | Metadata, Secondary info |
| `accent-primary` | `#4F46E5` (Indigo) | `#6366F1` (Indigo) | Primary Actions |
| `accent-danger` | `#EF4444` | `#F87171` | Destructive Actions |

## 3. Typography

**Font Family**: `Inter`, system-ui, sans-serif.

| Style | Weight | Size | Line Height | Usage |
| :--- | :--- | :--- | :--- | :--- |
| **H1** | 700 | 24px | 1.2 | Page Titles |
| **H2** | 600 | 20px | 1.3 | Section Headers |
| **Body** | 400 | 16px | 1.5 | Email Content |
| **Small** | 400 | 14px | 1.4 | Metadata |
| **Mono** | 400 | 13px | 1.4 | Code, Logs |

## 4. Layout & Spacing

We use a **4px grid** system. All margins and paddings should be multiples of 4.

*   **Compact**: `4px` / `8px` (Dense lists)
*   **Comfortable**: `16px` (Standard cards)
*   **Spacious**: `32px` (Section breaks)

### The "Stream" Layout
Instead of a fixed sidebar/main layout, Dhii-Mail uses a **Horizontal Scroll Stream** for context.
*   **Pane 1**: Navigation / Inbox List (Fixed 300px)
*   **Pane 2**: Active Item (Flexible)
*   **Pane 3**: Context / Assistant (Fixed 350px, Collapsible)

## 5. Motion Guidelines

Motion conveys **state change**.

1.  **Enter/Exit**:
    *   **Scale**: 0.95 -> 1.00
    *   **Opacity**: 0 -> 1
    *   **Duration**: 200ms
    *   **Easing**: `cubic-bezier(0.4, 0, 0.2, 1)`

2.  **Layout Shifts**:
    *   Use `framer-motion` layout prop for magical reordering of lists.
    *   When an email is deleted, the list should slide up to fill the gap.

## 6. Component Library (A2UI Primitives)

### Glass Card
```css
.card {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}
```

### Floating Action Button (FAB)
*   Used for the primary AI trigger.
*   Always visible in the bottom-right.
*   Morphs into the Chat Interface on click.

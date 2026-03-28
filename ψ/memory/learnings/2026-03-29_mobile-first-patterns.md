# Mobile-First CSS & Interaction Patterns

**Date**: 2026-03-29
**Source**: Session 10 — multiple mobile bug fixes
**Context**: Shipped 3 separate fixes for the same mobile focus bug pattern

## Pattern: Fixed-Position Click Handling

On mobile, `position: fixed` elements require a "focus tap" before `onClick` fires. This is browser behavior — the first tap focuses the element, the second tap triggers the click.

**Fix**: Use `onMouseDown` with `e.preventDefault()` instead of `onClick`. The `mousedown` event (mapped to `touchstart` on mobile) fires before the browser's focus logic.

```tsx
// BAD — requires two taps on mobile
<div onClick={() => toggle()}>

// GOOD — works on first tap
<div onMouseDown={(e) => { e.preventDefault(); toggle(); }}>
```

Guard against buttons inside the element:
```tsx
if ((e.target as HTMLElement).closest('button')) return;
```

## Pattern: Scroll Lock Without position:fixed

`position: fixed` on `<body>` conflicts with mobile virtual keyboard — after keyboard shows/hides, bottom half of screen becomes unresponsive.

**Fix**: Use `overflow: hidden` on both `html` and `body`:
```tsx
document.documentElement.style.overflow = 'hidden';
document.body.style.overflow = 'hidden';
```

Never use `position: fixed` + `top: -scrollY` on body for mobile apps.

## Pattern: No :hover on Touch

`:hover` CSS states don't work on touch devices. Buttons hidden behind hover states are invisible.

**Fix**: Use `@media (max-width: 768px)` to override opacity to always-visible.

## Key Takeaway

Always test these three on mobile before shipping:
1. Click/tap handlers on fixed elements → onMouseDown
2. Scroll lock modals → overflow:hidden only
3. Hover-revealed buttons → always visible on mobile

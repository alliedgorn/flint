# Lessons Learned: Mobile Overflow Pattern & Pile-On Prevention

**Date**: 2026-03-29
**Session**: 11 — Marathon Two
**Source**: T#456, T#472, T#485, Sable routing incident

## Mobile CSS Overflow

Every form input in a flex container needs these three properties to prevent overflow on mobile:

```css
.input {
  min-width: 0;        /* Override flex default min-width: auto */
  max-width: 100%;     /* Prevent native input min-width from overflowing */
  box-sizing: border-box; /* Include padding in width calculation */
}

.container {
  overflow: hidden;    /* Clip anything that still escapes */
}
```

Apply proactively on all form inputs, not reactively when Gorn finds overflow on iPhone.

## Pile-On Prevention

1. Read the full thread before responding
2. If someone already answered → react with emoji, don't reply
3. If someone already @mentioned Sable → don't @mention again
4. Gorn action items always go through Sable, even when the steps seem obvious

Both norms were violated in this session despite being displayed in /recap rules.

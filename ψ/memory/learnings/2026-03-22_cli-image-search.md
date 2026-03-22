# Lesson: CLI Image Search Patterns

**Date**: 2026-03-22
**Source**: Session 4 avatar hunt
**Tags**: cli, images, api, tooling

## Pattern

When searching for images from CLI without browser access:

1. **Wikimedia Commons API** is most reliable:
   - Search: `/w/api.php?action=query&list=search&srsearch=<terms>&srnamespace=6&format=json`
   - Get URLs: `/w/api.php?action=query&titles=File:<name>&prop=imageinfo&iiprop=url&iiurlwidth=600&format=json`
   - Thumbnails via `thumburl` field

2. **Pexels** works with direct URL pattern:
   - `https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=600`
   - But you need valid photo IDs — random guessing produces wrong images

3. **Unsplash, Pixabay** block CLI access (401/403)

4. **Strategy**: Use Wikimedia API to search → get thumbnail URLs → download and visually inspect before using.

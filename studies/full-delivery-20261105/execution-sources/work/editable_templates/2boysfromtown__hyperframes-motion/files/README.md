<p align="center"><img src="media/cover.png" alt="hyperframes-motion — After Effects-style motion graphics in HTML + GSAP" width="100%"></p>

# hyperframes-motion

**After Effects-style motion graphics in plain HTML + [GSAP](https://gsap.com).** Drop-in CSS effects, kinetic-typography helpers, and four ready-to-edit 1080×1920 templates that turn a web page into a cinematic vertical video — 3D camera moves, glitch and light-leak looks, character-by-character text reveals, smooth scene transitions. No After Effects, no timeline software.

[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) ![HTML + GSAP](https://img.shields.io/badge/HTML%20%2B-GSAP-88CE02) ![9:16](https://img.shields.io/badge/output-1080x1920-black) ![Claude Code skill](https://img.shields.io/badge/Claude%20Code-skill-8A2BE2)

## What's inside

| | |
|---|---|
| **`css/motion-effects.css`** | 3D camera moves (dolly, pan, tilt, orbit), motion blur, light leak, lens flare, chromatic aberration, film grain, vignette, and iris / wipe / morph / glitch transitions — all as plain CSS classes. |
| **`js/text-animations.js`** | Ten kinetic-typography helpers: split-by-character, split-by-word, typewriter, scramble-decode, mask wipe, wave, text-on-path, count-up, animated gradient, staggered reveal. |
| **`templates/`** | Four self-contained HTML videos: `cinematic-product`, `kinetic-typo`, `brand-story`, `social-ad`. Open one, change the text and colours, done. |

## Quick start (30 seconds)

Everything is standalone HTML — no build step. GSAP loads from a CDN in each template.

```bash
git clone https://github.com/2boysfromtown/hyperframes-motion.git
cd hyperframes-motion
```

Open any file in `templates/` in your browser to preview it. To make your own, copy a template, then change the headline, the product icon and the brand colour:

```html
<h1 class="brand-logo">YOUR BRAND</h1>
<span class="product-icon">🎒</span>
```

```css
.tagline { color: #ff0080; }   /* your brand colour */
```

Each template is a real 1080×1920 web page, so you can record it to MP4 with any HTML-to-video method — a headless-Chrome screen capture, a screen recorder, or your own renderer.

### Use it from Claude Code

```bash
npx skills add 2boysfromtown/hyperframes-motion --global --agent claude-code
```

Then ask: *"Make a cinematic 9:16 product-reveal video for this headline and logo."* The skill (see [SKILL.md](SKILL.md)) tells Claude which template to copy and which effects to apply.

## The text-animation helpers

Pass a **CSS selector** to any helper:

```javascript
splitTextChars('.headline', { stagger: 0.05, duration: 0.8, ease: 'back.out(1.7)' });
typewriter('.subtitle',    { speed: 0.05 });
scrambleText('.code',      { duration: 1.5 });
maskReveal('.title',       { direction: 'left', duration: 1 });
countUp('.big-number',     { suffix: '+' });
```

If GSAP has not loaded, the helpers now leave your text readable instead of hiding it.

## Requirements

- A modern browser (Chromium recommended for recording).
- [GSAP](https://gsap.com) 3.x — already pulled from jsDelivr in every template; no install needed.
- To export to MP4: any HTML-to-video tool you like.

## Credits

- Animation engine: [GSAP](https://gsap.com) by Webflow (free core).
- Built for our own video pipeline at 2BFT and opened up for other creators.

---

Built by **[2BFT, Two Boys From Town](https://2bft.in)** — a free AI school from Vaniyambadi, Tamil Nadu. Follow [@navaratan.ai](https://instagram.com/navaratan.ai).

# Unified InsightSwarm Theme Specification
### Style Profile: Premium Hybrid Claymorphism

This specification outlines the typography, color tokens, claymorphic rules, and animations used to achieve the unified **InsightSwarm** UI. Share this with developers working on vanilla HTML/CSS/JS or other framework workspaces to maintain exact visual alignment.

---

## 1. Typography

Add the following Google Fonts imports to the `<head>` of your HTML document:
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet" />
```

* **Display/Header Font**: `'Space Grotesk'`, sans-serif (used for hero text, titles, card headers).
* **Body/Interface Font**: `'Inter'`, sans-serif (used for input values, descriptions, labels).

---

## 2. Color Palette (Tokens)

Use these variables in your root CSS stylesheet:

```css
:root {
  /* Brand Gradients & Accents */
  --color-accent: #2dd4bf;      /* Vibrant Teal */
  --color-accent-glow: #14b8a6; /* Glowing Teal */
  --color-accent-dim: #0d9488;  /* Deep Teal */

  /* Text Colors (High Contrast) */
  --color-text-primary: #f8fafc;   /* Slate 50 (Bright White-Gray) */
  --color-text-secondary: #cbd5e1; /* Slate 300 (Cool Light Gray) */
  --color-text-muted: #64748b;     /* Slate 500 (Cool Mid Gray) */

  /* Semantic Alerts */
  --color-error: #f87171;
  --color-error-bg: rgba(248, 113, 113, 0.12);
  --color-success: #4ade80;
  --color-success-bg: rgba(74, 222, 128, 0.12);

  /* Hybrid Midnight Base (Rich Dark Teal-Slate) */
  --color-clay-base: #081115;     /* Midnight Base Background */
  --color-clay-surface: #0e1a1e;  /* Deep Input Slate */
  --color-clay-card: #142429;     /* Container Card Slate */

  /* Decorative Neon Glows (Happy Pastels) */
  --blob-pink: rgba(254, 215, 215, 0.35);    /* Pastel Pink */
  --blob-teal: rgba(167, 234, 234, 0.35);    /* Pastel Mint/Teal */
  --blob-blue: rgba(191, 219, 254, 0.3);     /* Pastel Sky Blue */
}
```

---

## 3. Claymorphism Core Rules (CSS Specs)

Claymorphic elements rely on **soft double-inset shadows** combined with **prominent outer depth shadows** and light borders to create a realistic 3D pillowy look.

### A. The 3D Container Card (`.clay-card`)
A soft card container that pops off the dark background.
```css
.clay-card {
  background: linear-gradient(135deg, rgba(20, 32, 38, 0.92), rgba(12, 20, 24, 0.96));
  border: 1.5px solid rgba(45, 212, 191, 0.2); /* Soft teal boundary outline */
  border-radius: 28px;
  backdrop-filter: blur(25px);
  
  /* Double outer shadow + white inner clay reflection */
  box-shadow:
    16px 16px 36px rgba(0, 0, 0, 0.65),            /* Dark drop depth */
    -10px -10px 24px rgba(45, 212, 191, 0.02),      /* Teal ambient glow back */
    inset 0 1px 0 rgba(255, 255, 255, 0.06),        /* Top edge inner light highlight */
    inset 0 -1px 0 rgba(0, 0, 0, 0.4);              /* Bottom edge inner shadow */
    
  transition: all 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.clay-card:hover {
  transform: translateY(-2px);
  border-color: rgba(45, 212, 191, 0.45);          /* Intensify glow border */
  box-shadow:
    20px 20px 44px rgba(0, 0, 0, 0.75),
    -12px -12px 30px rgba(45, 212, 191, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.08),
    inset 0 -1px 0 rgba(0, 0, 0, 0.4);
}
```

### B. The Sunken Input Field (`.clay-input`)
Inputs use inverted inset shadows to simulate a carved, sunken field inside the card.
```css
.clay-input {
  background: linear-gradient(135deg, rgba(8, 14, 16, 0.95), rgba(12, 20, 24, 0.9));
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  color: var(--color-text-primary);
  padding: 16px 20px;
  outline: none;
  
  /* Inner shadow to carve the input downwards */
  box-shadow:
    inset 4px 4px 12px rgba(0, 0, 0, 0.6),
    inset -2px -2px 8px rgba(45, 212, 191, 0.03),
    0 1px 0 rgba(255, 255, 255, 0.04);
    
  transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.clay-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.clay-input:focus {
  border-color: var(--color-accent);
  box-shadow:
    inset 4px 4px 12px rgba(0, 0, 0, 0.6),
    inset -2px -2px 8px rgba(45, 212, 191, 0.04),
    0 0 0 3px rgba(45, 212, 191, 0.15); /* Active glow ring */
}
```

### C. The Tactile Action Button (`.clay-btn-primary`)
Vibrant color gradient button that acts as the focal CTA point.
```css
.clay-btn-primary {
  background: linear-gradient(135deg, var(--color-accent-glow), var(--color-accent));
  border: none;
  border-radius: 18px;
  color: var(--color-clay-base); /* High-contrast dark text on bright button */
  font-family: var(--font-display);
  font-weight: 600;
  padding: 16px 32px;
  cursor: pointer;
  letter-spacing: 0.02em;
  
  box-shadow:
    8px 8px 24px rgba(0, 0, 0, 0.4),
    -4px -4px 16px rgba(45, 212, 191, 0.08),
    inset 0 1px 0 rgba(255, 255, 255, 0.2),
    inset 0 -2px 0 rgba(0, 0, 0, 0.1);
    
  transition: all 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.clay-btn-primary:hover {
  transform: translateY(-2px) scale(1.015);
  box-shadow:
    10px 10px 28px rgba(0, 0, 0, 0.5),
    -6px -6px 20px rgba(45, 212, 191, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.25),
    0 0 30px rgba(45, 212, 191, 0.18);
}

.clay-btn-primary:active {
  transform: translateY(0) scale(0.985);
  box-shadow:
    4px 4px 16px rgba(0, 0, 0, 0.45),
    inset 0 2px 4px rgba(0, 0, 0, 0.2);
}
```

---

## 4. Background Glow Animations

To create the "happy vibes" glowing background, render 3 simple circular nodes under the main interface container styled as follows:

```html
<!-- HTML Structure -->
<div class="bg-blob bg-blob-1"></div>
<div class="bg-blob bg-blob-2"></div>
<div class="bg-blob bg-blob-3"></div>
<div class="noise-overlay"></div>
```

```css
/* CSS Classes */
.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(100px);
  pointer-events: none;
  z-index: 0;
}

.bg-blob-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, var(--blob-pink), transparent 70%);
  top: -200px;
  right: -100px;
  animation: float-blob 20s ease-in-out infinite;
}

.bg-blob-2 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, var(--blob-teal), transparent 70%);
  bottom: -150px;
  left: -100px;
  animation: float-blob 25s ease-in-out infinite reverse;
}

.bg-blob-3 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, var(--blob-blue), transparent 70%);
  top: 30%;
  left: 20%;
  animation: float-blob 30s ease-in-out infinite;
}

/* Floating animation path */
@keyframes float-blob {
  0%, 100% { transform: translate(0, 0) scale(1); }
  25% { transform: translate(30px, -40px) scale(1.05); }
  50% { transform: translate(-20px, 20px) scale(0.95); }
  75% { transform: translate(40px, 30px) scale(1.02); }
}

/* Overlay fine noise texture to blend banding colors premiumly */
.noise-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  opacity: 0.025;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}
```

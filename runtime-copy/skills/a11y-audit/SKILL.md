---
name: "a11y-audit"
description: "Accessibility audit skill for scanning, fixing, and verifying WCAG 2.2 Level A and AA compliance across React, Next.js, Vue, Angular, Svelte, and plain HTML codebases. Use when auditing accessibility, fixing a11y violations, checking color contrast, generating compliance reports, or integrating accessibility checks into CI."
---

# Accessibility Audit

WCAG 2.2 Accessibility Audit and Remediation Skill.

## Description

A complete accessibility audit pipeline for modern web applications. It implements a three-phase workflow — Scan, Fix, Verify — that identifies WCAG 2.2 Level A and AA violations, generates exact fix code per framework, and produces a compliance summary.

For every violation found, it provides a precise before/after code fix tailored to your framework (React, Next.js, Vue, Angular, Svelte, or plain HTML).

**What this skill does:**

1. **Scans** the codebase for WCAG 2.2 Level A and AA violations across 10 categories, classified by severity.
2. **Fixes** each violation with framework-specific before/after code patterns.
3. **Verifies** that fixes resolve the original violations and introduce no regressions (re-run the scanner).
4. **Reports** findings in a structured format (text or JSON).

## Features

| Feature | Description |
|---------|-------------|
| **WCAG 2.2 Scan** | Static checks across 10 categories of Level A and AA criteria |
| **Severity Classification** | critical / serious / moderate / minor |
| **Fix Patterns** | Before/after code per framework |
| **Color Contrast Checker** | Validates foreground/background pairs against AA and AAA ratios; can suggest accessible backgrounds |
| **Keyboard Audit** | Detects positive tabindex and click-without-keyboard handlers |
| **ARIA Validation** | Invalid attributes, aria-hidden on focusable elements, missing aria-live |

### Severity Definitions

| Severity | Definition | Example | SLA |
|----------|-----------|---------|-----|
| **critical** | Blocks access for entire user groups | Missing alt text, no keyboard access, empty link | Fix before release |
| **serious** | Significant barrier that degrades experience | Missing form labels, missing skip link, video without captions | Fix within current sprint |
| **moderate** | Usability issue causing friction | Skipped heading level, redundant ARIA, missing table caption | Fix within next 2 sprints |
| **minor** | Low-impact polish | Suboptimal but non-blocking patterns | Backlog |

> Exit codes: `0` = clean, `1` = critical or serious found, `2` = only moderate/minor found.

## Usage

### Quick Start

```bash
# Scan entire project (text report)
python scripts/a11y_scanner.py /path/to/project

# Scan with JSON output for tooling
python scripts/a11y_scanner.py /path/to/project --json

# Filter to blocking issues only
python scripts/a11y_scanner.py /path/to/project --severity critical,serious

# Check contrast for a specific pair (positional: foreground background)
python scripts/contrast_checker.py "#777777" "#ffffff"

# Suggest accessible backgrounds for a foreground color
python scripts/contrast_checker.py --suggest "#777777"

# Check every color/background pair in a CSS file
python scripts/contrast_checker.py --batch /path/to/styles.css
```

### Three-Phase Workflow

**Phase 1: Scan** — Walk the source tree, apply the rule set, classify by severity.

```bash
python scripts/a11y_scanner.py /path/to/project --json > a11y-results.json
```

**Phase 2: Fix** — Apply framework-specific fixes for each violation.

> See [references/framework-a11y-patterns.md](references/framework-a11y-patterns.md) for the complete fix-patterns catalog, and [references/examples-by-framework.md](references/examples-by-framework.md) for full per-framework audit examples.

**Phase 3: Verify** — Re-run the scanner and confirm the issues are gone and no new ones appeared.

```bash
python scripts/a11y_scanner.py /path/to/project --json
```

## Example: React Component Audit

```tsx
// BEFORE
function ProductCard({ product }) {
  return (
    <div onClick={() => navigate(`/product/${product.id}`)}>
      <img src={product.image} />
      <div style={{ color: '#aaa', fontSize: '12px' }}>{product.name}</div>
      <span style={{ color: '#999' }}>${product.price}</span>
    </div>
  );
}
```

| # | WCAG | Severity | Issue |
|---|------|----------|-------|
| 1 | 1.1.1 | critical | `<img>` missing `alt` attribute |
| 2 | 2.1.1 | critical | `<div onClick>` not keyboard accessible |
| 3 | 1.4.3 | serious | Color `#aaa` on white fails contrast (2.32:1, needs 4.5:1) |
| 4 | 1.4.3 | serious | Color `#999` on white fails contrast (2.85:1, needs 4.5:1) |
| 5 | 4.1.2 | serious | Interactive element missing role and accessible name |

```tsx
// AFTER
function ProductCard({ product }) {
  return (
    <a href={`/product/${product.id}`} className="product-card"
       aria-label={`View ${product.name} - $${product.price}`}>
      <img src={product.image} alt={product.imageAlt || product.name} />
      <div style={{ color: '#595959', fontSize: '12px' }}>{product.name}</div>
      <span style={{ color: '#767676' }}>${product.price}</span>
    </a>
  );
}
```

## Tools Reference

### a11y_scanner.py

```
Usage: python scripts/a11y_scanner.py <path> [options]

Positional:
  path                          File or directory to scan

Options:
  --json                        Output results as JSON
  --format {text,json}          Output format (default: text)
  --severity LIST               Comma-separated filter, e.g. critical,serious

Supported file types: .html .htm .jsx .tsx .vue .svelte .css
Exit codes: 0 = pass, 1 = critical/serious found, 2 = moderate/minor only
```

### contrast_checker.py

```
Usage: python scripts/contrast_checker.py [foreground] [background] [options]

Positional (single-pair mode):
  foreground                    Text color: #RRGGBB, #RGB, rgb(r,g,b), or named
  background                    Background color (same formats)

Options:
  --suggest COLOR               Suggest accessible backgrounds for a foreground
  --batch CSS_FILE              Extract and check color pairs from a CSS file
  --json                        Output results as JSON
  --demo                        Show example output with sample color pairs
```

## Common Pitfalls

| Pitfall | Correct Approach |
|---------|------------------|
| `role="button"` on a `<div>` | Use native `<button>` — keyboard handling for free |
| `tabindex="0"` on everything | Only interactive elements need focus; use native elements |
| `aria-label` on non-interactive elements | Use `aria-labelledby` pointing to visible text |
| `display: none` for screen-reader hiding | Use an `.sr-only` class instead |
| Color alone to convey meaning | Add icons, text labels, or patterns alongside color |
| Placeholder as only label | Always provide a visible `<label>` |
| `outline: none` without replacement | Provide a visible focus indicator via `:focus-visible` |
| Empty `alt=""` on informational images | Informational images need descriptive alt text |
| Skipping heading levels (h1 → h3) | Heading levels must be sequential |
| `onClick` without `onKeyDown` | Add keyboard support or prefer native elements |
| Ignoring `prefers-reduced-motion` | Wrap animations in `@media (prefers-reduced-motion: no-preference)` |

## Reference Documentation

| Reference | Description |
|-----------|-------------|
| [wcag-quick-ref.md](references/wcag-quick-ref.md) | WCAG 2.2 Level A & AA criteria quick reference |
| [wcag-22-new-criteria.md](references/wcag-22-new-criteria.md) | New WCAG 2.2 criteria (Focus Appearance, Target Size, etc.) |
| [aria-patterns.md](references/aria-patterns.md) | ARIA patterns, keyboard interaction, live regions |
| [framework-a11y-patterns.md](references/framework-a11y-patterns.md) | Framework fix patterns (React, Vue, Angular, Svelte, HTML) |
| [examples-by-framework.md](references/examples-by-framework.md) | Full audit examples for Vue, Angular, Next.js, Svelte |
| [color-contrast-guide.md](references/color-contrast-guide.md) | Contrast details, Tailwind palette mapping, sr-only class |
| [audit-report-template.md](references/audit-report-template.md) | Audit report template |
| [testing-checklist.md](references/testing-checklist.md) | Manual testing checklist (keyboard, screen reader, visual, forms) |

## Resources

- WCAG 2.2 Specification — https://www.w3.org/TR/WCAG22/
- WAI-ARIA Authoring Practices 1.2 — https://www.w3.org/WAI/ARIA/apg/
- eslint-plugin-jsx-a11y — https://github.com/jsx-eslint/eslint-plugin-jsx-a11y

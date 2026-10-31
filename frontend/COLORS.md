# Verity colour system

`src/theme.css` owns the UI palette and the light/dark equivalents. Import it
before component and workspace styles. Use the same roles in new components:

| Role | Use |
| --- | --- |
| `--brand`, `--brand-paper`, `--brand-sage` | Deep teal, ivory and sage brand artwork |
| `--action`, `--action-hover`, `--on-brand` | Primary controls |
| `--ink`, `--muted`, `--link` | Text and navigation |
| `--surface`, `--surface-muted`, `--canvas`, `--line` | Panels, page backgrounds and borders |
| `--success`, `--success-bg`, `--success-border` | Verified, passed, completed |
| `--warning`, `--warning-bg`, `--warning-border` | Pending, review, caution |
| `--danger`, `--danger-bg`, `--danger-border` | Failed, rejected, blocked, errors |
| `--info`, `--info-bg`, `--info-border` | Guidance and informational checks |
| `--focus`, `--focus-ring` | Keyboard focus and focused inputs |

Use the foreground/background/border trio together. Use `--success-solid` or
`--danger-solid` with `--on-brand` for filled decision buttons; status text
colours become lighter in dark mode and must not be used as white-text fills.

Keep status text or icons alongside colour. Score bars show an assessment as
well as their number and colour. Model-chart intensity describes a share, not
a verification decision. Brand illustrations and camera overlays retain their
own artwork colours; the public landing page intentionally stays ivory.

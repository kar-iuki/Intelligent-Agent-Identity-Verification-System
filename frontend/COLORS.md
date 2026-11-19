# Verity colour system

`src/theme.css` owns the UI palette and the light/dark equivalents. Import it
before component and workspace styles. Use the same roles in new components:

| Role | Use |
| --- | --- |
| `--brand`, `--brand-paper`, `--brand-sage` | Forest green, pale paper and lime accents for artwork and highlights |
| `--action`, `--action-hover`, `--on-brand`, `--action-border` | Primary controls with white labels and a visible edge on dark panels |
| `--ink`, `--muted`, `--link` | Text and navigation |
| `--surface`, `--surface-muted`, `--canvas`, `--line` | Panels, page backgrounds and borders |
| `--success`, `--success-bg`, `--success-border` | Verified, passed, completed |
| `--warning`, `--warning-bg`, `--warning-border` | Pending, review, caution |
| `--danger`, `--danger-bg`, `--danger-border` | Failed, rejected, blocked, errors |
| `--info`, `--info-bg`, `--info-border` | Guidance and informational checks |
| `--focus`, `--focus-ring` | Keyboard focus and focused inputs |

Use the action colours for primary buttons, including approvals. Use the
danger colours for destructive actions and the status colour trios for outcomes.

Keep status text or icons alongside colour. Score bars show an assessment as
well as their number and colour. Model-chart intensity describes a share, not
a verification decision. Brand illustrations and camera overlays retain their
own artwork colours; the public landing page uses a fixed dark hero and light document guide.

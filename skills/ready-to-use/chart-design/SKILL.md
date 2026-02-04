---
name: chart-design
description: Apple HIG-inspired principles for effective data visualization. Use automatically when creating charts, graphs, or visualizations in reports, web apps, dashboards, or presentations. Applies to any charting technology (matplotlib, Chart.js, D3, Recharts, etc.). Ensures charts are focused, approachable, and accessible.
---

# Chart Design Principles

Design every chart to be **focused** (one clear message), **approachable** (context before complexity), and **accessible** (works for all users).

## Chart Type Selection

| Type | Best For | Key Strength |
|------|----------|--------------|
| **Bars** | Comparisons, rankings, categories | Shows zeros clearly; most flexible |
| **Lines** | Trends, rates of change, time series | Reveals patterns and inflection points |
| **Points** | Correlations, outliers, clusters | Identifies relationships and anomalies |

Default to bars when uncertain. Reserve novel chart types for central features only.

## Essential Elements

**Title**: States what the chart shows (not how to read it)
**Summary stat**: The key takeaway as a number ("Total: 1,234" or "Up 12%")
**Axis labels**: Use intuitive intervals (multiples of 10, 20, 25—never 17 or 23)

## Axis Ranges

- **Fixed**: When data has natural bounds (battery: 0-100%, satisfaction: 1-5)
- **Dynamic**: When no meaningful maximum exists (revenue, page views, steps)

## Color Rules

1. **Never rely on color alone**—pair with symbols, patterns, or labels
2. **Limit palette**—2-4 distinct colors maximum; one dominant, rest subordinate
3. **Cultural awareness**—red/green meanings vary; avoid for good/bad without symbols
4. **Balance visual weight**—equal saturation across categories unless hierarchy intended
5. **Test accessibility**—verify contrast ratios; check with colorblind simulation

## Progressive Disclosure

Match chart complexity to context:

| Context | Approach |
|---------|----------|
| Dashboard widget | Sparkline or mini-chart; no axes; click to expand |
| Report section | Full axes and labels; summary in title; hover for details |
| Deep analysis | Multiple perspectives; filters; drill-down capability |

## Multi-Chart Systems

When showing multiple charts together:
- Use consistent colors for the same data across charts
- Vary chart type to signal different data (bars → lines = different measure)
- Maintain visual continuity when expanding from preview to detail

## Quick Checklist

Before finalising any chart:
- [ ] One clear message (not three insights crammed together)
- [ ] Title + summary stat present
- [ ] Color not sole differentiator
- [ ] Axis labels at intuitive intervals
- [ ] High contrast between marks and background

# David-Specific Skills (Not Included)

These skills are part of David's setup but aren't included in this repository because they're highly specific to personal workflows or client projects.

## Why Not Included

| Skill | Reason |
|-------|--------|
| Client-branded document skills | Client-specific branding, typography, and colour rules |
| `diary` + `reflect` | Session diary pipeline — diary Step 4b auto-extracts `[LEARN:category]` corrections to MEMORY.md Corrections Log, `/reflect` analyses patterns across entries |
| `diary-from-transcripts` | Specific to OMI/Otter transcript processing workflow |
| `update-ibiza-demand` | Project-specific data pipeline |
| `transcripts-to-html` | Specific transcript archive format |
| `remotion-video` | Complex Remotion setup beyond this repo's scope |
| `generate-shortcuts-skill` | macOS/iOS Shortcuts plist generation (very niche) |

## If You Want Something Similar

### Client-Branded Documents

Create your own branded document skills:

1. Copy `docx` or `pptx` as a starting point
2. Add your client's brand guidelines (fonts, colours, spacing)
3. Name it `client-docx` or similar

See the `docx` skill's template selection logic for how to auto-detect client context.

### Diary/Transcript Processing

If you use voice recording apps (OMI, Otter, etc.):

1. Identify where your transcripts are stored
2. Create a skill that reads transcripts and formats them
3. Add your preferred diary structure

The pattern: read source files → extract relevant content → format into desired output.

### Project-Specific Pipelines

For recurring data pipelines:

1. Document the steps manually first
2. Create a skill that encapsulates those steps
3. Add day-of-week or other contextual logic

The `update-ibiza-demand` skill, for example, detects Monday vs other days to run different pipeline variants.

### Video Generation

For Remotion-based video:

1. Set up Remotion separately: `npm create video@latest`
2. Build your video components in the Remotion project
3. Create a skill that generates/updates the component files

This is substantial work — consider if simpler alternatives (screen recording, Canva) meet your needs first.

## Contact

If you're curious about any of these skills, ask David directly. Some may be shareable with context; others are truly specific to personal workflows.

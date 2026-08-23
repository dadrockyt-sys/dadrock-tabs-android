# DadRock AI Tab Final-Product PDF Architecture

This directory is the inactive construction home for final professional TAB rendering.

```text
pdf/final_product/
  shared/
  rhythm/
  lead/
  bass/
```

The renderer split mirrors the analyzer split:

- `shared/` contains only instrument-agnostic PDF/layout primitives.
- `rhythm/` owns professional six-string Rhythm engraving.
- `lead/` owns professional six-string Lead engraving.
- `bass/` owns professional four-string Bass engraving.

Preview and purchased/full PDF must consume the same authenticated analysis for the selected instrument. No renderer may invent missing measure, subdivision, pitch, string/fret, or technique evidence merely to produce a visually complete page.

Nothing in this directory is active by existence alone. Existing proven routes/renderers stay unchanged until a separately validated migration/activation step.

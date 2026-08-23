# Shared Professional PDF Core

Only instrument-agnostic rendering primitives belong here, such as page sizing, typography, title/metadata blocks, measure spacing helpers, common headers/footers, preview/full-page policies, and safe evidence labels.

Do not encode string counts, tuning, fret limits, instrument-specific technique symbols, or analyzer identities here unless they are supplied explicitly by the selected instrument renderer.

Shared PDF code must never infer missing musical placement.

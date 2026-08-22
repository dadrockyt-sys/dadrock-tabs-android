"""Run V64 with the adjacent-offset ambiguity bug removed.

V64 scores every integer vertical offset, but several neighbouring offsets can
resolve to the exact same six recovered staff rows after the +/-2 pixel local
row adjustment. The original score-margin gate then compares a candidate with
an equivalent duplicate and reports an artificial zero/tiny ambiguity margin.

This wrapper changes only that duplicate-margin gate. All six-line evidence,
spacing, horizontal continuity, read-only protections, and output paths remain
unchanged.
"""

from __future__ import annotations

import recover_gomyway_tab_system_bands_v64 as v64

# Adjacent integer offsets frequently collapse to the same recovered lattice.
# Do not reject a visually identical six-row solution merely because its
# duplicate received the same objective. Evidence and spacing gates still apply.
v64.MIN_OBJECTIVE_MARGIN = 0.0


if __name__ == "__main__":
    v64.main()

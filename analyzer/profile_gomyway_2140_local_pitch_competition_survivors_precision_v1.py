from __future__ import annotations

# Corrected runner for the validated local-pitch-competition champion.
# The underlying validated counts are 183 / 684 / 660, which grade to
# Pitch F1 21.40 (the earlier 21.44 label was a transcription mistake).
# Keep the original implementation intact for auditability and override
# only the expected F1 label before running it.

import profile_gomyway_2144_local_pitch_competition_survivors_precision_v1 as legacy

legacy.EXPECTED_F1 = 21.40

if __name__ == "__main__":
    legacy.main()

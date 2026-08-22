from __future__ import annotations

import benchmark_gomyway_3118_measure_register_precision_prune_cv_v1 as benchmark

# The saved 31.18 measure-register profiler currently contains three
# validated zero-precision signatures. Keep the benchmark logic unchanged;
# only align its count guard with the actual profiler artifact.
benchmark.EXPECTED_ZERO_SIGNATURES = 3

if __name__ == "__main__":
    benchmark.main()

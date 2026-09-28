# Astra source-domain V3 synthetic training arming decision V1

Date: 2026-09-28
Status: **GO — ONE FINAL SYNTHETIC TRAINING ATTEMPT**

The prospective V3 training design and execution package passed offline verification with zero optimizer steps.

Launch identity:
`source-domain-v3-training-20260928-canonical-01`

Frozen inputs:
- S9 control SHA-256 `16123bfab56050e355e424be0050b11e6447b24c32c105da86c0ec971d599894`
- V2 intervention SHA-256 `a17a16daeb8d698e325dc6820f18d5eda2fec75d9beebe2a9605a678124dc26b`
- V3 challenge SHA-256 `368032e81722a4ca97bf2ec81b432b90ef2fc982cac20c8bd543d34f514d9bce`
- offline verification run 36489377119 / artifact 11001326153 / receipt SHA-256 `02ea4fa1928024a010b790fce66514961212cd65be0b05df98dfe6fcaccedf41`

Execution:
- exact frozen S11 architecture/loss/sampler;
- seeds 20260927, 20260928, 20260929;
- two paired arms per seed;
- 500 optimizer steps/model;
- six models / 3,000 steps total;
- fixed thresholds 0.50/0.50;
- no threshold search/retuning;
- CPU only / paid compute $0;
- P1/P2/P3 access false;
- automatic retry false;
- run attempt must equal 1;
- main/Production unchanged.

The frozen V1 scientific gate is reused without weakening.

If this synthetic gate passes, stop at the fresh real-domain authorization boundary.
If it fails, freeze failure and do not run another source-domain synthetic redesign/model experiment automatically.

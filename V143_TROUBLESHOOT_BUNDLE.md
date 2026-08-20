# V143 Troubleshooting Bundle

Generated: 2026-08-20T05:57:07.053096+00:00

Purpose: remote troubleshooting of the V143 musical reconstruction calibration branch without opening professional-reference or untouched holdout contents.


## Git state

```text
branch: v143-musical-reconstruction-calibration
HEAD: b20e9df253fa931621fb56a3b24a29a27d483d3b
last commit: b20e9df2 Reject V143 sequence selector after frozen 17-96 evaluation

M analyzer/v143_intro_kong_pitch_benchmark.py
 M analyzer/v143_intro_synthtab_tabcnn_benchmark.py
 M app/ai-tab/page.js
 M app/api/analyze-audio-tab/route.js
 M app/api/generate-tab-pdf/route.js
 M app/api/generate-tab-preview/route.js
 M lib/v143RenderContract.js
 M yarn.lock
?? .venv-jimmy311/
?? analyzer/benchmark_gomyway_2476_harmonic_template_competition_precision_prune_cv_v1.py
?? analyzer/benchmark_gomyway_separator_upgrade_v2_forensic_replay.py
?? analyzer/build_gomyway_effective_activation_bounds_v2.py
?? analyzer/build_gomyway_full_song_measure_bounds_v1.py
?? analyzer/build_jimmy_paige_v134_midterm_blind_113_v1.py
?? analyzer/build_jimmy_paige_v134_midterm_blind_113_v2.py
?? analyzer/build_v143_modal_selector_verified.py
?? analyzer/compare_v143_historical_vs_modal_candidate.py
?? analyzer/compare_v143_modal_direct_downstream.py
?? analyzer/evaluate_v143_modal_finalfit.py
?? analyzer/evaluate_v143_production_finalfit.py
?? analyzer/export_v143_production_policy.py
?? analyzer/extract_gomyway_chorus_candidate_activation_v1.py
?? analyzer/extract_gomyway_chorus_candidate_activation_v2.py
?? analyzer/extract_gomyway_percussive_audio_evidence.py
?? analyzer/extract_gomyway_percussive_hpss_evidence_v6.py
?? analyzer/extract_gomyway_percussive_multiwindow_evidence_v5.py
?? analyzer/fit_v143_modal_candidate.py
?? analyzer/fit_v143_production_model.py
?? analyzer/launch_jimmy_midterm_resilient.py
?? analyzer/replay_v143_historical_demucs_defaults.py
?? analyzer/replay_v143_production_separator.py
?? analyzer/run_gomyway_chorus_activation_section_holdout_v1.py
?? analyzer/run_gomyway_chorus_phrase_position_consensus_v1.py
?? analyzer/run_gomyway_chorus_soft_evidence_ranking_v1.py
?? analyzer/run_gomyway_fullmix_rhythm_candidate_benchmark_v1.py
?? analyzer/run_gomyway_layered_reference_precision_benchmark_v1.py
?? analyzer/run_gomyway_layered_reference_precision_benchmark_v2.py
?? analyzer/run_gomyway_layered_rhythm_reconciliation_v1.py
?? analyzer/run_gomyway_layered_rhythm_reconciliation_v2.py
?? analyzer/run_gomyway_layered_section_holdout_benchmark_v1.py
?? analyzer/run_gomyway_other_stem_rhythm_candidate_benchmark_v1.py
?? analyzer/run_gomyway_repeated_chorus_soft_ranking_v1.py
?? analyzer/run_jimmy_paige_v134_blind_113_measure_midterm_v1.py
?? analyzer/run_jimmy_paige_v134_corrected_113_measure_midterm_v2.py
?? analyzer/score_jimmy_midterm_113_measure_v1.py
?? analyzer/search_gomyway_percussive_context_gates_v4.py
?? analyzer/test_gomyway_percussive_rhythm_classifier_v3.py
?? analyzer/v143_ai_tab_cpu_provenance.py
?? analyzer/v143_ai_tab_gpu_worker_historical_defaults.py
?? analyzer/v143_modal_domain_training_only.py
?? analyzer/v143_section2_duration_state_capture.py
?? analyzer/v143_section2_mix_contrast_capture.py
?? analyzer/v143_section2_transient_state_capture.py
?? analyzer/v143_section3_duration_state_capture.py
?? analyzer/v143_section3_mix_contrast_capture.py
?? analyzer/v143_section3_transient_state_capture.py
?? analyzer/v143_seeded_audio_separator.py
?? analyzer/watch_jimmy_midterm.py
?? "command: False\""
?? e
?? jimmy-paige-chorus-activation-heartbeat.log
?? jimmy-paige-midterm-heartbeat.log
?? jimmy-paige-v134-corrected-midterm-v2-heartbeat.log
?? "nset-slot-spectro-temporal-patch-stability-v1.json' "
?? "opened : False\""
?? public/gomyway-1113-recall-champion-effective-additions-precision-v1-manifest.json
?? public/gomyway-1113-recall-champion-effective-additions-precision-v1.json
?? public/gomyway-1113-recall-champion-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1113-recall-champion-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1163-champion-second-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1163-champion-second-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1163-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1163-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1186-champion-third-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1186-champion-third-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1186-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1186-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1217-champion-fourth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1217-champion-fourth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1217-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1217-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1229-champion-fifth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1229-champion-fifth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1229-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1229-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1244-champion-sixth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1244-champion-sixth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1244-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1244-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1253-champion-seventh-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1253-champion-seventh-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1253-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1253-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1258-champion-eighth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1258-champion-eighth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1258-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1258-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1272-champion-ninth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1272-champion-ninth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1272-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1272-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1285-champion-tenth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1285-champion-tenth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1285-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1285-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1305-champion-eleventh-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1305-champion-eleventh-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1305-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1305-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1308-champion-twelfth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1308-champion-twelfth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1308-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1308-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1312-champion-thirteenth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1312-champion-thirteenth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1312-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1312-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1315-champion-fourteenth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1315-champion-fourteenth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1315-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1315-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1316-champion-fifteenth-zero-precision-pitch-strength-prune-v1-manifest.json
?? public/gomyway-1316-champion-fifteenth-zero-precision-pitch-strength-prune-v1.json
?? public/gomyway-1316-champion-finer-cross-signatures-v1-manifest.json
?? public/gomyway-1316-champion-finer-cross-signatures-v1.json
?? public/gomyway-1316-champion-finer-score-agreement-cross-signature-gate-v1-manifest.json
?? public/gomyway-1316-champion-finer-score-agreement-cross-signature-gate-v1.json
?? public/gomyway-1316-pruned-recall-champion-residual-additions-precision-v1-manifest.json
?? public/gomyway-1316-pruned-recall-champion-residual-additions-precision-v1.json
?? public/gomyway-1328-champion-finer-cross-signatures-v1-manifest.json
?? public/gomyway-1328-champion-finer-cross-signatures-v1.json
?? public/gomyway-1328-champion-section-step-pitch-score-agreement-gate-v1-manifest.json
?? public/gomyway-1328-champion-section-step-pitch-score-agreement-gate-v1.json
?? public/gomyway-1345-champion-finer-cross-signatures-v1-manifest.json
?? public/gomyway-1345-champion-finer-cross-signatures-v1.json
?? public/gomyway-1345-champion-narrow-score-agreement-gate-v1-manifest.json
?? public/gomyway-1345-champion-narrow-score-agreement-gate-v1.json
?? public/gomyway-1370-champion-finer-cross-signatures-v1-manifest.json
?? public/gomyway-1370-champion-finer-cross-signatures-v1.json
?? public/gomyway-1370-champion-micro-score-singleton-gate-v1-manifest.json
?? public/gomyway-1370-champion-micro-score-singleton-gate-v1.json
?? public/gomyway-1382-champion-broadband-onset-flux-pocket-recall-gate-v1-manifest.json
?? public/gomyway-1382-champion-broadband-onset-flux-pocket-recall-gate-v1.json
?? public/gomyway-1382-champion-cached-onset-fundamental-joint-gate-v1-manifest.json
?? public/gomyway-1382-champion-cached-onset-fundamental-joint-gate-v1.json
?? public/gomyway-1382-champion-dual-stem-local-prominence-recall-gate-v1-manifest.json
?? public/gomyway-1382-champion-dual-stem-local-prominence-recall-gate-v1.json
?? public/gomyway-1382-champion-dual-stem-recurrence-recall-gate-v1-manifest.json
?? public/gomyway-1382-champion-dual-stem-recurrence-recall-gate-v1.json
?? public/gomyway-1382-champion-finer-cross-signatures-v1-manifest.json
?? public/gomyway-1382-champion-finer-cross-signatures-v1.json
?? public/gomyway-1382-champion-missing-reference-opportunities-v1-manifest.json
?? public/gomyway-1382-champion-missing-reference-opportunities-v1.json
?? public/gomyway-1382-champion-temporal-attack-pocket-recall-gate-v1-manifest.json
?? public/gomyway-1382-champion-temporal-attack-pocket-recall-gate-v1.json
?? public/gomyway-1382-dual-stem-broadband-onset-evidence-v1-manifest.json
?? public/gomyway-1382-dual-stem-broadband-onset-evidence-v1.json
?? public/gomyway-1382-dual-stem-fundamental-overtone-evidence-v1-manifest.json
?? public/gomyway-1382-dual-stem-fundamental-overtone-evidence-v1.json
?? public/gomyway-1382-dual-stem-temporal-attack-evidence-v1-manifest.json
?? public/gomyway-1382-dual-stem-temporal-attack-evidence-v1.json
?? public/gomyway-1382-never-seen-raw-spectral-evidence-v1-manifest.json
?? public/gomyway-1382-never-seen-raw-spectral-evidence-v1.json
?? public/gomyway-1382-onset-fundamental-joint-evidence-v1-manifest.json
?? public/gomyway-1382-onset-fundamental-joint-evidence-v1.json
?? public/gomyway-1417-champion-cached-joint-false-addition-prune-v1-manifest.json
?? public/gomyway-1417-champion-cached-joint-false-addition-prune-v1.json
?? public/gomyway-1417-champion-joint-recall-addition-details-v1-manifest.json
?? public/gomyway-1417-champion-joint-recall-addition-details-v1.json
?? public/gomyway-1417-champion-joint-recall-additions-profile-v1-manifest.json
?? public/gomyway-1417-champion-joint-recall-additions-profile-v1.json
?? public/gomyway-1419-cached-harmonic-chord-completion-v1-manifest.json
?? public/gomyway-1419-cached-harmonic-chord-completion-v1.json
?? public/gomyway-1419-cached-local-note-context-v1-manifest.json
?? public/gomyway-1419-cached-local-note-context-v1.json
?? public/gomyway-1419-cached-long-range-step-pitch-repetition-v1-manifest.json
?? public/gomyway-1419-cached-long-range-step-pitch-repetition-v1.json
?? public/gomyway-1419-cached-pitch-periodicity-gate-v1-manifest.json
?? public/gomyway-1419-cached-pitch-periodicity-gate-v1.json
?? public/gomyway-1419-cached-post-attack-sustain-evidence-v1-manifest.json
?? public/gomyway-1419-cached-post-attack-sustain-evidence-v1.json
?? public/gomyway-1419-cached-recur-distinct-structure-v1-manifest.json
?? public/gomyway-1419-cached-recur-distinct-structure-v1.json
?? public/gomyway-1419-cached-structural-joint-cross-signatures-v1-manifest.json
?? public/gomyway-1419-cached-structural-joint-cross-signatures-v1.json
?? public/gomyway-1419-cached-top-structural-joint-pocket-details-v1-manifest.json
?? public/gomyway-1419-cached-top-structural-joint-pocket-details-v1.json
?? public/gomyway-1419-champion-cached-family-b-recur13-gate-v1-manifest.json
?? public/gomyway-1419-champion-cached-family-b-recur13-gate-v1.json
?? public/gomyway-1419-champion-cached-repeatable-residual-joint-gate-v1-manifest.json
?? public/gomyway-1419-champion-cached-repeatable-residual-joint-gate-v1.json
?? public/gomyway-1419-champion-cached-residual-joint-opportunities-v1-manifest.json
?? public/gomyway-1419-champion-cached-residual-joint-opportunities-v1.json
?? public/gomyway-1419-champion-cached-residual-union-addition-details-v1-manifest.json
?? public/gomyway-1419-champion-cached-residual-union-addition-details-v1.json
?? public/gomyway-1419-dual-stem-pitch-periodicity-residual-v1-manifest.json
?? public/gomyway-1419-dual-stem-pitch-periodicity-residual-v1.json
?? public/gomyway-1419-dual-stem-spectral-shape-residual-v1-manifest.json
?? public/gomyway-1419-dual-stem-spectral-shape-residual-v1.json
?? public/gomyway-1419-source-categorical-evidence-inventory-v1-manifest.json
?? public/gomyway-1419-source-categorical-evidence-inventory-v1.json
?? public/gomyway-1419-source-confidence-duration-residual-v1-manifest.json
?? public/gomyway-1419-source-confidence-duration-residual-v1.json
?? public/gomyway-1419-source-detector-event-evidence-inventory-v1-manifest.json
?? public/gomyway-1419-source-detector-event-evidence-inventory-v1.json
?? public/gomyway-1419-source-remaining-native-evidence-inventory-v1-manifest.json
?? public/gomyway-1419-source-remaining-native-evidence-inventory-v1.json
?? public/gomyway-1419-source-starts-residual-agreement-v1-manifest.json
?? public/gomyway-1419-source-starts-residual-agreement-v1.json
?? public/gomyway-1419-source-strength-evidence-inventory-v1-manifest.json
?? public/gomyway-1419-source-strength-evidence-inventory-v1.json
?? public/gomyway-1430-cached-periodicity-precision-prune-cv-v2-manifest.json
?? public/gomyway-1430-cached-periodicity-precision-prune-cv-v2.json
?? public/gomyway-1430-cached-periodicity-zero-precision-prune-v1-manifest.json
?? public/gomyway-1430-cached-periodicity-zero-precision-prune-v1.json
?? public/gomyway-1430-periodicity-champion-additions-precision-v1-manifest.json
?? public/gomyway-1430-periodicity-champion-additions-precision-v1.json
?? public/gomyway-1430-zero-precision-prune-cross-validation-failures-v1-manifest.json
?? public/gomyway-1430-zero-precision-prune-cross-validation-failures-v1.json
?? public/gomyway-1444-cached-periodicity-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1444-cached-periodicity-survivor-precision-prune-cv-v1.json
?? public/gomyway-1444-periodicity-survivor-additions-precision-v1-manifest.json
?? public/gomyway-1444-periodicity-survivor-additions-precision-v1.json
?? public/gomyway-1448-periodicity-survivor-additions-precision-v1-manifest.json
?? public/gomyway-1448-periodicity-survivor-additions-precision-v1.json
?? public/gomyway-1448-periodicity-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1448-periodicity-survivor-precision-prune-cv-v1.json
?? public/gomyway-1451-periodicity-survivor-additions-precision-v1-manifest.json
?? public/gomyway-1451-periodicity-survivor-additions-precision-v1.json
?? public/gomyway-1451-periodicity-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1451-periodicity-survivor-precision-prune-cv-v1.json
?? public/gomyway-1454-broad-champion-extras-cross-signatures-v1-manifest.json
?? public/gomyway-1454-broad-champion-extras-cross-signatures-v1.json
?? public/gomyway-1454-broad-score-agreement-precision-prune-cv-v1-manifest.json
?? public/gomyway-1454-broad-score-agreement-precision-prune-cv-v1.json
?? public/gomyway-1454-periodicity-survivor-additions-precision-v1-manifest.json
?? public/gomyway-1454-periodicity-survivor-additions-precision-v1.json
?? public/gomyway-1460-attack-envelope-precision-prune-cv-v1-manifest.json
?? public/gomyway-1460-attack-envelope-precision-prune-cv-v1.json
?? public/gomyway-1460-broad-champion-extras-cross-signatures-v1-manifest.json
?? public/gomyway-1460-broad-champion-extras-cross-signatures-v1.json
?? public/gomyway-1460-dual-stem-attack-envelope-v1-manifest.json
?? public/gomyway-1460-dual-stem-attack-envelope-v1.json
?? public/gomyway-1499-attack-envelope-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1499-attack-envelope-survivor-precision-prune-cv-v1.json
?? public/gomyway-1499-attack-envelope-survivors-precision-v1-manifest.json
?? public/gomyway-1499-attack-envelope-survivors-precision-v1.json
?? public/gomyway-1542-attack-envelope-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1542-attack-envelope-survivor-precision-prune-cv-v1.json
?? public/gomyway-1542-attack-envelope-survivors-precision-v1-manifest.json
?? public/gomyway-1542-attack-envelope-survivors-precision-v1.json
?? public/gomyway-1569-attack-envelope-final-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1569-attack-envelope-final-survivor-precision-prune-cv-v1.json
?? public/gomyway-1569-attack-envelope-survivors-precision-v1-manifest.json
?? public/gomyway-1569-attack-envelope-survivors-precision-v1.json
?? public/gomyway-1590-dual-stem-harmonic-comb-coherence-v1-manifest.json
?? public/gomyway-1590-dual-stem-harmonic-comb-coherence-v1.json
?? public/gomyway-1590-harmonic-comb-precision-prune-cv-v1-manifest.json
?? public/gomyway-1590-harmonic-comb-precision-prune-cv-v1.json
?? public/gomyway-1652-harmonic-comb-final-survivor-precision-prune-cv-v1-manifest.json
?? public/gomyway-1652-harmonic-comb-final-survivor-precision-prune-cv-v1.json
?? public/gomyway-1652-harmonic-comb-survivors-precision-v1-manifest.json
?? public/gomyway-1652-harmonic-comb-survivors-precision-v1.json
?? public/gomyway-1661-dual-stem-temporal-pitch-persistence-v1-manifest.json
?? public/gomyway-1661-dual-stem-temporal-pitch-persistence-v1.json
?? public/gomyway-1661-temporal-pitch-persistence-precision-prune-cv-v1-manifest.json
?? public/gomyway-1661-temporal-pitch-persistence-precision-prune-cv-v1.json
?? public/gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1-manifest.json
?? public/gomyway-1694-dual-stem-octave-subharmonic-discrimination-v1.json
?? public/gomyway-1694-octave-subharmonic-precision-prune-cv-v1-manifest.json
?? public/gomyway-1694-octave-subharmonic-precision-prune-cv-v1.json
?? public/gomyway-1694-temporal-pitch-persistence-survivors-precision-v1-manifest.json
?? public/gomyway-1694-temporal-pitch-persistence-survivors-precision-v1.json
?? public/gomyway-1750-dual-stem-pitch-specific-onset-contrast-v1-manifest.json
?? public/gomyway-1750-dual-stem-pitch-specific-onset-contrast-v1.json
?? public/gomyway-1750-octave-subharmonic-survivors-precision-v1-manifest.json
?? public/gomyway-1750-octave-subharmonic-survivors-precision-v1.json
?? public/gomyway-1750-pitch-specific-onset-precision-prune-cv-v1-manifest.json
?? public/gomyway-1750-pitch-specific-onset-precision-prune-cv-v1.json
?? public/gomyway-1813-dual-stem-harmonic-occupancy-inharmonic-residual-v1-manifest.json
?? public/gomyway-1813-dual-stem-harmonic-occupancy-inharmonic-residual-v1.json
?? public/gomyway-1813-harmonic-occupancy-precision-prune-cv-v1-manifest.json
?? public/gomyway-1813-harmonic-occupancy-precision-prune-cv-v1.json
?? public/gomyway-1813-pitch-specific-onset-survivors-precision-v1-manifest.json
?? public/gomyway-1813-pitch-specific-onset-survivors-precision-v1.json
?? public/gomyway-1858-dual-stem-harmonic-shape-balance-v1-manifest.json
?? public/gomyway-1858-dual-stem-harmonic-shape-balance-v1.json
?? public/gomyway-1858-harmonic-occupancy-survivors-precision-v1-manifest.json
?? public/gomyway-1858-harmonic-occupancy-survivors-precision-v1.json
?? public/gomyway-1858-harmonic-shape-precision-prune-cv-v1-manifest.json
?? public/gomyway-1858-harmonic-shape-precision-prune-cv-v1.json
?? public/gomyway-2065-dual-stem-harmonic-peak-alignment-v1-manifest.json
?? public/gomyway-2065-dual-stem-harmonic-peak-alignment-v1.json
?? public/gomyway-2065-harmonic-peak-precision-prune-cv-v1-manifest.json
?? public/gomyway-2065-harmonic-peak-precision-prune-cv-v1.json
?? public/gomyway-2065-harmonic-shape-survivors-precision-v1-manifest.json
?? public/gomyway-2065-harmonic-shape-survivors-precision-v1.json
?? public/gomyway-2134-dual-stem-local-pitch-competition-v1-manifest.json
?? public/gomyway-2134-dual-stem-local-pitch-competition-v1.json
?? public/gomyway-2134-harmonic-peak-survivors-precision-v1-manifest.json
?? public/gomyway-2134-harmonic-peak-survivors-precision-v1.json
?? public/gomyway-2134-local-pitch-competition-precision-prune-cv-v1-manifest.json
?? public/gomyway-2134-local-pitch-competition-precision-prune-cv-v1.json
?? public/gomyway-2140-dual-stem-harmonic-onset-sustain-stability-v1-manifest.json
?? public/gomyway-2140-dual-stem-harmonic-onset-sustain-stability-v1.json
?? public/gomyway-2140-onset-sustain-stability-precision-prune-cv-v1-manifest.json
?? public/gomyway-2140-onset-sustain-stability-precision-prune-cv-v1.json
?? public/gomyway-2144-local-pitch-competition-survivors-precision-v1-manifest.json
?? public/gomyway-2144-local-pitch-competition-survivors-precision-v1.json
?? public/gomyway-2328-dual-stem-transient-onset-morphology-v1-manifest.json
?? public/gomyway-2328-dual-stem-transient-onset-morphology-v1.json
?? public/gomyway-2328-onset-sustain-survivors-precision-v1-manifest.json
?? public/gomyway-2328-onset-sustain-survivors-precision-v1.json
?? public/gomyway-2328-transient-onset-morphology-precision-prune-cv-v1-manifest.json
?? public/gomyway-2328-transient-onset-morphology-precision-prune-cv-v1.json
?? public/gomyway-2409-dual-stem-harmonic-band-concentration-v1-manifest.json
?? public/gomyway-2409-dual-stem-harmonic-band-concentration-v1.json
?? public/gomyway-2409-harmonic-band-concentration-precision-prune-cv-v1-manifest.json
?? public/gomyway-2409-harmonic-band-concentration-precision-prune-cv-v1.json
?? public/gomyway-2409-transient-onset-survivors-precision-v1-manifest.json
?? public/gomyway-2409-transient-onset-survivors-precision-v1.json
?? public/gomyway-2476-dual-stem-harmonic-template-competition-v1-manifest.json
?? public/gomyway-2476-dual-stem-harmonic-template-competition-v1.json
?? public/gomyway-2476-harmonic-band-survivors-precision-v1-manifest.json
?? public/gomyway-2476-harmonic-band-survivors-precision-v1.json
?? public/gomyway-2476-harmonic-template-competition-precision-prune-cv-v2-manifest.json
?? public/gomyway-2476-harmonic-template-competition-precision-prune-cv-v2.json
?? public/gomyway-2552-dual-stem-periodicity-phase-coherence-v1-manifest.json
?? public/gomyway-2552-dual-stem-periodicity-phase-coherence-v1.json
?? public/gomyway-2552-harmonic-template-survivors-precision-v1-manifest.json
?? public/gomyway-2552-harmonic-template-survivors-precision-v1.json
?? public/gomyway-2552-periodicity-phase-coherence-precision-prune-cv-v1-manifest.json
?? public/gomyway-2552-periodicity-phase-coherence-precision-prune-cv-v1.json
?? public/gomyway-2568-dual-stem-spectral-tonal-noise-contrast-v1-manifest.json
?? public/gomyway-2568-dual-stem-spectral-tonal-noise-contrast-v1.json
?? public/gomyway-2568-periodicity-survivors-precision-v1-manifest.json
?? public/gomyway-2568-periodicity-survivors-precision-v1.json
?? public/gomyway-2568-spectral-tonal-noise-precision-prune-cv-v1-manifest.json
?? public/gomyway-2568-spectral-tonal-noise-precision-prune-cv-v1.json
?? public/gomyway-2673-dual-stem-local-pitch-salience-v1-manifest.json
?? public/gomyway-2673-dual-stem-local-pitch-salience-v1.json
?? public/gomyway-2673-dual-stem-transient-attack-structure-v1-manifest.json
?? public/gomyway-2673-dual-stem-transient-attack-structure-v1.json
?? public/gomyway-2673-local-pitch-salience-precision-prune-cv-v1-manifest.json
?? public/gomyway-2673-local-pitch-salience-precision-prune-cv-v1.json
?? public/gomyway-2705-dual-stem-onset-jitter-consistency-v1-manifest.json
?? public/gomyway-2705-dual-stem-onset-jitter-consistency-v1.json
?? public/gomyway-2705-dual-stem-pitch-trajectory-stability-v1-manifest.json
?? public/gomyway-2705-dual-stem-pitch-trajectory-stability-v1.json
?? public/gomyway-2705-local-pitch-salience-survivors-precision-v1-manifest.json
?? public/gomyway-2705-local-pitch-salience-survivors-precision-v1.json
?? public/gomyway-2705-pitch-trajectory-precision-prune-cv-v1-manifest.json
?? public/gomyway-2705-pitch-trajectory-precision-prune-cv-v1.json
?? public/gomyway-2731-dual-stem-spectral-envelope-shape-v1-manifest.json
?? public/gomyway-2731-dual-stem-spectral-envelope-shape-v1.json
?? public/gomyway-2731-pitch-trajectory-survivors-precision-v1-manifest.json
?? public/gomyway-2731-pitch-trajectory-survivors-precision-v1.json
?? public/gomyway-2731-spectral-envelope-precision-prune-cv-v1-manifest.json
?? public/gomyway-2731-spectral-envelope-precision-prune-cv-v1.json
?? public/gomyway-2769-dual-stem-duration-sustain-shape-v1-manifest.json
?? public/gomyway-2769-dual-stem-duration-sustain-shape-v1.json
?? public/gomyway-2769-dual-stem-harmonic-phase-coherence-v1-manifest.json
?? public/gomyway-2769-dual-stem-harmonic-phase-coherence-v1.json
?? public/gomyway-2769-harmonic-phase-precision-prune-cv-v1-manifest.json
?? public/gomyway-2769-harmonic-phase-precision-prune-cv-v1.json
?? public/gomyway-2769-spectral-envelope-survivors-precision-v1-manifest.json
?? public/gomyway-2769-spectral-envelope-survivors-precision-v1.json
?? public/gomyway-2802-chord-context-precision-prune-cv-v1-manifest.json
?? public/gomyway-2802-chord-context-precision-prune-cv-v1.json
?? public/gomyway-2802-dual-stem-harmonic-residual-cancellation-v1-manifest.json
?? public/gomyway-2802-dual-stem-harmonic-residual-cancellation-v1.json
?? public/gomyway-2802-harmonic-phase-survivors-precision-v1-manifest.json
?? public/gomyway-2802-harmonic-phase-survivors-precision-v1.json
?? public/gomyway-2802-polyphonic-chord-context-v1-manifest.json
?? public/gomyway-2802-polyphonic-chord-context-v1.json
?? public/gomyway-2813-chord-context-survivors-precision-v1-manifest.json
?? public/gomyway-2813-chord-context-survivors-precision-v1.json
?? public/gomyway-2813-temporal-density-crowding-v1-manifest.json
?? public/gomyway-2813-temporal-density-crowding-v1.json
?? public/gomyway-2813-temporal-density-precision-prune-cv-v1-manifest.json
?? public/gomyway-2813-temporal-density-precision-prune-cv-v1.json
?? public/gomyway-2850-measure-position-precision-prune-cv-v1-manifest.json
?? public/gomyway-2850-measure-position-precision-prune-cv-v1.json
?? public/gomyway-2850-measure-position-rhythmic-role-v1-manifest.json
?? public/gomyway-2850-measure-position-rhythmic-role-v1.json
?? public/gomyway-2850-temporal-density-survivors-precision-v1-manifest.json
?? public/gomyway-2850-temporal-density-survivors-precision-v1.json
?? public/gomyway-3118-measure-position-survivors-precision-v1-manifest.json
?? public/gomyway-3118-measure-position-survivors-precision-v1.json
?? public/gomyway-3118-measure-register-distribution-v1-manifest.json
?? public/gomyway-3118-measure-register-distribution-v1.json
?? public/gomyway-3118-measure-register-precision-prune-cv-v1-manifest.json
?? public/gomyway-3118-measure-register-precision-prune-cv-v1.json
?? public/gomyway-3118-pitch-interval-rhythmic-neighbor-context-v1-manifest.json
?? public/gomyway-3118-pitch-interval-rhythmic-neighbor-context-v1.json
?? public/gomyway-3161-cross-family-interactions-v1-manifest.json
?? public/gomyway-3161-cross-family-interactions-v1.json
?? public/gomyway-3161-duration-sustain-shape-v1-manifest.json
?? public/gomyway-3161-duration-sustain-shape-v1.json
?? public/gomyway-3161-fundamental-harmonic-alias-survivors-v1-manifest.json
?? public/gomyway-3161-fundamental-harmonic-alias-survivors-v1.json
?? public/gomyway-3161-fundamental-periodicity-survivors-v1-manifest.json
?? public/gomyway-3161-fundamental-periodicity-survivors-v1.json
?? public/gomyway-3161-fundamental-phase-lock-survivors-v1-manifest.json
?? public/gomyway-3161-fundamental-phase-lock-survivors-v1.json
?? public/gomyway-3161-harmonic-comb-alignment-survivors-v1-manifest.json
?? public/gomyway-3161-harmonic-comb-alignment-survivors-v1.json
?? public/gomyway-3161-harmonic-residual-cancellation-survivors-v1-manifest.json
?? public/gomyway-3161-harmonic-residual-cancellation-survivors-v1.json
?? public/gomyway-3161-inharmonic-partial-spacing-survivors-v1-manifest.json
?? public/gomyway-3161-inharmonic-partial-spacing-survivors-v1.json
?? public/gomyway-3161-measure-register-survivors-precision-v1-manifest.json
?? public/gomyway-3161-measure-register-survivors-precision-v1.json
?? public/gomyway-3161-microtiming-contextual-cv-v1-manifest.json
?? public/gomyway-3161-microtiming-contextual-cv-v1.json
?? public/gomyway-3161-microtiming-contextual-support-sweep-cv-v1-manifest.json
?? public/gomyway-3161-microtiming-contextual-support-sweep-cv-v1.json
?? public/gomyway-3161-near-zero-cross-family-refinement-v1-manifest.json
?? public/gomyway-3161-near-zero-cross-family-refinement-v1.json
?? public/gomyway-3161-near-zero-microtiming-precision-prune-cv-v1-manifest.json
?? public/gomyway-3161-near-zero-microtiming-precision-prune-cv-v1.json
?? public/gomyway-3161-near-zero-microtiming-refinement-v1-manifest.json
?? public/gomyway-3161-near-zero-microtiming-refinement-v1.json
?? public/gomyway-3161-near-zero-microtiming-subset-search-cv-v1-manifest.json
?? public/gomyway-3161-near-zero-microtiming-subset-search-cv-v1.json
?? public/gomyway-3161-protected-source-recall-recovery-v1-manifest.json
?? public/gomyway-3161-protected-source-recall-recovery-v1.json
?? public/gomyway-3161-spectral-flux-survivors-v1-manifest.json
?? public/gomyway-3161-spectral-flux-survivors-v1.json
?? public/gomyway-3161-spectral-tonal-noise-survivors-v1-manifest.json
?? public/gomyway-3161-spectral-tonal-noise-survivors-v1.json
?? public/gomyway-3161-transient-attack-survivors-v1-manifest.json
?? public/gomyway-3161-transient-attack-survivors-v1.json
?? public/gomyway-3161-wide-recall-basic-pitch-sweep-v1-manifest.json
?? public/gomyway-3161-wide-recall-basic-pitch-sweep-v1.json
?? public/gomyway-3161-wide-recall-candidate-selection-v1-manifest.json
?? public/gomyway-3161-wide-recall-candidate-selection-v1.json
?? public/gomyway-3161-wide-recall-contextual-consensus-recovery-cv-v1-manifest.json
?? public/gomyway-3161-wide-recall-contextual-consensus-recovery-cv-v1.json
?? public/gomyway-3161-wide-recall-contextual-consensus-recovery-v1-manifest.json
?? public/gomyway-3161-wide-recall-contextual-consensus-recovery-v1.json
?? public/gomyway-3161-wide-recall-contextual-pattern-recovery-v1-manifest.json
?? public/gomyway-3161-wide-recall-contextual-pattern-recovery-v1.json
?? public/gomyway-3676-cross-experiment-hard-slot-anatomy-v1-manifest.json
?? public/gomyway-3676-cross-experiment-hard-slot-anatomy-v1.json
?? public/gomyway-3676-cross-experiment-hard-slot-anatomy-v2-manifest.json
?? public/gomyway-3676-cross-experiment-hard-slot-anatomy-v2.json
?? public/gomyway-3676-local-contrast-selection-instability-v1-manifest.json
?? public/gomyway-3676-local-contrast-selection-instability-v1.json
?? public/gomyway-3676-multifamily-agreement-diagnostic-v1-manifest.json
?? public/gomyway-3676-multifamily-agreement-diagnostic-v1.json
?? public/gomyway-3676-multifamily-nested-agreement-cv-v1-manifest.json
?? public/gomyway-3676-multifamily-nested-agreement-cv-v1.json
?? public/gomyway-3676-onset-slot-continuous-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-continuous-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-feature-orientation-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-feature-orientation-stability-v1.json
?? public/gomyway-3676-onset-slot-invariant-orientation-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-invariant-orientation-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-local-contrast-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-local-contrast-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-local-transient-contrast-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-local-transient-contrast-stability-v1.json
?? public/gomyway-3676-onset-slot-micro-temporal-consensus-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-micro-temporal-consensus-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-micro-temporal-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-micro-temporal-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-micro-temporal-ridge-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-micro-temporal-ridge-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-micro-temporal-shape-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-micro-temporal-shape-stability-v1.json
?? public/gomyway-3676-onset-slot-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-richer-audio-feature-consensus-nested-cv-v2-manifest.json
?? public/gomyway-3676-onset-slot-richer-audio-feature-consensus-nested-cv-v2.json
?? public/gomyway-3676-onset-slot-richer-audio-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-richer-audio-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-richer-audio-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-richer-audio-stability-v1.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-ridge-nested-cv-v1-manifest.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-ridge-nested-cv-v1.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-spectro-temporal-patch-stability-v1.json
?? public/gomyway-3676-onset-slot-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-stability-v1.json
?? public/gomyway-3676-onset-slot-transient-interaction-stability-v1-manifest.json
?? public/gomyway-3676-onset-slot-transient-interaction-stability-v1.json
?? public/gomyway-3676-patch-local-context-distribution-shift-v1-manifest.json
?? public/gomyway-3676-patch-local-context-distribution-shift-v1.json
?? public/gomyway-3676-patch-pairwise-pair-coverage-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-pair-coverage-v1.json
?? public/gomyway-3676-patch-pairwise-rank-available-measure-balanced-nested-cv-v4-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-available-measure-balanced-nested-cv-v4.json
?? public/gomyway-3676-patch-pairwise-rank-ensemble-nested-cv-v8-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-ensemble-nested-cv-v8.json
?? public/gomyway-3676-patch-pairwise-rank-interaction-basis-nested-cv-v12-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-interaction-basis-nested-cv-v12.json
?? public/gomyway-3676-patch-pairwise-rank-local-context-nested-cv-v7-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-local-context-nested-cv-v7.json
?? public/gomyway-3676-patch-pairwise-rank-nested-cv-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-nested-cv-v1.json
?? public/gomyway-3676-patch-pairwise-rank-nonlinear-basis-nested-cv-v11-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-nonlinear-basis-nested-cv-v11.json
?? public/gomyway-3676-patch-pairwise-rank-rhythm-phase-nested-cv-v13-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-rhythm-phase-nested-cv-v13.json
?? public/gomyway-3676-patch-pairwise-rank-rhythm-phase-period-ablation-v14-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-rhythm-phase-period-ablation-v14.json
?? public/gomyway-3676-patch-pairwise-rank-section-calibrated-dense-q-nested-cv-v6-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-section-calibrated-dense-q-nested-cv-v6.json
?? public/gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-section-calibrated-nested-cv-v5.json
?? public/gomyway-3676-patch-pairwise-rank-stratified-ablate-lowmiddecay60-nested-cv-v3-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-stratified-ablate-lowmiddecay60-nested-cv-v3.json
?? public/gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2-manifest.json
?? public/gomyway-3676-patch-pairwise-rank-stratified-nested-cv-v2.json
?? public/gomyway-3676-patch-pairwise-v1-v2-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v1-v2-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v2-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-failure-anatomy-v1.json
?? public/gomyway-3676-patch-pairwise-v2-section-domain-shift-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-section-domain-shift-anatomy-v1.json
?? public/gomyway-3676-patch-pairwise-v2-section-rank-separability-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-section-rank-separability-v1.json
?? public/gomyway-3676-patch-pairwise-v2-v3-ablation-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-v3-ablation-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v2-v3-trigger-explainer-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-v3-trigger-explainer-v1.json
?? public/gomyway-3676-patch-pairwise-v2-v4-sampler-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-v4-sampler-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v2-v5-section-calibration-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v2-v5-section-calibration-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v5-q-selector-stability-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-q-selector-stability-v1.json
?? public/gomyway-3676-patch-pairwise-v5-q-shape-predictive-signal-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-q-shape-predictive-signal-v1.json
?? public/gomyway-3676-patch-pairwise-v5-remaining-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-remaining-failure-anatomy-v1.json
?? public/gomyway-3676-patch-pairwise-v5-unlabeled-score-geometry-cutoff-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-unlabeled-score-geometry-cutoff-v1.json
?? public/gomyway-3676-patch-pairwise-v5-v6-dense-q-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-v6-dense-q-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v5-v7-local-context-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-v7-local-context-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v5-v8-ensemble-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-v8-ensemble-comparison-v1.json
?? public/gomyway-3676-patch-pairwise-v5-v9-pointwise-comparison-v1-manifest.json
?? public/gomyway-3676-patch-pairwise-v5-v9-pointwise-comparison-v1.json
?? public/gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9-manifest.json
?? public/gomyway-3676-patch-pointwise-ridge-section-calibrated-nested-cv-v9.json
?? public/gomyway-3676-patch-rhythm24-global-q-landscape-v27-manifest.json
?? public/gomyway-3676-patch-rhythm24-global-q-landscape-v27.json
?? public/gomyway-3676-patch-rhythm24-global-q020-unseen-phase-confirmation-v28-manifest.json
?? public/gomyway-3676-patch-rhythm24-global-q020-unseen-phase-confirmation-v28.json
?? public/gomyway-3676-patch-rhythm24-multiphase-training-q-selector-v25-manifest.json
?? public/gomyway-3676-patch-rhythm24-multiphase-training-q-selector-v25.json
?? public/gomyway-3676-patch-rhythm24-quarter-phase-training-q-selector-v20-manifest.json
?? public/gomyway-3676-patch-rhythm24-quarter-phase-training-q-selector-v20.json
?? public/gomyway-3676-patch-rhythm24-shifted-only-q-selector-nested-cv-v17-manifest.json
?? public/gomyway-3676-patch-rhythm24-shifted-only-q-selector-nested-cv-v17.json
?? public/gomyway-3676-patch-rhythm24-shifted-remaining-failure-anatomy-v15-manifest.json
?? public/gomyway-3676-patch-rhythm24-shifted-remaining-failure-anatomy-v15.json
?? public/gomyway-3676-patch-rhythm24-training-only-q-selector-nested-cv-v16-manifest.json
?? public/gomyway-3676-patch-rhythm24-training-only-q-selector-nested-cv-v16.json
?? public/gomyway-3676-patch-rhythm24-v17-fixed-policy-boundary-stress-v18-manifest.json
?? public/gomyway-3676-patch-rhythm24-v17-fixed-policy-boundary-stress-v18.json
?? public/gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23-manifest.json
?? public/gomyway-3676-patch-rhythm24-v17-frozen-unseen-phase-confirmation-v23.json
?? public/gomyway-3676-patch-rhythm24-v17-v25-paired-challenge-comparison-v26-manifest.json
?? public/gomyway-3676-patch-rhythm24-v17-v25-paired-challenge-comparison-v26.json
?? public/gomyway-3676-patch-rhythm24-v18-quarter-phase-failure-anatomy-v19-manifest.json
?? public/gomyway-3676-patch-rhythm24-v18-quarter-phase-failure-anatomy-v19.json
?? public/gomyway-3676-patch-rhythm24-v20-remaining-failure-anatomy-v21-manifest.json
?? public/gomyway-3676-patch-rhythm24-v20-remaining-failure-anatomy-v21.json
?? public/gomyway-3676-patch-rhythm24-v20-training-geometry-q-preference-v22-manifest.json
?? public/gomyway-3676-patch-rhythm24-v20-training-geometry-q-preference-v22.json
?? public/gomyway-3676-patch-rhythm24-v23-failure-map-v24-manifest.json
?? public/gomyway-3676-patch-rhythm24-v23-failure-map-v24.json
?? public/gomyway-3676-patch-rhythm24-v28-failure-map-v29-manifest.json
?? public/gomyway-3676-patch-rhythm24-v28-failure-map-v29.json
?? public/gomyway-3676-patch-rhythm24-v84-confirmation-floor-failure-anatomy-v85-manifest.json
?? public/gomyway-3676-patch-rhythm24-v84-confirmation-floor-failure-anatomy-v85.json
?? public/gomyway-3676-patch-ridge-calibration-selector-learnability-v1-manifest.json
?? public/gomyway-3676-patch-ridge-calibration-selector-learnability-v1.json
?? public/gomyway-3676-patch-ridge-calibration-strategy-comparison-v1-manifest.json
?? public/gomyway-3676-patch-ridge-calibration-strategy-comparison-v1.json
?? public/gomyway-3676-patch-ridge-local-normalization-impact-v1-manifest.json
?? public/gomyway-3676-patch-ridge-local-normalization-impact-v1.json
?? public/gomyway-3676-patch-ridge-local-normalization-impact-v2-manifest.json
?? public/gomyway-3676-patch-ridge-local-normalization-impact-v2.json
?? public/gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1-manifest.json
?? public/gomyway-3676-patch-ridge-local-robust-normalized-nested-cv-v1.json
?? public/gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1-manifest.json
?? public/gomyway-3676-patch-ridge-recurrent-feature-gate-nested-cv-v1.json
?? public/gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1-manifest.json
?? public/gomyway-3676-patch-ridge-relative-rank-calibration-nested-cv-v1.json
?? public/gomyway-3676-patch-ridge-section-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-ridge-section-failure-anatomy-v1.json
?? public/gomyway-3676-patch-ridge-section-shift-calibration-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-ridge-section-shift-calibration-anatomy-v1.json
?? public/gomyway-3676-patch-v10-cross-architecture-q-transfer-v1-manifest.json
?? public/gomyway-3676-patch-v10-cross-architecture-q-transfer-v1.json
?? public/gomyway-3676-patch-v10-cross-architecture-score-blend-v1-manifest.json
?? public/gomyway-3676-patch-v10-cross-architecture-score-blend-v1.json
?? public/gomyway-3676-patch-v10-negative-tail-hybrid-selector-signal-v1-manifest.json
?? public/gomyway-3676-patch-v10-negative-tail-hybrid-selector-signal-v1.json
?? public/gomyway-3676-patch-v10-negative-tail-hybrid-selector-tiebreak-v2-manifest.json
?? public/gomyway-3676-patch-v10-negative-tail-hybrid-selector-tiebreak-v2.json
?? public/gomyway-3676-patch-v10-negative-tail-threshold-v1-manifest.json
?? public/gomyway-3676-patch-v10-negative-tail-threshold-v1.json
?? public/gomyway-3676-patch-v10-remaining-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-patch-v10-remaining-failure-anatomy-v1.json
?? public/gomyway-3676-patch-v10-residual-geometry-negative-tail-selector-v1-manifest.json
?? public/gomyway-3676-patch-v10-residual-geometry-negative-tail-selector-v1.json
?? public/gomyway-3676-patch-v10-residual-score-distribution-signal-v1-manifest.json
?? public/gomyway-3676-patch-v10-residual-score-distribution-signal-v1.json
?? public/gomyway-3676-patch-v5-v10-hybrid-comparison-v1-manifest.json
?? public/gomyway-3676-patch-v5-v10-hybrid-comparison-v1.json
?? public/gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10-manifest.json
?? public/gomyway-3676-patch-v5-v9-hybrid-sectionpass-nested-cv-v10.json
?? public/gomyway-3676-patch-v5-v9-hybrid-selector-signal-v1-manifest.json
?? public/gomyway-3676-patch-v5-v9-hybrid-selector-signal-v1.json
?? public/gomyway-3676-pitch-register-interval-recovery-cv-v1-manifest.json
?? public/gomyway-3676-pitch-register-interval-recovery-cv-v1.json
?? public/gomyway-3676-pitch-register-interval-recovery-v1-manifest.json
?? public/gomyway-3676-pitch-register-interval-recovery-v1.json
?? public/gomyway-3676-pitch-register-interval-signature-stability-v1-manifest.json
?? public/gomyway-3676-pitch-register-interval-signature-stability-v1.json
?? public/gomyway-3676-pitchcore-adaptive-penalty-nested-cv-v1-manifest.json
?? public/gomyway-3676-pitchcore-adaptive-penalty-nested-cv-v1.json
?? public/gomyway-3676-pitchcore-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-pitchcore-failure-anatomy-v1.json
?? public/gomyway-3676-pitchcore-learned-failure-penalty-cv-v1-manifest.json
?? public/gomyway-3676-pitchcore-learned-failure-penalty-cv-v1.json
?? public/gomyway-3676-pitchcore-penalty-learnability-v1-manifest.json
?? public/gomyway-3676-pitchcore-penalty-learnability-v1.json
?? public/gomyway-3676-prcross-nested-consensus-cv-v1-manifest.json
?? public/gomyway-3676-prcross-nested-consensus-cv-v1.json
?? public/gomyway-3676-recovery-fold-consensus-prune-v1-manifest.json
?? public/gomyway-3676-recovery-fold-consensus-prune-v1.json
?? public/gomyway-3676-recovery-precision-prune-cv-v1-manifest.json
?? public/gomyway-3676-recovery-precision-prune-cv-v1.json
?? public/gomyway-3676-recovery-precision-survivors-v1-manifest.json
?? public/gomyway-3676-recovery-precision-survivors-v1.json
?? public/gomyway-3676-repeated-phrase-cross-partition-agreement-cv-v1-manifest.json
?? public/gomyway-3676-repeated-phrase-cross-partition-agreement-cv-v1.json
?? public/gomyway-3676-repeated-phrase-cross-partition-agreement-v1-manifest.json
?? public/gomyway-3676-repeated-phrase-cross-partition-agreement-v1.json
?? public/gomyway-3676-repeated-phrase-template-recovery-cv-v1-manifest.json
?? public/gomyway-3676-repeated-phrase-template-recovery-cv-v1.json
?? public/gomyway-3676-repeated-phrase-template-recovery-v1-manifest.json
?? public/gomyway-3676-repeated-phrase-template-recovery-v1.json
?? public/gomyway-3676-richer-audio-nested-failure-anatomy-v1-manifest.json
?? public/gomyway-3676-richer-audio-nested-failure-anatomy-v1.json
?? public/gomyway-3676-second-wave-contextual-recovery-cv-v1-manifest.json
?? public/gomyway-3676-second-wave-contextual-recovery-cv-v1.json
?? public/gomyway-3676-second-wave-contextual-recovery-v1-manifest.json
?? public/gomyway-3676-second-wave-contextual-recovery-v1.json
?? public/gomyway-3676-second-wave-partition-stable-recovery-cv-v1-manifest.json
?? public/gomyway-3676-second-wave-partition-stable-recovery-cv-v1.json
?? public/gomyway-3676-second-wave-partition-stable-recovery-v1-manifest.json
?? public/gomyway-3676-second-wave-partition-stable-recovery-v1.json
?? public/gomyway-3676-spectral-harmonic-onset-stability-v1-manifest.json
?? public/gomyway-3676-spectral-harmonic-onset-stability-v1.json
?? public/gomyway-3676-votes3-acoustic-precision-prune-cv-v1-manifest.json
?? public/gomyway-3676-votes3-acoustic-precision-prune-cv-v1.json
?? public/gomyway-3676-votes3-acoustic-refinement-v1-manifest.json
?? public/gomyway-3676-votes3-acoustic-refinement-v1.json
?? public/gomyway-3676-votes3-duration-guard-refinement-v1-manifest.json
?? public/gomyway-3676-votes3-duration-guard-refinement-v1.json
?? public/gomyway-3676-votes3-guarded-duration-prune-cv-v1-manifest.json
?? public/gomyway-3676-votes3-guarded-duration-prune-cv-v1.json
?? public/gomyway-3676-votes3-low-complexity-acoustic-rule-cv-v1-manifest.json
?? public/gomyway-3676-votes3-low-complexity-acoustic-rule-cv-v1.json
?? public/gomyway-3676-votes3-low-complexity-acoustic-rules-v1-manifest.json
?? public/gomyway-3676-votes3-low-complexity-acoustic-rules-v1.json
?? public/gomyway-909-champion-zero-precision-cross-signature-gate-v1-manifest.json
?? public/gomyway-909-champion-zero-precision-cross-signature-gate-v1.json
?? public/gomyway-910-champion-zero-precision-step-pitch-gate-v1-manifest.json
?? public/gomyway-910-champion-zero-precision-step-pitch-gate-v1.json
?? public/gomyway-916-champion-recurrent-step8-or-midi57-subgate-v1-manifest.json
?? public/gomyway-916-champion-recurrent-step8-or-midi57-subgate-v1.json
?? public/gomyway-916-champion-recurrent-step8-or-midi57-winner13-subgate-v1-manifest.json
?? public/gomyway-916-champion-recurrent-step8-or-midi57-winner13-subgate-v1.json
?? public/gomyway-916-champion-score13-16-both-ge10-gate-v1-manifest.json
?? public/gomyway-916-champion-score13-16-both-ge10-gate-v1.json
?? public/gomyway-916-recurrent-step8-or-midi57-failed-subgate-provenance-v1-manifest.json
?? public/gomyway-916-recurrent-step8-or-midi57-failed-subgate-provenance-v1.json
?? public/gomyway-916-score13-16-both-ge10-detector-features-v1-manifest.json
?? public/gomyway-916-score13-16-both-ge10-detector-features-v1.json
?? public/gomyway-916-score13-16-both-ge10-provenance-v1-manifest.json
?? public/gomyway-916-score13-16-both-ge10-provenance-v1.json
?? public/gomyway-919-champion-zero-precision-step-pitch-gate-v1-manifest.json
?? public/gomyway-919-champion-zero-precision-step-pitch-gate-v1.json
?? public/gomyway-921-champion-zero-precision-step-agreement-and-step-pitch-gate-v1-manifest.json
?? public/gomyway-921-champion-zero-precision-step-agreement-and-step-pitch-gate-v1.json
?? public/gomyway-923-champion-deep-cross-signature-residual-extras-profile-v1-manifest.json
?? public/gomyway-923-champion-deep-cross-signature-residual-extras-profile-v1.json
?? public/gomyway-923-champion-deep-zero-precision-gate-v1-manifest.json
?? public/gomyway-923-champion-deep-zero-precision-gate-v1.json
?? public/gomyway-926-champion-combined-staging-plus-step8-midi52-both10-only-gate-v1-manifest.json
?? public/gomyway-926-champion-combined-staging-plus-step8-midi52-both10-only-gate-v1.json
?? public/gomyway-926-champion-step0-midi57-score8-10-single-weak-gate-v1-manifest.json
?? public/gomyway-926-champion-step0-midi57-score8-10-single-weak-gate-v1.json
?? public/gomyway-926-champion-step0-midi57-staging-residual-extras-profile-v1-manifest.json
?? public/gomyway-926-champion-step0-midi57-staging-residual-extras-profile-v1.json
?? public/gomyway-927-champion-step0-midi57-recurrent-and-both10-gate-v1-manifest.json
?? public/gomyway-927-champion-step0-midi57-recurrent-and-both10-gate-v1.json
?? public/gomyway-929-champion-missing-reference-opportunities-v1-manifest.json
?? public/gomyway-929-champion-missing-reference-opportunities-v1.json
?? public/gomyway-929-champion-reference-free-upstream-recall-spectral-gate-v1-manifest.json
?? public/gomyway-929-champion-reference-free-upstream-recall-spectral-gate-v1.json
?? public/gomyway-929-never-seen-raw-spectral-evidence-v1-manifest.json
?? public/gomyway-929-never-seen-raw-spectral-evidence-v1.json
?? public/gomyway-adaptive-spectral-shifted-window-failure-profile-v1-manifest.json
?? public/gomyway-adaptive-spectral-shifted-window-failure-profile-v1.json
?? public/gomyway-adaptive-spectral-shifted-window-stability-v1-manifest.json
?? public/gomyway-adaptive-spectral-shifted-window-stability-v1.json
?? public/gomyway-adaptive-spectral-temporal-recurrence-gate-v1-manifest.json
?? public/gomyway-adaptive-spectral-temporal-recurrence-gate-v1.json
?? public/gomyway-ai-tab-113-measure-shadow-request.json
?? public/gomyway-approved-string-geometry-extraction-scaffold-v48.json
?? public/gomyway-authoritative-locked-reference-v16.json
?? public/gomyway-basic-pitch-chord-aware-filter-v1-manifest.json
?? public/gomyway-basic-pitch-chord-aware-filter-v1.json
?? public/gomyway-basic-pitch-confidence-recurrence-filter-v1-manifest.json
?? public/gomyway-basic-pitch-confidence-recurrence-filter-v1.json
?? public/gomyway-basic-pitch-consensus-recall-recovery-v1-manifest.json
?? public/gomyway-basic-pitch-consensus-recall-recovery-v1.json
?? public/gomyway-basic-pitch-harmonic-refinement-v2-manifest.json
?? public/gomyway-basic-pitch-harmonic-refinement-v2.json
?? public/gomyway-basic-pitch-threshold-sweep-v1-manifest.json
?? public/gomyway-basic-pitch-threshold-sweep-v1.json
?? public/gomyway-bridge-solo-ending-source-resolution-audit.json
?? public/gomyway-chord-shape-transfer-proof-review-v1-manifest.json
?? public/gomyway-chord-shape-transfer-proof-review-v1.json
?? public/gomyway-chord-shape-transfer-proof-v1-manifest.json
?? public/gomyway-chord-shape-transfer-proof-v1.json
?? public/gomyway-chorus-33-35-audio-chord-evidence-v1-manifest.json
?? public/gomyway-chorus-33-35-audio-chord-evidence-v1.json
?? public/gomyway-chorus-33-35-audio-technique-features-v1-manifest.json
?? public/gomyway-chorus-33-35-audio-technique-features-v1.json
?? public/gomyway-chorus-33-35-audio-technique-window-plan-v1-manifest.json
?? public/gomyway-chorus-33-35-audio-technique-window-plan-v1.json
?? public/gomyway-chorus-33-35-bend-vibrato-inventory-v1-manifest.json
?? public/gomyway-chorus-33-35-bend-vibrato-inventory-v1.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v1-manifest.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v1.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v2-manifest.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v2.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v3-manifest.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v3.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v4-manifest.json
?? public/gomyway-chorus-33-35-chord-candidate-projection-v4.json
?? public/gomyway-chorus-33-35-chord-recovery-audit-v1.json
?? public/gomyway-chorus-33-35-chord-recovery-plan-v1.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v1-manifest.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v1.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v2-manifest.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v2.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v3-manifest.json
?? public/gomyway-chorus-33-35-completed-timing-plan-v3.json
?? public/gomyway-chorus-33-35-conflicting-observed-timing-sources-v1-manifest.json
?? public/gomyway-chorus-33-35-conflicting-observed-timing-sources-v1.json
?? public/gomyway-chorus-33-35-final-post-correction-pitch-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-final-post-correction-pitch-proof-v1.json
?? public/gomyway-chorus-33-35-focused-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-focused-proof-v1.json
?? public/gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-harmonic-branch-corrected-pitch-contour-candidate-v1.json
?? public/gomyway-chorus-33-35-identity-separated-onset-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-identity-separated-onset-candidate-v1.json
?? public/gomyway-chorus-33-35-measure-step-row-identity-v1-manifest.json
?? public/gomyway-chorus-33-35-measure-step-row-identity-v1.json
?? public/gomyway-chorus-33-35-measure-step-timing-bridge-v1-manifest.json
?? public/gomyway-chorus-33-35-measure-step-timing-bridge-v1.json
?? public/gomyway-chorus-33-35-missing-timing-diagnostic-v1-manifest.json
?? public/gomyway-chorus-33-35-missing-timing-diagnostic-v1.json
?? public/gomyway-chorus-33-35-nonstandard-quantized-step-semantics-v1-manifest.json
?? public/gomyway-chorus-33-35-nonstandard-quantized-step-semantics-v1.json
?? public/gomyway-chorus-33-35-observed-timing-source-duplication-v1-manifest.json
?? public/gomyway-chorus-33-35-observed-timing-source-duplication-v1.json
?? public/gomyway-chorus-33-35-pitch-contour-reliability-v1-manifest.json
?? public/gomyway-chorus-33-35-pitch-contour-reliability-v1.json
?? public/gomyway-chorus-33-35-pitch-range-plausibility-v1-manifest.json
?? public/gomyway-chorus-33-35-pitch-range-plausibility-v1.json
?? public/gomyway-chorus-33-35-post-correction-pitch-plausibility-v1-manifest.json
?? public/gomyway-chorus-33-35-post-correction-pitch-plausibility-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-event-local-audio-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-event-local-audio-proof-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-candidate-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-attachment-proof-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-evidence-summary-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-evidence-summary-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-candidate-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-bend-support-overlay-proof-v1.json
?? public/gomyway-chorus-33-35-read-only-chorus-technique-handoff-plan-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-chorus-technique-handoff-plan-v1.json
?? public/gomyway-chorus-33-35-read-only-technique-closure-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-technique-closure-proof-v1.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-calibrated-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-calibrated-proof-v1.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-classifier-v1.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-support-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-support-candidate-v1.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-support-proof-v1-manifest.json
?? public/gomyway-chorus-33-35-read-only-technique-evidence-support-proof-v1.json
?? public/gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-recomputed-corrected-pitch-quality-candidate-v1.json
?? public/gomyway-chorus-33-35-remaining-v2-timing-conflict-v1-manifest.json
?? public/gomyway-chorus-33-35-remaining-v2-timing-conflict-v1.json
?? public/gomyway-chorus-33-35-residual-corrected-pitch-contour-failures-v1-manifest.json
?? public/gomyway-chorus-33-35-residual-corrected-pitch-contour-failures-v1.json
?? public/gomyway-chorus-33-35-source-balanced-observed-timing-candidate-v1-manifest.json
?? public/gomyway-chorus-33-35-source-balanced-observed-timing-candidate-v1.json
?? public/gomyway-chorus-33-35-source-family-local-order-v1-manifest.json
?? public/gomyway-chorus-33-35-source-family-local-order-v1.json
?? public/gomyway-chorus-33-35-step-grid-cardinality-v1-manifest.json
?? public/gomyway-chorus-33-35-step-grid-cardinality-v1.json
?? public/gomyway-chorus-33-35-technique-evidence-professional-label-benchmark-v1-manifest.json
?? public/gomyway-chorus-33-35-technique-evidence-professional-label-benchmark-v1.json
?? public/gomyway-chorus-33-35-timing-monotonicity-diagnostic-v1-manifest.json
?? public/gomyway-chorus-33-35-timing-monotonicity-diagnostic-v1.json
?? public/gomyway-chorus-33-35-timing-source-inventory-v1-manifest.json
?? public/gomyway-chorus-33-35-timing-source-inventory-v1.json
?? public/gomyway-chorus-35-step0-adaptive-boundary-onset-v3-manifest.json
?? public/gomyway-chorus-35-step0-adaptive-boundary-onset-v3.json
?? public/gomyway-chorus-35-step0-audio-onset-v1-manifest.json
?? public/gomyway-chorus-35-step0-audio-onset-v1.json
?? public/gomyway-chorus-35-step0-boundary-anchor-diagnostic-v1-manifest.json
?? public/gomyway-chorus-35-step0-boundary-anchor-diagnostic-v1.json
?? public/gomyway-chorus-35-step0-boundary-sequence-onset-v2-manifest.json
?? public/gomyway-chorus-35-step0-boundary-sequence-onset-v2.json
?? public/gomyway-chorus-35-step0-global-grid-timing-v1-manifest.json
?? public/gomyway-chorus-35-step0-global-grid-timing-v1.json
?? public/gomyway-chorus-activation-feature-family-conclusion-v1.json
?? public/gomyway-chorus-activation-section-holdout-v1.json
?? public/gomyway-chorus-candidate-activation-v1.json
?? public/gomyway-chorus-candidate-activation-v2.json
?? public/gomyway-chorus-phrase-position-conclusion-v1.json
?? public/gomyway-chorus-phrase-position-consensus-v1.json
?? public/gomyway-chorus-soft-evidence-ranking-v1.json
?? public/gomyway-chorus-source-resolution-audit.json
?? public/gomyway-chorus-source-review-packet.json
?? public/gomyway-chorus-source-review-packet.txt
?? public/gomyway-chorus1-chorus2-discrepancy-audit.json
?? public/gomyway-chorus1-chorus2-discrepancy-audit.txt
?? public/gomyway-chorus1-chorus2-musical-consensus.json
?? public/gomyway-chorus1-chorus2-musical-consensus.txt
?? public/gomyway-chorus2-prototype-refinement-conclusion-v1.json
?? public/gomyway-chorus2-prototype-refinement-v1.json
?? public/gomyway-consensus-recall-candidate-profile-v1-manifest.json
?? public/gomyway-consensus-recall-candidate-profile-v1.json
?? public/gomyway-cross-signature-pruned-residual-extras-profile-v1-manifest.json
?? public/gomyway-cross-signature-pruned-residual-extras-profile-v1.json
?? public/gomyway-cross-signature-pruned-residual-zero-precision-gate-v1-manifest.json
?? public/gomyway-cross-signature-pruned-residual-zero-precision-gate-v1.json
?? public/gomyway-cross-stem-consensus-recall-v1-manifest.json
?? public/gomyway-cross-stem-consensus-recall-v1.json
?? public/gomyway-cross-stem-missing-profile-v1-manifest.json
?? public/gomyway-cross-stem-missing-profile-v1.json
?? public/gomyway-cross-stem-recall-crossval-v1-manifest.json
?? public/gomyway-cross-stem-recall-crossval-v1.json
?? public/gomyway-cross-stem-recall-section-stability-v1-manifest.json
?? public/gomyway-cross-stem-recall-section-stability-v1.json
?? public/gomyway-effective-activation-bounds-v2.json
?? public/gomyway-event-row-membership-string-y-v42.json
?? public/gomyway-event-row-membership-string-y-v42/
?? public/gomyway-exact-repeat-confirmation-audit.json
?? public/gomyway-final-ending-event-detail-audit-v1.json
?? public/gomyway-final-ending-reference-content-audit-v1.json
?? public/gomyway-final-ending-rhythm-audit-v1.json
?? public/gomyway-final-ending-source-discovery-v1.json
?? public/gomyway-final-ending-validation-benchmark-v1.json
?? public/gomyway-final-unique-source-resolution-audit.json
?? public/gomyway-full-rhythm-sustain-projection-v1-manifest.json
?? public/gomyway-full-rhythm-sustain-projection-v1.json
?? public/gomyway-full-rhythm-technique-evidence-audit-v1.json
?? public/gomyway-full-song-intro-slot-recall-audit-v2.json
?? public/gomyway-full-song-measure-bounds-v1.json
?? public/gomyway-full-song-review-evidence-merge-v1.json
?? public/gomyway-full-song-review-evidence-reconciliation-v1.json
?? public/gomyway-full-song-rhythm-completion-audit-v1.json
?? public/gomyway-full-song-string-line-geometry-v52.json
?? public/gomyway-full-song-string-line-geometry-v52/
?? public/gomyway-full-song-string-line-geometry-v53.json
?? public/gomyway-full-song-string-line-geometry-v53/
?? public/gomyway-full-song-v8-genuine-tablature-proof-v1-manifest.json
?? public/gomyway-full-song-v8-genuine-tablature-proof-v1.pdf
?? public/gomyway-full-song-v8-notation-metadata.json
?? public/gomyway-full-song-v8-notation-proof-v1-manifest.json
?? public/gomyway-full-song-v8-notation-proof-v1.pdf
?? public/gomyway-full-song-v8-render-events-overlay-v1.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v1-manifest.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v1.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2-manifest.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2-rhythm-training-gate-v1.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-intro-recovered-v2.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1-manifest.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-locked-intro-v1.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-v2-audit.json
?? public/gomyway-full-song-v8-rhythm-candidates-1-113-v2.json
?? public/gomyway-full-song-v8-rhythm-training-gate-v1.json
?? public/gomyway-fullmix-v8-rhythm-candidates-comparison-v1.json
?? public/gomyway-gpu-separator-stem-grade-v1-manifest.json
?? public/gomyway-gpu-separator-stem-grade-v1.json
?? public/gomyway-guitar-specific-neural-detector-v1-manifest.json
?? public/gomyway-guitar-specific-neural-detector-v1.json
?? public/gomyway-intro-pitch-technique-training-pack-v1.json
?? public/gomyway-intro-review-evidence-audit-v1.json
?? public/gomyway-intro-unresolved-slot-consensus-recovery-v1.json
?? public/gomyway-intro-unresolved-slot-consensus-recovery-v2.json
?? public/gomyway-jimmy-paige-professional-value-annotation-queue.json
?? public/gomyway-jimmy-paige-professional-value-completion-plan.json
?? public/gomyway-jimmy-paige-professional-value-reference-inventory.json
?? public/gomyway-jimmy-paige-protected-113-measure-rhythm-regression.json
?? public/gomyway-jimmy-paige-protected-full-song-rhythm-regression-preflight.json
?? public/gomyway-jimmy-paige-protected-renderer-integration-approval.json
?? public/gomyway-jimmy-paige-protected-renderer-integration-gate.json
?? public/gomyway-jimmy-paige-protected-renderer-integration-preview.json
?? public/gomyway-jimmy-paige-protected-renderer-integration-preview.svg
?? public/gomyway-jimmy-paige-protected-section-comparison-preflight.json
?? public/gomyway-jimmy-paige-protected-section-evidence-comparison.json
?? public/gomyway-jimmy-paige-protected-section-value-extraction.json
?? public/gomyway-jimmy-paige-targeted-rhythm-gap-analysis.json
?? public/gomyway-layered-reference-precision-benchmark-v1.json
?? public/gomyway-layered-reference-precision-benchmark-v2.json
?? public/gomyway-layered-rhythm-reconciliation-v1.json
?? public/gomyway-layered-rhythm-reconciliation-v2.json
?? public/gomyway-layered-section-holdout-benchmark-v1.json
?? public/gomyway-librosa-multipeak-detector-v1-manifest.json
?? public/gomyway-librosa-multipeak-detector-v1.json
?? public/gomyway-locked-event-consensus-v20.json
?? public/gomyway-locked-event-glyph-reassignment-v23.json
?? public/gomyway-locked-event-glyph-validation-v22.json
?? public/gomyway-locked-event-glyph-validation-v22/
?? public/gomyway-locked-event-pdf-glyph-localization-v21.json
?? public/gomyway-locked-event-pdf-glyph-localization-v21/
?? public/gomyway-locked-fret-digit-raw-relocalization-v39.json
?? public/gomyway-locked-fret-near-string-band-v58.json
?? public/gomyway-locked-fret-near-string-band-v58/
?? public/gomyway-locked-fret-string-intersection-v57.json
?? public/gomyway-locked-fret-string-intersection-v57/
?? public/gomyway-locked-fret-template-matching-v56.json
?? public/gomyway-locked-fret-template-matching-v56/
?? public/gomyway-locked-glyph-mask-contact-sheets-v35/
?? public/gomyway-locked-glyph-mask-contact-sheets-v37/
?? public/gomyway-locked-glyph-mask-failure-audit-v36.json
?? public/gomyway-locked-glyph-mask-rebuild-v35.json
?? public/gomyway-locked-glyph-mask-rebuild-v35/
?? public/gomyway-locked-glyph-mask-targeted-rebuild-v37.json
?? public/gomyway-locked-glyph-mask-targeted-rebuild-v37/
?? public/gomyway-locked-glyph-template-contact-sheets-v34.json
?? public/gomyway-locked-glyph-template-contact-sheets-v34/
?? public/gomyway-locked-glyph-template-library-v33.json
?? public/gomyway-locked-glyph-template-library-v33/
?? public/gomyway-locked-intro-template-source-audit-v1.json
?? public/gomyway-locked-measure-time-model-v24.json
?? public/gomyway-locked-note-event-path-discovery-v19.json
?? public/gomyway-locked-reference-provenance-audit-v17.json
?? public/gomyway-locked-reference-schema-inspection-v18.json
?? public/gomyway-locked-reference-source-discovery-v15.json
?? public/gomyway-locked-template-coverage-audit-v31.json
?? public/gomyway-locked-template-source-box-audit-v38.json
?? public/gomyway-locked-template-source-box-audit-v38/
?? public/gomyway-locked-template-technique-signatures-v32.json
?? public/gomyway-metrically-pruned-champion-extras-profile-v1-manifest.json
?? public/gomyway-metrically-pruned-champion-extras-profile-v1.json
?? public/gomyway-metrically-pruned-champion-step10-exception-v1-manifest.json
?? public/gomyway-metrically-pruned-champion-step10-exception-v1.json
?? public/gomyway-mid-register-audio-preconditioning-v1-manifest.json
?? public/gomyway-mid-register-audio-preconditioning-v1.json
?? public/gomyway-mid-register-loss-stage-v1-manifest.json
?? public/gomyway-mid-register-loss-stage-v1.json
?? public/gomyway-mid-register-preconditioning-agreement-v1-manifest.json
?? public/gomyway-mid-register-preconditioning-agreement-v1.json
?? public/gomyway-mid-register-preconditioning-crossval-v1-manifest.json
?? public/gomyway-mid-register-preconditioning-crossval-v1.json
?? public/gomyway-mid-register-spectral-specialist-section-stability-v1-manifest.json
?? public/gomyway-mid-register-spectral-specialist-section-stability-v1.json
?? public/gomyway-mid-register-spectral-specialist-v1-manifest.json
?? public/gomyway-mid-register-spectral-specialist-v1.json
?? public/gomyway-mid-register-spectral-specialist-variant-stability-v1-manifest.json
?? public/gomyway-mid-register-spectral-specialist-variant-stability-v1.json
?? public/gomyway-missing-mid-register-harmonic-context-v1-manifest.json
?? public/gomyway-missing-mid-register-harmonic-context-v1.json
?? public/gomyway-missing-render-measures-106-113-audit-v1.json
?? public/gomyway-missing-render-measures-consensus-selection-v1.json
?? public/gomyway-missing-render-measures-cross-artifact-audit-v1.json
?? public/gomyway-mrmt3-detector-v1-manifest.json
?? public/gomyway-mrmt3-detector-v1.json
?? public/gomyway-neural-polyphonic-detector-v1-manifest.json
?? public/gomyway-neural-polyphonic-detector-v1.json
?? public/gomyway-open-string-technique-glyph-recovery-v26.json
?? public/gomyway-open-string-x-offset-hypothesis-v30.json
?? public/gomyway-open-string-x-position-model-v29.json
?? public/gomyway-open-string-x-position-model-v29/
?? public/gomyway-other-stem-v8-rhythm-candidates-v1.json
?? public/gomyway-out-chorus-reference-coverage-audit-v1.json
?? public/gomyway-out-chorus-retention-benchmark-v1.json
?? public/gomyway-out-chorus-retention-conclusion-v1.json
?? public/gomyway-out-chorus-sequence-pattern-benchmark-v1.json
?? public/gomyway-out-chorus-sequence-pattern-conclusion-v1.json
?? public/gomyway-out-chorus-transition-conclusion-v1.json
?? public/gomyway-out-chorus-transition-ranking-v1.json
?? public/gomyway-out-chorus-unresolved-review-pack-v1.json
?? public/gomyway-percussive-audio-evidence-v3.json
?? public/gomyway-percussive-context-gate-search-v4.json
?? public/gomyway-percussive-hpss-evidence-v6.json
?? public/gomyway-percussive-multiwindow-evidence-v5-fullmix.json
?? public/gomyway-percussive-multiwindow-evidence-v5-other-stem.json
?? public/gomyway-percussive-rhythm-classifier-experiment.json
?? public/gomyway-percussive-rhythm-classifier-v2-experiment.json
?? public/gomyway-precision-pruned-champion-extras-profile-v2-manifest.json
?? public/gomyway-precision-pruned-champion-extras-profile-v2.json
?? public/gomyway-precision-pruned-champion-metrical-gate-v1-manifest.json
?? public/gomyway-precision-pruned-champion-metrical-gate-v1.json
?? public/gomyway-professional-fret-recognition-input-audit-v50.json
?? public/gomyway-professional-fret-recognition-jobs-v49.json
?? public/gomyway-professional-rhythm-reference-17-113-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-merge-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-review-packet.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32-review-packet.txt
?? public/gomyway-professional-rhythm-reference-chunk-17-32-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-17-32.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-review-packet.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-review-packet.txt
?? public/gomyway-professional-rhythm-reference-chunk-33-48-source-resolved.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-33-48.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-source-resolved.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-49-64.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-review-packet.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-review-packet.txt
?? public/gomyway-professional-rhythm-reference-chunk-65-80-source-resolved.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-source-reviewed.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-65-80.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-source-resolved.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-81-96.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-final-approved.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-populated-audit.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-populated.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-repeat-confirmed.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-source-resolved.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113-validation.json
?? public/gomyway-professional-rhythm-reference-chunk-97-113.json
?? public/gomyway-professional-rhythm-reference-consensus-candidates-17-113.json
?? public/gomyway-professional-rhythm-reference-consensus-candidates-17-113.txt
?? public/gomyway-professional-rhythm-reference-full-machine-report.json
?? public/gomyway-professional-rhythm-reference-full-machine.json
?? public/gomyway-professional-rhythm-reference-full-review-17-113.json
?? public/gomyway-professional-rhythm-reference-full-review-17-113.txt
?? public/gomyway-professional-rhythm-reference-full-review-after-all-source-resolution.json
?? public/gomyway-professional-rhythm-reference-full-review-after-all-source-resolution.txt
?? public/gomyway-professional-rhythm-reference-full-review-after-chorus-resolution.json
?? public/gomyway-professional-rhythm-reference-full-review-after-chorus-resolution.txt
?? public/gomyway-professional-rhythm-reference-manual-review-31-measures.json
?? public/gomyway-professional-rhythm-reference-manual-review-31-measures.txt
?? public/gomyway-professional-string-row-coordinates-v51.json
?? public/gomyway-professional-string-row-coordinates-v51/
?? public/gomyway-protected-pdf-comparison-input-audit-v1.json
?? public/gomyway-protected-pdf-notation-input-gate-v1.json
?? public/gomyway-raw-digit-line-suppression-calibration-v40.json
?? public/gomyway-raw-row-coordinate-model-v41.json
?? public/gomyway-renderable-rhythm-event-source-audit-v1.json
?? public/gomyway-repeated-chorus-soft-ranking-v1.json
?? public/gomyway-repeated-chorus-transfer-conclusion-v1.json
?? public/gomyway-rhythm-anchor-36-whole-song-impact-review-v1-manifest.json
?? public/gomyway-rhythm-anchor-36-whole-song-impact-review-v1.json
?? public/gomyway-rhythm-anchor-51-whole-song-impact-review-v1-manifest.json
?? public/gomyway-rhythm-anchor-51-whole-song-impact-review-v1.json
?? public/gomyway-rhythm-learned-rules-whole-song-projection-v1-manifest.json
?? public/gomyway-rhythm-learned-rules-whole-song-projection-v1.json
?? public/gomyway-rhythm-measure-101-placement-diagnostic-v1-manifest.json
?? public/gomyway-rhythm-measure-101-placement-diagnostic-v1.json
?? public/gomyway-rhythm-measure-101-placement-variant-review-v1-manifest.json
?? public/gomyway-rhythm-measure-101-placement-variant-review-v1.json
?? public/gomyway-rhythm-next-novel-training-anchors-review-v1-manifest.json
?? public/gomyway-rhythm-next-novel-training-anchors-review-v1.json
?? public/gomyway-rhythm-next-novel-training-anchors-v1-manifest.json
?? public/gomyway-rhythm-next-novel-training-anchors-v1.json
?? public/gomyway-rhythm-novel-anchor-36-read-only-registration-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-36-read-only-registration-v1.json
?? public/gomyway-rhythm-novel-anchor-36-training-review-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-36-training-review-v1.json
?? public/gomyway-rhythm-novel-anchor-36-training-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-36-training-v1.json
?? public/gomyway-rhythm-novel-anchor-51-read-only-registration-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-51-read-only-registration-v1.json
?? public/gomyway-rhythm-novel-anchor-51-training-review-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-51-training-review-v1.json
?? public/gomyway-rhythm-novel-anchor-51-training-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-51-training-v1.json
?? public/gomyway-rhythm-novel-anchor-60-training-v1-manifest.json
?? public/gomyway-rhythm-novel-anchor-60-training-v1.json
?? public/gomyway-rhythm-pdf-canonical-row-crops-v10/
?? public/gomyway-rhythm-pdf-canonical-row-localization-v10.json
?? public/gomyway-rhythm-pdf-canonical-row-manifest-v9.json
?? public/gomyway-rhythm-pdf-measure-anchor-manifest-v8.json
?? public/gomyway-rhythm-pdf-raster-pages-v2/
?? public/gomyway-rhythm-pdf-raster-pages-v3/
?? public/gomyway-rhythm-pdf-raster-pages-v4/
?? public/gomyway-rhythm-pdf-raster-pages-v5/
?? public/gomyway-rhythm-pdf-raster-pages-v6/
?? public/gomyway-rhythm-pdf-raster-pages/
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v2.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v3.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v4.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v5.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v6.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic-v7.json
?? public/gomyway-rhythm-pdf-raster-structure-diagnostic.json
?? public/gomyway-rhythm-pdf-row-review-pack-v11.json
?? public/gomyway-rhythm-pdf-row-review-pack-v11/
?? public/gomyway-rhythm-pdf-visual-validation-v12.json
?? public/gomyway-rhythm-pitch-error-model-v1-manifest.json
?? public/gomyway-rhythm-pitch-error-model-v1.json
?? public/gomyway-rhythm-pitch-first-training-batch-v1-manifest.json
?? public/gomyway-rhythm-pitch-first-training-batch-v1.json
?? public/gomyway-rhythm-professional-glyph-hypotheses-v14.json
?? public/gomyway-rhythm-professional-glyph-hypotheses-v14/
?? public/gomyway-rhythm-professional-grade-training-plan-v2-manifest.json
?? public/gomyway-rhythm-professional-grade-training-plan-v2.json
?? public/gomyway-rhythm-professional-grade-v1-manifest.json
?? public/gomyway-rhythm-professional-grade-v1.json
?? public/gomyway-rhythm-professional-grade-v2-manifest.json
?? public/gomyway-rhythm-professional-grade-v2.json
?? public/gomyway-rhythm-professional-pitch-vs-tab-diagnostic-v1.json
?? public/gomyway-rhythm-professional-symbol-candidates-v13.json
?? public/gomyway-rhythm-professional-symbol-candidates-v13/
?? public/gomyway-rhythm-provisional-rule-transfer-evidence-review-v1-manifest.json
?? public/gomyway-rhythm-provisional-rule-transfer-evidence-review-v1.json
?? public/gomyway-rhythm-provisional-rule-transfer-evidence-v1-manifest.json
?? public/gomyway-rhythm-provisional-rule-transfer-evidence-v1.json
?? public/gomyway-rhythm-structure-transfer-proof-review-v1-manifest.json
?? public/gomyway-rhythm-structure-transfer-proof-review-v1.json
?? public/gomyway-rhythm-structure-transfer-proof-v1-manifest.json
?? public/gomyway-rhythm-structure-transfer-proof-v1.json
?? public/gomyway-rhythm-whole-song-generalization-closure-review-v1-manifest.json
?? public/gomyway-rhythm-whole-song-generalization-closure-review-v1.json
?? public/gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1-manifest.json
?? public/gomyway-rhythm-whole-song-learned-similarity-diagnostic-v1.json
?? public/gomyway-rhythm-whole-song-provisional-generalization-proof-review-v1-manifest.json
?? public/gomyway-rhythm-whole-song-provisional-generalization-proof-review-v1.json
?? public/gomyway-rhythm-whole-song-provisional-generalization-proof-v1-manifest.json
?? public/gomyway-rhythm-whole-song-provisional-generalization-proof-v1.json
?? public/gomyway-rhythm-whole-song-similarity-calibration-review-v1-manifest.json
?? public/gomyway-rhythm-whole-song-similarity-calibration-review-v1.json
?? public/gomyway-rhythm-whole-song-similarity-threshold-calibration-v1-manifest.json
?? public/gomyway-rhythm-whole-song-similarity-threshold-calibration-v1.json
?? public/gomyway-rhythm-whole-song-with-anchor-36-v1-manifest.json
?? public/gomyway-rhythm-whole-song-with-anchor-36-v1.json
?? public/gomyway-rhythm-whole-song-with-anchors-36-51-v1-manifest.json
?? public/gomyway-rhythm-whole-song-with-anchors-36-51-v1.json
?? public/gomyway-row-local-string-lattices-v60.json
?? public/gomyway-row-local-string-lattices-v60/
?? public/gomyway-row-specific-string-line-calibration-v43.json
?? public/gomyway-row-specific-string-line-calibration-v43/
?? public/gomyway-selective-recall-admission-v1-manifest.json
?? public/gomyway-selective-recall-admission-v1.json
?? public/gomyway-selective-recall-heldout-v1-manifest.json
?? public/gomyway-selective-recall-heldout-v1.json
?? public/gomyway-separator-gpu-benchmark-v1.json
?? public/gomyway-separator-upgrade-benchmark-v2-codespace-manifest.json
?? public/gomyway-separator-upgrade-benchmark-v2-codespace.json
?? public/gomyway-spectral-specialist-failure-structure-v1-manifest.json
?? public/gomyway-spectral-specialist-failure-structure-v1.json
?? public/gomyway-spectral-specialist-precision-gate-v1-manifest.json
?? public/gomyway-spectral-specialist-precision-gate-v1.json
?? public/gomyway-spectral-top1-adaptive-local-gate-v1-manifest.json
?? public/gomyway-spectral-top1-adaptive-local-gate-v1.json
?? public/gomyway-spectral-top1-block-density-profile-v1-manifest.json
?? public/gomyway-spectral-top1-block-density-profile-v1.json
?? public/gomyway-step10-agreement-gate-v1-manifest.json
?? public/gomyway-step10-agreement-gate-v1.json
?? public/gomyway-step10-agreement-pruned-champion-cross-signature-gate-v1-manifest.json
?? public/gomyway-step10-agreement-pruned-champion-cross-signature-gate-v1.json
?? public/gomyway-step10-agreement-pruned-champion-extras-profile-v1-manifest.json
?? public/gomyway-step10-agreement-pruned-champion-extras-profile-v1.json
?? public/gomyway-step10-pruned-champion-extras-profile-v1-manifest.json
?? public/gomyway-step10-pruned-champion-extras-profile-v1.json
?? public/gomyway-string-band-fret-recognition-v59.json
?? public/gomyway-string-band-fret-recognition-v59/
?? public/gomyway-string-line-geometry-calibration-v45.json
?? public/gomyway-string-line-geometry-calibration-v45/
?? public/gomyway-string-line-geometry-consensus-v46.json
?? public/gomyway-string-line-geometry-human-validation-v47.json
?? public/gomyway-tab-system-band-recovery-v64.json
?? public/gomyway-tab-system-band-recovery-v64/
?? public/gomyway-targeted-rhythm-correction-plan.json
?? public/gomyway-targeted-rhythm-correction-plan.txt
?? public/gomyway-temporal-champion-precision-pruning-v1-manifest.json
?? public/gomyway-temporal-champion-precision-pruning-v1.json
?? public/gomyway-temporal-recurrence-champion-extras-profile-v1-manifest.json
?? public/gomyway-temporal-recurrence-champion-extras-profile-v1.json
?? public/gomyway-unmatched-locked-glyph-slots-v25.json
?? public/gomyway-unresolved-open-string-adjacent-string-audit-v28.json
?? public/gomyway-unresolved-open-string-adjacent-string-audit-v28/
?? public/gomyway-unresolved-open-string-pixel-inspection-v27.json
?? public/gomyway-unresolved-open-string-pixel-inspection-v27/
?? public/gomyway-v43-row-specific-calibration-outliers-v44.json
?? public/gomyway-v51-canonical-fret-recognition-input-v55.json
?? public/gomyway-v53-geometry-failure-audit-v54.json
?? public/gomyway-v53-geometry-failure-audit-v54/
?? public/gomyway-v55-v60-coordinate-frame-audit-v62.json
?? public/gomyway-v55-v60-coordinate-frame-audit-v62/
?? public/gomyway-v60-row-local-string-lattice-failure-audit-v61.json
?? public/gomyway-v60-row-local-string-lattice-failure-audit-v61/
?? public/gomyway-v64-failure-gate-audit-v65.json
?? public/gomyway-v8-full-rhythm-proof-v1-manifest.json
?? public/gomyway-v8-full-rhythm-proof-v1.pdf
?? public/gomyway-v8-full-rhythm-sustain-proof-v2-manifest.json
?? public/gomyway-v8-full-rhythm-sustain-proof-v2.pdf
?? public/gomyway-v8-full-rhythm-sustain-proof-v4-manifest.json
?? public/gomyway-v8-full-rhythm-sustain-proof-v4.pdf
?? public/gomyway-v8-full-rhythm-sustain-proof-v5-manifest.json
?? public/gomyway-v8-full-rhythm-sustain-proof-v5.pdf
?? public/gomyway-v8-intro-first-rhythm-proof-v1-manifest.json
?? public/gomyway-v8-intro-first-rhythm-proof-v1.pdf
?? public/gomyway-v8-intro-renderability-diagnosis-v1.json
?? public/gomyway-v8-notation-projection-source-audit-v1.json
?? public/gomyway-v8-professional-intro-notation-proof-v4-manifest.json
?? public/gomyway-v8-professional-intro-notation-proof-v4.pdf
?? public/gomyway-v8-professional-intro-notation-proof-v5-manifest.json
?? public/gomyway-v8-professional-intro-notation-proof-v5.pdf
?? public/gomyway-v8-professional-intro-notation-proof-v6-manifest.json
?? public/gomyway-v8-professional-intro-notation-proof-v6.pdf
?? public/gomyway-v8-professional-intro-notation-proof-v7-manifest.json
?? public/gomyway-v8-professional-intro-notation-proof-v7.pdf
?? public/gomyway-v8-repeat-consensus-intro-proof-v3-manifest.json
?? public/gomyway-v8-repeat-consensus-intro-proof-v3.pdf
?? public/gomyway-v8-supervised-intro-overlay-v1.json
?? public/gomyway-v8-supervised-intro-overlay-v2.json
?? public/gomyway-v8-supervised-intro-overlay-v3-manifest.json
?? public/gomyway-v8-supervised-intro-overlay-v3.json
?? public/gomyway-v8-supervised-intro-proof-v1-manifest.json
?? public/gomyway-v8-supervised-intro-proof-v1.pdf
?? public/gomyway-v8-supervised-intro-proof-v2-manifest.json
?? public/gomyway-v8-supervised-intro-proof-v2.pdf
?? public/gomyway-vertical-string-offset-recovery-v63.json
?? public/gomyway-vertical-string-offset-recovery-v63/
?? public/gomyway-zero-precision-pruned-909-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-909-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-910-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-910-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-916-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-916-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-919-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-919-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-921-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-921-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-923-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-923-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-926-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-926-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-927-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-927-champion-residual-extras-profile-v1.json
?? public/gomyway-zero-precision-pruned-929-champion-residual-extras-profile-v1-manifest.json
?? public/gomyway-zero-precision-pruned-929-champion-residual-extras-profile-v1.json
?? public/jimmy-paige-midterm-v1/corrected-separation-v2/
?? public/jimmy-paige-midterm-v1/jimmy-midterm-113-measure-professional-score-v1.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-113-measure-rhythm-midterm-grade-v2.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-grader-adapter-v1.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-grader-adapter-v2.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-measures-v1-audit.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-measures-v1.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-measures-v2-audit.json
?? public/jimmy-paige-midterm-v1/jimmy-v134-blind-113-measures-v2.json
?? public/jimmy-paige-midterm-v1/midterm-audio-only-22050-mono.wav
?? public/jimmy-paige-midterm-v1/professional-113-grader-adapter-v2.json
?? public/jimmy-paige-midterm-v1/professional-113-grader-adapter-v3.json
?? public/professional-tablature-notation-standard-lock-v1.json
?? public/separator-benchmark-gpu-v1/
?? public/separator-benchmark-v2-forensic-replay/
?? public/separator-benchmark-v2/
?? public/training/gomyway-out-chorus-listening-window-pack-v1/
?? public/training/gomyway-protected-pdf-raster-comparison-pack-v1/
?? public/training/gomyway-v8-genuine-tab-review-v1/
?? public/training/v137-selective-sustain-development/v137-training-only-selector.json
?? public/training/v138-cross-band-sustain-development/v138-training-only-selector.json
?? public/training/v139-temporal-persistence-development/v139-training-only-selector.json
?? public/training/v140-attack-tail-coupling-development/v140-training-only-selector.json
?? public/training/v143-final-multifamily-development/v143-production-finalfit-evaluation-v1.json
?? public/training/v143-final-multifamily-development/v143-production-finalfit-metrics-v3.json
?? public/training/v143-final-multifamily-development/v143-production-finalfit-selection-v2.json
?? public/training/v143-final-multifamily-development/v143-production-finalfit-spec-v1.json
?? public/training/v143-final-multifamily-development/v143-production-policy-v1.json
?? public/training/v143-final-multifamily-development/v143-training-only-selector.json
?? public/training/v143-modal-domain-adaptation-v1/
?? public/training/v143-musical-reconstruction-calibration/baseline-intro-grade.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section2-duration-state-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section2-first-reference-event-grade.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section2-mix-contrast-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section2-transient-state-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section3-duration-state-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section3-first-reference-event-grade.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section3-mix-contrast-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-section3-transient-state-cache.json
?? public/training/v143-musical-reconstruction-calibration/fresh-verse1-first-reference-grade.json
?? public/training/v143-musical-reconstruction-calibration/fresh-verse1-frozen-predictions.json
?? public/training/v143-musical-reconstruction-calibration/fresh-verse1-reference-free-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-analysis-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-consensus-alignment-refinement-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-consensus-alignment-refinement-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-constrained-count-reranker-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-constrained-count-reranker-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-correlation-safe-attack-novelty-gate-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-correlation-safe-attack-novelty-gate-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-harmonic-family-rank-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-joint-sparse-pitchset-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-kong-pitch-benchmark.json
?? public/training/v143-musical-reconstruction-calibration/intro-learned-grid-event-selector-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-learned-grid-event-selector-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-learned-onset-spectral-set-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-learned-onset-spectral-set-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-onset-group-sequence-model-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-onset-group-sequence-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-onset-spectrum-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-pitch-recovery-neighbor-sweep.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-harmonic-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-harmonic-rank-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-pair-ranker-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-pair-ranker-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-pitch-rank-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-raw-attack-temporal-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-repetition-consensus-decoder-fast.json
?? public/training/v143-musical-reconstruction-calibration/intro-repetition-recovery-event-selector-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-selection-recovery-sweep.json
?? public/training/v143-musical-reconstruction-calibration/intro-sequence-event-model-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-sequence-event-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-softlabel-temporal-assignment-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-softlabel-temporal-assignment-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-spectral-pitch-cache.json
?? public/training/v143-musical-reconstruction-calibration/intro-spectral-pitch-ranker-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-spectral-pitch-ranker-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-stage-diagnostic.json
?? public/training/v143-musical-reconstruction-calibration/intro-structured-event-decoder-check-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-structured-event-decoder-check-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-supervised-pitch-ranker-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-supervised-pitch-ranker-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-supervised-temporal-assignment-model.json
?? public/training/v143-musical-reconstruction-calibration/intro-supervised-temporal-assignment-report.json
?? public/training/v143-musical-reconstruction-calibration/intro-synthtab-tabcnn-benchmark.json
?? public/training/v143-musical-reconstruction-calibration/intro-temporal-assignment-oracle.json
?? public/v143-modal-replay/
?? "sional|REFERENCE.*gomyway-professional|Path.*gomyway-professional|professional.*reference.*json' "
```


## analyzer/v143_intro_structured_event_decoder_check.py

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

import v143_intro_constrained_count_reranker as constrained
import v143_intro_sequence_event_model as sequence
import v143_intro_onset_group_sequence_model as onset
import v143_intro_consensus_alignment_refinement as consensus
from v143_intro_raw_attack_temporal_diagnostic import (
    CACHE_PATH as RAW_CACHE_PATH,
    REFERENCE_PATH,
    _grid_lookup,
)
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    MODEL_PATH as BASE_SELECTOR_MODEL_PATH,
    TRAIN_MEASURES,
    VALIDATION_MEASURES,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    _rows_by_measure,
)


CONSTRAINED_MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-constrained-count-reranker-model.json"
)
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-structured-event-decoder-check-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-structured-event-decoder-check-model.json"
)

COUNT_POLICIES = ("block", "per-measure")
COUNT_MULTIPLIERS = (0.90, 0.95, 1.00, 1.05, 1.10)
SEQUENCE_WEIGHTS = (0.0, 0.25, 0.5, 1.0)
RECURRENCE_WEIGHTS = (0.0, 0.25, 0.5, 1.0)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _rank_percentiles(
    values: dict[tuple[int, int], float],
    keys: list[tuple[int, int]],
    *,
    per_measure: bool,
) -> dict[tuple[int, int], float]:
    out: dict[tuple[int, int], float] = {}
    groups: dict[int, list[tuple[int, int]]] = {}
    if per_measure:
        for key in keys:
            groups.setdefault(int(key[0]), []).append(key)
    else:
        groups[0] = list(keys)

    for group_keys in groups.values():
        ranked = sorted(
            group_keys,
            key=lambda key: (float(values.get(key, 0.0)), key),
        )
        n = len(ranked)
        if n <= 1:
            for key in ranked:
                out[key] = 1.0
            continue
        for index, key in enumerate(ranked):
            out[key] = float(index) / float(n - 1)
    return out


def _recurrence_support(
    keys: list[tuple[int, int]],
    rerank_percentiles: dict[tuple[int, int], float],
) -> dict[tuple[int, int], float]:
    key_set = set(keys)
    measures = sorted({int(key[0]) for key in keys})
    result: dict[tuple[int, int], float] = {}
    for key in keys:
        measure, step = int(key[0]), int(key[1])
        all_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure and (other, step) in key_set
        ]
        phase2_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure
            and (other - 1) % 2 == (measure - 1) % 2
            and (other, step) in key_set
        ]
        phase4_peers = [
            float(rerank_percentiles[(other, step)])
            for other in measures
            if other != measure
            and (other - 1) % 4 == (measure - 1) % 4
            and (other, step) in key_set
        ]
        candidates = []
        if all_peers:
            candidates.append(float(np.mean(all_peers)))
        if phase2_peers:
            candidates.append(float(np.mean(phase2_peers)))
        if phase4_peers:
            candidates.append(float(np.mean(phase4_peers)))
        result[key] = max(candidates) if candidates else 0.0
    return result


def _component_maps(
    ds: dict[str, Any],
    sequence_scores: dict[tuple[int, int], float],
    mean: np.ndarray,
    std: np.ndarray,
    weights: np.ndarray,
) -> tuple[
    list[tuple[int, int]],
    dict[tuple[int, int], float],
    dict[tuple[int, int], float],
    dict[tuple[int, int], float],
]:
    keys = [
        key
        for key, evidence in zip(ds["keys"], ds["evidence"])
        if bool(evidence)
    ]
    raw_scores = constrained._scores(ds["X"], mean, std, weights)
    rerank_values = {
        key: float(score)
        for key, score, evidence in zip(ds["keys"], raw_scores, ds["evidence"])
        if bool(evidence)
    }
    sequence_values = {
        key: float(sequence_scores.get(key, 0.0))
        for key in keys
    }
    rerank_pct = _rank_percentiles(rerank_values, keys, per_measure=True)
    sequence_pct = _rank_percentiles(sequence_values, keys, per_measure=True)
    recurrence = _recurrence_support(keys, rerank_pct)
    return keys, rerank_pct, sequence_pct, recurrence


def _combined_scores(
    keys: list[tuple[int, int]],
    rerank_pct: dict[tuple[int, int], float],
    sequence_pct: dict[tuple[int, int], float],
    recurrence: dict[tuple[int, int], float],
    sequence_weight: float,
    recurrence_weight: float,
) -> dict[tuple[int, int], float]:
    return {
        key: (
            float(rerank_pct.get(key, 0.0))
            + float(sequence_weight) * float(sequence_pct.get(key, 0.0))
            + float(recurrence_weight) * float(recurrence.get(key, 0.0))
        )
        for key in keys
    }


def _scaled_count(count: int, multiplier: float, eligible_count: int) -> int:
    if count <= 0 or eligible_count <= 0:
        return 0
    target = int(round(float(count) * float(multiplier)))
    return max(1, min(target, eligible_count))


def _select(
    keys: list[tuple[int, int]],
    combined: dict[tuple[int, int], float],
    baseline_active: set[tuple[int, int]],
    policy: str,
    multiplier: float,
) -> set[tuple[int, int]]:
    if not keys:
        return set()
    if policy == "block":
        k = _scaled_count(len(baseline_active), multiplier, len(keys))
        ranked = sorted(keys, key=lambda key: (-combined[key], key))
        return set(ranked[:k])
    if policy == "per-measure":
        selected: set[tuple[int, int]] = set()
        measures = sorted({int(key[0]) for key in keys})
        for measure in measures:
            measure_keys = [key for key in keys if int(key[0]) == measure]
            baseline_count = sum(1 for key in baseline_active if int(key[0]) == measure)
            k = _scaled_count(baseline_count, multiplier, len(measure_keys))
            ranked = sorted(measure_keys, key=lambda key: (-combined[key], key))
            selected.update(ranked[:k])
        return selected
    raise ValueError(f"Unknown policy: {policy}")


def _objective(location: dict[str, Any], end_to_end: dict[str, Any]) -> float:
    precision = float(location["locationPrecisionPercent"])
    recall = float(location["locationRecallPercent"])
    location_f1 = float(location["locationF1Percent"])
    pitch_f1 = float(end_to_end["pitchF1Percent"])
    exact = float(end_to_end["exactPitchSetPercent"])
    score = (
        0.40 * pitch_f1
        + 0.30 * location_f1
        + 0.15 * precision
        + 0.10 * recall
        + 0.05 * exact
    )
    if precision < 75.0:
        score -= 1.5 * (75.0 - precision)
    if recall < 80.0:
        score -= 1.0 * (80.0 - recall)
    return float(score)


def _evaluate(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    onset_scores: dict[int, float],
    pitch_model: dict[str, Any],
    constrained_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    return constrained._evaluate_selection(
        active,
        reference,
        rows_by_measure,
        grid,
        onset_scores,
        pitch_model,
        int(constrained_model["assignWindowMs"]),
        float(constrained_model["residualPenalty"]),
    )


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    sequence_model = _load_json(sequence.MODEL_PATH)
    onset_model = _load_json(onset.MODEL_PATH)
    constrained_model = _load_json(CONSTRAINED_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)
    spectrum_len = int(spectrum_cache.get("spectrumMidiMax") or 112) - int(
        spectrum_cache.get("spectrumMidiMin") or 28
    ) + 1

    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)
    all_measures = set(range(1, 17))

    base_scores, base_evidence = consensus._score_measures(
        rows_by_measure,
        grid,
        all_measures,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])

    mean = np.asarray(constrained_model["featureMean"], dtype=np.float64)
    std = np.asarray(constrained_model["featureStd"], dtype=np.float64)
    weights = np.asarray(constrained_model["weights"], dtype=np.float64)

    validation, val_seq, val_seq_evidence, val_onset = constrained._split_scores(
        rows_by_measure,
        grid,
        validation_reference,
        VALIDATION_MEASURES,
        set(range(1, 13)),
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )
    development, dev_seq, dev_seq_evidence, dev_onset = constrained._split_scores(
        rows_by_measure,
        grid,
        development_reference,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )
    holdout, hold_seq, hold_seq_evidence, hold_onset = constrained._split_scores(
        rows_by_measure,
        grid,
        holdout_reference,
        HOLDOUT_MEASURES,
        all_measures,
        spectrum_len,
        base_scores,
        base_evidence,
        base_threshold,
        sequence_model,
        onset_model,
    )

    val_baseline = constrained._baseline_active(
        validation["keys"], val_seq, val_seq_evidence, float(sequence_model["threshold"])
    )
    dev_baseline = constrained._baseline_active(
        development["keys"], dev_seq, dev_seq_evidence, float(sequence_model["threshold"])
    )
    hold_baseline = constrained._baseline_active(
        holdout["keys"], hold_seq, hold_seq_evidence, float(sequence_model["threshold"])
    )

    val_components = _component_maps(validation, val_seq, mean, std, weights)
    dev_components = _component_maps(development, dev_seq, mean, std, weights)
    hold_components = _component_maps(holdout, hold_seq, mean, std, weights)

    print("=== V143 FINAL STRUCTURED EVENT DECODER CHECK ===")
    print("Purpose: preserve the constrained reranker's precision while recovering omitted recurrent events")
    print("Configuration chosen on measures 9-12 only")
    print("Measures 13-16 are diagnostic only; not a fresh untouched holdout")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    searched = 0
    total = (
        len(COUNT_POLICIES)
        * len(COUNT_MULTIPLIERS)
        * len(SEQUENCE_WEIGHTS)
        * len(RECURRENCE_WEIGHTS)
    )
    val_keys, val_rerank, val_sequence, val_recurrence = val_components
    for policy in COUNT_POLICIES:
        for multiplier in COUNT_MULTIPLIERS:
            for sequence_weight in SEQUENCE_WEIGHTS:
                for recurrence_weight in RECURRENCE_WEIGHTS:
                    searched += 1
                    combined = _combined_scores(
                        val_keys,
                        val_rerank,
                        val_sequence,
                        val_recurrence,
                        sequence_weight,
                        recurrence_weight,
                    )
                    active = _select(
                        val_keys,
                        combined,
                        val_baseline,
                        policy,
                        multiplier,
                    )
                    loc, e2e = _evaluate(
                        active,
                        validation_reference,
                        rows_by_measure,
                        grid,
                        val_onset,
                        pitch_model,
                        constrained_model,
                    )
                    objective = _objective(loc, e2e)
                    candidate = {
                        "countPolicy": policy,
                        "countMultiplier": float(multiplier),
                        "sequenceWeight": float(sequence_weight),
                        "recurrenceWeight": float(recurrence_weight),
                        "validationObjectivePercent": round(objective, 3),
                        "validationLocation": loc,
                        "validationEndToEnd": e2e,
                    }
                    if best is None or (
                        objective,
                        float(e2e["pitchF1Percent"]),
                        float(loc["locationF1Percent"]),
                        float(loc["locationRecallPercent"]),
                        float(loc["locationPrecisionPercent"]),
                    ) > (
                        float(best["validationObjectivePercent"]),
                        float(best["validationEndToEnd"]["pitchF1Percent"]),
                        float(best["validationLocation"]["locationF1Percent"]),
                        float(best["validationLocation"]["locationRecallPercent"]),
                        float(best["validationLocation"]["locationPrecisionPercent"]),
                    ):
                        best = candidate
                    if searched % 40 == 0 or searched == total:
                        print(f"searched {searched}/{total} structured configurations")

    if best is None:
        raise RuntimeError("No structured configuration evaluated")

    def run_split(
        components: tuple[
            list[tuple[int, int]],
            dict[tuple[int, int], float],
            dict[tuple[int, int], float],
            dict[tuple[int, int], float],
        ],
        baseline: set[tuple[int, int]],
        reference: dict[tuple[int, int], set[int]],
        onset_scores: dict[int, float],
    ) -> tuple[set[tuple[int, int]], dict[str, Any], dict[str, Any]]:
        keys, rerank_pct, sequence_pct, recurrence = components
        combined = _combined_scores(
            keys,
            rerank_pct,
            sequence_pct,
            recurrence,
            float(best["sequenceWeight"]),
            float(best["recurrenceWeight"]),
        )
        active = _select(
            keys,
            combined,
            baseline,
            str(best["countPolicy"]),
            float(best["countMultiplier"]),
        )
        loc, e2e = _evaluate(
            active,
            reference,
            rows_by_measure,
            grid,
            onset_scores,
            pitch_model,
            constrained_model,
        )
        return active, loc, e2e

    dev_active, dev_loc, dev_e2e = run_split(
        dev_components, dev_baseline, development_reference, dev_onset
    )
    hold_active, hold_loc, hold_e2e = run_split(
        hold_components, hold_baseline, holdout_reference, hold_onset
    )

    report = {
        "model": "v143-final-structured-event-decoder-check",
        "bestConfiguration": {
            key: best[key]
            for key in (
                "countPolicy",
                "countMultiplier",
                "sequenceWeight",
                "recurrenceWeight",
                "validationObjectivePercent",
            )
        },
        "validationLocation": best["validationLocation"],
        "validationEndToEnd": best["validationEndToEnd"],
        "developmentLocation": dev_loc,
        "developmentEndToEnd": dev_e2e,
        "diagnosticHoldoutLocation": hold_loc,
        "diagnosticHoldoutEndToEnd": hold_e2e,
        "sequenceBaselineCounts": {
            "validation": len(val_baseline),
            "development": len(dev_baseline),
            "diagnosticHoldout": len(hold_baseline),
        },
        "structuredSelectedCounts": {
            "development": len(dev_active),
            "diagnosticHoldout": len(hold_active),
        },
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because architecture decisions have already inspected them. A fresh unseen song/section is mandatory before any production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                **report["bestConfiguration"],
                "assignWindowMs": int(constrained_model["assignWindowMs"]),
                "residualPenalty": float(constrained_model["residualPenalty"]),
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION STRUCTURED CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== VALIDATION END-TO-END 9-12 ===")
    print(json.dumps(report["validationEndToEnd"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutEndToEnd"], indent=2))
    print("\nSequence baseline holdout count:", len(hold_baseline))
    print("Structured selected holdout count:", len(hold_active))

    precision = float(hold_loc["locationPrecisionPercent"])
    recall = float(hold_loc["locationRecallPercent"])
    pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 78.0:
        diagnosis = "structured-decoder-passes-calibration-gate-freeze-core-and-test-fresh-unseen-section"
    elif precision >= 75.0 and recall >= 80.0 and pitch_f1 >= 75.0:
        diagnosis = "structured-decoder-near-gate-do-not-retune-on-this-diagnostic-move-to-fresh-section"
    else:
        diagnosis = "structured-decoder-insufficient-do-not-freeze-event-core"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("NOTE: measures 13-16 are diagnostic, not a fresh untouched holdout anymore.")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()

```


## analyzer/v143_intro_supervised_pitch_ranker.py

```python
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-pitch-ranker-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-pitch-ranker-model.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
RADII = (1, 2)
POSITIVE_CLASS_WEIGHTS = (2.0, 4.0, 8.0, 12.0)
L2_VALUES = (0.001, 0.01, 0.05, 0.10)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(17))
TOP_K_VALUES = (1, 2, 3)

FEATURE_NAMES = (
    "exact_present",
    "nearest_support",
    "support_row_fraction",
    "distance_weighted_support",
    "max_source_count",
    "mean_source_count",
    "max_event_count",
    "max_amplitude",
    "mean_amplitude",
    "grid_accuracy",
    "max_duration",
    "dominant_exact",
    "dominant_support_fraction",
    "v143_rank_percentile",
    "v143_selected",
    "target_pitch_count",
    "same_step_measure_recurrence",
    "distance_from_target_dominant",
)


def _int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
        return result if math.isfinite(result) else default
    except (TypeError, ValueError):
        return default


def _global_step(row: dict[str, Any]) -> int:
    measure = int(row.get("measure", row.get("measureNumber", 0)) or 0)
    step = int(row.get("step", 0) or 0)
    return (measure - 1) * 16 + step


def _location(row: dict[str, Any]) -> tuple[int, int]:
    return (
        int(row.get("measure", row.get("measureNumber", 0)) or 0),
        int(row.get("step", 0) or 0),
    )


def _reference_by_location(payload: dict[str, Any]) -> dict[tuple[int, int], set[int]]:
    out: dict[tuple[int, int], set[int]] = {}
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number < 1 or number > 16:
            continue
        for event in measure.get("events", []) or []:
            if not isinstance(event, dict):
                continue
            midi = _int(event.get("midiPitch"))
            if midi is None:
                continue
            step = int(event.get("step") or 0)
            out.setdefault((number, step), set()).add(midi)
    return out


def _hypotheses(row: dict[str, Any]) -> list[dict[str, Any]]:
    values: list[dict[str, Any]] = []
    for raw in row.get("pitchHypotheses", []) or []:
        if not isinstance(raw, dict):
            continue
        midi = _int(raw.get("midi"))
        if midi is None:
            continue
        item = dict(raw)
        item["midi"] = midi
        values.append(item)
    return values


def _midi_set(row: dict[str, Any]) -> set[int]:
    return {int(item["midi"]) for item in _hypotheses(row)}


def _rank_percentile(row: dict[str, Any], total_rows: int) -> float:
    rank = _int(row.get("v143Rank"))
    if rank is None or total_rows <= 1:
        return 0.5
    return float(np.clip(1.0 - (rank - 1) / float(total_rows - 1), 0.0, 1.0))


def _build_feature_context(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_global = {_global_step(row): row for row in rows}
    by_location = {_location(row): row for row in rows}
    total_rows = len(rows)
    return {
        "rows": rows,
        "byGlobal": by_global,
        "byLocation": by_location,
        "totalRows": total_rows,
    }


def _candidate_midis_for_target(
    target: dict[str, Any],
    context: dict[str, Any],
    radius: int,
) -> set[int]:
    center = _global_step(target)
    values: set[int] = set()
    for delta in range(-radius, radius + 1):
        row = context["byGlobal"].get(center + delta)
        if row is not None:
            values.update(_midi_set(row))
    return values


def _features_for_candidate(
    target: dict[str, Any],
    midi: int,
    context: dict[str, Any],
    radius: int,
) -> np.ndarray:
    center = _global_step(target)
    observations: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    dominant_support = 0
    exact_present = 0.0
    dominant_exact = 0.0

    for delta in range(-radius, radius + 1):
        row = context["byGlobal"].get(center + delta)
        if row is None:
            continue
        if _int(row.get("dominantMidi")) == midi:
            dominant_support += 1
            if delta == 0:
                dominant_exact = 1.0
        for hypothesis in _hypotheses(row):
            if int(hypothesis["midi"]) == midi:
                observations.append((delta, hypothesis, row))
                if delta == 0:
                    exact_present = 1.0

    if not observations:
        raise ValueError("candidate MIDI has no supporting observation")

    abs_deltas = [abs(delta) for delta, _hyp, _row in observations]
    support_deltas = {delta for delta, _hyp, _row in observations}
    nearest_delta = min(abs_deltas)
    normalizer = sum(1.0 / (1.0 + abs(delta)) for delta in range(-radius, radius + 1))
    weighted_support = sum(1.0 / (1.0 + abs(delta)) for delta in support_deltas)

    source_counts = [_float(hyp.get("sourceCount")) for _d, hyp, _r in observations]
    event_counts = [_float(hyp.get("eventCount")) for _d, hyp, _r in observations]
    max_amplitudes = [_float(hyp.get("maxAmplitude")) for _d, hyp, _r in observations]
    mean_amplitudes = [_float(hyp.get("meanAmplitude")) for _d, hyp, _r in observations]
    grid_errors = [_float(hyp.get("minGridError"), 0.10) for _d, hyp, _r in observations]
    durations = [_float(hyp.get("maxDuration")) for _d, hyp, _r in observations]

    target_measure, target_step = _location(target)
    recurrence_hits = 0
    recurrence_total = 0
    for measure_delta in (-2, -1, 1, 2):
        measure = target_measure + measure_delta
        if measure < 1 or measure > 16:
            continue
        recurrence_total += 1
        row = context["byLocation"].get((measure, target_step))
        if row is not None and midi in _midi_set(row):
            recurrence_hits += 1

    target_dominant = _int(target.get("dominantMidi"))
    dominant_distance = (
        min(1.0, abs(midi - target_dominant) / 12.0)
        if target_dominant is not None
        else 1.0
    )

    target_pitch_count = max(1, int(target.get("candidatePitchCount") or len(_hypotheses(target)) or 1))
    neighborhood_size = float(2 * radius + 1)

    return np.asarray(
        [
            exact_present,
            1.0 / (1.0 + nearest_delta),
            len(support_deltas) / neighborhood_size,
            weighted_support / max(normalizer, 1e-9),
            min(1.0, max(source_counts, default=0.0) / 2.0),
            min(1.0, (sum(source_counts) / max(len(source_counts), 1)) / 2.0),
            min(1.0, max(event_counts, default=0.0) / 4.0),
            float(np.clip(max(max_amplitudes, default=0.0), 0.0, 1.0)),
            float(np.clip(max(mean_amplitudes, default=0.0), 0.0, 1.0)),
            float(np.clip(1.0 - min(grid_errors, default=0.10) / 0.10, 0.0, 1.0)),
            float(np.clip(max(durations, default=0.0) / 1.0, 0.0, 1.0)),
            dominant_exact,
            dominant_support / neighborhood_size,
            _rank_percentile(target, int(context["totalRows"])),
            1.0 if target.get("v143Selected") is True else 0.0,
            float(np.clip(target_pitch_count / 8.0, 0.0, 1.0)),
            recurrence_hits / float(max(recurrence_total, 1)),
            dominant_distance,
        ],
        dtype=np.float64,
    )


def _dataset(
    rows: list[dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    radius: int,
) -> tuple[np.ndarray, np.ndarray, list[tuple[tuple[int, int], int]]]:
    context = _build_feature_context(rows)
    features: list[np.ndarray] = []
    labels: list[float] = []
    keys: list[tuple[tuple[int, int], int]] = []

    for target in rows:
        location = _location(target)
        if location[0] not in measures:
            continue
        positives = reference_by_loc.get(location, set())
        for midi in sorted(_candidate_midis_for_target(target, context, radius)):
            features.append(_features_for_candidate(target, midi, context, radius))
            labels.append(1.0 if midi in positives else 0.0)
            keys.append((location, midi))

    if not features:
        raise RuntimeError("No pitch-ranking examples were built")
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def _sigmoid(z: np.ndarray) -> np.ndarray:
    z = np.clip(z, -40.0, 40.0)
    return 1.0 / (1.0 + np.exp(-z))


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    positive_weight: float,
    l2: float,
    epochs: int = 800,
    learning_rate: float = 0.08,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    xn = (x - mean) / scale

    weights = np.zeros(xn.shape[1], dtype=np.float64)
    bias = 0.0
    sample_weight = np.where(y > 0.5, float(positive_weight), 1.0)
    denom = float(np.sum(sample_weight))

    for epoch in range(epochs):
        probabilities = _sigmoid(xn @ weights + bias)
        error = (probabilities - y) * sample_weight
        gradient = (xn.T @ error) / denom + float(l2) * weights
        bias_gradient = float(np.sum(error) / denom)
        step = learning_rate / math.sqrt(1.0 + epoch / 200.0)
        weights -= step * gradient
        bias -= step * bias_gradient

    return {
        "mean": mean,
        "scale": scale,
        "weights": weights,
        "bias": float(bias),
    }


def _predict(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xn = (x - model["mean"]) / model["scale"]
    return _sigmoid(xn @ model["weights"] + float(model["bias"]))


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _percent(value: float) -> float:
    return round(100.0 * value, 3)


def _evaluate(
    probabilities: np.ndarray,
    keys: list[tuple[tuple[int, int], int]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    *,
    threshold: float,
    top_k: int,
) -> dict[str, Any]:
    grouped: dict[tuple[int, int], list[tuple[int, float]]] = {}
    for probability, (location, midi) in zip(probabilities, keys):
        grouped.setdefault(location, []).append((midi, float(probability)))

    predicted: dict[tuple[int, int], set[int]] = {}
    for location, candidates in grouped.items():
        selected = [item for item in sorted(candidates, key=lambda item: (-item[1], item[0])) if item[1] >= threshold]
        if selected:
            predicted[location] = {int(midi) for midi, _score in selected[:top_k]}

    reference = {
        location: set(midis)
        for location, midis in reference_by_loc.items()
        if location[0] in measures
    }
    reference_locations = set(reference)
    predicted_locations = set(predicted)
    location_hits = len(reference_locations & predicted_locations)
    location_precision = location_hits / max(len(predicted_locations), 1)
    location_recall = location_hits / max(len(reference_locations), 1)

    reference_event_count = sum(len(values) for values in reference.values())
    predicted_event_count = sum(len(values) for values in predicted.values())
    pitch_hits = sum(len(predicted.get(location, set()) & expected) for location, expected in reference.items())
    pitch_precision = pitch_hits / max(predicted_event_count, 1)
    pitch_recall = pitch_hits / max(reference_event_count, 1)

    exact_sets = sum(1 for location, expected in reference.items() if predicted.get(location, set()) == expected)
    exact_set_rate = exact_sets / max(len(reference), 1)

    return {
        "referenceLocationCount": len(reference_locations),
        "predictedLocationCount": len(predicted_locations),
        "locationPrecisionPercent": _percent(location_precision),
        "locationRecallPercent": _percent(location_recall),
        "locationF1Percent": _percent(_f1(location_precision, location_recall)),
        "referencePitchEventCount": reference_event_count,
        "predictedPitchEventCount": predicted_event_count,
        "pitchPrecisionPercent": _percent(pitch_precision),
        "pitchRecallPercent": _percent(pitch_recall),
        "pitchF1Percent": _percent(_f1(pitch_precision, pitch_recall)),
        "exactPitchSetPercent": _percent(exact_set_rate),
    }


def _oracle_recall(
    rows: list[dict[str, Any]],
    reference_by_loc: dict[tuple[int, int], set[int]],
    measures: set[int],
    radius: int,
) -> float:
    context = _build_feature_context(rows)
    hits = 0
    total = 0
    rows_by_loc = {_location(row): row for row in rows}
    for location, expected in reference_by_loc.items():
        if location[0] not in measures:
            continue
        target = rows_by_loc.get(location)
        for midi in expected:
            total += 1
            if target is not None and midi in _candidate_midis_for_target(target, context, radius):
                hits += 1
    return _percent(hits / max(total, 1))


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference_payload = json.loads(REFERENCE_PATH.read_text())
    rows = [dict(row) for row in cache.get("analysis", {}).get("introRows", []) or []]
    if not rows:
        raise RuntimeError("Analysis cache contains no intro rows")

    reference_by_loc = _reference_by_location(reference_payload)
    best: dict[str, Any] | None = None
    trials: list[dict[str, Any]] = []

    for radius in RADII:
        x_dev, y_dev, keys_dev = _dataset(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius)
        x_hold, _y_hold, keys_hold = _dataset(rows, reference_by_loc, HOLDOUT_MEASURES, radius)

        for positive_weight in POSITIVE_CLASS_WEIGHTS:
            for l2 in L2_VALUES:
                model = _fit_logistic(
                    x_dev,
                    y_dev,
                    positive_weight=positive_weight,
                    l2=l2,
                )
                p_dev = _predict(model, x_dev)
                p_hold = _predict(model, x_hold)

                for threshold in THRESHOLDS:
                    for top_k in TOP_K_VALUES:
                        development = _evaluate(
                            p_dev,
                            keys_dev,
                            reference_by_loc,
                            DEVELOPMENT_MEASURES,
                            threshold=threshold,
                            top_k=top_k,
                        )
                        objective = (
                            0.75 * development["pitchF1Percent"]
                            + 0.15 * development["locationF1Percent"]
                            + 0.10 * development["exactPitchSetPercent"]
                        )
                        trial = {
                            "radius": radius,
                            "positiveClassWeight": positive_weight,
                            "l2": l2,
                            "threshold": threshold,
                            "topK": top_k,
                            "developmentObjectivePercent": round(objective, 3),
                            "development": development,
                        }
                        trials.append(trial)
                        if best is None or (
                            trial["developmentObjectivePercent"],
                            development["pitchF1Percent"],
                            development["pitchRecallPercent"],
                            -development["predictedPitchEventCount"],
                        ) > (
                            best["trial"]["developmentObjectivePercent"],
                            best["trial"]["development"]["pitchF1Percent"],
                            best["trial"]["development"]["pitchRecallPercent"],
                            -best["trial"]["development"]["predictedPitchEventCount"],
                        ):
                            best = {
                                "trial": trial,
                                "model": model,
                                "holdout": _evaluate(
                                    p_hold,
                                    keys_hold,
                                    reference_by_loc,
                                    HOLDOUT_MEASURES,
                                    threshold=threshold,
                                    top_k=top_k,
                                ),
                            }

    if best is None:
        raise RuntimeError("No supervised pitch-ranker configuration was evaluated")

    trial = best["trial"]
    model = best["model"]
    holdout = best["holdout"]
    radius = int(trial["radius"])

    model_payload = {
        "schemaVersion": 1,
        "status": "development-only-not-promoted",
        "featureNames": list(FEATURE_NAMES),
        "radiusSteps": radius,
        "threshold": float(trial["threshold"]),
        "topK": int(trial["topK"]),
        "mean": [float(value) for value in model["mean"]],
        "scale": [float(value) for value in model["scale"]],
        "weights": [float(value) for value in model["weights"]],
        "bias": float(model["bias"]),
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "professionalReferenceUsedForTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionPromotionAllowed": False,
    }
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(json.dumps(model_payload, indent=2) + "\n")

    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    report = {
        "reportVersion": 1,
        "scope": "professional-intro-pitch-ranking",
        "oraclePitchRecallPercent": {
            "development": _oracle_recall(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius),
            "holdout": _oracle_recall(rows, reference_by_loc, HOLDOUT_MEASURES, radius),
        },
        "bestConfiguration": {
            key: value
            for key, value in trial.items()
            if key not in {"development"}
        },
        "development": trial["development"],
        "holdout": holdout,
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:10]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "modelPath": str(MODEL_PATH.relative_to(REPO_ROOT)),
    }
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("=== V143 SUPERVISED PITCH EVIDENCE RANKER ===")
    print("rows:", len(rows))
    print("developmentPositiveExamples:", int(sum(_dataset(rows, reference_by_loc, DEVELOPMENT_MEASURES, radius)[1])))
    print("oraclePitchRecallPercent:", report["oraclePitchRecallPercent"])
    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print()
    print("DEVELOPMENT:")
    print(json.dumps(report["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(report["holdout"], indent=2))
    print()
    print("TOP MODEL COEFFICIENTS:")
    print(json.dumps(report["topCoefficients"], indent=2))
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()

```


## analyzer/v143_intro_supervised_temporal_assignment.py

```python
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-analysis-cache.json"
)
REFERENCE_PATH = REPO_ROOT / "public" / "gomyway-professional-rhythm-reference-v2.json"
OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-temporal-assignment-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-supervised-temporal-assignment-model.json"
)

DEVELOPMENT_MEASURES = set(range(1, 13))
HOLDOUT_MEASURES = set(range(13, 17))
STEPS_PER_MEASURE = 16
RADIUS = 2
POSITIVE_WEIGHTS = (4.0, 8.0, 12.0, 16.0)
L2_VALUES = (0.001, 0.01, 0.05)
THRESHOLDS = tuple(round(0.10 + 0.05 * i, 2) for i in range(15))
MAX_POLYPHONY_VALUES = (1, 2, 3)
NEGATIVE_MULTIPLIER = 40

FEATURE_NAMES = (
    "source_count",
    "event_count",
    "max_amplitude",
    "mean_amplitude",
    "grid_accuracy",
    "duration",
    "v143_rank_percentile",
    "v143_selected",
    "row_candidate_count",
    "atom_relative_quality",
    "delta_minus2",
    "delta_minus1",
    "delta_zero",
    "delta_plus1",
    "delta_plus2",
    "abs_delta",
    "source_step_sin",
    "source_step_cos",
    "target_step_sin",
    "target_step_cos",
    "midi_norm",
    "pitch_class_sin",
    "pitch_class_cos",
    "recurrence_exact",
    "recurrence_tol1",
    "recurrence_tol2",
    "source_recurrence_exact",
    "target_competition",
    "source_competition",
)


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        out = float(value)
        return out if math.isfinite(out) else default
    except (TypeError, ValueError):
        return default


def _pct(value: float) -> float:
    return round(100.0 * value, 3)


def _f1(precision: float, recall: float) -> float:
    return 0.0 if precision + recall <= 0.0 else 2.0 * precision * recall / (precision + recall)


def _reference_events(payload: dict[str, Any], measures: set[int]) -> list[dict[str, int]]:
    events: list[dict[str, int]] = []
    for measure in payload.get("measures", []) or []:
        if not isinstance(measure, dict):
            continue
        number = int(measure.get("measureNumber") or 0)
        if number not in measures:
            continue
        for raw in measure.get("events", []) or []:
            if not isinstance(raw, dict):
                continue
            midi = _safe_int(raw.get("midiPitch"))
            if midi is None:
                midi = _safe_int(raw.get("soundingMidiPitch"))
            if midi is None:
                continue
            step = int(raw.get("step") or 0)
            if 0 <= step < STEPS_PER_MEASURE:
                events.append({"measure": number, "step": step, "midi": midi})
    return events


def _reference_sets(payload: dict[str, Any], measures: set[int]) -> dict[tuple[int, int], set[int]]:
    out: dict[tuple[int, int], set[int]] = {}
    for event in _reference_events(payload, measures):
        out.setdefault((event["measure"], event["step"]), set()).add(event["midi"])
    return out


def _rank_percentile(row: dict[str, Any], total_rows: int) -> float:
    rank = _safe_int(row.get("v143Rank"))
    if rank is None or total_rows <= 1:
        return 0.5
    return float(np.clip(1.0 - (rank - 1) / float(total_rows - 1), 0.0, 1.0))


def _candidate_atoms(cache: dict[str, Any]) -> list[dict[str, Any]]:
    analysis = cache.get("analysis", {}) or {}
    rows = analysis.get("introCandidates", []) or analysis.get("introRows", []) or []
    total_rows = len(rows)
    atoms: list[dict[str, Any]] = []
    atom_id = 0
    for row_index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        measure = int(row.get("measure") or 0)
        step = int(row.get("step") or 0)
        if not 1 <= measure <= 16 or not 0 <= step < STEPS_PER_MEASURE:
            continue
        hypotheses = [h for h in (row.get("pitchHypotheses", []) or []) if isinstance(h, dict)]
        dominant = _safe_int(row.get("dominantMidi"))
        if dominant is not None and all(_safe_int(h.get("midi")) != dominant for h in hypotheses):
            hypotheses.append({"midi": dominant})

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for hypothesis in hypotheses:
            midi = _safe_int(hypothesis.get("midi"))
            if midi is not None:
                grouped[midi].append(hypothesis)

        row_qualities: list[float] = []
        temporary: list[dict[str, Any]] = []
        for midi, values in grouped.items():
            source_count = max((_safe_float(v.get("sourceCount")) for v in values), default=0.0)
            event_count = max((_safe_float(v.get("eventCount")) for v in values), default=0.0)
            max_amplitude = max((_safe_float(v.get("maxAmplitude")) for v in values), default=0.0)
            mean_amplitude = max((_safe_float(v.get("meanAmplitude")) for v in values), default=0.0)
            min_grid_error = min((_safe_float(v.get("minGridError"), 0.10) for v in values), default=0.10)
            max_duration = max((_safe_float(v.get("maxDuration")) for v in values), default=0.0)
            quality = (
                min(source_count / 2.0, 1.0)
                + min(event_count / 4.0, 1.0)
                + float(np.clip(max_amplitude, 0.0, 1.0))
                + float(np.clip(1.0 - min_grid_error / 0.10, 0.0, 1.0))
                + float(np.clip(max_duration / 0.75, 0.0, 1.0))
            ) / 5.0
            row_qualities.append(quality)
            temporary.append(
                {
                    "midi": int(midi),
                    "sourceCount": source_count,
                    "eventCount": event_count,
                    "maxAmplitude": max_amplitude,
                    "meanAmplitude": mean_amplitude,
                    "minGridError": min_grid_error,
                    "maxDuration": max_duration,
                    "quality": quality,
                }
            )

        best_quality = max(row_qualities, default=1.0)
        for item in temporary:
            atom_id += 1
            atoms.append(
                {
                    "atomId": atom_id,
                    "rowIndex": row_index,
                    "measure": measure,
                    "sourceStep": step,
                    "midi": item["midi"],
                    "sourceCount": item["sourceCount"],
                    "eventCount": item["eventCount"],
                    "maxAmplitude": item["maxAmplitude"],
                    "meanAmplitude": item["meanAmplitude"],
                    "minGridError": item["minGridError"],
                    "maxDuration": item["maxDuration"],
                    "quality": item["quality"],
                    "relativeQuality": item["quality"] / max(best_quality, 1e-9),
                    "rowCandidateCount": len(temporary),
                    "v143RankPercentile": _rank_percentile(row, total_rows),
                    "v143Selected": 1.0 if row.get("v143Selected") is True else 0.0,
                }
            )
    return atoms


def _atoms_by_measure_step(atoms: list[dict[str, Any]]) -> dict[int, dict[int, list[dict[str, Any]]]]:
    out: dict[int, dict[int, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for atom in atoms:
        out[int(atom["measure"])][int(atom["sourceStep"])].append(atom)
    return out


def _teacher_matching(
    refs: list[dict[str, int]], atoms: list[dict[str, Any]], radius: int
) -> tuple[dict[int, int], int]:
    atom_indices_by_measure_midi: dict[tuple[int, int], list[int]] = defaultdict(list)
    for index, atom in enumerate(atoms):
        atom_indices_by_measure_midi[(int(atom["measure"]), int(atom["midi"]))].append(index)

    adjacency: list[list[int]] = []
    for ref in refs:
        options = [
            index
            for index in atom_indices_by_measure_midi.get((ref["measure"], ref["midi"]), [])
            if abs(int(atoms[index]["sourceStep"]) - ref["step"]) <= radius
        ]
        options.sort(
            key=lambda index: (
                abs(int(atoms[index]["sourceStep"]) - ref["step"]),
                -float(atoms[index]["quality"]),
                index,
            )
        )
        adjacency.append(options)

    atom_to_ref: dict[int, int] = {}

    def augment(ref_index: int, visited: set[int]) -> bool:
        for atom_index in adjacency[ref_index]:
            if atom_index in visited:
                continue
            visited.add(atom_index)
            previous = atom_to_ref.get(atom_index)
            if previous is None or augment(previous, visited):
                atom_to_ref[atom_index] = ref_index
                return True
        return False

    order = sorted(range(len(refs)), key=lambda idx: (len(adjacency[idx]), refs[idx]["measure"], refs[idx]["step"], refs[idx]["midi"]))
    matches = 0
    for ref_index in order:
        if augment(ref_index, set()):
            matches += 1

    labels: dict[int, int] = {}
    for atom_index, ref_index in atom_to_ref.items():
        atom = atoms[atom_index]
        ref = refs[ref_index]
        labels[int(atom["atomId"])] = int(ref["step"])
    return labels, matches


def _has_midi_near(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measure: int,
    target_step: int,
    midi: int,
    tolerance: int,
) -> bool:
    for delta in range(-tolerance, tolerance + 1):
        step = target_step + delta
        if 0 <= step < STEPS_PER_MEASURE and any(
            int(atom["midi"]) == midi for atom in indexed.get(measure, {}).get(step, [])
        ):
            return True
    return False


def _recurrence(
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    target_measure: int,
    target_step: int,
    midi: int,
    tolerance: int,
) -> float:
    comparison_measures = [m for m in range(1, 17) if m != target_measure]
    hits = sum(
        1
        for measure in comparison_measures
        if _has_midi_near(indexed, measure, target_step, midi, tolerance)
    )
    return hits / max(len(comparison_measures), 1)


def _competition(
    indexed: dict[int, dict[int, list[dict[str, Any]]]], measure: int, step: int
) -> float:
    midis = {int(atom["midi"]) for atom in indexed.get(measure, {}).get(step, [])}
    return float(np.clip(len(midis) / 24.0, 0.0, 1.0))


def _pair_features(
    atom: dict[str, Any], target_step: int, indexed: dict[int, dict[int, list[dict[str, Any]]]]
) -> np.ndarray:
    source_step = int(atom["sourceStep"])
    delta = target_step - source_step
    if abs(delta) > RADIUS:
        raise ValueError("pair outside temporal radius")
    phase = 2.0 * math.pi / STEPS_PER_MEASURE
    pitch_phase = 2.0 * math.pi * (int(atom["midi"]) % 12) / 12.0
    one_hot = [1.0 if delta == d else 0.0 for d in (-2, -1, 0, 1, 2)]
    measure = int(atom["measure"])
    midi = int(atom["midi"])
    return np.asarray(
        [
            min(float(atom["sourceCount"]) / 2.0, 1.0),
            min(float(atom["eventCount"]) / 4.0, 1.0),
            float(np.clip(atom["maxAmplitude"], 0.0, 1.0)),
            float(np.clip(atom["meanAmplitude"], 0.0, 1.0)),
            float(np.clip(1.0 - float(atom["minGridError"]) / 0.10, 0.0, 1.0)),
            float(np.clip(float(atom["maxDuration"]) / 0.75, 0.0, 1.0)),
            float(atom["v143RankPercentile"]),
            float(atom["v143Selected"]),
            float(np.clip(float(atom["rowCandidateCount"]) / 24.0, 0.0, 1.0)),
            float(atom["relativeQuality"]),
            *one_hot,
            abs(delta) / float(RADIUS),
            math.sin(phase * source_step),
            math.cos(phase * source_step),
            math.sin(phase * target_step),
            math.cos(phase * target_step),
            float(np.clip((midi - 40) / 48.0, 0.0, 1.0)),
            math.sin(pitch_phase),
            math.cos(pitch_phase),
            _recurrence(indexed, measure, target_step, midi, 0),
            _recurrence(indexed, measure, target_step, midi, 1),
            _recurrence(indexed, measure, target_step, midi, 2),
            _recurrence(indexed, measure, source_step, midi, 0),
            _competition(indexed, measure, target_step),
            _competition(indexed, measure, source_step),
        ],
        dtype=np.float64,
    )


def _build_pairs(
    atoms: list[dict[str, Any]],
    indexed: dict[int, dict[int, list[dict[str, Any]]]],
    measures: set[int],
    teacher_labels: dict[int, int] | None,
) -> tuple[np.ndarray, np.ndarray, list[tuple[int, int, int, int]]]:
    features: list[np.ndarray] = []
    labels: list[float] = []
    keys: list[tuple[int, int, int, int]] = []
    for atom in atoms:
        measure = int(atom["measure"])
        if measure not in measures:
            continue
        source_step = int(atom["sourceStep"])
        midi = int(atom["midi"])
        for delta in range(-RADIUS, RADIUS + 1):
            target_step = source_step + delta
            if not 0 <= target_step < STEPS_PER_MEASURE:
                continue
            features.append(_pair_features(atom, target_step, indexed))
            positive = teacher_labels is not None and teacher_labels.get(int(atom["atomId"])) == target_step
            labels.append(1.0 if positive else 0.0)
            keys.append((int(atom["atomId"]), measure, target_step, midi))
    return np.vstack(features), np.asarray(labels, dtype=np.float64), keys


def _downsample_training(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    positive_indices = np.flatnonzero(y > 0.5)
    negative_indices = np.flatnonzero(y <= 0.5)
    if len(positive_indices) == 0:
        raise RuntimeError("No positive temporal-assignment examples")
    limit = min(len(negative_indices), len(positive_indices) * NEGATIVE_MULTIPLIER)
    # Deterministic hard-negative preference: retain negatives with the largest
    # source/evidence mass before falling back to their original order.
    hardness = (
        x[negative_indices, 0]
        + x[negative_indices, 1]
        + x[negative_indices, 2]
        + x[negative_indices, 9]
        + x[negative_indices, 24]
        + x[negative_indices, 25]
    )
    order = np.argsort(-hardness, kind="stable")[:limit]
    selected = np.concatenate([positive_indices, negative_indices[order]])
    return x[selected], y[selected]


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40.0, 40.0)))


def _fit_logistic(
    x: np.ndarray,
    y: np.ndarray,
    *,
    positive_weight: float,
    l2: float,
    epochs: int = 240,
    learning_rate: float = 0.08,
) -> dict[str, Any]:
    mean = np.mean(x, axis=0)
    scale = np.std(x, axis=0)
    scale = np.where(scale < 1e-8, 1.0, scale)
    xn = (x - mean) / scale
    weights = np.zeros(x.shape[1], dtype=np.float64)
    bias = 0.0
    sample_weight = np.where(y > 0.5, positive_weight, 1.0)
    denom = float(np.sum(sample_weight))
    for epoch in range(epochs):
        probability = _sigmoid(xn @ weights + bias)
        error = (probability - y) * sample_weight
        grad = (xn.T @ error) / denom + l2 * weights
        bias_grad = float(np.sum(error) / denom)
        step = learning_rate / math.sqrt(1.0 + epoch / 80.0)
        weights -= step * grad
        bias -= step * bias_grad
    return {"mean": mean, "scale": scale, "weights": weights, "bias": bias}


def _predict(model: dict[str, Any], x: np.ndarray) -> np.ndarray:
    xn = (x - model["mean"]) / model["scale"]
    return _sigmoid(xn @ model["weights"] + float(model["bias"]))


def _decode(
    probabilities: np.ndarray,
    keys: list[tuple[int, int, int, int]],
    *,
    threshold: float,
    max_polyphony: int,
) -> dict[tuple[int, int], set[int]]:
    candidates = sorted(
        [
            (float(probability), atom_id, measure, target_step, midi)
            for probability, (atom_id, measure, target_step, midi) in zip(probabilities, keys)
            if probability >= threshold
        ],
        key=lambda item: (-item[0], item[2], item[3], item[4], item[1]),
    )
    used_atoms: set[int] = set()
    predicted: dict[tuple[int, int], set[int]] = defaultdict(set)
    for _probability, atom_id, measure, target_step, midi in candidates:
        if atom_id in used_atoms:
            continue
        location = (measure, target_step)
        if midi in predicted[location]:
            continue
        if len(predicted[location]) >= max_polyphony:
            continue
        predicted[location].add(midi)
        used_atoms.add(atom_id)
    return dict(predicted)


def _grade(
    reference: dict[tuple[int, int], set[int]], predicted: dict[tuple[int, int], set[int]]
) -> dict[str, Any]:
    ref_locations = set(reference)
    pred_locations = set(predicted)
    location_hits = len(ref_locations & pred_locations)
    lp = location_hits / max(len(pred_locations), 1)
    lr = location_hits / max(len(ref_locations), 1)
    ref_events = sum(len(v) for v in reference.values())
    pred_events = sum(len(v) for v in predicted.values())
    pitch_hits = sum(len(expected & predicted.get(location, set())) for location, expected in reference.items())
    pp = pitch_hits / max(pred_events, 1)
    pr = pitch_hits / max(ref_events, 1)
    exact = sum(1 for location, expected in reference.items() if predicted.get(location, set()) == expected)
    return {
        "referenceLocationCount": len(ref_locations),
        "predictedLocationCount": len(pred_locations),
        "locationPrecisionPercent": _pct(lp),
        "locationRecallPercent": _pct(lr),
        "locationF1Percent": _pct(_f1(lp, lr)),
        "referencePitchEventCount": ref_events,
        "predictedPitchEventCount": pred_events,
        "pitchPrecisionPercent": _pct(pp),
        "pitchRecallPercent": _pct(pr),
        "pitchF1Percent": _pct(_f1(pp, pr)),
        "exactPitchSetPercent": _pct(exact / max(len(ref_locations), 1)),
    }


def main() -> None:
    if not CACHE_PATH.exists():
        raise RuntimeError(f"Missing analysis cache: {CACHE_PATH}")
    if not REFERENCE_PATH.exists():
        raise RuntimeError(f"Missing professional reference: {REFERENCE_PATH}")

    cache = json.loads(CACHE_PATH.read_text())
    reference = json.loads(REFERENCE_PATH.read_text())
    atoms = _candidate_atoms(cache)
    indexed = _atoms_by_measure_step(atoms)

    dev_refs = _reference_events(reference, DEVELOPMENT_MEASURES)
    hold_refs = _reference_events(reference, HOLDOUT_MEASURES)
    dev_teacher, dev_oracle_matches = _teacher_matching(dev_refs, atoms, RADIUS)
    _hold_teacher, hold_oracle_matches = _teacher_matching(hold_refs, atoms, RADIUS)

    x_dev_all, y_dev_all, keys_dev = _build_pairs(atoms, indexed, DEVELOPMENT_MEASURES, dev_teacher)
    x_hold, _y_hold, keys_hold = _build_pairs(atoms, indexed, HOLDOUT_MEASURES, None)
    x_dev, y_dev = _downsample_training(x_dev_all, y_dev_all)

    dev_reference = _reference_sets(reference, DEVELOPMENT_MEASURES)
    hold_reference = _reference_sets(reference, HOLDOUT_MEASURES)

    print("=== V143 SUPERVISED TEMPORAL ASSIGNMENT ===")
    print("candidatePitchAtomCount:", len(atoms))
    print("developmentTeacherMatches:", dev_oracle_matches, "/", len(dev_refs))
    print("holdoutOracleMatches:", hold_oracle_matches, "/", len(hold_refs))
    print("trainingPairs:", len(x_dev), "positives:", int(np.sum(y_dev)))
    print("holdoutPairs:", len(x_hold))

    best: dict[str, Any] | None = None
    fitted: dict[tuple[float, float], dict[str, Any]] = {}
    for positive_weight in POSITIVE_WEIGHTS:
        for l2 in L2_VALUES:
            model = _fit_logistic(x_dev, y_dev, positive_weight=positive_weight, l2=l2)
            fitted[(positive_weight, l2)] = model
            p_dev = _predict(model, x_dev_all)
            for threshold in THRESHOLDS:
                for max_polyphony in MAX_POLYPHONY_VALUES:
                    prediction = _decode(
                        p_dev,
                        keys_dev,
                        threshold=threshold,
                        max_polyphony=max_polyphony,
                    )
                    grade = _grade(dev_reference, prediction)
                    objective = (
                        0.80 * grade["pitchF1Percent"]
                        + 0.10 * grade["pitchRecallPercent"]
                        + 0.05 * grade["locationF1Percent"]
                        + 0.05 * grade["exactPitchSetPercent"]
                    )
                    trial = {
                        "positiveClassWeight": positive_weight,
                        "l2": l2,
                        "threshold": threshold,
                        "maxPolyphony": max_polyphony,
                        "developmentObjectivePercent": round(objective, 3),
                        "development": grade,
                    }
                    if best is None or (
                        trial["developmentObjectivePercent"],
                        grade["pitchF1Percent"],
                        grade["pitchRecallPercent"],
                        -grade["predictedPitchEventCount"],
                    ) > (
                        best["trial"]["developmentObjectivePercent"],
                        best["trial"]["development"]["pitchF1Percent"],
                        best["trial"]["development"]["pitchRecallPercent"],
                        -best["trial"]["development"]["predictedPitchEventCount"],
                    ):
                        best = {"trial": trial, "model": model}

    if best is None:
        raise RuntimeError("No supervised temporal assignment trial completed")

    trial = best["trial"]
    model = best["model"]
    p_hold = _predict(model, x_hold)
    hold_prediction = _decode(
        p_hold,
        keys_hold,
        threshold=float(trial["threshold"]),
        max_polyphony=int(trial["maxPolyphony"]),
    )
    hold_grade = _grade(hold_reference, hold_prediction)

    coefficients = sorted(
        zip(FEATURE_NAMES, model["weights"]),
        key=lambda item: abs(float(item[1])),
        reverse=True,
    )
    config = {k: v for k, v in trial.items() if k not in {"development"}}
    report = {
        "reportVersion": 1,
        "scope": "supervised-temporal-candidate-reassignment",
        "radiusSteps": RADIUS,
        "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
        "holdoutMeasures": sorted(HOLDOUT_MEASURES),
        "developmentOracleRecallPercent": _pct(dev_oracle_matches / max(len(dev_refs), 1)),
        "holdoutOracleRecallPercent": _pct(hold_oracle_matches / max(len(hold_refs), 1)),
        "bestConfiguration": config,
        "development": trial["development"],
        "holdout": hold_grade,
        "topCoefficients": [
            {"feature": name, "weight": round(float(weight), 6)}
            for name, weight in coefficients[:12]
        ],
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceUsedForOfflineTemporalTraining": True,
        "professionalReferenceRequiredAtRuntime": False,
        "runtimeLabelsRequired": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "schemaVersion": 1,
                "status": "development-only-not-promoted",
                "featureNames": list(FEATURE_NAMES),
                "radiusSteps": RADIUS,
                "threshold": float(trial["threshold"]),
                "maxPolyphony": int(trial["maxPolyphony"]),
                "mean": [float(v) for v in model["mean"]],
                "scale": [float(v) for v in model["scale"]],
                "weights": [float(v) for v in model["weights"]],
                "bias": float(model["bias"]),
                "developmentMeasures": sorted(DEVELOPMENT_MEASURES),
                "holdoutMeasures": sorted(HOLDOUT_MEASURES),
                "professionalReferenceUsedForTraining": True,
                "professionalReferenceRequiredAtRuntime": False,
                "productionPromotionAllowed": False,
            },
            indent=2,
        )
        + "\n"
    )

    print()
    print("BEST DEVELOPMENT CONFIGURATION:")
    print(json.dumps(config, indent=2))
    print()
    print("DEVELOPMENT (measures 1-12):")
    print(json.dumps(trial["development"], indent=2))
    print()
    print("HOLDOUT (measures 13-16, never used to fit or choose configuration):")
    print(json.dumps(hold_grade, indent=2))
    print()
    print("TOP MODEL COEFFICIENTS:")
    print(json.dumps(report["topCoefficients"], indent=2))
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()

```


## analyzer/v143_intro_sequence_event_model.py

```python
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import CACHE_PATH as RAW_CACHE_PATH, REFERENCE_PATH, _grid_lookup
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    MODEL_PATH as BASE_SELECTOR_MODEL_PATH,
    TRAIN_MEASURES,
    VALIDATION_MEASURES,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    _rows_by_measure,
    _grid_keys,
    _grid_feature,
    _assign_groups_reference_free,
    _predict_pitch_sets_for_assignments,
    _evaluate_end_to_end,
    _pct,
    _f1,
)
from v143_intro_repetition_recovery_event_selector import _load_json, _score_measures


OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-sequence-event-model-report.json"
)
MODEL_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-sequence-event-model.json"
)

WINDOWS_MS = (50, 75, 100, 125, 150, 200)
PCA_COMPONENTS = (8, 12, 16, 24, 32, 48, 64)
L2_VALUES = (0.001, 0.01, 0.1, 1.0, 10.0)
THRESHOLDS = tuple(round(0.10 + 0.05 * index, 2) for index in range(17))


def _location_metrics(
    reference: dict[tuple[int, int], set[int]],
    active: set[tuple[int, int]],
) -> dict[str, Any]:
    expected = set(reference)
    correct = len(expected & active)
    precision = correct / len(active) if active else 0.0
    recall = correct / len(expected) if expected else 0.0
    return {
        "referenceLocationCount": len(expected),
        "predictedLocationCount": len(active),
        "correctLocationCount": correct,
        "locationPrecisionPercent": _pct(correct, len(active)),
        "locationRecallPercent": _pct(correct, len(expected)),
        "locationF1Percent": round(100.0 * _f1(precision, recall), 3),
    }


def _safe_score(scores: dict[tuple[int, int], float], key: tuple[int, int]) -> float:
    value = scores.get(key, 0.0)
    try:
        value = float(value)
        return value if math.isfinite(value) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _sequence_context(
    key: tuple[int, int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    context_measures: set[int],
    base_threshold: float,
) -> list[float]:
    measure, step = key
    values: list[float] = []

    # Local rhythmic context in the same measure.
    local_scores: list[float] = []
    local_evidence: list[float] = []
    for delta in (-3, -2, -1, 0, 1, 2, 3):
        source_step = step + delta
        if 0 <= source_step < 16:
            score = _safe_score(scores, (measure, source_step))
            has_evidence = 1.0 if evidence.get((measure, source_step), False) else 0.0
        else:
            score = 0.0
            has_evidence = 0.0
        values.extend([score, has_evidence])
        local_scores.append(score)
        local_evidence.append(has_evidence)

    local = np.asarray(local_scores, dtype=np.float64)
    values.extend(
        [
            float(np.mean(local)),
            float(np.std(local)),
            float(np.max(local)),
            float(np.min(local)),
            sum(score >= base_threshold for score in local_scores) / 7.0,
            sum(local_evidence) / 7.0,
        ]
    )

    # Same rhythmic position across the analyzed context. These are entirely
    # label-free recurrence features and can use the full uploaded section at runtime.
    peers = [other for other in sorted(context_measures) if other != measure]
    peer_scores = [_safe_score(scores, (other, step)) for other in peers]
    if peer_scores:
        peer = np.asarray(peer_scores, dtype=np.float64)
        values.extend(
            [
                float(np.mean(peer)),
                float(np.std(peer)),
                float(np.max(peer)),
                float(np.median(peer)),
                sum(score >= base_threshold for score in peer_scores) / len(peer_scores),
            ]
        )
    else:
        values.extend([0.0] * 5)

    for modulus in (2, 4):
        phase = (measure - 1) % modulus
        phase_peers = [
            other
            for other in sorted(context_measures)
            if other != measure and (other - 1) % modulus == phase
        ]
        phase_scores = [_safe_score(scores, (other, step)) for other in phase_peers]
        if phase_scores:
            arr = np.asarray(phase_scores, dtype=np.float64)
            values.extend(
                [
                    float(np.mean(arr)),
                    float(np.max(arr)),
                    float(np.median(arr)),
                    sum(score >= base_threshold for score in phase_scores) / len(phase_scores),
                ]
            )
        else:
            values.extend([0.0] * 4)

    # Adjacent-measure continuity at the same rhythmic position.
    for delta_measure in (-2, -1, 1, 2):
        other = measure + delta_measure
        if other in context_measures:
            values.extend(
                [
                    _safe_score(scores, (other, step)),
                    1.0 if evidence.get((other, step), False) else 0.0,
                ]
            )
        else:
            values.extend([0.0, 0.0])

    return values


def _feature_for_key(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    key: tuple[int, int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    context_measures: set[int],
    base_threshold: float,
) -> tuple[np.ndarray, bool]:
    target_time = grid.get(key)
    if target_time is None:
        raise RuntimeError(f"Missing grid time for {key}")

    features: list[float] = []
    wide_evidence = False
    # Multi-scale current-position evidence prevents the original selector's
    # narrow chosen window from imposing a hard recall ceiling.
    for window_ms in WINDOWS_MS:
        vector, nearest = _grid_feature(
            rows_by_measure,
            int(key[0]),
            int(key[1]),
            float(target_time),
            int(window_ms),
        )
        features.extend(np.asarray(vector, dtype=np.float64).tolist())
        wide_evidence = wide_evidence or nearest is not None

    current_score = _safe_score(scores, key)
    features.extend(
        [
            current_score,
            current_score - float(base_threshold),
            1.0 if evidence.get(key, False) else 0.0,
        ]
    )
    features.extend(
        _sequence_context(
            key,
            scores,
            evidence,
            context_measures,
            float(base_threshold),
        )
    )
    return np.asarray(features, dtype=np.float64), bool(wide_evidence)


def _dataset(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    reference: dict[tuple[int, int], set[int]],
    measures: set[int],
    context_measures: set[int],
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    base_threshold: float,
) -> dict[str, Any]:
    active_reference = set(reference)
    xs: list[np.ndarray] = []
    ys: list[float] = []
    keys: list[tuple[int, int]] = []
    wide_evidence: list[bool] = []
    for key in _grid_keys(measures):
        if key not in grid:
            continue
        feature, has_wide_evidence = _feature_for_key(
            rows_by_measure,
            grid,
            key,
            scores,
            evidence,
            context_measures,
            base_threshold,
        )
        xs.append(feature)
        ys.append(1.0 if key in active_reference else 0.0)
        keys.append(key)
        wide_evidence.append(has_wide_evidence)
    if not xs:
        return {
            "X": np.zeros((0, 1), dtype=np.float64),
            "Y": np.zeros(0, dtype=np.float64),
            "keys": [],
            "wideEvidence": [],
        }
    return {
        "X": np.stack(xs, axis=0),
        "Y": np.asarray(ys, dtype=np.float64),
        "keys": keys,
        "wideEvidence": wide_evidence,
    }


def _fit_projection(
    X: np.ndarray,
    components: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X.mean(axis=0)
    std = X.std(axis=0)
    std = np.where(std < 1e-6, 1.0, std)
    standardized = (X - mean) / std
    _, _, vt = np.linalg.svd(standardized, full_matrices=False)
    k = max(1, min(int(components), vt.shape[0], vt.shape[1]))
    basis = vt[:k].T
    return mean, std, basis


def _project(
    X: np.ndarray,
    mean: np.ndarray,
    std: np.ndarray,
    basis: np.ndarray,
) -> np.ndarray:
    reduced = ((X - mean) / std) @ basis
    return np.concatenate([np.ones((reduced.shape[0], 1), dtype=np.float64), reduced], axis=1)


def _fit_ridge(Z: np.ndarray, y: np.ndarray, l2: float) -> np.ndarray:
    reg = np.eye(Z.shape[1], dtype=np.float64) * float(l2)
    reg[0, 0] = 0.0
    return np.linalg.pinv(Z.T @ Z + reg) @ Z.T @ y


def _active_from_scores(
    keys: list[tuple[int, int]],
    scores: np.ndarray,
    wide_evidence: list[bool],
    threshold: float,
) -> set[tuple[int, int]]:
    return {
        key
        for key, score, has_evidence in zip(keys, scores, wide_evidence)
        if has_evidence and float(score) >= float(threshold)
    }


def _evaluate_e2e(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    pitch_model: dict[str, Any],
) -> dict[str, Any]:
    # Use the pitch model's own learned temporal window for one-to-one onset
    # assignment. Event selection itself already uses evidence out to 200 ms.
    assignments = _assign_groups_reference_free(
        active,
        rows_by_measure,
        grid,
        int(pitch_model["windowMs"]),
    )
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)
    return _evaluate_end_to_end(reference, pitch_sets)


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    base_selector_model = _load_json(BASE_SELECTOR_MODEL_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)

    train_reference = _reference_sets(reference_payload, TRAIN_MEASURES)
    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    all_measures = set(range(1, 17))
    base_scores, base_evidence = _score_measures(
        rows_by_measure,
        grid,
        all_measures,
        base_selector_model,
    )
    base_threshold = float(base_selector_model["threshold"])

    print("=== V143 MULTISCALE SEQUENCE EVENT MODEL ===")
    print("Training measures: 1-8")
    print("Validation measures: 9-12")
    print("Measures 13-16: diagnostic only, not fresh untouched holdout")
    print("Windows:", WINDOWS_MS)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    train = _dataset(
        rows_by_measure,
        grid,
        train_reference,
        TRAIN_MEASURES,
        TRAIN_MEASURES,
        base_scores,
        base_evidence,
        base_threshold,
    )
    validation = _dataset(
        rows_by_measure,
        grid,
        validation_reference,
        VALIDATION_MEASURES,
        set(range(1, 13)),
        base_scores,
        base_evidence,
        base_threshold,
    )

    best: dict[str, Any] | None = None
    searched = 0
    total = len(PCA_COMPONENTS) * len(L2_VALUES) * len(THRESHOLDS)
    for components in PCA_COMPONENTS:
        mean, std, basis = _fit_projection(train["X"], components)
        z_train = _project(train["X"], mean, std, basis)
        z_validation = _project(validation["X"], mean, std, basis)
        for l2 in L2_VALUES:
            weights = _fit_ridge(z_train, train["Y"], l2)
            validation_scores = z_validation @ weights
            for threshold in THRESHOLDS:
                searched += 1
                active = _active_from_scores(
                    validation["keys"],
                    validation_scores,
                    validation["wideEvidence"],
                    threshold,
                )
                loc = _location_metrics(validation_reference, active)
                precision = float(loc["locationPrecisionPercent"])
                recall = float(loc["locationRecallPercent"])
                f1 = float(loc["locationF1Percent"])
                # Recall matters because the conditional pitch decoder is already
                # highly precise; keep enough precision that recovered events do not
                # overwhelm the tab with false attacks.
                objective = 0.55 * f1 + 0.30 * recall + 0.15 * precision
                if precision < 70.0:
                    objective -= (70.0 - precision) * 1.5
                candidate = {
                    "pcaComponents": int(components),
                    "l2": float(l2),
                    "threshold": float(threshold),
                    "validationObjectivePercent": round(objective, 3),
                    "validationLocation": loc,
                }
                if best is None or (
                    objective,
                    f1,
                    recall,
                    precision,
                ) > (
                    float(best["validationObjectivePercent"]),
                    float(best["validationLocation"]["locationF1Percent"]),
                    float(best["validationLocation"]["locationRecallPercent"]),
                    float(best["validationLocation"]["locationPrecisionPercent"]),
                ):
                    best = candidate
                if searched % 100 == 0 or searched == total:
                    print(f"searched {searched}/{total} sequence configurations")

    if best is None:
        raise RuntimeError("No sequence-event configuration evaluated")

    development = _dataset(
        rows_by_measure,
        grid,
        development_reference,
        DEVELOPMENT_MEASURES,
        DEVELOPMENT_MEASURES,
        base_scores,
        base_evidence,
        base_threshold,
    )
    holdout = _dataset(
        rows_by_measure,
        grid,
        holdout_reference,
        HOLDOUT_MEASURES,
        all_measures,
        base_scores,
        base_evidence,
        base_threshold,
    )

    mean, std, basis = _fit_projection(development["X"], int(best["pcaComponents"]))
    z_development = _project(development["X"], mean, std, basis)
    z_holdout = _project(holdout["X"], mean, std, basis)
    weights = _fit_ridge(z_development, development["Y"], float(best["l2"]))
    development_scores = z_development @ weights
    holdout_scores = z_holdout @ weights

    development_active = _active_from_scores(
        development["keys"],
        development_scores,
        development["wideEvidence"],
        float(best["threshold"]),
    )
    holdout_active = _active_from_scores(
        holdout["keys"],
        holdout_scores,
        holdout["wideEvidence"],
        float(best["threshold"]),
    )

    development_location = _location_metrics(development_reference, development_active)
    holdout_location = _location_metrics(holdout_reference, holdout_active)
    development_e2e = _evaluate_e2e(
        development_active,
        development_reference,
        rows_by_measure,
        grid,
        pitch_model,
    )
    holdout_e2e = _evaluate_e2e(
        holdout_active,
        holdout_reference,
        rows_by_measure,
        grid,
        pitch_model,
    )

    report = {
        "model": "v143-multiscale-sequence-event-model",
        "bestConfiguration": {
            "pcaComponents": best["pcaComponents"],
            "l2": best["l2"],
            "threshold": best["threshold"],
            "validationObjectivePercent": best["validationObjectivePercent"],
        },
        "validationLocation": best["validationLocation"],
        "developmentLocation": development_location,
        "developmentEndToEnd": development_e2e,
        "diagnosticHoldoutLocation": holdout_location,
        "diagnosticHoldoutEndToEnd": holdout_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are diagnostic only because prior architecture iterations inspected them. Use a fresh song/section before production promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")
    MODEL_PATH.write_text(
        json.dumps(
            {
                "model": report["model"],
                "windowsMs": list(WINDOWS_MS),
                "baseSelectorThreshold": base_threshold,
                "pcaComponents": int(best["pcaComponents"]),
                "l2": float(best["l2"]),
                "threshold": float(best["threshold"]),
                "featureMean": [round(float(value), 8) for value in mean],
                "featureStd": [round(float(value), 8) for value in std],
                "pcaBasis": [[round(float(value), 8) for value in row] for row in basis.tolist()],
                "ridgeWeights": [round(float(value), 8) for value in weights],
                "professionalReferenceRequiredAtRuntime": False,
            },
            separators=(",", ":"),
        )
        + "\n"
    )

    print("\n=== BEST VALIDATION SEQUENCE CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["diagnosticHoldoutEndToEnd"], indent=2))

    loc_recall = float(holdout_location["locationRecallPercent"])
    loc_precision = float(holdout_location["locationPrecisionPercent"])
    pitch_f1 = float(holdout_e2e["pitchF1Percent"])
    if loc_recall >= 80.0 and loc_precision >= 75.0 and pitch_f1 >= 78.0:
        diagnosis = "multiscale-sequence-event-model-closes-core-selection-gap"
    elif loc_recall >= 70.0 and pitch_f1 >= 72.0:
        diagnosis = "sequence-model-promising-refine-before-fresh-song-gate"
    else:
        diagnosis = "event-selection-still-bottleneck-next-test-onset-group-sequence-model"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("NOTE: measures 13-16 are diagnostic, not a fresh untouched holdout anymore.")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))
    print("Model:", MODEL_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()

```


## analyzer/v143_intro_repetition_recovery_event_selector.py

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from v143_intro_raw_attack_temporal_diagnostic import CACHE_PATH as RAW_CACHE_PATH, REFERENCE_PATH, _grid_lookup
from v143_intro_supervised_temporal_assignment import REPO_ROOT, _reference_sets
from v143_intro_learned_grid_event_selector import (
    SPECTRUM_CACHE_PATH,
    PITCH_MODEL_PATH,
    MODEL_PATH as SELECTOR_MODEL_PATH,
    TRAIN_MEASURES,
    VALIDATION_MEASURES,
    DEVELOPMENT_MEASURES,
    HOLDOUT_MEASURES,
    _rows_by_measure,
    _grid_keys,
    _grid_feature,
    _assign_groups_reference_free,
    _predict_pitch_sets_for_assignments,
    _evaluate_end_to_end,
    _pct,
    _f1,
)

OUTPUT_PATH = (
    REPO_ROOT
    / "public"
    / "training"
    / "v143-musical-reconstruction-calibration"
    / "intro-repetition-recovery-event-selector-report.json"
)

MARGINS = (0.05, 0.10, 0.15, 0.20, 0.30, 0.40)
MIN_SUPPORTS = (0.25, 0.40, 0.50, 0.60, 0.75)
PHASE_MODULI = (1, 2, 4)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise RuntimeError(f"Missing required file: {path}")
    return json.loads(path.read_text())


def _score_measures(
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    measures: set[int],
    selector_model: dict[str, Any],
) -> tuple[dict[tuple[int, int], float], dict[tuple[int, int], bool]]:
    window_ms = int(selector_model["windowMs"])
    mean = np.asarray(selector_model["featureMean"], dtype=np.float64)
    std = np.asarray(selector_model["featureStd"], dtype=np.float64)
    weights = np.asarray(selector_model["weights"], dtype=np.float64)

    score_by_key: dict[tuple[int, int], float] = {}
    evidence_by_key: dict[tuple[int, int], bool] = {}
    for key in _grid_keys(measures):
        target_time = grid.get(key)
        if target_time is None:
            continue
        feature, nearest = _grid_feature(
            rows_by_measure,
            int(key[0]),
            int(key[1]),
            float(target_time),
            window_ms,
        )
        z = (feature - mean) / std
        design = np.concatenate([np.ones(1, dtype=np.float64), z])
        score_by_key[key] = float(design @ weights)
        evidence_by_key[key] = nearest is not None
    return score_by_key, evidence_by_key


def _recurrence_support(
    key: tuple[int, int],
    seeds: set[tuple[int, int]],
    measures: set[int],
    phase_modulus: int,
) -> float:
    measure, step = key
    phase = (measure - 1) % max(int(phase_modulus), 1)
    peers = [
        other
        for other in sorted(measures)
        if other != measure and (other - 1) % max(int(phase_modulus), 1) == phase
    ]
    if not peers:
        return 0.0
    return sum((other, step) in seeds for other in peers) / float(len(peers))


def _recover(
    scores: dict[tuple[int, int], float],
    evidence: dict[tuple[int, int], bool],
    measures: set[int],
    base_threshold: float,
    margin: float,
    min_support: float,
    phase_modulus: int,
) -> set[tuple[int, int]]:
    seeds = {
        key
        for key, score in scores.items()
        if key[0] in measures and evidence.get(key, False) and float(score) >= float(base_threshold)
    }
    active = set(seeds)
    low_threshold = float(base_threshold) - float(margin)

    # Two passes allow strong repeated locations recovered in the first pass to
    # reinforce the same rhythmic phase elsewhere, while every decision remains
    # based only on analyzer scores and repetition structure.
    for _ in range(2):
        additions: set[tuple[int, int]] = set()
        for key, score in scores.items():
            if key[0] not in measures or key in active or not evidence.get(key, False):
                continue
            if float(score) < low_threshold:
                continue
            support = _recurrence_support(key, active, measures, phase_modulus)
            if support >= float(min_support):
                additions.add(key)
        if not additions:
            break
        active |= additions
    return active


def _location_metrics(reference: dict[tuple[int, int], set[int]], active: set[tuple[int, int]]) -> dict[str, Any]:
    expected = set(reference)
    correct = len(expected & active)
    precision = correct / len(active) if active else 0.0
    recall = correct / len(expected) if expected else 0.0
    return {
        "referenceLocationCount": len(expected),
        "predictedLocationCount": len(active),
        "correctLocationCount": correct,
        "locationPrecisionPercent": _pct(correct, len(active)),
        "locationRecallPercent": _pct(correct, len(expected)),
        "locationF1Percent": round(100.0 * _f1(precision, recall), 3),
    }


def _evaluate_candidate(
    active: set[tuple[int, int]],
    reference: dict[tuple[int, int], set[int]],
    rows_by_measure: dict[int, list[dict[str, Any]]],
    grid: dict[tuple[int, int], float],
    selector_model: dict[str, Any],
    pitch_model: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    loc = _location_metrics(reference, active)
    assignments = _assign_groups_reference_free(
        active,
        rows_by_measure,
        grid,
        int(selector_model["windowMs"]),
    )
    pitch_sets = _predict_pitch_sets_for_assignments(assignments, grid, pitch_model)
    e2e = _evaluate_end_to_end(reference, pitch_sets)
    return loc, e2e


def main() -> None:
    spectrum_cache = _load_json(SPECTRUM_CACHE_PATH)
    raw_cache = _load_json(RAW_CACHE_PATH)
    reference_payload = _load_json(REFERENCE_PATH)
    selector_model = _load_json(SELECTOR_MODEL_PATH)
    pitch_model = _load_json(PITCH_MODEL_PATH)

    rows = [dict(row) for row in (spectrum_cache.get("rows") or []) if isinstance(row, dict)]
    rows_by_measure = _rows_by_measure(rows)
    grid = _grid_lookup(raw_cache)

    validation_reference = _reference_sets(reference_payload, VALIDATION_MEASURES)
    development_reference = _reference_sets(reference_payload, DEVELOPMENT_MEASURES)
    holdout_reference = _reference_sets(reference_payload, HOLDOUT_MEASURES)

    all_measures = set(range(1, 17))
    scores_all, evidence_all = _score_measures(rows_by_measure, grid, all_measures, selector_model)
    base_threshold = float(selector_model["threshold"])

    print("=== V143 REPETITION-AWARE EVENT RECOVERY SELECTOR ===")
    print("Base selector threshold:", base_threshold)
    print("Configuration chosen on measures 9-12 only")
    print("Measures 13-16 used only as diagnostic evaluation")
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")

    best: dict[str, Any] | None = None
    searched = 0
    validation_context = set(range(1, 13))
    for margin in MARGINS:
        for min_support in MIN_SUPPORTS:
            for phase_modulus in PHASE_MODULI:
                searched += 1
                recovered_context = _recover(
                    scores_all,
                    evidence_all,
                    validation_context,
                    base_threshold,
                    margin,
                    min_support,
                    phase_modulus,
                )
                active_validation = {key for key in recovered_context if key[0] in VALIDATION_MEASURES}
                loc, e2e = _evaluate_candidate(
                    active_validation,
                    validation_reference,
                    rows_by_measure,
                    grid,
                    selector_model,
                    pitch_model,
                )
                objective = (
                    0.70 * float(e2e["pitchF1Percent"])
                    + 0.20 * float(loc["locationF1Percent"])
                    + 0.10 * float(e2e["exactPitchSetPercent"])
                )
                candidate = {
                    "margin": float(margin),
                    "minimumRecurrenceSupport": float(min_support),
                    "phaseModulus": int(phase_modulus),
                    "validationObjectivePercent": round(objective, 3),
                    "validationLocation": loc,
                    "validationEndToEnd": e2e,
                }
                if best is None or (
                    objective,
                    float(e2e["pitchF1Percent"]),
                    float(loc["locationRecallPercent"]),
                    float(loc["locationPrecisionPercent"]),
                ) > (
                    float(best["validationObjectivePercent"]),
                    float(best["validationEndToEnd"]["pitchF1Percent"]),
                    float(best["validationLocation"]["locationRecallPercent"]),
                    float(best["validationLocation"]["locationPrecisionPercent"]),
                ):
                    best = candidate

    if best is None:
        raise RuntimeError("No repetition-recovery configuration evaluated")

    development_context = set(range(1, 13))
    development_active_all = _recover(
        scores_all,
        evidence_all,
        development_context,
        base_threshold,
        float(best["margin"]),
        float(best["minimumRecurrenceSupport"]),
        int(best["phaseModulus"]),
    )
    development_active = {key for key in development_active_all if key[0] in DEVELOPMENT_MEASURES}
    dev_loc, dev_e2e = _evaluate_candidate(
        development_active,
        development_reference,
        rows_by_measure,
        grid,
        selector_model,
        pitch_model,
    )

    # Holdout remains label-free during inference. Repetition support may use the
    # entire analyzed intro, exactly as a production decoder can use the full song
    # after upload; only the grading below touches professional labels.
    full_active = _recover(
        scores_all,
        evidence_all,
        all_measures,
        base_threshold,
        float(best["margin"]),
        float(best["minimumRecurrenceSupport"]),
        int(best["phaseModulus"]),
    )
    holdout_active = {key for key in full_active if key[0] in HOLDOUT_MEASURES}
    hold_loc, hold_e2e = _evaluate_candidate(
        holdout_active,
        holdout_reference,
        rows_by_measure,
        grid,
        selector_model,
        pitch_model,
    )

    report = {
        "model": "v143-repetition-aware-event-recovery-selector",
        "baseSelectorThreshold": base_threshold,
        "bestConfiguration": {
            "margin": best["margin"],
            "minimumRecurrenceSupport": best["minimumRecurrenceSupport"],
            "phaseModulus": best["phaseModulus"],
            "validationObjectivePercent": best["validationObjectivePercent"],
        },
        "validationLocation": best["validationLocation"],
        "validationEndToEnd": best["validationEndToEnd"],
        "developmentLocation": dev_loc,
        "developmentEndToEnd": dev_e2e,
        "holdoutLocation": hold_loc,
        "holdoutEndToEnd": hold_e2e,
        "professionalReferenceUsedByAnalyzer": False,
        "professionalReferenceRequiredAtRuntime": False,
        "productionModified": False,
        "productionPromotionAllowed": False,
        "evaluationNote": "Measures 13-16 are now diagnostic holdout because prior architecture iterations have already inspected them; use a fresh song/section before promotion.",
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(report, indent=2) + "\n")

    print("\n=== BEST VALIDATION RECOVERY CONFIGURATION ===")
    print(json.dumps(report["bestConfiguration"], indent=2))
    print("\n=== VALIDATION LOCATION 9-12 ===")
    print(json.dumps(report["validationLocation"], indent=2))
    print("\n=== VALIDATION END-TO-END 9-12 ===")
    print(json.dumps(report["validationEndToEnd"], indent=2))
    print("\n=== DEVELOPMENT LOCATION 1-12 ===")
    print(json.dumps(report["developmentLocation"], indent=2))
    print("\n=== DEVELOPMENT END-TO-END 1-12 ===")
    print(json.dumps(report["developmentEndToEnd"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT LOCATION 13-16 ===")
    print(json.dumps(report["holdoutLocation"], indent=2))
    print("\n=== DIAGNOSTIC HOLDOUT END-TO-END 13-16 ===")
    print(json.dumps(report["holdoutEndToEnd"], indent=2))

    hold_loc_recall = float(hold_loc["locationRecallPercent"])
    hold_pitch_f1 = float(hold_e2e["pitchF1Percent"])
    if hold_loc_recall >= 80.0 and hold_pitch_f1 >= 80.0:
        diagnosis = "repetition-recovery-closes-most-of-event-selection-gap"
    elif hold_loc_recall >= 70.0 and hold_pitch_f1 >= 72.0:
        diagnosis = "repetition-recovery-helps-but-event-selector-still-needs-sequence-model"
    else:
        diagnosis = "simple-repetition-recovery-insufficient-build-sequence-event-model"
    print("\nDIAGNOSIS:", diagnosis)
    print("Professional reference used by analyzer: False")
    print("Professional reference required at runtime: False")
    print("Production modified: False")
    print("Production promotion allowed: False")
    print("NOTE: measures 13-16 are diagnostic, not a fresh untouched holdout anymore.")
    print("Output:", OUTPUT_PATH.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()

```


## public/training/v143-musical-reconstruction-calibration/intro-structured-event-decoder-check-model.json

```json
{
  "model": "v143-final-structured-event-decoder-check",
  "countPolicy": "per-measure",
  "countMultiplier": 1.05,
  "sequenceWeight": 1.0,
  "recurrenceWeight": 1.0,
  "validationObjectivePercent": 96.103,
  "assignWindowMs": 200,
  "residualPenalty": 2.0,
  "professionalReferenceRequiredAtRuntime": false
}
```


## public/training/v143-musical-reconstruction-calibration/intro-correlation-safe-grid-event-selector-model.json

```json
{
  "model": "v143-correlation-safe-grid-event-selector",
  "trainingMeasures": "1-8",
  "validationMeasures": "9-12",
  "developmentMeasures": "1-12",
  "diagnosticMeasures": "13-16",
  "windowMs": 100,
  "l2": 10.0,
  "threshold": 0.27,
  "neutralizedFeatureColumns": [
    19,
    26,
    33
  ],
  "neutralizedFeatureNames": [
    "attackMax:viewCorrelation",
    "earlyMean:viewCorrelation",
    "sustainMean:viewCorrelation"
  ],
  "neutralizedRawValue": 1.0,
  "featureMean": [
    1.0,
    -0.01439254,
    0.09639307,
    0.28467112,
    0.65694444,
    0.18843537,
    0.57708333,
    0.99722222,
    0.80694444,
    0.91649306,
    1.0,
    0.99583333,
    1.52957176,
    0.33720289,
    0.48605214,
    2.07874587,
    0.28088985,
    5.4578663,
    5.4588353,
    1.0,
    0.35575739,
    0.53737323,
    2.4766193,
    0.43716118,
    5.94566634,
    5.94795531,
    1.0,
    0.33997705,
    0.51002514,
    2.33072011,
    0.42977956,
    5.65552774,
    5.65611384,
    1.0,
    -0.01674261,
    0.01118705
  ],
  "featureStd": [
    1.0,
    0.11452518,
    0.06349439,
    0.08082243,
    0.08241391,
    0.0939687,
    0.28777915,
    0.03716413,
    0.26064897,
    0.48367255,
    1.0,
    0.03200477,
    0.3668336,
    0.0884059,
    0.10377237,
    0.47353624,
    0.24514231,
    1.23726342,
    1.23847959,
    1.0,
    0.0879877,
    0.10986713,
    0.55228282,
    0.37986083,
    1.27296256,
    1.27501106,
    1.0,
    0.08070333,
    0.10287141,
    0.55790574,
    0.36487054,
    1.18319291,
    1.1834575,
    1.0,
    0.70887055,
    0.70505111
  ],
  "weights": [
    0.5,
    -0.0,
    0.03649541,
    0.03924443,
    0.00172398,
    -0.06355477,
    -0.01393956,
    -0.01393956,
    0.01189265,
    -0.03461514,
    0.11632987,
    0.0,
    -0.02990847,
    0.05656503,
    -0.01614589,
    -0.08172875,
    -0.08197069,
    0.00605689,
    -0.05283145,
    -0.0625844,
    -0.0,
    -0.05396719,
    0.0076009,
    0.14635933,
    0.00906895,
    -0.00943237,
    -0.01668868,
    0.0,
    -0.0077387,
    0.08204458,
    0.03447195,
    -0.01203612,
    0.05191543,
    0.04776922,
    0.0,
    -0.08258206,
    0.04549953
  ],
  "professionalReferenceRequiredAtRuntime": false,
  "verse1ReferenceUsedForTraining": false,
  "productionModified": false
}
```


## public/training/v143-musical-reconstruction-calibration/sequence-model-17-96-rejection-report.txt

```text
=== V143 FROZEN SEQUENCE GRADING 17-96 ===
Candidate frozen before grading: True
97-113 chunk loaded            : False

=== 17-32 ===
BASE 0.27 N=136 REF=115 TP/FP/FN=65/71/50 P=0.4779 R=0.5652 F1=0.5179
SEQUENCE  N=211 REF=115 TP/FP/FN=95/116/20 P=0.4502 R=0.8261 F1=0.5828
F1 delta sequence-base: +0.0649

=== 33-48 ===
BASE 0.27 N=173 REF=93 TP/FP/FN=72/101/21 P=0.4162 R=0.7742 F1=0.5414
SEQUENCE  N=222 REF=93 TP/FP/FN=82/140/11 P=0.3694 R=0.8817 F1=0.5206
F1 delta sequence-base: -0.0207

=== 49-64 ===
BASE 0.27 N=134 REF=110 TP/FP/FN=75/59/35 P=0.5597 R=0.6818 F1=0.6148
SEQUENCE  N=215 REF=110 TP/FP/FN=93/122/17 P=0.4326 R=0.8455 F1=0.5723
F1 delta sequence-base: -0.0424

=== 65-80 ===
BASE 0.27 N=157 REF=50 TP/FP/FN=37/120/13 P=0.2357 R=0.7400 F1=0.3575
SEQUENCE  N=199 REF=50 TP/FP/FN=40/159/10 P=0.2010 R=0.8000 F1=0.3213
F1 delta sequence-base: -0.0362

=== 81-96 ===
BASE 0.27 N=165 REF=65 TP/FP/FN=54/111/11 P=0.3273 R=0.8308 F1=0.4696
SEQUENCE  N=204 REF=65 TP/FP/FN=59/145/6 P=0.2892 R=0.9077 F1=0.4387
F1 delta sequence-base: -0.0309

=== COMBINED 17-96 ===
BASE 0.27 N=765 REF=433 TP/FP/FN=303/462/130 P=0.3961 R=0.6998 F1=0.5058
SEQUENCE  N=1051 REF=433 TP/FP/FN=369/682/64 P=0.3511 R=0.8522 F1=0.4973
Combined F1 delta: -0.0085

=== ROBUSTNESS ===
blocks improved : 1 / 5
blocks tied     : 0 / 5
blocks worsened : 4 / 5
worst block delta: -0.0424
mean block delta : -0.0131

=== SAFETY / PROVENANCE ===
97-113 professional chunk loaded : False
Frozen candidate modified         : False
Sequence model refit              : False
Sequence parameters modified      : False
Base model modified               : False
Production modified               : False

```


## Relevant V143 inventory

```text
analyzer/v143_ai_tab_cpu_provenance.py
analyzer/v143_ai_tab_gpu_worker.py
analyzer/v143_ai_tab_gpu_worker_historical_defaults.py
analyzer/v143_candidate_timing_adapter.py
analyzer/v143_deterministic_separator.py
analyzer/v143_fresh_section2_reference_free_capture.py
analyzer/v143_fresh_section3_reference_free_capture.py
analyzer/v143_fresh_section4_reference_free_capture.py
analyzer/v143_fresh_section5_reference_free_capture.py
analyzer/v143_fresh_verse1_frozen_predict.py
analyzer/v143_fresh_verse1_reference_free_capture.py
analyzer/v143_intro_capture_analysis_cache.py
analyzer/v143_intro_capture_onset_spectrum_cache.py
analyzer/v143_intro_capture_raw_attack_cache.py
analyzer/v143_intro_capture_raw_attack_harmonic_cache.py
analyzer/v143_intro_capture_spectral_pitch_cache.py
analyzer/v143_intro_consensus_alignment_refinement.py
analyzer/v143_intro_constrained_count_reranker.py
analyzer/v143_intro_harmonic_family_rank_diagnostic.py
analyzer/v143_intro_joint_sparse_pitchset_diagnostic.py
analyzer/v143_intro_kong_pitch_benchmark.py
analyzer/v143_intro_learned_grid_event_selector.py
analyzer/v143_intro_learned_onset_spectral_set_model.py
analyzer/v143_intro_onset_group_sequence_model.py
analyzer/v143_intro_pitch_recovery_neighbor_sweep.py
analyzer/v143_intro_raw_attack_harmonic_rank_diagnostic.py
analyzer/v143_intro_raw_attack_pair_ranker.py
analyzer/v143_intro_raw_attack_pitch_rank_diagnostic.py
analyzer/v143_intro_raw_attack_temporal_diagnostic.py
analyzer/v143_intro_repetition_consensus_decoder.py
analyzer/v143_intro_repetition_consensus_decoder_fast.py
analyzer/v143_intro_repetition_recovery_event_selector.py
analyzer/v143_intro_selection_recovery_sweep.py
analyzer/v143_intro_sequence_event_model.py
analyzer/v143_intro_softlabel_temporal_assignment.py
analyzer/v143_intro_spectral_pitch_ranker.py
analyzer/v143_intro_stage_diagnostic.py
analyzer/v143_intro_structured_event_decoder_check.py
analyzer/v143_intro_supervised_pitch_ranker.py
analyzer/v143_intro_supervised_temporal_assignment.py
analyzer/v143_intro_synthtab_tabcnn_benchmark.py
analyzer/v143_intro_temporal_assignment_oracle.py
analyzer/v143_modal_bend_consensus_e2e_smoke.py
analyzer/v143_modal_bend_e2e_smoke.py
analyzer/v143_modal_deterministic_dependency_smoke.py
analyzer/v143_modal_domain_training_only.py
analyzer/v143_modal_e2e_smoke.py
analyzer/v143_modal_http_endpoint.py
analyzer/v143_modal_http_live_smoke.py
analyzer/v143_modal_legato_e2e_smoke.py
analyzer/v143_modal_live_endpoint.py
analyzer/v143_modal_repeatability_diagnostic.py
analyzer/v143_modal_rhythm_router.py
analyzer/v143_modal_seeded_repeatability_diagnostic.py
analyzer/v143_production_engine.py
analyzer/v143_production_separator.py
analyzer/v143_professional_intro_baseline.py
analyzer/v143_reference_free_rhythm_pipeline.py
analyzer/v143_reference_free_timing.py
analyzer/v143_rhythm_bend_consensus.py
analyzer/v143_rhythm_bend_evidence.py
analyzer/v143_rhythm_deterministic_stem_provider.py
analyzer/v143_rhythm_event_assembly.py
analyzer/v143_rhythm_guitar_note_mapper.py
analyzer/v143_rhythm_legato_evidence.py
analyzer/v143_rhythm_output_adapter.py
analyzer/v143_rhythm_runtime.py
analyzer/v143_rhythm_stem_provider.py
analyzer/v143_rhythm_sustain_technique_enricher.py
analyzer/v143_section2_duration_state_capture.py
analyzer/v143_section2_mix_contrast_capture.py
analyzer/v143_section2_transient_state_capture.py
analyzer/v143_section3_duration_state_capture.py
analyzer/v143_section3_mix_contrast_capture.py
analyzer/v143_section3_transient_state_capture.py
analyzer/v143_seeded_audio_separator.py
analyzer/v143_seeded_audio_separator_cli.py
analyzer/v143_seeded_separator.py
analyzer/v143_vercel_audio_request_adapter.py
```


## Calibration artifact inventory — names only

```text
baseline-intro-grade.json
fresh-17-96-correlation-safe-sequence-freeze-manifest.json
fresh-17-96-correlation-safe-sequence-frozen-events.json
fresh-section2-correlation-safe-frozen-events.json
fresh-section2-duration-state-cache.json
fresh-section2-first-reference-event-grade.json
fresh-section2-mix-contrast-cache.json
fresh-section2-reference-free-cache.json
fresh-section2-transient-state-cache.json
fresh-section3-correlation-safe-frozen-events.json
fresh-section3-duration-state-cache.json
fresh-section3-first-reference-event-grade.json
fresh-section3-mix-contrast-cache.json
fresh-section3-reference-free-cache.json
fresh-section3-transient-state-cache.json
fresh-section4-blind-prediction-freeze-manifest.json
fresh-section4-final-holdout-grade.json
fresh-section4-reference-free-cache.json
fresh-section4-threshold027-frozen-events.json
fresh-section4-threshold045-frozen-events.json
fresh-section5-base027-frozen-events.json
fresh-section5-base027-recovery-frozen-events.json
fresh-section5-blind-prediction-freeze-manifest.json
fresh-section5-final-blind-holdout-grade.json
fresh-section5-reference-free-cache.json
fresh-verse1-first-reference-grade.json
fresh-verse1-frozen-predictions.json
fresh-verse1-reference-free-cache.json
intro-analysis-cache.json
intro-consensus-alignment-refinement-model.json
intro-consensus-alignment-refinement-report.json
intro-constrained-count-reranker-model.json
intro-constrained-count-reranker-report.json
intro-correlation-safe-attack-novelty-gate-model.json
intro-correlation-safe-attack-novelty-gate-report.json
intro-correlation-safe-grid-event-selector-model.json
intro-correlation-safe-grid-event-selector-report.json
intro-correlation-safe-grid-event-selector-threshold027-candidate.json
intro-correlation-safe-grid-event-selector-threshold045-incumbent.json
intro-correlation-safe-sequence-event-model-report.json
intro-correlation-safe-sequence-event-model.json
intro-harmonic-family-rank-diagnostic.json
intro-joint-sparse-pitchset-diagnostic.json
intro-kong-pitch-benchmark.json
intro-learned-grid-event-selector-model.json
intro-learned-grid-event-selector-report.json
intro-learned-onset-spectral-set-model.json
intro-learned-onset-spectral-set-report.json
intro-onset-group-sequence-model-report.json
intro-onset-group-sequence-model.json
intro-onset-spectrum-cache.json
intro-pitch-recovery-neighbor-sweep.json
intro-raw-attack-cache.json
intro-raw-attack-harmonic-cache.json
intro-raw-attack-harmonic-rank-diagnostic.json
intro-raw-attack-pair-ranker-model.json
intro-raw-attack-pair-ranker-report.json
intro-raw-attack-pitch-rank-diagnostic.json
intro-raw-attack-temporal-diagnostic.json
intro-repetition-consensus-decoder-fast.json
intro-repetition-recovery-base027-lobo-validation-report.json
intro-repetition-recovery-base027-robust-candidate.json
intro-repetition-recovery-event-selector-report.json
intro-selection-recovery-sweep.json
intro-sequence-event-model-report.json
intro-sequence-event-model.json
intro-softlabel-temporal-assignment-model.json
intro-softlabel-temporal-assignment-report.json
intro-spectral-pitch-cache.json
intro-spectral-pitch-ranker-model.json
intro-spectral-pitch-ranker-report.json
intro-stage-diagnostic.json
intro-structured-event-decoder-check-model.json
intro-structured-event-decoder-check-report.json
intro-supervised-pitch-ranker-model.json
intro-supervised-pitch-ranker-report.json
intro-supervised-temporal-assignment-model.json
intro-supervised-temporal-assignment-report.json
intro-synthtab-tabcnn-benchmark.json
intro-temporal-assignment-oracle.json
recovery-family-final-rejection-report.json
sequence-model-17-96-rejection-report.txt
threshold027-blind-holdout-promotion-report.json
threshold027-calibration-freeze-report.json
```


## Provenance guardrails

- Professional-reference JSON contents copied into this bundle: **False**
- 97+ professional-reference contents copied: **False**
- Untouched holdout contents copied: **False**
- Models modified by bundle generation: **False**
- Production modified by bundle generation: **False**
- Bundle is diagnostic/source material only.

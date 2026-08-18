from __future__ import annotations

import inspect

import v143_modal_live_endpoint as live


def main() -> None:
    source = inspect.getsource(live)
    request_source = inspect.getsource(live.rhythm_v143_request)
    dispatch_source = inspect.getsource(live.dispatch_authorized_request)

    checks = {
        "Deterministic separator module packaged": '"v143_deterministic_separator"' in source,
        "Deterministic stem provider packaged": '"v143_rhythm_deterministic_stem_provider"' in source,
        "Strict bend consensus module packaged": '"v143_rhythm_bend_consensus"' in source,
        "Legato evidence module packaged": '"v143_rhythm_legato_evidence"' in source,
        "Deterministic Rhythm provider wired": "build_deterministic_rhythm_stem_bundle" in request_source,
        "Strict bend consensus wired": "enrich_router_assembly_with_consensus_bends" in request_source,
        "Legato evidence wired": "enrich_router_assembly_with_legato" in request_source,
        "Bends run before legato": (
            request_source.find("enrich_router_assembly_with_consensus_bends")
            < request_source.find("enrich_router_assembly_with_legato")
        ),
        "Combined technique enricher wired to router": "assembly_enricher=enrich_rhythm_techniques" in request_source,
        "Seed 143 advertised": '"separatorSeed": 143' in request_source,
        "Demucs shifts=1 advertised": '"demucsShifts": 1' in request_source,
        "Two-view bend consensus advertised": '"bendConsensusViews": 2' in request_source,
        "Two-view legato consensus advertised": '"legatoConsensusViews": 2' in request_source,
        "Live V143 version 4 advertised": '"version": 4' in request_source,
        "Reference-free live identity preserved": '"referenceFree": True' in request_source,
        "Professional reference excluded": '"professionalReferenceUsed": False' in request_source,
        "Runtime labels excluded": '"runtimeLabelsRequired": False' in request_source,
        "Rhythm-only dispatch preserved": 'if transcription_type == "rhythm"' in dispatch_source,
        "Lead/Bass legacy fallback preserved": "return legacy_handler(dict(payload))" in dispatch_source,
    }

    ready = all(checks.values())

    print("=== V143 DETERMINISTIC STRICT TECHNIQUE LIVE WIRING VERIFIED ===")
    for label, value in checks.items():
        print(f"{label}: {value}")
    print(f"READY FOR UPDATED MODAL DEPENDENCY SMOKE: {ready}")

    if not ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

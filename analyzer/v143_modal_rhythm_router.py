from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from v143_reference_free_rhythm_pipeline import analyze_reference_free_rhythm
from v143_rhythm_event_assembly import assemble_rhythm_events
from v143_rhythm_output_adapter import build_rhythm_output


LegacyAnalyzer = Callable[[str, str], dict[str, Any]]
RhythmStemProvider = Callable[[str | Path], "RhythmStemBundle"]
RhythmPipeline = Callable[..., Any]
EventAssembler = Callable[[Any], Any]
AssemblyEnricher = Callable[[Any, "RhythmStemBundle"], Any]
OutputBuilder = Callable[[Any], dict[str, Any]]


@dataclass(frozen=True)
class RhythmStemBundle:
    """Reference-free production inputs required by the frozen V143 rhythm carrier."""

    candidate_stem_paths: tuple[str | Path, ...]
    carrier_stem_a_path: str | Path
    carrier_stem_b_path: str | Path

    def validate(self) -> "RhythmStemBundle":
        if not self.candidate_stem_paths:
            raise ValueError("Rhythm stem provider returned no candidate stems")

        candidate_paths = tuple(Path(path) for path in self.candidate_stem_paths)
        carrier_a = Path(self.carrier_stem_a_path)
        carrier_b = Path(self.carrier_stem_b_path)

        if any(not str(path).strip() for path in candidate_paths):
            raise ValueError("Rhythm candidate stem path cannot be empty")
        if not str(carrier_a).strip() or not str(carrier_b).strip():
            raise ValueError("Both V143 carrier stem paths are required")

        return RhythmStemBundle(
            candidate_stem_paths=candidate_paths,
            carrier_stem_a_path=carrier_a,
            carrier_stem_b_path=carrier_b,
        )


def route_normalized_audio(
    normalized_full_mix_path: str | Path,
    transcription_type: str,
    *,
    legacy_analyzer: LegacyAnalyzer,
    rhythm_stem_provider: RhythmStemProvider,
    rhythm_pipeline: RhythmPipeline = analyze_reference_free_rhythm,
    event_assembler: EventAssembler = assemble_rhythm_events,
    assembly_enricher: AssemblyEnricher | None = None,
    output_builder: OutputBuilder = build_rhythm_output,
    rhythm_pipeline_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Route only Rhythm Guitar into the V143 reference-free production chain.

    Lead Guitar and Bass are delegated byte-for-byte as returned by the existing
    analyzer. Rhythm Guitar bypasses the legacy note/voicing path and consumes a
    provider-supplied candidate/carrier stem bundle through the frozen V143 chain.

    Optional assembly enrichment happens strictly after frozen V143 selection,
    timing, pitch hypotheses, and deterministic string/fret mapping. It may append
    evidence-derived notation metadata, but it must return an assembly compatible
    with the existing output builder.
    """
    requested = str(transcription_type or "").strip().lower()
    if requested not in {"lead", "rhythm", "bass"}:
        raise ValueError("transcription_type must be lead, rhythm, or bass")

    full_mix = Path(normalized_full_mix_path)

    if requested != "rhythm":
        return legacy_analyzer(str(full_mix), requested)

    bundle = rhythm_stem_provider(full_mix)
    if not isinstance(bundle, RhythmStemBundle):
        raise TypeError("rhythm_stem_provider must return RhythmStemBundle")
    bundle = bundle.validate()

    kwargs = dict(rhythm_pipeline_kwargs or {})
    rhythm_result = rhythm_pipeline(
        full_mix,
        bundle.candidate_stem_paths,
        bundle.carrier_stem_a_path,
        bundle.carrier_stem_b_path,
        **kwargs,
    )
    assembly = event_assembler(rhythm_result)
    if assembly_enricher is not None:
        enriched = assembly_enricher(assembly, bundle)
        if enriched is None:
            raise TypeError("assembly_enricher returned None")
        assembly = enriched
    output = output_builder(assembly)

    if not isinstance(output, dict):
        raise TypeError("Rhythm output builder must return a dict")
    if not str(output.get("generatedTab") or "").strip():
        raise RuntimeError("V143 rhythm output returned no generatedTab")

    routed = dict(output)
    routed["rhythmRouting"] = {
        "version": 1,
        "mode": "v143-reference-free-rhythm-only",
        "requestedPart": "rhythm",
        "legacyLeadChanged": False,
        "legacyBassChanged": False,
        "normalizedFullMixTimingSource": True,
        "candidateStemCount": len(bundle.candidate_stem_paths),
        "pairedCarrierStemContractPreserved": True,
        "postSelectionEvidenceEnrichment": assembly_enricher is not None,
        "professionalReferenceUsed": False,
        "runtimeLabelsRequired": False,
    }
    return routed


__all__ = [
    "RhythmStemBundle",
    "route_normalized_audio",
]

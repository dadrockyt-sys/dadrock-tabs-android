from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if new in text:
        print(f"{label}: already applied")
        return
    if old not in text:
        raise RuntimeError(f"{label}: expected source block not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    print(f"{label}: applied")


def patch_render_contract() -> None:
    path = ROOT / "lib" / "v143RenderContract.js"
    replace_once(
        path,
        "    const output = {\n      eventIndex,\n      measure,",
        "    const stableEventIndex = optionalInteger(event.eventIndex);\n\n    const output = {\n      eventIndex:\n        stableEventIndex !== null && stableEventIndex >= 0\n          ? stableEventIndex\n          : eventIndex,\n      measure,",
        "render contract preserves stable eventIndex",
    )


def patch_analyzer_route() -> None:
    path = ROOT / "app" / "api" / "analyze-audio-tab" / "route.js"
    replace_once(
        path,
        "import { NextResponse } from 'next/server';\n",
        "import { NextResponse } from 'next/server';\nimport { projectV143RenderEvents } from '@/lib/v143RenderContract';\n",
        "analyzer imports render contract",
    )
    replace_once(
        path,
        "export const maxDuration = 150;",
        "export const maxDuration = 600;",
        "analyzer duration raised to 600 seconds",
    )
    replace_once(
        path,
        "    return NextResponse.json({\n      generatedTab,",
        "    const renderEvents =\n      analyzerData?.liveV143?.referenceFree === true\n        ? projectV143RenderEvents(analyzerData?.events)\n        : [];\n\n    return NextResponse.json({\n      generatedTab,",
        "analyzer projects V143 render events",
    )
    replace_once(
        path,
        "      techniques: Array.isArray(\n        analyzerData?.techniques\n      )\n        ? analyzerData.techniques\n        : [],\n      confidence:",
        "      techniques: Array.isArray(\n        analyzerData?.techniques\n      )\n        ? analyzerData.techniques\n        : [],\n      renderEvents,\n      renderContractVersion:\n        renderEvents.length > 0 ? 1 : null,\n      confidence:",
        "analyzer response exposes render-safe events",
    )


def patch_preview_route() -> None:
    path = ROOT / "app" / "api" / "generate-tab-preview" / "route.js"
    replace_once(
        path,
        "import { createTabPdf } from '@/lib/createTabPdfPolished';",
        "import { createAiTabPdf } from '@/lib/createAiTabPdf';\nimport { projectV143RenderEvents } from '@/lib/v143RenderContract';",
        "preview imports structured renderer",
    )
    replace_once(
        path,
        "    const keySignature = cleanText(body?.keySignature, 40);\n    const previewSystems = Math.min(",
        "    const keySignature = cleanText(body?.keySignature, 40);\n    const analysisEngine = cleanText(body?.analysisEngine, 80);\n    const renderEvents = projectV143RenderEvents(body?.renderEvents);\n    const previewSystems = Math.min(",
        "preview accepts render metadata",
    )
    replace_once(
        path,
        "    const pdfBytes = await createTabPdf({",
        "    const pdfBytes = await createAiTabPdf({",
        "preview uses renderer dispatcher",
    )
    replace_once(
        path,
        "      keySignature,\n      preview: true,",
        "      keySignature,\n      analysisEngine,\n      renderEvents,\n      preview: true,",
        "preview forwards render events",
    )


def patch_full_pdf_route() -> None:
    path = ROOT / "app" / "api" / "generate-tab-pdf" / "route.js"
    replace_once(
        path,
        "import { createTabPdf } from '@/lib/createTabPdfPolished';",
        "import { createAiTabPdf } from '@/lib/createAiTabPdf';\nimport { projectV143RenderEvents } from '@/lib/v143RenderContract';",
        "full PDF imports structured renderer",
    )
    replace_once(
        path,
        "    const keySignature = cleanText(body?.keySignature, 40);\n\n    const emailIsValid =",
        "    const keySignature = cleanText(body?.keySignature, 40);\n    const analysisEngine = cleanText(body?.analysisEngine, 80);\n    const renderEvents = projectV143RenderEvents(body?.renderEvents);\n\n    const emailIsValid =",
        "full PDF accepts render metadata",
    )
    replace_once(
        path,
        "    const pdfBytes = await createTabPdf({",
        "    const pdfBytes = await createAiTabPdf({",
        "full PDF uses renderer dispatcher",
    )
    replace_once(
        path,
        "      keySignature,\n      preview: false,",
        "      keySignature,\n      analysisEngine,\n      renderEvents,\n      preview: false,",
        "full PDF forwards render events",
    )


def patch_ai_tab_page() -> None:
    path = ROOT / "app" / "ai-tab" / "page.js"
    replace_once(
        path,
        "  const [\n    previewReady,\n    setPreviewReady,\n  ] = useState(false);",
        "  const [\n    analysisMetadata,\n    setAnalysisMetadata,\n  ] = useState(null);\n\n  const [\n    previewReady,\n    setPreviewReady,\n  ] = useState(false);",
        "AI tab stores analyzer render metadata",
    )
    replace_once(
        path,
        "    setGeneratedTab('');\n    setPreviewReady(false);",
        "    setGeneratedTab('');\n    setAnalysisMetadata(null);\n    setPreviewReady(false);",
        "AI tab resets render metadata",
    )
    replace_once(
        path,
        "  keySignature:\n    analysisMetadata.keySignature || '',\n\n            previewSystems: 4,",
        "  keySignature:\n    analysisMetadata.keySignature || '',\n\n  analysisEngine:\n    analysisMetadata.analysisEngine || '',\n\n  techniques:\n    Array.isArray(analysisMetadata.techniques)\n      ? analysisMetadata.techniques\n      : [],\n\n  renderEvents:\n    Array.isArray(analysisMetadata.renderEvents)\n      ? analysisMetadata.renderEvents\n      : [],\n\n            previewSystems: 4,",
        "preview request sends techniques and events",
    )
    replace_once(
        path,
        "      setGeneratedTab('');\n      setPreviewReady(false);\n      setPreviewUnlocked(false);",
        "      setGeneratedTab('');\n      setAnalysisMetadata(null);\n      setPreviewReady(false);\n      setPreviewUnlocked(false);",
        "new generation clears prior render metadata",
    )
    replace_once(
        path,
        "        setGeneratedTab(\n          tabContent\n        );\n\n        await requestPreviewPdf(",
        "        setGeneratedTab(\n          tabContent\n        );\n        setAnalysisMetadata(analyzerData);\n\n        await requestPreviewPdf(",
        "AI tab retains analyzer metadata",
    )
    replace_once(
        path,
        "        setGeneratedTab('');\n        setPreviewReady(false);\n        clearPreviewPdfUrl();",
        "        setGeneratedTab('');\n        setAnalysisMetadata(null);\n        setPreviewReady(false);\n        clearPreviewPdfUrl();",
        "failed generation clears render metadata",
    )
    replace_once(
        path,
        "              generatedTab,\n\n              sourceType,",
        "              generatedTab,\n\n              tuning:\n                analysisMetadata?.tuning || 'Standard Tuning',\n\n              tempo:\n                analysisMetadata?.tempo || 120,\n\n              timeSignature:\n                analysisMetadata?.timeSignature || '4/4',\n\n              keySignature:\n                analysisMetadata?.keySignature || '',\n\n              analysisEngine:\n                analysisMetadata?.analysisEngine || '',\n\n              techniques:\n                Array.isArray(analysisMetadata?.techniques)\n                  ? analysisMetadata.techniques\n                  : [],\n\n              renderEvents:\n                Array.isArray(analysisMetadata?.renderEvents)\n                  ? analysisMetadata.renderEvents\n                  : [],\n\n              sourceType,",
        "finished PDF receives analyzer metadata",
    )


def main() -> None:
    patch_render_contract()
    patch_analyzer_route()
    patch_preview_route()
    patch_full_pdf_route()
    patch_ai_tab_page()
    print("=== V143 RENDER PIPELINE WIRING APPLIED ===")
    print("Run: python analyzer/verify_v143_render_pipeline_wiring.py")


if __name__ == "__main__":
    main()

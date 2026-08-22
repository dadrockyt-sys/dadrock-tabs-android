#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/ai-tab/page.js"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_page() -> bool:
    page = PAGE.read_text(encoding="utf-8")

    already_integrated = (
        "setAnalysisMetadata" in page
        and "analysisMetadata?.renderEvents" in page
        and "analysisMetadata.renderEvents" in page
    )
    if already_integrated:
        print("Jimmy PAIge browser transport is already integrated")
        return False

    page = replace_once(
        page,
        """  const [\n    generatedTab,\n    setGeneratedTab,\n  ] = useState('');\n""",
        """  const [\n    generatedTab,\n    setGeneratedTab,\n  ] = useState('');\n\n  const [\n    analysisMetadata,\n    setAnalysisMetadata,\n  ] = useState(null);\n""",
        "analysis metadata state",
    )

    page = replace_once(
        page,
        """    setGeneratedTab('');\n    setPreviewReady(false);\n""",
        """    setGeneratedTab('');\n    setAnalysisMetadata(null);\n    setPreviewReady(false);\n""",
        "reset analysis metadata",
    )

    page = replace_once(
        page,
        """      setGeneratedTab('');\n      setPreviewReady(false);\n""",
        """      setGeneratedTab('');\n      setAnalysisMetadata(null);\n      setPreviewReady(false);\n""",
        "generation-start analysis reset",
    )

    page = replace_once(
        page,
        """        setGeneratedTab(\n          tabContent\n        );\n\n        await requestPreviewPdf(\n""",
        """        setGeneratedTab(\n          tabContent\n        );\n        setAnalysisMetadata(\n          analyzerData\n        );\n\n        await requestPreviewPdf(\n""",
        "preserve analyzer result",
    )

    page = replace_once(
        page,
        """        setGeneratedTab('');\n        setPreviewReady(false);\n""",
        """        setGeneratedTab('');\n        setAnalysisMetadata(null);\n        setPreviewReady(false);\n""",
        "clear analyzer result after generation failure",
    )

    page = replace_once(
        page,
        """  keySignature:\n    analysisMetadata.keySignature || '',\n\n            previewSystems: 4,\n""",
        """  keySignature:\n    analysisMetadata.keySignature || '',\n\n  analysisEngine:\n    analysisMetadata.analysisEngine || '',\n\n  techniques:\n    Array.isArray(analysisMetadata.techniques)\n      ? analysisMetadata.techniques\n      : [],\n\n  renderEvents:\n    Array.isArray(analysisMetadata.renderEvents)\n      ? analysisMetadata.renderEvents\n      : [],\n\n  measureGrid:\n    analysisMetadata.measureGrid || null,\n\n  confidence:\n    analysisMetadata.confidence ?? null,\n\n  difficulty:\n    analysisMetadata.difficulty || null,\n\n            previewSystems: 4,\n""",
        "preview structured metadata",
    )

    page = replace_once(
        page,
        """              generatedTab,\n\n              sourceType,\n""",
        """              generatedTab,\n\n              tuning:\n                analysisMetadata?.tuning || 'Standard Tuning',\n\n              tempo:\n                analysisMetadata?.tempo || 120,\n\n              timeSignature:\n                analysisMetadata?.timeSignature || '4/4',\n\n              keySignature:\n                analysisMetadata?.keySignature || '',\n\n              analysisEngine:\n                analysisMetadata?.analysisEngine || '',\n\n              techniques:\n                Array.isArray(analysisMetadata?.techniques)\n                  ? analysisMetadata.techniques\n                  : [],\n\n              renderEvents:\n                Array.isArray(analysisMetadata?.renderEvents)\n                  ? analysisMetadata.renderEvents\n                  : [],\n\n              measureGrid:\n                analysisMetadata?.measureGrid || null,\n\n              confidence:\n                analysisMetadata?.confidence ?? null,\n\n              difficulty:\n                analysisMetadata?.difficulty || null,\n\n              sourceType,\n""",
        "finished PDF structured metadata",
    )

    PAGE.write_text(page, encoding="utf-8")
    return True


def main() -> None:
    changed = patch_page()
    print(
        "Jimmy PAIge browser upload-to-PDF transport applied"
        if changed
        else "Jimmy PAIge browser upload-to-PDF transport already present"
    )


if __name__ == "__main__":
    main()

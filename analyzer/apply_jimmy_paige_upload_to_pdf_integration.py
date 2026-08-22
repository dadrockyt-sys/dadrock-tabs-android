#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "app/ai-tab/page.js"
FINAL = ROOT / "app/api/generate-tab-pdf/route.js"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_page() -> None:
    page = PAGE.read_text(encoding="utf-8")

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
        """        setGeneratedTab(\n          tabContent\n        );\n\n        setAnalysisMetadata(\n          analyzerData\n        );\n\n        await requestPreviewPdf(\n""",
        "preserve analyzer result",
    )

    page = replace_once(
        page,
        """  keySignature:\n    analysisMetadata.keySignature || '',\n\n            previewSystems: 4,\n""",
        """  keySignature:\n    analysisMetadata.keySignature || '',\n\n  measureGrid:\n    analysisMetadata.measureGrid || null,\n\n  analysisEngine:\n    analysisMetadata.analysisEngine || '',\n\n  confidence:\n    analysisMetadata.confidence ?? null,\n\n  difficulty:\n    analysisMetadata.difficulty || null,\n\n  techniques:\n    Array.isArray(analysisMetadata.techniques)\n      ? analysisMetadata.techniques\n      : [],\n\n            previewSystems: 4,\n""",
        "preview structured metadata",
    )

    page = replace_once(
        page,
        """              generatedTab,\n\n              sourceType,\n""",
        """              generatedTab,\n\n              tuning:\n                analysisMetadata?.tuning || 'Standard Tuning',\n\n              tempo:\n                analysisMetadata?.tempo || 120,\n\n              timeSignature:\n                analysisMetadata?.timeSignature || '4/4',\n\n              keySignature:\n                analysisMetadata?.keySignature || '',\n\n              measureGrid:\n                analysisMetadata?.measureGrid || null,\n\n              analysisEngine:\n                analysisMetadata?.analysisEngine || '',\n\n              confidence:\n                analysisMetadata?.confidence ?? null,\n\n              difficulty:\n                analysisMetadata?.difficulty || null,\n\n              techniques:\n                Array.isArray(analysisMetadata?.techniques)\n                  ? analysisMetadata.techniques\n                  : [],\n\n              sourceType,\n""",
        "finished PDF structured metadata",
    )

    PAGE.write_text(page, encoding="utf-8")


def patch_final_route() -> None:
    final = FINAL.read_text(encoding="utf-8")

    final = replace_once(
        final,
        "import { createTabPdf } from '@/lib/createTabPdfPolished';\n",
        "import { createTabPdf } from '@/lib/createTabPdfPolished';\n"
        "import { createJimmyPaigeProfessionalPdf } from '@/lib/createJimmyPaigeProfessionalPdf';\n",
        "professional bridge import",
    )

    final = replace_once(
        final,
        """    const pdfBytes = await createTabPdf({\n      song,\n      artist,\n      transcriptionType,\n      generatedTab,\n      tuning,\n      tempo,\n      timeSignature,\n      keySignature,\n      preview: false,\n    });\n""",
        """    const useProfessionalRenderer =\n      process.env.JIMMY_PAIGE_PROFESSIONAL_PDF_V1 === 'true';\n\n    let pdfBytes;\n\n    if (useProfessionalRenderer) {\n      const result =\n        await createJimmyPaigeProfessionalPdf({\n          song,\n          artist,\n          transcriptionType,\n          generatedTab,\n          tuning,\n          tempo,\n          timeSignature,\n          keySignature,\n          preview: false,\n          measureGrid:\n            body?.measureGrid || null,\n          analysisEngine:\n            body?.analysisEngine || '',\n          confidence:\n            body?.confidence ?? null,\n          difficulty:\n            body?.difficulty || null,\n          techniques:\n            Array.isArray(body?.techniques)\n              ? body.techniques\n              : [],\n        });\n\n      pdfBytes = result.pdfBytes;\n    } else {\n      pdfBytes = await createTabPdf({\n        song,\n        artist,\n        transcriptionType,\n        generatedTab,\n        tuning,\n        tempo,\n        timeSignature,\n        keySignature,\n        preview: false,\n      });\n    }\n""",
        "feature-gated final renderer",
    )

    FINAL.write_text(final, encoding="utf-8")


def main() -> None:
    patch_page()
    patch_final_route()
    print("Jimmy PAIge upload-to-professional-PDF patch applied")


if __name__ == "__main__":
    main()

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

import cv2
import fitz
import numpy as np


def cluster_rows(values: list[int], tolerance: int = 3) -> list[int]:
    if not values:
        return []
    groups=[[values[0]]]
    for v in values[1:]:
        if v-groups[-1][-1] <= tolerance:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [round(median(g)) for g in groups]


def long_horizontal_rows(image: np.ndarray) -> list[int]:
    # Dark-pixel support across the musical body. Ignore page margins.
    h,w=image.shape
    x0=round(w*0.05); x1=round(w*0.97)
    dark=(image[:,x0:x1] < 175)
    support=dark.sum(axis=1)
    threshold=max(80, round((x1-x0)*0.42))
    return cluster_rows([int(i) for i,v in enumerate(support) if int(v)>=threshold], 3)


def candidate_staves(rows: list[int], expected_lines: int) -> list[dict]:
    out=[]
    if len(rows)<expected_lines:
        return out
    for i in range(len(rows)-expected_lines+1):
        g=rows[i:i+expected_lines]
        gaps=[g[j+1]-g[j] for j in range(expected_lines-1)]
        spacing=float(median(gaps))
        if not 5 <= spacing <= 35:
            continue
        irregular=max(abs(x-spacing) for x in gaps)
        if irregular > max(2.5, spacing*0.22):
            continue
        out.append({
            "rowsPixels":g,
            "spacingPixels":round(spacing,2),
            "irregularityPixels":round(irregular,2),
            "top":g[0],
            "bottom":g[-1],
        })
    # Keep non-overlapping candidates, preferring lower irregularity.
    out=sorted(out,key=lambda x:(x["top"],x["irregularityPixels"]))
    chosen=[]
    for cand in out:
        overlaps=False
        for prior in chosen:
            if min(cand["bottom"],prior["bottom"]) - max(cand["top"],prior["top"]) > 0:
                overlaps=True; break
        if not overlaps:
            chosen.append(cand)
    return chosen


def page_barline_candidates(image: np.ndarray, stave: dict) -> list[int]:
    h,w=image.shape
    y0=max(0,int(stave["top"]-stave["spacingPixels"]*1.2))
    y1=min(h,int(stave["bottom"]+stave["spacingPixels"]*1.2))
    region=(image[y0:y1,:] < 150)
    # Vertical ink through most of tablature height.
    support=region.sum(axis=0)
    need=max(4, round((y1-y0)*0.55))
    xs=[int(i) for i,v in enumerate(support) if int(v)>=need]
    if not xs:
        return []
    groups=[[xs[0]]]
    for x in xs[1:]:
        if x-groups[-1][-1] <= 4:
            groups[-1].append(x)
        else:
            groups.append([x])
    centers=[round(median(g)) for g in groups if len(g)>=1]
    # Exclude extreme page edges.
    return [x for x in centers if round(w*0.03) <= x <= round(w*0.98)]


def inspect_pdf(path: Path, role: str, expected_lines: int, out_dir: Path) -> dict:
    doc=fitz.open(path)
    out_dir.mkdir(parents=True,exist_ok=True)
    pages=[]
    total_staves=0
    total_boxes=0
    for pi,page in enumerate(doc,start=1):
        pix=page.get_pixmap(matrix=fitz.Matrix(2.5,2.5),alpha=False,colorspace=fitz.csGRAY)
        img=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width)
        rows=long_horizontal_rows(img)
        staves=candidate_staves(rows,expected_lines)
        annotated=cv2.cvtColor(img,cv2.COLOR_GRAY2BGR)
        page_boxes=0
        for si,stave in enumerate(staves,start=1):
            bars=page_barline_candidates(img,stave)
            stave["barlineColumnsPixels"]=bars
            stave["roughBoxCount"]=max(0,len(bars)-1)
            page_boxes += stave["roughBoxCount"]
            for y in stave["rowsPixels"]:
                cv2.line(annotated,(0,y),(pix.width-1,y),(255,0,0),1)
            for x in bars:
                cv2.line(annotated,(x,max(0,stave["top"]-10)),(x,min(pix.height-1,stave["bottom"]+10)),(0,0,255),1)
        preview=out_dir/f"{role}-page-{pi:02d}-structure.png"
        cv2.imwrite(str(preview),annotated)
        total_staves+=len(staves); total_boxes+=page_boxes
        pages.append({
            "pageNumber":pi,
            "widthPixels":pix.width,
            "heightPixels":pix.height,
            "longHorizontalRowCount":len(rows),
            "longHorizontalRowsPixels":rows,
            "tablatureStaveCount":len(staves),
            "roughBoxCount":page_boxes,
            "tablatureStaves":staves,
            "preview":str(preview),
        })
    return {
        "role":role,
        "pdfPath":str(path),
        "pageCount":len(doc),
        "expectedTabStringLines":expected_lines,
        "tablatureStaveCount":total_staves,
        "roughBoxCountAcrossPages":total_boxes,
        "pages":pages,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bass-pdf",required=True)
    ap.add_argument("--lead-pdf",required=True)
    ap.add_argument("--output",required=True)
    ap.add_argument("--preview-dir",required=True)
    args=ap.parse_args()
    root=Path(args.preview_dir)
    bass=inspect_pdf(Path(args.bass_pdf),"bass",4,root/"bass")
    lead=inspect_pdf(Path(args.lead_pdf),"lead",6,root/"lead")
    out={
        "schemaVersion":1,
        "kind":"gomyway-bass-lead-professional-pdf-structure-inventory-v1",
        "candidateAudioUsed":False,
        "candidatePredictionsUsed":False,
        "semanticNoteRecognitionPerformed":False,
        "professionalReferencesRemainAuthority":True,
        "expectedMeasureCoverageByRole":{"bass":[1,113],"lead":[1,113]},
        "bass":bass,
        "lead":lead,
        "interpretationBoundary":"Structure localization only. Rough box counts are not authoritative measure counts. No note, fret, pitch, timing, or technique label is inferred here.",
    }
    Path(args.output).write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({
        "bass":{"pages":bass["pageCount"],"staves":bass["tablatureStaveCount"],"roughBoxes":bass["roughBoxCountAcrossPages"]},
        "lead":{"pages":lead["pageCount"],"staves":lead["tablatureStaveCount"],"roughBoxes":lead["roughBoxCountAcrossPages"]},
    },indent=2))

if __name__=="__main__":
    main()

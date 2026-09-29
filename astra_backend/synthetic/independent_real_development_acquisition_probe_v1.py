#!/usr/bin/env python3
from __future__ import annotations
import argparse, asyncio, hashlib, json, re
from pathlib import Path
from urllib.parse import urlparse
from playwright.async_api import async_playwright

async def acquire(source_url: str, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    seen=[]
    chosen=None
    async with async_playwright() as p:
        browser=await p.chromium.launch(headless=True)
        context=await browser.new_context(accept_downloads=True)
        page=await context.new_page()
        async def on_response(resp):
            nonlocal chosen
            try:
                ct=(await resp.all_headers()).get("content-type","")
            except Exception:
                ct=""
            u=resp.url
            if "cdn.pixabay.com/audio/" in u and (".mp3" in u or ct.startswith("audio/")):
                seen.append({"url":u,"contentType":ct,"status":resp.status})
                if resp.status==200 and chosen is None:
                    chosen=u
        page.on("response", on_response)
        await page.goto(source_url, wait_until="domcontentloaded", timeout=90000)
        await page.wait_for_timeout(2500)

        # Trigger media loading without bypassing any access control.
        for label in ["Play","Free download"]:
            try:
                loc=page.get_by_role("button", name=re.compile(label, re.I))
                if await loc.count():
                    await loc.first.click(timeout=5000)
                    await page.wait_for_timeout(2500)
            except Exception:
                pass

        if chosen is None:
            html=await page.content()
            m=re.search(r'https://cdn\.pixabay\.com/audio/[^"\'<> ]+\.mp3', html)
            if m:
                chosen=m.group(0)

        if chosen is None:
            await browser.close()
            raise RuntimeError("no public Pixabay audio URL observed")

        resp=await context.request.get(chosen, timeout=90000)
        if not resp.ok:
            await browser.close()
            raise RuntimeError(f"audio GET failed status={resp.status}")
        data=await resp.body()
        if len(data)<1024:
            await browser.close()
            raise RuntimeError("audio response unexpectedly small")

        name=Path(urlparse(chosen).path).name or "clip.mp3"
        audio=out_dir/name
        audio.write_bytes(data)
        meta={
            "schema":"astra-independent-realdev-acquisition-probe-result-v1",
            "sourceUrl":source_url,
            "finalPageUrl":page.url,
            "audioUrl":chosen,
            "fileName":name,
            "bytes":len(data),
            "sha256":hashlib.sha256(data).hexdigest(),
            "observedAudioResponses":seen,
            "modelInference":False,
            "optimizerSteps":0,
            "p1Accessed":False,
            "p2Accessed":False,
            "p3Accessed":False,
        }
        (out_dir/"result.json").write_text(json.dumps(meta,indent=2,sort_keys=True)+"\n")
        await browser.close()
        return meta

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-url",required=True)
    ap.add_argument("--out-dir",required=True)
    a=ap.parse_args()
    r=asyncio.run(acquire(a.source_url,Path(a.out_dir)))
    print("ACQUISITION_PROBE="+json.dumps(r,sort_keys=True))

if __name__=="__main__":
    main()

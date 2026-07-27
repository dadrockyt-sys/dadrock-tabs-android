from pathlib import Path

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

text = text.replace(
    "AI is creating your preview...",
    "Tab Studio is analyzing your audio...",
)

if text == original:
    print("Loading text already updated or source text not found.")
else:
    path.write_text(text, encoding="utf-8")
    print("Updated AI tab loading message.")

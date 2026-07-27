from pathlib import Path
import re

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

# Find and remove the existing email delivery field from the song-details section.
email_pattern = re.compile(
    r'''\n            <div className="mt-4">\n'''
    r'''              <label\n'''
    r'''                htmlFor="customer-email".*?'''
    r'''\n            </div>\n'''
    r'''(?=\n            <div className="mt-6">\n'''
    r'''              <div className="mb-3">\n'''
    r'''                <h3[^>]*>\n'''
    r'''                  Choose your transcription)''',
    re.DOTALL,
)

match = email_pattern.search(text)
if match:
    email_block = match.group(0)
    text = text[: match.start()] + "\n" + text[match.end() :]
else:
    # Idempotency: it may already be in the desired location.
    email_block = None

# Insert the email field after the permission checkbox and before the Generate button.
if email_block:
    insertion_anchor = '''              </label>\n\n              <div className="mt-6">\n\n                <button'''
    if insertion_anchor not in text:
        raise RuntimeError("Could not find the checkbox-to-generate insertion point")

    moved_block = email_block.replace(
        '\n            <div className="mt-4">',
        '\n\n              <div className="mt-6">',
        1,
    )
    moved_block = moved_block.replace('\n            </div>\n', '\n              </div>\n', 1)

    replacement = (
        '              </label>'
        + moved_block
        + '\n              <div className="mt-6">\n\n                <button'
    )
    text = text.replace(insertion_anchor, replacement, 1)

if text == original:
    print("Email field is already below the permission checkbox.")
else:
    path.write_text(text, encoding="utf-8")
    print("Moved the PDF delivery email below the permission checkbox and above Generate.")

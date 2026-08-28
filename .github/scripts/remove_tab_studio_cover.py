from pathlib import Path

path = Path('app/admin/tab-studio/page.js')
text = path.read_text()

start_marker = "      const cover = pdfDoc.addPage([612, 792]);\n"
end_marker = "      for (let index = 0; index < pageFiles.length; index += 1) {\n"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1:
    raise SystemExit('Tab Studio cover start marker not found')
if end == -1:
    raise SystemExit('Tab Studio page loop marker not found')

# Remove the dedicated cover page. The first source JPG now becomes PDF page 1
# and uses the existing compact DadRock header with song metadata.
text = text[:start] + text[end:]

# Top-align every original JPG immediately below the metadata divider rather
# than vertically centering short images in the available tab area.
old_image_y = "        const imageY = 48 + (650 - renderHeight) / 2;\n"
new_image_y = "        const imageY = 698 - renderHeight;\n"
if old_image_y not in text:
    raise SystemExit('Tab Studio image alignment marker not found')
text = text.replace(old_image_y, new_image_y, 1)

path.write_text(text)

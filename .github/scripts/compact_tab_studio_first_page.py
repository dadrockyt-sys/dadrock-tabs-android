from pathlib import Path

path = Path('app/admin/tab-studio/page.js')
text = path.read_text()

start_marker = "      for (let index = 0; index < pageFiles.length; index += 1) {\n"
end_marker = "      const bytes = await pdfDoc.save();\n"

start = text.find(start_marker)
end = text.find(end_marker, start)

if start == -1 or end == -1:
    raise SystemExit('Tab Studio PDF page loop markers not found')

new_block = r'''      for (let index = 0; index < pageFiles.length; index += 1) {
        const source = pageFiles[index];
        const sourceBytes = await source.file.arrayBuffer();
        const jpg = await pdfDoc.embedJpg(sourceBytes);
        const page = pdfDoc.addPage([612, 792]);
        const isFirstPage = index === 0;

        if (isFirstPage) {
          // Keep the full DadRock Tab Studio logo on page one, then move
          // straight into the song metadata so the tab gets maximum room.
          if (logoImage) {
            const heroLogo = logoImage.scaleToFit(150, 68);
            page.drawImage(logoImage, {
              x: (612 - heroLogo.width) / 2,
              y: 714,
              width: heroLogo.width,
              height: heroLogo.height,
            });
          } else {
            const fallbackWidth = bold.widthOfTextAtSize('DADROCK TABS STUDIO', 20);
            page.drawText('DADROCK TABS STUDIO', {
              x: (612 - fallbackWidth) / 2,
              y: 744,
              size: 20,
              font: bold,
              color: dark,
            });
          }

          page.drawLine({
            start: { x: 40, y: 704 },
            end: { x: 572, y: 704 },
            thickness: 0.8,
            color: lightLine,
          });

          const firstSongSize = fitTextSize(bold, cleanSong, 532, 20, 13);
          page.drawText(cleanSong, {
            x: 40,
            y: 676,
            size: firstSongSize,
            font: bold,
            color: dark,
          });

          const firstArtistSize = fitTextSize(regular, cleanArtist, 532, 12, 9);
          page.drawText(cleanArtist, {
            x: 40,
            y: 655,
            size: firstArtistSize,
            font: regular,
            color: muted,
          });

          page.drawText(instrumentLabel.toUpperCase(), {
            x: 40,
            y: 633,
            size: 9.5,
            font: bold,
            color: accent,
          });

          page.drawText(`1/${pageFiles.length}`, {
            x: 548,
            y: 633,
            size: 8,
            font: bold,
            color: muted,
          });

          page.drawLine({
            start: { x: 40, y: 619 },
            end: { x: 572, y: 619 },
            thickness: 0.8,
            color: lightLine,
          });
        } else {
          // Compact continuation-page identity and song metadata.
          if (logoImage) {
            const smallLogo = logoImage.scaleToFit(96, 43);
            page.drawImage(logoImage, {
              x: 30,
              y: 733,
              width: smallLogo.width,
              height: smallLogo.height,
            });
          } else {
            page.drawText('DadRock Tabs', {
              x: 30,
              y: 752,
              size: 12,
              font: bold,
              color: dark,
            });
          }

          const headerSongSize = fitTextSize(bold, cleanSong, 300, 12, 8);
          page.drawText(cleanSong, {
            x: 150,
            y: 754,
            size: headerSongSize,
            font: bold,
            color: dark,
          });

          const headerArtistSize = fitTextSize(
            regular,
            `${cleanArtist} • ${instrumentLabel}`,
            300,
            9,
            7
          );
          page.drawText(`${cleanArtist} • ${instrumentLabel}`, {
            x: 150,
            y: 738,
            size: headerArtistSize,
            font: regular,
            color: muted,
          });

          page.drawText(`${index + 1}/${pageFiles.length}`, {
            x: 548,
            y: 748,
            size: 8,
            font: bold,
            color: muted,
          });

          page.drawLine({
            start: { x: 30, y: 719 },
            end: { x: 582, y: 719 },
            thickness: 0.8,
            color: lightLine,
          });
        }

        // Preserve the JPG exactly and only apply one uniform scale factor.
        // Page one now gives the reclaimed branding space directly to the tab.
        const maxWidth = isFirstPage ? 532 : 552;
        const maxHeight = isFirstPage ? 568 : 650;
        const imageTop = isFirstPage ? 606 : 698;
        const scale = Math.min(maxWidth / jpg.width, maxHeight / jpg.height);
        const renderWidth = jpg.width * scale;
        const renderHeight = jpg.height * scale;
        const imageX = (612 - renderWidth) / 2;
        const imageY = imageTop - renderHeight;

        page.drawImage(jpg, {
          x: imageX,
          y: imageY,
          width: renderWidth,
          height: renderHeight,
        });

        page.drawLine({
          start: { x: 30, y: 37 },
          end: { x: 582, y: 37 },
          thickness: 0.6,
          color: lightLine,
        });
        page.drawText('Original JPG embedded directly • uniform scale only • no OCR/AI redraw', {
          x: 139,
          y: 21,
          size: 7,
          font: regular,
          color: muted,
        });
      }

'''

text = text[:start] + new_block + text[end:]
text = text.replace(
    "{generatedPdf.sourcePages} JPG pages + cover • {formatBytes(generatedPdf.bytes)} • stored only as a temporary browser object URL",
    "{generatedPdf.sourcePages} JPG pages • {formatBytes(generatedPdf.bytes)} • stored only as a temporary browser object URL"
)
path.write_text(text)

'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import {
  ArrowDown,
  ArrowLeft,
  ArrowUp,
  CheckCircle2,
  Download,
  FileImage,
  Loader2,
  LockKeyhole,
  ShieldCheck,
  Trash2,
  Upload,
  X,
} from 'lucide-react';
import { PDFDocument, StandardFonts, rgb } from 'pdf-lib';

const LOGO_URL = '/DadRock-Tabs-Logo.png';
const MAX_PAGES = 30;
const MAX_FILE_BYTES = 15 * 1024 * 1024;

const INSTRUMENTS = [
  { value: 'lead', label: 'Lead Guitar' },
  { value: 'rhythm', label: 'Rhythm Guitar' },
  { value: 'bass', label: 'Bass Guitar' },
];

function safeFileName(value) {
  return String(value || '')
    .normalize('NFKD')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .toLowerCase()
    .slice(0, 90);
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes) || bytes <= 0) return '0 KB';
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function imageDimensions(url) {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve({ width: image.naturalWidth, height: image.naturalHeight });
    image.onerror = () => reject(new Error('Unable to read this JPG image.'));
    image.src = url;
  });
}

function fitTextSize(font, text, maximumWidth, preferredSize, minimumSize = 8) {
  let size = preferredSize;
  while (size > minimumSize && font.widthOfTextAtSize(text, size) > maximumWidth) {
    size -= 0.5;
  }
  return size;
}

export default function AdminJpgTabStudioPage() {
  const fileInputRef = useRef(null);
  const pageFilesRef = useRef([]);
  const pdfUrlRef = useRef('');

  const [authStatus, setAuthStatus] = useState('checking');
  const [artist, setArtist] = useState('');
  const [song, setSong] = useState('');
  const [instrument, setInstrument] = useState('lead');
  const [pageFiles, setPageFiles] = useState([]);
  const [isReadingFiles, setIsReadingFiles] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [generatedPdf, setGeneratedPdf] = useState(null);

  const instrumentLabel = useMemo(
    () => INSTRUMENTS.find((item) => item.value === instrument)?.label || 'Lead Guitar',
    [instrument]
  );

  useEffect(() => {
    pageFilesRef.current = pageFiles;
  }, [pageFiles]);

  useEffect(() => {
    const verify = async () => {
      const password = window.sessionStorage.getItem('dadrock_admin_auth') || '';
      if (!password) {
        setAuthStatus('unauthorized');
        return;
      }

      try {
        const response = await fetch('/api/admin/tab-studio-auth', {
          headers: {
            Authorization: `Basic ${window.btoa(`admin:${password}`)}`,
          },
          cache: 'no-store',
        });
        setAuthStatus(response.ok ? 'authorized' : 'unauthorized');
      } catch {
        setAuthStatus('unauthorized');
      }
    };

    verify();
  }, []);

  useEffect(() => {
    return () => {
      pageFilesRef.current.forEach((item) => {
        if (item.previewUrl) window.URL.revokeObjectURL(item.previewUrl);
      });
      if (pdfUrlRef.current) window.URL.revokeObjectURL(pdfUrlRef.current);
    };
  }, []);

  const clearGeneratedPdf = () => {
    if (pdfUrlRef.current) {
      window.URL.revokeObjectURL(pdfUrlRef.current);
      pdfUrlRef.current = '';
    }
    setGeneratedPdf(null);
  };

  const invalidatePdf = () => {
    clearGeneratedPdf();
    setMessage({ type: '', text: '' });
  };

  const handleFiles = async (event) => {
    const selected = Array.from(event.target.files || []);
    if (!selected.length) return;

    clearGeneratedPdf();
    setMessage({ type: '', text: '' });
    setIsReadingFiles(true);

    try {
      const availableSlots = Math.max(0, MAX_PAGES - pageFiles.length);
      const candidates = selected.slice(0, availableSlots);
      const accepted = [];
      const rejected = [];

      for (const file of candidates) {
        const isJpeg = file.type === 'image/jpeg' || /\.jpe?g$/i.test(file.name);
        if (!isJpeg) {
          rejected.push(`${file.name}: JPG/JPEG only`);
          continue;
        }
        if (file.size > MAX_FILE_BYTES) {
          rejected.push(`${file.name}: larger than 15 MB`);
          continue;
        }

        const previewUrl = window.URL.createObjectURL(file);
        try {
          const dimensions = await imageDimensions(previewUrl);
          accepted.push({
            id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
            file,
            previewUrl,
            width: dimensions.width,
            height: dimensions.height,
          });
        } catch (error) {
          window.URL.revokeObjectURL(previewUrl);
          rejected.push(`${file.name}: ${error.message}`);
        }
      }

      setPageFiles((current) => [...current, ...accepted]);

      const notices = [];
      if (accepted.length) notices.push(`${accepted.length} JPG page${accepted.length === 1 ? '' : 's'} added.`);
      if (selected.length > availableSlots) notices.push(`Maximum ${MAX_PAGES} pages.`);
      if (rejected.length) notices.push(rejected.join(' • '));
      setMessage({ type: rejected.length ? 'warning' : 'success', text: notices.join(' ') });
    } finally {
      setIsReadingFiles(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const removePage = (index) => {
    clearGeneratedPdf();
    setPageFiles((current) => {
      const next = [...current];
      const [removed] = next.splice(index, 1);
      if (removed?.previewUrl) window.URL.revokeObjectURL(removed.previewUrl);
      return next;
    });
  };

  const movePage = (index, direction) => {
    clearGeneratedPdf();
    setPageFiles((current) => {
      const target = index + direction;
      if (target < 0 || target >= current.length) return current;
      const next = [...current];
      [next[index], next[target]] = [next[target], next[index]];
      return next;
    });
  };

  const generatePdf = async () => {
    const cleanArtist = artist.trim();
    const cleanSong = song.trim();

    if (!cleanArtist || !cleanSong || !pageFiles.length) {
      setMessage({ type: 'error', text: 'Add the artist, song and at least one JPG tab page.' });
      return;
    }

    setIsGenerating(true);
    setMessage({ type: '', text: '' });
    clearGeneratedPdf();

    try {
      const pdfDoc = await PDFDocument.create();
      const regular = await pdfDoc.embedFont(StandardFonts.Helvetica);
      const bold = await pdfDoc.embedFont(StandardFonts.HelveticaBold);
      const accent = rgb(1, 0.27, 0);
      const dark = rgb(0.06, 0.06, 0.07);
      const muted = rgb(0.39, 0.39, 0.42);
      const lightLine = rgb(0.84, 0.84, 0.86);

      pdfDoc.setTitle(`${cleanSong} - ${instrumentLabel} Tab`);
      pdfDoc.setAuthor('DadRock Tab Studio');
      pdfDoc.setSubject(`${instrumentLabel} tablature assembled from original JPG pages`);
      pdfDoc.setCreator('DadRock Tab Studio - dadrocktabs.com');
      pdfDoc.setProducer('DadRock Tab Studio');

      let logoImage = null;
      try {
        const logoResponse = await fetch(LOGO_URL, { cache: 'force-cache' });
        if (logoResponse.ok) {
          logoImage = await pdfDoc.embedPng(await logoResponse.arrayBuffer());
        }
      } catch {
        logoImage = null;
      }

      for (let index = 0; index < pageFiles.length; index += 1) {
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
      }

      const bytes = await pdfDoc.save();
      const blob = new Blob([bytes], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      pdfUrlRef.current = url;

      const fileName = `${safeFileName(cleanArtist) || 'artist'}-${safeFileName(cleanSong) || 'song'}-${instrument}-tab.pdf`;
      setGeneratedPdf({
        url,
        fileName,
        bytes: blob.size,
        sourcePages: pageFiles.length,
      });
      setMessage({
        type: 'success',
        text: 'PDF ready. Every tab page uses the original JPG directly with proportional scaling only.',
      });
    } catch (error) {
      console.error('Personal JPG Tab Studio PDF error:', error);
      setMessage({
        type: 'error',
        text: error instanceof Error ? error.message : 'Unable to generate the PDF.',
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadPdf = () => {
    if (!generatedPdf?.url) return;
    const link = document.createElement('a');
    link.href = generatedPdf.url;
    link.download = generatedPdf.fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const deleteNow = () => {
    if (!window.confirm('Delete the generated PDF and clear all selected JPG pages now?')) return;

    clearGeneratedPdf();
    pageFiles.forEach((item) => {
      if (item.previewUrl) window.URL.revokeObjectURL(item.previewUrl);
    });
    setPageFiles([]);
    setArtist('');
    setSong('');
    setInstrument('lead');
    setMessage({ type: 'success', text: 'Deleted. The PDF URL and all selected JPG references were cleared from this browser session.' });
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  if (authStatus === 'checking') {
    return (
      <main className="min-h-screen bg-zinc-950 text-white flex items-center justify-center px-4">
        <div className="flex items-center gap-3 text-zinc-300">
          <Loader2 className="h-5 w-5 animate-spin text-orange-500" />
          Verifying admin access...
        </div>
      </main>
    );
  }

  if (authStatus !== 'authorized') {
    return (
      <main className="min-h-screen bg-zinc-950 text-white px-4 py-16">
        <div className="mx-auto max-w-lg rounded-2xl border border-red-500/30 bg-zinc-900 p-6 text-center">
          <LockKeyhole className="mx-auto mb-4 h-10 w-10 text-red-400" />
          <h1 className="text-2xl font-black">Admin access required</h1>
          <p className="mt-3 text-zinc-400">Open this tool from the authenticated DadRock admin panel. Your existing admin login is required.</p>
          <a href="/" className="mt-6 inline-flex items-center gap-2 rounded-lg bg-zinc-800 px-4 py-3 font-bold hover:bg-zinc-700">
            <ArrowLeft className="h-4 w-4" /> Back to DadRock Tabs
          </a>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-zinc-950 text-white px-4 py-6 sm:px-6 sm:py-10">
      <div className="mx-auto max-w-5xl">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <a href="/" className="inline-flex items-center gap-2 text-sm font-bold text-zinc-400 hover:text-white">
            <ArrowLeft className="h-4 w-4" /> DadRock Admin
          </a>
          <div className="inline-flex items-center gap-2 rounded-full border border-green-500/30 bg-green-500/10 px-3 py-1.5 text-xs font-bold text-green-300">
            <ShieldCheck className="h-4 w-4" /> Private admin tool
          </div>
        </div>

        <section className="rounded-2xl border border-zinc-800 bg-zinc-900 p-5 sm:p-7">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <p className="text-xs font-black uppercase tracking-[0.22em] text-orange-500">DadRock Tab Studio</p>
              <h1 className="mt-2 text-3xl font-black sm:text-4xl">JPG → Professional PDF</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base">
                Personal exact-image mode. Your JPGs stay on this device and are embedded directly into the PDF. Nothing is OCR'd, redrawn, reflowed or uploaded.
              </p>
            </div>
            <div className="rounded-xl border border-orange-500/20 bg-orange-500/5 px-4 py-3 text-sm text-zinc-300">
              <div className="flex items-center gap-2 font-bold text-orange-300"><CheckCircle2 className="h-4 w-4" /> Measure-for-measure protection</div>
              <p className="mt-1 text-xs text-zinc-500">Uniform proportional scaling only.</p>
            </div>
          </div>

          <div className="mt-7 grid gap-4 md:grid-cols-3">
            <label className="text-sm font-bold text-zinc-300">
              Artist
              <input
                value={artist}
                onChange={(event) => { setArtist(event.target.value); invalidatePdf(); }}
                placeholder="e.g. AC/DC"
                maxLength={120}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-base text-white outline-none focus:border-orange-500"
              />
            </label>
            <label className="text-sm font-bold text-zinc-300">
              Song
              <input
                value={song}
                onChange={(event) => { setSong(event.target.value); invalidatePdf(); }}
                placeholder="e.g. Back In Black"
                maxLength={120}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-base text-white outline-none focus:border-orange-500"
              />
            </label>
            <label className="text-sm font-bold text-zinc-300">
              Part
              <select
                value={instrument}
                onChange={(event) => { setInstrument(event.target.value); invalidatePdf(); }}
                className="mt-2 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-base text-white outline-none focus:border-orange-500"
              >
                {INSTRUMENTS.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
              </select>
            </label>
          </div>

          <div className="mt-7 rounded-2xl border border-dashed border-zinc-700 bg-zinc-950/70 p-5 text-center sm:p-8">
            <FileImage className="mx-auto h-10 w-10 text-orange-500" />
            <h2 className="mt-3 text-lg font-black">Upload JPG tab pages</h2>
            <p className="mt-2 text-sm text-zinc-500">JPG/JPEG only • up to {MAX_PAGES} pages • 15 MB per page</p>
            <input ref={fileInputRef} type="file" accept="image/jpeg,.jpg,.jpeg" multiple onChange={handleFiles} className="hidden" />
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              disabled={isReadingFiles || pageFiles.length >= MAX_PAGES}
              className="mt-5 inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-orange-600 px-5 py-3 font-black text-white hover:bg-orange-500 disabled:opacity-50"
            >
              {isReadingFiles ? <Loader2 className="h-5 w-5 animate-spin" /> : <Upload className="h-5 w-5" />}
              {isReadingFiles ? 'Reading JPGs...' : 'Add JPG Pages'}
            </button>
          </div>

          {pageFiles.length > 0 && (
            <div className="mt-7">
              <div className="mb-3 flex flex-wrap items-end justify-between gap-2">
                <div>
                  <h2 className="text-lg font-black">Page order</h2>
                  <p className="text-sm text-zinc-500">Use the arrows to put the measures/pages in the exact order you want.</p>
                </div>
                <span className="text-sm font-bold text-zinc-400">{pageFiles.length} page{pageFiles.length === 1 ? '' : 's'}</span>
              </div>

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {pageFiles.map((item, index) => (
                  <article key={item.id} className="overflow-hidden rounded-xl border border-zinc-800 bg-zinc-950">
                    <div className="flex h-52 items-center justify-center bg-white p-2">
                      <img src={item.previewUrl} alt={`Tab source page ${index + 1}`} className="max-h-full max-w-full object-contain" />
                    </div>
                    <div className="p-3">
                      <div className="flex items-start justify-between gap-2">
                        <div className="min-w-0">
                          <p className="font-black text-white">Page {index + 1}</p>
                          <p className="truncate text-xs text-zinc-500" title={item.file.name}>{item.file.name}</p>
                          <p className="mt-1 text-xs text-zinc-600">{item.width}×{item.height} • {formatBytes(item.file.size)}</p>
                        </div>
                        <button type="button" onClick={() => removePage(index)} className="rounded-lg p-2 text-red-400 hover:bg-red-500/10" title="Remove page">
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                      <div className="mt-3 grid grid-cols-2 gap-2">
                        <button type="button" onClick={() => movePage(index, -1)} disabled={index === 0} className="inline-flex min-h-10 items-center justify-center gap-1 rounded-lg bg-zinc-800 text-sm font-bold text-zinc-300 hover:bg-zinc-700 disabled:opacity-30">
                          <ArrowUp className="h-4 w-4" /> Earlier
                        </button>
                        <button type="button" onClick={() => movePage(index, 1)} disabled={index === pageFiles.length - 1} className="inline-flex min-h-10 items-center justify-center gap-1 rounded-lg bg-zinc-800 text-sm font-bold text-zinc-300 hover:bg-zinc-700 disabled:opacity-30">
                          <ArrowDown className="h-4 w-4" /> Later
                        </button>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            </div>
          )}

          {message.text && (
            <div className={`mt-6 rounded-xl border px-4 py-3 text-sm ${message.type === 'error' ? 'border-red-500/30 bg-red-500/10 text-red-300' : message.type === 'warning' ? 'border-amber-500/30 bg-amber-500/10 text-amber-300' : 'border-green-500/30 bg-green-500/10 text-green-300'}`}>
              {message.text}
            </div>
          )}

          <div className="mt-7 flex flex-col gap-3 sm:flex-row">
            <button
              type="button"
              onClick={generatePdf}
              disabled={isGenerating || !artist.trim() || !song.trim() || pageFiles.length === 0}
              className="inline-flex min-h-12 flex-1 items-center justify-center gap-2 rounded-xl bg-orange-600 px-5 py-3 font-black text-white hover:bg-orange-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {isGenerating ? <Loader2 className="h-5 w-5 animate-spin" /> : <FileImage className="h-5 w-5" />}
              {isGenerating ? 'Building exact-image PDF...' : 'Generate Professional PDF'}
            </button>
          </div>
        </section>

        {generatedPdf && (
          <section className="mt-6 rounded-2xl border border-green-500/30 bg-zinc-900 p-5 sm:p-7">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="mt-0.5 h-7 w-7 shrink-0 text-green-400" />
              <div>
                <h2 className="text-xl font-black text-white">PDF ready</h2>
                <p className="mt-1 break-all text-sm text-zinc-400">{generatedPdf.fileName}</p>
                <p className="mt-2 text-xs text-zinc-500">{generatedPdf.sourcePages} JPG pages • {formatBytes(generatedPdf.bytes)} • stored only as a temporary browser object URL</p>
              </div>
            </div>

            <div className="mt-5 grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg bg-zinc-950 px-3 py-2 text-sm text-zinc-300">✓ Original JPG embedded directly</div>
              <div className="rounded-lg bg-zinc-950 px-3 py-2 text-sm text-zinc-300">✓ Aspect ratio preserved</div>
              <div className="rounded-lg bg-zinc-950 px-3 py-2 text-sm text-zinc-300">✓ No OCR reconstruction</div>
              <div className="rounded-lg bg-zinc-950 px-3 py-2 text-sm text-zinc-300">✓ No AI tab redraw</div>
            </div>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
              <button type="button" onClick={downloadPdf} className="inline-flex min-h-12 flex-1 items-center justify-center gap-2 rounded-xl bg-green-600 px-5 py-3 font-black text-white hover:bg-green-500">
                <Download className="h-5 w-5" /> Download PDF
              </button>
              <button type="button" onClick={deleteNow} className="inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-red-500/40 bg-red-500/10 px-5 py-3 font-black text-red-300 hover:bg-red-500/20">
                <Trash2 className="h-5 w-5" /> Delete Now
              </button>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

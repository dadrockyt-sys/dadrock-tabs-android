'use client';

import { Suspense, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  ArrowLeft,
  Check,
  CreditCard,
  FileAudio,
  FileText,
  Guitar,
  Music,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Youtube,
} from 'lucide-react';

import LanguageSelector, {
  useLanguage,
} from '@/components/LanguageSelector';

import PayPalCheckoutButton from '@/components/PayPalCheckoutButton';

import {
  getAiTabTranslation,
} from '@/lib/aiTabTranslations';

function getLocalizedPath(path, lang) {
  if (!lang || lang === 'en') return path;

  return `/${lang}${path}`;
}

const LOGO_URL = '/DadRock-Tabs-Logo.png';

const YOUTUBE_URL =
  'https://youtube.com/@dadrockytofficial?si=TjBWK-QMUu7vdcrI';

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();

  const [selectedLang] = useLanguage();
  const currentLang = selectedLang || 'en';
  const t = getAiTabTranslation(currentLang);

  const initialSong =
    searchParams.get('song') || '';

  const initialArtist =
    searchParams.get('artist') || '';

  const [youtubeUrl, setYoutubeUrl] =
    useState('');

  const [audioFile, setAudioFile] =
    useState(null);

  const [songTitle, setSongTitle] =
    useState(initialSong);

  const [artistName, setArtistName] =
    useState(initialArtist);

  const [selectedType, setSelectedType] =
    useState('');

  const [responsibilityAccepted, setResponsibilityAccepted] =
    useState(false);

  const [customerEmail, setCustomerEmail] =
    useState('');

  const [isGenerating, setIsGenerating] =
    useState(false);

  const [previewReady, setPreviewReady] =
    useState(false);

  const [paymentCompleted, setPaymentCompleted] =
    useState(false);

  const [purchaseOrderId, setPurchaseOrderId] =
    useState('');

  const [isDownloading, setIsDownloading] =
    useState(false);

  const [generatedTab, setGeneratedTab] =
    useState('');

  const [generationError, setGenerationError] =
    useState('');

  const [statusMessage, setStatusMessage] =
    useState('');

  function handleFileChange(event) {
    const file = event.target.files?.[0];

    if (!file) return;

    setAudioFile(file);
    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setGeneratedTab('');
  }

  function removeAudioFile() {
    setAudioFile(null);
    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setGeneratedTab('');
  }

  function handleDrop(event) {
    event.preventDefault();

    const file = event.dataTransfer.files?.[0];

    if (!file) return;

    setAudioFile(file);
    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setGeneratedTab('');
  }

  function handleDragOver(event) {
    event.preventDefault();
  }

  const formIsComplete =
    Boolean(audioFile) &&
    Boolean(songTitle.trim()) &&
    Boolean(artistName.trim()) &&
    Boolean(selectedType) &&
    responsibilityAccepted;

  const emailIsValid =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      customerEmail.trim()
    );
    const handleGeneratePreview = async () => {
    if (!formIsComplete || isGenerating) {
      setStatusMessage(t.selectRequirements);
      return;
    }

    setIsGenerating(true);
    setPreviewReady(false);
    setGeneratedTab('');
    setGenerationError('');
    setStatusMessage('');
    setPaymentCompleted(false);
    setPurchaseOrderId('');

    try {
      const response = await fetch(
        '/api/generate-tab',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            song: songTitle.trim(),
            artist: artistName.trim(),
            transcriptionType: selectedType,
            youtubeUrl: youtubeUrl.trim(),
            audioFileName: audioFile?.name || '',
            audioFileType: audioFile?.type || '',
            audioFileSize: audioFile?.size || 0,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            'The tab could not be generated.'
        );
      }

      setGeneratedTab(data.tab);
      setPreviewReady(true);
    } catch (error) {
      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Something went wrong while generating the tab.'
      );
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownloadPdf = async () => {
    if (!purchaseOrderId || isDownloading) {
      return;
    }

    setIsDownloading(true);
    setGenerationError('');

    try {
      const response = await fetch(
        '/api/generate-tab-pdf',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            orderId: purchaseOrderId,
            song: songTitle.trim(),
            artist: artistName.trim(),
            transcriptionType: selectedType,
            generatedTab,
            customerEmail: customerEmail.trim(),
          }),
        }
      );

      if (!response.ok) {
        const data = await response.json();

        throw new Error(
          data.error ||
            'The PDF could not be generated.'
        );
      }

      const pdfBlob = await response.blob();

      const downloadUrl =
        window.URL.createObjectURL(pdfBlob);

      const disposition =
        response.headers.get(
          'Content-Disposition'
        );

      const fileNameMatch =
        disposition?.match(
          /filename="([^"]+)"/i
        );

      const fileName =
        fileNameMatch?.[1] ||
        'dadrock-ai-tab.pdf';

      const downloadLink =
        document.createElement('a');

      downloadLink.href = downloadUrl;
      downloadLink.download = fileName;

      document.body.appendChild(downloadLink);
      downloadLink.click();
      downloadLink.remove();

      window.URL.revokeObjectURL(
        downloadUrl
      );
    } catch (error) {
      setGenerationError(
        error instanceof Error
          ? error.message
          : 'The PDF could not be downloaded.'
      );
    } finally {
      setIsDownloading(false);
    }
  };
    return (
    <main className="min-h-screen bg-gradient-to-b from-black via-zinc-950 to-zinc-900 text-white">
      <header className="border-b border-zinc-800 bg-black/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
          <Link
            href={getLocalizedPath('/', currentLang)}
            className="flex min-w-0 items-center gap-3"
          >
            <Image
              src={LOGO_URL}
              alt="DadRock Tabs"
              width={220}
              height={80}
              className="h-12 w-auto object-contain sm:h-14"
              priority
            />
          </Link>

          <div className="flex items-center gap-3">
            <nav className="hidden items-center gap-5 text-sm font-semibold text-zinc-300 lg:flex">
              <Link
                href={getLocalizedPath('/', currentLang)}
                className="transition hover:text-amber-400"
              >
                {t.home}
              </Link>

              <Link
                href={getLocalizedPath('/artists', currentLang)}
                className="transition hover:text-amber-400"
              >
                {t.artists}
              </Link>

              <Link
                href={getLocalizedPath('/songs', currentLang)}
                className="transition hover:text-amber-400"
              >
                {t.songs}
              </Link>

              <Link
                href={getLocalizedPath('/top-lessons', currentLang)}
                className="transition hover:text-amber-400"
              >
                {t.lessons}
              </Link>

              <Link
                href={getLocalizedPath('/partners', currentLang)}
                className="transition hover:text-amber-400"
              >
                {t.partners}
              </Link>
            </nav>

            <LanguageSelector />
          </div>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-4 py-8 sm:py-12">
        <Link
          href={getLocalizedPath('/', currentLang)}
          className="mb-8 inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 transition hover:text-amber-400"
        >
          <ArrowLeft className="h-5 w-5" />
          {t.backToHome}
        </Link>

        <section className="overflow-hidden rounded-3xl border border-amber-500/30 bg-zinc-900/80 shadow-2xl shadow-orange-500/10">
          <div className="bg-gradient-to-br from-amber-500 via-orange-600 to-red-700 px-6 py-10 sm:px-10 sm:py-14">
            <div className="mx-auto max-w-4xl text-center">
              <p className="text-sm font-bold uppercase tracking-[0.3em] text-white/80">
                {t.eyebrow}
              </p>

              <div className="mt-5 flex justify-center">
                <div className="rounded-2xl border border-white/20 bg-black/20 p-4">
                  <Guitar className="h-12 w-12 text-white sm:h-14 sm:w-14" />
                </div>
              </div>

              <h1 className="mt-6 text-4xl font-black leading-tight sm:text-5xl lg:text-6xl">
                {t.title}
              </h1>

              <p className="mx-auto mt-5 max-w-3xl text-base leading-relaxed text-white/90 sm:text-lg">
                {t.subtitle}
              </p>
            </div>
          </div>

          <div className="grid gap-8 p-6 sm:p-10 lg:grid-cols-[1.15fr_0.85fr]">
            <form
              onSubmit={(event) => {
                event.preventDefault();
                handleGeneratePreview();
              }}
              className="space-y-8"
            >
              <section className="rounded-2xl border border-zinc-700 bg-black/30 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <Youtube className="mt-1 h-6 w-6 shrink-0 text-red-500" />

                  <div className="min-w-0 flex-1">
                    <h2 className="text-xl font-bold">
                      {t.youtubeTitle}
                    </h2>

                    <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                      {t.youtubeDescription}
                    </p>

                    <input
                      type="url"
                      value={youtubeUrl}
                      onChange={(event) =>
                        setYoutubeUrl(event.target.value)
                      }
                      placeholder={t.youtubePlaceholder}
                      className="mt-4 w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-red-500 focus:ring-2 focus:ring-red-500/20"
                    />
                  </div>
                </div>
              </section>

              <section className="rounded-2xl border border-zinc-700 bg-black/30 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <Upload className="mt-1 h-6 w-6 shrink-0 text-amber-400" />

                  <div className="min-w-0 flex-1">
                    <h2 className="text-xl font-bold">
                      {t.uploadTitle}
                    </h2>

                    <p className="mt-2 text-sm leading-relaxed text-zinc-400">
                      {t.uploadDescription}
                    </p>
                  </div>
                </div>

                {!audioFile ? (
                  <label
                    onDrop={handleDrop}
                    onDragOver={handleDragOver}
                    className="mt-5 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-zinc-700 bg-zinc-950/70 px-5 py-10 text-center transition hover:border-amber-500 hover:bg-amber-500/5"
                  >
                    <FileAudio className="h-12 w-12 text-amber-400" />

                    <span className="mt-4 rounded-full bg-gradient-to-r from-amber-500 to-orange-600 px-6 py-3 font-bold text-white">
                      {t.browseFiles}
                    </span>

                    <span className="mt-4 text-sm text-zinc-400">
                      {t.dropAudio}
                    </span>

                    <span className="mt-2 text-xs text-zinc-500">
                      {t.supportedFormats}
                    </span>

                    <input
                      type="file"
                      accept=".mp3,.wav,.m4a,audio/mpeg,audio/wav,audio/x-m4a,audio/mp4"
                      onChange={handleFileChange}
                      className="hidden"
                    />
                  </label>
                ) : (
                  <div className="mt-5 flex items-center gap-4 rounded-2xl border border-green-500/30 bg-green-500/10 p-4">
                    <div className="rounded-xl bg-green-500/15 p-3">
                      <FileAudio className="h-7 w-7 text-green-400" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="text-xs font-bold uppercase tracking-wider text-green-400">
                        {t.selectedFile}
                      </p>

                      <p className="mt-1 truncate font-semibold text-white">
                        {audioFile.name}
                      </p>

                      <p className="mt-1 text-xs text-zinc-400">
                        {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={removeAudioFile}
                      className="rounded-full border border-zinc-600 p-2 text-zinc-400 transition hover:border-red-500 hover:text-red-400"
                      aria-label={t.removeFile}
                      title={t.removeFile}
                    >
                      <X className="h-5 w-5" />
                    </button>
                  </div>
                )}
              </section>
              <section className="rounded-2xl border border-zinc-700 bg-black/30 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <Music className="mt-1 h-6 w-6 shrink-0 text-amber-400" />

                  <div className="min-w-0 flex-1">
                    <h2 className="text-xl font-bold">
                      {t.detailsTitle}
                    </h2>
                  </div>
                </div>

                <div className="mt-5 grid gap-5 sm:grid-cols-2">
                  <div>
                    <label
                      htmlFor="song-title"
                      className="mb-2 block text-sm font-bold text-zinc-200"
                    >
                      {t.songLabel}
                    </label>

                    <input
                      id="song-title"
                      type="text"
                      value={songTitle}
                      onChange={(event) =>
                        setSongTitle(event.target.value)
                      }
                      placeholder={t.songPlaceholder}
                      className="w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20"
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="artist-name"
                      className="mb-2 block text-sm font-bold text-zinc-200"
                    >
                      {t.artistLabel}
                    </label>

                    <input
                      id="artist-name"
                      type="text"
                      value={artistName}
                      onChange={(event) =>
                        setArtistName(event.target.value)
                      }
                      placeholder={t.artistPlaceholder}
                      className="w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20"
                    />
                  </div>
                </div>
              </section>

              <section className="rounded-2xl border border-zinc-700 bg-black/30 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <Guitar className="mt-1 h-6 w-6 shrink-0 text-amber-400" />

                  <div className="min-w-0 flex-1">
                    <h2 className="text-xl font-bold">
                      {t.instrumentTitle}
                    </h2>
                  </div>
                </div>

                <div className="mt-5 space-y-3">
                  <button
                    type="button"
                    onClick={() =>
                      setSelectedType('lead')
                    }
                    className={`w-full rounded-2xl border p-4 text-left transition-all ${
                      selectedType === 'lead'
                        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/10'
                        : 'border-zinc-700 bg-zinc-950/70 hover:border-amber-500 hover:bg-amber-500/5'
                    }`}
                  >
                    <span className="flex items-center justify-between gap-4">
                      <span className="min-w-0">
                        <span className="block font-bold text-white">
                          {t.leadTitle}
                        </span>

                        <span className="mt-1 block text-sm leading-relaxed text-zinc-400">
                          {t.leadDescription}
                        </span>
                      </span>

                      {selectedType === 'lead' && (
                        <span className="shrink-0 rounded-full bg-amber-400 p-1 text-black">
                          <Check className="h-4 w-4" />
                        </span>
                      )}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setSelectedType('rhythm')
                    }
                    className={`w-full rounded-2xl border p-4 text-left transition-all ${
                      selectedType === 'rhythm'
                        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/10'
                        : 'border-zinc-700 bg-zinc-950/70 hover:border-amber-500 hover:bg-amber-500/5'
                    }`}
                  >
                    <span className="flex items-center justify-between gap-4">
                      <span className="min-w-0">
                        <span className="block font-bold text-white">
                          {t.rhythmTitle}
                        </span>

                        <span className="mt-1 block text-sm leading-relaxed text-zinc-400">
                          {t.rhythmDescription}
                        </span>
                      </span>

                      {selectedType === 'rhythm' && (
                        <span className="shrink-0 rounded-full bg-amber-400 p-1 text-black">
                          <Check className="h-4 w-4" />
                        </span>
                      )}
                    </span>
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      setSelectedType('bass')
                    }
                    className={`w-full rounded-2xl border p-4 text-left transition-all ${
                      selectedType === 'bass'
                        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/10'
                        : 'border-zinc-700 bg-zinc-950/70 hover:border-amber-500 hover:bg-amber-500/5'
                    }`}
                  >
                    <span className="flex items-center justify-between gap-4">
                      <span className="min-w-0">
                        <span className="block font-bold text-white">
                          {t.bassTitle}
                        </span>

                        <span className="mt-1 block text-sm leading-relaxed text-zinc-400">
                          {t.bassDescription}
                        </span>
                      </span>

                      {selectedType === 'bass' && (
                        <span className="shrink-0 rounded-full bg-amber-400 p-1 text-black">
                          <Check className="h-4 w-4" />
                        </span>
                      )}
                    </span>
                  </button>
                </div>
              </section>
              <section className="rounded-2xl border border-zinc-700 bg-black/30 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <ShieldCheck className="mt-1 h-6 w-6 shrink-0 text-green-400" />

                  <div className="min-w-0 flex-1">
                    <h2 className="text-xl font-bold">
                      {t.responsibilityTitle}
                    </h2>

                    <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-zinc-700 bg-zinc-950/70 p-4">
                      <input
                        type="checkbox"
                        checked={responsibilityAccepted}
                        onChange={(event) =>
                          setResponsibilityAccepted(
                            event.target.checked
                          )
                        }
                        className="mt-1 h-5 w-5 shrink-0 accent-amber-500"
                      />

                      <span className="text-sm leading-relaxed text-zinc-300">
                        {t.responsibilityText}
                      </span>
                    </label>
                  </div>
                </div>
              </section>

              <button
                type="submit"
                disabled={!formIsComplete || isGenerating}
                className={`flex w-full items-center justify-center gap-3 rounded-2xl px-6 py-4 text-base font-black transition-all sm:text-lg ${
                  formIsComplete && !isGenerating
                    ? 'bg-gradient-to-r from-amber-500 via-orange-600 to-red-600 text-white shadow-lg shadow-orange-500/20 hover:scale-[1.01]'
                    : 'cursor-not-allowed bg-zinc-800 text-zinc-500'
                }`}
              >
                <Sparkles
                  className={`h-6 w-6 ${
                    isGenerating ? 'animate-pulse' : ''
                  }`}
                />

                {isGenerating
                  ? 'AI is creating your preview...'
                  : t.analyzeButton}
              </button>

              {!formIsComplete && (
                <p className="text-center text-sm leading-relaxed text-zinc-500">
                  {t.selectRequirements}
                </p>
              )}

              {statusMessage && (
                <p className="rounded-xl border border-amber-500/30 bg-amber-500/10 p-4 text-sm leading-relaxed text-amber-200">
                  {statusMessage}
                </p>
              )}

              {generationError && (
                <p className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm leading-relaxed text-red-300">
                  {generationError}
                </p>
              )}
            </form>
            <aside className="space-y-6">
              <section className="rounded-2xl border border-amber-500/30 bg-gradient-to-br from-amber-500/10 to-orange-700/5 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <Sparkles className="mt-1 h-6 w-6 shrink-0 text-amber-400" />

                  <div>
                    <h2 className="text-xl font-bold text-amber-300">
                      {t.processingTitle}
                    </h2>

                    <div className="mt-5 space-y-4">
                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 font-black text-black">
                          1
                        </span>

                        <p className="text-sm text-zinc-300">
                          {t.processingUpload}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 font-black text-black">
                          2
                        </span>

                        <p className="text-sm text-zinc-300">
                          {t.processingSeparate}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 font-black text-black">
                          3
                        </span>

                        <p className="text-sm text-zinc-300">
                          {t.processingDetect}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 font-black text-black">
                          4
                        </span>

                        <p className="text-sm text-zinc-300">
                          {t.processingCreate}
                        </p>
                      </div>

                      <div className="flex items-center gap-3">
                        <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-amber-500 font-black text-black">
                          5
                        </span>

                        <p className="text-sm text-zinc-300">
                          {t.processingPreview}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </section>

              <section className="rounded-2xl border border-green-500/30 bg-green-500/10 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <ShieldCheck className="mt-1 h-6 w-6 shrink-0 text-green-400" />

                  <div>
                    <h2 className="text-xl font-bold text-green-300">
                      {t.privacyTitle}
                    </h2>

                    <p className="mt-3 text-sm leading-relaxed text-zinc-300">
                      {t.privacyText}
                    </p>
                  </div>
                </div>
              </section>

              <section className="rounded-2xl border border-blue-500/30 bg-blue-500/10 p-5 sm:p-6">
                <div className="flex items-start gap-3">
                  <CreditCard className="mt-1 h-6 w-6 shrink-0 text-blue-400" />

                  <div>
                    <h2 className="text-xl font-bold text-blue-300">
                      {t.paymentTitle}
                    </h2>

                    <p className="mt-3 text-sm leading-relaxed text-zinc-300">
                      {t.paymentText}
                    </p>
                  </div>
                </div>
              </section>
            </aside>
          </div>
        </section>
        {previewReady && (
          <section className="mt-10 rounded-3xl border border-amber-500/30 bg-zinc-900/80 p-6 shadow-2xl shadow-orange-500/10 sm:p-10">
            <div className="flex items-center gap-3">
              <FileText className="h-7 w-7 text-amber-400" />

              <div>
                <h2 className="text-3xl font-black">
                  {t.previewTitle}
                </h2>

                <p className="mt-2 text-zinc-400">
                  {t.previewDescription}
                </p>
              </div>
            </div>

            <div className="mt-8 rounded-2xl border border-zinc-700 bg-black p-6">
              <pre className="overflow-x-auto whitespace-pre-wrap font-mono text-sm leading-6 text-green-400">
{generatedTab}
              </pre>
            </div>

            {!paymentCompleted ? (
              <div className="mt-10 rounded-2xl border border-blue-500/30 bg-blue-500/10 p-6">
                <h3 className="text-2xl font-bold">
                  {t.unlockTitle}
                </h3>

                <p className="mt-3 text-zinc-300">
                  {t.unlockDescription}
                </p>

                <div className="mt-6">
                  <label className="mb-2 block font-semibold">
                    {t.emailLabel}
                  </label>

                  <input
                    type="email"
                    value={customerEmail}
                    onChange={(event) =>
                      setCustomerEmail(event.target.value)
                    }
                    placeholder={t.emailPlaceholder}
                    className="w-full rounded-xl border border-zinc-700 bg-zinc-950 px-4 py-3 outline-none transition focus:border-blue-500"
                  />
                </div>

                {emailIsValid && (
                  <div className="mt-8">
                    <PayPalCheckoutButton
                      amount="9.99"
                      currency="CAD"
                      description={`${songTitle} - ${selectedType}`}
                      customerEmail={customerEmail}
                      onSuccess={(details) => {
                        setPaymentCompleted(true);

                        setPurchaseOrderId(
                          details?.id || ''
                        );
                      }}
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="mt-10 rounded-2xl border border-green-500/30 bg-green-500/10 p-6">
                <div className="flex items-center gap-3">
                  <Check className="h-8 w-8 text-green-400" />

                  <div>
                    <h3 className="text-2xl font-bold text-green-300">
                      {t.paymentSuccess}
                    </h3>

                    <p className="mt-2 text-zinc-300">
                      {t.downloadReady}
                    </p>
                  </div>
                </div>

                <div className="mt-8 flex flex-col gap-4 sm:flex-row">
                  <button
                    onClick={handleDownloadPdf}
                    disabled={isDownloading}
                    className="flex flex-1 items-center justify-center gap-3 rounded-xl bg-gradient-to-r from-green-500 to-emerald-600 px-6 py-4 font-bold transition hover:scale-[1.02]"
                  >
                    <Download className="h-5 w-5" />

                    {isDownloading
                      ? t.preparingPdf
                      : t.downloadPdf}
                  </button>

                  <button
                    onClick={() => window.print()}
                    className="flex flex-1 items-center justify-center gap-3 rounded-xl border border-zinc-600 bg-zinc-900 px-6 py-4 font-bold transition hover:border-amber-500"
                  >
                    <Printer className="h-5 w-5" />

                    {t.printTab}
                  </button>
                </div>
              </div>
            )}
          </section>
        )}
        <section className="mt-10 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6 sm:p-10">
          <div className="mx-auto max-w-3xl text-center">
            <h2 className="text-3xl font-black sm:text-4xl">
              {t.faqTitle}
            </h2>

            <p className="mt-3 leading-relaxed text-zinc-400">
              {t.faqSubtitle ||
                'Answers to common questions about the DadRock AI Tab Generator.'}
            </p>
          </div>

          <div className="mx-auto mt-8 max-w-4xl space-y-4">
            {[
              {
                question:
                  t.faq1Question ||
                  t.faqQuestion1 ||
                  'How accurate will my AI-generated tab be?',
                answer:
                  t.faq1Answer ||
                  t.faqAnswer1 ||
                  'The AI analyzes the uploaded audio and creates a detailed starting point. Complex solos, layered instruments, unusual tunings, and low-quality recordings may require some manual adjustments.',
              },
              {
                question:
                  t.faq2Question ||
                  t.faqQuestion2 ||
                  'What audio files can I upload?',
                answer:
                  t.faq2Answer ||
                  t.faqAnswer2 ||
                  'You can upload common audio formats including MP3, WAV, and M4A. A clear recording with the selected instrument easy to hear will usually produce the best result.',
              },
              {
                question:
                  t.faq3Question ||
                  t.faqQuestion3 ||
                  'Can I generate guitar and bass tabs?',
                answer:
                  t.faq3Answer ||
                  t.faqAnswer3 ||
                  'Yes. You can choose lead guitar, rhythm guitar, or bass before starting the analysis.',
              },
              {
                question:
                  t.faq4Question ||
                  t.faqQuestion4 ||
                  'What happens to my uploaded audio?',
                answer:
                  t.faq4Answer ||
                  t.faqAnswer4 ||
                  'Your audio is used only to process your transcription request. It is not added to the DadRock lesson library or offered publicly.',
              },
              {
                question:
                  t.faq5Question ||
                  t.faqQuestion5 ||
                  'What do I receive after payment?',
                answer:
                  t.faq5Answer ||
                  t.faqAnswer5 ||
                  'After successful payment, you can download a portrait-format PDF containing your generated tablature and print it for personal practice.',
              },
            ].map((item, index) => (
              <details
                key={index}
                className="group rounded-2xl border border-zinc-700 bg-black/30 p-5 open:border-amber-500/40 open:bg-amber-500/5"
              >
                <summary className="flex cursor-pointer list-none items-center justify-between gap-4 font-bold text-white">
                  <span>{item.question}</span>

                  <span className="text-2xl text-amber-400 transition-transform group-open:rotate-45">
                    +
                  </span>
                </summary>

                <p className="mt-4 border-t border-zinc-700 pt-4 text-sm leading-relaxed text-zinc-400">
                  {item.answer}
                </p>
              </details>
            ))}
          </div>
        </section>

        <footer className="mt-12 border-t border-zinc-800 py-8">
          <div className="flex flex-col items-center justify-between gap-5 text-center sm:flex-row sm:text-left">
            <div>
              <p className="font-bold text-white">
                {t.footerBrand || 'DadRock Tabs'}
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                {t.footerText ||
                  'Guitar and bass lessons for classic rock and heavy metal fans.'}
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                href={getLocalizedPath('/', currentLang)}
                className="text-sm font-semibold text-zinc-400 transition hover:text-amber-400"
              >
                {t.home}
              </Link>

              <Link
                href={getLocalizedPath('/partners', currentLang)}
                className="text-sm font-semibold text-zinc-400 transition hover:text-amber-400"
              >
                {t.partners}
              </Link>

              <a
                href={YOUTUBE_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 transition hover:text-red-400"
              >
                <Youtube className="h-4 w-4" />
                YouTube
              </a>
            </div>
          </div>

          <p className="mt-6 text-center text-xs leading-relaxed text-zinc-600">
            {t.copyrightText ||
              `© ${new Date().getFullYear()} DadRock Tabs. All rights reserved.`}
          </p>
        </footer>
      </div>
    </main>
  );
}

function AiTabLoadingFallback() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-black px-4 text-white">
      <div className="text-center">
        <div className="mx-auto h-12 w-12 animate-spin rounded-full border-4 border-zinc-700 border-t-amber-500" />

        <p className="mt-5 font-semibold text-zinc-300">
          Loading AI Tab Generator...
        </p>
      </div>
    </main>
  );
}

export default function AiTabPage() {
  return (
    <Suspense fallback={<AiTabLoadingFallback />}>
      <AiTabGeneratorContent />
    </Suspense>
  );
                  }

'use client';

import {
  Suspense,
  useMemo,
  useRef,
  useState,
} from 'react';

import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

import {
  ArrowLeft,
  Check,
  ChevronDown,
  Download,
  FileAudio,
  FileText,
  Music2,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Youtube,
} from 'lucide-react';

import LanguageSelector, {
  useLanguage,
} from '@/components/LanguageSelector';

import PayPalCheckoutButton from
  '@/components/PayPalCheckoutButton';

const TRANSCRIPTION_TYPES = [
  {
    value: 'lead',
    label: 'Lead Guitar',
    description:
      'Solos, melodies, bends, and fills',
    icon: '🎸',
    iconClass: 'text-red-400',
  },
  {
    value: 'rhythm',
    label: 'Rhythm Guitar',
    description:
      'Riffs, chords, and backing parts',
    icon: '🎸',
    iconClass: 'text-blue-400',
  },
  {
    value: 'bass',
    label: 'Bass Guitar',
    description:
      'Bass lines, grooves, and runs',
    icon: '🎸',
    iconClass: 'text-emerald-400',
  },
];

const PROCESS_STEPS = [
  {
    number: 1,
    label: 'Upload Audio',
  },
  {
    number: 2,
    label: 'Separate Parts',
  },
  {
    number: 3,
    label: 'Detect Notes',
  },
  {
    number: 4,
    label: 'Generate Tab',
  },
  {
    number: 5,
    label: 'Preview & Pay',
  },
];

const FAQ_ITEMS = [
  {
    question:
      'How accurate will my AI-generated tab be?',
    answer:
      'Accuracy depends on the clarity of the instrument, recording quality, tuning, tempo, and complexity. You can review the preview before paying.',
  },
  {
    question:
      'What audio files can I upload?',
    answer:
      'You can upload common audio formats including MP3, WAV, M4A, and AAC, up to 100 MB.',
  },
  {
    question:
      'Can I generate guitar and bass tabs?',
    answer:
      'Yes. Choose lead guitar, rhythm guitar, or bass guitar before generating your transcription.',
  },
  {
    question:
      'What happens to my uploaded audio?',
    answer:
      'Your recording is used only to process your private transcription request and is never published as a DadRock Tabs lesson.',
  },
  {
    question:
      'What do I receive after payment?',
    answer:
      'You receive a polished, printable DadRock Tabs PDF containing the completed tablature.',
  },
];

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();
  const [selectedLang] = useLanguage();
  const fileInputRef = useRef(null);

  const currentLang =
    selectedLang || 'en';

  const localizedHomePath =
    currentLang === 'en'
      ? '/'
      : `/${currentLang}`;

  const [youtubeUrl, setYoutubeUrl] =
    useState(
      searchParams.get('youtube') || ''
    );

  const [songTitle, setSongTitle] =
    useState(
      searchParams.get('song') || ''
    );

  const [artistName, setArtistName] =
    useState(
      searchParams.get('artist') || ''
    );

  const [
    selectedType,
    setSelectedType,
  ] = useState('lead');

  const [audioFile, setAudioFile] =
    useState(null);

  const [
    copyrightConfirmed,
    setCopyrightConfirmed,
  ] = useState(false);

  const [
    customerEmail,
    setCustomerEmail,
  ] = useState('');

  const [
    generatedTab,
    setGeneratedTab,
  ] = useState('');

  const [
    previewReady,
    setPreviewReady,
  ] = useState(false);

  const [
    isGenerating,
    setIsGenerating,
  ] = useState(false);

  const [
    generationError,
    setGenerationError,
  ] = useState('');

  const [
    statusMessage,
    setStatusMessage,
  ] = useState('');
    const [
    paymentCompleted,
    setPaymentCompleted,
  ] = useState(false);

  const [
    purchaseOrderId,
    setPurchaseOrderId,
  ] = useState('');

  const [
    isDownloading,
    setIsDownloading,
  ] = useState(false);

  const [openFaq, setOpenFaq] =
    useState(null);

  const formIsComplete = useMemo(
  () =>
    Boolean(
      songTitle.trim() &&
      artistName.trim() &&
      selectedType &&
      (audioFile || youtubeUrl.trim()) &&
      copyrightConfirmed
    ),
  [
    songTitle,
    artistName,
    selectedType,
    audioFile,
    youtubeUrl,
    copyrightConfirmed,
  ]
);

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0] || null;

    setGenerationError('');
    setStatusMessage('');

    if (!selectedFile) {
      setAudioFile(null);
      return;
    }

    const maximumFileSize =
      100 * 1024 * 1024;

    if (
      !selectedFile.type.startsWith(
        'audio/'
      )
    ) {
      setAudioFile(null);

      setGenerationError(
        'Please choose a valid audio file.'
      );

      event.target.value = '';
      return;
    }

    if (
      selectedFile.size >
      maximumFileSize
    ) {
      setAudioFile(null);

      setGenerationError(
        'The audio file must be smaller than 100 MB.'
      );

      event.target.value = '';
      return;
    }

    setAudioFile(selectedFile);
    setPreviewReady(false);
    setGeneratedTab('');
    setPaymentCompleted(false);
    setPurchaseOrderId('');
  };

  const removeAudioFile = () => {
    setAudioFile(null);
    setPreviewReady(false);
    setGeneratedTab('');
    setPaymentCompleted(false);
    setPurchaseOrderId('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGeneratePreview =
    async () => {
      if (
        !formIsComplete ||
        isGenerating
      ) {
        setStatusMessage(
          'Upload an audio file, enter the song information, choose an instrument, and confirm the copyright statement.'
        );

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
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              song: songTitle.trim(),
              artist:
                artistName.trim(),
              transcriptionType:
                selectedType,
              youtubeUrl:
                youtubeUrl.trim(),
              audioFileName:
                audioFile?.name || '',
              audioFileType:
                audioFile?.type || '',
              audioFileSize:
                audioFile?.size || 0,
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data.error ||
              'The tab preview could not be generated.'
          );
        }

        setGeneratedTab(
          data.tab ||
            data.generatedTab ||
            ''
        );

        setPreviewReady(true);

        setStatusMessage(
          'Your AI tablature preview is ready.'
        );
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
    const handlePaymentApproved =
    async (orderId) => {
      if (!orderId) {
        setGenerationError(
          'The PayPal order could not be verified.'
        );
        return;
      }

      setGenerationError('');
      setStatusMessage(
        'Verifying your payment...'
      );

      try {
        const response = await fetch(
          '/api/paypal/capture-order',
          {
            method: 'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              orderId,
              song: songTitle.trim(),
              artist:
                artistName.trim(),
              transcriptionType:
                selectedType,
              customerEmail:
                customerEmail.trim(),
            }),
          }
        );

        const data =
          await response.json();

        if (!response.ok) {
          throw new Error(
            data.error ||
              'The PayPal payment could not be completed.'
          );
        }

        setPurchaseOrderId(orderId);
        setPaymentCompleted(true);

        setStatusMessage(
          'Payment successful! Your polished PDF is ready.'
        );
      } catch (error) {
        setPaymentCompleted(false);
        setPurchaseOrderId('');
        setStatusMessage('');

        setGenerationError(
          error instanceof Error
            ? error.message
            : 'The PayPal payment could not be completed.'
        );
      }
    };

  const handlePaymentCancelled =
    () => {
      setGenerationError('');

      setStatusMessage(
        'Payment cancelled.'
      );
    };

  const handlePaymentError =
    () => {
      setPaymentCompleted(false);
      setPurchaseOrderId('');
      setStatusMessage('');

      setGenerationError(
        'PayPal encountered an error.'
      );
    };

  const handleDownloadPdf =
    async () => {
      if (
        !purchaseOrderId ||
        isDownloading
      ) {
        return;
      }

      setIsDownloading(true);

      try {
        const response = await fetch(
          '/api/generate-tab-pdf',
          {
            method: 'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              orderId:
                purchaseOrderId,
              song:
                songTitle.trim(),
              artist:
                artistName.trim(),
              transcriptionType:
                selectedType,
              generatedTab,
              customerEmail:
                customerEmail.trim(),
            }),
          }
        );

        if (!response.ok) {
          throw new Error(
            'The PDF could not be generated.'
          );
        }

        const pdfBlob =
          await response.blob();

        const url =
          window.URL.createObjectURL(
            pdfBlob
          );

        const link =
          document.createElement('a');

        link.href = url;
        link.download =
          'dadrock-ai-tab.pdf';

        document.body.appendChild(
          link
        );

        link.click();

        link.remove();

        window.URL.revokeObjectURL(
          url
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
    const handleStartOver = () => {
    setYoutubeUrl('');
    setSongTitle('');
    setArtistName('');
    setSelectedType('lead');
    setAudioFile(null);
    setCopyrightConfirmed(false);
    setCustomerEmail('');
    setGeneratedTab('');
    setPreviewReady(false);
    setGenerationError('');
    setStatusMessage('');
    setPaymentCompleted(false);
    setPurchaseOrderId('');
    setOpenFaq(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <main className="min-h-screen bg-black text-white">
      <div className="mx-auto w-full max-w-6xl px-3 py-4 sm:px-5 lg:px-6">
        <div className="mb-3 flex items-center justify-between gap-3">
          <Link
            href={localizedHomePath}
            className="inline-flex items-center gap-2 text-xs font-bold text-amber-400 transition hover:text-orange-300 sm:text-sm"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to DadRock Tabs
          </Link>

          <LanguageSelector />
        </div>

        <header className="text-center">
  <img
    src="/DadRock-Tabs-Logo.png"
    alt="DadRock Tabs"
    className="mx-auto h-auto w-full max-w-[30rem] object-contain"
  />

  <div className="mx-auto mt-2 max-w-5xl rounded-2xl border border-orange-500/60 bg-black px-4 py-4 shadow-[0_0_24px_rgba(249,115,22,0.2)] sm:mt-3 sm:px-7 sm:py-5">
    <h1 className="text-2xl font-black tracking-tight text-white sm:text-4xl">
      AI Guitar &amp; Bass Tab Generator
    </h1>

    <p className="mx-auto mt-2 max-w-3xl text-sm leading-5 text-zinc-300 sm:text-base">
      Upload any song and get printable guitar or bass tabs in minutes with the power of AI.
    </p>
  </div>
</header>

        <section className="mt-3 grid gap-3 lg:grid-cols-2">
          <div className="space-y-3">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4 sm:p-5">
              <div className="flex items-start gap-3">
                <Youtube className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />

                <div className="min-w-0 flex-1">
                  <h2 className="text-base font-black text-white sm:text-lg">
                    YouTube reference link
                  </h2>

                  <p className="mt-1 text-xs leading-5 text-zinc-400 sm:text-sm">
                    Paste a YouTube link to identify and preview
                    the recording.
                  </p>
                </div>
              </div>

              <input
                type="url"
                value={youtubeUrl}
                onChange={(event) =>
                  setYoutubeUrl(event.target.value)
                }
                placeholder="https://www.youtube.com/watch?v=..."
                className="mt-3 w-full rounded-xl border border-zinc-700 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
              />
            </div>

            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4 sm:p-5">
              <div className="flex items-center gap-3">
                <Music2 className="h-5 w-5 text-amber-400" />

                <h2 className="text-base font-black text-white sm:text-lg">
                  Song Information
                </h2>
              </div>

              <div className="mt-3 grid gap-3">
                <div>
                  <label
                    htmlFor="song-title"
                    className="mb-1.5 block text-xs font-bold text-zinc-300 sm:text-sm"
                  >
                    Song Title
                  </label>

                  <input
                    id="song-title"
                    type="text"
                    value={songTitle}
                    onChange={(event) =>
                      setSongTitle(event.target.value)
                    }
                    placeholder="Enter the song title"
                    className="w-full rounded-xl border border-zinc-700 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>

                <div>
                  <label
                    htmlFor="artist-name"
                    className="mb-1.5 block text-xs font-bold text-zinc-300 sm:text-sm"
                  >
                    Artist or Band
                  </label>

                  <input
                    id="artist-name"
                    type="text"
                    value={artistName}
                    onChange={(event) =>
                      setArtistName(event.target.value)
                    }
                    placeholder="Enter the artist or band"
                    className="w-full rounded-xl border border-zinc-700 bg-black px-3 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>
              </div>
            </div>
          </div>
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4 sm:p-5">
            <div className="flex items-start gap-3">
              <Upload className="mt-0.5 h-5 w-5 shrink-0 text-orange-400" />

              <div>
                <h2 className="text-base font-black text-white sm:text-lg">
                  Upload Audio
                </h2>

                <p className="mt-1 text-xs leading-5 text-zinc-400 sm:text-sm">
                  Choose an MP3, WAV, M4A, or AAC file from your
                  device.
                </p>
              </div>
            </div>

            <label
              htmlFor="audio-file"
              className="mt-3 flex min-h-52 cursor-pointer flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-700 bg-black px-4 py-6 text-center transition hover:border-orange-500 hover:bg-orange-500/5 sm:min-h-64"
            >
              <FileAudio className="h-11 w-11 text-orange-400 sm:h-14 sm:w-14" />

              <span className="mt-3 rounded-full bg-gradient-to-r from-orange-500 to-red-500 px-5 py-2 text-sm font-black text-white shadow-[0_0_18px_rgba(249,115,22,0.3)]">
                Browse Audio Files
              </span>

              <span className="mt-3 text-xs text-zinc-400">
                or tap here to select your audio
              </span>

              <span className="mt-1 text-[11px] text-zinc-600">
                Supported formats: MP3, WAV, M4A, AAC
              </span>

              <input
                ref={fileInputRef}
                id="audio-file"
                type="file"
                accept="audio/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {audioFile && (
              <div className="mt-3 flex items-center justify-between gap-3 rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-3">
                <div className="min-w-0">
                  <p className="truncate text-sm font-bold text-emerald-300">
                    {audioFile.name}
                  </p>

                  <p className="mt-0.5 text-xs text-zinc-500">
                    {(audioFile.size / 1024 / 1024).toFixed(1)} MB
                  </p>
                </div>

                <button
                  type="button"
                  onClick={removeAudioFile}
                  className="rounded-full border border-zinc-700 bg-black p-2 text-zinc-400 transition hover:border-red-500 hover:text-red-400"
                  aria-label="Remove audio file"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </section>

        <section className="mt-3 rounded-2xl border border-zinc-800 bg-zinc-950 p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <Music2 className="h-5 w-5 text-amber-400" />

            <h2 className="text-base font-black text-white sm:text-lg">
              Choose the Part to Transcribe
            </h2>
          </div>

          <div className="mt-3 grid gap-3 md:grid-cols-3">
            {TRANSCRIPTION_TYPES.map((type) => {
              const isSelected =
                selectedType === type.value;

              return (
                <button
                  key={type.value}
                  type="button"
                  onClick={() =>
                    setSelectedType(type.value)
                  }
                  className={`relative flex items-center gap-3 rounded-2xl border px-4 py-3 text-left transition ${
                    isSelected
                      ? 'border-orange-500 bg-orange-500/12 shadow-[0_0_18px_rgba(249,115,22,0.16)]'
                      : 'border-zinc-800 bg-black hover:border-orange-500/70'
                  }`}
                >
                  <span className={`text-3xl ${type.iconClass}`}>
                    {type.icon}
                  </span>

                  <span className="min-w-0 flex-1">
                    <span className="block text-sm font-black text-white">
                      {type.label}
                    </span>

                    <span className="mt-0.5 block text-xs leading-4 text-zinc-400">
                      {type.description}
                    </span>
                  </span>

                  <span
                    className={`h-5 w-5 shrink-0 rounded-full border ${
                      isSelected
                        ? 'border-orange-500 bg-orange-500'
                        : 'border-zinc-600 bg-black'
                    }`}
                  >
                    {isSelected && (
                      <Check className="h-full w-full p-0.5 text-white" />
                    )}
                  </span>
                </button>
              );
            })}
          </div>
        </section>
        <section className="mt-3 rounded-2xl border border-orange-500/40 bg-gradient-to-r from-orange-500/10 via-orange-500/5 to-transparent p-4 sm:p-5">
          <div className="grid gap-5 lg:grid-cols-[1fr_320px] lg:items-center">
            <div>
              <div className="rounded-2xl border border-zinc-700 bg-black/40 p-4">
                <div className="flex items-start gap-3">
                  <ShieldCheck className="mt-0.5 h-5 w-5 text-emerald-400" />

                  <div>
                    <h3 className="text-sm font-black text-white">
                      Copyright Confirmation
                    </h3>

                    <p className="mt-2 text-xs leading-5 text-zinc-400">
                      Only upload recordings you own or have
                      permission to use. Your upload is used only
                      to generate your private transcription.
                    </p>
                  </div>
                </div>

                <label className="mt-4 flex cursor-pointer items-start gap-3">
                  <input
                    type="checkbox"
                    checked={copyrightConfirmed}
                    onChange={(event) =>
                      setCopyrightConfirmed(
                        event.target.checked
                      )
                    }
                    className="mt-1 h-5 w-5 accent-orange-500"
                  />

                  <span className="text-xs leading-5 text-zinc-300">
                    I confirm that I own this recording or have
                    permission to create this AI transcription.
                  </span>
                </label>

                <div className="mt-4">
                  <label className="mb-2 block text-xs font-bold text-zinc-300">
                    Email address
                  </label>

                  <input
                    type="email"
                    value={customerEmail}
                    onChange={(event) =>
                      setCustomerEmail(
                        event.target.value
                      )
                    }
                    placeholder="you@example.com"
required
                    className="w-full rounded-xl border border-zinc-700 bg-black px-3 py-3 text-sm text-white outline-none placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>

                {statusMessage && (
                  <div className="mt-4 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-300">
                    {statusMessage}
                  </div>
                )}

                {generationError && (
                  <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-300">
                    {generationError}
                  </div>
                )}
              </div>
            </div>

            <div className="text-center">
              <button
                type="button"
                onClick={handleGeneratePreview}
                disabled={
                  !formIsComplete ||
                  isGenerating
                }
                className="w-full rounded-3xl bg-gradient-to-r from-amber-400 via-orange-500 to-red-600 px-6 py-7 text-2xl font-black tracking-tight text-white shadow-[0_0_50px_rgba(249,115,22,0.55)] transition duration-300 hover:scale-[1.03] hover:shadow-[0_0_70px_rgba(249,115,22,0.75)] disabled:cursor-not-allowed disabled:opacity-50"
              >
                {isGenerating ? (
                  <>
                    <Sparkles className="mx-auto mb-2 h-7 w-7 animate-pulse" />
                    Generating...
                  </>
                ) : (
                  <>
                    🎸 Generate Professional AI Tab
                  </>
                )}
              </button>

              <p className="mt-3 text-xs text-zinc-400">
                Preview first • Pay only if you're happy
              </p>
            </div>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-2 sm:grid-cols-5 [&>*:last-child]:col-span-2 [&>*:last-child]:sm:col-span-1">
            {PROCESS_STEPS.map((step) => (
              <div
                key={step.number}
                className="rounded-xl border border-zinc-800 bg-black/50 p-3 text-center"
              >
                <div className="mx-auto flex h-9 w-9 items-center justify-center rounded-full bg-orange-500 text-sm font-black text-white">
                  {step.number}
                </div>

                <p className="mt-2 text-[11px] font-bold text-zinc-300">
                  {step.label}
                </p>
              </div>
            ))}
          </div>
        </section>
        {previewReady && (
          <section className="mt-3 rounded-2xl border border-orange-500/40 bg-zinc-950 p-4 sm:p-5">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-xs font-black uppercase tracking-[0.2em] text-orange-400">
                  Your AI Transcription
                </p>

                <h2 className="mt-1 text-xl font-black text-white sm:text-2xl">
                  Preview Your Generated Tab
                </h2>

                <p className="mt-1 text-xs text-zinc-400 sm:text-sm">
                  {songTitle} by {artistName}
                </p>
              </div>

              <span className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 text-xs font-black text-emerald-300">
                <Check className="h-4 w-4" />
                Preview Ready
              </span>
            </div>

            <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_320px]">
              <div className="overflow-hidden rounded-2xl border border-zinc-700 bg-zinc-200">
                <div className="flex items-center justify-between border-b border-zinc-300 bg-white px-4 py-3 text-black">
                  <div className="flex items-center gap-2">
                    <FileText className="h-5 w-5 text-orange-500" />

                    <span className="text-sm font-black">
                      DadRock AI Tab Preview
                    </span>
                  </div>

                  <span className="rounded-full bg-zinc-100 px-3 py-1 text-[11px] font-bold text-zinc-600">
                    {TRANSCRIPTION_TYPES.find(
                      (type) =>
                        type.value === selectedType
                    )?.label || 'Tab'}
                  </span>
                </div>

                <div className="bg-white p-4 text-black sm:p-6">
                  <div className="mx-auto max-w-3xl rounded-xl border border-zinc-300 bg-white p-4 shadow-sm sm:p-6">
                    <div className="border-b border-zinc-300 pb-4 text-center">
                      <h3 className="text-xl font-black">
                        {songTitle}
                      </h3>

                      <p className="mt-1 text-sm text-zinc-600">
                        {artistName}
                      </p>

                      <p className="mt-2 text-xs font-bold uppercase tracking-[0.15em] text-orange-500">
                        DadRock Tabs AI Transcription
                      </p>
                    </div>

                    <pre className="mt-4 max-h-[520px] overflow-auto whitespace-pre-wrap font-mono text-[11px] leading-5 text-zinc-900 sm:text-xs">
                      {generatedTab ||
                        'Your generated tablature will appear here.'}
                    </pre>
                  </div>
                </div>
              </div>

              {!paymentCompleted ? (
                <div className="rounded-2xl border border-orange-500/30 bg-gradient-to-b from-orange-500/12 to-black p-4">
                  <div className="text-center">
                    <Download className="mx-auto h-8 w-8 text-orange-400" />

                    <h3 className="mt-3 text-xl font-black text-white">
                      Download the Polished PDF
                    </h3>

                    <p className="mt-2 text-xs leading-5 text-zinc-400">
                      Unlock the complete printable PDF after
                      reviewing your AI-generated preview.
                    </p>
                  </div>

                  <div className="mt-4 space-y-2 text-xs text-zinc-300">
                    <p className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-emerald-400" />
                      Clean portrait layout
                    </p>

                    <p className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-emerald-400" />
                      Full guitar or bass tab
                    </p>

                    <p className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-emerald-400" />
                      Instant download
                    </p>
                  </div>

                  <div className="mt-5 rounded-xl border border-zinc-700 bg-black p-3">
                    <PayPalCheckoutButton
                      song={songTitle.trim()}
                      artist={artistName.trim()}
                      transcriptionType={selectedType}
                      customerEmail={customerEmail.trim()}
                      onApprove={handlePaymentApproved}
                      onCancel={handlePaymentCancelled}
                      onError={handlePaymentError}
                    />
                  </div>
                </div>
              ) : (
                <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                  <div className="flex items-start gap-3">
                    <div className="rounded-full bg-emerald-500 p-2 text-white">
                      <Check className="h-5 w-5" />
                    </div>

                    <div>
                      <h3 className="text-lg font-black text-white">
                        Payment Complete
                      </h3>

                      <p className="mt-1 text-xs leading-5 text-emerald-300">
                        Your polished DadRock Tabs PDF is ready.
                      </p>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleDownloadPdf}
                    disabled={isDownloading}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-emerald-500 px-4 py-3 text-sm font-black text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Download className="h-4 w-4" />

                    {isDownloading
                      ? 'Preparing PDF...'
                      : 'Download Polished PDF'}
                  </button>

                  <button
                    type="button"
                    onClick={handleStartOver}
                    className="mt-3 w-full rounded-xl border border-zinc-700 bg-black/50 px-4 py-3 text-sm font-bold text-zinc-200 transition hover:border-orange-500 hover:text-white"
                  >
                    Generate Another Tab
                  </button>
                </div>
              )}
            </div>
          </section>
        )}

        <section className="mt-3 grid gap-3 md:grid-cols-3">
          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-start gap-3">
              <Sparkles className="mt-0.5 h-5 w-5 text-orange-400" />

              <div>
                <h2 className="text-sm font-black text-white">
                  AI-Powered Separation
                </h2>

                <p className="mt-1 text-xs leading-5 text-zinc-400">
                  AI isolates the selected guitar or bass part
                  before analyzing the notes.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-start gap-3">
              <ShieldCheck className="mt-0.5 h-5 w-5 text-emerald-400" />

              <div>
                <h2 className="text-sm font-black text-white">
                  Private and Secure
                </h2>

                <p className="mt-1 text-xs leading-5 text-zinc-400">
                  Your recording is used only for your private
                  transcription request.
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-zinc-800 bg-zinc-950 p-4">
            <div className="flex items-start gap-3">
              <FileText className="mt-0.5 h-5 w-5 text-blue-400" />

              <div>
                <h2 className="text-sm font-black text-white">
                  Print-Ready PDF
                </h2>

                <p className="mt-1 text-xs leading-5 text-zinc-400">
                  Download a polished portrait PDF designed for
                  practice and printing.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-3 rounded-2xl border border-zinc-800 bg-zinc-950 p-4 sm:p-5">
          <div className="text-center">
            <p className="text-xs font-black uppercase tracking-[0.2em] text-orange-400">
              Frequently Asked Questions
            </p>

            <h2 className="mt-1 text-xl font-black text-white sm:text-2xl">
              Everything You Need to Know
            </h2>
          </div>

          <div className="mt-4 grid gap-3 md:grid-cols-2">
            {FAQ_ITEMS.map((item, index) => {
              const isOpen =
                openFaq === index;

              return (
                <div
                  key={item.question}
                  className="overflow-hidden rounded-xl border border-zinc-800 bg-black/50"
                >
                  <button
                    type="button"
                    onClick={() =>
                      setOpenFaq(
                        isOpen ? null : index
                      )
                    }
                    className="flex w-full items-center justify-between gap-3 px-4 py-4 text-left"
                  >
                    <span className="text-sm font-black text-white">
                      {item.question}
                    </span>

                    <ChevronDown
                      className={`h-4 w-4 shrink-0 text-orange-400 transition ${
                        isOpen
                          ? 'rotate-180'
                          : ''
                      }`}
                    />
                  </button>

                  {isOpen && (
                    <div className="border-t border-zinc-800 px-4 py-4 text-xs leading-5 text-zinc-400">
                      {item.answer}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
        <footer className="mt-4 border-t border-zinc-800 py-6 text-center">
          <img
  src="/DadRock-Tabs-Logo.png"
  alt="DadRock Tabs"
  className="mx-auto h-auto w-full max-w-48 object-contain"
/>

          <p className="mx-auto mt-2 max-w-2xl text-xs leading-5 text-zinc-500">
            AI-generated tablature may require small corrections.
            Always use your ears and compare the transcription with
            the original recording.
          </p>

          <Link
            href={localizedHomePath}
            className="mt-4 inline-flex items-center gap-2 text-sm font-bold text-orange-400 transition hover:text-orange-300"
          >
            <ArrowLeft className="h-4 w-4" />
            Return to DadRock Tabs
          </Link>
        </footer>
      </div>
    </main>
  );
}

export default function AiTabGeneratorPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-black text-white">
          <div className="text-center">
            <Sparkles className="mx-auto h-8 w-8 animate-pulse text-orange-400" />

            <p className="mt-3 text-sm font-bold text-zinc-300">
              Loading AI Tab Generator...
            </p>
          </div>
        </main>
      }
    >
      <AiTabGeneratorContent />
    </Suspense>
  );
}

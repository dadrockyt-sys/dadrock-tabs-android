'use client';

import {
  Suspense,
  useMemo,
  useRef,
  useState,
} from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  ArrowLeft,
  Check,
  CreditCard,
  Download,
  FileAudio,
  FileText,
  Guitar,
  Music,
  Printer,
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
    value: 'lead-guitar',
    label: 'Lead Guitar',
    description: 'Solos, melodies, bends, and fills',
    icon: '🎸',
  },
  {
    value: 'rhythm-guitar',
    label: 'Rhythm Guitar',
    description: 'Riffs, chords, and backing parts',
    icon: '🎸',
  },
  {
    value: 'bass-guitar',
    label: 'Bass Guitar',
    description: 'Bass lines, grooves, and runs',
    icon: '🎸',
  },
];

const FAQ_ITEMS = [
  {
    question:
      'How accurate will my AI-generated tab be?',
    answer:
      'Accuracy depends on the recording quality, instrument clarity, tuning, and complexity of the song. You can review the generated preview before purchasing the polished PDF.',
  },
  {
    question:
      'What audio files can I upload?',
    answer:
      'The generator accepts common audio formats such as MP3, WAV, M4A, AAC, and similar browser-supported audio files.',
  },
  {
    question:
      'Can I generate guitar and bass tabs?',
    answer:
      'Yes. You can choose lead guitar, rhythm guitar, or bass guitar before generating your preview.',
  },
  {
    question:
      'What happens to my uploaded audio?',
    answer:
      'Your audio is used only to process the requested transcription. It is not displayed publicly or added to the DadRock Tabs lesson library.',
  },
  {
    question:
      'What do I receive after payment?',
    answer:
      'After successful payment, you can download a polished, printable PDF containing your generated tablature.',
  },
];

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();
  const [selectedLang] = useLanguage();

  const currentLang =
    selectedLang || 'en';

  const fileInputRef = useRef(null);

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
  ] = useState('lead-guitar');

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
          audioFile &&
          copyrightConfirmed
      ),
    [
      songTitle,
      artistName,
      selectedType,
      audioFile,
      copyrightConfirmed,
    ]
  );

  const localizedHomePath =
    !currentLang ||
    currentLang === 'en'
      ? '/'
      : `/${currentLang}`;

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
          'Upload an audio file, choose an instrument, enter the song information, and confirm the copyright statement.'
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
          'Payment successful! Your polished tab PDF is ready to download.'
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

  const handlePaymentCancelled = () => {
    setGenerationError('');

    setStatusMessage(
      'Payment was cancelled. You have not been charged.'
    );
  };

  const handlePaymentError = () => {
    setPaymentCompleted(false);
    setPurchaseOrderId('');
    setStatusMessage('');

    setGenerationError(
      'PayPal encountered an error. Please try again.'
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
      setGenerationError('');

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
              song: songTitle.trim(),
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
          let errorMessage =
            'The PDF could not be generated.';

          try {
            const data =
              await response.json();

            errorMessage =
              data.error ||
              errorMessage;
          } catch {
            // Keep the default message.
          }

          throw new Error(
            errorMessage
          );
        }

        const pdfBlob =
          await response.blob();

        const downloadUrl =
          window.URL.createObjectURL(
            pdfBlob
          );

        const disposition =
          response.headers.get(
            'Content-Disposition'
          );

        const fileNameMatch =
          disposition?.match(
            /filename="?([^"]+)"?/i
          );

        const fileName =
          fileNameMatch?.[1] ||
          'dadrock-ai-tab.pdf';

        const downloadLink =
          document.createElement('a');

        downloadLink.href =
          downloadUrl;

        downloadLink.download =
          fileName;

        document.body.appendChild(
          downloadLink
        );

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
    const handleStartOver = () => {
    setYoutubeUrl('');
    setSongTitle('');
    setArtistName('');
    setSelectedType('lead-guitar');
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
      <div className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(249,115,22,0.15),transparent_35%)]" />

        <div className="relative mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 lg:px-8">
          <div className="mb-5 flex items-center justify-between gap-4">
            <Link
              href={localizedHomePath}
              className="inline-flex items-center gap-2 text-sm font-bold text-amber-400 transition hover:text-orange-300"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to DadRock Tabs
            </Link>

            <LanguageSelector />
          </div>

          <header className="text-center">
            <Image
              src="/dadrockmetal.png"
              alt="DadRock Tabs"
              width={760}
              height={330}
              priority
              className="mx-auto h-auto w-full max-w-2xl object-contain"
            />

            <div className="mx-auto mt-2 max-w-5xl rounded-3xl border border-orange-500/50 bg-black/80 px-5 py-7 shadow-[0_0_35px_rgba(249,115,22,0.18)] sm:px-10">
              <h1 className="text-3xl font-black tracking-tight text-white sm:text-5xl">
                AI Guitar &amp; Bass Tab Generator
              </h1>

              <p className="mx-auto mt-3 max-w-3xl text-base leading-7 text-zinc-300 sm:text-lg">
                Upload any song and get printable guitar or bass
                tabs in minutes with the power of AI.
              </p>
            </div>
          </header>

          <section className="mt-5 grid gap-4 lg:grid-cols-2">
            <div className="rounded-3xl border border-zinc-800 bg-zinc-950/85 p-5 shadow-xl sm:p-6">
              <div className="flex items-center gap-3">
                <Youtube className="h-6 w-6 text-red-500" />

                <div>
                  <h2 className="text-xl font-black text-white">
                    YouTube reference link
                  </h2>

                  <p className="mt-1 text-sm text-zinc-400">
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
                className="mt-5 w-full rounded-2xl border border-zinc-700 bg-black px-4 py-4 text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20"
              />

              <div className="mt-5 border-t border-zinc-800 pt-5">
                <div className="flex items-center gap-3">
                  <Music className="h-6 w-6 text-amber-400" />

                  <h2 className="text-xl font-black text-white">
                    Song Information
                  </h2>
                </div>

                <div className="mt-4 space-y-4">
                  <div>
                    <label
                      htmlFor="song-title"
                      className="mb-2 block text-sm font-bold text-zinc-300"
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
                      className="w-full rounded-2xl border border-zinc-700 bg-black px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                    />
                  </div>
                    <div>
                    <label
                      htmlFor="artist-name"
                      className="mb-2 block text-sm font-bold text-zinc-300"
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
                      className="w-full rounded-2xl border border-zinc-700 bg-black px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-950/85 p-5 shadow-xl sm:p-6">
              <div className="flex items-center gap-3">
                <Upload className="h-6 w-6 text-orange-400" />

                <div>
                  <h2 className="text-xl font-black text-white">
                    Upload your audio
                  </h2>

                  <p className="mt-1 text-sm text-zinc-400">
                    MP3, WAV, M4A, AAC, or another supported audio
                    format up to 100 MB.
                  </p>
                </div>
              </div>

              <label
                htmlFor="audio-file"
                className="mt-5 flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-3xl border-2 border-dashed border-zinc-700 bg-black/60 px-5 py-8 text-center transition hover:border-orange-500 hover:bg-orange-500/5"
              >
                <FileAudio className="h-12 w-12 text-orange-400" />

                <span className="mt-4 text-lg font-black text-white">
                  Choose an audio file
                </span>

                <span className="mt-2 text-sm text-zinc-500">
                  Tap here to browse files on your device
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
                <div className="mt-4 flex items-center justify-between gap-4 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4">
                  <div className="min-w-0">
                    <p className="truncate font-bold text-emerald-300">
                      {audioFile.name}
                    </p>

                    <p className="mt-1 text-xs text-zinc-400">
                      {(audioFile.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={removeAudioFile}
                    className="rounded-full border border-zinc-700 bg-black p-2 text-zinc-300 transition hover:border-red-500 hover:text-red-400"
                    aria-label="Remove audio file"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              )}
            </div>
          </section>

          <section className="mt-5 rounded-3xl border border-zinc-800 bg-zinc-950/85 p-5 shadow-xl sm:p-7">
            <div className="text-center">
              <p className="text-sm font-black uppercase tracking-[0.25em] text-orange-400">
                Choose your transcription
              </p>

              <h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">
                Which instrument do you want tabbed?
              </h2>
            </div>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
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
                    className={`relative rounded-3xl border p-6 text-left transition ${
                      isSelected
                        ? 'border-orange-500 bg-orange-500/15 shadow-[0_0_24px_rgba(249,115,22,0.18)]'
                        : 'border-zinc-800 bg-black/60 hover:border-orange-500/70'
                    }`}
                  >
                    {isSelected && (
                      <span className="absolute right-4 top-4 rounded-full bg-orange-500 p-1 text-white">
                        <Check className="h-4 w-4" />
                      </span>
                    )}

                    <div className="text-5xl">
                      {type.icon}
                    </div>

                    <h3 className="mt-5 text-xl font-black text-white">
                      {type.label}
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-zinc-400">
                      {type.description}
                    </p>
                  </button>
                );
              })}
            </div>
              </section>
          <section className="mt-5 rounded-3xl border border-orange-500/40 bg-gradient-to-r from-orange-500/15 via-orange-500/8 to-transparent p-6 shadow-[0_0_35px_rgba(249,115,22,0.18)]">
            <div className="grid gap-8 lg:grid-cols-[1.3fr_0.7fr] lg:items-center">
              <div>
                <div className="flex items-start gap-3 rounded-2xl border border-zinc-700 bg-black/40 p-4">
                  <ShieldCheck className="mt-1 h-6 w-6 text-emerald-400" />

                  <div>
                    <h3 className="font-black text-white">
                      Copyright Confirmation
                    </h3>

                    <p className="mt-2 text-sm leading-6 text-zinc-400">
                      Only upload recordings you own or have
                      permission to use. DadRock Tabs does not
                      store or publish your uploaded audio.
                    </p>
                  </div>
                </div>

                <label className="mt-5 flex cursor-pointer items-start gap-4 rounded-2xl border border-zinc-700 bg-black/40 p-4">
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

                  <span className="text-sm leading-6 text-zinc-300">
                    I confirm that I own this recording or have
                    permission to generate a private AI
                    transcription.
                  </span>
                </label>

                <div className="mt-6">
                  <label className="mb-2 block text-sm font-bold text-zinc-300">
                    Email address (optional)
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
                    className="w-full rounded-2xl border border-zinc-700 bg-black px-4 py-3 text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>

                {statusMessage && (
                  <div className="mt-5 rounded-2xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300">
                    {statusMessage}
                  </div>
                )}

                {generationError && (
                  <div className="mt-5 rounded-2xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
                    {generationError}
                  </div>
                )}
              </div>

              <div className="text-center">
                <button
                  type="button"
                  onClick={handleGeneratePreview}
                  disabled={!formIsComplete || isGenerating}
                  className="w-full rounded-3xl bg-gradient-to-r from-orange-500 to-amber-500 px-8 py-6 text-2xl font-black text-white shadow-[0_0_35px_rgba(249,115,22,0.35)] transition hover:scale-[1.02] disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isGenerating ? (
                    <>
                      <Sparkles className="mx-auto mb-2 h-8 w-8 animate-pulse" />
                      Generating...
                    </>
                  ) : (
                    <>
                      🎸 Generate My AI Tab
                    </>
                  )}
                </button>

                <p className="mt-4 text-sm text-zinc-400">
                  Preview first • Pay only if you're happy
                </p>
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-5">
              {[
                'Upload',
                'Analyze',
                'Generate',
                'Preview',
                'Download',
              ].map((step, index) => (
                <div
                  key={step}
                  className="rounded-2xl border border-zinc-800 bg-black/50 p-5 text-center"
                >
                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-orange-500 text-lg font-black text-white">
                    {index + 1}
                  </div>

                  <p className="mt-4 font-bold text-white">
                    {step}
                  </p>
                </div>
              ))}
            </div>
          </section>
          {previewReady && (
            <section className="mt-5 rounded-3xl border border-orange-500/40 bg-zinc-950/90 p-5 shadow-[0_0_35px_rgba(249,115,22,0.15)] sm:p-7">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-black uppercase tracking-[0.25em] text-orange-400">
                    Your AI transcription
                  </p>

                  <h2 className="mt-2 text-2xl font-black text-white sm:text-3xl">
                    Preview your generated tab
                  </h2>

                  <p className="mt-2 text-sm text-zinc-400">
                    {songTitle} by {artistName}
                  </p>
                </div>

                <span className="inline-flex w-fit items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm font-black text-emerald-300">
                  <Check className="h-4 w-4" />
                  Preview Ready
                </span>
              </div>

              <div className="mt-6 overflow-hidden rounded-3xl border border-zinc-800 bg-black">
                <div className="flex items-center justify-between border-b border-zinc-800 px-5 py-4">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-orange-400" />

                    <span className="font-black text-white">
                      DadRock AI Tab Preview
                    </span>
                  </div>

                  <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs font-bold text-zinc-400">
                    {TRANSCRIPTION_TYPES.find(
                      (type) =>
                        type.value === selectedType
                    )?.label || 'Tab'}
                  </span>
                </div>

                <pre className="max-h-[520px] overflow-auto whitespace-pre-wrap p-5 font-mono text-xs leading-6 text-zinc-200 sm:p-7 sm:text-sm">
                  {generatedTab ||
                    'Your generated tablature will appear here.'}
                </pre>
              </div>

              {!paymentCompleted ? (
                <div className="mt-6 grid gap-6 rounded-3xl border border-orange-500/30 bg-gradient-to-br from-orange-500/15 to-transparent p-6 lg:grid-cols-[1fr_0.8fr] lg:items-center">
                  <div>
                    <div className="flex items-center gap-3">
                      <Printer className="h-7 w-7 text-orange-400" />

                      <h3 className="text-2xl font-black text-white">
                        Get the polished printable PDF
                      </h3>
                    </div>

                    <p className="mt-4 leading-7 text-zinc-300">
                      Unlock the complete professionally formatted
                      tablature PDF for printing, practice, and
                      offline use.
                    </p>

                    <div className="mt-5 space-y-3 text-sm text-zinc-300">
                      <p className="flex items-center gap-3">
                        <Check className="h-5 w-5 text-emerald-400" />
                        Clean portrait PDF layout
                      </p>

                      <p className="flex items-center gap-3">
                        <Check className="h-5 w-5 text-emerald-400" />
                        Complete guitar or bass transcription
                      </p>

                      <p className="flex items-center gap-3">
                        <Check className="h-5 w-5 text-emerald-400" />
                        Instant download after payment
                      </p>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-zinc-700 bg-black/70 p-5">
                    <div className="mb-5 text-center">
                      <CreditCard className="mx-auto h-8 w-8 text-orange-400" />

                      <p className="mt-3 text-sm font-bold text-zinc-400">
                        Secure payment with PayPal
                      </p>
                    </div>

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
                <div className="mt-6 rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-6">
                  <div className="flex flex-col gap-5 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-start gap-4">
                      <div className="rounded-full bg-emerald-500 p-3 text-white">
                        <Check className="h-6 w-6" />
                      </div>

                      <div>
                        <h3 className="text-2xl font-black text-white">
                          Payment complete
                        </h3>

                        <p className="mt-2 text-emerald-300">
                          Your polished DadRock tab PDF is ready to
                          download.
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={handleDownloadPdf}
                      disabled={isDownloading}
                      className="inline-flex items-center justify-center gap-3 rounded-2xl bg-emerald-500 px-6 py-4 text-lg font-black text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      <Download className="h-5 w-5" />

                      {isDownloading
                        ? 'Preparing PDF...'
                        : 'Download Polished PDF'}
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={handleStartOver}
                    className="mt-5 w-full rounded-2xl border border-zinc-700 bg-black/50 px-5 py-3 font-bold text-zinc-200 transition hover:border-orange-500 hover:text-white"
                  >
                    Generate Another Tab
                  </button>
                </div>
              )}
            </section>
          )}

          <section className="mt-5 grid gap-4 md:grid-cols-3">
            <div className="rounded-3xl border border-zinc-800 bg-zinc-950/85 p-6 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-orange-500/15">
                <Sparkles className="h-7 w-7 text-orange-400" />
              </div>

              <h2 className="mt-5 text-xl font-black text-white">
                AI-Powered Accuracy
              </h2>

              <p className="mt-3 text-sm leading-6 text-zinc-400">
                Advanced transcription technology analyzes the
                guitar or bass parts in your recording.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-950/85 p-6 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-orange-500/15">
                <ShieldCheck className="h-7 w-7 text-orange-400" />
              </div>

              <h2 className="mt-5 text-xl font-black text-white">
                Private and Secure
              </h2>

              <p className="mt-3 text-sm leading-6 text-zinc-400">
                Your uploaded recording is used only for your
                transcription request and is never published.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-950/85 p-6 text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-orange-500/15">
                <FileText className="h-7 w-7 text-orange-400" />
              </div>

              <h2 className="mt-5 text-xl font-black text-white">
                Print-Ready PDF
              </h2>

              <p className="mt-3 text-sm leading-6 text-zinc-400">
                Receive a polished tablature document designed for
                printing, practice, and offline use.
              </p>
            </div>
          </section>

          <section className="mt-5 rounded-3xl border border-zinc-800 bg-zinc-950/85 p-5 sm:p-7">
            <div className="text-center">
              <p className="text-sm font-black uppercase tracking-[0.25em] text-orange-400">
                Frequently Asked Questions
              </p>

              <h2 className="mt-2 text-3xl font-black text-white">
                Everything you need to know
              </h2>
            </div>

            <div className="mx-auto mt-7 max-w-4xl space-y-3">
              {FAQ_ITEMS.map((item, index) => {
                const isOpen =
                  openFaq === index;

                return (
                  <div
                    key={item.question}
                    className="overflow-hidden rounded-2xl border border-zinc-800 bg-black/50"
                  >
                    <button
                      type="button"
                      onClick={() =>
                        setOpenFaq(
                          isOpen ? null : index
                        )
                      }
                      className="flex w-full items-center justify-between gap-4 px-5 py-5 text-left"
                    >
                      <span className="font-black text-white">
                        {item.question}
                      </span>

                      <span className="text-2xl font-light text-orange-400">
                        {isOpen ? '−' : '+'}
                      </span>
                    </button>

                    {isOpen && (
                      <div className="border-t border-zinc-800 px-5 py-5 text-sm leading-7 text-zinc-400">
                        {item.answer}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>
          <footer className="mt-5 border-t border-zinc-900 py-8 text-center">
            <div className="flex flex-wrap items-center justify-center gap-5 text-sm font-bold text-zinc-500">
              <Link
                href={localizedHomePath}
                className="transition hover:text-orange-400"
              >
                DadRock Tabs
              </Link>

              <Link
                href="/privacy"
                className="transition hover:text-orange-400"
              >
                Privacy
              </Link>

              <Link
                href="/terms"
                className="transition hover:text-orange-400"
              >
                Terms
              </Link>
            </div>

            <p className="mt-4 text-xs leading-6 text-zinc-600">
              AI-generated tablature may require review and
              correction. Use only audio you own or have permission
              to transcribe.
            </p>
          </footer>
        </div>
      </div>
    </main>
  );
}

export default function AiTabPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-black text-white">
          <div className="text-center">
            <Sparkles className="mx-auto h-10 w-10 animate-pulse text-orange-400" />

            <p className="mt-4 font-bold text-zinc-300">
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

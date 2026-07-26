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
  Guitar,
  Headphones,
  Loader2,
  LockKeyhole,
  Mail,
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

import PayPalCheckoutButton from '@/components/PayPalCheckoutButton';

const LOGO_URL = '/DadRock-Tabs-Logo.png';

const TRANSCRIPTION_TYPES = [
  {
    value: 'lead',
    title: 'Lead Guitar',
    description: 'Solos, melodies, bends, and fills',
    emoji: '🎸',
  },
  {
    value: 'rhythm',
    title: 'Rhythm Guitar',
    description: 'Riffs, chords, and backing parts',
    emoji: '🎸',
  },
  {
    value: 'bass',
    title: 'Bass Guitar',
    description: 'Bass lines, grooves, and runs',
    emoji: '🎸',
  },
];

const BENEFITS = [
  {
    title: 'Upload Any Song',
    description: 'Use a YouTube link or audio file.',
    icon: Headphones,
  },
  {
    title: 'Choose Your Part',
    description: 'Lead, rhythm, or bass guitar.',
    icon: Guitar,
  },
  {
    title: 'Preview Before Payment',
    description: 'Review the tab before purchasing.',
    icon: FileText,
  },
];

const PROCESS_STEPS = [
  'Upload Audio',
  'Separate Parts',
  'Detect Notes',
  'Generate Tab',
  'Preview & Pay',
];

const FAQ_ITEMS = [
  {
    question: 'How accurate will my AI-generated tab be?',
    answer:
      'Accuracy depends on recording quality, tuning, effects, instrument separation, and performance complexity. Small corrections may sometimes be required.',
  },
  {
    question: 'What audio files can I upload?',
    answer:
      'You can upload MP3, WAV, M4A, or AAC audio files from your device.',
  },
  {
    question: 'Can I generate guitar and bass tabs?',
    answer:
      'Yes. Choose lead guitar, rhythm guitar, or bass before generating your transcription.',
  },
  {
    question: 'What happens to my uploaded audio?',
    answer:
      'Your audio is used only to process your private transcription request.',
  },
  {
    question: 'What do I receive after payment?',
    answer:
      'You receive a polished PDF that can be downloaded immediately and delivered to your email.',
  },
];

function getLocalizedPath(path, language) {
  if (!language || language === 'en') {
    return path;
  }

  return `/${language}${path}`;
}

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();
  const [selectedLanguage] = useLanguage();

  const currentLanguage = selectedLanguage || 'en';
  const fileInputRef = useRef(null);

  const [youtubeUrl, setYoutubeUrl] = useState(
    searchParams.get('youtube') || ''
  );
    const [songTitle, setSongTitle] = useState(
    searchParams.get('title') || ''
  );

  const [artistName, setArtistName] = useState(
    searchParams.get('artist') || ''
  );

  const [selectedType, setSelectedType] = useState('lead');

  const [audioFile, setAudioFile] = useState(null);

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

  const [
    openFaq,
    setOpenFaq,
  ] = useState(null);

  const emailIsValid = useMemo(() => {
    const trimmedEmail = customerEmail.trim();

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      trimmedEmail
    );
  }, [customerEmail]);

  const hasAudioSource = useMemo(
    () =>
      Boolean(
        audioFile ||
          youtubeUrl.trim()
      ),
    [audioFile, youtubeUrl]
  );

  const formIsComplete = useMemo(
    () =>
      Boolean(
        songTitle.trim() &&
          artistName.trim() &&
          selectedType &&
          hasAudioSource &&
          copyrightConfirmed &&
          emailIsValid
      ),
    [
      songTitle,
      artistName,
      selectedType,
      hasAudioSource,
      copyrightConfirmed,
      emailIsValid,
    ]
  );

  const resetGeneratedResults = () => {
    setGeneratedTab('');
    setPreviewReady(false);
    setPaymentCompleted(false);
    setPurchaseOrderId('');
    setStatusMessage('');
    setGenerationError('');
  };

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0] || null;

    resetGeneratedResults();

    if (!selectedFile) {
      setAudioFile(null);
      return;
    }

    const allowedTypes = [
      'audio/mpeg',
      'audio/mp3',
      'audio/wav',
      'audio/x-wav',
      'audio/mp4',
      'audio/m4a',
      'audio/aac',
      'audio/x-m4a',
    ];

    const allowedExtension =
      /\.(mp3|wav|m4a|aac)$/i.test(
        selectedFile.name
      );

    if (
      !allowedTypes.includes(
        selectedFile.type
      ) &&
      !allowedExtension
    ) {
      setAudioFile(null);
            if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      setGenerationError(
        'Please choose an MP3, WAV, M4A, or AAC audio file.'
      );

      return;
    }

    setAudioFile(selectedFile);
  };

  const removeAudioFile = () => {
    setAudioFile(null);
    resetGeneratedResults();

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleGeneratePreview = async () => {
    setGenerationError('');
    setStatusMessage('');

    if (!formIsComplete || isGenerating) {
      setGenerationError(
        'Please complete every required field before generating your tab.'
      );
      return;
    }

    if (
      !['lead', 'rhythm', 'bass'].includes(
        selectedType
      )
    ) {
      setGenerationError(
        'Please choose lead guitar, rhythm guitar, or bass guitar.'
      );
      return;
    }

    setIsGenerating(true);
    setPreviewReady(false);
    setPaymentCompleted(false);
    setGeneratedTab('');
    setPurchaseOrderId('');

    try {
      const formData = new FormData();

      formData.append(
        'songTitle',
        songTitle.trim()
      );

      formData.append(
        'artistName',
        artistName.trim()
      );

      formData.append(
        'transcriptionType',
        selectedType
      );

      formData.append(
        'customerEmail',
        customerEmail.trim()
      );

      formData.append(
        'copyrightConfirmed',
        String(copyrightConfirmed)
      );

      if (youtubeUrl.trim()) {
        formData.append(
          'youtubeUrl',
          youtubeUrl.trim()
        );
      }

      if (audioFile) {
        formData.append(
          'audioFile',
          audioFile
        );
      }

      setStatusMessage(
        'Analyzing your audio and building your preview...'
      );

      const response = await fetch(
        '/api/generate-tab',
        {
          method: 'POST',
          body: formData,
        }
      );

      const data = await response.json().catch(
        () => ({})
      );

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.message ||
            'Unable to generate your tab preview.'
        );
      }

      const transcription =
        data.generatedTab ||
        data.tab ||
        data.transcription ||
        '';

      if (!transcription) {
        throw new Error(
          'The transcription service returned an empty preview.'
        );
      }

      setGeneratedTab(transcription);
      setPreviewReady(true);

      setStatusMessage(
        'Your preview is ready. Review it before continuing to payment.'
      );
            window.setTimeout(() => {
        document
          .getElementById('tab-preview')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    } catch (error) {
      console.error(
        'AI tab generation error:',
        error
      );

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Unable to generate your tab preview.'
      );

      setStatusMessage('');
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePaymentApproved = async (
    orderId
  ) => {
    setGenerationError('');
    setStatusMessage(
      'Confirming your PayPal payment...'
    );

    try {
      if (!orderId) {
        throw new Error(
          'PayPal did not return an order ID.'
        );
      }

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
            songTitle: songTitle.trim(),
            artistName: artistName.trim(),
            transcriptionType:
              selectedType,
            customerEmail:
              customerEmail.trim(),
          }),
        }
      );

      const data = await response
        .json()
        .catch(() => ({}));

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.message ||
            'Unable to confirm your PayPal payment.'
        );
      }

      const paymentStatus =
        data.status ||
        data.captureStatus ||
        '';

      const acceptedStatuses = [
        'COMPLETED',
        'APPROVED',
        'SUCCESS',
      ];

      if (
        paymentStatus &&
        !acceptedStatuses.includes(
          String(
            paymentStatus
          ).toUpperCase()
        )
      ) {
        throw new Error(
          'PayPal has not marked this payment as completed.'
        );
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);

      setStatusMessage(
        'Payment confirmed. Your finished PDF is ready.'
      );

      window.setTimeout(() => {
        document
          .getElementById(
            'download-section'
          )
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    } catch (error) {
      console.error(
        'PayPal capture error:',
        error
      );

      setPaymentCompleted(false);

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Unable to confirm your PayPal payment.'
      );

      setStatusMessage('');
    }
  };
    const handlePaymentCancelled = () => {
    setPaymentCompleted(false);
    setGenerationError('');

    setStatusMessage(
      'PayPal checkout was cancelled. Your preview is still available.'
    );
  };

  const handlePaymentError = (error) => {
    console.error(
      'PayPal checkout error:',
      error
    );

    setPaymentCompleted(false);
    setStatusMessage('');

    setGenerationError(
      error instanceof Error
        ? error.message
        : 'PayPal checkout could not be completed.'
    );
  };

  const handleDownloadPdf = async () => {
    setGenerationError('');
    setStatusMessage('');

    if (!paymentCompleted) {
      setGenerationError(
        'Payment must be completed before downloading the finished PDF.'
      );
      return;
    }

    if (!purchaseOrderId) {
      setGenerationError(
        'The confirmed PayPal order ID is missing.'
      );
      return;
    }

    if (!generatedTab.trim()) {
      setGenerationError(
        'There is no generated transcription available for the PDF.'
      );
      return;
    }

    if (isDownloading) {
      return;
    }

    setIsDownloading(true);

    setStatusMessage(
      'Creating your finished PDF and preparing email delivery...'
    );

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
            orderId: purchaseOrderId,
            songTitle: songTitle.trim(),
            artistName: artistName.trim(),
            transcriptionType:
              selectedType,
            customerEmail:
              customerEmail.trim(),
            generatedTab,
            youtubeUrl:
              youtubeUrl.trim() || null,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          errorData.error ||
            errorData.message ||
            'Unable to create your finished PDF.'
        );
      }

      const contentType =
        response.headers.get(
          'content-type'
        ) || '';

      if (
        !contentType.includes(
          'application/pdf'
        )
      ) {
        const data = await response
          .json()
          .catch(() => ({}));

        throw new Error(
          data.error ||
            data.message ||
            'The server did not return a valid PDF file.'
        );
      }

      const pdfBlob = await response.blob();

      const downloadUrl =
        window.URL.createObjectURL(
          pdfBlob
        );

      const safeArtist =
        artistName
          .trim()
          .replace(
            /[^a-z0-9]+/gi,
            '-'
          )
          .replace(
            /^-+|-+$/g,
            ''
          )
          .toLowerCase() ||
        'artist';
            const safeTitle =
        songTitle
          .trim()
          .replace(
            /[^a-z0-9]+/gi,
            '-'
          )
          .replace(
            /^-+|-+$/g,
            ''
          )
          .toLowerCase() ||
        'song';

      const downloadLink =
        document.createElement('a');

      downloadLink.href = downloadUrl;

      downloadLink.download =
        `${safeArtist}-${safeTitle}-${selectedType}-tab.pdf`;

      document.body.appendChild(
        downloadLink
      );

      downloadLink.click();
      downloadLink.remove();

      window.URL.revokeObjectURL(
        downloadUrl
      );

      setStatusMessage(
        'Your PDF has downloaded. A copy is also being sent to your email.'
      );
    } catch (error) {
      console.error(
        'PDF download error:',
        error
      );

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Unable to download your finished PDF.'
      );

      setStatusMessage('');
    } finally {
      setIsDownloading(false);
    }
  };

  const selectedTypeDetails =
    TRANSCRIPTION_TYPES.find(
      (type) =>
        type.value ===
        selectedType
    ) ||
    TRANSCRIPTION_TYPES[0];

  return (
    <main className="min-h-screen bg-[#090909] text-white">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-180px] h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-orange-600/10 blur-[130px]" />

        <div className="absolute bottom-[-220px] right-[-160px] h-[420px] w-[420px] rounded-full bg-amber-500/5 blur-[130px]" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-16 pt-4 sm:px-6 lg:px-8">
        <header className="mb-5 flex items-center justify-between gap-3">
          <Link
            href={getLocalizedPath(
              '/',
              currentLanguage
            )}
            className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-950/80 px-4 py-2 text-sm font-semibold text-zinc-300 transition hover:border-orange-500/60 hover:text-white"
          >
            <ArrowLeft
              size={17}
            />

            <span>
              Back Home
            </span>
          </Link>

          <LanguageSelector />
        </header>

        <div className="overflow-hidden rounded-[28px] border border-orange-500/30 bg-gradient-to-b from-zinc-950 via-[#111111] to-zinc-950 shadow-2xl shadow-orange-950/20">
          <div className="border-b border-zinc-800 px-5 py-7 text-center sm:px-8">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs"
              className="mx-auto mb-4 h-auto w-full max-w-[440px] object-contain"
            />

            <div className="mx-auto max-w-3xl">
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-orange-500/40 bg-orange-500/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-orange-300">
                <Sparkles
                  size={15}
                />

                AI Powered Transcription
              </div>

              <h1 className="whitespace-nowrap text-[1.55rem] font-black tracking-tight text-white sm:text-5xl">
                Guitar & Bass Tab Generator
              </h1>

              <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base">
                Turn any audio into a professional guitar or bass TAB PDF
              </p>
            </div>
          </div>
            <div className="mb-4 text-center sm:mb-5">

  <h2 className="text-xl font-black text-white sm:text-3xl">
    Everything You Need in One Place
  </h2>

  <p className="mx-auto mt-1.5 max-w-2xl text-xs leading-5 text-zinc-400 sm:mt-2 sm:text-sm sm:leading-6">
    Upload your song, choose the instrument part, preview the
    transcription, and download a polished PDF.
  </p>
</div>

<div className="grid gap-2 sm:grid-cols-3 sm:gap-3">
  {BENEFITS.map(
    ({
      title,
      description,
      icon: Icon,
    }) => (
      <div
        key={title}
        className="rounded-xl border border-zinc-800 bg-zinc-900/70 px-3 py-2.5 transition hover:border-orange-500/40 sm:rounded-2xl sm:p-4"
      >
        <div className="flex items-center gap-3 sm:items-start">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg border border-orange-500/30 bg-orange-500/10 text-orange-300 sm:h-10 sm:w-10 sm:rounded-xl">
            <Icon size={18} className="sm:h-5 sm:w-5" />
          </div>

          <div className="min-w-0 flex-1">
            <h3 className="text-sm font-bold leading-5 text-white">
              {title}
            </h3>

            <p className="mt-0.5 text-[11px] leading-4 text-zinc-400 sm:mt-1 sm:text-xs sm:leading-5">
              {description}
            </p>
          </div>
        </div>
      </div>
    )
  )}
</div>

          <div className="border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8">
            <div className="grid gap-4 lg:grid-cols-2">
              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-red-500/30 bg-red-500/10 text-red-300">
                    <Youtube
                      size={21}
                    />
                  </div>

                  <div>
                    <h2 className="text-lg font-black text-white">
                      YouTube Reference
                    </h2>

                    <p className="text-xs text-zinc-500">
                      Paste a public song URL
                    </p>
                  </div>
                </div>

                <label
                  htmlFor="youtube-url"
                  className="mb-2 block text-sm font-semibold text-zinc-300"
                >
                  YouTube URL
                </label>

                <input
                  id="youtube-url"
                  type="url"
                  value={youtubeUrl}
                  onChange={(event) => {
                    setYoutubeUrl(
                      event.target.value
                    );

                    resetGeneratedResults();
                  }}
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full rounded-xl border border-zinc-700 bg-black/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                />

                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  Use this as a reference when
                  you do not have an audio file
                  saved on your device.
                </p>
              </section>

              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                    <Upload
                      size={21}
                    />
                  </div>

                  <div>
                    <h2 className="text-lg font-black text-white">
                      Upload Audio
                    </h2>

                    <p className="text-xs text-zinc-500">
                      MP3, WAV, M4A, or AAC
                    </p>
                  </div>
                </div>
                <input
                  ref={fileInputRef}
                  id="audio-file"
                  type="file"
                  accept=".mp3,.wav,.m4a,.aac,audio/*"
                  onChange={handleFileChange}
                  className="hidden"
                />

                {!audioFile ? (
                  <button
                    type="button"
                    onClick={() =>
                      fileInputRef.current?.click()
                    }
                    className="flex min-h-[128px] w-full flex-col items-center justify-center rounded-2xl border border-dashed border-zinc-700 bg-black/40 px-5 py-6 text-center transition hover:border-orange-500/60 hover:bg-orange-500/5"
                  >
                    <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-full border border-orange-500/30 bg-orange-500/10 text-orange-300">
                      <FileAudio
                        size={24}
                      />
                    </div>

                    <span className="text-sm font-bold text-white">
                      Choose Audio File
                    </span>

                    <span className="mt-1 text-xs text-zinc-500">
                      Tap to browse your device
                    </span>
                  </button>
                ) : (
                  <div className="rounded-2xl border border-green-500/30 bg-green-500/5 p-4">
                    <div className="flex items-start gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-green-500/30 bg-green-500/10 text-green-300">
                        <Check
                          size={22}
                        />
                      </div>

                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-bold text-white">
                          {audioFile.name}
                        </p>

                        <p className="mt-1 text-xs text-zinc-500">
                          {(
                            audioFile.size /
                            1024 /
                            1024
                          ).toFixed(2)}{' '}
                          MB
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={removeAudioFile}
                        aria-label="Remove audio file"
                        className="rounded-lg border border-zinc-700 p-2 text-zinc-400 transition hover:border-red-500/50 hover:text-red-300"
                      >
                        <X
                          size={17}
                        />
                      </button>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        fileInputRef.current?.click()
                      }
                      className="mt-4 w-full rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-xs font-bold text-zinc-300 transition hover:border-orange-500/50 hover:text-white"
                    >
                      Replace File
                    </button>
                  </div>
                )}

                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  For the best result, upload a
                  clear recording with minimal
                  background noise.
                </p>
              </section>
            </div>
          </div>

          <div className="border-t border-zinc-800 px-5 py-6 sm:px-8">
            <section className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">
              <div className="mb-5 flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                  <Music2
                    size={21}
                  />
                </div>

                <div>
                  <h2 className="text-lg font-black text-white">
                    Song Information
                  </h2>

                  <p className="text-xs text-zinc-500">
                    Add the title and artist
                  </p>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label
                    htmlFor="song-title"
                    className="mb-2 block text-sm font-semibold text-zinc-300"
                  >
                    Song Title
                  </label>

                  <input
                    id="song-title"
                    type="text"
                    value={songTitle}
                    onChange={(event) => {
                      setSongTitle(
                        event.target.value
                      );

                      resetGeneratedResults();
                    }}
                    placeholder="Enter song title"
                    className="w-full rounded-xl border border-zinc-700 bg-black/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>
                <div>
                  <label
                    htmlFor="artist-name"
                    className="mb-2 block text-sm font-semibold text-zinc-300"
                  >
                    Artist Name
                  </label>

                  <input
                    id="artist-name"
                    type="text"
                    value={artistName}
                    onChange={(event) => {
                      setArtistName(
                        event.target.value
                      );

                      resetGeneratedResults();
                    }}
                    placeholder="Enter artist name"
                    className="w-full rounded-xl border border-zinc-700 bg-black/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                  />
                </div>
              </div>
            </section>
          </div>

          <div className="border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8">
            <section>
              <div className="mb-5 text-center">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                  Choose Your Instrument
                </p>

                <h2 className="mt-2 text-2xl font-black text-white">
                  Which Part Should We Transcribe?
                </h2>

                <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                  Select the main instrument part
                  you want included in your
                  finished tablature PDF.
                </p>
              </div>

              <div className="grid gap-3 sm:grid-cols-3">
                {TRANSCRIPTION_TYPES.map(
                  ({
                    value,
                    title,
                    description,
                    emoji,
                  }) => {
                    const isSelected =
                      selectedType === value;

                    return (
                      <button
                        key={value}
                        type="button"
                        onClick={() => {
                          setSelectedType(value);
                          resetGeneratedResults();
                        }}
                        className={`relative rounded-2xl border p-5 text-left transition ${
                          isSelected
                            ? 'border-orange-500 bg-orange-500/10 shadow-lg shadow-orange-950/20'
                            : 'border-zinc-800 bg-zinc-950/80 hover:border-orange-500/40'
                        }`}
                      >
                        {isSelected && (
                          <div className="absolute right-3 top-3 flex h-7 w-7 items-center justify-center rounded-full bg-orange-500 text-black">
                            <Check
                              size={16}
                              strokeWidth={3}
                            />
                          </div>
                        )}

                        <div className="mb-4 text-3xl">
                          {emoji}
                        </div>

                        <h3 className="text-base font-black text-white">
                          {title}
                        </h3>

                        <p className="mt-2 text-xs leading-5 text-zinc-500">
                          {description}
                        </p>

                        <div
                          className={`mt-4 rounded-xl px-3 py-2 text-center text-xs font-bold ${
                            isSelected
                              ? 'bg-orange-500 text-black'
                              : 'border border-zinc-700 bg-black/40 text-zinc-400'
                          }`}
                        >
                          {isSelected
                            ? 'Selected'
                            : 'Select Part'}
                        </div>
                      </button>
                    );
                  }
                )}
              </div>

              <div className="mt-4 flex items-center justify-center gap-2 rounded-xl border border-zinc-800 bg-zinc-950/60 px-4 py-3 text-center text-xs text-zinc-400">
                <Guitar
                  size={16}
                  className="shrink-0 text-orange-400"
                />

                <span>
                  Selected:{' '}
                  <strong className="text-white">
                    {selectedTypeDetails.title}
                  </strong>
                </span>
              </div>
            </section>
          </div>

          <div className="border-t border-zinc-800 px-5 py-6 sm:px-8">
            <div className="grid gap-4 lg:grid-cols-2">
              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-green-500/30 bg-green-500/10 text-green-300">
                    <ShieldCheck
                      size={21}
                    />
                  </div>

                  <div>
                    <h2 className="text-lg font-black text-white">
                      Copyright Confirmation
                    </h2>

                    <p className="text-xs text-zinc-500">
                      Required before processing
                    </p>
                  </div>
                </div>
                <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-zinc-800 bg-black/40 p-4 transition hover:border-green-500/40">
                  <input
                    type="checkbox"
                    checked={copyrightConfirmed}
                    onChange={(event) => {
                      setCopyrightConfirmed(
                        event.target.checked
                      );

                      resetGeneratedResults();
                    }}
                    className="mt-1 h-5 w-5 shrink-0 accent-orange-500"
                  />

                  <span>
                    <span className="block text-sm font-bold text-white">
                      I confirm I have permission
                      to use this audio.
                    </span>

                    <span className="mt-1 block text-xs leading-5 text-zinc-500">
                      This tool is intended for
                      private educational use,
                      original recordings, or audio
                      you are legally permitted to
                      process.
                    </span>
                  </span>
                </label>

                <div className="mt-4 flex items-start gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-3 text-xs leading-5 text-amber-100/70">
                  <LockKeyhole
                    size={17}
                    className="mt-0.5 shrink-0 text-amber-400"
                  />

                  Uploaded audio is used only to
                  process your private
                  transcription request.
                </div>
              </section>

              <section className="rounded-2xl border border-orange-500/30 bg-gradient-to-b from-orange-500/10 to-zinc-950 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/40 bg-orange-500/15 text-orange-300">
                    <Mail
                      size={21}
                    />
                  </div>

                  <div>
                    <h2 className="text-lg font-black text-white">
                      Delivery Email
                    </h2>

                    <p className="text-xs text-zinc-500">
                      Required for PDF delivery
                    </p>
                  </div>
                </div>

                <label
                  htmlFor="customer-email"
                  className="mb-2 block text-sm font-semibold text-zinc-300"
                >
                  Email Address
                </label>

                <input
                  id="customer-email"
                  type="email"
                  value={customerEmail}
                  onChange={(event) => {
                    setCustomerEmail(
                      event.target.value
                    );

                    resetGeneratedResults();
                  }}
                  placeholder="you@example.com"
                  autoComplete="email"
                  className={`w-full rounded-xl border bg-black/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 ${
                    customerEmail &&
                    !emailIsValid
                      ? 'border-red-500'
                      : 'border-zinc-700 focus:border-orange-500'
                  }`}
                />

                {customerEmail &&
                  !emailIsValid && (
                    <p className="mt-2 text-xs text-red-300">
                      Please enter a valid email
                      address.
                    </p>
                  )}

                <button
                  type="button"
                  onClick={handleGeneratePreview}
                  disabled={
                    !formIsComplete ||
                    isGenerating
                  }
                  className="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-4 text-base font-black text-black shadow-xl shadow-orange-950/30 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {isGenerating ? (
                    <>
                      <Loader2
                        size={21}
                        className="animate-spin"
                      />

                      Generating Preview...
                    </>
                  ) : (
                    <>
                      <Sparkles
                        size={21}
                      />

                      Generate My AI Tab
                    </>
                  )}
                </button>

                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  {PROCESS_STEPS.slice(
                    0,
                    3
                  ).map((step, index) => (
                    <div
                      key={step}
                      className="rounded-xl border border-zinc-800 bg-black/40 px-2 py-3"
                    >
                      <span className="block text-xs font-black text-orange-400">
                        {index + 1}
                      </span>

                      <span className="mt-1 block text-[10px] leading-4 text-zinc-500">
                        {step}
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            {(generationError ||
              statusMessage) && (
              <div
                className={`mt-4 rounded-2xl border px-4 py-3 text-sm leading-6 ${
                  generationError
                    ? 'border-red-500/40 bg-red-500/10 text-red-200'
                    : 'border-green-500/30 bg-green-500/10 text-green-200'
                }`}
              >
                {generationError ||
                  statusMessage}
              </div>
            )}
          </div>
          <div className="border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8">
            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                  <Headphones
                    size={20}
                  />
                </div>

                <h3 className="text-sm font-black text-white">
                  How Audio Is Processed
                </h3>

                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  The selected instrument is
                  separated, analyzed, and
                  converted into readable
                  tablature.
                </p>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl border border-green-500/30 bg-green-500/10 text-green-300">
                  <LockKeyhole
                    size={20}
                  />
                </div>

                <h3 className="text-sm font-black text-white">
                  Private Processing
                </h3>

                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  Your uploaded audio and
                  generated transcription are
                  used only for your private
                  request.
                </p>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-4">
                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl border border-blue-500/30 bg-blue-500/10 text-blue-300">
                  <FileText
                    size={20}
                  />
                </div>

                <h3 className="text-sm font-black text-white">
                  Preview Before Payment
                </h3>

                <p className="mt-2 text-xs leading-5 text-zinc-500">
                  Review your generated tab
                  before opening PayPal and
                  purchasing the finished PDF.
                </p>
              </div>
            </div>
          </div>

          {previewReady && (
            <div
              id="tab-preview"
              className="scroll-mt-6 border-t border-zinc-800 px-5 py-6 sm:px-8"
            >
              <section className="overflow-hidden rounded-2xl border border-orange-500/30 bg-zinc-950/90">
                <div className="flex flex-col gap-3 border-b border-zinc-800 bg-orange-500/5 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.16em] text-orange-400">
                      AI Preview
                    </p>

                    <h2 className="mt-1 text-xl font-black text-white">
                      {songTitle} — {artistName}
                    </h2>

                    <p className="mt-1 text-xs text-zinc-500">
                      {selectedTypeDetails.title}
                    </p>
                  </div>

                  <div className="inline-flex items-center gap-2 self-start rounded-full border border-green-500/30 bg-green-500/10 px-3 py-2 text-xs font-bold text-green-300">
                    <Check
                      size={15}
                    />

                    Preview Ready
                  </div>
                </div>

                <div className="p-5">
                  <div className="overflow-x-auto rounded-2xl border border-zinc-800 bg-black p-4">
                    <pre className="min-h-[260px] whitespace-pre-wrap break-words font-mono text-xs leading-6 text-zinc-200 sm:text-sm">
                      {generatedTab}
                    </pre>
                  </div>

                  <div className="mt-4 flex items-start gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-xs leading-5 text-amber-100/70">
                    <ShieldCheck
                      size={18}
                      className="mt-0.5 shrink-0 text-amber-400"
                    />

                    Review this preview carefully.
AI-generated tablature may
require small corrections for
tuning, timing, or complex
overlapping instruments.
                  </div>
                </div>
              </section>
            </div>
          )}

          {previewReady && (
            <div className="border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8">
              <div className="grid gap-4 lg:grid-cols-2">
                <section className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-blue-500/30 bg-blue-500/10 text-blue-300">
                      <ShieldCheck
                        size={21}
                      />
                    </div>

                    <div>
                      <h2 className="text-lg font-black text-white">
                        Secure PayPal Checkout
                      </h2>

                      <p className="text-xs text-zinc-500">
                        Pay only after reviewing
                        your preview
                      </p>
                    </div>
                  </div>

                  <div className="mb-4 rounded-2xl border border-zinc-800 bg-black/40 p-4">
                    <div className="flex items-center justify-between gap-4">
                      <div>
                        <p className="text-sm font-bold text-white">
                          Finished Tab PDF
                        </p>

                        <p className="mt-1 text-xs text-zinc-500">
                          Printable PDF plus email
                          delivery
                        </p>
                      </div>

                      <p className="text-2xl font-black text-orange-400">
                        $4.99
                      </p>
                    </div>
                  </div>

                  {!paymentCompleted ? (
                    <PayPalCheckoutButton
                      amount="4.99"
                      description={`${songTitle} by ${artistName} — ${selectedTypeDetails.title} Tab PDF`}
                      customerEmail={customerEmail.trim()}
                      songTitle={songTitle.trim()}
                      artistName={artistName.trim()}
                      transcriptionType={selectedType}
                      onApprove={handlePaymentApproved}
                      onCancel={handlePaymentCancelled}
                      onError={handlePaymentError}
                    />
                  ) : (
                    <div className="flex items-center gap-3 rounded-2xl border border-green-500/30 bg-green-500/10 p-4">
                      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-green-500 text-black">
                        <Check
                          size={21}
                          strokeWidth={3}
                        />
                      </div>

                      <div>
                        <p className="text-sm font-black text-green-200">
                          Payment Confirmed
                        </p>

                        <p className="mt-1 text-xs text-green-100/60">
                          Your finished PDF is now
                          unlocked.
                        </p>
                      </div>
                    </div>
                  )}

                  <p className="mt-4 text-center text-[11px] leading-5 text-zinc-600">
                    Payments are processed securely
                    by PayPal. DadRock Tabs does not
                    store your payment details.
                  </p>
                </section>

                <section
                  id="download-section"
                  className="scroll-mt-6 rounded-2xl border border-orange-500/30 bg-gradient-to-b from-orange-500/10 to-zinc-950 p-5"
                >
                  <div className="mb-4 flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/40 bg-orange-500/15 text-orange-300">
                      <Download
                        size={21}
                      />
                    </div>

                    <div>
                      <h2 className="text-lg font-black text-white">
                        Download Your PDF
                      </h2>

                      <p className="text-xs text-zinc-500">
                        Available after payment
                      </p>
                    </div>
                  </div>

                  <div className="rounded-2xl border border-zinc-800 bg-black/40 p-4">
                    <div className="flex items-center gap-3">
                      <FileText
                        size={34}
                        className="shrink-0 text-orange-400"
                      />

                      <div className="min-w-0">
                        <p className="truncate text-sm font-black text-white">
                          {artistName} — {songTitle}
                        </p>

                        <p className="mt-1 text-xs text-zinc-500">
                          {selectedTypeDetails.title}
                          {' • '}
                          Portrait PDF
                        </p>
                      </div>
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={handleDownloadPdf}
                    disabled={
                      !paymentCompleted ||
                      isDownloading
                    }
                    className="mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-orange-500 to-amber-400 px-5 py-4 text-base font-black text-black shadow-xl shadow-orange-950/30 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {isDownloading ? (
                      <>
                        <Loader2
                          size={21}
                          className="animate-spin"
                        />

                        Creating PDF...
                      </>
                    ) : (
                      <>
                        <Download
                          size={21}
                        />

                        Download Finished PDF
                      </>
                    )}
                  </button>

                  <div className="mt-4 flex items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-950/70 p-3 text-xs leading-5 text-zinc-500">
                    <Mail
                      size={17}
                      className="mt-0.5 shrink-0 text-orange-400"
                    />

                    A copy will also be sent to{' '}
                    <strong className="break-all text-zinc-300">
                      {customerEmail}
                    </strong>
                  </div>
                </section>
              </div>
            </div>
          )}
          <div className="border-t border-zinc-800 px-5 py-6 sm:px-8">
            <section className="mx-auto max-w-4xl">
              <div className="mb-5 text-center">
                <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                  Questions
                </p>

                <h2 className="mt-2 text-2xl font-black text-white">
                  Frequently Asked Questions
                </h2>

                <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                  Quick answers about uploads,
                  accuracy, privacy, payment, and
                  PDF delivery.
                </p>
              </div>

              <div className="space-y-3">
                {FAQ_ITEMS.map(
                  ({
                    question,
                    answer,
                  }, index) => {
                    const isOpen =
                      openFaq === index;

                    return (
                      <div
                        key={question}
                        className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950/80"
                      >
                        <button
                          type="button"
                          onClick={() =>
                            setOpenFaq(
                              isOpen
                                ? null
                                : index
                            )
                          }
                          aria-expanded={isOpen}
                          className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                        >
                          <span className="text-sm font-bold text-white sm:text-base">
                            {question}
                          </span>

                          <ChevronDown
                            size={19}
                            className={`shrink-0 text-orange-400 transition-transform ${
                              isOpen
                                ? 'rotate-180'
                                : ''
                            }`}
                          />
                        </button>

                        {isOpen && (
                          <div className="border-t border-zinc-800 px-5 py-4">
                            <p className="text-sm leading-6 text-zinc-400">
                              {answer}
                            </p>
                          </div>
                        )}
                      </div>
                    );
                  }
                )}
              </div>
            </section>
          </div>

          <footer className="border-t border-zinc-800 bg-black/30 px-5 py-6 text-center sm:px-8">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs"
              className="mx-auto h-auto w-full max-w-[230px] object-contain opacity-90"
            />

            <p className="mx-auto mt-3 max-w-xl text-xs leading-5 text-zinc-500">
              AI-generated guitar and bass
              tablature for private educational
              use. Always review generated tabs
              before relying on them.
            </p>

            <div className="mt-4 flex flex-wrap items-center justify-center gap-3 text-xs font-semibold text-zinc-500">
              <Link
                href={getLocalizedPath(
                  '/',
                  currentLanguage
                )}
                className="transition hover:text-orange-400"
              >
                Home
              </Link>

              <span aria-hidden="true">
                •
              </span>

              <Link
                href={getLocalizedPath(
                  '/partners',
                  currentLanguage
                )}
                className="transition hover:text-orange-400"
              >
                Partnership Opportunities
              </Link>

              <span aria-hidden="true">
                •
              </span>

              <a
                href="https://youtube.com/@dadrockytofficial"
                target="_blank"
                rel="noreferrer"
                className="transition hover:text-orange-400"
              >
                YouTube
              </a>
            </div>

            <p className="mt-4 text-[11px] text-zinc-700">
              © {new Date().getFullYear()}{' '}
              DadRock Tabs. All rights reserved.
            </p>
          </footer>
        </div>
      </div>
    </main>
  );
}

export default function AiTabGeneratorPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-[#090909] text-white">
          <div className="flex items-center gap-3 text-sm font-bold text-zinc-400">
            <Loader2
              size={22}
              className="animate-spin text-orange-400"
            />

            Loading AI Tab Generator...
          </div>
        </main>
      }
    >
      <AiTabGeneratorContent />
    </Suspense>
  );
                }

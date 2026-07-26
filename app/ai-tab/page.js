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
  Loader2,
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
    question: 'How accurate will my AI-generated tab be?',
    answer:
      'Accuracy depends on the recording quality, instrument separation, tuning, effects, and complexity of the performance. AI-generated tabs may require small corrections.',
  },
  {
    question: 'What audio files can I upload?',
    answer:
      'You can upload MP3, WAV, M4A, or AAC audio files from your device.',
  },
  {
    question: 'Can I generate guitar and bass tabs?',
    answer:
      'Yes. You can choose lead guitar, rhythm guitar, or bass guitar before generating your transcription.',
  },
  {
    question: 'What happens to my uploaded audio?',
    answer:
      'Your recording is used only to process your private transcription request.',
  },
  {
    question: 'What do I receive after payment?',
    answer:
      'You receive a polished portrait PDF that can be downloaded and emailed to the delivery address you provide.',
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

  const formIsComplete = useMemo(
    () =>
      Boolean(
        songTitle.trim() &&
          artistName.trim() &&
          selectedType &&
          (audioFile || youtubeUrl.trim()) &&
          emailIsValid &&
          copyrightConfirmed
      ),
    [
      songTitle,
      artistName,
      selectedType,
      audioFile,
      youtubeUrl,
      emailIsValid,
      copyrightConfirmed,
    ]
  );

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0] || null;

    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setPaymentCompleted(false);
    setGeneratedTab('');
    setPurchaseOrderId('');

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

    const allowedExtensions =
      /\.(mp3|wav|m4a|aac)$/i;

    const typeIsAllowed =
      allowedTypes.includes(selectedFile.type) ||
      allowedExtensions.test(selectedFile.name);

    if (!typeIsAllowed) {
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
    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setPaymentCompleted(false);
    setGeneratedTab('');
    setPurchaseOrderId('');

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
        'Transcription type must be lead, rhythm, or bass.'
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
        'Analyzing your recording and generating a preview...'
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
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            orderId,
            songTitle: songTitle.trim(),
            artistName: artistName.trim(),
            transcriptionType: selectedType,
            customerEmail:
              customerEmail.trim(),
          }),
        }
      );

      const data = await response.json().catch(
        () => ({})
      );

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

      if (
        paymentStatus &&
        ![
          'COMPLETED',
          'APPROVED',
          'SUCCESS',
        ].includes(
          String(paymentStatus).toUpperCase()
        )
      ) {
        throw new Error(
          'PayPal has not marked this payment as completed.'
        );
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);

      setStatusMessage(
        'Payment confirmed. Your finished PDF is ready to download and will be sent to your delivery email.'
      );

      window.setTimeout(() => {
        document
          .getElementById('download-section')
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

    setStatusMessage(
      'PayPal checkout was cancelled. Your preview is still available.'
    );

    setGenerationError('');
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
      'Creating your polished tab PDF and preparing your email delivery...'
    );

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
            songTitle: songTitle.trim(),
            artistName: artistName.trim(),
            transcriptionType: selectedType,
            customerEmail:
              customerEmail.trim(),
            generatedTab,
            youtubeUrl:
              youtubeUrl.trim() || null,
          }),
        }
      );

      if (!response.ok) {
        const errorData =
          await response.json().catch(
            () => ({})
          );

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
        const data =
          await response.json().catch(
            () => ({})
          );

        throw new Error(
          data.error ||
            data.message ||
            'The server did not return a valid PDF file.'
        );
      }

      const pdfBlob = await response.blob();
      const downloadUrl =
        window.URL.createObjectURL(pdfBlob);

      const safeArtist =
        artistName
          .trim()
          .replace(/[^a-z0-9]+/gi, '-')
          .replace(/^-+|-+$/g, '')
          .toLowerCase() || 'artist';

      const safeTitle =
        songTitle
          .trim()
          .replace(/[^a-z0-9]+/gi, '-')
          .replace(/^-+|-+$/g, '')
          .toLowerCase() || 'song';

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
        `Your PDF has downloaded successfully. A copy is also being sent to ${customerEmail.trim()}.`
      );
    } catch (error) {
      console.error(
        'PDF generation error:',
        error
      );

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'Unable to create your finished PDF.'
      );

      setStatusMessage('');
    } finally {
      setIsDownloading(false);
    }
  };
    return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <div className="mx-auto w-full max-w-6xl px-4 pb-16 pt-4 sm:px-6 lg:px-8">
        <header className="flex items-center justify-between gap-4">
          <Link
            href={getLocalizedPath(
              '/',
              currentLanguage
            )}
            className="inline-flex items-center gap-2 rounded-full border border-zinc-700 bg-zinc-900/80 px-4 py-2 text-sm font-semibold text-zinc-200 transition hover:border-orange-400 hover:text-white"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>

          <LanguageSelector />
        </header>

        <section className="pt-8 text-center sm:pt-10">
          <div className="mx-auto flex max-w-3xl flex-col items-center">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs"
              className="h-auto w-full max-w-[330px] object-contain sm:max-w-[420px]"
            />

            <div className="mt-7 inline-flex items-center gap-2 rounded-full border border-orange-400/40 bg-orange-500/10 px-4 py-2 text-sm font-bold text-orange-300">
              <Sparkles className="h-4 w-4" />
              AI-Powered Guitar and Bass Tabs
            </div>

            <h1 className="mt-5 text-4xl font-black tracking-tight text-white sm:text-5xl lg:text-6xl">
              AI Guitar &amp; Bass
              <span className="block text-orange-400">
                Tab Generator
              </span>
            </h1>

            <p className="mt-5 max-w-2xl text-base leading-7 text-zinc-300 sm:text-lg">
              Upload your audio, choose the instrument
              part you want, and generate a polished
              tablature preview before purchasing your
              downloadable PDF.
            </p>

            <div className="mt-7 grid w-full max-w-3xl gap-3 sm:grid-cols-3">
              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-4">
                <Music2 className="mx-auto h-6 w-6 text-orange-400" />

                <p className="mt-2 font-bold">
                  Guitar &amp; Bass
                </p>

                <p className="mt-1 text-sm text-zinc-400">
                  Lead, rhythm, or bass
                </p>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-4">
                <FileText className="mx-auto h-6 w-6 text-orange-400" />

                <p className="mt-2 font-bold">
                  Polished PDF
                </p>

                <p className="mt-1 text-sm text-zinc-400">
                  Ready to print and practise
                </p>
              </div>

              <div className="rounded-2xl border border-zinc-800 bg-zinc-900/70 p-4">
                <ShieldCheck className="mx-auto h-6 w-6 text-orange-400" />

                <p className="mt-2 font-bold">
                  Secure Checkout
                </p>

                <p className="mt-1 text-sm text-zinc-400">
                  Protected by PayPal
                </p>
              </div>
            </div>
          </div>
        </section>

        <section className="mt-10 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-4 shadow-2xl shadow-black/30 sm:p-6">
          <div className="grid gap-3 sm:grid-cols-5">
            {PROCESS_STEPS.map((step) => (
              <div
                key={step.number}
                className="flex items-center gap-3 rounded-2xl border border-zinc-800 bg-zinc-950/70 p-3 sm:flex-col sm:text-center"
              >
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-orange-500 font-black text-white">
                  {step.number}
                </span>

                <span className="text-sm font-bold text-zinc-200">
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </section>
        <section className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
            <div className="flex items-center gap-3">
              <Youtube className="h-7 w-7 text-red-500" />

              <div>
                <h2 className="text-xl font-bold">
                  YouTube Reference
                </h2>

                <p className="text-sm text-zinc-400">
                  Optional if you are uploading audio.
                </p>
              </div>
            </div>

            <input
              type="url"
              value={youtubeUrl}
              onChange={(e) =>
                setYoutubeUrl(e.target.value)
              }
              placeholder="https://www.youtube.com/watch?v=..."
              className="mt-5 w-full rounded-2xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition focus:border-orange-400"
            />
          </div>

          <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
            <div className="flex items-center gap-3">
              <FileAudio className="h-7 w-7 text-orange-400" />

              <div>
                <h2 className="text-xl font-bold">
                  Upload Audio
                </h2>

                <p className="text-sm text-zinc-400">
                  MP3, WAV, M4A or AAC
                </p>
              </div>
            </div>

            <label className="mt-5 flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-zinc-700 bg-zinc-950 px-6 py-10 transition hover:border-orange-400">
              <Upload className="h-10 w-10 text-orange-400" />

              <span className="mt-4 font-bold">
                Tap to choose an audio file
              </span>

              <span className="mt-1 text-sm text-zinc-500">
                or drag and drop from your computer
              </span>

              <input
                ref={fileInputRef}
                type="file"
                accept=".mp3,.wav,.m4a,.aac,audio/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>

            {audioFile && (
              <div className="mt-5 flex items-center justify-between rounded-2xl border border-green-700 bg-green-900/20 p-4">
                <div>
                  <p className="font-semibold text-green-300">
                    {audioFile.name}
                  </p>

                  <p className="text-sm text-zinc-400">
                    {(audioFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>

                <button
                  type="button"
                  onClick={removeAudioFile}
                  className="rounded-full bg-red-600 p-2 transition hover:bg-red-500"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            )}
          </div>
        </section>
        <section className="mt-6 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
          <div className="flex items-center gap-3">
            <Music2 className="h-7 w-7 text-orange-400" />

            <div>
              <h2 className="text-xl font-bold">
                Choose Your Instrument Part
              </h2>

              <p className="text-sm text-zinc-400">
                Select the part you want the AI to transcribe.
              </p>
            </div>
          </div>

          <div className="mt-5 grid gap-3 md:grid-cols-3">
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
                  className={`rounded-2xl border p-5 text-left transition ${
                    isSelected
                      ? 'border-orange-400 bg-orange-500/15 shadow-lg shadow-orange-950/30'
                      : 'border-zinc-700 bg-zinc-950 hover:border-zinc-500'
                  }`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <span className="text-3xl">
                      {type.emoji}
                    </span>

                    <span
                      className={`flex h-6 w-6 items-center justify-center rounded-full border ${
                        isSelected
                          ? 'border-orange-400 bg-orange-500'
                          : 'border-zinc-600'
                      }`}
                    >
                      {isSelected && (
                        <Check className="h-4 w-4 text-white" />
                      )}
                    </span>
                  </div>

                  <p className="mt-4 font-bold text-white">
                    {type.title}
                  </p>

                  <p className="mt-1 text-sm leading-6 text-zinc-400">
                    {type.description}
                  </p>
                </button>
              );
            })}
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
            <div className="flex items-center gap-3">
              <Music2 className="h-7 w-7 text-orange-400" />

              <div>
                <h2 className="text-xl font-bold">
                  Song Information
                </h2>

                <p className="text-sm text-zinc-400">
                  Add the title and artist for your finished PDF.
                </p>
              </div>
            </div>

            <div className="mt-5 space-y-4">
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
                  onChange={(e) =>
                    setSongTitle(e.target.value)
                  }
                  placeholder="Enter the song title"
                  required
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition focus:border-orange-400"
                />
              </div>

              <div>
                <label
                  htmlFor="artist-name"
                  className="mb-2 block text-sm font-semibold text-zinc-300"
                >
                  Artist
                </label>

                <input
                  id="artist-name"
                  type="text"
                  value={artistName}
                  onChange={(e) =>
                    setArtistName(e.target.value)
                  }
                  placeholder="Enter the artist name"
                  required
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition focus:border-orange-400"
                />
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <div className="flex items-center gap-3">
                <ShieldCheck className="h-7 w-7 text-orange-400" />

                <div>
                  <h2 className="text-xl font-bold">
                    Copyright Confirmation
                  </h2>

                  <p className="text-sm text-zinc-400">
                    Required before transcription.
                  </p>
                </div>
              </div>

              <label className="mt-5 flex cursor-pointer items-start gap-3 rounded-2xl border border-zinc-700 bg-zinc-950 p-4">
                <input
                  type="checkbox"
                  checked={copyrightConfirmed}
                  onChange={(e) =>
                    setCopyrightConfirmed(
                      e.target.checked
                    )
                  }
                  className="mt-1 h-5 w-5 accent-orange-500"
                />

                <span className="text-sm leading-6 text-zinc-300">
                  I confirm that I own this audio, have permission to use it,
                  or am submitting it for lawful personal or educational use.
                </span>
              </label>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <div>
                <h2 className="text-xl font-bold">
                  Delivery Email
                </h2>

                <p className="mt-1 text-sm text-zinc-400">
                  Your finished PDF will also be sent here.
                </p>
              </div>

              <label
                htmlFor="customer-email"
                className="mb-2 mt-5 block text-sm font-semibold text-zinc-300"
              >
                Email Address
              </label>

              <input
                id="customer-email"
                type="email"
                value={customerEmail}
                onChange={(e) =>
                  setCustomerEmail(e.target.value)
                }
                placeholder="you@example.com"
                required
                className="w-full rounded-2xl border border-zinc-700 bg-zinc-950 px-4 py-3 text-white outline-none transition focus:border-orange-400"
              />

              {customerEmail &&
                !emailIsValid && (
                  <p className="mt-2 text-sm text-red-400">
                    Please enter a valid email address.
                  </p>
                )}
            </div>
          </div>
        </section>
        <section className="mt-6 rounded-3xl border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-zinc-900 p-6 sm:p-8">
          <div className="mx-auto max-w-3xl text-center">
            <Sparkles className="mx-auto h-9 w-9 text-orange-400" />

            <h2 className="mt-3 text-2xl font-black">
              Generate Your Tab Preview
            </h2>

            <p className="mt-2 text-sm leading-6 text-zinc-400 sm:text-base">
              We will analyze your audio and create a preview before
              payment. You can review the result before purchasing the
              finished PDF.
            </p>

            <button
              type="button"
              onClick={handleGeneratePreview}
              disabled={!formIsComplete || isGenerating}
              className="mt-6 inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-orange-500 px-6 py-4 text-lg font-black text-white transition hover:bg-orange-400 disabled:cursor-not-allowed disabled:bg-zinc-700 disabled:text-zinc-400 sm:w-auto sm:min-w-[320px]"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Generating Preview...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Generate Preview
                </>
              )}
            </button>

            {!formIsComplete && (
              <p className="mt-3 text-sm text-zinc-500">
                Complete all required fields, confirm copyright, and provide
                either an audio file or YouTube link.
              </p>
            )}

            {statusMessage && (
              <div className="mt-5 rounded-2xl border border-blue-700 bg-blue-950/40 p-4 text-sm text-blue-200">
                {statusMessage}
              </div>
            )}

            {generationError && (
              <div className="mt-5 rounded-2xl border border-red-700 bg-red-950/40 p-4 text-sm text-red-200">
                {generationError}
              </div>
            )}
          </div>
        </section>

        {previewReady && (
          <section
            id="tab-preview"
            className="mt-8 scroll-mt-24 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6 sm:p-8"
          >
            <div className="flex flex-col gap-4 border-b border-zinc-800 pb-5 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <p className="text-sm font-bold uppercase tracking-wider text-orange-400">
                  AI Preview
                </p>

                <h2 className="mt-1 text-2xl font-black">
                  {songTitle} — {artistName}
                </h2>

                <p className="mt-2 text-sm text-zinc-400">
                  {TRANSCRIPTION_TYPES.find(
                    (type) => type.value === selectedType
                  )?.title || 'Tab Transcription'}
                </p>
              </div>

              <div className="rounded-full border border-green-700 bg-green-900/20 px-4 py-2 text-sm font-bold text-green-300">
                Preview Ready
              </div>
            </div>

            <div className="mt-6 overflow-x-auto rounded-2xl border border-zinc-800 bg-black p-4 sm:p-6">
              <pre className="min-w-[700px] whitespace-pre-wrap font-mono text-sm leading-6 text-zinc-200">
                {generatedTab}
              </pre>
            </div>

            <div className="mt-5 rounded-2xl border border-yellow-700/60 bg-yellow-950/20 p-4 text-sm leading-6 text-yellow-200">
              AI-generated tablature may need small corrections depending on
              recording quality, tuning, effects, and performance complexity.
            </div>
          </section>
        )}
        {previewReady && !paymentCompleted && (
          <section className="mt-8 rounded-3xl border border-blue-700/50 bg-blue-950/20 p-6 sm:p-8">
            <div className="mx-auto max-w-3xl text-center">
              <ShieldCheck className="mx-auto h-10 w-10 text-blue-300" />

              <p className="mt-3 text-sm font-bold uppercase tracking-wider text-blue-300">
                Secure Checkout
              </p>

              <h2 className="mt-2 text-2xl font-black">
                Unlock Your Finished PDF
              </h2>

              <p className="mt-3 leading-7 text-zinc-300">
                Review your preview above, then complete payment to receive
                the polished downloadable PDF and email delivery.
              </p>

              <div className="mx-auto mt-6 max-w-md rounded-2xl border border-zinc-700 bg-zinc-950 p-5 text-left">
                <div className="flex items-center justify-between gap-4">
                  <span className="text-zinc-400">
                    Song
                  </span>

                  <span className="text-right font-bold text-white">
                    {songTitle}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between gap-4">
                  <span className="text-zinc-400">
                    Artist
                  </span>

                  <span className="text-right font-bold text-white">
                    {artistName}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between gap-4">
                  <span className="text-zinc-400">
                    Tab Type
                  </span>

                  <span className="text-right font-bold text-white">
                    {TRANSCRIPTION_TYPES.find(
                      (type) => type.value === selectedType
                    )?.title || selectedType}
                  </span>
                </div>

                <div className="mt-3 flex items-center justify-between gap-4">
                  <span className="text-zinc-400">
                    Delivery
                  </span>

                  <span className="break-all text-right font-bold text-white">
                    {customerEmail}
                  </span>
                </div>
              </div>

              <div className="mx-auto mt-6 max-w-md rounded-2xl bg-white p-4">
                <PayPalCheckoutButton
                  songTitle={songTitle.trim()}
                  artistName={artistName.trim()}
                  transcriptionType={selectedType}
                  customerEmail={customerEmail.trim()}
                  onApprove={handlePaymentApproved}
                  onCancel={handlePaymentCancelled}
                  onError={handlePaymentError}
                />
              </div>

              <p className="mt-4 text-xs leading-5 text-zinc-500">
                Payment is processed securely by PayPal. DadRock Tabs does not
                receive or store your card details.
              </p>
            </div>
          </section>
        )}

        {paymentCompleted && (
          <section
            id="download-section"
            className="mt-8 scroll-mt-24 rounded-3xl border border-green-600/60 bg-green-950/20 p-6 sm:p-8"
          >
            <div className="mx-auto max-w-3xl text-center">
              <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-green-600">
                <Check className="h-8 w-8 text-white" />
              </div>

              <p className="mt-4 text-sm font-bold uppercase tracking-wider text-green-300">
                Payment Confirmed
              </p>

              <h2 className="mt-2 text-3xl font-black">
                Your Tab PDF Is Ready
              </h2>

              <p className="mt-3 leading-7 text-zinc-300">
                Download your finished tablature now. A copy will also be sent
                to your delivery email.
              </p>

              <button
                type="button"
                onClick={handleDownloadPdf}
                disabled={isDownloading}
                className="mt-6 inline-flex w-full items-center justify-center gap-3 rounded-2xl bg-green-600 px-6 py-4 text-lg font-black text-white transition hover:bg-green-500 disabled:cursor-not-allowed disabled:bg-zinc-700 disabled:text-zinc-400 sm:w-auto sm:min-w-[320px]"
              >
                {isDownloading ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    Creating PDF...
                  </>
                ) : (
                  <>
                    <Download className="h-5 w-5" />
                    Download Finished PDF
                  </>
                )}
              </button>

              {purchaseOrderId && (
                <p className="mt-4 break-all text-xs text-zinc-500">
                  PayPal Order: {purchaseOrderId}
                </p>
              )}
            </div>
          </section>
        )}
        <section className="mt-10">
          <div className="text-center">
            <p className="text-sm font-bold uppercase tracking-wider text-orange-400">
              Built for Musicians
            </p>

            <h2 className="mt-2 text-3xl font-black sm:text-4xl">
              Everything You Need in One Place
            </h2>

            <p className="mx-auto mt-3 max-w-2xl leading-7 text-zinc-400">
              From audio upload to polished PDF delivery, every step is
              designed to be simple, clear, and easy to use on any device.
            </p>
          </div>

          <div className="mt-7 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <FileAudio className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Flexible Audio Input
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Upload MP3, WAV, M4A, or AAC audio, or provide a YouTube
                reference link.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <Music2 className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Part-Specific Transcription
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Choose lead guitar, rhythm guitar, or bass before the AI begins
                processing.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <Sparkles className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Preview Before Payment
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Review the generated tablature before deciding whether to
                purchase the finished PDF.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <FileText className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Printable PDF
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Receive a polished portrait-format document that is ready to
                print, save, and practise from.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <ShieldCheck className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Secure PayPal Checkout
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Payment is completed through PayPal without DadRock Tabs
                storing your card information.
              </p>
            </div>

            <div className="rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6">
              <Download className="h-8 w-8 text-orange-400" />

              <h3 className="mt-4 text-xl font-bold">
                Download and Email Delivery
              </h3>

              <p className="mt-2 leading-7 text-zinc-400">
                Download your PDF immediately and receive a copy at the email
                address you provide.
              </p>
            </div>
          </div>
        </section>

        <section className="mt-12 rounded-3xl border border-zinc-800 bg-zinc-900/70 p-6 sm:p-8">
          <div className="text-center">
            <p className="text-sm font-bold uppercase tracking-wider text-orange-400">
              Frequently Asked Questions
            </p>

            <h2 className="mt-2 text-3xl font-black">
              Questions About the AI Tab Generator
            </h2>
          </div>

          <div className="mx-auto mt-7 max-w-4xl space-y-3">
            {FAQ_ITEMS.map((item, index) => {
              const isOpen = openFaq === index;

              return (
                <div
                  key={item.question}
                  className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950"
                >
                  <button
                    type="button"
                    onClick={() =>
                      setOpenFaq(isOpen ? null : index)
                    }
                    className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
                  >
                    <span className="font-bold text-white">
                      {item.question}
                    </span>

                    <ChevronDown
                      className={`h-5 w-5 shrink-0 text-orange-400 transition ${
                        isOpen ? 'rotate-180' : ''
                      }`}
                    />
                  </button>

                  {isOpen && (
                    <div className="border-t border-zinc-800 px-5 py-4">
                      <p className="leading-7 text-zinc-400">
                        {item.answer}
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
        <footer className="mt-12 border-t border-zinc-800 pt-8">
          <div className="flex flex-col items-center justify-between gap-5 text-center sm:flex-row sm:text-left">
            <div>
              <p className="font-bold text-white">
                DadRock Tabs
              </p>

              <p className="mt-1 text-sm text-zinc-500">
                Guitar and bass lessons, tools, and tablature for rock musicians.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-3">
              <Link
                href={getLocalizedPath(
                  '/',
                  currentLanguage
                )}
                className="rounded-full border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-300 transition hover:border-orange-400 hover:text-white"
              >
                Home
              </Link>

              <Link
                href={getLocalizedPath(
                  '/tools',
                  currentLanguage
                )}
                className="rounded-full border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-300 transition hover:border-orange-400 hover:text-white"
              >
                Guitar Tools
              </Link>

              <Link
                href={getLocalizedPath(
                  '/partners',
                  currentLanguage
                )}
                className="rounded-full border border-zinc-700 px-4 py-2 text-sm font-semibold text-zinc-300 transition hover:border-orange-400 hover:text-white"
              >
                Partnerships
              </Link>
            </div>
          </div>

          <div className="mt-6 rounded-2xl border border-zinc-800 bg-zinc-900/60 p-4 text-center text-xs leading-5 text-zinc-500">
            AI-generated tablature is intended for personal, educational, and
            permitted use. Results may require manual review and correction.
          </div>

          <p className="mt-6 text-center text-xs text-zinc-600">
            © {new Date().getFullYear()} DadRock Tabs. All rights reserved.
          </p>
        </footer>
      </div>
    </main>
  );
}

export default function AiTabGeneratorPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-screen items-center justify-center bg-zinc-950 text-white">
          <div className="flex items-center gap-3 rounded-2xl border border-zinc-800 bg-zinc-900 px-6 py-4">
            <Loader2 className="h-5 w-5 animate-spin text-orange-400" />

            <span className="font-semibold">
              Loading AI Tab Generator...
            </span>
          </div>
        </main>
      }
    >
      <AiTabGeneratorContent />
    </Suspense>
  );
}

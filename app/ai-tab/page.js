'use client';

import { Suspense, useState } from 'react';
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

import PayPalCheckoutButton from '@/components/PayPalCheckoutButton';

import {
  getAiTabTranslation,
} from '@/lib/aiTabTranslations';

function getLocalizedPath(path, lang) {
  if (!lang || lang === 'en') {
    return path;
  }

  return `/${lang}${path}`;
}

const LOGO_URL = '/dadrock-logo.png';

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

  const [
    responsibilityAccepted,
    setResponsibilityAccepted,
  ] = useState(false);

  const [customerEmail, setCustomerEmail] =
    useState('');

  const [isGenerating, setIsGenerating] =
    useState(false);

  const [previewReady, setPreviewReady] =
    useState(false);

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

  const [generatedTab, setGeneratedTab] =
    useState('');

  const [
    generationError,
    setGenerationError,
  ] = useState('');

  const [
    statusMessage,
    setStatusMessage,
  ] = useState('');

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setAudioFile(selectedFile);
    setGenerationError('');
    setStatusMessage('');
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
    setGenerationError('');
    setStatusMessage('');
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const droppedFile =
      event.dataTransfer.files?.[0];

    if (!droppedFile) {
      return;
    }

    setAudioFile(droppedFile);
    setGenerationError('');
    setStatusMessage('');
    setPreviewReady(false);
    setGeneratedTab('');
    setPaymentCompleted(false);
    setPurchaseOrderId('');
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

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
      setStatusMessage(
        t.selectRequirements ||
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
            artist: artistName.trim(),
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

      const data = await response.json();

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
            orderId: purchaseOrderId,
            song: songTitle.trim(),
            artist: artistName.trim(),
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
            data.error || errorMessage;
        } catch {
          // Keep the default message.
        }

        throw new Error(errorMessage);
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

      downloadLink.href = downloadUrl;
      downloadLink.download = fileName;

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
    const handlePaymentApproved = async (
    orderId
  ) => {
    if (!orderId) {
      setGenerationError(
        'The PayPal order could not be verified.'
      );

      return;
    }

    setIsCapturingPayment(true);
    setGenerationError('');
    setStatusMessage('');

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
            artist: artistName.trim(),
            transcriptionType:
              selectedType,
            customerEmail:
              customerEmail.trim(),
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.error ||
            'The PayPal payment could not be completed.'
        );
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);

      setStatusMessage(
        t.paymentSuccessful ||
          'Payment successful! Your polished tab PDF is ready to download.'
      );
    } catch (error) {
      setPaymentCompleted(false);
      setPurchaseOrderId('');

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'The PayPal payment could not be completed.'
      );
    } finally {
      setIsCapturingPayment(false);
    }
  };

  const handlePaymentCancelled = () => {
    setGenerationError('');
    setStatusMessage(
      t.paymentCancelled ||
        'Payment was cancelled. You have not been charged.'
    );
  };

  const handlePaymentError = () => {
    setPaymentCompleted(false);
    setPurchaseOrderId('');

    setGenerationError(
      t.paymentError ||
        'PayPal encountered an error. Please try again.'
    );
  };

  const handleStartOver = () => {
    setSongTitle('');
    setArtistName('');
    setYoutubeUrl('');
    setSelectedType('');
    setAudioFile(null);
    setCopyrightConfirmed(false);
    setCustomerEmail('');
    setGeneratedTab('');
    setPreviewReady(false);
    setPaymentCompleted(false);
    setPurchaseOrderId('');
    setGenerationError('');
    setStatusMessage('');

    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }

    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };

  return (
    <main className="min-h-screen bg-[#070707] text-white">
          <div className="mx-auto flex w-full max-w-7xl flex-col gap-12 px-6 py-12 lg:px-8">
        <div className="flex justify-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 rounded-full border border-zinc-700 bg-zinc-900/80 px-5 py-2 text-sm font-semibold text-zinc-200 transition hover:border-orange-400 hover:text-white"
          >
            ← {t.backToHome || 'Back to Home'}
          </Link>
        </div>

        <header className="text-center">
          <img
            src="/dadrockmetal.png"
            alt="DadRock Tabs"
            className="mx-auto mb-8 w-full max-w-lg"
          />

          <div className="mx-auto max-w-4xl rounded-3xl border border-orange-500/30 bg-gradient-to-br from-orange-500/15 via-orange-500/5 to-transparent p-8 shadow-2xl">
            <h1 className="text-4xl font-black tracking-tight text-orange-400 sm:text-6xl">
              🎸 AI Guitar & Bass Tab Generator
            </h1>

            <p className="mt-6 text-lg leading-8 text-zinc-300">
              {t.aiGeneratorDescription ||
                'Upload an audio file or provide a YouTube link and generate a professional AI guitar or bass tablature preview. Purchase the polished PDF after previewing your results.'}
            </p>
          </div>
        </header>

        <section className="grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
                        <div className="rounded-3xl border border-zinc-800 bg-zinc-950/80 p-6 shadow-2xl sm:p-8">
            <div className="mb-8">
              <p className="text-sm font-bold uppercase tracking-[0.25em] text-orange-400">
                Step 1
              </p>

              <h2 className="mt-2 text-3xl font-black text-white">
                Tell us about the song
              </h2>

              <p className="mt-3 leading-7 text-zinc-400">
                Add the song details and choose the instrument
                you want transcribed.
              </p>
            </div>

            <div className="space-y-6">
              <div>
                <label
                  htmlFor="song-title"
                  className="mb-2 block text-sm font-bold text-zinc-200"
                >
                  Song title
                </label>

                <input
                  id="song-title"
                  type="text"
                  value={songTitle}
                  onChange={(event) =>
                    setSongTitle(
                      event.target.value
                    )
                  }
                  placeholder="Enter the song title"
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-900 px-4 py-4 text-white outline-none transition placeholder:text-zinc-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20"
                />
              </div>

              <div>
                <label
                  htmlFor="artist-name"
                  className="mb-2 block text-sm font-bold text-zinc-200"
                >
                  Artist or band
                </label>

                <input
                  id="artist-name"
                  type="text"
                  value={artistName}
                  onChange={(event) =>
                    setArtistName(
                      event.target.value
                    )
                  }
                  placeholder="Enter the artist or band"
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-900 px-4 py-4 text-white outline-none transition placeholder:text-zinc-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20"
                />
              </div>

              <div>
                <label
                  htmlFor="youtube-url"
                  className="mb-2 block text-sm font-bold text-zinc-200"
                >
                  YouTube link
                  <span className="ml-2 font-normal text-zinc-500">
                    Optional
                  </span>
                </label>

                <input
                  id="youtube-url"
                  type="url"
                  value={youtubeUrl}
                  onChange={(event) =>
                    setYoutubeUrl(
                      event.target.value
                    )
                  }
                  placeholder="https://youtube.com/watch?v=..."
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-900 px-4 py-4 text-white outline-none transition placeholder:text-zinc-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-bold text-zinc-200">
                  Instrument
                </label>

                <div className="grid grid-cols-2 gap-4">
                  {TRANSCRIPTION_TYPES.map(
                    (type) => (
                      <button
                        key={type.value}
                        type="button"
                        onClick={() =>
                          setSelectedType(
                            type.value
                          )
                        }
                        className={`rounded-2xl border px-4 py-4 text-left transition ${
                          selectedType ===
                          type.value
                            ? 'border-orange-400 bg-orange-500/20 text-white'
                            : 'border-zinc-700 bg-zinc-900 text-zinc-300 hover:border-orange-500'
                        }`}
                      >
                        <div className="text-lg font-bold">
                          {type.label}
                        </div>

                        <div className="mt-1 text-sm text-zinc-400">
                          {type.description}
                        </div>
                      </button>
                    )
                  )}
                </div>
              </div>

              <div>
                <label
                  htmlFor="audio-file"
                  className="mb-2 block text-sm font-bold text-zinc-200"
                >
                  Upload audio file
                </label>

                <input
                  ref={fileInputRef}
                  id="audio-file"
                  type="file"
                  accept="audio/*"
                  onChange={(event) =>
                    setAudioFile(
                      event.target.files?.[0] ||
                        null
                    )
                  }
                  className="block w-full rounded-2xl border border-dashed border-zinc-600 bg-zinc-900 px-4 py-4 text-sm text-zinc-300 file:mr-4 file:rounded-full file:border-0 file:bg-orange-500 file:px-4 file:py-2 file:font-semibold file:text-white hover:border-orange-400"
                />

                {audioFile && (
                  <p className="mt-3 text-sm text-emerald-400">
                    ✓ {audioFile.name}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="customer-email"
                  className="mb-2 block text-sm font-bold text-zinc-200"
                >
                  Email address
                </label>

                <input
                  id="customer-email"
                  type="email"
                  value={customerEmail}
                  onChange={(event) =>
                    setCustomerEmail(
                      event.target.value
                    )
                  }
                  placeholder="you@example.com"
                  className="w-full rounded-2xl border border-zinc-700 bg-zinc-900 px-4 py-4 text-white outline-none transition placeholder:text-zinc-500 focus:border-orange-400 focus:ring-2 focus:ring-orange-400/20"
                />
              </div>
              <label className="flex cursor-pointer items-start gap-3 rounded-2xl border border-zinc-800 bg-zinc-900/70 p-4">
                <input
                  type="checkbox"
                  checked={copyrightConfirmed}
                  onChange={(event) =>
                    setCopyrightConfirmed(
                      event.target.checked
                    )
                  }
                  className="mt-1 h-5 w-5 rounded border-zinc-600 bg-zinc-800 text-orange-500 focus:ring-orange-400"
                />

                <span className="text-sm leading-6 text-zinc-300">
                  I confirm that I own the audio or have permission
                  to use it for transcription, and that this request
                  does not violate copyright law.
                </span>
              </label>

              {statusMessage && (
                <div className="rounded-2xl border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-300">
                  {statusMessage}
                </div>
              )}

              {generationError && (
                <div className="rounded-2xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
                  {generationError}
                </div>
              )}

              <button
                type="button"
                onClick={handleGeneratePreview}
                disabled={!formIsComplete || isGenerating}
                className="inline-flex w-full items-center justify-center rounded-2xl bg-orange-500 px-6 py-4 text-lg font-black text-white transition hover:bg-orange-400 disabled:cursor-not-allowed disabled:opacity-40"
              >
                {isGenerating
                  ? 'Generating preview...'
                  : 'Generate AI Tab Preview'}
              </button>
            </div>
          </div>

          <div className="rounded-3xl border border-zinc-800 bg-zinc-950/80 p-6 shadow-2xl sm:p-8">
            <div className="mb-8">
              <p className="text-sm font-bold uppercase tracking-[0.25em] text-orange-400">
                Step 2
              </p>

              <h2 className="mt-2 text-3xl font-black text-white">
                Preview and download
              </h2>

              <p className="mt-3 leading-7 text-zinc-400">
                Review the generated tablature before purchasing
                the polished PDF.
              </p>
            </div>
            {!previewReady ? (
              <div className="flex min-h-[420px] items-center justify-center rounded-3xl border border-dashed border-zinc-700 bg-zinc-900/50 p-8 text-center">
                <div>
                  <div className="mb-4 text-6xl">🎸</div>

                  <h3 className="text-2xl font-bold text-white">
                    AI Tab Preview
                  </h3>

                  <p className="mt-4 max-w-md text-zinc-400">
                    Your generated tablature preview will appear
                    here after you complete the form and click
                    <strong> Generate AI Tab Preview</strong>.
                  </p>
                </div>
              </div>
            ) : (
              <>
                <div className="rounded-3xl border border-orange-500/30 bg-zinc-900 p-6">
                  <div className="mb-4 flex items-center justify-between">
                    <h3 className="text-xl font-bold text-orange-400">
                      Preview
                    </h3>

                    <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-bold text-emerald-300">
                      READY
                    </span>
                  </div>

                  <pre className="overflow-x-auto whitespace-pre-wrap rounded-2xl bg-black/40 p-4 font-mono text-sm leading-6 text-zinc-200">
                    {generatedTab}
                  </pre>
                </div>

                {!paymentCompleted ? (
                  <div className="mt-6 rounded-3xl border border-orange-500/30 bg-orange-500/10 p-6">
                    <h3 className="text-2xl font-black text-white">
                      Unlock the polished PDF
                    </h3>

                    <p className="mt-3 text-zinc-300">
                      Complete your secure PayPal payment to
                      download the professionally formatted,
                      print-ready PDF.
                    </p>

                    <div className="mt-6">
                      <PayPalButtons
                        createOrder={createPayPalOrder}
                        onApprove={(data) =>
                          handlePaymentApproved(
                            data.orderID
                          )
                        }
                        onCancel={
                          handlePaymentCancelled
                        }
                        onError={
                          handlePaymentError
                        }
                        disabled={
                          isCapturingPayment
                        }
                      />
                    </div>
                  </div>
                                 ) : (
                  <div className="mt-6 rounded-3xl border border-emerald-500/30 bg-emerald-500/10 p-6">
                    <div className="mb-4 flex items-center gap-3">
                      <span className="text-3xl">✅</span>

                      <div>
                        <h3 className="text-2xl font-black text-white">
                          Payment Complete
                        </h3>

                        <p className="text-emerald-300">
                          Your polished PDF is ready!
                        </p>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={handleDownloadPdf}
                      disabled={isDownloading}
                      className="w-full rounded-2xl bg-emerald-500 px-6 py-4 text-lg font-black text-white transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-40"
                    >
                      {isDownloading
                        ? 'Preparing PDF...'
                        : '⬇ Download Polished PDF'}
                    </button>

                    <button
                      type="button"
                      onClick={handleStartOver}
                      className="mt-4 w-full rounded-2xl border border-zinc-700 bg-zinc-900 px-6 py-4 font-bold text-zinc-200 transition hover:border-orange-400 hover:text-white"
                    >
                      Generate Another Tab
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </section>

        <section className="rounded-3xl border border-orange-500/20 bg-gradient-to-br from-orange-500/10 via-transparent to-transparent p-8 text-center">
          <h2 className="text-3xl font-black text-white">
            Powered by AI
          </h2>

          <p className="mx-auto mt-4 max-w-3xl text-lg leading-8 text-zinc-300">
            DadRock Tabs uses advanced AI transcription technology
            to create high-quality guitar and bass tablature from
            your recordings. Preview your transcription first,
            then purchase a professionally formatted PDF for
            practice, printing, and offline use.
          </p>
        </section>
      </div>
    </main>
  );
}

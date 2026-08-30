'use client';

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { upload } from '@vercel/blob/client';
import Link from 'next/link';
import {
  ArrowLeft,
  CheckCircle2,
  Download,
  FileAudio,
  Guitar,
  Headphones,
  Loader2,
  Mail,
  Music2,
  Upload,
} from 'lucide-react';

import BTSPayPalCheckoutButton from '@/components/BTSPayPalCheckoutButton';
import LanguageSelector from '@/components/LanguageSelector';

const LOGO_URL = '/dadrock-tabs-bts-logo.png';
const PRICE = '1.00';
const MAX_AUDIO_SIZE_BYTES = 50 * 1024 * 1024;

const REMOVAL_OPTIONS = [
  {
    value: 'guitar',
    title: 'Remove Guitars',
    description:
      'Keep vocals, drums, bass, piano and other backing elements.',
    emoji: '🎸',
  },
  {
    value: 'bass',
    title: 'Remove Bass',
    description:
      'Keep guitars and the rest of the mix while removing the bass stem.',
    emoji: '🎵',
  },
  {
    value: 'guitar-bass',
    title: 'Remove Guitars + Bass',
    description:
      'Create a rhythm-section practice track without guitar or bass stems.',
    emoji: '🔥',
  },
];

function isValidEmail(value) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    String(value || '').trim()
  );
}

function fallbackDownloadName(removalMode) {
  if (removalMode === 'guitar-bass') {
    return 'dadrock-backing-track-no-guitars-no-bass.mp3';
  }

  if (removalMode === 'guitar') {
    return 'dadrock-backing-track-no-guitars.mp3';
  }

  return 'dadrock-backing-track-no-bass.mp3';
}

export default function BackingTrackStudioPage() {
  const fileInputRef = useRef(null);

  const [customerEmail, setCustomerEmail] =
    useState('');
  const [audioFile, setAudioFile] =
    useState(null);
  const [removalMode, setRemovalMode] =
    useState('guitar');
  const [copyrightConfirmed, setCopyrightConfirmed] =
    useState(false);

  const [uploadedAudio, setUploadedAudio] =
    useState(null);
  const [isUploading, setIsUploading] =
    useState(false);
  const [isProcessing, setIsProcessing] =
    useState(false);
  const [paymentCompleted, setPaymentCompleted] =
    useState(false);
  const [statusMessage, setStatusMessage] =
    useState('');
  const [errorMessage, setErrorMessage] =
    useState('');
  const [downloadUrl, setDownloadUrl] =
    useState('');
  const [downloadName, setDownloadName] =
    useState('');

  const emailIsValid = useMemo(
    () => isValidEmail(customerEmail),
    [customerEmail]
  );

  const selectedRemoval = useMemo(
    () =>
      REMOVAL_OPTIONS.find(
        (option) => option.value === removalMode
      ) || REMOVAL_OPTIONS[0],
    [removalMode]
  );

  const formIsComplete = Boolean(
    audioFile &&
      emailIsValid &&
      copyrightConfirmed &&
      removalMode
  );

  const formLocked = Boolean(
    uploadedAudio ||
      isUploading ||
      isProcessing ||
      paymentCompleted
  );

  useEffect(() => {
    return () => {
      if (downloadUrl?.startsWith('blob:')) {
        window.URL.revokeObjectURL(downloadUrl);
      }
    };
  }, [downloadUrl]);

  const clearResult = useCallback(() => {
    if (downloadUrl?.startsWith('blob:')) {
      window.URL.revokeObjectURL(downloadUrl);
    }

    setDownloadUrl('');
    setDownloadName('');
    setErrorMessage('');
    setStatusMessage('');
  }, [downloadUrl]);

  const handleFileChange = (event) => {
    const selectedFile =
      event.target.files?.[0] || null;

    clearResult();
    setUploadedAudio(null);
    setPaymentCompleted(false);

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
      'audio/x-m4a',
      'audio/aac',
    ];

    const extensionIsAllowed =
      /\.(mp3|wav|m4a|aac)$/i.test(
        selectedFile.name
      );

    if (
      !allowedTypes.includes(selectedFile.type) &&
      !extensionIsAllowed
    ) {
      setAudioFile(null);
      setErrorMessage(
        'Please choose an MP3, WAV, M4A, or AAC audio file.'
      );

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    if (selectedFile.size > MAX_AUDIO_SIZE_BYTES) {
      setAudioFile(null);
      setErrorMessage(
        'Please choose an audio file smaller than 50 MB.'
      );

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      return;
    }

    setAudioFile(selectedFile);
  };

  const prepareCheckout = async () => {
    setErrorMessage('');

    if (!audioFile) {
      setErrorMessage(
        'Please choose an audio file first.'
      );
      return;
    }

    if (!emailIsValid) {
      setErrorMessage(
        'Please enter a valid email address.'
      );
      return;
    }

    if (!copyrightConfirmed) {
      setErrorMessage(
        'Please confirm that you have the right to process this audio.'
      );
      return;
    }

    setIsUploading(true);
    setStatusMessage(
      'Uploading your audio securely...'
    );

    try {
      const safeFileName = audioFile.name
        .replace(/[^a-zA-Z0-9._-]/g, '-')
        .replace(/-+/g, '-')
        .slice(0, 120);

      const blob = await upload(
        `bts-audio/${Date.now()}-${safeFileName}`,
        audioFile,
        {
          access: 'private',
          handleUploadUrl:
            '/api/bts/audio-upload',
          clientPayload: JSON.stringify({
            removalMode,
            customerEmail:
              customerEmail.trim(),
            copyrightConfirmed,
          }),
        }
      );

      if (!blob?.url || !blob?.pathname) {
        throw new Error(
          'The upload did not return a valid audio reference.'
        );
      }

      setUploadedAudio({
        url: blob.url,
        pathname: blob.pathname,
      });
      setStatusMessage(
        'Upload complete. Complete the $1.00 sandbox checkout to generate your backing track.'
      );
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : 'Unable to upload the audio.'
      );
      setStatusMessage('');
    } finally {
      setIsUploading(false);
    }
  };

  const handlePaymentCompleted = useCallback(
    async ({ orderId, jobToken }) => {
      if (!uploadedAudio) {
        setErrorMessage(
          'The uploaded audio reference is missing.'
        );
        return;
      }

      setPaymentCompleted(true);
      setIsProcessing(true);
      setErrorMessage('');
      setStatusMessage(
        'Payment verified. Separating stems and building your backing track...'
      );

      try {
        const response = await fetch(
          '/api/bts/process',
          {
            method: 'POST',
            headers: {
              'Content-Type':
                'application/json',
            },
            body: JSON.stringify({
              orderId,
              jobToken,
              customerEmail:
                customerEmail.trim(),
              removalMode,
              audioUrl: uploadedAudio.url,
              pathname:
                uploadedAudio.pathname,
            }),
          }
        );

        if (!response.ok) {
          const data = await response
            .json()
            .catch(() => ({}));

          throw new Error(
            data.error ||
              'The backing track could not be generated.'
          );
        }

        const trackBlob = await response.blob();

        if (!trackBlob.size) {
          throw new Error(
            'The backing-track response was empty.'
          );
        }

        const disposition =
          response.headers.get(
            'content-disposition'
          ) || '';

        const filenameMatch =
          disposition.match(
            /filename="?([^";]+)"?/i
          );

        const nextDownloadName =
          filenameMatch?.[1] ||
          fallbackDownloadName(removalMode);

        const objectUrl =
          window.URL.createObjectURL(trackBlob);

        setDownloadUrl((previous) => {
          if (previous?.startsWith('blob:')) {
            window.URL.revokeObjectURL(previous);
          }
          return objectUrl;
        });
        setDownloadName(nextDownloadName);
        setStatusMessage(
          'Your backing track is ready.'
        );
      } catch (error) {
        setErrorMessage(
          error instanceof Error
            ? error.message
            : 'Unable to generate the backing track.'
        );
        setStatusMessage('');
      } finally {
        setIsProcessing(false);
      }
    },
    [
      customerEmail,
      removalMode,
      uploadedAudio,
    ]
  );

  const handlePaymentCancelled = useCallback(() => {
    setErrorMessage(
      'Checkout was cancelled. You have not been charged.'
    );
  }, []);

  const handlePaymentError = useCallback((error) => {
    setErrorMessage(
      error instanceof Error
        ? error.message
        : 'PayPal sandbox checkout could not be completed.'
    );
  }, []);

  return (
    <main className="min-h-screen bg-zinc-950 text-white">
      <div className="mx-auto w-full max-w-5xl px-4 py-8 sm:px-6 sm:py-12">
        <div className="mb-6 flex items-center justify-between gap-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-400 transition hover:text-orange-400"
          >
            <ArrowLeft className="h-4 w-4" />
            DadRock Tabs
          </Link>

          <LanguageSelector />
        </div>

        <section className="overflow-hidden rounded-3xl border border-orange-500/25 bg-zinc-900/80 shadow-2xl shadow-orange-950/20">
          <div className="border-b border-zinc-800 bg-black/30 px-5 py-7 text-center sm:px-8">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs Backing Track Studio"
              className="mx-auto h-auto w-full max-w-xl"
            />

            <h1 className="mt-6 text-3xl font-black tracking-tight sm:text-4xl">
              Backing Track Studio
            </h1>
            <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base">
              Upload your audio, choose what you want removed, and create a practice-ready backing track using AI stem separation.
            </p>
          </div>

          <div className="grid gap-6 p-5 sm:p-8 lg:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-6">
              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="rounded-xl bg-orange-500/10 p-2 text-orange-400">
                    <FileAudio className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="font-bold">1. Upload your audio</h2>
                    <p className="text-xs text-zinc-500">
                      MP3, WAV, M4A or AAC · maximum 50 MB
                    </p>
                  </div>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".mp3,.wav,.m4a,.aac,audio/mpeg,audio/wav,audio/mp4,audio/aac"
                  onChange={handleFileChange}
                  disabled={formLocked}
                  className="block w-full rounded-xl border border-zinc-700 bg-zinc-900 p-3 text-sm text-zinc-300 file:mr-4 file:rounded-lg file:border-0 file:bg-orange-500 file:px-4 file:py-2 file:font-bold file:text-black disabled:opacity-60"
                />

                {audioFile && (
                  <div className="mt-3 flex items-center gap-2 rounded-xl border border-green-500/20 bg-green-500/5 p-3 text-sm text-green-300">
                    <CheckCircle2 className="h-4 w-4 shrink-0" />
                    <span className="truncate">{audioFile.name}</span>
                  </div>
                )}
              </section>

              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="rounded-xl bg-orange-500/10 p-2 text-orange-400">
                    <Guitar className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="font-bold">2. Choose what to remove</h2>
                    <p className="text-xs text-zinc-500">
                      One separation run creates the stems needed for your selected mix.
                    </p>
                  </div>
                </div>

                <div className="grid gap-3">
                  {REMOVAL_OPTIONS.map((option) => {
                    const selected =
                      option.value === removalMode;

                    return (
                      <button
                        key={option.value}
                        type="button"
                        disabled={formLocked}
                        onClick={() =>
                          setRemovalMode(option.value)
                        }
                        className={`rounded-xl border p-4 text-left transition disabled:cursor-not-allowed disabled:opacity-60 ${
                          selected
                            ? 'border-orange-500 bg-orange-500/10'
                            : 'border-zinc-800 bg-zinc-900 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">{option.emoji}</span>
                          <div>
                            <p className="font-bold text-white">
                              {option.title}
                            </p>
                            <p className="mt-1 text-xs leading-5 text-zinc-400">
                              {option.description}
                            </p>
                          </div>
                        </div>
                      </button>
                    );
                  })}
                </div>
              </section>

              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5">
                <div className="mb-4 flex items-center gap-3">
                  <div className="rounded-xl bg-orange-500/10 p-2 text-orange-400">
                    <Mail className="h-5 w-5" />
                  </div>
                  <div>
                    <h2 className="font-bold">3. Your email</h2>
                    <p className="text-xs text-zinc-500">
                      Uses the same email-format verification as AI Tab.
                    </p>
                  </div>
                </div>

                <input
                  type="email"
                  value={customerEmail}
                  disabled={formLocked}
                  onChange={(event) =>
                    setCustomerEmail(event.target.value)
                  }
                  placeholder="you@example.com"
                  className="w-full rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-3 text-sm outline-none transition placeholder:text-zinc-600 focus:border-orange-500 disabled:opacity-60"
                />

                {customerEmail && !emailIsValid && (
                  <p className="mt-2 text-xs text-red-300">
                    Please enter a valid email address.
                  </p>
                )}

                <label className="mt-4 flex cursor-pointer items-start gap-3 rounded-xl border border-zinc-800 bg-zinc-900/70 p-3 text-xs leading-5 text-zinc-400">
                  <input
                    type="checkbox"
                    checked={copyrightConfirmed}
                    disabled={formLocked}
                    onChange={(event) =>
                      setCopyrightConfirmed(
                        event.target.checked
                      )
                    }
                    className="mt-1 h-4 w-4 accent-orange-500"
                  />
                  <span>
                    I confirm that I own this audio or have permission to process it and create a backing track from it.
                  </span>
                </label>
              </section>
            </div>

            <aside className="space-y-5">
              <section className="rounded-2xl border border-orange-500/25 bg-gradient-to-b from-orange-500/10 to-zinc-950 p-5">
                <div className="flex items-center gap-3">
                  <Music2 className="h-6 w-6 text-orange-400" />
                  <div>
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-orange-300">
                      Your backing track
                    </p>
                    <p className="font-black">
                      {selectedRemoval.title}
                    </p>
                  </div>
                </div>

                <div className="mt-5 rounded-xl border border-zinc-800 bg-black/30 p-4">
                  <div className="flex items-end justify-between gap-3">
                    <div>
                      <p className="text-xs text-zinc-500">
                        Sandbox test price
                      </p>
                      <p className="text-3xl font-black text-white">
                        ${PRICE}
                      </p>
                    </div>
                    <p className="pb-1 text-xs font-semibold text-zinc-500">
                      USD · one track
                    </p>
                  </div>
                </div>

                {!uploadedAudio && (
                  <button
                    type="button"
                    disabled={!formIsComplete || isUploading}
                    onClick={prepareCheckout}
                    className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-orange-500 px-4 py-3 font-black text-black transition hover:bg-orange-400 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {isUploading ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        Uploading audio…
                      </>
                    ) : (
                      <>
                        <Upload className="h-5 w-5" />
                        Continue to $1 Checkout
                      </>
                    )}
                  </button>
                )}

                {uploadedAudio && !paymentCompleted && (
                  <div className="mt-5">
                    <BTSPayPalCheckoutButton
                      customerEmail={customerEmail.trim()}
                      removalMode={removalMode}
                      pathname={uploadedAudio.pathname}
                      onPaymentCompleted={
                        handlePaymentCompleted
                      }
                      onPaymentCancelled={
                        handlePaymentCancelled
                      }
                      onPaymentError={
                        handlePaymentError
                      }
                    />
                  </div>
                )}

                {isProcessing && (
                  <div className="mt-5 rounded-xl border border-orange-500/30 bg-orange-500/10 p-4 text-center">
                    <Loader2 className="mx-auto h-7 w-7 animate-spin text-orange-400" />
                    <p className="mt-3 font-bold text-orange-200">
                      Building your backing track…
                    </p>
                    <p className="mt-1 text-xs leading-5 text-zinc-400">
                      Stem separation is the slowest step. Keep this page open while your audio is processed.
                    </p>
                  </div>
                )}

                {downloadUrl && (
                  <div className="mt-5 rounded-xl border border-green-500/30 bg-green-500/10 p-4">
                    <div className="flex items-center gap-2 font-bold text-green-300">
                      <CheckCircle2 className="h-5 w-5" />
                      Backing track ready
                    </div>

                    <audio
                      controls
                      src={downloadUrl}
                      className="mt-4 w-full"
                    />

                    <a
                      href={downloadUrl}
                      download={downloadName}
                      className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-green-500 px-4 py-3 font-black text-black transition hover:bg-green-400"
                    >
                      <Download className="h-5 w-5" />
                      Download MP3
                    </a>
                  </div>
                )}
              </section>

              <section className="rounded-2xl border border-zinc-800 bg-zinc-950/70 p-5 text-sm text-zinc-400">
                <div className="flex items-start gap-3">
                  <Headphones className="mt-0.5 h-5 w-5 shrink-0 text-orange-400" />
                  <div>
                    <p className="font-bold text-white">
                      What the AI removes
                    </p>
                    <p className="mt-1 text-xs leading-5">
                      BTS uses six-source waveform separation to rebuild the mix without the guitar or bass stems you select. Because instruments can overlap inside a mastered recording, some bleed or separation artifacts may remain in complex mixes.
                    </p>
                  </div>
                </div>
              </section>

              {(statusMessage || errorMessage) && (
                <section
                  className={`rounded-2xl border p-4 text-sm ${
                    errorMessage
                      ? 'border-red-500/30 bg-red-500/10 text-red-200'
                      : 'border-blue-500/30 bg-blue-500/10 text-blue-200'
                  }`}
                >
                  {errorMessage || statusMessage}
                </section>
              )}
            </aside>
          </div>

          <section
            aria-labelledby="bts-seo-heading"
            className="border-t border-zinc-800 bg-black/20 px-5 py-7 sm:px-8"
          >
            <div className="mx-auto max-w-3xl text-center">
              <h2
                id="bts-seo-heading"
                className="text-xl font-black text-white sm:text-2xl"
              >
                AI Guitar and Bass Backing Track Maker
              </h2>
              <p className="mt-3 text-sm leading-7 text-zinc-400 sm:text-base">
                DadRock Tabs Backing Track Studio is an online AI backing track maker for guitarists, bass players, singers, and musicians who want custom practice tracks from audio they have the right to use. Upload an MP3, WAV, M4A, or AAC file, then remove guitar, remove bass, or remove both guitar and bass with six-source AI stem separation and download the rebuilt mix as an MP3. Use it to practice riffs and solos, rehearse bass lines, play along with classic rock, hard rock, metal, blues, and other music, or hear the rest of an arrangement more clearly while learning a part.
              </p>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

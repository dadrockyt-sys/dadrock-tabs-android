'use client';

import {
  Suspense,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

import { upload } from '@vercel/blob/client';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

import {
  ArrowLeft,
  ArrowRight,
  AlertCircle,
  Check,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  Download,
  FileAudio,
  FileText,
  Guitar,
  Headphones,
  Home,
  Loader2,
  Lock,
  LockKeyhole,
  Mail,
  Music,
  Music2,
  Play,
  ShieldCheck,
  Sparkles,
  Upload,
  X,
  Ticket,
} from 'lucide-react';

import LanguageSelector, {
  useLanguage,
} from '@/components/LanguageSelector';

import PayPalCheckoutButton from '@/components/PayPalCheckoutButton';

const LOGO_URL = '/DadRock-Tabs-Logo.png';

const PRICE = '2.99';

const TRANSCRIPTION_TYPES = [
  {
    value: 'lead',
    title: 'Lead Guitar',
    description: 'Solos, melodies, bends and fills',
    emoji: '🎸',
  },
  {
    value: 'rhythm',
    title: 'Rhythm Guitar',
    description: 'Riffs, chords and backing parts',
    emoji: '🎸',
  },
  {
    value: 'bass',
    title: 'Bass Guitar',
    description: 'Bass lines, grooves and runs',
    emoji: '🎸',
  },
];

const BENEFITS = [
  {
    title: 'Upload Your Audio',
    description:
      'Upload an audio file you possess and have permission to analyze.',
    icon: Headphones,
  },
  {
    title: 'Choose Your Instrument',
    description:
      'Generate Lead Guitar, Rhythm Guitar or Bass.',
    icon: Guitar,
  },
  {
    title: 'Preview Before You Pay',
    description:
      'View a watermarked sample before unlocking.',
    icon: FileText,
  },
];

const FAQ_ITEMS = [
  {
    question:
      'How accurate are AI generated tabs?',
    answer:
      'Accuracy depends on recording quality, tuning, effects and instrument separation. Minor corrections may occasionally be required.',
  },
  {
    question:
      'What audio formats are supported?',
    answer:
      'MP3, WAV, AAC and M4A files are currently supported.',
  },
  {
    question:
      'Can I generate Bass tabs?',
    answer:
      'Yes. Choose Lead Guitar, Rhythm Guitar or Bass before generating your transcription.',
  },
  {
    question:
      'Do you keep my uploaded audio?',
    answer:
      'No. Audio is processed only for your transcription request.',
  },
  {
    question:
      'What happens after payment?',
    answer:
      'Your polished PDF becomes available immediately and is also emailed to you.',
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

  const [selectedLanguage] =
    useLanguage();

  const currentLanguage =
    selectedLanguage || 'en';

  const fileInputRef = useRef(null);

  /* -----------------------------
     SOURCE
  ------------------------------ */

  const [youtubeUrl, setYoutubeUrl] =
    useState(
      searchParams.get('youtube') || ''
    );

  const [audioFile, setAudioFile] =
    useState(null);

  const [youtubeVideoInfo,
    setYoutubeVideoInfo] =
    useState(null);

  const [
    isLoadingYoutubeInfo,
    setIsLoadingYoutubeInfo,
  ] = useState(false);

  const [
    youtubeInfoError,
    setYoutubeInfoError,
  ] = useState('');

  /* -----------------------------
     SONG
  ------------------------------ */

  const [songTitle, setSongTitle] =
    useState(
      searchParams.get('title') || ''
    );

  const [artistName, setArtistName] =
    useState(
      searchParams.get('artist') || ''
    );

  const [
    selectedType,
    setSelectedType,
  ] = useState('lead');

  /* -----------------------------
     USER
  ------------------------------ */

  const [
    customerEmail,
    setCustomerEmail,
  ] = useState('');

  const [
    copyrightConfirmed,
    setCopyrightConfirmed,
  ] = useState(false);

  /* -----------------------------
     GENERATION
  ------------------------------ */

  const [
    generatedTab,
    setGeneratedTab,
  ] = useState('');

  const [
    analysisMetadata,
    setAnalysisMetadata,
  ] = useState(null);

  const [
    previewReady,
    setPreviewReady,
  ] = useState(false);

  const [
    paymentCompleted,
    setPaymentCompleted,
  ] = useState(false);

  const [
    purchaseOrderId,
    setPurchaseOrderId,
  ] = useState('');

  const [
    isGenerating,
    setIsGenerating,
  ] = useState(false);

  const [
    isDownloading,
    setIsDownloading,
  ] = useState(false);

  const [
    generationError,
    setGenerationError,
  ] = useState('');

  const [
    statusMessage,
    setStatusMessage,
  ] = useState('');

  /* -----------------------------
     NEW PREVIEW SYSTEM
  ------------------------------ */

  const [
    previewPdfUrl,
    setPreviewPdfUrl,
  ] = useState('');

  const [
    previewUnlocked,
    setPreviewUnlocked,
  ] = useState(false);

  const [
    usingFreeToken,
    setUsingFreeToken,
  ] = useState(false);

  const [showTokenEntry, setShowTokenEntry] =
    useState(false);

  const [freeTokenCode, setFreeTokenCode] =
    useState('');
  const [tokenError, setTokenError] =
  useState('');
  const [tokenErrorTitle, setTokenErrorTitle] =
  useState('');

const [tokenUsesRemaining, setTokenUsesRemaining] =
  useState(null);

  /* -----------------------------
     FAQ
  ------------------------------ */

  const [openFaq, setOpenFaq] =
    useState(null);
    /* -----------------------------
     DERIVED SOURCE INFORMATION
  ------------------------------ */

  const youtubeVideoId = useMemo(() => {
    const match = youtubeUrl.match(
      /(?:youtu\.be\/|youtube\.com\/(?:watch\?v=|shorts\/|embed\/|live\/))([A-Za-z0-9_-]{11})/
    );

    return match?.[1] || null;
  }, [youtubeUrl]);

  const hasYouTubeUrl =
    youtubeUrl.trim().length > 0;

  const isValidYouTubeUrl =
    Boolean(youtubeVideoId);

  const sourceType = audioFile ? 'audio' : null;

  const hasValidSource =
    sourceType !== null;

  const emailIsValid = useMemo(() => {
    const trimmedEmail =
      customerEmail.trim();

    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      trimmedEmail
    );
  }, [customerEmail]);

  const selectedTypeDetails =
    useMemo(
      () =>
        TRANSCRIPTION_TYPES.find(
          (type) =>
            type.value ===
            selectedType
        ) ||
        TRANSCRIPTION_TYPES[0],
      [selectedType]
    );

  const formIsComplete = useMemo(
    () =>
      Boolean(
        songTitle.trim() &&
          artistName.trim() &&
          selectedType &&
          hasValidSource &&
          copyrightConfirmed &&
          emailIsValid
      ),
    [
      songTitle,
      artistName,
      selectedType,
      hasValidSource,
      copyrightConfirmed,
      emailIsValid,
    ]
  );

  /* -----------------------------
     RESET HELPERS
  ------------------------------ */

  const clearPreviewPdfUrl = () => {
    if (
      previewPdfUrl &&
      previewPdfUrl.startsWith('blob:')
    ) {
      window.URL.revokeObjectURL(
        previewPdfUrl
      );
    }

    setPreviewPdfUrl('');
  };

  const resetGeneratedResults = () => {
    clearPreviewPdfUrl();

    setGeneratedTab('');
    setAnalysisMetadata(null);
    setPreviewReady(false);
    setPreviewUnlocked(false);
    setPaymentCompleted(false);
    setPurchaseOrderId('');
    setUsingFreeToken(false);
    setShowTokenEntry(false);
    setFreeTokenCode('');
    setStatusMessage('');
    setGenerationError('');
  };

  useEffect(() => {
    return () => {
      if (
        previewPdfUrl &&
        previewPdfUrl.startsWith('blob:')
      ) {
        window.URL.revokeObjectURL(
          previewPdfUrl
        );
      }
    };
  }, [previewPdfUrl]);

  /* -----------------------------
     YOUTUBE VIDEO LOOKUP
  ------------------------------ */

  const fetchYoutubeVideoInfo =
    async (videoId) => {
      if (!videoId) {
        setYoutubeVideoInfo(null);
        setYoutubeInfoError('');
        return;
      }

      setIsLoadingYoutubeInfo(true);
      setYoutubeInfoError('');
      setYoutubeVideoInfo(null);

      try {
        const response = await fetch(
          `/api/youtube-video-info?videoId=${encodeURIComponent(
            videoId
          )}`
        );

        const data = await response
          .json()
          .catch(() => ({}));

        if (!response.ok) {
          throw new Error(
            data.error ||
              'Unable to retrieve this YouTube video.'
          );
        }

        setYoutubeVideoInfo(data);

        if (
          data.title &&
          !songTitle.trim()
        ) {
          setSongTitle(data.title);
        }

        if (
          data.channelTitle &&
          !artistName.trim()
        ) {
          setArtistName(
            data.channelTitle
          );
        }
      } catch (error) {
        setYoutubeInfoError(
          error instanceof Error
            ? error.message
            : 'Unable to retrieve this YouTube video.'
        );
      } finally {
        setIsLoadingYoutubeInfo(false);
      }
    };

  useEffect(() => {
    const lookupDelay =
      window.setTimeout(() => {
        if (isValidYouTubeUrl) {
          fetchYoutubeVideoInfo(
            youtubeVideoId
          );
          return;
        }

        setYoutubeVideoInfo(null);
        setYoutubeInfoError('');
        setIsLoadingYoutubeInfo(false);
      }, 400);

    return () => {
      window.clearTimeout(
        lookupDelay
      );
    };
  }, [
    youtubeVideoId,
    isValidYouTubeUrl,
  ]);

  /* -----------------------------
     SOURCE SELECTION
  ------------------------------ */

  const handleYoutubeUrlChange = (
    event
  ) => {
    const nextUrl =
      event.target.value;

    setYoutubeUrl(nextUrl);
    resetGeneratedResults();

    if (nextUrl.trim()) {
      setAudioFile(null);

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };
    /* -----------------------------
     AUDIO FILE HANDLING
  ------------------------------ */

  const handleFileChange = (
    event
  ) => {
    const selectedFile =
      event.target.files?.[0] ||
      null;

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
        fileInputRef.current.value =
          '';
      }

      setGenerationError(
        'Please choose an MP3, WAV, M4A, or AAC audio file.'
      );

      return;
    }

    setAudioFile(selectedFile);

    setYoutubeUrl('');
    setYoutubeVideoInfo(null);
    setYoutubeInfoError('');

    const filenameWithoutExtension =
      selectedFile.name
        .replace(/\.[^/.]+$/, '')
        .trim();

    const filenameParts =
      filenameWithoutExtension
        .split(/\s+-\s+/)
        .map((part) => part.trim())
        .filter(Boolean);

    if (filenameParts.length >= 2) {
      const parsedArtist =
        filenameParts.shift();

      const parsedSong =
        filenameParts.join(' - ');

      if (
        parsedArtist &&
        !artistName.trim()
      ) {
        setArtistName(parsedArtist);
      }

      if (
        parsedSong &&
        !songTitle.trim()
      ) {
        setSongTitle(parsedSong);
      }
    }
  };

  const removeAudioFile = () => {
    setAudioFile(null);
    resetGeneratedResults();

    if (fileInputRef.current) {
      fileInputRef.current.value =
        '';
    }
  };

  /* -----------------------------
     AUDIO UPLOAD
  ------------------------------ */

  const uploadAudioSource =
    async () => {
      if (!audioFile) {
        throw new Error(
          'Please choose an audio file before continuing.'
        );
      }

      setStatusMessage(
        'Uploading your audio securely...'
      );

      const safeFileName =
        audioFile.name
          .replace(
            /[^a-zA-Z0-9._-]/g,
            '-'
          )
          .replace(/-+/g, '-')
          .slice(0, 120);

      const uploadedBlob =
        await upload(
          `audio/${Date.now()}-${safeFileName}`,
          audioFile,
          {
            access: 'private',

            handleUploadUrl:
              '/api/audio-upload',

            clientPayload:
              JSON.stringify({
                song:
                  songTitle.trim(),
                artist:
                  artistName.trim(),
                transcriptionType:
                  selectedType,
                copyrightConfirmed,
                customerEmail:
                  customerEmail.trim(),
              }),
          }
        );

      if (
        !uploadedBlob?.url ||
        !uploadedBlob?.pathname
      ) {
        throw new Error(
          'The audio upload did not return a valid file reference.'
        );
      }

      return {
        audioUrl:
          uploadedBlob.url,
        pathname:
          uploadedBlob.pathname,
      };
    };

  /* -----------------------------
     ANALYZER REQUEST
  ------------------------------ */

  const requestTabAnalysis =
    async ({
      source,
      audioUrl = null,
      pathname = null,
    }) => {
      const endpoint = '/api/analyze-audio-tab';

      const sendAnalyzerRequest =
        async (payload) => {
          const response = await fetch(
            endpoint,
            {
              method: 'POST',

              headers: {
                'Content-Type':
                  'application/json',
              },

              body: JSON.stringify(
                payload
              ),
            }
          );

          const data = await response
            .json()
            .catch(() => ({}));

          return {
            response,
            data,
          };
        };

      const analysisRequest = {
        source,
        audioUrl,
        pathname,
        song:
          songTitle.trim(),
        artist:
          artistName.trim(),
        transcriptionType:
          selectedType,
        customerEmail:
          customerEmail.trim(),
      };

      setStatusMessage(
        selectedType === 'rhythm'
          ? 'Starting your Rhythm Guitar analysis...'
          : 'Analyzing your uploaded audio...'
      );

      let {
        response,
        data,
      } = await sendAnalyzerRequest(
        analysisRequest
      );

      if (
        response.status === 202 &&
        selectedType === 'rhythm'
      ) {
        const jobToken =
          data?.analysisJob?.token;

        if (!jobToken) {
          throw new Error(
            'The analyzer did not return a valid Rhythm job.'
          );
        }

        const startedAt = Date.now();
        const clientDeadline =
          startedAt +
          21 * 60 * 1000;

        let pollAfterMs = Math.max(
          1500,
          Math.min(
            5000,
            Number(
              data?.analysisJob
                ?.pollAfterMs
            ) || 3000
          )
        );

        while (
          Date.now() < clientDeadline
        ) {
          const elapsedSeconds =
            Math.max(
              0,
              Math.floor(
                (Date.now() -
                  startedAt) /
                  1000
              )
            );

          if (elapsedSeconds < 60) {
            setStatusMessage(
              'Separating instruments and building your Rhythm Guitar tab...'
            );
          } else {
            const elapsedMinutes =
              Math.max(
                1,
                Math.floor(
                  elapsedSeconds / 60
                )
              );

            setStatusMessage(
              `Your Rhythm Guitar tab is still processing (${elapsedMinutes} min). You can keep this page open while the analysis finishes.`
            );
          }

          await new Promise(
            (resolve) => {
              window.setTimeout(
                resolve,
                pollAfterMs
              );
            }
          );

          ({
            response,
            data,
          } = await sendAnalyzerRequest({
            operation: 'status',
            jobToken,
            transcriptionType:
              selectedType,
          }));

          if (
            response.status === 202
          ) {
            pollAfterMs =
              Math.max(
                1500,
                Math.min(
                  5000,
                  Number(
                    data?.analysisJob
                      ?.pollAfterMs
                  ) || pollAfterMs
                )
              );
            continue;
          }

          if (!response.ok) {
            throw new Error(
              data.error ||
                data.message ||
                'The analyzer could not generate tablature.'
            );
          }

          if (
            !data.generatedTab ||
            typeof data.generatedTab !==
              'string'
          ) {
            throw new Error(
              'The analyzer returned no tablature.'
            );
          }

          // The completed result has now crossed the browser boundary safely.
          // Acknowledge deletion of the transient Modal Queue partition. Ack
          // failure is non-fatal because the partition has a 15-minute TTL.
          try {
            await sendAnalyzerRequest({
              operation: 'ack',
              jobToken,
              transcriptionType:
                selectedType,
            });
          } catch (ackError) {
            console.warn(
              'Async Rhythm result cleanup acknowledgement failed; TTL cleanup remains active.',
              ackError
            );
          }

          return data;
        }

        throw new Error(
          'Your Rhythm Guitar analysis did not finish within the processing window. Please try again.'
        );
      }

      if (!response.ok) {
        throw new Error(
          data.error ||
            data.message ||
            'The analyzer could not generate tablature.'
        );
      }

      if (
        !data.generatedTab ||
        typeof data.generatedTab !==
          'string'
      ) {
        throw new Error(
          'The analyzer returned no tablature.'
        );
      }

      return data;
    };
    /* -----------------------------
     WATERMARKED PREVIEW PDF
  ------------------------------ */

  const requestPreviewPdf =
    async (tabContent, analysisMetadata = {}) => {
      setStatusMessage(
        'Creating your watermarked tab preview...'
      );

      const response = await fetch(
        '/api/generate-tab-preview',
        {
          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body: JSON.stringify({
  song:
    songTitle.trim(),

  artist:
    artistName.trim(),

  transcriptionType:
    selectedType,

  generatedTab:
    tabContent,

  tuning:
    analysisMetadata.tuning || 'Standard Tuning',

  tempo:
    analysisMetadata.tempo || 120,

  timeSignature:
    analysisMetadata.timeSignature || '4/4',

  keySignature:
    analysisMetadata.keySignature || '',

  analysisEngine:
    analysisMetadata.analysisEngine || '',

  techniques:
    Array.isArray(analysisMetadata.techniques)
      ? analysisMetadata.techniques
      : [],

  renderEvents:
    Array.isArray(analysisMetadata.renderEvents)
      ? analysisMetadata.renderEvents
      : [],

  measureGrid:
    analysisMetadata.measureGrid || null,

  confidence:
    analysisMetadata.confidence ?? null,

  difficulty:
    analysisMetadata.difficulty || null,

            previewSystems: 4,

            watermark:
              'DADROCK TABS PREVIEW',

            locked:
              true,
          }),
        }
      );

      if (!response.ok) {
        const errorData =
          await response
            .json()
            .catch(() => ({}));

        throw new Error(
          errorData.error ||
            errorData.message ||
            'Unable to create the watermarked preview.'
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
        throw new Error(
          'The preview server did not return a valid PDF.'
        );
      }

      const previewBlob =
        await response.blob();

      clearPreviewPdfUrl();

      const objectUrl =
        window.URL.createObjectURL(
          previewBlob
        );

      setPreviewPdfUrl(objectUrl);

      return objectUrl;
    };

  /* -----------------------------
     GENERATE PREVIEW
  ------------------------------ */

  const handleGeneratePreview =
    async () => {
      setGenerationError('');
      setStatusMessage('');

      if (
        !formIsComplete ||
        isGenerating
      ) {
        setGenerationError(
          'Please complete every required field before generating your tab.'
        );

        return;
      }

      if (
        ![
          'lead',
          'rhythm',
          'bass',
        ].includes(selectedType)
      ) {
        setGenerationError(
          'Please choose Lead Guitar, Rhythm Guitar, or Bass Guitar.'
        );

        return;
      }

      if (!sourceType) {
        setGenerationError(
          'Please upload an audio file before continuing.'
        );

        return;
      }

      setIsGenerating(true);
      setGeneratedTab('');
      setAnalysisMetadata(null);
      setPreviewReady(false);
      setPreviewUnlocked(false);
      setPaymentCompleted(false);
      setPurchaseOrderId('');
      setUsingFreeToken(false);

      clearPreviewPdfUrl();

      try {
        let analysisSource = {
          source: sourceType,
          audioUrl: null,
          pathname: null,
        };

        if (
          sourceType === 'audio'
        ) {
          const uploadedAudio =
            await uploadAudioSource();

          analysisSource = {
            source: 'audio',

            audioUrl:
              uploadedAudio.audioUrl,

            pathname:
              uploadedAudio.pathname,
          };
        }

        const analyzerData =
          await requestTabAnalysis(
            analysisSource
          );

        const tabContent =
          analyzerData.generatedTab.trim();

        setGeneratedTab(
          tabContent
        );
        setAnalysisMetadata(
          analyzerData
        );

        await requestPreviewPdf(
          tabContent,
          analyzerData
        );

        setPreviewReady(true);

        setStatusMessage(
          'Your watermarked AI tablature preview is ready.'
        );

        window.setTimeout(() => {
          document
            .getElementById(
              'tab-preview'
            )
            ?.scrollIntoView({
              behavior: 'smooth',
              block: 'start',
            });
        }, 150);
      } catch (error) {
        console.error(
          'AI tab preview error:',
          error
        );

        setGeneratedTab('');
        setAnalysisMetadata(null);
        setPreviewReady(false);
        clearPreviewPdfUrl();

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
    /* -----------------------------
     PAYPAL UNLOCK
  ------------------------------ */

  const handlePaymentApproved =
    async ({ orderId } = {}) => {
      setGenerationError('');

      if (!orderId) {
        setPaymentCompleted(false);
        setPreviewUnlocked(false);
        setStatusMessage('');
        setGenerationError(
          'PayPal did not return an order ID.'
        );
        return;
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);
      setPreviewUnlocked(true);
      setUsingFreeToken(false);
      setStatusMessage(
        'Payment confirmed. Creating and emailing your full PDF...'
      );

      await handleDownloadPdf({
        unlockReference: orderId,
        unlockMethod: 'paypal',
      });

      window.setTimeout(() => {
        document
          .getElementById('download-section')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    };

  const handlePaymentCancelled =
    () => {
      setPaymentCompleted(false);
      setPreviewUnlocked(false);
      setGenerationError('');

      setStatusMessage(
        'PayPal checkout was cancelled. Your preview is still available.'
      );
    };

  const handlePaymentError =
    (error) => {
      console.error(
        'PayPal checkout error:',
        error
      );

      setPaymentCompleted(false);
      setPreviewUnlocked(false);
      setStatusMessage('');

      setGenerationError(
        error instanceof Error
          ? error.message
          : 'PayPal checkout could not be completed.'
      );
    };

  /* -----------------------------
     FREE TOKEN UNLOCK
  ------------------------------ */

  const handleFreeTokenUnlock =
    async () => {
      if (
        usingFreeToken ||
        previewUnlocked
      ) {
        return;
      }

      const normalizedToken = freeTokenCode
        .trim()
        .toUpperCase();

      if (!normalizedToken) {
  setTokenError(
    'Enter your free token code before unlocking.'
  );
  setTokenUsesRemaining(null);
  return;
      }

      setUsingFreeToken(true);
      setGenerationError('');
      setTokenError('');
setTokenErrorTitle('');
setTokenUsesRemaining(null);

      setStatusMessage(
        'Checking your free token...'
      );

      try {
        const response = await fetch(
          '/api/free-tab-token',
          {
            method: 'POST',

            headers: {
              'Content-Type':
                'application/json',
            },

            body: JSON.stringify({
              tokenCode: normalizedToken,

              customerEmail:
                customerEmail.trim(),

              song:
                songTitle.trim(),

              artist:
                artistName.trim(),

              transcriptionType:
                selectedType,

              youtubeUrl:
                sourceType ===
                'youtube'
                  ? youtubeUrl.trim()
                  : null,
            }),
          }
        );

        const data = await response
          .json()
          .catch(() => ({}));

        if (!response.ok) {
  const errorTitles = {
    TOKEN_NOT_FOUND: 'Token Not Found',
    TOKEN_EXPIRED: 'Token Expired',
    TOKEN_EXHAUSTED: 'Token Fully Used',
    TOKEN_EMAIL_MISMATCH: 'Wrong Email Address',
    TOKEN_INACTIVE: 'Invalid Token',
  };

  setTokenErrorTitle(
    errorTitles[data.code] || 'Invalid Token'
  );

  setTokenError(
    data.error ||
      data.message ||
      'This token could not be used.'
  );

  setTokenUsesRemaining(null);

  throw new Error(
    data.error ||
      data.message ||
      'This token could not be used.'
  );
        }

        if (
          !data.success &&
          !data.unlocked
        ) {
          throw new Error(
            'No valid free token was found for this email address.'
          );
        }

        const tokenReference =
          data.tokenId ||
          data.reference ||
          `FREE-${Date.now()}`;

        setPurchaseOrderId(
          tokenReference
        );

        setPaymentCompleted(
          false
        );

        setPreviewUnlocked(
          true
        );

        setTokenUsesRemaining(
  data.usesRemaining ?? null
);

setTokenError('');
        setFreeTokenCode('');

        setStatusMessage(
          'Free token accepted. Creating and emailing your full PDF...'
        );

        await handleDownloadPdf({
          unlockReference: tokenReference,
          unlockMethod: 'free-token',
        });

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
          'Free token error:',
          error
        );

        setPreviewUnlocked(
          false
        );

        setGenerationError(
          error instanceof Error
            ? error.message
            : 'Unable to use your free token.'
        );

        setStatusMessage('');
      } finally {
        setUsingFreeToken(false);
      }
    };
    /* -----------------------------
     FINISHED PDF DOWNLOAD
  ------------------------------ */

  const handleDownloadPdf =
    async ({ unlockReference = '', unlockMethod = '' } = {}) => {
      setGenerationError('');
      setStatusMessage('');

      const resolvedUnlockReference =
        unlockReference || purchaseOrderId;

      const hasExplicitUnlock = Boolean(
        unlockReference && unlockMethod
      );

      if (!previewUnlocked && !hasExplicitUnlock) {
        setGenerationError(
          'Unlock the finished PDF before downloading.'
        );

        return;
      }

      const resolvedUnlockMethod =
        unlockMethod ||
        (paymentCompleted ? 'paypal' : 'free-token');

      if (!resolvedUnlockReference) {
        setGenerationError(
          'The unlock reference is missing.'
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

      document
        .getElementById('download-section')
        ?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });

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
                resolvedUnlockMethod === 'paypal'
                  ? resolvedUnlockReference
                  : null,

              tokenReference:
                resolvedUnlockMethod === 'free-token'
                  ? resolvedUnlockReference
                  : null,

              unlockMethod:
                resolvedUnlockMethod,

              song:
                songTitle.trim(),

              artist:
                artistName.trim(),

              transcriptionType:
                selectedType,

              customerEmail:
                customerEmail.trim(),

              generatedTab,

              tuning:
                analysisMetadata?.tuning || 'Standard Tuning',

              tempo:
                analysisMetadata?.tempo || 120,

              timeSignature:
                analysisMetadata?.timeSignature || '4/4',

              keySignature:
                analysisMetadata?.keySignature || '',

              analysisEngine:
                analysisMetadata?.analysisEngine || '',

              techniques:
                Array.isArray(analysisMetadata?.techniques)
                  ? analysisMetadata.techniques
                  : [],

              renderEvents:
                Array.isArray(analysisMetadata?.renderEvents)
                  ? analysisMetadata.renderEvents
                  : [],

              measureGrid:
                analysisMetadata?.measureGrid || null,

              confidence:
                analysisMetadata?.confidence ?? null,

              difficulty:
                analysisMetadata?.difficulty || null,

              sourceType,
            }),
          }
        );

        if (!response.ok) {
          const errorData =
            await response
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

        const pdfBlob =
          await response.blob();

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

        downloadLink.href =
          downloadUrl;

        downloadLink.download =
          `${safeArtist}-${safeTitle}-${selectedType}-tab.pdf`;

        document.body.appendChild(
          downloadLink
        );

        downloadLink.click();
        downloadLink.remove();

        window.setTimeout(() => {
          window.URL.revokeObjectURL(
            downloadUrl
          );
        }, 1000);

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

  return (
    <main className="min-h-screen bg-[#090909] text-white">
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-[-180px] h-[420px] w-[420px] -translate-x-1/2 rounded-full bg-orange-600/10 blur-[130px]" />

        <div className="absolute bottom-[-220px] right-[-160px] h-[420px] w-[420px] rounded-full bg-amber-500/5 blur-[130px]" />
      </div>

      <div className="relative z-10 mx-auto w-full max-w-2xl px-4 py-8">
        <header className="mb-5 flex items-center justify-between gap-3">
          <Link
            href={getLocalizedPath(
              '/',
              currentLanguage
            )}
            className="inline-flex items-center gap-2 text-zinc-400 transition-colors hover:text-amber-400"
          >
            <ArrowLeft size={17} />

            <span>Back to DadRock Tabs</span>
          </Link>

          <LanguageSelector />
        </header>
          <div className="overflow-hidden rounded-3xl border border-amber-500/40 bg-zinc-900 shadow-2xl shadow-orange-500/10">
          <section className="border-b border-zinc-800 px-5 py-7 text-center sm:px-8">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs"
              className="mx-auto mb-4 h-auto w-full max-w-[440px] object-contain"
            />

            <div className="mx-auto max-w-3xl">
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-orange-500/40 bg-orange-500/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-orange-300">
                <Sparkles size={15} />

                AI Powered Transcription
              </div>

              <h1 className="text-2xl font-bold text-white sm:text-3xl">
                Tab Generator Studio
              </h1>

              <p className="mt-1 text-sm text-zinc-400">
                Create professional-quality guitar or bass tablature from your audio.
              </p>
            </div>
          </section>

          <section className="border-t border-zinc-800 bg-black/20 px-5 py-6 sm:px-8">
            <div className="mb-5 text-center">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                Step One
              </p>

              <h2 className="mt-2 text-2xl font-black text-white">
                Upload Your Audio
              </h2>

              <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                Upload an audio file from your device that you possess and have permission to analyze.
              </p>
            </div>

            <div className="mx-auto max-w-2xl">

              <section
                className={`rounded-2xl border p-5 transition ${
                  sourceType === 'audio'
                    ? 'border-orange-500/50 bg-orange-500/5'
                    : 'border-zinc-800 bg-zinc-950/80'
                }`}
              >
                <div className="mb-4 flex items-center gap-3">
                  <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                    <Upload size={21} />
                  </div>

                  <div>
                    <h3 className="text-xl font-bold text-white">
                      Upload Audio
                    </h3>

                    <p className="text-xs text-zinc-500">
                      MP3, WAV, M4A or AAC
                    </p>
                  </div>
                </div>

                {!audioFile ? (
                  <label
                    htmlFor="audio-upload"
                    className="flex min-h-[190px] cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed border-zinc-700 bg-black/40 px-5 py-8 text-center transition hover:border-orange-500/60 hover:bg-orange-500/5"
                  >
                    <div className="flex h-14 w-14 items-center justify-center rounded-full border border-orange-500/30 bg-orange-500/10 text-orange-300">
                      <Upload size={25} />
                    </div>

                    <p className="mt-3 text-[13px] font-black leading-tight text-white sm:text-lg">
                      Tap to choose an audio file
                    </p>

                    <p className="mt-2 max-w-xs text-xs leading-5 text-zinc-500">
                      Upload a clear recording for
                      the strongest transcription
                      results.
                    </p>

                    <input
                      id="audio-upload"
                      type="file"
                      accept="audio/*,.mp3,.wav,.m4a,.aac"
                      onChange={
                        handleFileChange
                      }
                      className="hidden"
                    />
                  </label>
                ) : (
                  <div className="rounded-2xl border border-green-500/30 bg-green-500/5 p-4">
                    <div className="flex items-center gap-3">
                      <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-green-500/30 bg-green-500/10 text-green-300">
                        <Music size={21} />
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
                        onClick={
                          removeAudioFile
                        }
                        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-zinc-700 text-zinc-400 transition hover:border-red-500/60 hover:text-red-300"
                        aria-label="Remove audio file"
                      >
                        <X size={17} />
                      </button>
                    </div>

                    <div className="mt-4 flex items-center gap-2 rounded-xl border border-green-500/20 bg-black/30 px-3 py-2 text-xs font-semibold text-green-300">
                      <CheckCircle2
                        size={15}
                      />

                      Audio file ready for analysis
                    </div>
                  </div>
                )}
              </section>
            </div>
          </section>
          <section className="border-t border-zinc-800 px-5 py-6 sm:px-8">
            <div className="mb-5 text-center">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                Step Two
              </p>

              <h2 className="mt-2 text-2xl font-black text-white">
                Add Song Details
              </h2>

              <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                Confirm the song, artist,
                delivery email, and instrument
                part you want transcribed.
              </p>
            </div>

            <div className="mx-auto max-w-2xl">
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
                  placeholder="Enter the song title"
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
                  placeholder="Enter the artist name"
                  className="w-full rounded-xl border border-zinc-700 bg-black/60 px-4 py-3 text-sm text-white outline-none transition placeholder:text-zinc-600 focus:border-orange-500"
                />
              </div>
            </div>


            <div className="mt-6">
              <div className="mb-3">
                <h3 className="text-xl font-bold text-white">
                  Choose your transcription
                </h3>

                <p className="mt-1 hidden text-xs leading-5 text-zinc-400 sm:block">
                  Select the part you want the AI
                  analyzer to isolate and
                  transcribe.
                </p>
              </div>

              <div className="grid grid-cols-3 gap-2 sm:gap-3">
                {TRANSCRIPTION_TYPES.map(
                  (type) => {
                    const Icon = Guitar;

                    const isSelected =
                      selectedType ===
                      type.value;

                    return (
                      <button
                        key={
                          type.value
                        }
                        type="button"
                        onClick={() => {
                          setSelectedType(
                            type.value
                          );

                          resetGeneratedResults();
                        }}
                        className={`relative min-w-0 rounded-xl border p-2.5 text-center transition sm:rounded-2xl sm:p-4 ${
                          isSelected
                            ? 'border-orange-500 bg-orange-500/10 shadow-lg shadow-orange-950/20'
                            : 'border-zinc-800 bg-zinc-950/80 hover:border-zinc-700'
                        }`}
                      >
                        <div className="flex items-center justify-center">
                          <div
                            className={`flex h-10 w-10 items-center justify-center rounded-xl border sm:h-12 sm:w-12 ${
                              isSelected
                                ? 'border-orange-500/50 bg-orange-500/15 text-orange-300'
                                : 'border-zinc-700 bg-zinc-900 text-zinc-400'
                            }`}
                          >
                            <Icon
                              size={22}
                            />
                          </div>

                          {isSelected && (
                            <CheckCircle2
                              size={16}
                              className="absolute right-2 top-2 text-orange-400 sm:right-3 sm:top-3"
                            />
                          )}
                        </div>

                        <h4 className="mt-3 text-[13px] font-black leading-tight text-white sm:text-lg">
                          {type.title}
                        </h4>

                        <p className="mt-1 text-xs leading-5 text-zinc-500">
                          {
                            type.description
                          }
                        </p>
                      </button>
                    );
                  }
                )}
              </div>
            </div>
          </section>
          <section className="border-t border-zinc-800 px-5 py-6 sm:px-8">
            <div className="rounded-2xl border border-zinc-800 bg-zinc-950/80 p-5">

              <label className="flex items-start gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={copyrightConfirmed}
                  onChange={(event) => {
                    setCopyrightConfirmed(
                      event.target.checked
                    );
                  }}
                  className="mt-1 h-5 w-5 rounded border-zinc-600 bg-zinc-900 text-orange-500"
                />

                <span className="text-sm leading-6 text-zinc-300">
                  I confirm that I possess this audio file, have permission to analyze it, and understand this AI transcription is generated for educational and personal practice purposes.
                </span>
              </label>

              <div className="mt-6">
              <label
                htmlFor="customer-email"
                className="mb-2 block text-sm font-semibold text-zinc-300"
              >
                Email for PDF Delivery
              </label>

              <div className="relative">
                <Mail
                  size={18}
                  className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500"
                />

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
                  className={`w-full rounded-xl border bg-black/60 py-3 pl-11 pr-4 text-sm text-white outline-none transition placeholder:text-zinc-600 ${
                    !customerEmail
                      ? 'border-zinc-700 focus:border-orange-500'
                      : emailIsValid
                        ? 'border-green-500/70 focus:border-green-400'
                        : 'border-red-500/70 focus:border-red-400'
                  }`}
                />
              </div>

              {customerEmail && (
                <p
                  className={`mt-2 text-xs font-semibold ${
                    emailIsValid
                      ? 'text-green-400'
                      : 'text-red-400'
                  }`}
                >
                  {emailIsValid
                    ? '✓ Valid delivery email'
                    : 'Please enter a valid email address.'}
                </p>
              )}
              </div>

              <div className="mt-6">

                <button
                  type="button"
                  disabled={
                    !formIsComplete ||
                    isGenerating
                  }
                  onClick={
                    handleGeneratePreview
                  }
                  className={`flex w-full items-center justify-center gap-3 rounded-xl px-5 py-4 text-lg font-black transition-all ${
                    formIsComplete &&
                    !isGenerating
                      ? 'bg-gradient-to-r from-amber-500 to-red-600 text-white hover:scale-[1.02]'
                      : 'cursor-not-allowed bg-zinc-700 text-zinc-400'
                  }`}
                >
                  {isGenerating ? (
                    <>
                      <Loader2
                        size={22}
                        className="animate-spin"
                      />

                      Tab Studio is analyzing your audio...
                    </>
                  ) : (
                    <>
                      <FileText size={22} />

                      {selectedType
                        ? `Generate ${
                            selectedType.charAt(0).toUpperCase() +
                            selectedType.slice(1)
                          } Tab`
                        : 'Select a transcription'}
                    </>
                  )}
                </button>
                </div>

              {generationError && (

                <div className="mt-6 rounded-2xl border border-red-500/30 bg-red-500/10 p-4">

                  <div className="flex items-start gap-3">

                    <AlertCircle
                      size={20}
                      className="mt-0.5 text-red-400"
                    />

                    <div>

                      <h3 className="font-bold text-red-300">
                        Something went wrong
                      </h3>

                      <p className="mt-1 text-sm leading-6 text-red-200">
                        {generationError}
                      </p>

                    </div>

                  </div>

                </div>

              )}

            </div>

          </section>
          {previewReady &&
            previewPdfUrl && (
              <section
                id="tab-preview"
                className="border-t border-zinc-800 bg-black/30 px-5 py-7 sm:px-8"
              >
                <div className="mb-5 text-center">
                  <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                    Step Three
                  </p>

                  <h2 className="mt-2 text-2xl font-black text-white">
                    Tab Studio Preview
                  </h2>

                  <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                    Your preview contains a short,
                    watermarked sample. Unlock the
                    complete polished PDF below.
                  </p>
                </div>

                <div className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950">
                  <a
                    href={previewPdfUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex w-full flex-col items-center justify-center gap-3 border-b border-zinc-800 px-4 py-5 text-center transition hover:bg-orange-500/5"
                  >
                    <div className="flex h-12 w-12 items-center justify-center rounded-xl border border-orange-500/30 bg-orange-500/10 text-orange-300">
                      <FileText size={24} />
                    </div>

                    <div className="min-w-0">
                      <p className="truncate text-base font-black text-white">
                        {songTitle}
                      </p>

                      <p className="truncate text-sm text-zinc-500">
                        {artistName} ·{' '}
                        {selectedTypeDetails?.title}
                      </p>
                    </div>

                    <span className="mt-1 inline-flex items-center gap-2 rounded-xl border border-orange-500/50 bg-orange-500/10 px-5 py-3 font-black text-orange-200">
                      Click Here For Preview
                      <ArrowRight size={19} />
                    </span>
                  </a>

                  <a
                    href={previewPdfUrl}
                    download={`${artistName || 'DadRock'}-${songTitle || 'Tab'}-${selectedType || 'preview'}-preview.pdf`}
                    className="mx-4 mb-5 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-red-600 px-4 py-3 font-black text-white transition hover:scale-[1.01]"
                  >
                    <Download size={19} />
                    Download Preview PDF
                  </a>

                  <div className="relative bg-zinc-900">
                    <iframe
                      src={`${previewPdfUrl}#toolbar=0&navpanes=0&scrollbar=1`}
                      title={`${songTitle} tab preview`}
                      className="hidden h-[680px] w-full bg-white sm:block"
                    />
                  </div>
                </div>

                {!previewUnlocked && (
                  <div className="mt-5 rounded-2xl border border-orange-500/30 bg-gradient-to-br from-orange-500/10 to-amber-500/5 p-5">
                    <div className="text-center">
                      <div className="inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-black/30 px-3 py-1.5 text-xs font-bold text-orange-300">
                        <ShieldCheck size={15} />

                        Secure Unlock
                      </div>

                      <h3 className="mt-3 text-xl font-black text-white">
                        Unlock the Complete PDF
                      </h3>

                      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-zinc-400">
                        Receive the full portrait
                        tablature PDF with every
                        generated section included.
                      </p>
                    </div>

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">
                      <div className="space-y-3">
                        <button
                          type="button"
                          onClick={() => {
                            setShowTokenEntry(
                              (current) => !current
                            );
                            setGenerationError('');
                            setTokenError('');
setTokenUsesRemaining(null);
                          }}
                          disabled={usingFreeToken}
                          className="flex min-h-[54px] w-full items-center justify-center gap-2 rounded-xl border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm font-black text-green-300 transition hover:bg-green-500/15 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          <Ticket size={19} />
                          Use Free Token
                        </button>

                        {showTokenEntry && (
                          <div className="rounded-xl border border-green-500/30 bg-black/40 p-3">
                            <label
                              htmlFor="free-token-code"
                              className="mb-2 block text-xs font-bold uppercase tracking-wide text-green-300"
                            >
                              Enter Token Code
                            </label>

                            <input
                              id="free-token-code"
                              type="text"
                              value={freeTokenCode}
                              onChange={(event) => {
  setFreeTokenCode(
    event.target.value.toUpperCase()
  );
  setTokenError('');
  setTokenUsesRemaining(null);
}}
                              onKeyDown={(event) => {
                                if (event.key === 'Enter') {
                                  event.preventDefault();
                                  handleFreeTokenUnlock();
                                }
                              }}
                              placeholder="DRT-XXXX-XXXX-XXXX"
                              autoCapitalize="characters"
                              autoComplete="off"
                              spellCheck={false}
                              className="w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-3 text-center font-mono text-sm uppercase tracking-wider text-white outline-none transition focus:border-green-500"
                            />

                            <button
                              type="button"
                              onClick={handleFreeTokenUnlock}
                              disabled={
                                usingFreeToken ||
                                !freeTokenCode.trim()
                              }
                              className="mt-3 flex min-h-[48px] w-full items-center justify-center gap-2 rounded-lg bg-green-500 px-4 py-3 text-sm font-black text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-50"
                            >
                              {usingFreeToken ? (
                                <Loader2
                                  size={18}
                                  className="animate-spin"
                                />
                              ) : (
                                <LockKeyhole size={18} />
                              )}

                              {usingFreeToken
                                ? 'Checking Token...'
                                : 'Redeem Token & Unlock'}
                            </button>
                          </div>
                        )}
                      </div>

                      {tokenError && (
  <p className="mt-3 text-sm font-semibold text-red-400">
    ❌ {tokenError}
  </p>
)}

{tokenUsesRemaining !== null && (
  <p className="mt-2 text-sm font-semibold text-green-400">
    ✅ Token accepted — {tokenUsesRemaining}{' '}
    {tokenUsesRemaining === 1 ? 'use' : 'uses'} remaining
  </p>
)}

                      <div className="min-h-[54px] rounded-xl border border-zinc-700 bg-white p-2">
                        <PayPalCheckoutButton
                          song={songTitle.trim()}
                          artist={artistName.trim()}
                          transcriptionType={selectedType}
                          customerEmail={customerEmail.trim()}
                          onPaymentCompleted={handlePaymentApproved}
                          onPaymentCancelled={handlePaymentCancelled}
                          onPaymentError={handlePaymentError}
                        />
                      </div>
                    </div>

                    <p className="mt-4 text-center text-xs leading-5 text-zinc-500">
                      Pay once: ${PRICE} USD. Your
                      unlocked PDF can be downloaded
                      immediately and delivered by
                      email.
                    </p>
                  </div>
                )}
              </section>
            )}
          {previewUnlocked && (
            <section
              id="download-section"
              className="border-t border-zinc-800 bg-green-500/[0.03] px-5 py-7 sm:px-8"
            >
              <div className="rounded-2xl border border-green-500/30 bg-gradient-to-br from-green-500/10 to-emerald-500/5 p-5 sm:p-6">
                <div className="text-center">
                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full border border-green-500/40 bg-green-500/15 text-green-300">
                    <CheckCircle2 size={28} />
                  </div>

                  <p className="mt-4 text-xs font-bold uppercase tracking-[0.18em] text-green-400">
                    PDF Unlocked
                  </p>

                  <h2 className="mt-2 text-2xl font-black text-white">
                    Your Full Tab Is Ready
                  </h2>

                  <p className="mx-auto mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
                    Download the complete,
                    watermark-free PDF and keep it
                    for practice, printing, or
                    reference.
                  </p>
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-3">
                  <div className="rounded-xl border border-zinc-800 bg-black/30 p-4 text-center">
                    <FileText
                      size={22}
                      className="mx-auto text-orange-300"
                    />

                    <p className="mt-2 text-sm font-bold text-white">
                      Full PDF
                    </p>

                    <p className="mt-1 text-xs leading-5 text-zinc-500">
                      Every generated section
                      included
                    </p>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-black/30 p-4 text-center">
                    <ShieldCheck
                      size={22}
                      className="mx-auto text-green-300"
                    />

                    <p className="mt-2 text-sm font-bold text-white">
                      No Watermark
                    </p>

                    <p className="mt-1 text-xs leading-5 text-zinc-500">
                      Clean, polished final
                      tablature
                    </p>
                  </div>

                  <div className="rounded-xl border border-zinc-800 bg-black/30 p-4 text-center">
                    <Mail
                      size={22}
                      className="mx-auto text-blue-300"
                    />

                    <p className="mt-2 text-sm font-bold text-white">
                      Email Copy
                    </p>

                    <p className="mt-1 text-xs leading-5 text-zinc-500">
                      Delivered to your saved
                      email
                    </p>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => {
                    handleDownloadPdf();
                  }}
                  disabled={isDownloading}
                  className="relative z-20 mt-6 flex w-full touch-manipulation items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4 text-lg font-black text-white transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {isDownloading ? (
                    <>
                      <Loader2
                        size={22}
                        className="animate-spin"
                      />

                      Creating Your PDF...
                    </>
                  ) : (
                    <>
                      <Download size={22} />

                      Download Full PDF
                    </>
                  )}
                </button>

                <div className="mt-4 rounded-xl border border-green-500/20 bg-black/30 px-4 py-3 text-center">
                  <p className="text-xs leading-5 text-zinc-400">
                    Unlocked using{' '}
                    <span className="font-bold text-green-300">
                      {paymentCompleted
                        ? 'PayPal'
                        : 'a Free Pass'}
                    </span>
                    .
                  </p>

                  {!paymentCompleted && tokenUsesRemaining !== null && (
  <p className="mt-2 text-sm font-semibold text-green-300">
    {tokenUsesRemaining > 0 ? (
  <>
  🎉 Free Pass redeemed successfully!
  <br />
  {tokenUsesRemaining}{' '}
  {tokenUsesRemaining === 1 ? 'use' : 'uses'} remaining.
</>
) : (
  <>
  🎉 Final redemption complete!
  <br />
  This Free Pass has now been fully redeemed.
</>
)}
  </p>
)}

                  {purchaseOrderId && (
                    <p className="mt-1 break-all text-[11px] text-zinc-600">
  {paymentCompleted ? 'PayPal Reference:' : 'Free Pass ID:'}{' '}
  {purchaseOrderId}
</p>
                  )}
                </div>
              </div>
            </section>
          )}

          <section className="border-t border-zinc-800 px-5 py-8 sm:px-8">
            <div className="text-center">
              <p className="text-xs font-bold uppercase tracking-[0.18em] text-orange-400">
                Frequently Asked Questions
              </p>

              <h2 className="mt-2 text-2xl font-black text-white">
                Tab Generator Studio FAQ
              </h2>

              <p className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-zinc-400">
                Everything you need to know before
                generating your guitar or bass
                tablature.
              </p>
            </div>

            <div className="mt-8 space-y-4">
              {FAQ_ITEMS.map((faq, index) => {
                const isOpen =
                  openFaq === index;

                return (
                  <div
                    key={faq.question}
                    className="overflow-hidden rounded-2xl border border-zinc-800 bg-zinc-950/70"
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
                      className="flex w-full items-center justify-between gap-4 px-5 py-5 text-left transition hover:bg-white/[0.02]"
                    >
                      <span className="text-sm font-bold text-white sm:text-base">
                        {faq.question}
                      </span>

                      {isOpen ? (
                        <ChevronUp
                          size={20}
                          className="shrink-0 text-orange-400"
                        />
                      ) : (
                        <ChevronDown
                          size={20}
                          className="shrink-0 text-zinc-500"
                        />
                      )}
                    </button>

                    {isOpen && (
                      <div className="border-t border-zinc-800 px-5 pb-5 pt-4">
                        <p className="text-sm leading-7 text-zinc-400">
                          {faq.answer}
                        </p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </section>

          <section className="border-t border-zinc-800 bg-gradient-to-b from-zinc-950 to-black px-5 py-8 sm:px-8">
            <div className="mx-auto max-w-3xl text-center">
              <div className="inline-flex items-center gap-2 rounded-full border border-orange-500/30 bg-orange-500/10 px-4 py-2 text-xs font-bold uppercase tracking-[0.18em] text-orange-300">
                <Guitar size={15} />

                DadRock Tab Studio
              </div>

              <h2 className="mt-5 text-3xl font-black text-white">
                Learn Songs Faster
              </h2>

              <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-zinc-400">
                Upload your audio and let the DadRock Tab Studio create beautiful printable PDF Tab for guitar or bass in minutes.
              </p>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <div className="rounded-full border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-xs font-semibold text-zinc-300">
                  🎸 Guitar
                </div>

                <div className="rounded-full border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-xs font-semibold text-zinc-300">
                  🎵 Bass
                </div>

                <div className="rounded-full border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-xs font-semibold text-zinc-300">
                  📄 PDF
                </div>

                <div className="rounded-full border border-zinc-700 bg-zinc-900/60 px-4 py-2 text-xs font-semibold text-zinc-300">
                  🤖 AI Powered
                </div>
              </div>

              <Link
                href={getLocalizedPath(
                  '/',
                  currentLanguage
                )}
                className="mt-8 inline-flex items-center gap-3 rounded-full border border-orange-500/40 bg-orange-500/10 px-6 py-3 text-sm font-black text-orange-300 transition hover:border-orange-400 hover:bg-orange-500/20"
              >
                <Home size={18} />

                Back to DadRock Tabs
              </Link>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
                }

export default function AiTabGeneratorPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-[#090909] text-white">
          <div className="flex min-h-screen items-center justify-center">
            <div className="text-center">
              <Loader2
                size={32}
                className="mx-auto animate-spin text-orange-400"
              />

              <p className="mt-4 text-sm font-semibold text-zinc-400">
                Loading Tab Generator Studio...
              </p>
            </div>
          </div>
        </main>
      }
    >
      <AiTabGeneratorContent />
    </Suspense>
  );
}

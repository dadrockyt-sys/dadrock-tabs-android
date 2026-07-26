export const AI_TAB_TRANSLATIONS = {
  en: {
    home: 'Home',
    artists: 'Artists',
    songs: 'Songs',
    lessons: 'Lessons',
    partners: 'Partners',

    eyebrow: 'DadRock Tabs presents',
    title: 'AI Guitar & Bass Tab Generator',
    subtitle:
      'Upload an audio file and generate AI-assisted lead guitar, rhythm guitar, or bass tablature.',

    youtubeTitle: 'YouTube reference link',
    youtubeDescription:
      'Paste a YouTube link to identify and preview the recording. You must still upload the audio file that will be analyzed.',
    youtubePlaceholder: 'https://www.youtube.com/watch?v=...',

    uploadTitle: 'Upload Audio',
    uploadDescription:
      'Choose an MP3, WAV, or M4A file from your device.',
    browseFiles: 'Browse Audio Files',
    dropAudio: 'or drag and drop your audio file here',
    supportedFormats: 'Supported formats: MP3, WAV, and M4A',
    selectedFile: 'Selected Audio File',
    removeFile: 'Remove File',

    detailsTitle: 'Song Information',
    songLabel: 'Song Title',
    songPlaceholder: 'Enter the song title',
    artistLabel: 'Artist',
    artistPlaceholder: 'Enter the artist name',

    instrumentTitle: 'Choose the Part to Transcribe',
    leadTitle: 'Lead Guitar',
    leadDescription: 'Solos, melodies, bends, fills, and lead sections',
    rhythmTitle: 'Rhythm Guitar',
    rhythmDescription: 'Riffs, chords, rhythm patterns, and backing parts',
    bassTitle: 'Bass Guitar',
    bassDescription: 'Bass lines, grooves, runs, and fills',

    responsibilityTitle: 'Copyright Responsibility',
    responsibilityText:
      'I confirm that I am responsible for the audio I upload and that I have the necessary rights or permission to use it. I also agree to comply with applicable copyright laws and the terms of service of the platform from which the audio originated.',

    analyzeButton: 'Analyze Audio & Generate Tab',
    selectRequirements:
      'Upload an audio file, choose an instrument, enter the song details, and confirm the copyright statement.',
    analyzerNext:
      'The interface is ready. The secure AI audio-processing engine will be connected in the next development phase.',

    processingTitle: 'How Your Audio Will Be Processed',
    processingUpload: 'Securely upload your audio',
    processingSeparate: 'Separate guitar and bass parts',
    processingDetect: 'Detect notes, timing, and tuning',
    processingCreate: 'Generate playable tablature',
    processingPreview: 'Preview the tab before payment',

    privacyTitle: 'Temporary & Private Processing',
    privacyText:
      'Uploaded audio, separated stems, and generated tablature data are stored only while your job is being processed. All temporary files are automatically deleted after delivery or when the processing session expires.',

    paymentTitle: 'Preview Before Payment',
    paymentText:
      'You'll be able to preview your tablature before entering your email address and completing your PayPal purchase. Your printable PDF will then be available for download and emailed to you.',

    seoTitle: 'Convert Audio into Guitar or Bass Tablature',
    seoParagraph1:
      'DadRock Tabs is building an AI-assisted audio-to-tab generator for guitarists and bass players. Upload a recording, choose the instrument part you want, and receive clean, readable tablature that's ready for practice or printing.',
    seoParagraph2:
      'The generator will support lead guitar, rhythm guitar, and bass guitar transcription from common audio formats, including MP3, WAV, and M4A.',

    faqTitle: 'Frequently Asked Questions',
    faqAudioQuestion: 'Which audio formats are supported?',
    faqAudioAnswer:
      'The initial release will support MP3, WAV, and M4A audio files.',
    faqYouTubeQuestion: 'Can I use a YouTube video?',
    faqYouTubeAnswer:
      'You can paste a YouTube link to identify the recording, but the AI will transcribe the audio file that you upload.',
    faqStorageQuestion: 'Will DadRock Tabs keep my audio?',
    faqStorageAnswer:
      'No. Your uploaded audio and temporary processing files are automatically deleted after your transcription has been completed.',
    faqPaymentQuestion: 'When do I pay?',
    faqPaymentAnswer:
      'Payment is only required after your transcription preview is ready.',

    footerDescription:
      'AI-assisted guitar and bass tablature for musicians around the world.',
    backToHome: 'Back to DadRock Tabs',
    copyright: 'DadRock Tabs. All rights reserved.',
  },
};

export function getAiTabTranslation(lang = 'en') {
  return AI_TAB_TRANSLATIONS[lang] || AI_TAB_TRANSLATIONS.en;
}

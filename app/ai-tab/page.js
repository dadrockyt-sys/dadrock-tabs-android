'use client';

import { Suspense, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  ArrowLeft,
  Guitar,
  FileText,
  Sparkles,
} from 'lucide-react';
import PayPalCheckoutButton from '@/components/PayPalCheckoutButton';
import Image from 'next/image';

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();

  const song =
    searchParams.get('song') || 'Selected Song';

  const artist =
    searchParams.get('artist') || 'Unknown Artist';

  const [selectedType, setSelectedType] =
    useState('');

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

  const handleGeneratePreview = async () => {
    if (!selectedType || isGenerating) {
      return;
    }

    setIsGenerating(true);
    setPreviewReady(false);
    setGeneratedTab('');
    setGenerationError('');
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
            song,
            artist,
            transcriptionType: selectedType,
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
          song,
          artist,
          transcriptionType: selectedType,
          generatedTab,
        }),
      }
    );

    if (!response.ok) {
      const data = await response.json();

      throw new Error(
        data.error || 'The PDF could not be generated.'
      );
    }

    const pdfBlob = await response.blob();
    const downloadUrl =
      window.URL.createObjectURL(pdfBlob);

    const disposition =
      response.headers.get('Content-Disposition');

    const fileNameMatch =
      disposition?.match(/filename="([^"]+)"/i);

    const fileName =
      fileNameMatch?.[1] || 'dadrock-ai-tab.pdf';

    const link = document.createElement('a');

    link.href = downloadUrl;
    link.download = fileName;

    document.body.appendChild(link);
    link.click();
    link.remove();

    window.URL.revokeObjectURL(downloadUrl);
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

  const emailIsValid =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
      customerEmail.trim()
    );

  return (
    <main className="min-h-screen bg-gradient-to-b from-black via-zinc-950 to-zinc-900 px-4 py-8 text-white">
      <div className="mx-auto max-w-2xl">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-zinc-400 transition-colors hover:text-amber-400"
        >
          <ArrowLeft className="h-5 w-5" />
          Back to DadRock Tabs
        </Link>

        <section className="overflow-hidden rounded-3xl border border-amber-500/40 bg-zinc-900 shadow-2xl shadow-orange-500/10">
          <div className="bg-gradient-to-r from-amber-500 via-orange-500 to-red-600 p-6">
            <div className="flex items-center gap-3">
              <Guitar className="h-9 w-9 text-white" />

              <div>
                <h1 className="text-2xl font-bold sm:text-3xl">
                  AI Tab Generator
                </h1>

                <p className="mt-1 text-sm text-white/90">
                  Create a printable PDF using AI
                </p>
              </div>
            </div>
          </div>

          <div className="space-y-8 p-6 sm:p-8">
            <div className="rounded-2xl border border-zinc-700 bg-black/40 p-5">
              <p className="text-sm uppercase tracking-wider text-zinc-500">
                Selected song
              </p>

              <h2 className="mt-2 text-2xl font-bold text-white">
                {song}
              </h2>

              <p className="mt-1 text-lg text-amber-400">
                {artist}
              </p>
            </div>

            <div>
              <h2 className="mb-4 text-xl font-bold">
                Choose your transcription
              </h2>

              <div className="space-y-3">
                <button
                  type="button"
                  onClick={() =>
                    setSelectedType('lead')
                  }
                  className={`w-full rounded-xl border p-4 text-left transition-all ${
                    selectedType === 'lead'
                      ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
                      : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
                  }`}
                >
                  <span className="flex items-center justify-between font-bold">
                    <span>🎸 Lead Guitar</span>

                    {selectedType === 'lead' && (
                      <span className="text-amber-400">
                        ✓
                      </span>
                    )}
                  </span>

                  <span className="mt-1 block text-sm text-zinc-400">
                    Solos, lead melodies, bends and fills
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setSelectedType('rhythm')
                  }
                  className={`w-full rounded-xl border p-4 text-left transition-all ${
                    selectedType === 'rhythm'
                      ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
                      : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
                  }`}
                >
                  <span className="flex items-center justify-between font-bold">
                    <span>🎸 Rhythm Guitar</span>

                    {selectedType === 'rhythm' && (
                      <span className="text-amber-400">
                        ✓
                      </span>
                    )}
                  </span>

                  <span className="mt-1 block text-sm text-zinc-400">
                    Riffs, chords and rhythm sections
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setSelectedType('bass')
                  }
                  className={`w-full rounded-xl border p-4 text-left transition-all ${
                    selectedType === 'bass'
                      ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
                      : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
                  }`}
                >
                  <span className="flex items-center justify-between font-bold">
                    <span>🎸 Bass Guitar</span>

                    {selectedType === 'bass' && (
                      <span className="text-amber-400">
                        ✓
                      </span>
                    )}
                  </span>

                  <span className="mt-1 block text-sm text-zinc-400">
                    Bass lines and fills
                  </span>
                </button>
              </div>
            </div>

            <div className="rounded-2xl border border-amber-500/20 bg-amber-500/5 p-5">
              <div className="flex gap-3">
                <Sparkles className="mt-1 h-5 w-5 flex-shrink-0 text-amber-400" />

                <div>
                  <h3 className="font-bold text-amber-400">
                    AI-generated transcription
                  </h3>

                  <p className="mt-1 text-sm leading-relaxed text-zinc-400">
                    You will be able to preview the generated
                    tab before purchasing the printable PDF.
                  </p>
                </div>
              </div>
            </div>

            <button
              type="button"
              disabled={!selectedType || isGenerating}
              onClick={handleGeneratePreview}
              className={`flex w-full items-center justify-center gap-2 rounded-xl py-4 font-bold transition-all ${
                selectedType && !isGenerating
                  ? 'bg-gradient-to-r from-amber-500 to-red-600 text-white hover:scale-[1.02]'
                  : 'cursor-not-allowed bg-zinc-700 text-zinc-400'
              }`}
            >
              <FileText
                className={`h-5 w-5 ${
                  isGenerating ? 'animate-pulse' : ''
                }`}
              />

              {isGenerating
                ? 'AI is creating your preview...'
                : selectedType
                  ? `Generate ${
                      selectedType
                        .charAt(0)
                        .toUpperCase() +
                      selectedType.slice(1)
                    } Tab`
                  : 'Select a transcription'}
            </button>

            <p className="text-center text-xs text-zinc-500">
              PDF download price: $2.99 USD after
              preview
            </p>

            {generationError && (
              <p className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300">
                {generationError}
              </p>
            )}

            {previewReady && (
              <section className="overflow-hidden rounded-2xl border border-amber-500/30 bg-white text-black shadow-xl">
                <div className="border-b-4 border-amber-500 bg-zinc-950 px-5 py-5 text-white">
                  <div className="flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <Image
                        src="/DadRock-Tabs-Logo.png"
                        alt="DadRock Tabs"
                        width={340}
                        height={120}
                        className="mx-auto h-20 w-auto object-contain"
                        priority
                      />

                      <p className="mt-3 text-center text-xs font-semibold uppercase tracking-[0.35em] text-amber-400">
                        AI Guitar Transcription
                      </p>
                    </div>

                    <div className="shrink-0 rounded-full border border-amber-400/60 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-amber-400 sm:px-3 sm:text-xs">
                      Preview
                    </div>
                  </div>
                </div>
                             <div className="p-5 sm:p-7">
                  <div className="border-b-2 border-zinc-900 pb-5">
                    <p className="text-xs font-bold uppercase tracking-[0.2em] text-amber-600">
                      Printable Guitar Tab
                    </p>

                    <h2 className="mt-2 text-3xl font-black leading-tight text-zinc-950">
                      {song}
                    </h2>

                    <p className="mt-1 text-xl font-semibold text-zinc-600">
                      {artist}
                    </p>

                    <div className="mt-5 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
                      <div className="rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                        <p className="text-xs font-bold uppercase text-zinc-500">
                          Instrument
                        </p>

                        <p className="mt-1 font-bold capitalize text-zinc-900">
                          {selectedType}
                        </p>
                      </div>

                      <div className="rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                        <p className="text-xs font-bold uppercase text-zinc-500">
                          Tuning
                        </p>

                        <p className="mt-1 font-bold text-zinc-900">
                          Standard
                        </p>
                      </div>

                      <div className="rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                        <p className="text-xs font-bold uppercase text-zinc-500">
                          Difficulty
                        </p>

                        <p className="mt-1 font-bold text-zinc-900">
                          Intermediate
                        </p>
                      </div>

                      <div className="rounded-lg border border-zinc-300 bg-zinc-50 p-3">
                        <p className="text-xs font-bold uppercase text-zinc-500">
                          Format
                        </p>

                        <p className="mt-1 font-bold text-zinc-900">
                          Guitar TAB
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="relative mt-6 overflow-hidden border-y-2 border-black bg-white px-5 py-8 font-mono text-[13px] leading-6 sm:px-8 sm:text-sm sm:leading-7">
                    <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                      <span className="-rotate-12 text-5xl font-black text-zinc-300/40">
                        PREVIEW
                      </span>
                    </div>

                    <pre className="relative z-10 mx-auto max-w-full overflow-x-auto whitespace-pre font-mono text-black">
                      {generatedTab}
                    </pre>
                  </div>

                  {!paymentCompleted ? (
                    <div className="mt-5 rounded-xl border border-zinc-300 bg-zinc-50 p-4">
                      <h3 className="mb-3 text-center font-bold text-black">
                        Unlock the printable PDF — $2.99 USD
                      </h3>

                      <div className="mb-4">
                        <label
                          htmlFor="customer-email"
                          className="mb-2 block text-sm font-bold text-zinc-800"
                        >
                          Email address for PDF delivery
                        </label>

                        <input
                          id="customer-email"
                          type="email"
                          value={customerEmail}
                          onChange={(event) =>
                            setCustomerEmail(event.target.value)
                          }
                          placeholder="you@example.com"
                          autoComplete="email"
                          required
                          className="w-full rounded-xl border border-zinc-300 bg-white px-4 py-3 text-black outline-none transition focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20"
                        />

                        <p className="mt-2 text-xs leading-relaxed text-zinc-500">
                          Your PDF will be emailed once and then deleted from
                          temporary server storage. Please keep your emailed
                          copy because it cannot be recovered later.
                        </p>
                      </div>

                      {emailIsValid ? (
                        <PayPalCheckoutButton
                          song={song}
                          artist={artist}
                          transcriptionType={selectedType}
                          customerEmail={customerEmail.trim()}
                          onPaymentCompleted={(result) => {
  const receivedOrderId = result?.orderId || '';

  alert(
    receivedOrderId
      ? `PayPal order received: ${receivedOrderId}`
      : 'ERROR: PayPal order ID was not received.'
  );

  setPurchaseOrderId(receivedOrderId);
  setPaymentCompleted(true);
}}
                        />
                      ) : (
                        <p className="rounded-lg border border-amber-500/30 bg-amber-500/10 p-3 text-center text-sm text-amber-700">
                          Enter a valid email address to continue to PayPal.
                        </p>
                      )}
                    </div>
                  ) : (
                                        <div className="mt-5 space-y-3">
                      <div className="rounded-xl border border-green-500/40 bg-green-500/10 p-4 text-center">
                        <p className="font-bold text-green-700">
                          ✓ Payment completed
                        </p>

                        <p className="mt-1 text-sm text-zinc-600">
                          Your printable tab is unlocked and
                          will be emailed to:
                        </p>

                        <p className="mt-1 break-all text-sm font-bold text-zinc-900">
                          {customerEmail}
                        </p>
                      </div>

                      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
                        <button
                          type="button"
                          onClick={() =>
                            alert(
                              'The finished PDF download will be connected next.'
                            )
                          }
                          className="rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 px-4 py-3 font-bold text-white"
                        >
                          Download PDF
                        </button>

                        <button
                          type="button"
                          onClick={() => window.print()}
                          className="rounded-xl border border-zinc-400 bg-zinc-100 px-4 py-3 font-bold text-black"
                        >
                          Print Tab
                        </button>
                      </div>

                      <p className="text-center text-xs leading-relaxed text-zinc-500">
                        Your PDF will be emailed once and then
                        removed from temporary server storage.
                      </p>
                    </div>
                  )}
                </div>
              </section>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export default function AiTabGeneratorPage() {
  return (
    <Suspense
      fallback={
        <main className="min-h-screen bg-black p-8 text-center text-white">
          Loading AI Tab Generator…
        </main>
      }
    >
      <AiTabGeneratorContent />
    </Suspense>
  );
}

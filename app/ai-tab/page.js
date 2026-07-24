'use client';

import { Suspense, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { ArrowLeft, Guitar, FileText, Sparkles } from 'lucide-react';

function AiTabGeneratorContent() {
  const searchParams = useSearchParams();

  const song = searchParams.get('song') || 'Selected Song';
  const artist = searchParams.get('artist') || 'Unknown Artist';
  const [selectedType, setSelectedType] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
const [previewReady, setPreviewReady] = useState(false);
  const handleGeneratePreview = () => {
  if (!selectedType || isGenerating) return;

  setIsGenerating(true);
  setPreviewReady(false);

  setTimeout(() => {
    setIsGenerating(false);
    setPreviewReady(true);
  }, 2500);
};

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
    onClick={() => setSelectedType('lead')}
    className={`w-full rounded-xl border p-4 text-left transition-all ${
      selectedType === 'lead'
        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
        : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
    }`}
  >
    <span className="flex items-center justify-between font-bold">
      <span>🎸 Lead Guitar</span>
      {selectedType === 'lead' && <span className="text-amber-400">✓</span>}
    </span>
    <span className="mt-1 block text-sm text-zinc-400">
      Solos, lead melodies, bends and fills
    </span>
  </button>

  <button
    type="button"
    onClick={() => setSelectedType('rhythm')}
    className={`w-full rounded-xl border p-4 text-left transition-all ${
      selectedType === 'rhythm'
        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
        : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
    }`}
  >
    <span className="flex items-center justify-between font-bold">
      <span>🎸 Rhythm Guitar</span>
      {selectedType === 'rhythm' && <span className="text-amber-400">✓</span>}
    </span>
    <span className="mt-1 block text-sm text-zinc-400">
      Riffs, chords and rhythm sections
    </span>
  </button>

  <button
    type="button"
    onClick={() => setSelectedType('bass')}
    className={`w-full rounded-xl border p-4 text-left transition-all ${
      selectedType === 'bass'
        ? 'border-amber-400 bg-amber-500/15 shadow-lg shadow-amber-500/20'
        : 'border-zinc-700 bg-zinc-800 hover:border-amber-500 hover:bg-zinc-700'
    }`}
  >
    <span className="flex items-center justify-between font-bold">
      <span>🎸 Bass Guitar</span>
      {selectedType === 'bass' && <span className="text-amber-400">✓</span>}
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
                    You will be able to preview the generated tab before
                    purchasing the printable PDF.
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
  <FileText className={`h-5 w-5 ${isGenerating ? 'animate-pulse' : ''}`} />

  {isGenerating
    ? 'AI is creating your preview...'
    : selectedType
      ? `Generate ${
          selectedType.charAt(0).toUpperCase() + selectedType.slice(1)
        } Tab`
      : 'Select a transcription'}
</button>

            <p className="text-center text-xs text-zinc-500">
              PDF download price: $2.99 USD after preview
            </p>
          </div>
        </section>
      </div>
    </main>
  );
}
{previewReady && (
  <section className="rounded-2xl border border-amber-500/30 bg-white p-5 text-black shadow-xl">
    <div className="mb-5 border-b border-zinc-300 pb-4 text-center">
      <p className="text-xs font-bold uppercase tracking-widest text-zinc-500">
        DadRock Tabs AI Preview
      </p>

      <h2 className="mt-2 text-2xl font-bold">
        {song}
      </h2>

      <p className="text-zinc-600">
        {artist} — {selectedType.charAt(0).toUpperCase() + selectedType.slice(1)} Tab
      </p>
    </div>

    <div className="relative overflow-hidden rounded-xl border border-zinc-300 bg-white p-4 font-mono text-sm leading-7">
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <span className="-rotate-12 text-5xl font-black text-zinc-300/40">
          PREVIEW
        </span>
      </div>

      <pre className="relative z-10 overflow-x-auto whitespace-pre">
{`e|----------------|----------------|
B|------8b10------|--8-------------|
G|--7h9-----------|-----9--7--------|
D|----------------|-----------9--7--|
A|----------------|----------------|
E|----------------|----------------|

e|----------------|----------------|
B|----------------|----------------|
G|--7-------------|--7h9--7--------|
D|-----9--7-------|----------9--7---|
A|-----------9----|----------------|
E|----------------|----------------|`}
      </pre>
    </div>

    <div className="mt-5 grid grid-cols-1 gap-3 sm:grid-cols-2">
      <button
        type="button"
        onClick={() =>
          alert('PayPal checkout for $2.99 USD will open here.')
        }
        className="rounded-xl bg-gradient-to-r from-amber-500 to-orange-600 px-4 py-3 font-bold text-white"
      >
        Download PDF — $2.99 USD
      </button>

      <button
        type="button"
        onClick={() =>
          alert('Payment will be required before printing.')
        }
        className="rounded-xl border border-zinc-400 bg-zinc-100 px-4 py-3 font-bold text-black"
      >
        Print Tab — $2.99 USD
      </button>
    </div>
  </section>
)}

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

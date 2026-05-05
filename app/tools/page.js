'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';

// ─── METRONOME ───
function Metronome() {
  const [bpm, setBpm] = useState(120);
  const [playing, setPlaying] = useState(false);
  const [beat, setBeat] = useState(0);
  const [timeSignature, setTimeSignature] = useState(4);
  const intervalRef = useRef(null);
  const audioCtxRef = useRef(null);

  const playClick = useCallback((accent = false) => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    const ctx = audioCtxRef.current;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.frequency.value = accent ? 1000 : 800;
    gain.gain.setValueAtTime(accent ? 0.5 : 0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.05);
  }, []);

  useEffect(() => {
    if (playing) {
      let currentBeat = 0;
      const tick = () => {
        playClick(currentBeat === 0);
        setBeat(currentBeat);
        currentBeat = (currentBeat + 1) % timeSignature;
      };
      tick();
      intervalRef.current = setInterval(tick, 60000 / bpm);
    } else {
      if (intervalRef.current) clearInterval(intervalRef.current);
      setBeat(0);
    }
    return () => { if (intervalRef.current) clearInterval(intervalRef.current); };
  }, [playing, bpm, timeSignature, playClick]);

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🥁 Metronome</h3>
      
      {/* BPM Display */}
      <div className="text-center mb-4">
        <span className="text-5xl font-bold text-white">{bpm}</span>
        <span className="text-gray-400 ml-2">BPM</span>
      </div>

      {/* Beat indicators */}
      <div className="flex justify-center gap-2 mb-4">
        {Array.from({ length: timeSignature }).map((_, i) => (
          <div
            key={i}
            className={`w-4 h-4 rounded-full transition-all ${
              playing && beat === i
                ? i === 0 ? 'bg-red-500 scale-125' : 'bg-orange-400 scale-110'
                : 'bg-gray-600'
            }`}
          />
        ))}
      </div>

      {/* BPM Slider */}
      <input
        type="range"
        min="40"
        max="240"
        value={bpm}
        onChange={(e) => setBpm(Number(e.target.value))}
        className="w-full mb-4 accent-orange-500"
      />

      {/* Controls */}
      <div className="flex gap-3 justify-center items-center">
        <select
          value={timeSignature}
          onChange={(e) => setTimeSignature(Number(e.target.value))}
          className="bg-gray-700 border border-gray-600 text-white px-3 py-2 rounded-lg text-sm"
        >
          <option value={3}>3/4</option>
          <option value={4}>4/4</option>
          <option value={6}>6/8</option>
        </select>
        <button
          onClick={() => setPlaying(!playing)}
          className={`px-6 py-3 rounded-lg font-bold text-lg transition-all ${
            playing
              ? 'bg-red-600 hover:bg-red-700 text-white'
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {playing ? '⏹ Stop' : '▶ Start'}
        </button>
        <div className="flex gap-1">
          <button onClick={() => setBpm(Math.max(40, bpm - 5))} className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white">-5</button>
          <button onClick={() => setBpm(Math.min(240, bpm + 5))} className="px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white">+5</button>
        </div>
      </div>

      {/* Common tempos */}
      <div className="flex flex-wrap gap-2 mt-4 justify-center">
        {[60, 80, 100, 120, 140, 160, 180, 200].map(t => (
          <button
            key={t}
            onClick={() => setBpm(t)}
            className={`px-2 py-1 text-xs rounded ${
              bpm === t ? 'bg-orange-500 text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}

// ─── GUITAR TUNER ───
function GuitarTuner() {
  const [activeString, setActiveString] = useState(null);
  const audioCtxRef = useRef(null);
  const oscRef = useRef(null);

  const strings = [
    { name: 'E2', freq: 82.41, label: '6th (Low E)' },
    { name: 'A2', freq: 110.00, label: '5th (A)' },
    { name: 'D3', freq: 146.83, label: '4th (D)' },
    { name: 'G3', freq: 196.00, label: '3rd (G)' },
    { name: 'B3', freq: 246.94, label: '2nd (B)' },
    { name: 'E4', freq: 329.63, label: '1st (High E)' },
  ];

  const playString = (string) => {
    if (!audioCtxRef.current) {
      audioCtxRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    // Stop previous
    if (oscRef.current) {
      try { oscRef.current.stop(); } catch(e) {}
    }

    const ctx = audioCtxRef.current;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.type = 'sawtooth';
    osc.frequency.value = string.freq;
    gain.gain.setValueAtTime(0.3, ctx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 2);
    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 2);
    oscRef.current = osc;
    setActiveString(string.name);
    setTimeout(() => setActiveString(null), 2000);
  };

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🎵 Reference Tuner</h3>
      <p className="text-gray-400 text-sm mb-4">Click a string to hear its reference pitch. Tune your guitar by ear.</p>
      
      <div className="space-y-2">
        {strings.map(s => (
          <button
            key={s.name}
            onClick={() => playString(s)}
            className={`w-full flex items-center justify-between px-4 py-3 rounded-lg transition-all ${
              activeString === s.name
                ? 'bg-orange-500/20 border-2 border-orange-500 text-orange-300'
                : 'bg-gray-700/50 border-2 border-gray-600 hover:border-orange-500/50 text-gray-200'
            }`}
          >
            <span className="font-bold text-lg">{s.name}</span>
            <span className="text-sm text-gray-400">{s.label}</span>
            <span className="text-xs text-gray-500">{s.freq} Hz</span>
            {activeString === s.name && (
              <span className="animate-pulse text-orange-400">♪</span>
            )}
          </button>
        ))}
      </div>

      <p className="text-xs text-gray-500 mt-4">Standard tuning: E A D G B E</p>
    </div>
  );
}

// ─── CHORD REFERENCE ───
function ChordReference() {
  const [selectedChord, setSelectedChord] = useState('C');

  const chords = {
    'C':  { frets: ['x', 3, 2, 0, 1, 0], fingers: 'x32010' },
    'D':  { frets: ['x', 'x', 0, 2, 3, 2], fingers: 'xx0232' },
    'E':  { frets: [0, 2, 2, 1, 0, 0], fingers: '022100' },
    'G':  { frets: [3, 2, 0, 0, 0, 3], fingers: '320003' },
    'A':  { frets: ['x', 0, 2, 2, 2, 0], fingers: 'x02220' },
    'Am': { frets: ['x', 0, 2, 2, 1, 0], fingers: 'x02210' },
    'Em': { frets: [0, 2, 2, 0, 0, 0], fingers: '022000' },
    'Dm': { frets: ['x', 'x', 0, 2, 3, 1], fingers: 'xx0231' },
    'F':  { frets: [1, 1, 2, 3, 3, 1], fingers: '133211' },
    'B7': { frets: ['x', 2, 1, 2, 0, 2], fingers: 'x21202' },
    'C7': { frets: ['x', 3, 2, 3, 1, 0], fingers: 'x32310' },
    'A7': { frets: ['x', 0, 2, 0, 2, 0], fingers: 'x02020' },
  };

  const chord = chords[selectedChord];

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🎼 Chord Reference</h3>
      
      {/* Chord selector */}
      <div className="flex flex-wrap gap-2 mb-6">
        {Object.keys(chords).map(c => (
          <button
            key={c}
            onClick={() => setSelectedChord(c)}
            className={`px-3 py-2 rounded-lg font-bold text-sm transition-all ${
              selectedChord === c
                ? 'bg-orange-500 text-white'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            {c}
          </button>
        ))}
      </div>

      {/* Chord diagram */}
      <div className="bg-gray-900 rounded-lg p-4 text-center">
        <h4 className="text-2xl font-bold text-white mb-4">{selectedChord}</h4>
        <div className="inline-block">
          {/* String labels */}
          <div className="flex gap-4 justify-center mb-2">
            {['E', 'A', 'D', 'G', 'B', 'e'].map((s, i) => (
              <span key={i} className="w-8 text-center text-xs text-gray-400">{s}</span>
            ))}
          </div>
          {/* Frets */}
          <div className="flex gap-4 justify-center">
            {chord.frets.map((fret, i) => (
              <div key={i} className="w-8 text-center">
                <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-sm font-bold ${
                  fret === 'x' ? 'text-red-400' : fret === 0 ? 'text-green-400 border border-green-400' : 'bg-orange-500 text-white'
                }`}>
                  {fret === 'x' ? '✕' : fret === 0 ? 'O' : fret}
                </span>
              </div>
            ))}
          </div>
        </div>
        <p className="text-gray-500 text-xs mt-4">Fret positions from nut (0 = open, x = mute)</p>
      </div>
    </div>
  );
}

// ─── MAIN TOOLS PAGE ───
export default function ToolsPage() {
  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 py-4 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="text-orange-400 hover:text-orange-300 flex items-center gap-2">
            ← Back to Home
          </Link>
          <h1 className="text-xl font-bold text-orange-400">🎸 Guitar Tools</h1>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-2">Free Guitar Tools</h2>
          <p className="text-gray-400">Everything you need to practice — no apps to download, no signup required.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Metronome />
          <GuitarTuner />
        </div>

        <div className="mt-8">
          <ChordReference />
        </div>

        {/* SEO Content */}
        <div className="mt-12 prose prose-invert max-w-none">
          <h2 className="text-xl font-bold text-orange-400">Why Use These Tools?</h2>
          <p className="text-gray-400">
            Every guitarist needs a metronome for timing, a tuner for pitch accuracy, and a chord reference for learning new shapes. 
            These free browser-based tools require no downloads or signups — just bookmark this page and use them whenever you practice.
          </p>
          <p className="text-gray-400">
            The metronome supports common time signatures and tempos from 40-240 BPM. The reference tuner plays standard tuning pitches (E A D G B E). 
            The chord reference shows finger positions for the most common open chords.
          </p>
        </div>
      </main>
    </div>
  );
}

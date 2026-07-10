'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';

// ─── METRONOME ───
function Metronome({ lang = 'en' }) {
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
  const metronomeT = {
  en: { title: 'Metronome', start: 'Start', stop: 'Stop' },
  es: { title: 'Metrónomo', start: 'Iniciar', stop: 'Detener' },
  fr: { title: 'Métronome', start: 'Démarrer', stop: 'Arrêter' },
  de: { title: 'Metronom', start: 'Start', stop: 'Stopp' }
  it: { title: 'Metronomo', start: 'Avvia', stop: 'Stop' },
  pt: { title: 'Metrônomo', start: 'Iniciar', stop: 'Parar' },
  'pt-br': { title: 'Metrônomo', start: 'Iniciar', stop: 'Parar' },
  ja: { title: 'メトロノーム', start: '開始', stop: '停止' },
  ko: { title: '메트로놈', start: '시작', stop: '정지' },
  zh: { title: '节拍器', start: '开始', stop: '停止' },
  ru: { title: 'Метроном', start: 'Старт', stop: 'Стоп' },
  hi: { title: 'मेट्रोनोम', start: 'शुरू', stop: 'रोकें' },
  sv: { title: 'Metronom', start: 'Start', stop: 'Stopp' },
  fi: { title: 'Metronomi', start: 'Käynnistä', stop: 'Pysäytä' }
}:

const mt = metronomeT[lang] || metronomeT.en;

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🥁 {mt.title}</h3>
      
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
          {playing ? `⏹ ${mt.stop}` : `▶ ${mt.start}`}
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
function GuitarTuner({ lang = 'en' }) {
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
  
    const tunerT = {
  en: {
    title: 'Reference Tuner',
    text: 'Click a string to hear its reference pitch. Tune your guitar by ear.',
    standard: 'Standard tuning: E A D G B E'
  },
  es: {
    title: 'Afinador de referencia',
    text: 'Haz clic en una cuerda para escuchar su tono de referencia. Afina tu guitarra de oído.',
    standard: 'Afinación estándar: E A D G B E'
  },
  fr: {
    title: 'Accordeur de référence',
    text: 'Cliquez sur une corde pour entendre sa hauteur de référence. Accordez votre guitare à l’oreille.',
    standard: 'Accordage standard : E A D G B E'
  },
  de: {
    title: 'Referenz-Stimmgerät',
    text: 'Klicke auf eine Saite, um ihren Referenzton zu hören. Stimme deine Gitarre nach Gehör.',
    standard: 'Standardstimmung: E A D G B E'
  }
};

const gt = tunerT[lang] || tunerT.en;

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🎵 {gt.title}</h3>
<p className="text-gray-400 text-sm mb-4">{gt.text}</p>
      
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

     <p className="text-xs text-gray-500 mt-4">{gt.standard}</p>
    </div>
  );
}

// ─── CHORD REFERENCE ───
function ChordReference({ lang = 'en' }) {
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
  const chordT = {
  en: { title: 'Chord Reference', frets: 'Frets', fingers: 'Fingers', fretInfo: 'Fret positions from nut (0 = open, x = mute)' },
  es: { title: 'Referencia de acordes', frets: 'Trastes', fingers: 'Dedos', fretInfo: 'Posiciones de los trastes desde la cejuela (0 = al aire, x = silenciada)' },
  fr: { title: 'Référence des accords', frets: 'Frettes', fingers: 'Doigts', fretInfo: 'Positions des frettes depuis le sillet (0 = corde à vide, x = corde étouffée)' },
  de: { title: 'Akkordreferenz', frets: 'Bünde', fingers: 'Finger', fretInfo: 'Bundpositionen vom Sattel (0 = leer, x = gedämpft)' },
  it: { title: 'Riferimento accordi', frets: 'Tasti', fingers: 'Dita', fretInfo: 'Posizioni dei tasti dal capotasto (0 = corda a vuoto, x = corda muta)' },
  pt: { title: 'Referência de acordes', frets: 'Trastes', fingers: 'Dedos', fretInfo: 'Posições dos trastes a partir da pestana (0 = corda solta, x = abafada)' },
  'pt-br': { title: 'Referência de acordes', frets: 'Trastes', fingers: 'Dedos', fretInfo: 'Posições dos trastes a partir da pestana (0 = corda solta, x = abafada)' },
  ja: { title: 'コードリファレンス', frets: 'フレット', fingers: '指', fretInfo: 'ナットからのフレット位置（0 = 開放弦、x = ミュート）' },
  ko: { title: '코드 참조', frets: '프렛', fingers: '손가락', fretInfo: '너트 기준 프렛 위치 (0 = 개방현, x = 뮤트)' },
  zh: { title: '和弦参考', frets: '品格', fingers: '手指', fretInfo: '从弦枕开始的品位位置（0 = 空弦，x = 闷音）' },
  ru: { title: 'Справочник аккордов', frets: 'Лады', fingers: 'Пальцы', fretInfo: 'Позиции ладов от верхнего порожка (0 = открытая струна, x = приглушено)' },
  hi: { title: 'कॉर्ड संदर्भ', frets: 'फ्रेट्स', fingers: 'उंगलियाँ', fretInfo: 'नट से फ्रेट की स्थिति (0 = खुली स्ट्रिंग, x = म्यूट)' },
  sv: { title: 'Ackordreferens', frets: 'Band', fingers: 'Fingrar', fretInfo: 'Bandpositioner från sadeln (0 = öppen sträng, x = dämpad)' },
  fi: { title: 'Sointuviite', frets: 'Nauhat', fingers: 'Sormet', fretInfo: 'Nauhojen sijainnit satulasta (0 = avoin kieli, x = mykistetty)' }
};

const ct = chordT[lang] || chordT.en;

  return (
    <div className="bg-gray-800/50 border border-orange-500/30 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">🎼 {ct.title}</h3>
      
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
        <p className="text-sm text-zinc-500 mt-4">
  {ct.fretInfo}
</p>
      </div>
    </div>
  );
}

// ─── MAIN TOOLS PAGE ───
export default function ToolsPage() {
  const { lang } = useLanguage();
const pathname = usePathname();
const pathLocale = pathname.split('/')[1];
const currentLang = pathLocale && pathLocale !== 'tools' ? pathLocale : lang;

const toolsT = {
  en: {
    backHome: '← Back To Home',
    pageTitle: '🎸 Guitar Tools',
    heroTitle: 'Free Guitar Tools',
    heroText: 'Everything you need to practice — no apps to download, no signup required.',
    seoTitle: 'Why Use These Tools?',
    seoP1: 'Every guitarist needs a metronome for timing, a tuner for pitch accuracy, and a chord reference for learning new shapes. These free browser-based tools require no downloads or signups — just bookmark this page and use them whenever you practice.',
    seoP2: 'The metronome supports common time signatures and tempos from 40-240 BPM. The reference tuner plays standard tuning pitches (E A D G B E). The chord reference shows finger positions for the most common open chords.',
  },
  fr: {
    backHome: "← Retour à l'accueil",
    pageTitle: '🎸 Outils de guitare',
    heroTitle: 'Outils de guitare gratuits',
    heroText: 'Tout ce dont vous avez besoin pour pratiquer — aucune application à télécharger, aucune inscription requise.',
    seoTitle: 'Pourquoi utiliser ces outils ?',
    seoP1: "Chaque guitariste a besoin d'un métronome pour le rythme, d'un accordeur pour la justesse et d'une référence d'accords pour apprendre de nouvelles positions.",
    seoP2: "Le métronome prend en charge les signatures rythmiques courantes et les tempos de 40 à 240 BPM. L'accordeur joue les notes d'accordage standard.",
  },
  es: {
    backHome: '← Volver al inicio',
    pageTitle: '🎸 Herramientas de guitarra',
    heroTitle: 'Herramientas de guitarra gratis',
    heroText: 'Todo lo que necesitas para practicar — sin descargar apps ni registrarte.',
    seoTitle: '¿Por qué usar estas herramientas?',
    seoP1: 'Todo guitarrista necesita un metrónomo, un afinador y una referencia de acordes para practicar mejor.',
    seoP2: 'El metrónomo admite tempos de 40 a 240 BPM. El afinador reproduce la afinación estándar de guitarra.',
  },
  de: {
    backHome: '← Zurück zur Startseite',
    pageTitle: '🎸 Gitarren-Tools',
    heroTitle: 'Kostenlose Gitarren-Tools',
    heroText: 'Alles, was du zum Üben brauchst — keine App, keine Anmeldung.',
    seoTitle: 'Warum diese Tools verwenden?',
    seoP1: 'Jeder Gitarrist braucht ein Metronom, ein Stimmgerät und eine Akkordübersicht zum Üben.',
    seoP2: 'Das Metronom unterstützt Tempi von 40 bis 240 BPM. Das Stimmgerät spielt die Standardstimmung.',
  },
it: {
  backHome: '← Torna alla home',
  pageTitle: '🎸 Strumenti per chitarra',
  heroTitle: 'Strumenti gratuiti per chitarra',
  heroText: 'Tutto ciò che ti serve per esercitarti: nessuna app da scaricare e nessuna registrazione richiesta.',
  seoTitle: 'Perché usare questi strumenti?',
  seoP1: 'Ogni chitarrista ha bisogno di un metronomo per il tempo, di un accordatore per l’intonazione e di un riferimento per gli accordi.',
  seoP2: 'Il metronomo supporta tempi da 40 a 240 BPM. L’accordatore riproduce l’accordatura standard (E A D G B E). Il riferimento degli accordi mostra le diteggiature degli accordi aperti più comuni.'
},
pt: {
  backHome: '← Voltar ao início',
  pageTitle: '🎸 Ferramentas para guitarra',
  heroTitle: 'Ferramentas gratuitas para guitarra',
  heroText: 'Tudo o que você precisa para praticar — sem aplicativos, sem downloads e sem cadastro.',
  seoTitle: 'Por que usar estas ferramentas?',
  seoP1: 'Todo guitarrista precisa de um metrônomo para ritmo, um afinador para precisão de afinação e uma referência de acordes.',
  seoP2: 'O metrônomo suporta tempos de 40–240 BPM. O afinador reproduz a afinação padrão (E A D G B E). A referência de acordes mostra as posições dos dedos para os acordes abertos mais comuns.'
},
'pt-br': {
  backHome: '← Voltar ao início',
  pageTitle: '🎸 Ferramentas para guitarra',
  heroTitle: 'Ferramentas gratuitas para guitarra',
  heroText: 'Tudo o que você precisa para praticar — sem aplicativos, sem downloads e sem cadastro.',
  seoTitle: 'Por que usar estas ferramentas?',
  seoP1: 'Todo guitarrista precisa de um metrônomo para ritmo, um afinador para precisão de afinação e uma referência de acordes.',
  seoP2: 'O metrônomo suporta tempos de 40–240 BPM. O afinador reproduz a afinação padrão (E A D G B E). A referência de acordes mostra as posições dos dedos para os acordes abertos mais comuns.'
},
ja: {
  backHome: '← ホームへ戻る',
  pageTitle: '🎸 ギターツール',
  heroTitle: '無料ギターツール',
  heroText: '練習に必要なものがすべてここに。ダウンロードも登録も不要です。',
  seoTitle: 'これらのツールを使う理由',
  seoP1: 'すべてのギタリストにメトロノーム、チューナー、コードリファレンスは欠かせません。',
  seoP2: 'メトロノームは40〜240 BPMに対応しています。チューナーは標準チューニング（E A D G B E）を再生します。'
},
ko: {
  backHome: '← 홈으로',
  pageTitle: '🎸 기타 도구',
  heroTitle: '무료 기타 도구',
  heroText: '연습에 필요한 모든 것. 다운로드나 회원가입이 필요 없습니다.',
  seoTitle: '왜 이 도구를 사용해야 할까요?',
  seoP1: '모든 기타리스트에게는 메트로놈, 튜너, 코드 참고 자료가 필요합니다.',
  seoP2: '메트로놈은 40~240 BPM을 지원합니다. 튜너는 표준 튜닝(E A D G B E)을 재생합니다.'
},
zh: {
  backHome: '← 返回首页',
  pageTitle: '🎸 吉他工具',
  heroTitle: '免费吉他工具',
  heroText: '练习所需的一切——无需下载，无需注册。',
  seoTitle: '为什么使用这些工具？',
  seoP1: '每位吉他手都需要节拍器、调音器和和弦参考。',
  seoP2: '节拍器支持40–240 BPM。调音器播放标准调弦（E A D G B E）。'
},
ru: {
  backHome: '← Назад домой',
  pageTitle: '🎸 Гитарные инструменты',
  heroTitle: 'Бесплатные гитарные инструменты',
  heroText: 'Всё, что нужно для занятий — без скачивания и регистрации.',
  seoTitle: 'Зачем использовать эти инструменты?',
  seoP1: 'Каждому гитаристу нужны метроном, тюнер и справочник аккордов.',
  seoP2: 'Метроном поддерживает темп от 40 до 240 BPM. Тюнер воспроизводит стандартный строй (E A D G B E).'
},
hi: {
  backHome: '← होम पर वापस जाएँ',
  pageTitle: '🎸 गिटार टूल्स',
  heroTitle: 'निःशुल्क गिटार टूल्स',
  heroText: 'अभ्यास के लिए ज़रूरी सब कुछ — बिना डाउनलोड और बिना साइन-अप।',
  seoTitle: 'इन टूल्स का उपयोग क्यों करें?',
  seoP1: 'हर गिटारवादक को मेट्रोनोम, ट्यूनर और कॉर्ड संदर्भ की आवश्यकता होती है।',
  seoP2: 'मेट्रोनोम 40–240 BPM का समर्थन करता है। ट्यूनर मानक ट्यूनिंग (E A D G B E) बजाता है।'
},
sv: {
  backHome: '← Tillbaka till startsidan',
  pageTitle: '🎸 Gitarrverktyg',
  heroTitle: 'Gratis gitarrverktyg',
  heroText: 'Allt du behöver för att öva – inga nedladdningar eller registrering krävs.',
  seoTitle: 'Varför använda dessa verktyg?',
  seoP1: 'Varje gitarrist behöver en metronom, en stämapparat och ett ackordreferensverktyg.',
  seoP2: 'Metronomen stöder 40–240 BPM. Stämapparaten spelar standardstämning (E A D G B E).'
},
fi: {
  backHome: '← Takaisin etusivulle',
  pageTitle: '🎸 Kitaratyökalut',
  heroTitle: 'Ilmaiset kitaratyökalut',
  heroText: 'Kaikki mitä tarvitset harjoitteluun – ei latauksia eikä rekisteröitymistä.',
  seoTitle: 'Miksi käyttää näitä työkaluja?',
  seoP1: 'Jokainen kitaristi tarvitsee metronomin, virittimen ja sointuviitteen.',
  seoP2: 'Metronomi tukee 40–240 BPM:n tempoja. Viritin soittaa vakiovirityksen (E A D G B E).'
}
};

const t = toolsT[currentLang] || toolsT[lang] || toolsT.en;
const homeHref = currentLang === 'en' ? '/' : `/${currentLang}`;
  
  return (
    
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <header className="border-b border-gray-800 py-4 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href={homeHref} className="text-orange-400 hover:text-orange-300 flex items-center gap-2">
            {t.backHome}
          </Link>
          <div className="flex items-center gap-3">
  <h1 className="text-xl font-bold text-white">{t.pageTitle}</h1>
  <LanguageSelector
  onLanguageChange={(newLang) => {
    window.location.href = newLang === 'en'
      ? '/tools'
      : `/${newLang}/tools`;
  }}
/>
</div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-white mb-3">{t.heroTitle}</h2>
          <p className="text-gray-400">{t.heroText}</p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          <Metronome lang={currentLang} />
          <GuitarTuner lang={currentLang} />
        </div>

        <div className="mt-8">
          <ChordReference lang={currentLang} />
        </div>

        {/* SEO Content */}
        <div className="mt-12 prose prose-invert max-w-none">
          <h2 className="text-2xl font-bold mb-4">{t.seoTitle}</h2>
          <p className="text-gray-400">{t.seoP1}</p>
          <p className="text-gray-400">{t.seoP2}</p>
        </div>
      </main>
    </div>
  );
}

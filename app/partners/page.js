'use client';

import Link from 'next/link';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';

function getLocalizedPath(path, lang) {
  if (!lang || lang === 'en') return path;
  return `/${lang}${path}`;
}

const LOGO_URL = "/dadrock-logo.png";
const YOUTUBE_URL = "https://youtube.com/@dadrockytofficial?si=TjBWK-QMUu7vdcrI";

export default function PartnersPage() {
  const [selectedLang] = useLanguage();
  const currentLang = selectedLang || 'en';
  const t = getSubPageTranslation(currentLang);
  
  const stats = [
  ["75K+", t.youtubeSubscribers, "🎸"],
  ["723K+", t.monthlyYouTubeViews, "👁️"],
  ["231K+", t.monthlyAudience, "👥"],
  ["3,200+", t.lessonVideos, "▶️"],
  ["371", t.artistsCovered, "🎶"],
  ["732+", t.indexedWebsitePages, "🌎"],
];

  const opportunities = [
  [t.sponsoredLessons, t.sponsoredLessonsDescription, "🎸"],
  [t.productReviews, t.productReviewsDescription, "🎛️"],
  [t.affiliateCampaigns, t.affiliateCampaignsDescription, "🔗"],
  [t.websitePlacement, t.websitePlacementDescription, "🖥️"],
  [t.androidAppPromotion, t.androidAppPromotionDescription, "📱"],
  [t.giveaways, t.giveawaysDescription, "🎁"],
];

  const brands = [
    "Fender",
    "Gibson",
    "Ernie Ball",
    "Dunlop",
    "Boss",
    "Positive Grid",
    "Sweetwater",
    "Thomann",
    "D'Addario",
    "Elixir",
    "IK Multimedia",
    "Neural DSP",
  ];

  return (
    <main className="min-h-screen bg-black text-white overflow-hidden px-4 py-6">
      <div className="fixed inset-0 pointer-events-none opacity-40">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(245,158,11,0.22),transparent_35%),radial-gradient(circle_at_top_right,rgba(251,191,36,0.18),transparent_30%),radial-gradient(circle_at_bottom,rgba(180,83,9,0.18),transparent_35%)]" />
        <span className="absolute top-28 left-[10%] text-amber-400 text-5xl animate-pulse">♪</span>
        <span className="absolute top-40 right-[16%] text-amber-400 text-6xl animate-pulse">♫</span>
        <span className="absolute top-[38%] left-[85%] text-amber-400 text-4xl animate-pulse">♪</span>
        <span className="absolute bottom-32 left-[20%] text-amber-400 text-4xl animate-pulse">♫</span>
      </div>

      <header className="max-w-7xl mx-auto flex items-center justify-between border-b border-amber-500/30 pb-4 mb-10 relative z-10">
        <Link href={getLocalizedPath('/', currentLang)}>
          <img
            src={LOGO_URL}
            alt="DadRock Tabs"
            className="h-16 sm:h-20 object-contain"
          />
        </Link>

       <LanguageSelector />

        <nav className="hidden md:flex items-center gap-7 text-sm font-extrabold tracking-wide text-zinc-200">
          <Link href={getLocalizedPath('/', currentLang)} className="hover:text-amber-400 transition">HOME</Link>
          <Link href={getLocalizedPath('/artist/acdc', currentLang)} className="hover:text-amber-400 transition">ARTISTS</Link>
          <Link href={getLocalizedPath('/songs/acdc-back-in-black', currentLang)} className="hover:text-amber-400 transition">SONGS</Link>
          <Link href={getLocalizedPath('/learn', currentLang)} className="hover:text-amber-400 transition">LESSONS</Link>
          <Link href={getLocalizedPath('/partners', currentLang)} className="text-amber-400 border border-amber-500 rounded-lg px-4 py-2">
  PARTNERS
</Link>
        </nav>
      </header>

      <section className="max-w-7xl mx-auto text-center relative z-10 mb-12">
        <p className="text-2xl sm:text-4xl font-black italic text-white mb-1">
          {t.partnerWith}
        </p>

        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black mb-6 text-amber-400 drop-shadow-[0_0_22px_rgba(251,191,36,0.55)]">
          {t.partnerTitle}
        </h1>

        <p className="text-amber-400 font-extrabold tracking-wide mb-4">
          {t.partnerTagline}
        </p>

        <p className="text-lg sm:text-xl text-zinc-200 max-w-4xl mx-auto mb-8 leading-relaxed">
  {t.partnerIntro}
</p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
          <a
            href="/media-kit/DadRockTabs-Agency-Media-Kit-2026.pdf"
download
            className="bg-amber-500 hover:bg-amber-400 text-black font-black px-8 py-4 rounded-xl shadow-lg shadow-amber-500/30 transition"
          >
            {t.downloadMediaKit}
          </a>

          <a
            href={YOUTUBE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-black/70 hover:bg-zinc-900 text-white font-black px-8 py-4 rounded-xl border border-amber-500/50 transition"
          >
            {t.visitYouTubeChannel}
          </a>
        </div>
      </section>
        <section className="max-w-7xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-16 relative z-10">
        {stats.map(([number, label, icon]) => (
          <div
            key={label}
            className="bg-black/75 border border-amber-500/40 rounded-2xl p-5 text-center shadow-lg shadow-amber-500/10 hover:border-amber-400 transition"
          >
            <div className="text-3xl mb-2">{icon}</div>
            <div className="text-3xl sm:text-4xl font-black text-amber-400 mb-2">
              {number}
            </div>
            <div className="text-sm text-zinc-200">{label}</div>
          </div>
        ))}
      </section>

      <section className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-6 mb-16 relative z-10">
        <div className="bg-black/75 border border-amber-500/40 rounded-3xl p-6 sm:p-10 shadow-xl">
          <h2 className="text-3xl sm:text-4xl font-black text-amber-400 mb-5">
  {t.whyPartnerTitle}
</h2>

          <p className="text-zinc-200 text-lg leading-relaxed mb-5">
  {t.whyPartnerParagraph1}

        <p className="text-zinc-300 leading-relaxed">
  {t.whyPartnerParagraph2}
</p>
        </div>

        <div className="bg-gradient-to-br from-amber-500/20 to-orange-700/10 border border-amber-500/40 rounded-3xl p-6 sm:p-10 shadow-xl">
          <h2 className="text-3xl sm:text-4xl font-black text-amber-400 mb-5">
  {t.multiPlatformTitle}
</h2>

<div className="space-y-4 text-zinc-200">
  <p>🎥 {t.multiPlatformYouTube}</p>
  <p>🌐 {t.multiPlatformWebsite}</p>
  <p>📱 {t.multiPlatformAndroid}</p>
  <p>🔍 {t.multiPlatformSearch}</p>
</div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto mb-16 relative z-10">
        <h2 className="text-4xl sm:text-5xl font-black text-center text-amber-400 mb-4">
  {t.partnershipOpportunitiesTitle}
</h2>

<p className="text-zinc-300 text-center max-w-3xl mx-auto mb-8">
  {t.partnershipOpportunitiesDescription}
</p>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map(([title, description, icon]) => (
            <div
              key={title}
              className="bg-black/75 border border-amber-500/40 rounded-2xl p-6 shadow-lg hover:border-amber-400 hover:shadow-amber-500/10 transition"
            >
              <div className="text-4xl mb-4">{icon}</div>
              <h3 className="text-xl font-black text-amber-400 mb-3">
                {title}
              </h3>
              <p className="text-zinc-300 leading-relaxed">
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>
      <section className="max-w-7xl mx-auto mb-16 relative z-10">
        <h2 className="text-4xl sm:text-5xl font-black text-center text-amber-400 mb-4">
  {t.brandsTitle}
</h2>

<p className="text-zinc-300 text-center max-w-3xl mx-auto mb-10">
  {t.brandsDescription}
</p>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
          {brands.map((brand) => (
            <div
              key={brand}
              className="bg-gradient-to-br from-zinc-900 to-black border border-amber-500/40 rounded-2xl p-8 text-center hover:border-amber-400 hover:scale-105 transition-all duration-300 shadow-lg"
            >
              <div className="text-xl font-black tracking-wide text-zinc-100">
                {brand}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-7xl mx-auto mb-16 relative z-10">
        <h2 className="text-4xl sm:text-5xl font-black text-center text-amber-400 mb-10">
  {t.audienceSnapshotTitle}
</h2>

        <div className="grid lg:grid-cols-2 gap-6">

          <div className="bg-black/75 border border-amber-500/40 rounded-3xl p-8 shadow-xl">
            <h3 className="text-2xl font-black text-amber-400 mb-4">
  🎸 {t.buyingPowerTitle}
</h3>

            <ul className="space-y-3 text-zinc-200">
  <li>✔ {t.buyingPower1}</li>
  <li>✔ {t.buyingPower2}</li>
  <li>✔ {t.buyingPower3}</li>
  <li>✔ {t.buyingPower4}</li>
  <li>✔ {t.buyingPower5}</li>
</ul>
          </div>

          <div className="bg-black/75 border border-amber-500/40 rounded-3xl p-8 shadow-xl">
            <h3 className="text-2xl font-black text-amber-400 mb-4">
  🌎 {t.globalReachTitle}
</h3>

            <ul className="space-y-3 text-zinc-200">
  <li>🇺🇸 {t.countryUnitedStates}</li>
  <li>🇯🇵 {t.countryJapan}</li>
  <li>🇧🇷 {t.countryBrazil}</li>
  <li>🇨🇦 {t.countryCanada}</li>
  <li>🌍 {t.countryWorldwide}</li>
</ul>
          </div>

        </div>
      </section>

      <section className="max-w-7xl mx-auto mb-16 relative z-10">

        <div className="rounded-3xl overflow-hidden border border-amber-500/40 bg-gradient-to-r from-amber-500/20 via-orange-500/10 to-black shadow-2xl">
  <div className="p-10 sm:p-16 text-center">
    <img
      src={LOGO_URL}
      alt="DadRock Tabs"
      className="mx-auto h-24 object-contain mb-8"
    />

    <h2 className="text-4xl sm:text-5xl font-black text-amber-400 mb-6">
  {t.ctaTitle}
</h2>

    <p className="text-xl text-zinc-200 max-w-4xl mx-auto leading-relaxed mb-10">
  {t.ctaDescription}
</p>

        <div className="flex flex-col sm:flex-row justify-center gap-4">
  <a
    href="/media-kit/DadRockTabs-Agency-Media-Kit-2026.pdf"
    download
    className="bg-amber-500 hover:bg-amber-400 text-black font-black px-8 py-4 rounded-xl shadow-lg shadow-amber-500/30 transition"
  >
    {t.downloadMediaKit}
  </a>
      <a
        href={YOUTUBE_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="border border-amber-500 text-white font-black px-10 py-5 rounded-xl hover:bg-amber-500/10 transition"
      >
        {t.visitYouTubeChannel}
      </a>
    </div>
  </div>
</div>
</section>

</main>
);
}

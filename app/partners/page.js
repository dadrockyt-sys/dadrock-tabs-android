const LOGO_URL = "/dadrock-logo.png";
const YOUTUBE_URL = "https://youtube.com/@dadrockytofficial?si=TjBWK-QMUu7vdcrI";

export default function PartnersPage() {
  const stats = [
    ["75K+", "YouTube Subscribers", "🎸"],
    ["723K+", "Monthly YouTube Views", "👁️"],
    ["231K+", "Monthly Audience", "👥"],
    ["3,200+", "Lesson Videos", "▶️"],
    ["371", "Artists Covered", "🎶"],
    ["732+", "Indexed Website Pages", "🌎"],
  ];

  const opportunities = [
    ["Sponsored Lessons", "Feature a brand naturally inside guitar and bass lesson content.", "🎸"],
    ["Product Reviews", "Showcase guitars, pedals, amps, strings, apps, software, or accessories.", "🎛️"],
    ["Affiliate Campaigns", "Drive targeted traffic from viewers actively learning and buying gear.", "🔗"],
    ["Website Placement", "Promote offers across DadRockTabs.com lesson and artist pages.", "🖥️"],
    ["Android App Promotion", "Reach users directly through the DadRock Tabs mobile experience.", "📱"],
    ["Giveaways", "Create excitement through community contests and product promotions.", "🎁"],
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
        <a href="/">
          <img
            src={LOGO_URL}
            alt="DadRock Tabs"
            className="h-16 sm:h-20 object-contain"
          />
        </a>

        <nav className="hidden md:flex items-center gap-7 text-sm font-extrabold tracking-wide text-zinc-200">
          <a href="/" className="hover:text-amber-400 transition">HOME</a>
          <a href="/artist/acdc" className="hover:text-amber-400 transition">ARTISTS</a>
          <a href="/songs/acdc-back-in-black" className="hover:text-amber-400 transition">SONGS</a>
          <a href="/learn" className="hover:text-amber-400 transition">LESSONS</a>
          <a href="/partners" className="text-amber-400 border border-amber-500 rounded-lg px-4 py-2">
            PARTNERS
          </a>
        </nav>
      </header>

      <section className="max-w-7xl mx-auto text-center relative z-10 mb-12">
        <p className="text-2xl sm:text-4xl font-black italic text-white mb-1">
          PARTNER WITH
        </p>

        <h1 className="text-5xl sm:text-7xl lg:text-8xl font-black mb-6 text-amber-400 drop-shadow-[0_0_22px_rgba(251,191,36,0.55)]">
          DADROCK TABS
        </h1>

        <p className="text-amber-400 font-extrabold tracking-wide mb-4">
          SPONSORSHIPS • BRAND DEALS • MUSIC PARTNERSHIPS
        </p>

        <p className="text-lg sm:text-xl text-zinc-200 max-w-4xl mx-auto mb-8 leading-relaxed">
          DadRock Tabs helps classic rock and metal fans learn the guitar and bass
          parts they love through YouTube, DadRockTabs.com, and the DadRock Tabs Android app.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-12">
          <a
            href="/partners-media-kit.png"
download
            className="bg-amber-500 hover:bg-amber-400 text-black font-black px-8 py-4 rounded-xl shadow-lg shadow-amber-500/30 transition"
          >
            📥 Download Media Kit
          </a>

          <a
            href={YOUTUBE_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="bg-black/70 hover:bg-zinc-900 text-white font-black px-8 py-4 rounded-xl border border-amber-500/50 transition"
          >
            ▶ Visit YouTube Channel
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
            Why Brands Partner With DadRock Tabs
          </h2>

          <p className="text-zinc-200 text-lg leading-relaxed mb-5">
            DadRock Tabs reaches guitar and bass players who are actively searching
            for lessons, tabs, tones, amps, pedals, strings, software, and music
            learning tools.
          </p>

          <p className="text-zinc-300 leading-relaxed">
            Our content is educational, search-driven, and built around iconic songs
            musicians return to again and again — creating long-term exposure instead
            of one-time impressions.
          </p>
        </div>

        <div className="bg-gradient-to-br from-amber-500/20 to-orange-700/10 border border-amber-500/40 rounded-3xl p-6 sm:p-10 shadow-xl">
          <h2 className="text-3xl sm:text-4xl font-black text-amber-400 mb-5">
            A Multi-Platform Music Brand
          </h2>

          <div className="space-y-4 text-zinc-200">
            <p>🎥 YouTube lessons, Shorts, and long-form educational videos</p>
            <p>🌐 DadRockTabs.com artist hubs and song lesson pages</p>
            <p>📱 Android app presence through Google Play</p>
            <p>🔍 Search-driven discovery from musicians looking to learn</p>
          </div>
        </div>
      </section>

      <section className="max-w-7xl mx-auto mb-16 relative z-10">
        <h2 className="text-4xl sm:text-5xl font-black text-center text-amber-400 mb-4">
          Partnership Opportunities
        </h2>

        <p className="text-zinc-300 text-center max-w-3xl mx-auto mb-8">
          Flexible sponsorship options for brands that want to reach classic rock,
          metal, guitar, bass, and music gear audiences.
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
          Brands We'd Love To Work With
        </h2>

        <p className="text-zinc-300 text-center max-w-3xl mx-auto mb-10">
          DadRock Tabs is a natural fit for guitar manufacturers, strings,
          pedals, amplifiers, music software, online education, creator tools,
          and lifestyle brands that connect with musicians.
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
          Audience Snapshot
        </h2>

        <div className="grid lg:grid-cols-2 gap-6">

          <div className="bg-black/75 border border-amber-500/40 rounded-3xl p-8 shadow-xl">
            <h3 className="text-2xl font-black text-amber-400 mb-4">
              🎸 Guitarists With Buying Power
            </h3>

            <ul className="space-y-3 text-zinc-200">
              <li>✔ 95% Male Audience</li>
              <li>✔ Core age 25–64</li>
              <li>✔ Passionate classic rock & heavy metal fans</li>
              <li>✔ Long-form educational content</li>
              <li>✔ Highly engaged repeat viewers</li>
            </ul>
          </div>

          <div className="bg-black/75 border border-amber-500/40 rounded-3xl p-8 shadow-xl">
            <h3 className="text-2xl font-black text-amber-400 mb-4">
              🌎 Global Reach
            </h3>

            <ul className="space-y-3 text-zinc-200">
              <li>🇺🇸 United States</li>
              <li>🇯🇵 Japan</li>
              <li>🇧🇷 Brazil</li>
              <li>🇨🇦 Canada</li>
              <li>🌍 Viewers from around the world</li>
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
      Let's Build Something Great Together
    </h2>

    <p className="text-xl text-zinc-200 max-w-4xl mx-auto leading-relaxed mb-10">
      Whether you're launching a new guitar, promoting music software,
      introducing a new pedal, or growing your brand, DadRock Tabs can
      help you reach one of YouTube's most passionate classic rock
      communities.
    </p>

    <div className="flex flex-col sm:flex-row justify-center gap-4">
    <a
  href="/partners-media-kit.png"
  download
  className="bg-amber-500 hover:bg-amber-400 text-black font-black px-8 py-4 rounded-xl shadow-lg shadow-amber-500/30 transition"
>
        📩 Contact DadRock Tabs
      </a>

      <a
        href={YOUTUBE_URL}
        target="_blank"
        rel="noopener noreferrer"
        className="border border-amber-500 text-white font-black px-10 py-5 rounded-xl hover:bg-amber-500/10 transition"
      >
        ▶ Visit Our Channel
      </a>
    </div>
  </div>
</div>
</section>

</main>
);
}

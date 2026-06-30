const BANNER_URL = "/dadrock-logo.png";
  
export default function PartnersPage() {
  const stats = [
    ["75K+", "YouTube Subscribers"],
    ["723K+", "Monthly YouTube Views"],
    ["231K+", "Monthly Audience"],
    ["3,200+", "Lesson Videos"],
    ["371", "Artists Covered"],
    ["732+", "Indexed Website Pages"],
  ];

  const brands = [
    "Fender", "Gibson", "Ernie Ball", "Dunlop",
    "Boss", "Positive Grid", "Sweetwater", "Thomann",
    "D'Addario", "Elixir", "IK Multimedia", "Neural DSP",
  ];

  return (
    <main className="min-h-screen bg-black bg-guitarist text-white px-4 py-8 overflow-hidden">
      <div className="fixed inset-0 pointer-events-none opacity-30">
        <span className="absolute top-24 left-[12%] text-amber-400 text-4xl animate-pulse">♪</span>
        <span className="absolute top-40 right-[18%] text-amber-400 text-5xl animate-pulse">♫</span>
        <span className="absolute top-80 left-[80%] text-amber-400 text-4xl animate-pulse">♪</span>
      </div>

      <section className="max-w-6xl mx-auto text-center relative z-10">
        <img
          src={BANNER_URL}
          alt="DadRock Tabs"
          className="mx-auto h-24 sm:h-32 object-contain mb-6"
        />

        <p className="text-amber-400 font-bold tracking-wide mb-3">
          SPONSORSHIPS • BRAND DEALS • MUSIC PARTNERSHIPS
        </p>

        <h1 className="text-5xl sm:text-7xl font-extrabold mb-6 text-amber-400 drop-shadow-lg">
          Partner With DadRock Tabs
        </h1>

        <p className="text-lg sm:text-xl text-zinc-200 max-w-4xl mx-auto mb-8 leading-relaxed">
          Reach passionate classic rock and metal guitar players through YouTube,
          DadRockTabs.com, and the DadRock Tabs Android app.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-14">
          <a
            href="mailto:dadrocktabsyt@gmail.com"
            className="bg-amber-500 hover:bg-amber-400 text-black font-extrabold px-8 py-4 rounded-xl shadow-lg shadow-amber-500/30 transition"
          >
            ✉ Request Our Media Kit
          </a>

          <a
            href="https://www.youtube.com/@DadRock2.0"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-zinc-950/80 hover:bg-zinc-900 text-white font-bold px-8 py-4 rounded-xl border border-amber-500/40 transition"
          >
            ▶ Visit YouTube Channel
          </a>
        </div>
      </section>

      <section className="max-w-6xl mx-auto grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-14 relative z-10">
        {stats.map(([number, label]) => (
          <div
            key={label}
            className="bg-black/70 border border-amber-500/50 rounded-2xl p-5 text-center shadow-lg shadow-amber-500/10"
          >
            <div className="text-3xl sm:text-4xl font-extrabold text-amber-400 mb-2">
              {number}
            </div>
            <div className="text-sm text-zinc-200">{label}</div>
          </div>
        ))}
      </section>

      <section className="max-w-6xl mx-auto bg-black/75 border border-amber-500/40 rounded-3xl p-6 sm:p-10 mb-14 relative z-10">
        <h2 className="text-3xl font-extrabold mb-4 text-amber-400">
          ★ Why Brands Partner With DadRock Tabs
        </h2>
        <p className="text-zinc-200 text-lg leading-relaxed">
          Our audience is made up of guitar and bass players actively searching
          for lessons, tabs, tones, amps, pedals, strings, software, and music
          learning tools. DadRock Tabs content is educational, search-driven,
          and built around iconic songs musicians return to again and again.
        </p>
      </section>

      <section className="max-w-6xl mx-auto mb-14 relative z-10">
        <h2 className="text-4xl font-extrabold text-center text-amber-400 mb-8">
          Partnership Opportunities
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            "Sponsored Lessons",
            "Product Reviews",
            "Affiliate Campaigns",
            "Website Placement",
            "Android App Promotion",
            "Giveaways",
          ].map((item) => (
            <div
              key={item}
              className="bg-black/75 border border-amber-500/40 rounded-2xl p-6 hover:border-amber-400 transition"
            >
              <h3 className="text-xl font-extrabold text-amber-400 mb-2">
                {item}
              </h3>
              <p className="text-zinc-300">
                Promote your brand naturally to guitar and bass players already
                looking for lessons, gear, and music tools.
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto mb-14 relative z-10">
        <h2 className="text-4xl font-extrabold text-center text-amber-400 mb-3">
          Brands We’d Love To Work With
        </h2>

        <p className="text-zinc-300 text-center mb-8">
          Guitar gear, music software, accessories, education platforms, and creator-focused brands.
        </p>

        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          {brands.map((brand) => (
            <div
              key={brand}
              className="bg-black/75 border border-amber-500/40 rounded-xl p-5 text-center font-extrabold text-zinc-100 hover:text-amber-400 transition"
            >
              {brand}
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-6xl mx-auto text-center bg-gradient-to-br from-amber-500/25 to-orange-700/10 border border-amber-500/50 rounded-3xl p-8 sm:p-12 relative z-10">
        <img
          src={BANNER_URL}
          alt="DadRock Tabs"
          className="mx-auto h-20 object-contain mb-6"
        />

        <h2 className="text-3xl sm:text-4xl font-extrabold text-amber-400 mb-4">
          Let’s Build Something Great Together
        </h2>

        <p className="text-zinc-200 text-lg mb-8 max-w-3xl mx-auto">
          For sponsorships, product features, affiliate partnerships, giveaways,
          or long-term brand collaborations, contact DadRock Tabs directly.
        </p>

        <a
          href="mailto:dadrocktabsyt@gmail.com"
          className="inline-block bg-amber-500 hover:bg-amber-400 text-black font-extrabold px-8 py-4 rounded-xl transition"
        >
          Contact DadRock Tabs
        </a>
      </section>
    </main>
  );
}

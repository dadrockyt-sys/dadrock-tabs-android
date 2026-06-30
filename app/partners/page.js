export default function PartnersPage() {
  const stats = [
    ["75K+", "YouTube Subscribers"],
    ["723K+", "Monthly YouTube Views"],
    ["231K+", "Monthly Audience"],
    ["3,200+", "Lesson Videos"],
    ["371", "Artists Covered"],
    ["732+", "Indexed Website Pages"],
  ];

  const opportunities = [
    ["Sponsored Lessons", "Feature a brand naturally inside guitar and bass lesson content."],
    ["Product Reviews", "Showcase guitars, pedals, amps, strings, apps, software, or accessories."],
    ["Affiliate Campaigns", "Drive targeted traffic from viewers actively learning and buying gear."],
    ["Website Placement", "Promote offers across DadRockTabs.com lesson and artist pages."],
    ["Android App Promotion", "Reach users directly through the DadRock Tabs mobile experience."],
    ["Giveaways", "Create excitement through community contests and product promotions."],
  ];

  return (
    <main className="min-h-screen bg-black bg-guitarist text-white px-4 py-10 sm:py-16">
      <section className="max-w-6xl mx-auto text-center transition-opacity duration-500">
        <p className="text-amber-400 font-semibold mb-4">
          Sponsorships • Brand Deals • Music Partnerships
        </p>

        <h1 className="text-4xl sm:text-6xl font-extrabold mb-6">
          Partner With DadRock Tabs
        </h1>

        <p className="text-lg sm:text-xl text-zinc-300 max-w-4xl mx-auto mb-8 leading-relaxed">
          DadRock Tabs helps classic rock and metal fans learn the guitar and
          bass parts they love through YouTube, DadRockTabs.com, and the
          DadRock Tabs Android app.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 mb-14">
          <a
            href="mailto:dadrocktabsyt@gmail.com"
            className="bg-amber-500 hover:bg-amber-400 text-black font-bold px-8 py-4 rounded-xl shadow-lg shadow-amber-500/20 transition"
          >
            Request Our Media Kit
          </a>

          <a
            href="https://www.youtube.com/@DadRockTabs"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-zinc-900/80 hover:bg-zinc-800 text-white font-bold px-8 py-4 rounded-xl border border-zinc-700 transition"
          >
            View YouTube Channel
          </a>
        </div>
      </section>

      <section className="max-w-6xl mx-auto grid grid-cols-2 sm:grid-cols-3 gap-4 mb-16">
        {stats.map(([number, label]) => (
          <div
            key={label}
            className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-5 sm:p-6 text-center shadow-lg backdrop-blur-sm"
          >
            <div className="text-3xl sm:text-4xl font-extrabold text-amber-400 mb-2">
              {number}
            </div>
            <div className="text-sm sm:text-base text-zinc-300">
              {label}
            </div>
          </div>
        ))}
      </section>

      <section className="max-w-5xl mx-auto bg-zinc-900/80 border border-zinc-800 rounded-3xl p-6 sm:p-10 mb-16 shadow-xl">
        <h2 className="text-3xl font-bold mb-4 text-center">
          Why Brands Partner With DadRock Tabs
        </h2>

        <p className="text-zinc-300 text-lg leading-relaxed text-center max-w-4xl mx-auto">
          Our audience is made up of guitar and bass players actively searching
          for lessons, tabs, tones, amps, pedals, strings, software, and music
          learning tools. DadRock Tabs content is educational, search-driven,
          and built around iconic songs that musicians return to again and again.
        </p>
      </section>

      <section className="max-w-6xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-center mb-8">
          Partnership Opportunities
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map(([title, description]) => (
            <div
              key={title}
              className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-6 shadow-lg hover:border-amber-500/40 transition"
            >
              <h3 className="text-xl font-bold text-amber-400 mb-3">
                {title}
              </h3>
              <p className="text-zinc-300 leading-relaxed">
                {description}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto bg-zinc-900/80 border border-zinc-800 rounded-3xl p-6 sm:p-10 mb-16">
        <h2 className="text-3xl font-bold mb-6 text-center">
          Audience Snapshot
        </h2>

        <div className="grid sm:grid-cols-2 gap-4 text-zinc-300">
          <div className="bg-black/40 rounded-2xl p-5 border border-zinc-800">
            <strong className="text-white">Primary Audience:</strong>
            <br />
            Classic rock, hard rock, blues rock, and heavy metal guitar players.
          </div>

          <div className="bg-black/40 rounded-2xl p-5 border border-zinc-800">
            <strong className="text-white">Audience Profile:</strong>
            <br />
            95% male, with strong reach among adult musicians aged 25–64.
          </div>

          <div className="bg-black/40 rounded-2xl p-5 border border-zinc-800">
            <strong className="text-white">Top Markets:</strong>
            <br />
            United States, Japan, Brazil, Canada, United Kingdom, and global music fans.
          </div>

          <div className="bg-black/40 rounded-2xl p-5 border border-zinc-800">
            <strong className="text-white">Traffic Quality:</strong>
            <br />
            Search-driven viewers looking for lessons, songs, tabs, and gear.
          </div>
        </div>
      </section>

      <section className="max-w-5xl mx-auto text-center bg-gradient-to-br from-amber-500/20 to-orange-600/10 border border-amber-500/30 rounded-3xl p-8 sm:p-12 shadow-xl">
        <h2 className="text-3xl font-bold mb-4">
          Let’s Build Something Great Together
        </h2>

        <p className="text-zinc-300 text-lg mb-8 max-w-3xl mx-auto">
          For sponsorships, product features, affiliate partnerships,
          giveaways, or long-term brand collaborations, contact DadRock Tabs
          directly.
        </p>

        <a
          href="mailto:dadrocktabsyt@gmail.com"
          className="inline-block bg-amber-500 hover:bg-amber-400 text-black font-bold px-8 py-4 rounded-xl transition shadow-lg shadow-amber-500/20"
        >
          Contact DadRock Tabs
        </a>
      </section>
    </main>
  );
            }

export default function PartnersPage() {
  const stats = [
    ["75,000+", "YouTube Subscribers"],
    ["723K+", "Monthly YouTube Views"],
    ["231K+", "Monthly Audience"],
    ["3,200+", "Lesson Videos"],
    ["371", "Artists Covered"],
    ["732+", "Indexed Website Pages"],
  ];

  const opportunities = [
    "Sponsored guitar & bass lessons",
    "Product reviews and demos",
    "Affiliate campaigns",
    "Website advertising",
    "Android app promotion",
    "Giveaways and long-term partnerships",
  ];

  return (
    <main className="min-h-screen bg-black bg-guitarist text-white px-4 py-10 sm:py-16">
      <section className="max-w-6xl mx-auto text-center">
        <p className="text-amber-400 font-semibold mb-4">
          Sponsorships • Partnerships • Brand Collaborations
        </p>

        <h1 className="text-4xl sm:text-6xl font-bold mb-6">
          Partner With DadRock Tabs
        </h1>

        <p className="text-lg sm:text-xl text-zinc-300 max-w-4xl mx-auto mb-8 leading-relaxed">
          Reach a passionate audience of classic rock and metal guitar and bass
          players through YouTube, DadRockTabs.com, and the DadRock Tabs Android app.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <a
            href="mailto:dadrocktabsyt@gmail.com"
            className="bg-amber-500 hover:bg-amber-400 text-black font-bold px-8 py-4 rounded-xl shadow-lg transition"
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
            className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-6 text-center shadow-lg"
          >
            <div className="text-3xl sm:text-4xl font-bold text-amber-400 mb-2">
              {number}
            </div>
            <div className="text-sm sm:text-base text-zinc-300">{label}</div>
          </div>
        ))}
      </section>

      <section className="max-w-5xl mx-auto bg-zinc-900/80 border border-zinc-800 rounded-3xl p-6 sm:p-10 mb-16">
        <h2 className="text-3xl font-bold mb-4 text-center">
          Why Partner With DadRock Tabs?
        </h2>

        <p className="text-zinc-300 text-lg leading-relaxed text-center max-w-4xl mx-auto">
          DadRock Tabs reaches musicians who are actively searching for guitar
          lessons, bass tabs, classic rock songs, tones, gear, amps, pedals,
          strings, and music learning tools. Our content is educational,
          search-driven, and built around songs people return to again and again.
        </p>
      </section>

      <section className="max-w-6xl mx-auto mb-16">
        <h2 className="text-3xl font-bold text-center mb-8">
          Partnership Opportunities
        </h2>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {opportunities.map((item) => (
            <div
              key={item}
              className="bg-zinc-900/80 border border-zinc-800 rounded-2xl p-6 text-center text-zinc-200 font-semibold"
            >
              {item}
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-5xl mx-auto text-center bg-gradient-to-br from-amber-500/20 to-orange-600/10 border border-amber-500/30 rounded-3xl p-8 sm:p-12">
        <h2 className="text-3xl font-bold mb-4">
          Let’s Build Something Great Together
        </h2>

        <p className="text-zinc-300 text-lg mb-8">
          For sponsorships, product features, affiliate partnerships, or long-term
          brand collaborations, contact DadRock Tabs directly.
        </p>

        <a
          href="mailto:dadrocktabsyt@gmail.com"
          className="inline-block bg-amber-500 hover:bg-amber-400 text-black font-bold px-8 py-4 rounded-xl transition"
        >
          Contact DadRock Tabs
        </a>
      </section>
    </main>
  );
            }

import Link from 'next/link';

export default function ArtistNotFound() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 text-white flex items-center justify-center">
      <div className="text-center px-4">
        <h1 className="text-6xl font-bold text-amber-500 mb-4">404</h1>
        <h2 className="text-2xl font-bold mb-4">Artist Not Found</h2>
        <p className="text-zinc-400 mb-8">
          We couldn't find any lessons for this artist. Try searching for a different artist!
        </p>
        <Link
          href="/"
          className="inline-flex items-center gap-2 px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-full transition-colors"
        >
          Go to Homepage
        </Link>
      </div>
    </div>
  );
}

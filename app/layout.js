import './globals.css';

export const metadata = {
  title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
  description: 'Free guitar and bass tabs for classic rock hits. Learn to play Led Zeppelin, AC/DC, Van Halen, and more!',
  keywords: 'guitar tabs, bass tabs, classic rock, dad rock, guitar lessons, Led Zeppelin, AC/DC, Van Halen',
  openGraph: {
    title: 'DadRock Tabs - Guitar & Bass Tabs for Classic Rock',
    description: 'Free guitar and bass tabs for classic rock hits.',
    type: 'website',
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-background antialiased">
        {children}
      </body>
    </html>
  );
}

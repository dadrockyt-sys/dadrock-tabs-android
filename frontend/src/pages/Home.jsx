import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Download, ShoppingBag, MessageSquarePlus, Heart, Youtube, Share2, Facebook, Twitter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/u9nzw1f2_20201025_123236.jpg";
const YOUTUBE_CHANNEL_URL = "https://youtube.com/@dadrockytofficial?si=8Tl_CxtfUExseIk1";

// Popular searches for SEO and user engagement
const POPULAR_SEARCHES = [
  { name: "Led Zeppelin", icon: "🎸" },
  { name: "AC/DC", icon: "⚡" },
  { name: "Van Halen", icon: "🔥" },
  { name: "Def Leppard", icon: "🎵" },
  { name: "Guns N' Roses", icon: "🌹" },
  { name: "Metallica", icon: "🤘" },
  { name: "Black Sabbath", icon: "🦇" },
  { name: "Aerosmith", icon: "💎" },
];

const Home = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [installPrompt, setInstallPrompt] = useState(null);
  const [showInstallButton, setShowInstallButton] = useState(false);
  const [logoClickCount, setLogoClickCount] = useState(0);

  // Secret admin access: tap logo 5 times quickly
  const handleLogoClick = () => {
    const newCount = logoClickCount + 1;
    setLogoClickCount(newCount);
    
    // Reset count after 3 seconds of inactivity
    setTimeout(() => setLogoClickCount(0), 3000);
    
    // Navigate on 5th click
    if (newCount >= 5) {
      setLogoClickCount(0);
      navigate("/admin");
    }
  };

  useEffect(() => {
    const handleBeforeInstall = (e) => {
      e.preventDefault();
      setInstallPrompt(e);
      setShowInstallButton(true);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstall);
    
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setShowInstallButton(false);
    }

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstall);
    };
  }, []);

  const handleInstall = async () => {
    if (!installPrompt) return;
    
    installPrompt.prompt();
    const { outcome } = await installPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setShowInstallButton(false);
    }
    setInstallPrompt(null);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}&type=all`);
    }
  };

  return (
    <div className="min-h-screen relative bg-black">
      {/* Hero Section */}
      <div className="min-h-screen relative">
        {/* Content */}
        <div className="relative z-10 flex flex-col min-h-screen">
          {/* Header with Banner */}
          <header className="relative">
            {/* Banner Image */}
            <div className="w-full h-14 sm:h-16 md:h-20 lg:h-24 overflow-hidden bg-black">
              <img 
                src={BANNER_URL} 
                alt="DadRock Guitar Tabs Banner"
                className="w-full h-full object-contain"
              />
            </div>
            {/* Top Right Buttons */}
            <div className="absolute top-4 right-4 flex gap-2">
              <a
                href="https://my-store-b8bb42.creator-spring.com"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary hover:text-primary/80 bg-black/50 backdrop-blur-sm rounded-md transition-colors"
                data-testid="merch-link"
              >
                <ShoppingBag className="w-4 h-4" />
                <span className="hidden sm:inline">Support Merch</span>
              </a>
              {showInstallButton && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleInstall}
                  className="text-primary hover:text-primary/80 bg-black/50 backdrop-blur-sm"
                  data-testid="install-app-button"
                >
                  <Download className="w-5 h-5 mr-1" />
                  <span className="hidden sm:inline">Install</span>
                </Button>
              )}
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 flex flex-col items-center justify-center px-4 pt-4 md:pt-0 md:-mt-10">
            {/* Logo and Definition Section */}
            <div className="w-full max-w-4xl mb-6 md:mb-8 fade-in px-4">
              <div className="flex flex-col items-center md:flex-row md:items-center md:justify-center gap-4 md:gap-10">
                {/* Logo - Left Side - Tap 5 times for secret admin access */}
                <div className="flex-shrink-0 mt-2 md:mt-0">
                  <img 
                    src={LOGO_URL} 
                    alt="DadRock Tabs Logo"
                    onClick={handleLogoClick}
                    className="w-36 sm:w-40 md:w-56 lg:w-64 drop-shadow-[0_0_30px_rgba(245,158,11,0.3)] cursor-pointer select-none"
                  />
                </div>
                
                {/* Dictionary Definition - Right Side */}
                <div className="text-center md:text-left">
                  <h2 className="font-heading text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white tracking-tight">
                    DadRock <span className="text-primary font-normal text-sm sm:text-base md:text-xl lg:text-2xl">[dad•rok]</span>
                  </h2>
                  <p className="text-muted-foreground italic mt-1 text-xs sm:text-sm">n.</p>
                  <p className="text-white/90 text-sm sm:text-base md:text-lg mt-1 md:mt-2 max-w-sm md:max-w-md leading-relaxed">
                    Rock music that appeals to an older generation; or is heavily influenced by that of an earlier era.
                  </p>
                </div>
              </div>
              
              {/* Tagline */}
              <p className="text-sm md:text-base lg:text-lg text-muted-foreground text-center mt-4 md:mt-6 max-w-2xl mx-auto">
                Your go-to database for classic rock guitar & bass tutorials. Search by song or artist.
              </p>
            </div>

            {/* Search Form */}
            <form 
              onSubmit={handleSearch}
              className="w-full max-w-3xl fade-in stagger-1"
              data-testid="search-form"
            >
              <div className="flex flex-col md:flex-row gap-4">
                {/* Search Input */}
                <div className="flex-1 relative">
                  <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-muted-foreground" />
                  <Input
                    type="text"
                    placeholder="Search for songs or artists..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="search-input h-16 text-lg md:text-xl bg-black/50 border-2 border-white/20 focus:border-primary rounded-full pl-16 pr-6 text-white placeholder:text-white/40 backdrop-blur-md"
                    data-testid="search-input"
                  />
                </div>

                {/* Search Button */}
                <Button
                  type="submit"
                  size="lg"
                  className="h-16 px-10 rounded-full font-heading font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90 glow-amber btn-lift"
                  data-testid="search-button"
                >
                  Search
                </Button>

                {/* Subscribe Button */}
                <a
                  href={YOUTUBE_CHANNEL_URL}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <Button
                    type="button"
                    size="lg"
                    className="h-16 px-10 rounded-full font-heading font-bold uppercase tracking-wider bg-red-600 text-white hover:bg-red-700 btn-lift"
                    data-testid="subscribe-button"
                  >
                    <Youtube className="w-5 h-5 mr-2" />
                    Subscribe Here! It's FREE
                  </Button>
                </a>
              </div>
            </form>

            {/* Popular Searches Section */}
            <div className="w-full max-w-3xl mt-6 fade-in stagger-2">
              <p className="text-sm text-muted-foreground text-center mb-3">🔥 Popular Searches</p>
              <div className="flex flex-wrap justify-center gap-2">
                {POPULAR_SEARCHES.map((artist) => (
                  <button
                    key={artist.name}
                    onClick={() => navigate(`/search?q=${encodeURIComponent(artist.name)}&type=all`)}
                    className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-primary/50 rounded-full text-sm text-white/80 hover:text-white transition-all duration-200"
                    data-testid={`popular-${artist.name.toLowerCase().replace(/[^a-z]/g, '-')}`}
                  >
                    {artist.icon} {artist.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Social Sharing Section */}
            <div className="w-full max-w-3xl mt-6 fade-in stagger-3">
              <p className="text-sm text-muted-foreground text-center mb-3">📢 Share DadRock Tabs</p>
              <div className="flex justify-center gap-3">
                <a
                  href="https://www.facebook.com/sharer/sharer.php?u=https://dadrocktabs.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 bg-blue-600 hover:bg-blue-700 rounded-full text-white transition-all duration-200"
                  data-testid="share-facebook"
                >
                  <Facebook className="w-5 h-5" />
                </a>
                <a
                  href="https://twitter.com/intent/tweet?text=Check%20out%20DadRock%20Tabs%20-%20Free%20guitar%20%26%20bass%20tutorials%20for%20classic%20rock!&url=https://dadrocktabs.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 bg-sky-500 hover:bg-sky-600 rounded-full text-white transition-all duration-200"
                  data-testid="share-twitter"
                >
                  <Twitter className="w-5 h-5" />
                </a>
                <a
                  href="https://api.whatsapp.com/send?text=Check%20out%20DadRock%20Tabs%20-%20Free%20guitar%20%26%20bass%20tutorials%20for%20classic%20rock!%20https://dadrocktabs.com"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="p-3 bg-green-500 hover:bg-green-600 rounded-full text-white transition-all duration-200"
                  data-testid="share-whatsapp"
                >
                  <Share2 className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Make a Request Button */}
            <a
              href="https://buymeacoffee.com/dadrockytq/commissions"
              target="_blank"
              rel="noopener noreferrer"
              className="mt-6 w-full max-w-3xl fade-in stagger-1"
              data-testid="request-button"
            >
              <Button
                type="button"
                size="lg"
                className="w-full h-16 rounded-full font-heading font-bold uppercase tracking-wider bg-gradient-to-r from-amber-500 to-orange-600 text-white hover:from-amber-600 hover:to-orange-700 glow-amber btn-lift text-lg"
              >
                <MessageSquarePlus className="w-6 h-6 mr-3" />
                Make a Request
              </Button>
            </a>

            {/* Support & Merch Buttons */}
            <div className="mt-6 w-full max-w-3xl flex gap-4 fade-in stagger-2">
              <a
                href="https://www.paypal.com/donate?hosted_button_id=FKZ2C3QW9ZBTE"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1"
                data-testid="support-button"
              >
                <Button
                  type="button"
                  size="lg"
                  className="w-full h-12 rounded-full font-heading font-bold uppercase tracking-wider bg-secondary border border-white/20 text-white hover:bg-white/10 btn-lift"
                >
                  <Heart className="w-5 h-5 mr-2 text-red-500" />
                  Support
                </Button>
              </a>
              <a
                href="https://my-store-b8bb42.creator-spring.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1"
                data-testid="merch-button"
              >
                <Button
                  type="button"
                  size="lg"
                  className="w-full h-12 rounded-full font-heading font-bold uppercase tracking-wider bg-secondary border border-white/20 text-white hover:bg-white/10 btn-lift"
                >
                  <ShoppingBag className="w-5 h-5 mr-2 text-primary" />
                  Merchandise
                </Button>
              </a>
            </div>
          </main>

          {/* Footer */}
          <footer className="p-6 text-center">
            <p className="text-sm text-muted-foreground">
              © 2024 DadRock Tabs. All rights reserved.
            </p>
          </footer>
        </div>
      </div>
    </div>
  );
};

export default Home;

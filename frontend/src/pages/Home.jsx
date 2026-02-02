import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Music, Settings, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/u9nzw1f2_20201025_123236.jpg";

const Home = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("all");
  const [installPrompt, setInstallPrompt] = useState(null);
  const [showInstallButton, setShowInstallButton] = useState(false);

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
      navigate(`/search?q=${encodeURIComponent(searchQuery)}&type=${searchType}`);
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
            <div className="w-full h-16 sm:h-24 md:h-32 overflow-hidden">
              <img 
                src={BANNER_URL} 
                alt="DadRock Guitar Tabs Banner"
                className="w-full h-full object-cover object-center"
              />
            </div>
            {/* Admin Button */}
            <div className="absolute top-4 right-4 flex gap-2">
              {showInstallButton && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleInstall}
                  className="text-primary hover:text-primary/80 bg-black/50 backdrop-blur-sm"
                  data-testid="install-app-button"
                >
                  <Download className="w-5 h-5 mr-1" />
                  Install
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate("/admin")}
                className="text-muted-foreground hover:text-primary bg-black/50 backdrop-blur-sm"
                data-testid="admin-link"
              >
              <Settings className="w-5 h-5" />
            </Button>
          </header>

          {/* Main Content */}
          <main className="flex-1 flex flex-col items-center justify-center px-4 -mt-10">
            {/* Logo */}
            <div className="text-center mb-6 md:mb-8 fade-in px-4">
              <img 
                src={LOGO_URL} 
                alt="DadRock Tabs Logo"
                className="w-full max-w-xs sm:max-w-sm md:max-w-lg lg:max-w-xl mx-auto mb-4 md:mb-6 drop-shadow-[0_0_30px_rgba(245,158,11,0.3)]"
              />
              <p className="text-base md:text-lg lg:text-xl text-muted-foreground max-w-2xl mx-auto">
                Your go-to database for classic rock guitar tutorials. Search by song or artist.
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

                {/* Search Type Select */}
                <Select value={searchType} onValueChange={setSearchType}>
                  <SelectTrigger 
                    className="w-full md:w-40 h-16 bg-secondary border-2 border-white/10 rounded-full text-white"
                    data-testid="search-type-select"
                  >
                    <SelectValue placeholder="Search by" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all" data-testid="search-type-all">All</SelectItem>
                    <SelectItem value="song" data-testid="search-type-song">Song</SelectItem>
                    <SelectItem value="artist" data-testid="search-type-artist">Artist</SelectItem>
                  </SelectContent>
                </Select>

                {/* Search Button */}
                <Button
                  type="submit"
                  size="lg"
                  className="h-16 px-10 rounded-full font-heading font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90 glow-amber btn-lift"
                  data-testid="search-button"
                >
                  Search
                </Button>
              </div>
            </form>

            {/* Quick Stats */}
            <div className="mt-16 flex gap-8 md:gap-16 fade-in stagger-2">
              <div className="text-center">
                <Music className="w-8 h-8 text-primary mx-auto mb-2" />
                <p className="text-sm text-muted-foreground uppercase tracking-widest">Guitar Tabs</p>
              </div>
              <div className="text-center">
                <Music className="w-8 h-8 text-primary mx-auto mb-2" />
                <p className="text-sm text-muted-foreground uppercase tracking-widest">Classic Rock</p>
              </div>
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

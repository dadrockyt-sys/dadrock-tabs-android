import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, Guitar, Music, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const Home = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("all");

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}&type=${searchType}`);
    }
  };

  return (
    <div className="min-h-screen relative">
      {/* Hero Section */}
      <div className="hero-bg min-h-screen relative">
        {/* Overlay */}
        <div className="absolute inset-0 hero-overlay" />
        
        {/* Content */}
        <div className="relative z-10 flex flex-col min-h-screen">
          {/* Header */}
          <header className="flex justify-between items-center p-6 md:p-8">
            <div className="flex items-center gap-3">
              <Guitar className="w-8 h-8 text-primary" />
              <span className="font-heading text-2xl font-bold uppercase tracking-tight text-white">
                DadRock Tabs
              </span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => navigate("/admin")}
              className="text-muted-foreground hover:text-primary"
              data-testid="admin-link"
            >
              <Settings className="w-5 h-5" />
            </Button>
          </header>

          {/* Main Content */}
          <main className="flex-1 flex flex-col items-center justify-center px-4 -mt-20">
            {/* Title */}
            <div className="text-center mb-12 fade-in">
              <h1 className="font-heading text-6xl md:text-8xl font-bold uppercase tracking-tighter text-white mb-4">
                DadRock <span className="text-primary">Tabs</span>
              </h1>
              <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
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
                <Guitar className="w-8 h-8 text-primary mx-auto mb-2" />
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

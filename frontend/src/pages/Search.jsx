import { useState, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import axios from "axios";
import { Search as SearchIcon, Guitar, ArrowLeft, Play, User, Music } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const VideoCard = ({ video, onClick }) => {
  return (
    <div
      className="video-card group relative overflow-hidden bg-card rounded-xl border border-white/5 cursor-pointer"
      onClick={() => onClick(video)}
      data-testid={`video-card-${video.id}`}
    >
      {/* Thumbnail */}
      <div className="relative aspect-video overflow-hidden">
        <img
          src={video.thumbnail || `https://img.youtube.com/vi/default/mqdefault.jpg`}
          alt={video.song}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
        />
        {/* Play overlay */}
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-16 h-16 rounded-full bg-primary flex items-center justify-center glow-amber">
            <Play className="w-8 h-8 text-primary-foreground ml-1" fill="currentColor" />
          </div>
        </div>
        {/* Gradient overlay */}
        <div className="absolute bottom-0 left-0 right-0 h-20 thumbnail-overlay" />
      </div>

      {/* Info */}
      <div className="p-5">
        <h3 className="font-heading text-xl font-bold uppercase tracking-tight text-white truncate group-hover:text-primary transition-colors">
          {video.song}
        </h3>
        <div className="flex items-center gap-2 mt-2 text-muted-foreground">
          <User className="w-4 h-4" />
          <span className="text-sm">{video.artist}</span>
        </div>
      </div>
    </div>
  );
};

const Search = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialQuery = searchParams.get("q") || "";
  const initialType = searchParams.get("type") || "all";

  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [searchType, setSearchType] = useState(initialType);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const fetchVideos = async (query, type) => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/videos`, {
        params: {
          search: query || undefined,
          search_type: type,
        },
      });
      setVideos(response.data.videos);
      setTotal(response.data.total);
    } catch (error) {
      console.error("Error fetching videos:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVideos(initialQuery, initialType);
  }, [initialQuery, initialType]);

  const handleSearch = (e) => {
    e.preventDefault();
    navigate(`/search?q=${encodeURIComponent(searchQuery)}&type=${searchType}`);
    fetchVideos(searchQuery, searchType);
  };

  const handleVideoClick = (video) => {
    navigate(`/watch/${video.id}`);
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-background/80 backdrop-blur-lg border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row gap-4 items-center">
            {/* Logo & Back */}
            <div className="flex items-center gap-4 w-full md:w-auto">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => navigate("/")}
                className="text-muted-foreground hover:text-primary"
                data-testid="back-button"
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              <div 
                className="flex items-center gap-2 cursor-pointer"
                onClick={() => navigate("/")}
              >
                <Guitar className="w-6 h-6 text-primary" />
                <span className="font-heading text-xl font-bold uppercase tracking-tight text-white">
                  DadRock Tabs
                </span>
              </div>
            </div>

            {/* Search Form */}
            <form 
              onSubmit={handleSearch}
              className="flex-1 flex gap-3 w-full"
              data-testid="search-form"
            >
              <div className="flex-1 relative">
                <SearchIcon className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                <Input
                  type="text"
                  placeholder="Search..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="h-12 bg-secondary border-white/10 rounded-full pl-12 pr-4 text-white placeholder:text-muted-foreground"
                  data-testid="search-input"
                />
              </div>
              <Select value={searchType} onValueChange={setSearchType}>
                <SelectTrigger 
                  className="w-32 h-12 bg-secondary border-white/10 rounded-full"
                  data-testid="search-type-select"
                >
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="song">Song</SelectItem>
                  <SelectItem value="artist">Artist</SelectItem>
                </SelectContent>
              </Select>
              <Button
                type="submit"
                className="h-12 px-6 rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
                data-testid="search-submit"
              >
                Search
              </Button>
            </form>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Results Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-2xl md:text-3xl font-bold uppercase tracking-tight text-white">
              {initialQuery ? `Results for "${initialQuery}"` : "All Videos"}
            </h1>
            <p className="text-muted-foreground mt-1">
              {total} {total === 1 ? "video" : "videos"} found
            </p>
          </div>
        </div>

        {/* Loading State */}
        {loading && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6" data-testid="loading-skeleton">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-card rounded-xl overflow-hidden">
                <Skeleton className="aspect-video" />
                <div className="p-5">
                  <Skeleton className="h-6 w-3/4 mb-2" />
                  <Skeleton className="h-4 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Grid */}
        {!loading && videos.length > 0 && (
          <div 
            className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            data-testid="video-grid"
          >
            {videos.map((video, index) => (
              <div key={video.id} className={`fade-in stagger-${(index % 5) + 1}`}>
                <VideoCard video={video} onClick={handleVideoClick} />
              </div>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!loading && videos.length === 0 && (
          <div 
            className="text-center py-20"
            data-testid="empty-state"
          >
            <Music className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="font-heading text-2xl font-bold uppercase text-white mb-2">
              No Videos Found
            </h2>
            <p className="text-muted-foreground mb-6">
              {initialQuery 
                ? `No results for "${initialQuery}". Try a different search term.`
                : "No videos in the database yet. Check back later!"}
            </p>
            <Button
              onClick={() => navigate("/")}
              className="bg-primary text-primary-foreground hover:bg-primary/90"
              data-testid="go-home-button"
            >
              Go Home
            </Button>
          </div>
        )}
      </main>
    </div>
  );
};

export default Search;

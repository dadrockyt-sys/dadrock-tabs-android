import { useState, useEffect, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { ExternalLink, FastForward } from "lucide-react";
import { Button } from "@/components/ui/button";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdInterstitial = () => {
  const { videoId } = useParams();
  const navigate = useNavigate();
  const [countdown, setCountdown] = useState(5);
  const [canSkip, setCanSkip] = useState(false);
  const [video, setVideo] = useState(null);
  const [loading, setLoading] = useState(true);

  const redirectToYouTube = useCallback(() => {
    if (video?.youtube_url) {
      window.open(video.youtube_url, "_blank");
      navigate("/search");
    }
  }, [video, navigate]);

  useEffect(() => {
    const fetchVideo = async () => {
      try {
        const response = await axios.get(`${API}/videos/${videoId}`);
        setVideo(response.data);
      } catch (error) {
        console.error("Error fetching video:", error);
        navigate("/search");
      } finally {
        setLoading(false);
      }
    };

    fetchVideo();
  }, [videoId, navigate]);

  useEffect(() => {
    if (!video) return;

    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          setCanSkip(true);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [video]);

  useEffect(() => {
    if (countdown === 0 && canSkip) {
      // Auto-redirect after countdown
      const autoRedirect = setTimeout(() => {
        redirectToYouTube();
      }, 2000);
      return () => clearTimeout(autoRedirect);
    }
  }, [countdown, canSkip, redirectToYouTube]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <img src={LOGO_URL} alt="Loading" className="w-32 h-auto mx-auto animate-pulse" />
          <p className="text-muted-foreground mt-4">Loading...</p>
        </div>
      </div>
    );
  }

  const progress = ((5 - countdown) / 5) * 100;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="max-w-lg w-full text-center">
        {/* Vinyl Record with Countdown */}
        <div className="relative mb-12">
          {/* Vinyl outer */}
          <div className="relative w-64 h-64 mx-auto">
            {/* Progress ring */}
            <svg className="absolute inset-0 w-full h-full -rotate-90">
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="hsl(var(--secondary))"
                strokeWidth="8"
                fill="none"
              />
              <circle
                cx="128"
                cy="128"
                r="120"
                stroke="hsl(var(--primary))"
                strokeWidth="8"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${progress * 7.54} 754`}
                className="transition-all duration-1000 ease-linear"
              />
            </svg>

            {/* Vinyl record */}
            <div 
              className={`absolute inset-4 vinyl-record overflow-hidden ${countdown > 0 ? 'animate-spin-slow' : ''}`}
              style={{
                backgroundImage: `url('https://images.unsplash.com/photo-1669801158950-f663cf15298c?crop=entropy&cs=srgb&fm=jpg&q=85')`,
                backgroundSize: 'cover',
                backgroundPosition: 'center'
              }}
            >
              {/* Center label */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-20 h-20 rounded-full bg-background border-4 border-primary flex items-center justify-center">
                  {countdown > 0 ? (
                    <span className="font-heading text-4xl font-bold text-primary" data-testid="countdown-number">
                      {countdown}
                    </span>
                  ) : (
                    <img src={LOGO_URL} alt="DadRock" className="w-12 h-12 object-contain" />
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Video Info */}
        {video && (
          <div className="mb-8 fade-in" data-testid="video-info">
            <h2 className="font-heading text-3xl md:text-4xl font-bold uppercase tracking-tight text-white mb-2">
              {video.song}
            </h2>
            <p className="text-xl text-muted-foreground">{video.artist}</p>
          </div>
        )}

        {/* Ad Message */}
        <div className="mb-8 p-6 bg-card rounded-xl border border-white/5">
          <p className="text-sm text-muted-foreground uppercase tracking-widest mb-2">
            Support DadRock Tabs
          </p>
          <p className="text-white">
            Love learning classic rock? Subscribe to our YouTube channel for more tabs!
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-4">
          {canSkip ? (
            <Button
              onClick={redirectToYouTube}
              size="lg"
              className="h-14 px-8 rounded-full font-heading font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90 glow-amber btn-lift"
              data-testid="watch-now-button"
            >
              <ExternalLink className="w-5 h-5 mr-2" />
              Watch on YouTube
            </Button>
          ) : (
            <Button
              onClick={() => {
                setCountdown(0);
                setCanSkip(true);
              }}
              variant="outline"
              size="lg"
              className="h-14 px-8 rounded-full font-heading font-bold uppercase tracking-wider border-white/20 text-white hover:bg-white/5"
              data-testid="skip-ad-button"
            >
              <FastForward className="w-5 h-5 mr-2" />
              Skip Ad ({countdown}s)
            </Button>
          )}

          <Button
            variant="ghost"
            onClick={() => navigate("/search")}
            className="text-muted-foreground hover:text-white"
            data-testid="back-to-search"
          >
            Back to Search
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AdInterstitial;

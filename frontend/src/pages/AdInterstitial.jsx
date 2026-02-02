import { useState, useEffect, useCallback, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { ExternalLink, FastForward } from "lucide-react";
import { Button } from "@/components/ui/button";

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Google Ad Component
const GoogleAd = () => {
  const adRef = useRef(null);
  const [adLoaded, setAdLoaded] = useState(false);

  useEffect(() => {
    try {
      if (window.adsbygoogle && adRef.current) {
        // Push the ad
        (window.adsbygoogle = window.adsbygoogle || []).push({});
        setAdLoaded(true);
      }
    } catch (error) {
      console.log("Ad loading error:", error);
    }
  }, []);

  return (
    <div className="w-full flex justify-center my-4">
      <ins
        ref={adRef}
        className="adsbygoogle"
        style={{ 
          display: "block",
          width: "100%",
          maxWidth: "336px",
          height: "280px",
          backgroundColor: adLoaded ? "transparent" : "#18181b"
        }}
        data-ad-client="ca-pub-6391677195320364"
        data-ad-slot="7237947171"
        data-ad-format="rectangle"
        data-full-width-responsive="true"
      />
    </div>
  );
};

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
      // Auto-redirect after countdown (increased to 5 seconds to show ad longer)
      const autoRedirect = setTimeout(() => {
        redirectToYouTube();
      }, 5000);
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
        {/* Video Info */}
        {video && (
          <div className="mb-6 fade-in" data-testid="video-info">
            <h2 className="font-heading text-2xl md:text-3xl font-bold uppercase tracking-tight text-white mb-1">
              {video.song}
            </h2>
            <p className="text-lg text-muted-foreground">{video.artist}</p>
          </div>
        )}

        {/* Countdown Timer */}
        <div className="relative mb-6">
          <div className="relative w-32 h-32 mx-auto">
            {/* Progress ring */}
            <svg className="absolute inset-0 w-full h-full -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="58"
                stroke="hsl(var(--secondary))"
                strokeWidth="6"
                fill="none"
              />
              <circle
                cx="64"
                cy="64"
                r="58"
                stroke="hsl(var(--primary))"
                strokeWidth="6"
                fill="none"
                strokeLinecap="round"
                strokeDasharray={`${progress * 3.64} 364`}
                className="transition-all duration-1000 ease-linear"
              />
            </svg>

            {/* Center content */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-24 h-24 rounded-full bg-card border-2 border-primary flex items-center justify-center">
                {countdown > 0 ? (
                  <span className="font-heading text-4xl font-bold text-primary" data-testid="countdown-number">
                    {countdown}
                  </span>
                ) : (
                  <img src={LOGO_URL} alt="DadRock" className="w-16 h-16 object-contain" />
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Google Ad */}
        <div className="mb-6 p-4 bg-card rounded-xl border border-white/5">
          <p className="text-xs text-muted-foreground uppercase tracking-widest mb-3">
            Advertisement
          </p>
          <GoogleAd />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col gap-3">
          {canSkip ? (
            <Button
              onClick={redirectToYouTube}
              size="lg"
              className="h-12 px-6 rounded-full font-heading font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90 glow-amber btn-lift"
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
              className="h-12 px-6 rounded-full font-heading font-bold uppercase tracking-wider border-white/20 text-white hover:bg-white/5"
              data-testid="skip-ad-button"
            >
              <FastForward className="w-5 h-5 mr-2" />
              Skip Ad ({countdown}s)
            </Button>
          )}

          <Button
            variant="ghost"
            onClick={() => navigate("/search")}
            className="text-muted-foreground hover:text-white text-sm"
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

import React from 'react';
import { Button } from "@/components/ui/button";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ error, errorInfo });
    // Log to console for debugging
    console.error('DadRock Tabs Error:', error);
    console.error('Component Stack:', errorInfo?.componentStack);
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-black flex items-center justify-center p-4">
          <div className="max-w-md w-full text-center">
            <img 
              src="https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png"
              alt="DadRock Tabs"
              className="w-32 h-auto mx-auto mb-6 opacity-50"
            />
            <h1 className="font-heading text-2xl font-bold uppercase tracking-tight text-white mb-4">
              Oops! Something went wrong
            </h1>
            <p className="text-muted-foreground mb-6">
              Don't worry, it happens to the best of us. Let's get you back to rocking!
            </p>
            <div className="flex flex-col gap-3">
              <Button
                onClick={this.handleReload}
                className="w-full h-12 rounded-full font-heading font-bold uppercase tracking-wider bg-primary text-primary-foreground hover:bg-primary/90"
              >
                Try Again
              </Button>
              <Button
                onClick={this.handleGoHome}
                variant="outline"
                className="w-full h-12 rounded-full font-heading font-bold uppercase tracking-wider border-white/20 text-white hover:bg-white/5"
              >
                Go Home
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

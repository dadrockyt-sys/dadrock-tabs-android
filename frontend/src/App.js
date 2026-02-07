import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "@/components/ui/sonner";
import ErrorBoundary from "@/components/ErrorBoundary";
import Home from "@/pages/Home";
import Search from "@/pages/Search";
import AdInterstitial from "@/pages/AdInterstitial";
import AdminLogin from "@/pages/AdminLogin";
import AdminDashboard from "@/pages/AdminDashboard";

function App() {
  return (
    <ErrorBoundary>
      <div className="App min-h-screen bg-background">
        {/* Noise overlay */}
        <div className="noise-overlay" />
        
        <BrowserRouter>
          <Routes>
            {/* Default routes */}
            <Route path="/" element={<Home />} />
            <Route path="/search" element={<Search />} />
            <Route path="/watch/:videoId" element={<AdInterstitial />} />
            <Route path="/admin" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminDashboard />} />
            
            {/* Language-specific routes */}
            <Route path="/en/*" element={<Home />} />
            <Route path="/es/*" element={<Home />} />
            <Route path="/pt-br/*" element={<Home />} />
            <Route path="/fr/*" element={<Home />} />
            <Route path="/de/*" element={<Home />} />
            <Route path="/it/*" element={<Home />} />
            <Route path="/ja/*" element={<Home />} />
            <Route path="/ru/*" element={<Home />} />
            
            {/* Language-specific search routes */}
            <Route path="/en/search" element={<Search />} />
            <Route path="/es/search" element={<Search />} />
            <Route path="/pt-br/search" element={<Search />} />
            <Route path="/fr/search" element={<Search />} />
            <Route path="/de/search" element={<Search />} />
            <Route path="/it/search" element={<Search />} />
            <Route path="/ja/search" element={<Search />} />
            <Route path="/ru/search" element={<Search />} />
          </Routes>
        </BrowserRouter>
        
        <Toaster position="top-right" />
      </div>
    </ErrorBoundary>
  );
}

export default App;

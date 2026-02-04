import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";

// Global error handler to catch unhandled errors
window.onerror = function(message, source, lineno, colno, error) {
  console.error('DadRock Tabs Global Error:', {
    message,
    source,
    lineno,
    colno,
    error: error?.stack || error
  });
  return false;
};

// Unhandled promise rejection handler
window.onunhandledrejection = function(event) {
  console.error('DadRock Tabs Unhandled Promise Rejection:', event.reason);
};

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then((registration) => {
        console.log('DadRock Tabs: Service Worker registered', registration.scope);
      })
      .catch((error) => {
        console.log('DadRock Tabs: Service Worker registration failed', error);
      });
  });
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

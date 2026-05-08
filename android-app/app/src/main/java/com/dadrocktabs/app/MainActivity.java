package com.dadrocktabs.app;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;

import androidx.appcompat.app.AppCompatActivity;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

import com.google.android.play.core.review.ReviewInfo;
import com.google.android.play.core.review.ReviewManager;
import com.google.android.play.core.review.ReviewManagerFactory;
import com.google.android.gms.tasks.Task;
import com.google.firebase.analytics.FirebaseAnalytics;

public class MainActivity extends AppCompatActivity {

    private static final String WEBSITE_URL = "https://www.dadrocktabs.com";
    private static final String APP_TRACKING_PARAMS = "?utm_source=android_app&utm_medium=app&utm_campaign=dadrock_app";
    private static final String PREFS_NAME = "dadrock_prefs";
    private static final String KEY_OPEN_COUNT = "app_open_count";
    private static final String KEY_LAST_REVIEW_PROMPT = "last_review_prompt_time";
    private static final int OPENS_BEFORE_REVIEW = 5;
    private static final long REVIEW_COOLDOWN_MS = 30L * 24 * 60 * 60 * 1000; // 30 days
    
    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefreshLayout;
    private FirebaseAnalytics firebaseAnalytics;
    private ReviewManager reviewManager;
    private Handler mainHandler;
    private boolean isShowingOfflinePage = false;
    private String lastLoadedUrl = "";

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize Firebase Analytics
        firebaseAnalytics = FirebaseAnalytics.getInstance(this);
        firebaseAnalytics.setAnalyticsCollectionEnabled(true);
        
        // Initialize main thread handler for delayed operations
        mainHandler = new Handler(Looper.getMainLooper());
        
        // Log app open event
        Bundle bundle = new Bundle();
        bundle.putString(FirebaseAnalytics.Param.SOURCE, "android_app");
        firebaseAnalytics.logEvent(FirebaseAnalytics.Event.APP_OPEN, bundle);
        
        // Set user property to identify app users
        firebaseAnalytics.setUserProperty("app_platform", "android");

        // Initialize In-App Review
        reviewManager = ReviewManagerFactory.create(this);

        // Track app opens and prompt for review
        trackAppOpenAndPromptReview();

        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);

        // Configure WebView settings
        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);
        webSettings.setLoadWithOverviewMode(true);
        webSettings.setUseWideViewPort(true);
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        webSettings.setMediaPlaybackRequiresUserGesture(false);
        webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setAllowFileAccess(true);
        webSettings.setJavaScriptCanOpenWindowsAutomatically(true);

        // Set WebViewClient
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageStarted(WebView view, String url, Bitmap favicon) {
                super.onPageStarted(view, url, favicon);
                progressBar.setVisibility(View.VISIBLE);
                
                // If we're navigating away from the offline page, reset the flag
                if (isShowingOfflinePage && url != null && !url.startsWith("file:///android_asset/")) {
                    isShowingOfflinePage = false;
                }
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                progressBar.setVisibility(View.GONE);
                swipeRefreshLayout.setRefreshing(false);
                
                // Don't track the offline error page in analytics
                if (isShowingOfflinePage || (url != null && url.startsWith("file:///android_asset/"))) {
                    return;
                }
                
                // Save the URL for retry after offline
                if (url != null && url.contains("dadrocktabs.com")) {
                    lastLoadedUrl = url;
                }
                
                // Delay reading the title to allow React/Next.js to hydrate
                // and update document.title via client-side rendering.
                // onPageFinished fires when initial HTML is loaded, but the
                // <title> tag may still be updating via JavaScript.
                mainHandler.postDelayed(() -> {
                    if (view == null) return;
                    
                    String pageTitle = view.getTitle();
                    if (pageTitle == null || pageTitle.isEmpty() 
                            || pageTitle.equals("about:blank")
                            || pageTitle.equalsIgnoreCase("Web page not available")) {
                        pageTitle = "DadRock Tabs";
                    }
                    
                    Bundle screenBundle = new Bundle();
                    screenBundle.putString(FirebaseAnalytics.Param.SCREEN_NAME, pageTitle);
                    screenBundle.putString(FirebaseAnalytics.Param.SCREEN_CLASS, "WebView");
                    screenBundle.putString("page_location", url);
                    screenBundle.putString("page_path", Uri.parse(url).getPath());
                    screenBundle.putString("page_title", pageTitle);
                    firebaseAnalytics.logEvent(FirebaseAnalytics.Event.SCREEN_VIEW, screenBundle);
                }, 800); // 800ms delay for React hydration
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                super.onReceivedError(view, request, error);
                
                // Only handle main frame errors (not sub-resource failures like images)
                if (request.isForMainFrame()) {
                    // Show branded offline page instead of default "Web page not available"
                    isShowingOfflinePage = true;
                    view.loadUrl("file:///android_asset/offline.html");
                }
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                
                // Keep dadrocktabs.com URLs in WebView
                if (url.contains("dadrocktabs.com")) {
                    return false;
                }
                
                // Open YouTube links in YouTube app or browser
                if (url.contains("youtube.com") || url.contains("youtu.be")) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }
                
                // Open all other external links in browser
                if (url.startsWith("http://") || url.startsWith("https://")) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }
                
                return false;
            }
        });

        // Set WebChromeClient for progress
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                progressBar.setProgress(newProgress);
            }
        });

        // Setup swipe to refresh
        swipeRefreshLayout.setOnRefreshListener(() -> {
            // If showing offline page, retry the last real URL
            if (isShowingOfflinePage && !lastLoadedUrl.isEmpty()) {
                isShowingOfflinePage = false;
                webView.loadUrl(lastLoadedUrl);
            } else {
                webView.reload();
            }
        });

        swipeRefreshLayout.setColorSchemeResources(
            android.R.color.holo_orange_dark,
            android.R.color.holo_red_dark
        );

        // Load the website with tracking params
        if (savedInstanceState == null) {
            webView.loadUrl(WEBSITE_URL + APP_TRACKING_PARAMS);
        }
    }

    /**
     * Track app open count and show Google Play In-App Review after the 5th open.
     * Respects a 30-day cooldown between review prompts.
     */
    private void trackAppOpenAndPromptReview() {
        SharedPreferences prefs = getSharedPreferences(PREFS_NAME, MODE_PRIVATE);
        int openCount = prefs.getInt(KEY_OPEN_COUNT, 0) + 1;
        long lastPrompt = prefs.getLong(KEY_LAST_REVIEW_PROMPT, 0);
        long now = System.currentTimeMillis();

        // Save updated open count
        prefs.edit().putInt(KEY_OPEN_COUNT, openCount).apply();

        // Check if we should prompt for review:
        // - At least N opens
        // - At least 30 days since last prompt (or never prompted)
        boolean shouldPrompt = openCount >= OPENS_BEFORE_REVIEW
                && (now - lastPrompt > REVIEW_COOLDOWN_MS);

        if (shouldPrompt) {
            // Pre-cache the review info
            Task<ReviewInfo> request = reviewManager.requestReviewFlow();
            request.addOnCompleteListener(task -> {
                if (task.isSuccessful()) {
                    ReviewInfo reviewInfo = task.getResult();
                    // Launch the review flow
                    Task<Void> flow = reviewManager.launchReviewFlow(this, reviewInfo);
                    flow.addOnCompleteListener(flowTask -> {
                        // Review flow finished (user may or may not have left a review)
                        // Google doesn't tell us the result — save timestamp regardless
                        prefs.edit().putLong(KEY_LAST_REVIEW_PROMPT, now).apply();
                        
                        // Log the review prompt event to Firebase
                        Bundle reviewBundle = new Bundle();
                        reviewBundle.putInt("open_count", openCount);
                        firebaseAnalytics.logEvent("review_prompt_shown", reviewBundle);
                    });
                }
            });
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        webView.saveState(outState);
    }

    @Override
    protected void onRestoreInstanceState(Bundle savedInstanceState) {
        super.onRestoreInstanceState(savedInstanceState);
        webView.restoreState(savedInstanceState);
    }

    @Override
    public void onConfigurationChanged(Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        // WebView will automatically adjust to the new configuration
    }
}

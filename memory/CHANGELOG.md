# DadRock Tabs - Changelog

## [Feb 4, 2026] - Bug Fix Session

### Fixed
- **Script Error Investigation**: Added comprehensive error handling to debug generic "Script error"
  - Added `ErrorBoundary` component to catch React errors gracefully
  - Added global `window.onerror` and `window.onunhandledrejection` handlers
  - Fixed race condition in 5-tap secret admin access logic in `Home.jsx`
  
- **External Resource Error**: Fixed 402 error from `grainy-gradients.vercel.app/noise.svg`
  - Replaced external SVG with inline CSS-based noise pattern
  - No more external dependencies for visual effects

### Tested
- All features verified working:
  - Home page: 100%
  - Search: 100% (93 results for "Led Zeppelin")
  - Ad interstitial: 100%
  - Admin login: 100%
  - Secret admin access (5-tap): 100%
  - External links: 100%
- Backend API: 20/20 tests passed

### Files Changed
- `/app/frontend/src/components/ErrorBoundary.jsx` (NEW)
- `/app/frontend/src/App.js` - Added ErrorBoundary wrapper
- `/app/frontend/src/index.js` - Added global error handlers
- `/app/frontend/src/pages/Home.jsx` - Fixed 5-tap logic
- `/app/frontend/src/index.css` - Fixed noise overlay

---

## [Feb 2, 2026] - Initial Build & Features

### Added
- Full-stack application with FastAPI backend and React frontend
- Searchable video database with 4,212+ videos
- Video cards with YouTube thumbnails
- 5-second skippable ad interstitial with merchandise promo
- Admin panel with password protection
- Secret admin access (tap logo 5 times)
- CRUD operations for videos
- Bulk CSV import
- YouTube channel sync feature
- PWA support (installable app)
- SEO setup (meta tags, sitemap, robots.txt)
- QR code for app access
- Android app configuration via Capacitor
- GitHub Actions workflow for Android builds
- Custom domain setup (dadrocktabs.com)
- Google Search Console verification

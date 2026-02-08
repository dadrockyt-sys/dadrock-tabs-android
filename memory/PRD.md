# DadRock Tabs - Product Requirements Document

## Original Problem Statement
Build an app that is used as a searchable database for the YouTube channel "DadRock Tabs". 
- Populate the database with all videos from the channel (4,212+ videos)
- Allow searching by song or artist
- Play a skippable ad (merchandise promo) before launching YouTube
- Create an admin panel to manage the database
- Support PWA installation
- Generate QR code for app access
- Link to merchandise store
- Make app discoverable by search engines

## User Personas
1. **Visitors**: Guitar/bass enthusiasts searching for classic rock tutorials
2. **Admin**: Channel owner managing the video database

## Core Requirements
- [x] Searchable video database (by song and artist) - 4,212+ videos
- [x] Video cards with YouTube thumbnails
- [x] 5-second skippable ad interstitial (merchandise promo)
- [x] Admin panel with password protection
- [x] Secret admin access (5-tap on logo)
- [x] CRUD operations for videos
- [x] Bulk CSV import functionality
- [x] YouTube channel sync feature
- [x] Dark theme with rock/music aesthetic
- [x] PWA support (installable)
- [x] SEO meta tags, sitemap, robots.txt
- [x] Merchandise links (creator-spring.com)
- [x] Support links (PayPal donations)
- [x] Request feature (Buy Me a Coffee)
- [x] QR code for app access
- [x] Android app via Capacitor

## Architecture
- **Frontend**: React with Tailwind CSS, Shadcn/UI components
- **Backend**: FastAPI with MongoDB
- **Auth**: Simple password-based admin authentication
- **Mobile**: Capacitor.js wrapper loading live web URL
- **CI/CD**: GitHub Actions for Android APK/AAB builds

## Database Schema
```javascript
videos: {
  id: UUID,
  song: String,
  artist: String,
  youtube_url: String,
  thumbnail: String,
  created_at: DateTime
}
```

## Admin Credentials
- Password: `Babyty99`
- Access: Click logo 5 times on home page OR navigate to /admin

## API Endpoints
- `GET /api/videos` - Search videos (query params: search, search_type, limit, skip)
- `GET /api/videos/{id}` - Get single video
- `POST /api/admin/login` - Admin authentication
- `GET /api/admin/stats` - Database statistics
- `POST /api/admin/videos` - Create video
- `PUT /api/admin/videos/{id}` - Update video
- `DELETE /api/admin/videos/{id}` - Delete video
- `POST /api/admin/videos/bulk` - Bulk CSV import
- `POST /api/admin/sync_youtube` - Sync from YouTube channel
- `GET /api/sitemap.xml` - XML sitemap for SEO

## External Links
- Merchandise: https://my-store-b8bb42.creator-spring.com
- Support: https://www.paypal.com/donate?hosted_button_id=FKZ2C3QW9ZBTE
- Request: https://buymeacoffee.com/dadrockytq/commissions
- YouTube Channel: DadRock Tabs

## Current Status
- **Videos in Database**: 4,212+
- **Artists**: 460+
- **All core features**: WORKING
- **PWA**: WORKING
- **Android App**: Ready for Play Store (loads live URL)
- **Featured Video**: YouTube Shorts embed added (Feb 2025)

## Prioritized Backlog
### P0 (Complete)
- [x] Core search functionality
- [x] Admin CRUD
- [x] Ad interstitial (merchandise promo)
- [x] YouTube sync
- [x] PWA support
- [x] SEO setup
- [x] Error handling (ErrorBoundary)

### P1 (Future Enhancements)
- [ ] Apple App Store version (requires Mac + Apple Developer account)
- [ ] Video categories/tags
- [ ] Featured videos section
- [ ] Advanced filtering

### P2 (Nice to Have)
- [ ] Analytics dashboard
- [ ] User favorites/bookmarks
- [ ] Email newsletter signup
- [ ] Custom domain sitemap fix

## Known Issues
- Sitemap returns 404 on custom domain (dadrocktabs.com) - works on preview URL
- Workaround: Use Google URL Inspection tool for manual indexing

## Recent Fixes (Feb 2025)
- **Android App Blank Screen Fix**: Added `dadrocktabs.com` and YouTube domains to `network_security_config.xml`
- **SDK Downgrade**: Downgraded from SDK 35 to SDK 34 for stable GitHub Actions builds
- **Gradle Version**: Updated to Gradle 8.2 and Android Gradle Plugin 8.2.2
- **Capacitor Config**: Added `allowNavigation` for YouTube domains
- **Version Bump**: v1.3 (versionCode 4)

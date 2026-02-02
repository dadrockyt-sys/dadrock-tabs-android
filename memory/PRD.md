# DadRock Tabs - Product Requirements Document

## Original Problem Statement
Build an app that is used as a searchable database for YouTube channel called DadRock Tabs. Populate the database with all of the videos on the channel. Allow the database to be searched by song or by artist. When the user clicks a link it will play a skippable ad before launching the search result on the YouTube platform. Create a backdoor (admin panel) to populate the YouTube database.

## User Personas
1. **Visitors**: Guitar enthusiasts searching for classic rock tabs/tutorials
2. **Admin**: Channel owner managing the video database

## Core Requirements
- [x] Searchable video database (by song and artist)
- [x] Video cards with YouTube thumbnails
- [x] 5-second skippable ad interstitial before YouTube redirect
- [x] Admin panel with password protection
- [x] CRUD operations for videos
- [x] Bulk CSV import functionality
- [x] Dark theme with rock/music aesthetic

## Architecture
- **Frontend**: React with Tailwind CSS, Shadcn/UI components
- **Backend**: FastAPI with MongoDB
- **Auth**: Simple password-based admin authentication

## What's Been Implemented (Feb 2, 2026)
- Home page with hero section and search bar
- Search results page with video grid
- Ad interstitial with vinyl record animation and countdown
- Admin login page
- Admin dashboard with:
  - Stats display (total videos, total artists)
  - Video table with thumbnails
  - Add/Edit/Delete video modals
  - Bulk CSV import
- Full CRUD API endpoints
- YouTube thumbnail auto-extraction

## Prioritized Backlog
### P0 (Done)
- [x] Core search functionality
- [x] Admin CRUD
- [x] Ad interstitial

### P1 (Future)
- [ ] Pagination for large datasets
- [ ] Video categories/tags
- [ ] Featured videos section

### P2 (Nice to Have)
- [ ] Analytics dashboard
- [ ] User favorites/bookmarks
- [ ] Email newsletter signup

## Admin Credentials
- Password: `dadrock2024` (configurable via ADMIN_PASSWORD env var)

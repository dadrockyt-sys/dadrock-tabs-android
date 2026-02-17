# DadRock Tabs - Product Requirements Document

## Overview
DadRock Tabs is a guitar and bass tablature finder app for classic rock music. It allows users to search for guitar/bass tabs from a curated collection of "dad rock" classics.

## Core Features

### 1. Home Page
- Hero section with DadRock logo
- Featured video player (admin configurable)
- Search functionality
- Popular artists quick links
- YouTube subscription button
- Social sharing buttons
- Request song / Support / Merch links
- Multi-language support (9 languages)

### 2. Search Page
- Search input with filter options (All/Song/Artist)
- Video grid with thumbnails
- Click-to-watch functionality
- Loading states

### 3. Watch Page
- Embedded YouTube player
- Video details (song, artist)
- Link to watch on YouTube
- Back navigation

### 4. Admin Panel
- Password-protected access (click logo 5 times)
- Featured video settings (URL, title, artist)
- Site statistics (total videos, total artists)
- Video preview

## API Endpoints

### Public
- `GET /api/health` - Health check
- `GET /api/settings` - Get site settings
- `GET /api/videos` - List videos with search
- `GET /api/videos/:id` - Get single video

### Admin (requires Basic Auth)
- `POST /api/admin/login` - Verify admin password
- `GET /api/admin/stats` - Get database stats
- `PUT /api/admin/settings` - Update site settings
- `POST /api/admin/videos` - Create video
- `PUT /api/admin/videos/:id` - Update video
- `DELETE /api/admin/videos/:id` - Delete video

## Database Collections

### videos
- id (UUID)
- song (string)
- artist (string)
- youtube_url (string)
- thumbnail (string)
- created_at (datetime)

### settings
- type: "site"
- featured_video_url (string)
- featured_video_title (string)
- featured_video_artist (string)
- updated_at (datetime)

## Tech Stack
- Next.js 14 (Full-stack)
- MongoDB
- Tailwind CSS
- shadcn/ui components
- Lucide React icons

## Default Admin Password
- `dadrock2024` (configurable via ADMIN_PASSWORD env var)

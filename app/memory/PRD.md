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

### artist_seo_content
- slug (string, unique) — primary lookup key
- artist (string) — display name
- content (object) — AI-generated bio, playing_style, gear_info, why_learn, fun_facts, meta_description
- generated_at (datetime)
- model (string) — e.g., "gpt-5-nano"

### song_seo_content
- slug (string, unique) — matches song_pages.slug
- title (string)
- artist (string)
- content (object) — AI-generated song_story, lesson_overview, difficulty_info, techniques, pro_tips, meta_description
- generated_at (datetime)
- model (string)

## API Endpoints

### Public
- `GET /api/health` - Health check
- `GET /api/settings` - Get site settings
- `GET /api/videos` - List videos with search
- `GET /api/videos/:id` - Get single video
- `GET /api/seo-content?type=artist&slug=...` - Get AI-generated SEO content for artist or song

### Admin (requires Basic Auth)
- `POST /api/admin/login` - Verify admin password
- `GET /api/admin/stats` - Get database stats
- `PUT /api/admin/settings` - Update site settings
- `POST /api/admin/videos` - Create video
- `PUT /api/admin/videos/:id` - Update video
- `DELETE /api/admin/videos/:id` - Delete video
- `GET /api/admin/health` - Website health check scanner
- `GET /api/admin/generate-seo` - Get AI content generation status (supports `?detail=artists` and `?detail=songs`)
- `POST /api/admin/generate-seo` - Generate AI SEO content (single or batch)

## Tech Stack
- Next.js 16 (Full-stack, App Router)
- MongoDB
- Tailwind CSS
- shadcn/ui components
- Lucide React icons
- OpenAI SDK (GPT-5-nano for SEO content generation)

## Default Admin Password
- `Babyty99` (configurable via ADMIN_PASSWORD env var)

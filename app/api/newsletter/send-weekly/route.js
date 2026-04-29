import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';
import { Resend } from 'resend';

// Weekly digest endpoint — triggered by external cron every Saturday
// Protected by a secret key to prevent unauthorized sends
// Usage: GET /api/newsletter/send-weekly?secret=YOUR_CRON_SECRET

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const secret = searchParams.get('secret');
  const cronSecret = process.env.CRON_SECRET || 'dadrock-weekly-2024';

  // Verify cron secret
  if (secret !== cronSecret) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const resendKey = process.env.RESEND_API_KEY;
  if (!resendKey) {
    return NextResponse.json({ 
      error: 'RESEND_API_KEY not configured. Add it to .env to enable email sending.',
      status: 'skipped'
    }, { status: 503 });
  }

  try {
    const db = await getDb();
    const resend = new Resend(resendKey);

    // Get videos from the last 7 days
    const sevenDaysAgo = new Date();
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);

    const recentVideos = await db.collection('videos')
      .find({ 
        created_at: { $gte: sevenDaysAgo.toISOString() }
      })
      .sort({ created_at: -1 })
      .limit(30)
      .project({ artist: 1, song: 1, thumbnail: 1, youtube_url: 1, created_at: 1 })
      .toArray();

    // If no new videos by created_at, try by MongoDB insertion order (last 20)
    let videosToSend = recentVideos;
    if (videosToSend.length === 0) {
      videosToSend = await db.collection('videos')
        .find({})
        .sort({ _id: -1 })
        .limit(20)
        .project({ artist: 1, song: 1, thumbnail: 1, youtube_url: 1, created_at: 1 })
        .toArray();
    }

    if (videosToSend.length === 0) {
      return NextResponse.json({ 
        message: 'No new videos to send this week',
        sent: 0,
      });
    }

    // Get active subscribers
    const subscribers = await db.collection('newsletter_subscribers')
      .find({ active: true })
      .project({ email: 1 })
      .toArray();

    if (subscribers.length === 0) {
      return NextResponse.json({ 
        message: 'No active subscribers',
        sent: 0,
      });
    }

    // Build the email HTML
    const emailHtml = buildWeeklyDigestEmail(videosToSend);
    const subject = `🎸 This Week on DadRock Tabs — ${videosToSend.length} New Lessons`;

    // Send to all subscribers (batch)
    let sentCount = 0;
    let failCount = 0;
    const errors = [];

    // Send in batches of 10 to respect rate limits
    const batchSize = 10;
    for (let i = 0; i < subscribers.length; i += batchSize) {
      const batch = subscribers.slice(i, i + batchSize);
      
      const sendPromises = batch.map(async (subscriber) => {
        try {
          await resend.emails.send({
            from: process.env.SENDER_EMAIL || 'DadRock Tabs <noreply@dadrocktabs.com>',
            to: [subscriber.email],
            subject,
            html: emailHtml,
          });
          sentCount++;
        } catch (err) {
          failCount++;
          errors.push({ email: subscriber.email, error: err.message });
        }
      });

      await Promise.all(sendPromises);
      
      // Small delay between batches
      if (i + batchSize < subscribers.length) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    // Log the send
    await db.collection('newsletter_logs').insertOne({
      date: new Date().toISOString(),
      type: 'weekly_digest',
      total_subscribers: subscribers.length,
      sent: sentCount,
      failed: failCount,
      videos_count: videosToSend.length,
      errors: errors.length > 0 ? errors : undefined,
    });

    return NextResponse.json({
      message: `Weekly digest sent successfully`,
      sent: sentCount,
      failed: failCount,
      total_subscribers: subscribers.length,
      videos_included: videosToSend.length,
    });

  } catch (error) {
    console.error('Weekly digest send error:', error);
    return NextResponse.json({ error: 'Failed to send weekly digest', details: error.message }, { status: 500 });
  }
}

function buildWeeklyDigestEmail(videos) {
  const today = new Date();
  const weekStart = new Date(today);
  weekStart.setDate(weekStart.getDate() - 7);
  
  const formatDate = (d) => d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  // Group videos by artist
  const byArtist = {};
  for (const video of videos) {
    const artist = video.artist?.replace(/ -$/, '').trim() || 'Unknown';
    if (!byArtist[artist]) byArtist[artist] = [];
    byArtist[artist].push(video);
  }

  const videoRows = videos.slice(0, 20).map((video, index) => {
    const artist = video.artist?.replace(/ -$/, '').trim() || 'Unknown';
    const song = video.song || 'Untitled';
    const thumbnail = video.thumbnail || `https://img.youtube.com/vi/default/mqdefault.jpg`;
    const songSlug = `${artist}-${song}`.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/(^-|-$)/g, '');
    const songUrl = `https://dadrocktabs.com/songs/${songSlug}`;

    return `
      <tr style="border-bottom: 1px solid #333;">
        <td style="padding: 12px 8px; vertical-align: middle; width: 30px; color: #666; font-size: 14px; text-align: center;">
          ${index + 1}
        </td>
        <td style="padding: 12px 8px; vertical-align: middle; width: 80px;">
          <img src="${thumbnail}" alt="${song}" width="72" height="54" style="border-radius: 6px; object-fit: cover; display: block;" />
        </td>
        <td style="padding: 12px 8px; vertical-align: middle;">
          <a href="${songUrl}" style="color: #fff; text-decoration: none; font-weight: 600; font-size: 15px; display: block;">
            ${song}
          </a>
          <span style="color: #f59e0b; font-size: 13px;">${artist}</span>
        </td>
        <td style="padding: 12px 8px; vertical-align: middle; text-align: right;">
          <a href="${songUrl}" style="display: inline-block; padding: 6px 14px; background: #f59e0b; color: #000; font-size: 12px; font-weight: 700; border-radius: 6px; text-decoration: none;">
            Learn
          </a>
        </td>
      </tr>
    `;
  }).join('');

  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>DadRock Tabs - Weekly Digest</title>
</head>
<body style="margin: 0; padding: 0; background-color: #09090b; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #09090b;">
    <tr>
      <td align="center" style="padding: 40px 16px;">
        <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="max-width: 600px; width: 100%;">
          
          <!-- Header -->
          <tr>
            <td style="padding: 0 0 30px 0; text-align: center;">
              <img src="https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png" alt="DadRock Tabs" width="60" height="60" style="display: inline-block; margin-bottom: 12px;" />
              <h1 style="margin: 0; color: #f59e0b; font-size: 28px; font-weight: 800;">
                DadRock Tabs
              </h1>
              <p style="margin: 8px 0 0; color: #888; font-size: 14px;">
                Weekly Lesson Digest — ${formatDate(weekStart)} to ${formatDate(today)}
              </p>
            </td>
          </tr>

          <!-- Intro -->
          <tr>
            <td style="padding: 0 0 24px 0;">
              <div style="background: linear-gradient(135deg, #1c1917, #292524); border: 1px solid #333; border-radius: 16px; padding: 24px;">
                <h2 style="margin: 0 0 8px; color: #fff; font-size: 20px;">
                  🎸 ${videos.length} New Lessons This Week
                </h2>
                <p style="margin: 0; color: #a1a1aa; font-size: 14px; line-height: 1.5;">
                  Here's what dropped on DadRock Tabs this week. Click any lesson to watch the free video tab tutorial.
                </p>
              </div>
            </td>
          </tr>

          <!-- Video List -->
          <tr>
            <td style="padding: 0 0 24px 0;">
              <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background: #18181b; border: 1px solid #333; border-radius: 12px; overflow: hidden;">
                ${videoRows}
              </table>
            </td>
          </tr>

          <!-- CTA -->
          <tr>
            <td style="padding: 0 0 30px 0; text-align: center;">
              <a href="https://dadrocktabs.com" style="display: inline-block; padding: 14px 32px; background: #f59e0b; color: #000; font-size: 16px; font-weight: 700; border-radius: 10px; text-decoration: none;">
                Browse All Lessons →
              </a>
            </td>
          </tr>

          <!-- Quick Links -->
          <tr>
            <td style="padding: 0 0 30px 0; text-align: center;">
              <p style="margin: 0 0 12px; color: #888; font-size: 13px;">Browse by category:</p>
              <a href="https://dadrocktabs.com/difficulty/beginner" style="color: #4ade80; text-decoration: none; font-size: 13px; margin: 0 8px;">Beginner</a>
              <a href="https://dadrocktabs.com/difficulty/intermediate" style="color: #fbbf24; text-decoration: none; font-size: 13px; margin: 0 8px;">Intermediate</a>
              <a href="https://dadrocktabs.com/difficulty/advanced" style="color: #f87171; text-decoration: none; font-size: 13px; margin: 0 8px;">Advanced</a>
              <a href="https://dadrocktabs.com/learn" style="color: #a78bfa; text-decoration: none; font-size: 13px; margin: 0 8px;">Guides</a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="border-top: 1px solid #333; padding: 24px 0 0; text-align: center;">
              <p style="margin: 0 0 8px; color: #555; font-size: 12px;">
                You're receiving this because you subscribed to DadRock Tabs weekly updates.
              </p>
              <p style="margin: 0; color: #555; font-size: 12px;">
                <a href="https://dadrocktabs.com" style="color: #666; text-decoration: underline;">Visit Website</a>
                &nbsp;|&nbsp;
                <a href="https://dadrocktabs.com/api/newsletter/unsubscribe?email={{EMAIL}}" style="color: #666; text-decoration: underline;">Unsubscribe</a>
              </p>
              <p style="margin: 16px 0 0; color: #444; font-size: 11px;">
                © ${today.getFullYear()} DadRock Tabs. Free guitar & bass tab lessons.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
  `;
}

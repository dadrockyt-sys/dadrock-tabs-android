import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';

// Unsubscribe endpoint — accessed via email link
// GET /api/newsletter/unsubscribe?email=user@example.com

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const email = searchParams.get('email');

  if (!email) {
    return new NextResponse(unsubscribeHtml('Invalid unsubscribe link.', false), {
      headers: { 'Content-Type': 'text/html' },
    });
  }

  try {
    const db = await getDb();
    const normalizedEmail = email.toLowerCase().trim();

    const result = await db.collection('newsletter_subscribers').updateOne(
      { email: normalizedEmail },
      { $set: { active: false, unsubscribed_at: new Date().toISOString() } }
    );

    if (result.matchedCount === 0) {
      return new NextResponse(unsubscribeHtml('This email was not found in our list.', false), {
        headers: { 'Content-Type': 'text/html' },
      });
    }

    return new NextResponse(unsubscribeHtml('You have been successfully unsubscribed.', true), {
      headers: { 'Content-Type': 'text/html' },
    });
  } catch (error) {
    console.error('Unsubscribe error:', error);
    return new NextResponse(unsubscribeHtml('Something went wrong. Please try again.', false), {
      headers: { 'Content-Type': 'text/html' },
    });
  }
}

function unsubscribeHtml(message, success) {
  return `
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Unsubscribe - DadRock Tabs</title>
  <style>
    body { 
      margin: 0; padding: 40px 20px; 
      background: #09090b; color: #fff; 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      display: flex; align-items: center; justify-content: center; min-height: 100vh;
    }
    .container { text-align: center; max-width: 400px; }
    .icon { font-size: 48px; margin-bottom: 16px; }
    h1 { color: ${success ? '#4ade80' : '#f59e0b'}; font-size: 24px; margin-bottom: 12px; }
    p { color: #a1a1aa; font-size: 16px; line-height: 1.5; }
    a { color: #f59e0b; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
  <div class="container">
    <div class="icon">${success ? '✅' : '⚠️'}</div>
    <h1>${success ? 'Unsubscribed' : 'Oops'}</h1>
    <p>${message}</p>
    <p style="margin-top: 24px;">
      <a href="https://dadrocktabs.com">← Back to DadRock Tabs</a>
    </p>
  </div>
</body>
</html>
  `;
}

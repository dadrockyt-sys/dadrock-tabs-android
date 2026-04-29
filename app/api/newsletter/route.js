import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';

export async function POST(request) {
  try {
    const body = await request.json();
    const { email } = body;

    if (!email || !email.includes('@') || !email.includes('.')) {
      return NextResponse.json({ error: 'Valid email required' }, { status: 400 });
    }

    // Normalize email
    const normalizedEmail = email.toLowerCase().trim();

    const db = await getDb();

    // Check if already subscribed
    const existing = await db.collection('newsletter_subscribers').findOne({ email: normalizedEmail });
    if (existing) {
      return NextResponse.json({ message: 'Already subscribed!', already_subscribed: true });
    }

    // Save subscriber
    await db.collection('newsletter_subscribers').insertOne({
      id: uuidv4(),
      email: normalizedEmail,
      subscribed_at: new Date().toISOString(),
      source: 'website',
      active: true,
    });

    return NextResponse.json({ message: 'Successfully subscribed!', already_subscribed: false });
  } catch (error) {
    console.error('Newsletter signup error:', error);
    return NextResponse.json({ error: 'Failed to subscribe' }, { status: 500 });
  }
}

// GET: Admin endpoint to view subscriber count
export async function GET(request) {
  try {
    const authHeader = request.headers.get('authorization');
    if (!authHeader || authHeader !== 'Basic ' + btoa('admin:Babyty99')) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const db = await getDb();
    const count = await db.collection('newsletter_subscribers').countDocuments({ active: true });
    const recent = await db.collection('newsletter_subscribers')
      .find({ active: true })
      .sort({ subscribed_at: -1 })
      .limit(10)
      .project({ email: 1, subscribed_at: 1 })
      .toArray();

    return NextResponse.json({ total_subscribers: count, recent });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch' }, { status: 500 });
  }
}

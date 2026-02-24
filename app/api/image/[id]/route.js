import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export async function GET(request, { params }) {
  try {
    const imageId = params.id;

    if (!imageId) {
      return NextResponse.json({ error: 'Image ID required' }, { status: 400 });
    }

    const db = await getDb();
    const image = await db.collection('uploads').findOne({ id: imageId });

    if (!image) {
      return NextResponse.json({ error: 'Image not found' }, { status: 404 });
    }

    // Extract base64 data from dataUrl
    const base64Data = image.dataUrl.split(',')[1];
    const buffer = Buffer.from(base64Data, 'base64');

    // Return the image with proper content type
    return new NextResponse(buffer, {
      headers: {
        'Content-Type': image.mimeType,
        'Cache-Control': 'public, max-age=31536000, immutable',
      },
    });

  } catch (error) {
    console.error('Image fetch error:', error);
    return NextResponse.json({ error: 'Failed to fetch image' }, { status: 500 });
  }
}

import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

// Admin password from env
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';

// Helper to verify admin auth
function verifyAdmin(request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    return false;
  }
  try {
    const base64Credentials = authHeader.split(' ')[1];
    const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8');
    const [, password] = credentials.split(':');
    return password === ADMIN_PASSWORD;
  } catch {
    return false;
  }
}

export async function POST(request) {
  try {
    // Verify admin authentication
    if (!verifyAdmin(request)) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const formData = await request.formData();
    const file = formData.get('file');

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json({ 
        error: 'Invalid file type. Allowed: JPEG, PNG, GIF, WebP' 
      }, { status: 400 });
    }

    // Validate file size (max 2MB for base64 storage)
    const maxSize = 2 * 1024 * 1024; // 2MB
    if (file.size > maxSize) {
      return NextResponse.json({ 
        error: 'File too large. Maximum size is 2MB' 
      }, { status: 400 });
    }

    // Convert file to base64
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    const base64 = buffer.toString('base64');
    const dataUrl = `data:${file.type};base64,${base64}`;

    // Generate unique ID for the image
    const imageId = uuidv4();

    // Store in MongoDB
    const db = await getDb();
    await db.collection('uploads').insertOne({
      id: imageId,
      filename: file.name,
      mimeType: file.type,
      dataUrl: dataUrl,
      size: file.size,
      created_at: new Date().toISOString()
    });

    // Return the API URL to fetch this image
    const publicUrl = `/api/image/${imageId}`;

    return NextResponse.json({ 
      success: true, 
      url: publicUrl,
      imageId: imageId 
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json({ 
      error: 'Failed to upload file: ' + error.message 
    }, { status: 500 });
  }
}

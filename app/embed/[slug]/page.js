'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';

export default function EmbedPage() {
  const params = useParams();
  const [song, setSong] = useState(null);

  useEffect(() => {
    fetch(`/api/songs?slug=${params.slug}`)
      .then(r => r.json())
      .then(data => {
        if (data.songs && data.songs.length > 0) setSong(data.songs[0]);
      })
      .catch(() => {});
  }, [params.slug]);

  if (!song) {
    return (
      <div style={{ padding: '20px', fontFamily: 'sans-serif', background: '#1a1a1a', color: '#fff', borderRadius: '12px', maxWidth: '400px' }}>
        <p>Loading...</p>
      </div>
    );
  }

  const baseUrl = typeof window !== 'undefined' ? window.location.origin : '';

  return (
    <div style={{
      padding: '20px',
      fontFamily: 'sans-serif',
      background: 'linear-gradient(135deg, #1a0a00, #2d1200)',
      color: '#fff',
      borderRadius: '12px',
      maxWidth: '400px',
      border: '2px solid #ff4500',
      boxShadow: '0 0 20px rgba(255,69,0,0.3)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
        <span style={{ fontSize: '24px' }}>🎸</span>
        <div>
          <h3 style={{ margin: 0, fontSize: '18px', color: '#ffd700' }}>{song.title}</h3>
          <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#ccc' }}>{song.artist}</p>
        </div>
      </div>
      {song.difficulty && (
        <span style={{ fontSize: '12px', background: '#ff4500', padding: '2px 8px', borderRadius: '4px' }}>
          {song.difficulty}
        </span>
      )}
      <a
        href={`${baseUrl}/songs/${song.slug}`}
        target="_blank"
        rel="noopener noreferrer"
        style={{
          display: 'block',
          marginTop: '12px',
          padding: '8px 16px',
          background: '#ff4500',
          color: '#fff',
          textDecoration: 'none',
          borderRadius: '6px',
          textAlign: 'center',
          fontWeight: 'bold',
          fontSize: '14px',
        }}
      >
        Learn This Song on DadRock Tabs →
      </a>
      <p style={{ fontSize: '10px', color: '#666', marginTop: '8px', textAlign: 'center' }}>
        Powered by DadRock Tabs
      </p>
    </div>
  );
}

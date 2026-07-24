import OpenAI from 'openai';
import { NextResponse } from 'next/server';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(request) {
  try {
    const { song, artist, transcriptionType } = await request.json();

    if (!song || !artist || !transcriptionType) {
      return NextResponse.json(
        { error: 'Song, artist, and transcription type are required.' },
        { status: 400 }
      );
    }

    const response = await openai.responses.create({
      model: 'gpt-5.4-mini',
      instructions: `
You create clear, readable guitar and bass tablature for educational use.

Return only plain-text tablature with:
- Song and artist
- Instrument
- Suggested tuning
- Section names such as Intro, Verse, Chorus, Riff, or Solo
- Six-string guitar TAB or four-string bass TAB
- Short performance notes where helpful

Do not include Markdown code fences.
Clearly state when the transcription is an approximate interpretation.
`,
      input: `
Create an approximate ${transcriptionType} transcription for:

Song: ${song}
Artist: ${artist}

Keep the preview concise and readable on a mobile screen.
`,
    });

    return NextResponse.json({
      tab: response.output_text,
    });
  } catch (error) {
    console.error('Generate tab error:', error);

    return NextResponse.json(
      { error: 'The tab could not be generated.' },
      { status: 500 }
    );
  }
}

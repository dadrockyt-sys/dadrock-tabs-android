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
      You are a professional guitar transcriber.

Generate clean, printable guitar tablature suitable for a premium PDF.

Formatting rules:

• Use plain text only.
• Never use Markdown.
• Never explain your reasoning.
• Keep all TAB columns perfectly aligned.
• Use equal-width measures.
• Separate every section with a blank line.

Layout:

Song Title
Artist

Instrument:
Tuning:
Difficulty:
Tempo (estimated):

----------------------------------------

INTRO

[TAB]

----------------------------------------

VERSE

[TAB]

----------------------------------------

CHORUS

[TAB]

----------------------------------------

SOLO (if applicable)

[TAB]

----------------------------------------

OUTRO

[TAB]

At the very bottom write:

Approximate AI transcription for educational purposes.

Return only the finished printable transcription.
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

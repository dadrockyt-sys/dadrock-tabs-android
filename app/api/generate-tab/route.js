import OpenAI from 'openai';
import { NextResponse } from 'next/server';

const ALLOWED_TRANSCRIPTION_TYPES = ['lead', 'rhythm', 'bass'];
const PREVIEW_LINE_LIMIT = 24;

function cleanText(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function createProtectedPreview(fullTab) {
  const lines = fullTab
    .split('\n')
    .map((line) => line.replace(/\s+$/g, ''));

  const previewLines = lines.slice(0, PREVIEW_LINE_LIMIT);

  return `${previewLines.join('\n')}

----------------------------------------
DADROCK TABS — PREVIEW ONLY
Purchase the printable PDF to unlock the full transcription.
dadrocktabs.com
----------------------------------------`;
}

export async function POST(request) {
  try {
    const apiKey = process.env.OPENAI_API_KEY;

    if (!apiKey) {
      return NextResponse.json(
        {
          error: 'OPENAI_API_KEY is not configured.',
        },
        { status: 503 }
      );
    }

    const openai = new OpenAI({
      apiKey,
    });

    const requestBody = await request.json();

    const song = cleanText(requestBody.song);
    const artist = cleanText(requestBody.artist);
    const transcriptionType = cleanText(
      requestBody.transcriptionType
    ).toLowerCase();

    if (!song || !artist || !transcriptionType) {
      return NextResponse.json(
        {
          error:
            'Song, artist, and transcription type are required.',
        },
        { status: 400 }
      );
    }

    if (!ALLOWED_TRANSCRIPTION_TYPES.includes(transcriptionType)) {
      return NextResponse.json(
        {
          error:
            'Transcription type must be lead, rhythm, or bass.',
        },
        { status: 400 }
      );
    }

    const response = await openai.responses.create({
      model:
        process.env.OPENAI_TAB_MODEL ||
        'gpt-5.4-mini',

      instructions: `
You are a professional guitar and bass transcriber.

Generate a clean, structured, printable tablature transcription suitable for a premium DadRock Tabs PDF.

Important requirements:

• Use plain text only.
• Never use Markdown.
• Never use code fences.
• Never explain your reasoning.
• Keep every tablature row aligned using monospaced spacing.
• Use equal-width measures whenever possible.
• Separate each musical section with a blank line.
• Include only the requested instrument.
• Do not include vocals, drums, keyboards, or unrelated instruments.
• Use realistic guitar or bass positions.
• Include common tablature notation where appropriate:
  h = hammer-on
  p = pull-off
  / = slide up
  \\ = slide down
  b = bend
  r = release
  ~ = vibrato
  x = muted note
  PM = palm mute

Use this layout:

Song Title
Artist

Instrument:
Tuning:
Difficulty:
Tempo (estimated):
Time Signature:

----------------------------------------

INTRO

[TAB]

----------------------------------------

VERSE

[TAB]

----------------------------------------

PRE-CHORUS (if applicable)

[TAB]

----------------------------------------

CHORUS

[TAB]

----------------------------------------

BRIDGE (if applicable)

[TAB]

----------------------------------------

SOLO (if applicable)

[TAB]

----------------------------------------

OUTRO

[TAB]

At the very bottom write:

Approximate AI transcription for educational purposes.

Return only the finished transcription.
`,

      input: `
Create an approximate ${transcriptionType} transcription for:

Song: ${song}
Artist: ${artist}

Generate enough structured material for a complete printable transcription.
`,
    });

    const fullTab = cleanText(response.output_text);

    if (!fullTab) {
      return NextResponse.json(
        {
          error:
            'The AI returned an empty transcription. Please try again.',
        },
        { status: 502 }
      );
    }

    const previewTab = createProtectedPreview(fullTab);

    /*
     * SECURITY:
     *
     * Only previewTab is returned to the browser.
     * fullTab is never included in the response.
     *
     * Future paid-download workflow:
     * 1. Save fullTab securely on the server or regenerate it after payment.
     * 2. Associate it with an internal generation ID.
     * 3. Verify the completed PayPal payment on the server.
     * 4. Generate the finished PDF only after verification.
     * 5. Return a short-lived download link.
     */

    return NextResponse.json({
      tab: previewTab,
      previewOnly: true,
      purchaseRequired: true,
      song,
      artist,
      transcriptionType,
    });
  } catch (error) {
    console.error('Generate tab error:', error);

    return NextResponse.json(
      {
        error:
          'The tab could not be generated. Please try again.',
      },
      { status: 500 }
    );
  }
}

from pathlib import Path
import re


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError(f"Missing expected block: {label}")
    return text.replace(old, new, 1)


page_path = Path('app/ai-tab/page.js')
page = page_path.read_text()

page = replace_once(
    page,
    """  const [
    usingFreeToken,
    setUsingFreeToken,
  ] = useState(false);
""",
    """  const [
    usingFreeToken,
    setUsingFreeToken,
  ] = useState(false);

  const [showTokenEntry, setShowTokenEntry] =
    useState(false);

  const [freeTokenCode, setFreeTokenCode] =
    useState('');
""",
    'free token state',
)

page = page.replace(
    """    setUsingFreeToken(false);
    setStatusMessage('');
""",
    """    setUsingFreeToken(false);
    setShowTokenEntry(false);
    setFreeTokenCode('');
    setStatusMessage('');
""",
    1,
)

page = replace_once(
    page,
    """      setUsingFreeToken(true);
      setGenerationError('');

      setStatusMessage(
        'Checking your free token...'
      );
""",
    """      const normalizedToken = freeTokenCode
        .trim()
        .toUpperCase();

      if (!normalizedToken) {
        setGenerationError(
          'Enter your free token code before unlocking.'
        );
        return;
      }

      setUsingFreeToken(true);
      setGenerationError('');

      setStatusMessage(
        'Checking your free token...'
      );
""",
    'token handler validation',
)

page = replace_once(
    page,
    """            body: JSON.stringify({
              customerEmail:
                customerEmail.trim(),

              song:
                songTitle.trim(),

              artist:
                artistName.trim(),
""",
    """            body: JSON.stringify({
              tokenCode: normalizedToken,

              customerEmail:
                customerEmail.trim(),

              songTitle:
                songTitle.trim(),

              artistName:
                artistName.trim(),
""",
    'token redemption payload',
)

page = replace_once(
    page,
    """        setStatusMessage(
          'Free token accepted. Your full PDF is now unlocked.'
        );
""",
    """        setShowTokenEntry(false);
        setFreeTokenCode('');

        setStatusMessage(
          'Free token accepted. Your full PDF is now unlocked.'
        );
""",
    'token success cleanup',
)

old_button = """                      <button
                        type=\"button\"
                        onClick={
                          handleFreeTokenUnlock
                        }
                        disabled={usingFreeToken}
                        className=\"flex min-h-[54px] items-center justify-center gap-2 rounded-xl border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm font-black text-green-300 transition hover:bg-green-500/15 disabled:cursor-not-allowed disabled:opacity-60\"
                      >
                        {usingFreeToken ? (
                          <Loader2
                            size={19}
                            className=\"animate-spin\"
                          />
                        ) : (
                          <Ticket size={19} />
                        )}

                        {usingFreeToken
                          ? 'Checking Token...'
                          : 'Use Free Token'}
                      </button>
"""

new_button = """                      <div className=\"space-y-3\">
                        <button
                          type=\"button\"
                          onClick={() => {
                            setShowTokenEntry(
                              (current) => !current
                            );
                            setGenerationError('');
                          }}
                          disabled={usingFreeToken}
                          className=\"flex min-h-[54px] w-full items-center justify-center gap-2 rounded-xl border border-green-500/40 bg-green-500/10 px-4 py-3 text-sm font-black text-green-300 transition hover:bg-green-500/15 disabled:cursor-not-allowed disabled:opacity-60\"
                        >
                          <Ticket size={19} />
                          Use Free Token
                        </button>

                        {showTokenEntry && (
                          <div className=\"rounded-xl border border-green-500/30 bg-black/40 p-3\">
                            <label
                              htmlFor=\"free-token-code\"
                              className=\"mb-2 block text-xs font-bold uppercase tracking-wide text-green-300\"
                            >
                              Enter Token Code
                            </label>

                            <input
                              id=\"free-token-code\"
                              type=\"text\"
                              value={freeTokenCode}
                              onChange={(event) =>
                                setFreeTokenCode(
                                  event.target.value.toUpperCase()
                                )
                              }
                              onKeyDown={(event) => {
                                if (event.key === 'Enter') {
                                  event.preventDefault();
                                  handleFreeTokenUnlock();
                                }
                              }}
                              placeholder=\"DRT-XXXX-XXXX-XXXX\"
                              autoCapitalize=\"characters\"
                              autoComplete=\"off\"
                              spellCheck={false}
                              className=\"w-full rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-3 text-center font-mono text-sm uppercase tracking-wider text-white outline-none transition focus:border-green-500\"
                            />

                            <button
                              type=\"button\"
                              onClick={handleFreeTokenUnlock}
                              disabled={
                                usingFreeToken ||
                                !freeTokenCode.trim()
                              }
                              className=\"mt-3 flex min-h-[48px] w-full items-center justify-center gap-2 rounded-lg bg-green-500 px-4 py-3 text-sm font-black text-black transition hover:bg-green-400 disabled:cursor-not-allowed disabled:opacity-50\"
                            >
                              {usingFreeToken ? (
                                <Loader2
                                  size={18}
                                  className=\"animate-spin\"
                                />
                              ) : (
                                <LockKeyhole size={18} />
                              )}

                              {usingFreeToken
                                ? 'Checking Token...'
                                : 'Redeem Token & Unlock'}
                            </button>
                          </div>
                        )}
                      </div>
"""
page = replace_once(page, old_button, new_button, 'free token UI')
page_path.write_text(page)


free_route = Path('app/api/free-tab-token/route.js')
free_route.write_text("""import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function clean(value, maximumLength = 254) {
  return String(value || '').trim().slice(0, maximumLength);
}

export async function POST(request) {
  try {
    const body = await request.json();
    const tokenCode = clean(body.tokenCode, 40).toUpperCase();
    const customerEmail = clean(body.customerEmail).toLowerCase();
    const songTitle = clean(body.songTitle, 120);
    const artistName = clean(body.artistName, 120);
    const transcriptionType = clean(body.transcriptionType, 40).toLowerCase();

    if (!tokenCode) {
      return NextResponse.json(
        { error: 'Enter your free token code.' },
        { status: 400 }
      );
    }

    if (!/^DRT-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$/.test(tokenCode)) {
      return NextResponse.json(
        { error: 'Enter a valid token in the format DRT-XXXX-XXXX-XXXX.' },
        { status: 400 }
      );
    }

    if (!customerEmail || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(customerEmail)) {
      return NextResponse.json(
        { error: 'Enter the email address being used for this PDF.' },
        { status: 400 }
      );
    }

    if (!songTitle || !artistName || !['lead', 'rhythm', 'bass'].includes(transcriptionType)) {
      return NextResponse.json(
        { error: 'Song, artist, and transcription type are required.' },
        { status: 400 }
      );
    }

    const db = await getDb();
    const collection = db.collection('tab_tokens');
    const now = new Date();

    const token = await collection.findOne({
      code: tokenCode,
      active: true,
      usesRemaining: { $gt: 0 },
      $and: [
        {
          $or: [
            { assignedEmail: null },
            { assignedEmail: { $exists: false } },
            { assignedEmail: customerEmail },
          ],
        },
        {
          $or: [
            { expiresAt: null },
            { expiresAt: { $exists: false } },
            { expiresAt: { $gt: now } },
          ],
        },
      ],
    });

    if (!token) {
      return NextResponse.json(
        { error: 'This token is invalid, expired, already used, or assigned to another email.' },
        { status: 404 }
      );
    }

    const redemption = {
      redeemedAt: now,
      customerEmail,
      songTitle,
      artistName,
      transcriptionType,
      youtubeUrl: body.youtubeUrl ? String(body.youtubeUrl) : null,
    };

    const result = await collection.findOneAndUpdate(
      {
        _id: token._id,
        active: true,
        usesRemaining: { $gt: 0 },
      },
      {
        $inc: { usesRemaining: -1 },
        $push: { redemptions: redemption },
        $set: { updatedAt: now },
      },
      { returnDocument: 'after' }
    );

    if (!result) {
      return NextResponse.json(
        { error: 'This token is no longer available.' },
        { status: 409 }
      );
    }

    return NextResponse.json({
      success: true,
      unlocked: true,
      tokenId: token.code,
      usesRemaining: result.usesRemaining,
    });
  } catch (error) {
    console.error('Free token redemption error:', error);
    return NextResponse.json(
      { error: 'Unable to redeem the free token.' },
      { status: 500 }
    );
  }
}
""")

pdf_path = Path('app/api/generate-tab-pdf/route.js')
pdf = pdf_path.read_text()
old_verify = """  const token = await db.collection('tab_tokens').findOne({
    code: tokenReference,
    assignedEmail: customerEmail,
    redemptions: {
"""
new_verify = """  const token = await db.collection('tab_tokens').findOne({
    code: tokenReference,
    $or: [
      { assignedEmail: null },
      { assignedEmail: { $exists: false } },
      { assignedEmail: customerEmail },
    ],
    redemptions: {
"""
pdf = replace_once(pdf, old_verify, new_verify, 'free token PDF verification')
pdf_path.write_text(pdf)

print('Free token entry and redemption flow repaired.')

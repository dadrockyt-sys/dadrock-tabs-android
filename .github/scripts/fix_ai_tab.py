from pathlib import Path
import re

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

# Keep the previously verified runtime repairs idempotent.
required_icons = {
    "AlertCircle": "  ArrowLeft,\n",
    "ArrowRight": "  ArrowLeft,\n",
    "CheckCircle2": "  Check,\n",
    "Lock": "  Loader2,\n",
    "Music": "  Mail,\n",
    "Play": "  Music2,\n",
}

for icon, anchor in required_icons.items():
    if re.search(rf"^\s*{icon},\s*$", text, re.MULTILINE) is None:
        if anchor not in text:
            raise RuntimeError(f"Could not find import anchor for {icon}")
        text = text.replace(anchor, anchor + f"  {icon},\n", 1)

text = text.replace("isEmailValid", "emailIsValid")
text = text.replace("type.label", "type.title")
text = text.replace("selectedTypeDetails?.label", "selectedTypeDetails?.title")
text = text.replace("<PayPalButton", "<PayPalCheckoutButton")
text = text.replace("</PayPalButton>", "</PayPalCheckoutButton>")
text = re.sub(
    r"const\s+Icon\s*=\s*type\.icon\s*;",
    "const Icon = Guitar;",
    text,
)

# Make uploaded audio the only accepted source.
text = re.sub(
    r"const sourceType = audioFile\s*\? 'audio'\s*:\s*isValidYouTubeUrl\s*\? 'youtube'\s*:\s*null;",
    "const sourceType = audioFile ? 'audio' : null;",
    text,
    count=1,
)

# Remove the visible YouTube input card while preserving the upload card.
youtube_card_pattern = re.compile(
    r"\n\s*<section\n\s*className=\{`rounded-2xl border p-5 transition \$\{\n\s*sourceType === 'youtube'.*?\n\s*</section>\n(?=\s*<section\n\s*className=\{`rounded-2xl border p-5 transition \$\{\n\s*sourceType === 'audio')",
    re.DOTALL,
)
text, removed_cards = youtube_card_pattern.subn("\n", text, count=1)

text = text.replace(
    '            <div className="grid gap-4 lg:grid-cols-2">',
    '            <div className="mx-auto max-w-2xl">',
    1,
)

# Route all analysis requests through the existing uploaded-audio endpoint.
text = re.sub(
    r"const endpoint =\s*source === 'youtube'\s*\? '/api/analyze-youtube-tab'\s*:\s*'/api/analyze-audio-tab';",
    "const endpoint = '/api/analyze-audio-tab';",
    text,
    count=1,
)
text = re.sub(
    r"setStatusMessage\(\s*source === 'youtube'\s*\? 'Preparing the YouTube audio for analysis\.\.\.'\s*:\s*'Analyzing your selected instrument\.\.\.'\s*\);",
    "setStatusMessage('Analyzing your uploaded audio...');",
    text,
    count=1,
)

# Remove YouTube-only fields from payloads.
text = re.sub(
    r"\n\s*youtubeUrl:\s*source === 'youtube'\s*\? youtubeUrl\.trim\(\)\s*:\s*null,\s*\n\s*youtubeVideoId:\s*source === 'youtube'\s*\? youtubeVideoId\s*:\s*null,",
    "",
    text,
)
text = re.sub(
    r"\n\s*youtubeUrl:\s*sourceType === 'youtube'\s*\? youtubeUrl\.trim\(\)\s*:\s*null,",
    "",
    text,
)
text = re.sub(
    r"\n\s*if \(\s*sourceType === 'youtube'\s*\) \{\s*setStatusMessage\(\s*'Sending the YouTube reference to the DadRock analyzer\.\.\.'\s*\);\s*\}",
    "",
    text,
    count=1,
)

replacements = {
    "Use a YouTube link or upload your own audio.": "Upload an audio file you possess and have permission to analyze.",
    "Turn your audio or YouTube reference into professional guitar or bass tablature.": "Turn an audio file you possess into professional guitar or bass tablature.",
    "Choose your source, select Lead, Rhythm, or Bass, review a short watermarked preview, then unlock the finished PDF.": "Upload your audio, select Lead, Rhythm, or Bass, review a short watermarked preview, then unlock the finished PDF.",
    "Paste a public YouTube link or upload an audio file from your device.": "Upload an audio file from your device that you possess and have permission to analyze.",
    "Choose Your Audio Source": "Upload Your Audio",
    "Please provide a valid YouTube link or upload an audio file.": "Please upload an audio file before continuing.",
    "Paste a YouTube link or upload an audio file.": "Upload an audio file you possess and may legally analyze.",
    "Upload Any Song": "Upload Your Audio",
    "source selection to PDF delivery.": "audio upload to PDF delivery.",
    "Upload your own recording or paste a YouTube reference and let the DadRock AI transcription engine": "Upload an audio file you possess and let the DadRock AI transcription engine",
    "I confirm that I have permission to analyze this recording and that I understand this AI transcription is generated for educational and personal practice purposes.": "I confirm that I possess this audio file, have permission to analyze it, and understand this AI transcription is generated for educational and personal practice purposes.",
}
for old, new in replacements.items():
    text = text.replace(old, new)

text = text.replace(
    "description: 'Paste a YouTube link or upload an audio file.',",
    "description: 'Upload an audio file you possess and may legally analyze.',",
)

# Match the cleaner Version 1 presentation.
style_replacements = {
    'className="relative z-10 mx-auto w-full max-w-6xl px-4 pb-16 pt-4 sm:px-6 lg:px-8"':
        'className="relative z-10 mx-auto w-full max-w-2xl px-4 py-8"',
    'className="inline-flex items-center gap-2 rounded-full border border-zinc-800 bg-zinc-950/80 px-4 py-2 text-sm font-semibold text-zinc-300 transition hover:border-orange-500/60 hover:text-white"':
        'className="mb-8 inline-flex items-center gap-2 text-zinc-400 transition-colors hover:text-amber-400"',
    '<span>Back Home</span>': '<span>Back to DadRock Tabs</span>',
    'className="overflow-hidden rounded-[28px] border border-orange-500/30 bg-gradient-to-b from-zinc-950 via-[#111111] to-zinc-950 shadow-2xl shadow-orange-950/20"':
        'className="overflow-hidden rounded-3xl border border-amber-500/40 bg-zinc-900 shadow-2xl shadow-orange-500/10"',
    'className="text-3xl font-black tracking-tight text-white sm:text-5xl"':
        'className="text-2xl font-bold text-white sm:text-3xl"',
    'Guitar & Bass Tab Generator': 'AI Tab Generator',
    'className="mx-auto mt-3 max-w-2xl text-sm leading-6 text-zinc-400 sm:text-base"':
        'className="mt-1 text-sm text-zinc-400"',
    'Everything You Need in One Place': 'Create a printable PDF using AI',
    'className="text-xl font-black text-white sm:text-3xl"':
        'className="text-xl font-bold text-white"',
    'Choose Your Instrument Part': 'Choose your transcription',
    'className="text-lg font-black text-white"':
        'className="text-xl font-bold text-white"',
}
for old, new in style_replacements.items():
    text = text.replace(old, new)

# Put all three transcription choices on one mobile row with no horizontal slider.
text = text.replace(
    'className="grid gap-3 sm:grid-cols-3"',
    'className="grid grid-cols-3 gap-2 sm:gap-3"',
    1,
)
text = text.replace(
    'className={`rounded-2xl border p-5 text-left transition ${',
    'className={`min-w-0 rounded-xl border p-2.5 text-center transition sm:rounded-2xl sm:p-4 ${',
    1,
)
text = text.replace(
    'className="flex items-start justify-between gap-3"',
    'className="flex items-center justify-center"',
    1,
)
text = text.replace(
    'className={`flex h-12 w-12 items-center justify-center rounded-xl border ${',
    'className={`flex h-10 w-10 items-center justify-center rounded-xl border sm:h-12 sm:w-12 ${',
    1,
)
text = text.replace('<Icon\n                              size={25}\n                            />', '<Icon\n                              size={22}\n                            />', 1)
text = text.replace(
    'className="mt-4 text-xl font-black leading-tight text-white"',
    'className="mt-3 text-[13px] font-black leading-tight text-white sm:text-lg"',
    1,
)
text = text.replace(
    'className="mt-2 text-sm leading-6 text-zinc-400"',
    'className="mt-1 hidden text-xs leading-5 text-zinc-400 sm:block"',
    1,
)
# Keep the selected check visible without stealing card width.
text = text.replace(
    '<CheckCircle2\n                              size={19}\n                              className="text-orange-400"\n                            />',
    '<CheckCircle2\n                              size={16}\n                              className="absolute right-2 top-2 text-orange-400 sm:right-3 sm:top-3"\n                            />',
    1,
)
text = text.replace(
    'className={`min-w-0 rounded-xl border p-2.5 text-center transition sm:rounded-2xl sm:p-4 ${',
    'className={`relative min-w-0 rounded-xl border p-2.5 text-center transition sm:rounded-2xl sm:p-4 ${',
    1,
)

# Restore the original dynamic generate button wording.
old_button = """{isGenerating ? (
                    <>
                      <Loader2
                        size={22}
                        className=\"animate-spin\"
                      />

                      Generating AI Preview...
                    </>
                  ) : (
                    <>
                      <Sparkles size={22} />

                      Generate Watermarked Preview
                    </>
                  )}"""
new_button = """{isGenerating ? (
                    <>
                      <Loader2
                        size={22}
                        className=\"animate-spin\"
                      />

                      AI is creating your preview...
                    </>
                  ) : (
                    <>
                      <FileText size={22} />

                      {selectedType
                        ? `Generate ${
                            selectedType.charAt(0).toUpperCase() +
                            selectedType.slice(1)
                          } Tab`
                        : 'Select a transcription'}
                    </>
                  )}"""
text = text.replace(old_button, new_button)
text = text.replace(
    'className={`flex w-full items-center justify-center gap-2 rounded-xl py-4 font-bold transition-all ${',
    'className={`flex w-full items-center justify-center gap-3 rounded-xl px-5 py-4 text-lg font-black transition-all ${',
)
text = text.replace(
    "? 'bg-gradient-to-r from-orange-500 to-amber-500 text-white hover:scale-[1.01]'",
    "? 'bg-gradient-to-r from-amber-500 to-red-600 text-white hover:scale-[1.02]'",
)
text = text.replace(
    ": 'cursor-not-allowed bg-zinc-800 text-zinc-500'",
    ": 'cursor-not-allowed bg-zinc-700 text-zinc-400'",
)

text = re.sub(r"^\s*Youtube,\s*\n", "", text, flags=re.MULTILINE)

if text == original:
    print("No changes needed; the transcription choices are already compact.")
else:
    if removed_cards == 0 and "YouTube Reference" in text:
        raise RuntimeError("Could not safely locate and remove the YouTube input card")
    path.write_text(text, encoding="utf-8")
    print("Placed all three transcription choices in one compact mobile row.")

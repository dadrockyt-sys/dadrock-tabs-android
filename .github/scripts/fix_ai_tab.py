from pathlib import Path
import re

path = Path("app/ai-tab/page.js")
text = path.read_text(encoding="utf-8")
original = text

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

old_steps = """const PROCESS_STEPS = [
  'Choose Source',
  'Analyze Audio',
  'Detect Notes',
  'Generate Tab',
  'Unlock PDF',
];"""

new_steps = """const PROCESS_STEPS = [
  {
    title: 'Choose Source',
    description: 'Paste a YouTube link or upload an audio file.',
  },
  {
    title: 'Analyze Audio',
    description: 'The analyzer isolates the selected instrument part.',
  },
  {
    title: 'Detect Notes',
    description: 'Pitch and timing information are converted into notes.',
  },
  {
    title: 'Generate Tab',
    description: 'The detected notes are arranged as playable tablature.',
  },
  {
    title: 'Unlock PDF',
    description: 'Preview the result and unlock the finished PDF.',
  },
];"""

text = text.replace(old_steps, new_steps)

if text == original:
    print("No changes needed; all known repairs are already applied.")
else:
    path.write_text(text, encoding="utf-8")
    print("Applied AI tab runtime repairs.")

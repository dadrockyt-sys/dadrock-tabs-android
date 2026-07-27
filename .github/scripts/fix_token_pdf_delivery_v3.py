from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text()

old_guard = """      if (!previewUnlocked) {
        setGenerationError(
          'Unlock the finished PDF before downloading.'
        );

        return;
      }

      const resolvedUnlockReference =
        unlockReference || purchaseOrderId;
"""
new_guard = """      const resolvedUnlockReference =
        unlockReference || purchaseOrderId;

      const hasExplicitUnlock = Boolean(
        unlockReference && unlockMethod
      );

      if (!previewUnlocked && !hasExplicitUnlock) {
        setGenerationError(
          'Unlock the finished PDF before downloading.'
        );

        return;
      }
"""
if old_guard not in text:
    raise RuntimeError('Expected download unlock guard not found')
text = text.replace(old_guard, new_guard, 1)

old_fields = """              songTitle:
                songTitle.trim(),

              artistName:
                artistName.trim(),
"""
new_fields = """              song:
                songTitle.trim(),

              artist:
                artistName.trim(),
"""
if old_fields not in text:
    raise RuntimeError('Expected PDF request fields not found')
text = text.replace(old_fields, new_fields, 1)

# Make token errors visible beside the token controls rather than only in an earlier page section.
old_token_button = """                          onClick={
                            handleFreeTokenUnlock
                          }
"""
new_token_button = """                          onClick={() => {
                            setGenerationError('');
                            handleFreeTokenUnlock();
                          }}
"""
if old_token_button in text:
    text = text.replace(old_token_button, new_token_button, 1)

path.write_text(text)
print('Token redemption and PDF delivery state repaired.')

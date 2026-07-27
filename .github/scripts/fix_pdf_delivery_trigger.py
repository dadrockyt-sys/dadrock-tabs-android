from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text()

text = text.replace(
"""  const handleDownloadPdf =
    async () => {
""",
"""  const handleDownloadPdf =
    async ({ unlockReference = '', unlockMethod = '' } = {}) => {
""",
1,
)

text = text.replace(
"""      if (!purchaseOrderId) {
        setGenerationError(
          'The unlock reference is missing.'
        );

        return;
      }
""",
"""      const resolvedUnlockReference =
        unlockReference || purchaseOrderId;

      const resolvedUnlockMethod =
        unlockMethod ||
        (paymentCompleted ? 'paypal' : 'free-token');

      if (!resolvedUnlockReference) {
        setGenerationError(
          'The unlock reference is missing.'
        );

        return;
      }
""",
1,
)

text = text.replace(
"""              orderId:
                paymentCompleted
                  ? purchaseOrderId
                  : null,

              tokenReference:
                !paymentCompleted
                  ? purchaseOrderId
                  : null,

              unlockMethod:
                paymentCompleted
                  ? 'paypal'
                  : 'free-token',
""",
"""              orderId:
                resolvedUnlockMethod === 'paypal'
                  ? resolvedUnlockReference
                  : null,

              tokenReference:
                resolvedUnlockMethod === 'free-token'
                  ? resolvedUnlockReference
                  : null,

              unlockMethod:
                resolvedUnlockMethod,
""",
1,
)

text = text.replace(
"""        setStatusMessage(
          'Free token accepted. Your full PDF is now unlocked.'
        );

        window.setTimeout(() => {
""",
"""        setStatusMessage(
          'Free token accepted. Creating and emailing your full PDF...'
        );

        await handleDownloadPdf({
          unlockReference: tokenReference,
          unlockMethod: 'free-token',
        });

        window.setTimeout(() => {
""",
1,
)

text = text.replace(
"""                  onClick={
                    handleDownloadPdf
                  }
                  disabled={isDownloading}
                  className="mt-6 flex w-full items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4 text-lg font-black text-white transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
""",
"""                  onClick={() => {
                    handleDownloadPdf();
                  }}
                  disabled={isDownloading}
                  className="relative z-20 mt-6 flex w-full touch-manipulation items-center justify-center gap-3 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 px-6 py-4 text-lg font-black text-white transition hover:scale-[1.01] disabled:cursor-not-allowed disabled:opacity-60"
""",
1,
)

path.write_text(text)
print('Robust PDF delivery trigger repair applied.')

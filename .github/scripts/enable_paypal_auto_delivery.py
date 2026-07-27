from pathlib import Path

path = Path('app/ai-tab/page.js')
text = path.read_text(encoding='utf-8')

old = """  const handlePaymentApproved =
    ({ orderId } = {}) => {
      setGenerationError('');

      if (!orderId) {
        setPaymentCompleted(false);
        setPreviewUnlocked(false);
        setStatusMessage('');
        setGenerationError(
          'PayPal did not return an order ID.'
        );
        return;
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);
      setPreviewUnlocked(true);
      setUsingFreeToken(false);
      setStatusMessage(
        'Payment confirmed. Your full PDF is now unlocked.'
      );

      window.setTimeout(() => {
        document
          .getElementById('download-section')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    };"""

new = """  const handlePaymentApproved =
    async ({ orderId } = {}) => {
      setGenerationError('');

      if (!orderId) {
        setPaymentCompleted(false);
        setPreviewUnlocked(false);
        setStatusMessage('');
        setGenerationError(
          'PayPal did not return an order ID.'
        );
        return;
      }

      setPurchaseOrderId(orderId);
      setPaymentCompleted(true);
      setPreviewUnlocked(true);
      setUsingFreeToken(false);
      setStatusMessage(
        'Payment confirmed. Creating and emailing your full PDF...'
      );

      await handleDownloadPdf({
        unlockReference: orderId,
        unlockMethod: 'paypal',
      });

      window.setTimeout(() => {
        document
          .getElementById('download-section')
          ?.scrollIntoView({
            behavior: 'smooth',
            block: 'start',
          });
      }, 150);
    };"""

if old not in text:
    raise SystemExit('Expected PayPal approval handler was not found; no changes made.')

path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('Updated PayPal approval to automatically generate, download, and email the PDF.')

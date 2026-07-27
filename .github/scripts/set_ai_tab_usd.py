from pathlib import Path

replacements = {
    Path('components/PayPalCheckoutButton.js'): [
        ('&currency=CAD&intent=capture', '&currency=USD&intent=capture'),
    ],
    Path('app/api/paypal/create-order/route.js'): [
        ("const CURRENCY = 'CAD';", "const CURRENCY = 'USD';"),
    ],
    Path('app/api/paypal/capture-order/route.js'): [
        ("const CURRENCY = 'CAD';", "const CURRENCY = 'USD';"),
    ],
    Path('app/api/generate-tab-pdf/route.js'): [
        ("const CURRENCY = 'CAD';", "const CURRENCY = 'USD';"),
    ],
    Path('app/ai-tab/page.js'): [
        ('Pay once: ${PRICE} CAD.', 'Pay once: ${PRICE} USD.'),
    ],
}

changed = []
for path, pairs in replacements.items():
    text = path.read_text()
    original = text
    for old, new in pairs:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text)
        changed.append(str(path))

if not changed:
    raise SystemExit('No USD currency changes were needed or expected text was not found.')

print('Updated to USD:', ', '.join(changed))

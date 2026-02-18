# DadRock Tabs Android App

Android WebView app for [www.dadrocktabs.com](https://www.dadrocktabs.com)

## Features
- Full WebView wrapper for the DadRock Tabs website
- Pull-to-refresh functionality
- Progress bar while loading
- External links open in browser/YouTube app
- Back button navigation support
- Dark theme matching the website

## 🚀 Automated GitHub Actions Build

### Quick Start - Run a Build
1. Go to your GitHub repository
2. Click **Actions** tab
3. Select **"Build Android AAB"** workflow
4. Click **"Run workflow"**
5. Enter version code (e.g., `20`) and version name (e.g., `2.0.0`)
6. Click **"Run workflow"**
7. Download AAB from **Artifacts** when complete

### Setting Up Signed Builds (For Play Store)

To create signed AAB files automatically, add these secrets to your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:

| Secret Name | Description |
|------------|-------------|
| `KEYSTORE_BASE64` | Your keystore file encoded in base64 |
| `KEYSTORE_PASSWORD` | Password for the keystore |
| `KEY_ALIAS` | Alias of the signing key |
| `KEY_PASSWORD` | Password for the key |

#### How to encode your keystore:
```bash
base64 -i your-keystore.jks | pbcopy  # macOS (copies to clipboard)
base64 -w 0 your-keystore.jks         # Linux (outputs to terminal)
```

### Workflow Triggers
- **Manual**: Run anytime via "Run workflow" button
- **Auto on push**: Builds when `android-app/` folder changes
- **Pull requests**: Builds for testing on PRs

## Build Instructions (Local)

### Using Android Studio
1. Open this project in Android Studio
2. Go to **Build** → **Generate Signed Bundle / APK**
3. Select **Android App Bundle**
4. Create or select your keystore
5. Choose **release** build variant
6. Click **Finish**

### Using Command Line
```bash
./gradlew bundleRelease
```

The AAB file will be at: `app/build/outputs/bundle/release/app-release.aab`

## App Icons
Replace the placeholder icons in:
- `app/src/main/res/mipmap-mdpi/` (48x48px)
- `app/src/main/res/mipmap-hdpi/` (72x72px)
- `app/src/main/res/mipmap-xhdpi/` (96x96px)
- `app/src/main/res/mipmap-xxhdpi/` (144x144px)
- `app/src/main/res/mipmap-xxxhdpi/` (192x192px)

## Version
- Version Code: 20
- Version Name: 2.0.0

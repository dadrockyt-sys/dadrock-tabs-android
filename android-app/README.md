# DadRock Tabs Android App

Android WebView app for [www.dadrocktabs.com](https://www.dadrocktabs.com)

## Features
- Full WebView wrapper for the DadRock Tabs website
- Pull-to-refresh functionality
- Progress bar while loading
- External links open in browser/YouTube app
- Back button navigation support
- Dark theme matching the website

## Build Instructions

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
- Version Code: 2
- Version Name: 2.0.0

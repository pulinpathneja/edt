# EDT Flutter App

Travel companion app built with Flutter.

## Setup

1. **Install Flutter**: https://docs.flutter.dev/get-started/install

2. **Get dependencies**:
   ```bash
   cd flutter_app
   flutter pub get
   ```

3. **Add assets**:
   - Place background image as `assets/images/welcome_bg.png`
   - Add SF Pro Display fonts to `assets/fonts/` (or use system fonts)

4. **Run the app**:
   ```bash
   flutter run
   ```

## Structure

```
lib/
├── main.dart              # App entry point
├── screens/
│   └── welcome_screen.dart  # Welcome/onboarding screen
└── theme/
    └── app_theme.dart       # Colors, typography, spacing
```

## Design System

### Colors
- Primary Dark: `#1A1A2E`
- Text Secondary: `#4A4A68`
- Background: `#F5F5F7`

### Typography
- Font: SF Pro Display
- Headline: 28px semibold
- Body: 16px regular

### Spacing
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, xxl: 48px

### Border Radius
- sm: 8px, md: 12px, lg: 16px, xl: 24px, pill: 28px

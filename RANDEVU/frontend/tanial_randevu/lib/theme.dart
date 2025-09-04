import 'package:flutter/material.dart';

class AppTheme {
  static const Color _primary = Color(0xFF2E7D32); // health green
  static const Color _onPrimary = Color(0xFFFFFFFF);
  static const Color _secondary = Color(0xFF00695C);

  static ColorScheme get lightColorScheme => const ColorScheme(
        brightness: Brightness.light,
        primary: _primary,
        onPrimary: _onPrimary,
        primaryContainer: Color(0xFFA5D6A7),
        onPrimaryContainer: Color(0xFF003314),
        secondary: _secondary,
        onSecondary: Colors.white,
        secondaryContainer: Color(0xFF8BD0C7),
        onSecondaryContainer: Color(0xFF00201C),
        tertiary: Color(0xFF1565C0),
        onTertiary: Colors.white,
        tertiaryContainer: Color(0xFFBBDEFB),
        onTertiaryContainer: Color(0xFF001E3C),
        error: Color(0xFFB3261E),
        onError: Colors.white,
        errorContainer: Color(0xFFFCDAD5),
        onErrorContainer: Color(0xFF410002),
        background: Colors.white,
        onBackground: Color(0xFF1C1B1F),
        surface: Colors.white,
        onSurface: Color(0xFF1C1B1F),
        outline: Color(0xFF74777F),
        outlineVariant: Color(0xFFC4C6CC),
        shadow: Colors.black54,
        scrim: Colors.black,
        inverseSurface: Color(0xFF313033),
        onInverseSurface: Color(0xFFF4EFF4),
        inversePrimary: Color(0xFF81C784),
      );

  static ColorScheme get darkColorScheme => const ColorScheme(
        brightness: Brightness.dark,
        primary: _primary,
        onPrimary: _onPrimary,
        primaryContainer: Color(0xFF204D24),
        onPrimaryContainer: Color(0xFFB9F6CA),
        secondary: _secondary,
        onSecondary: Colors.white,
        secondaryContainer: Color(0xFF004D43),
        onSecondaryContainer: Color(0xFFA7FFEB),
        tertiary: Color(0xFF90CAF9),
        onTertiary: Color(0xFF0A0A0A),
        tertiaryContainer: Color(0xFF0D47A1),
        onTertiaryContainer: Color(0xFFE3F2FD),
        error: Color(0xFFF2B8B5),
        onError: Color(0xFF601410),
        errorContainer: Color(0xFF8C1D18),
        onErrorContainer: Color(0xFFFFDAD4),
        background: Color(0xFF121212),
        onBackground: Color(0xFFE6E1E5),
        surface: Color(0xFF121212),
        onSurface: Color(0xFFE6E1E5),
        outline: Color(0xFF8E9199),
        outlineVariant: Color(0xFF3F424A),
        shadow: Colors.black,
        scrim: Colors.black,
        inverseSurface: Color(0xFFE6E1E5),
        onInverseSurface: Color(0xFF313033),
        inversePrimary: Color(0xFF81C784),
      );

  static ThemeData light() {
    return ThemeData(
      colorScheme: lightColorScheme,
      useMaterial3: true,
      visualDensity: VisualDensity.adaptivePlatformDensity,
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        titleTextStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(72),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          elevation: 1.5,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(72),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          elevation: 0,
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(12))),
      ),
    );
  }

  static ThemeData dark() {
    return ThemeData(
      colorScheme: darkColorScheme,
      useMaterial3: true,
      visualDensity: VisualDensity.adaptivePlatformDensity,
      appBarTheme: const AppBarTheme(
        centerTitle: true,
        titleTextStyle: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          minimumSize: const Size.fromHeight(72),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          elevation: 1.5,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size.fromHeight(72),
          shape:
              RoundedRectangleBorder(borderRadius: BorderRadius.circular(24)),
          textStyle: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
          elevation: 0,
        ),
      ),
      inputDecorationTheme: const InputDecorationTheme(
        border: OutlineInputBorder(
            borderRadius: BorderRadius.all(Radius.circular(12))),
      ),
    );
  }
}

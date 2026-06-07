import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // ─── Color palette ───────────────────────────────────────
  static const Color _primaryDark = Color(0xFF1A237E); // Deep indigo
  static const Color _primary = Color(0xFF3F51B5); // Indigo
  static const Color _primaryLight = Color(0xFF5C6BC0);
  static const Color _accent = Color(0xFF00BFA5); // Teal accent
  static const Color _surface = Color(0xFF1E1E2E);
  static const Color _surfaceVariant = Color(0xFF252540);
  static const Color _background = Color(0xFF14142B);
  static const Color _cardColor = Color(0xFF1E1E34);
  static const Color _error = Color(0xFFEF5350);
  static const Color _onPrimary = Colors.white;
  static const Color _onSurface = Color(0xFFE0E0E0);
  static const Color _onSurfaceDim = Color(0xFF9E9E9E);
  static const Color _divider = Color(0xFF2A2A45);

  // ─── Sidebar colors ──────────────────────────────────────
  static const Color sidebarBg = Color(0xFF12122A);
  static const Color sidebarItemHover = Color(0xFF1E1E3C);
  static const Color sidebarItemActive = Color(0xFF2A2A55);

  // ─── Semantic colors ─────────────────────────────────────
  static const Color success = Color(0xFF66BB6A);
  static const Color warning = Color(0xFFFFA726);
  static const Color danger = _error;

  // ─── ThemeData ────────────────────────────────────────────
  static ThemeData get darkTheme {
    final baseTextTheme = GoogleFonts.interTextTheme(
      ThemeData.dark().textTheme,
    );

    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: _background,
      colorScheme: const ColorScheme.dark(
        primary: _primary,
        onPrimary: _onPrimary,
        secondary: _accent,
        surface: _surface,
        onSurface: _onSurface,
        error: _error,
      ),
      cardColor: _cardColor,
      dividerColor: _divider,
      appBarTheme: const AppBarTheme(
        backgroundColor: _surface,
        foregroundColor: _onPrimary,
        elevation: 0,
      ),
      textTheme: baseTextTheme.copyWith(
        headlineLarge: baseTextTheme.headlineLarge?.copyWith(
          color: _onPrimary,
          fontWeight: FontWeight.w700,
        ),
        headlineMedium: baseTextTheme.headlineMedium?.copyWith(
          color: _onPrimary,
          fontWeight: FontWeight.w600,
        ),
        titleLarge: baseTextTheme.titleLarge?.copyWith(
          color: _onPrimary,
          fontWeight: FontWeight.w600,
        ),
        titleMedium: baseTextTheme.titleMedium?.copyWith(
          color: _onSurface,
          fontWeight: FontWeight.w500,
        ),
        bodyLarge: baseTextTheme.bodyLarge?.copyWith(color: _onSurface),
        bodyMedium: baseTextTheme.bodyMedium?.copyWith(color: _onSurface),
        bodySmall: baseTextTheme.bodySmall?.copyWith(color: _onSurfaceDim),
        labelLarge: baseTextTheme.labelLarge?.copyWith(
          color: _onPrimary,
          fontWeight: FontWeight.w600,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: _surfaceVariant,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 18,
          vertical: 16,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide.none,
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _divider, width: 1),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _primaryLight, width: 2),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _error, width: 1),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: const BorderSide(color: _error, width: 2),
        ),
        labelStyle: GoogleFonts.inter(color: _onSurfaceDim),
        hintStyle: GoogleFonts.inter(color: _onSurfaceDim),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: _primary,
          foregroundColor: _onPrimary,
          minimumSize: const Size(double.infinity, 52),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(14),
          ),
          textStyle: GoogleFonts.inter(
            fontSize: 16,
            fontWeight: FontWeight.w600,
          ),
          elevation: 0,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(foregroundColor: _primaryLight),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: _surface,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        titleTextStyle: GoogleFonts.inter(
          color: _onPrimary,
          fontSize: 20,
          fontWeight: FontWeight.w700,
        ),
      ),
      snackBarTheme: SnackBarThemeData(
        backgroundColor: _surfaceVariant,
        contentTextStyle: GoogleFonts.inter(color: _onSurface),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      dataTableTheme: DataTableThemeData(
        headingRowColor: WidgetStateProperty.all(_surfaceVariant),
        dataRowColor: WidgetStateProperty.resolveWith((states) {
          if (states.contains(WidgetState.hovered)) {
            return _surfaceVariant.withAlpha(120);
          }
          return Colors.transparent;
        }),
        headingTextStyle: GoogleFonts.inter(
          color: _onSurfaceDim,
          fontWeight: FontWeight.w600,
          fontSize: 13,
        ),
        dataTextStyle: GoogleFonts.inter(color: _onSurface, fontSize: 14),
        dividerThickness: 0.5,
      ),
      tooltipTheme: TooltipThemeData(
        decoration: BoxDecoration(
          color: _primaryDark,
          borderRadius: BorderRadius.circular(8),
        ),
        textStyle: GoogleFonts.inter(color: _onPrimary, fontSize: 12),
      ),
    );
  }
}

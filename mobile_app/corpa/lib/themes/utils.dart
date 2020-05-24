import 'package:flutter/material.dart';

final ThemeData kLightTheme = _buildLightTheme();

ThemeData _buildLightTheme() {
  final ThemeData base = ThemeData.light();
  return base.copyWith(
    primaryColor: Colors.white,
    accentColor: Colors.black,
    canvasColor: Colors.transparent,
    primaryIconTheme: IconThemeData(color: Colors.black),
    textTheme: TextTheme(
      headline5: TextStyle(
          fontFamily: 'Sans',
          fontWeight: FontWeight.bold,
          color: Colors.black,
          fontSize: 24),
      bodyText2: TextStyle(
          fontFamily: 'Sans',
          fontWeight: FontWeight.bold,
          color: Colors.black,
          fontSize: 24),
      bodyText1: TextStyle(
          fontFamily: 'Sans',
          fontWeight: FontWeight.bold,
          color: Colors.black,
          fontSize: 18),
    ),
  );
}

final ThemeData kDarkTheme = _buildDarkTheme();

ThemeData _buildDarkTheme() {
  final ThemeData base = ThemeData.dark();
  return base.copyWith(
    primaryColor: Color(0xff323639),
    accentColor: Colors.blue,
    canvasColor: Colors.transparent,
    primaryIconTheme: IconThemeData(color: Colors.black),
    // textTheme: TextTheme(
    // headline: TextStyle(
    //     fontFamily: 'Sans',
    //     fontWeight: FontWeight.bold,
    //     color: Colors.white,
    //     fontSize: 24),
    // body1: TextStyle(
    //     fontFamily: 'Sans',
    //     fontWeight: FontWeight.bold,
    //     color: Colors.white,
    //     fontSize: 24),
    // body2: TextStyle(
    //     fontFamily: 'Sans',
    //     fontWeight: FontWeight.bold,
    //     color: Colors.white,
    //     fontSize: 18),
    // ),
  );
}

final ThemeData kAmoledTheme = _buildAmoledTheme();

ThemeData _buildAmoledTheme() {
  final ThemeData base = ThemeData.dark();
  return base.copyWith(
    primaryColor: Colors.black,
    accentColor: Colors.white,
    // backgroundColor: Colors.black,
    // foregroundColor: Colors.greenAccent,
    canvasColor: Colors.black,
    primaryIconTheme: IconThemeData(color: Colors.black),
    scaffoldBackgroundColor: Colors.black,
  );
}

// Gradient Bgs
/// HomePage bg gradient
final kGradientBackground = BoxDecoration(
  gradient: RadialGradient(
    radius: 2.5,
    center: Alignment.bottomRight,
    colors: [Colors.greenAccent, Colors.black],
  ),
);

/// LoginPage bg gradient
final kGradientBackgroundLogin = BoxDecoration(
  gradient: RadialGradient(
    radius: 2.5,
    center: Alignment.centerRight,
    colors: [Colors.greenAccent, Colors.black],
  ),
);

/// RecordPage bg gradient
final kGradientBackgroundRecord = BoxDecoration(
    gradient: RadialGradient(
  radius: 2.5,
  center: Alignment.centerRight,
  colors: [Colors.blueGrey, Colors.black],
));

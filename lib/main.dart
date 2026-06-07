import 'dart:io';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';

import 'core/theme.dart';
import 'providers/auth_provider.dart';
import 'providers/producto_provider.dart';
import 'screens/dashboard/dashboard_screen.dart';
import 'screens/login/login_screen.dart';
import 'services/auth_service.dart';
import 'services/producto_service.dart';

// ─── Allow HTTP (non-HTTPS) connections ────────────────────
class MyHttpOverrides extends HttpOverrides {
  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return super.createHttpClient(context)
      ..badCertificateCallback = (cert, host, port) => true;
  }
}

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = MyHttpOverrides();

  final authService = AuthService();
  final productoService = ProductoService(authService);

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authService)..checkSession(),
        ),
        ChangeNotifierProvider(
          create: (_) => ProductoProvider(productoService),
        ),
      ],
      child: const MercadoShopApp(),
    ),
  );
}

class MercadoShopApp extends StatelessWidget {
  const MercadoShopApp({super.key});

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();

    final router = GoRouter(
      initialLocation: '/login',
      redirect: (context, state) {
        final loggedIn = authProvider.isAuthenticated;
        final loggingIn = state.matchedLocation == '/login';

        if (!loggedIn && !loggingIn) return '/login';
        if (loggedIn && loggingIn) return '/dashboard';
        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/dashboard',
          builder: (context, state) => const DashboardScreen(),
        ),
      ],
    );

    return MaterialApp.router(
      title: 'MercadoShop',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      routerConfig: router,
    );
  }
}

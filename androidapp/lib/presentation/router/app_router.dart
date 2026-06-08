import 'package:go_router/go_router.dart';
import 'package:mercadoshop_app/presentation/pages/main/main_navigation_page.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      name: 'home',
      builder: (context, state) => const MainNavigationPage(),
    ),
  ],
);

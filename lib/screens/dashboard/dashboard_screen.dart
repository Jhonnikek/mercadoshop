import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/producto_provider.dart';
import 'pages/home_page.dart';
import 'pages/productos_page.dart';
import 'widgets/sidebar.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    // Load products when the dashboard opens.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ProductoProvider>().loadProductos();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Row(
        children: [
          // Sidebar
          Sidebar(
            selectedIndex: _selectedIndex,
            onItemTap: (i) => setState(() => _selectedIndex = i),
          ),
          // Main content area
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 280),
              switchInCurve: Curves.easeOut,
              switchOutCurve: Curves.easeIn,
              child: _selectedIndex == 0
                  ? const HomePage(key: ValueKey('home'))
                  : const ProductosPage(key: ValueKey('productos')),
            ),
          ),
        ],
      ),
    );
  }
}

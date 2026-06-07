import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../providers/auth_provider.dart';
import '../../../core/theme.dart';

class Sidebar extends StatefulWidget {
  final int selectedIndex;
  final ValueChanged<int> onItemTap;

  const Sidebar({
    super.key,
    required this.selectedIndex,
    required this.onItemTap,
  });

  @override
  State<Sidebar> createState() => _SidebarState();
}

class _SidebarState extends State<Sidebar> {
  int _hoveredIndex = -1;

  static final _items = [
    _SidebarItem(icon: Icons.dashboard_rounded, label: 'Dashboard'),
    _SidebarItem(icon: Icons.inventory_2_rounded, label: 'Productos'),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 220,
      decoration: const BoxDecoration(
        color: AppTheme.sidebarBg,
        border: Border(
          right: BorderSide(color: Color(0xFF2A2A45), width: 1),
        ),
      ),
      child: Column(
        children: [
          // ── Brand ────────────────────────────────────────
          const SizedBox(height: 28),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: LinearGradient(
                    colors: [
                      Theme.of(context).colorScheme.primary,
                      const Color(0xFF00BFA5),
                    ],
                  ),
                ),
                child: const Icon(
                  Icons.storefront_rounded,
                  size: 18,
                  color: Colors.white,
                ),
              ),
              const SizedBox(width: 10),
              Text(
                'MercadoShop',
                style: GoogleFonts.inter(
                  fontSize: 17,
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                  letterSpacing: -0.3,
                ),
              ),
            ],
          ),
          const SizedBox(height: 36),

          // ── Menu items ───────────────────────────────────
          for (int i = 0; i < _items.length; i++) ...[
            _buildItem(i, _items[i]),
            if (i < _items.length - 1) const SizedBox(height: 4),
          ],

          const Spacer(),

          // ── Logout ───────────────────────────────────────
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 20),
            child: SizedBox(
              width: double.infinity,
              child: TextButton.icon(
                onPressed: () => _confirmLogout(context),
                icon: const Icon(Icons.logout_rounded, size: 18),
                label: Text(
                  'Cerrar sesión',
                  style: GoogleFonts.inter(fontSize: 13),
                ),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.white60,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildItem(int index, _SidebarItem item) {
    final isActive = widget.selectedIndex == index;
    final isHovered = _hoveredIndex == index;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: MouseRegion(
        onEnter: (_) => setState(() => _hoveredIndex = index),
        onExit: (_) => setState(() => _hoveredIndex = -1),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          curve: Curves.easeOut,
          decoration: BoxDecoration(
            color: isActive
                ? AppTheme.sidebarItemActive
                : isHovered
                    ? AppTheme.sidebarItemHover
                    : Colors.transparent,
            borderRadius: BorderRadius.circular(10),
            border: isActive
                ? Border.all(
                    color: Theme.of(context).colorScheme.primary.withAlpha(60),
                    width: 1,
                  )
                : null,
          ),
          child: Material(
            color: Colors.transparent,
            child: InkWell(
              borderRadius: BorderRadius.circular(10),
              onTap: () => widget.onItemTap(index),
              child: Padding(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                child: Row(
                  children: [
                    Icon(
                      item.icon,
                      size: 20,
                      color: isActive
                          ? Theme.of(context).colorScheme.secondary
                          : Colors.white54,
                    ),
                    const SizedBox(width: 12),
                    Text(
                      item.label,
                      style: GoogleFonts.inter(
                        fontSize: 14,
                        fontWeight:
                            isActive ? FontWeight.w600 : FontWeight.w400,
                        color: isActive ? Colors.white : Colors.white70,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _confirmLogout(BuildContext context) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cerrar sesión'),
        content: const Text('¿Estás seguro de que deseas cerrar sesión?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancelar'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(ctx);
              context.read<AuthProvider>().logout();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Cerrar sesión'),
          ),
        ],
      ),
    );
  }
}

class _SidebarItem {
  final IconData icon;
  final String label;
  const _SidebarItem({required this.icon, required this.label});
}

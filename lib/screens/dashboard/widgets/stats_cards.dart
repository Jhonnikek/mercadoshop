import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class StatsCards extends StatelessWidget {
  final int totalProductos;
  final String? mayorStockNombre;
  final int? mayorStockValor;
  final String? masCaroNombre;
  final double? masCaroPrecio;

  const StatsCards({
    super.key,
    required this.totalProductos,
    this.mayorStockNombre,
    this.mayorStockValor,
    this.masCaroNombre,
    this.masCaroPrecio,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.inventory_2_rounded,
            label: 'Total Productos',
            value: '$totalProductos',
            gradient: const [Color(0xFF3F51B5), Color(0xFF5C6BC0)],
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _StatCard(
            icon: Icons.trending_up_rounded,
            label: 'Mayor Stock',
            value: mayorStockNombre ?? '—',
            subtitle: mayorStockValor != null
                ? '$mayorStockValor unidades'
                : null,
            gradient: const [Color(0xFF00897B), Color(0xFF00BFA5)],
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: _StatCard(
            icon: Icons.attach_money_rounded,
            label: 'Más Caro',
            value: masCaroNombre ?? '—',
            subtitle: masCaroPrecio != null
                ? '\$${masCaroPrecio!.toStringAsFixed(2)}'
                : null,
            gradient: const [Color(0xFFE65100), Color(0xFFFFA726)],
          ),
        ),
      ],
    );
  }
}

class _StatCard extends StatefulWidget {
  final IconData icon;
  final String label;
  final String value;
  final String? subtitle;
  final List<Color> gradient;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    this.subtitle,
    required this.gradient,
  });

  @override
  State<_StatCard> createState() => _StatCardState();
}

class _StatCardState extends State<_StatCard> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
        transform: Matrix4.diagonal3Values(_hovered ? 1.02 : 1.0, _hovered ? 1.02 : 1.0, 1.0),
        transformAlignment: Alignment.center,
        padding: const EdgeInsets.all(22),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(18),
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              widget.gradient[0].withAlpha(50),
              widget.gradient[1].withAlpha(25),
            ],
          ),
          border: Border.all(
            color: widget.gradient[0].withAlpha(60),
            width: 1,
          ),
          boxShadow: _hovered
              ? [
                  BoxShadow(
                    color: widget.gradient[0].withAlpha(40),
                    blurRadius: 20,
                    offset: const Offset(0, 6),
                  ),
                ]
              : [],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Icon row
            Container(
              width: 42,
              height: 42,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                gradient: LinearGradient(colors: widget.gradient),
              ),
              child: Icon(widget.icon, size: 22, color: Colors.white),
            ),
            const SizedBox(height: 16),

            // Label
            Text(
              widget.label,
              style: GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w500,
                color: Colors.white54,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 6),

            // Value
            Text(
              widget.value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: Colors.white,
              ),
            ),

            if (widget.subtitle != null) ...[
              const SizedBox(height: 4),
              Text(
                widget.subtitle!,
                style: GoogleFonts.inter(
                  fontSize: 13,
                  color: widget.gradient[1],
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

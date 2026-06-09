import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../../../core/theme.dart';

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
    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: _StatCard(
              icon: Icons.inventory_2_rounded,
              iconColor: AppTheme.primary,
              label: 'Total Productos',
              value: '$totalProductos',
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: _StatCard(
              icon: Icons.trending_up_rounded,
              iconColor: AppTheme.success,
              label: 'Mayor Stock',
              value: mayorStockNombre ?? '—',
              subtitle: mayorStockValor != null ? '$mayorStockValor unidades' : null,
              subtitleColor: AppTheme.success,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: _StatCard(
              icon: Icons.attach_money_rounded,
              iconColor: AppTheme.warning,
              label: 'Más Caro',
              value: masCaroNombre ?? '—',
              subtitle: masCaroPrecio != null
                  ? '\$${masCaroPrecio!.toStringAsFixed(2)}'
                  : null,
              subtitleColor: AppTheme.warning,
            ),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatefulWidget {
  final IconData icon;
  final Color iconColor;
  final String label;
  final String value;
  final String? subtitle;
  final Color? subtitleColor;

  const _StatCard({
    required this.icon,
    required this.iconColor,
    required this.label,
    required this.value,
    this.subtitle,
    this.subtitleColor,
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
        duration: const Duration(milliseconds: 200),
        curve: Curves.easeOut,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: AppTheme.surface,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: AppTheme.border.withAlpha(_hovered ? 255 : 153),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withAlpha(_hovered ? 46 : 25),
              blurRadius: 12,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Icon container ──────────────────────────────
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                color: widget.iconColor.withAlpha(38),
              ),
              child: Icon(widget.icon, size: 22, color: widget.iconColor),
            ),
            const SizedBox(height: 12),

            // ── Label ───────────────────────────────────────
            Text(
              widget.label,
              style: GoogleFonts.inter(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: AppTheme.textSecondary,
                letterSpacing: 0.4,
              ),
            ),
            const SizedBox(height: 6),

            // ── Value ───────────────────────────────────────
            Text(
              widget.value,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
            ),

            // ── Subtitle ────────────────────────────────────
            if (widget.subtitle != null) ...[
              const SizedBox(height: 4),
              Text(
                widget.subtitle!,
                style: GoogleFonts.inter(
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                  color: widget.subtitleColor ?? AppTheme.textSecondary,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

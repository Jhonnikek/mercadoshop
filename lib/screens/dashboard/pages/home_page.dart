import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme.dart';
import '../../../providers/producto_provider.dart';
import '../widgets/stats_cards.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ProductoProvider>().fetchProductos();
    });
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ProductoProvider>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Page header ─────────────────────────────────
          Text(
            'Dashboard',
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Resumen de tu tienda',
            style: GoogleFonts.inter(
              fontSize: 13,
              color: AppTheme.textSecondary,
            ),
          ),
          const SizedBox(height: 24),

          // ── Stats cards ─────────────────────────────────
          StatsCards(
            totalProductos: provider.totalProductos,
            mayorStockNombre: provider.productoMayorStock?.nombre,
            mayorStockValor: provider.productoMayorStock?.stock,
            masCaroNombre: provider.productoMasCaro?.nombre,
            masCaroPrecio: provider.productoMasCaro?.precio,
          ),
          const SizedBox(height: 32),

          // ── Section title ───────────────────────────────
          Row(
            children: [
              Text(
                'Últimos productos',
                style: GoogleFonts.inter(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary,
                ),
              ),
              const SizedBox(width: 12),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.surfaceLight,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: AppTheme.border),
                ),
                child: Text(
                  '${provider.ultimosCinco.length}',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textSecondary,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // ── Recent list ─────────────────────────────────
          _buildRecentList(provider),
        ],
      ),
    );
  }

  Widget _headerText(String text) {
    return Text(
      text,
      style: GoogleFonts.inter(
        fontSize: 12,
        fontWeight: FontWeight.w600,
        color: AppTheme.textSecondary,
        letterSpacing: 0.5,
      ),
    );
  }

  Widget _buildRecentList(ProductoProvider provider) {
    if (provider.status == ProductoStatus.loading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(40),
          child: CircularProgressIndicator(color: AppTheme.primary),
        ),
      );
    }

    if (provider.status == ProductoStatus.error) {
      return _EmptyOrError(
        icon: Icons.error_outline_rounded,
        message: provider.errorMessage,
        action: OutlinedButton.icon(
          onPressed: () => provider.loadProductos(),
          icon: const Icon(Icons.refresh_rounded, size: 16),
          label: const Text('Reintentar'),
          style: OutlinedButton.styleFrom(
            foregroundColor: AppTheme.primary,
            side: const BorderSide(color: AppTheme.primary),
            shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10)),
          ),
        ),
      );
    }

    final items = provider.ultimosCinco;
    if (items.isEmpty) {
      return const _EmptyOrError(
        icon: Icons.inventory_2_outlined,
        message: 'Sin productos aún',
      );
    }

    return Container(
      constraints: const BoxConstraints(minHeight: 350),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: AppTheme.surface,
        border: Border.all(color: AppTheme.border),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Container(
              height: 48,
              padding: const EdgeInsets.symmetric(horizontal: 16),
              decoration: const BoxDecoration(
                color: AppTheme.surfaceLight,
                border: Border(
                  bottom: BorderSide(color: AppTheme.border, width: 0.5),
                ),
              ),
              child: Row(
                children: [
                  Expanded(flex: 3, child: _headerText('NOMBRE')),
                  Expanded(flex: 2, child: _headerText('PRECIO')),
                  Expanded(flex: 1, child: _headerText('STOCK')),
                  Expanded(flex: 4, child: _headerText('DESCRIPCIÓN')),
                ],
              ),
            ),
            // Rows
            ...items.map((p) {
              final isLast = p == items.last;
              return Container(
                height: 52,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                decoration: BoxDecoration(
                  border: isLast
                      ? null
                      : const Border(
                          bottom: BorderSide(
                              color: AppTheme.border, width: 0.5)),
                ),
                child: Row(
                  children: [
                    Expanded(
                      flex: 3,
                      child: Text(
                        p.nombre,
                        style: GoogleFonts.inter(
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          color: AppTheme.textPrimary,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ),
                    Expanded(
                      flex: 2,
                      child: Text(
                        '\$${p.precio.toStringAsFixed(2)}',
                        style: GoogleFonts.inter(
                            fontSize: 14, color: AppTheme.textPrimary),
                      ),
                    ),
                    Expanded(
                      flex: 1,
                      child: Text(
                        '${p.stock}',
                        style: GoogleFonts.inter(
                            fontSize: 14, color: AppTheme.textPrimary),
                      ),
                    ),
                    Expanded(
                      flex: 4,
                      child: Text(
                        p.descripcion.isNotEmpty ? p.descripcion : '—',
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                        style: GoogleFonts.inter(
                            fontSize: 14, color: AppTheme.textSecondary),
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}

// ── Empty / error state ──────────────────────────────────────
class _EmptyOrError extends StatelessWidget {
  final IconData icon;
  final String message;
  final Widget? action;

  const _EmptyOrError({
    required this.icon,
    required this.message,
    this.action,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 56),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: AppTheme.surface,
        border: Border.all(color: AppTheme.border),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 56,
            height: 56,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(14),
              color: AppTheme.surfaceLight,
            ),
            child: Icon(icon, size: 28, color: AppTheme.textSecondary),
          ),
          const SizedBox(height: 16),
          Text(
            message,
            style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppTheme.textSecondary,
            ),
          ),
          if (action != null) ...[
            const SizedBox(height: 16),
            action!,
          ],
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../providers/producto_provider.dart';
import '../widgets/stats_cards.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ProductoProvider>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ─────────────────────────────────────────
          Text(
            'Dashboard',
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Resumen de tu tienda',
            style: GoogleFonts.inter(fontSize: 14, color: Colors.white54),
          ),
          const SizedBox(height: 28),

          // ── Stats cards ────────────────────────────────────
          StatsCards(
            totalProductos: provider.totalProductos,
            mayorStockNombre: provider.productoMayorStock?.nombre,
            mayorStockValor: provider.productoMayorStock?.stock,
            masCaroNombre: provider.productoMasCaro?.nombre,
            masCaroPrecio: provider.productoMasCaro?.precio,
          ),
          const SizedBox(height: 36),

          // ── Recent products ────────────────────────────────
          Text(
            'Últimos productos',
            style: GoogleFonts.inter(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 16),
          _buildRecentList(context, provider),
        ],
      ),
    );
  }

  Widget _buildRecentList(BuildContext context, ProductoProvider provider) {
    if (provider.status == ProductoStatus.loading) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(40),
          child: CircularProgressIndicator(),
        ),
      );
    }

    if (provider.status == ProductoStatus.error) {
      return _EmptyOrError(
        icon: Icons.error_outline_rounded,
        message: provider.errorMessage,
        action: TextButton.icon(
          onPressed: () => provider.loadProductos(),
          icon: const Icon(Icons.refresh_rounded),
          label: const Text('Reintentar'),
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
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        color: const Color(0xFF1E1E34),
        border: Border.all(color: const Color(0xFF2A2A45)),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: DataTable(
          columnSpacing: 24,
          horizontalMargin: 20,
          headingRowHeight: 48,
          dataRowMinHeight: 50,
          dataRowMaxHeight: 50,
          columns: const [
            DataColumn(label: Text('Nombre')),
            DataColumn(label: Text('Precio'), numeric: true),
            DataColumn(label: Text('Stock'), numeric: true),
            DataColumn(label: Text('Descripción')),
          ],
          rows: items.map((p) {
            return DataRow(cells: [
              DataCell(Text(
                p.nombre,
                style: GoogleFonts.inter(fontWeight: FontWeight.w500),
              )),
              DataCell(Text('\$${p.precio.toStringAsFixed(2)}')),
              DataCell(Text('${p.stock}')),
              DataCell(Text(
                p.descripcion.isNotEmpty ? p.descripcion : '—',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              )),
            ]);
          }).toList(),
        ),
      ),
    );
  }
}

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
      padding: const EdgeInsets.symmetric(vertical: 50),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(14),
        color: const Color(0xFF1E1E34),
        border: Border.all(color: const Color(0xFF2A2A45)),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 48, color: Colors.white30),
          const SizedBox(height: 14),
          Text(
            message,
            style: GoogleFonts.inter(color: Colors.white54, fontSize: 14),
          ),
          if (action != null) ...[
            const SizedBox(height: 12),
            action!,
          ],
        ],
      ),
    );
  }
}

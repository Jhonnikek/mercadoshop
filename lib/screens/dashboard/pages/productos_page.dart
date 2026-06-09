import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import '../../../core/theme.dart';
import '../../../models/producto.dart';
import '../../../providers/producto_provider.dart';
import '../widgets/producto_dialog.dart';

class ProductosPage extends StatefulWidget {
  const ProductosPage({super.key});

  @override
  State<ProductosPage> createState() => _ProductosPageState();
}

class _ProductosPageState extends State<ProductosPage> {
  final _searchCtrl = TextEditingController();
  int _currentPage = 0;
  static const _rowsPerPage = 10;

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ProductoProvider>();
    final productos = provider.productos;
    final totalPages = (productos.length / _rowsPerPage).ceil();

    // Clamp current page
    if (_currentPage >= totalPages && totalPages > 0) {
      _currentPage = totalPages - 1;
    }
    if (_currentPage < 0) _currentPage = 0;

    final startIdx = _currentPage * _rowsPerPage;
    final endIdx = (startIdx + _rowsPerPage).clamp(0, productos.length);
    final pageItems =
        productos.isNotEmpty ? productos.sublist(startIdx, endIdx) : <Producto>[];

    return Padding(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ───────────────────────────────────────
          Text(
            'Productos',
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Gestiona tu inventario',
            style: GoogleFonts.inter(
              fontSize: 13,
              color: AppTheme.textSecondary,
            ),
          ),
          const SizedBox(height: 24),

          // ── Toolbar ──────────────────────────────────────
          Row(
            children: [
              // Search
              SizedBox(
                width: 300,
                height: 44,
                child: TextField(
                  controller: _searchCtrl,
                  onChanged: (v) {
                    provider.setSearch(v);
                    setState(() => _currentPage = 0);
                  },
                  style: GoogleFonts.inter(
                      fontSize: 14, color: AppTheme.textPrimary),
                  decoration: InputDecoration(
                    hintText: 'Buscar por nombre...',
                    prefixIcon:
                        const Icon(Icons.search_rounded, size: 18),
                    suffixIcon: _searchCtrl.text.isNotEmpty
                        ? IconButton(
                            icon:
                                const Icon(Icons.close_rounded, size: 16),
                            onPressed: () {
                              _searchCtrl.clear();
                              provider.setSearch('');
                              setState(() => _currentPage = 0);
                            },
                          )
                        : null,
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 16, vertical: 0),
                    filled: true,
                    fillColor: AppTheme.surfaceLight,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: const BorderSide(color: AppTheme.border),
                    ),
                    enabledBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: const BorderSide(color: AppTheme.border),
                    ),
                    focusedBorder: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: const BorderSide(
                          color: AppTheme.primary, width: 1.5),
                    ),
                  ),
                ),
              ),
              const Spacer(),
              // New product button
              ElevatedButton.icon(
                onPressed: () => _openDialog(context),
                icon: const Icon(Icons.add_rounded, size: 18),
                label: Text(
                  'Nuevo Producto',
                  style: GoogleFonts.inter(
                      fontSize: 14, fontWeight: FontWeight.w600),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primary,
                  foregroundColor: AppTheme.textPrimary,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  minimumSize: const Size(0, 44),
                  elevation: 0,
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // ── Table ─────────────────────────────────────────
          Expanded(child: _buildBody(provider, pageItems)),

          // ── Pagination ────────────────────────────────────
          if (totalPages > 1) ...[
            const SizedBox(height: 16),
            _buildPagination(totalPages),
          ],
        ],
      ),
    );
  }

  Widget _buildBody(ProductoProvider provider, List<Producto> pageItems) {
    if (provider.status == ProductoStatus.loading) {
      return const Center(
        child: CircularProgressIndicator(color: AppTheme.primary),
      );
    }

    if (provider.status == ProductoStatus.error) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded,
                size: 48, color: AppTheme.textSecondary),
            const SizedBox(height: 16),
            Text(
              provider.errorMessage,
              style: GoogleFonts.inter(
                  fontSize: 14, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            OutlinedButton.icon(
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
          ],
        ),
      );
    }

    if (provider.allProductos.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(16),
                color: AppTheme.surfaceLight,
              ),
              child: const Icon(Icons.inventory_2_outlined,
                  size: 32, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            Text(
              'Sin productos aún',
              style: GoogleFonts.inter(
                fontSize: 16,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Crea tu primer producto para comenzar',
              style: GoogleFonts.inter(
                  fontSize: 13, color: AppTheme.textSecondary),
            ),
          ],
        ),
      );
    }

    if (pageItems.isEmpty) {
      return Center(
        child: Text(
          'Sin resultados para "${provider.searchQuery}"',
          style: GoogleFonts.inter(
              fontSize: 14, color: AppTheme.textSecondary),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(12),
        color: AppTheme.surface,
        border: Border.all(color: AppTheme.border),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: SingleChildScrollView(
          child: SizedBox(
            width: double.infinity,
            child: DataTable(
              columnSpacing: 24,
              horizontalMargin: 16,
              headingRowHeight: 48,
              dataRowMinHeight: 52,
              dataRowMaxHeight: 52,
              headingRowColor: WidgetStateProperty.all(AppTheme.surfaceLight),
              dividerThickness: 0.5,
              columns: [
                DataColumn(
                  label: Text(
                    'NOMBRE',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                DataColumn(
                  numeric: true,
                  label: Text(
                    'PRECIO',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                DataColumn(
                  numeric: true,
                  label: Text(
                    'STOCK',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'DESCRIPCIÓN',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                DataColumn(
                  label: Text(
                    'ACCIONES',
                    style: GoogleFonts.inter(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textSecondary,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
              ],
              rows: pageItems.map((p) => _buildRow(p, provider)).toList(),
            ),
          ),
        ),
      ),
    );
  }

  DataRow _buildRow(Producto p, ProductoProvider provider) {
    // Stock color indicator
    final stockColor = p.stock > 10
        ? AppTheme.success
        : p.stock > 0
            ? AppTheme.warning
            : AppTheme.danger;

    return DataRow(
      cells: [
        DataCell(Text(
          p.nombre,
          style: GoogleFonts.inter(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: AppTheme.textPrimary),
        )),
        DataCell(Text(
          '\$${p.precio.toStringAsFixed(2)}',
          style: GoogleFonts.inter(
              fontSize: 14, color: AppTheme.textPrimary),
        )),
        DataCell(
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 7,
                height: 7,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: stockColor,
                ),
              ),
              const SizedBox(width: 8),
              Text(
                '${p.stock}',
                style: GoogleFonts.inter(
                    fontSize: 14, color: AppTheme.textPrimary),
              ),
            ],
          ),
        ),
        DataCell(Text(
          p.descripcion.isNotEmpty ? p.descripcion : '—',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: GoogleFonts.inter(
              fontSize: 14, color: AppTheme.textSecondary),
        )),
        DataCell(
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _ActionIcon(
                icon: Icons.edit_rounded,
                color: AppTheme.primary,
                tooltip: 'Editar',
                onTap: () => _openDialog(context, producto: p),
              ),
              const SizedBox(width: 4),
              _ActionIcon(
                icon: Icons.delete_rounded,
                color: AppTheme.danger,
                tooltip: 'Eliminar',
                onTap: () => _confirmDelete(context, provider, p),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPagination(int totalPages) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed:
              _currentPage > 0 ? () => setState(() => _currentPage--) : null,
          icon: const Icon(Icons.chevron_left_rounded,
              color: AppTheme.textSecondary),
          splashRadius: 18,
        ),
        for (int i = 0; i < totalPages; i++)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: InkWell(
              borderRadius: BorderRadius.circular(8),
              onTap: () => setState(() => _currentPage = i),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 180),
                width: 32,
                height: 32,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: _currentPage == i
                      ? AppTheme.primary
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                  border: _currentPage == i
                      ? null
                      : Border.all(color: AppTheme.border.withAlpha(0)),
                ),
                child: Text(
                  '${i + 1}',
                  style: GoogleFonts.inter(
                    fontSize: 13,
                    fontWeight: _currentPage == i
                        ? FontWeight.w700
                        : FontWeight.w400,
                    color: _currentPage == i
                        ? AppTheme.textPrimary
                        : AppTheme.textSecondary,
                  ),
                ),
              ),
            ),
          ),
        IconButton(
          onPressed: _currentPage < totalPages - 1
              ? () => setState(() => _currentPage++)
              : null,
          icon: const Icon(Icons.chevron_right_rounded,
              color: AppTheme.textSecondary),
          splashRadius: 18,
        ),
      ],
    );
  }

  void _openDialog(BuildContext context, {Producto? producto}) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => ProductoDialog(producto: producto),
    );
  }

  void _confirmDelete(
    BuildContext context,
    ProductoProvider provider,
    Producto p,
  ) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surface,
        shape:
            RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                color: AppTheme.danger.withAlpha(38),
              ),
              child: const Icon(
                Icons.warning_rounded,
                color: AppTheme.danger,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              'Confirmar eliminación',
              style: GoogleFonts.inter(
                fontSize: 20,
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
              ),
            ),
          ],
        ),
        content: RichText(
          text: TextSpan(
            style: GoogleFonts.inter(
                fontSize: 14, color: AppTheme.textSecondary),
            children: [
              const TextSpan(text: '¿Estás seguro de eliminar '),
              TextSpan(
                text: p.nombre,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary,
                ),
              ),
              const TextSpan(text: '? Esta acción no se puede deshacer.'),
            ],
          ),
        ),
        actionsPadding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
        actions: [
          // Ghost cancel
          OutlinedButton(
            onPressed: () => Navigator.pop(ctx),
            style: OutlinedButton.styleFrom(
              foregroundColor: AppTheme.textSecondary,
              side: const BorderSide(color: AppTheme.border),
              padding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
            child: Text(
              'Cancelar',
              style: GoogleFonts.inter(
                  fontSize: 14, fontWeight: FontWeight.w500),
            ),
          ),
          const SizedBox(width: 8),
          // Danger delete
          ElevatedButton.icon(
            onPressed: () async {
              final ok = await provider.deleteProducto(p.id!);
              if (context.mounted) Navigator.of(ctx).pop();
              if (context.mounted && !ok) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    backgroundColor: AppTheme.danger.withAlpha(38),
                    content: Row(
                      children: [
                        const Icon(Icons.error_outline_rounded,
                            color: AppTheme.danger, size: 18),
                        const SizedBox(width: 10),
                        Text(
                          'Error al eliminar producto',
                          style: GoogleFonts.inter(
                              fontSize: 14, color: AppTheme.danger),
                        ),
                      ],
                    ),
                  ),
                );
              }
            },
            icon: const Icon(Icons.delete_rounded, size: 16),
            label: Text(
              'Eliminar',
              style: GoogleFonts.inter(
                  fontSize: 14, fontWeight: FontWeight.w600),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.danger.withAlpha(38),
              foregroundColor: AppTheme.danger,
              padding:
                  const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
              elevation: 0,
            ),
          ),
        ],
      ),
    );
  }
}

// ── Small action icon button ────────────────────────────────
class _ActionIcon extends StatefulWidget {
  final IconData icon;
  final Color color;
  final String tooltip;
  final VoidCallback onTap;

  const _ActionIcon({
    required this.icon,
    required this.color,
    required this.tooltip,
    required this.onTap,
  });

  @override
  State<_ActionIcon> createState() => _ActionIconState();
}

class _ActionIconState extends State<_ActionIcon> {
  bool _hovered = false;

  @override
  Widget build(BuildContext context) {
    return MouseRegion(
      onEnter: (_) => setState(() => _hovered = true),
      onExit: (_) => setState(() => _hovered = false),
      child: Tooltip(
        message: widget.tooltip,
        child: InkWell(
          borderRadius: BorderRadius.circular(8),
          onTap: widget.onTap,
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 160),
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: _hovered
                  ? widget.color.withAlpha(38)
                  : Colors.transparent,
            ),
            child: Icon(
              widget.icon,
              size: 17,
              color: _hovered ? widget.color : AppTheme.textSecondary,
            ),
          ),
        ),
      ),
    );
  }
}

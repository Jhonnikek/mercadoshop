import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
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
    final cs = Theme.of(context).colorScheme;
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
      padding: const EdgeInsets.all(28),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Header ─────────────────────────────────────────
          Text(
            'Productos',
            style: GoogleFonts.inter(
              fontSize: 28,
              fontWeight: FontWeight.w800,
              color: Colors.white,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'Gestiona tu inventario',
            style: GoogleFonts.inter(fontSize: 14, color: Colors.white54),
          ),
          const SizedBox(height: 24),

          // ── Search + Create ────────────────────────────────
          Row(
            children: [
              // Search field
              SizedBox(
                width: 320,
                height: 44,
                child: TextField(
                  controller: _searchCtrl,
                  onChanged: (v) {
                    provider.setSearch(v);
                    setState(() => _currentPage = 0);
                  },
                  style: GoogleFonts.inter(fontSize: 14),
                  decoration: InputDecoration(
                    hintText: 'Buscar por nombre...',
                    prefixIcon:
                        const Icon(Icons.search_rounded, size: 20),
                    suffixIcon: _searchCtrl.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.close_rounded, size: 18),
                            onPressed: () {
                              _searchCtrl.clear();
                              provider.setSearch('');
                              setState(() => _currentPage = 0);
                            },
                          )
                        : null,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 0,
                    ),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(10),
                      borderSide: BorderSide.none,
                    ),
                    filled: true,
                    fillColor: const Color(0xFF252540),
                  ),
                ),
              ),
              const Spacer(),
              SizedBox(
                height: 44,
                child: ElevatedButton.icon(
                  onPressed: () => _openDialog(context, provider),
                  icon: const Icon(Icons.add_rounded, size: 20),
                  label: Text(
                    'Nuevo Producto',
                    style: GoogleFonts.inter(fontWeight: FontWeight.w600),
                  ),
                  style: ElevatedButton.styleFrom(
                    minimumSize: Size.zero,
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // ── Table ──────────────────────────────────────────
          Expanded(child: _buildBody(provider, pageItems, cs)),

          // ── Pagination ─────────────────────────────────────
          if (totalPages > 1) ...[
            const SizedBox(height: 12),
            _buildPagination(totalPages, cs),
          ],
        ],
      ),
    );
  }

  Widget _buildBody(
    ProductoProvider provider,
    List<Producto> pageItems,
    ColorScheme cs,
  ) {
    if (provider.status == ProductoStatus.loading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (provider.status == ProductoStatus.error) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded,
                size: 48, color: Colors.white30),
            const SizedBox(height: 14),
            Text(
              provider.errorMessage,
              style: GoogleFonts.inter(color: Colors.white54),
            ),
            const SizedBox(height: 12),
            TextButton.icon(
              onPressed: () => provider.loadProductos(),
              icon: const Icon(Icons.refresh_rounded),
              label: const Text('Reintentar'),
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
            const Icon(Icons.inventory_2_outlined,
                size: 56, color: Colors.white24),
            const SizedBox(height: 14),
            Text(
              'Sin productos aún',
              style: GoogleFonts.inter(
                fontSize: 16,
                color: Colors.white54,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              'Crea tu primer producto para comenzar',
              style: GoogleFonts.inter(fontSize: 13, color: Colors.white38),
            ),
          ],
        ),
      );
    }

    if (pageItems.isEmpty) {
      return Center(
        child: Text(
          'Sin resultados para "${provider.searchQuery}"',
          style: GoogleFonts.inter(color: Colors.white54),
        ),
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
        child: SingleChildScrollView(
          child: SizedBox(
            width: double.infinity,
            child: DataTable(
              columnSpacing: 24,
              horizontalMargin: 20,
              headingRowHeight: 48,
              dataRowMinHeight: 52,
              dataRowMaxHeight: 52,
              columns: const [
                DataColumn(label: Text('Nombre')),
                DataColumn(label: Text('Precio'), numeric: true),
                DataColumn(label: Text('Stock'), numeric: true),
                DataColumn(label: Text('Descripción')),
                DataColumn(label: Text('Acciones')),
              ],
              rows: pageItems.map((p) => _buildRow(p, provider)).toList(),
            ),
          ),
        ),
      ),
    );
  }

  DataRow _buildRow(Producto p, ProductoProvider provider) {
    return DataRow(
      cells: [
        DataCell(Text(
          p.nombre,
          style: GoogleFonts.inter(fontWeight: FontWeight.w500),
        )),
        DataCell(Text('\$${p.precio.toStringAsFixed(2)}')),
        DataCell(
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: p.stock > 10
                      ? const Color(0xFF66BB6A)
                      : p.stock > 0
                          ? const Color(0xFFFFA726)
                          : const Color(0xFFEF5350),
                ),
              ),
              const SizedBox(width: 8),
              Text('${p.stock}'),
            ],
          ),
        ),
        DataCell(Text(
          p.descripcion.isNotEmpty ? p.descripcion : '—',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        )),
        DataCell(
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _ActionIcon(
                icon: Icons.edit_rounded,
                color: const Color(0xFF5C6BC0),
                tooltip: 'Editar',
                onTap: () => _openDialog(context, provider, producto: p),
              ),
              const SizedBox(width: 4),
              _ActionIcon(
                icon: Icons.delete_rounded,
                color: const Color(0xFFEF5350),
                tooltip: 'Eliminar',
                onTap: () => _confirmDelete(context, provider, p),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildPagination(int totalPages, ColorScheme cs) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        IconButton(
          onPressed:
              _currentPage > 0 ? () => setState(() => _currentPage--) : null,
          icon: const Icon(Icons.chevron_left_rounded),
          splashRadius: 18,
        ),
        for (int i = 0; i < totalPages; i++)
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 2),
            child: InkWell(
              borderRadius: BorderRadius.circular(8),
              onTap: () => setState(() => _currentPage = i),
              child: AnimatedContainer(
                duration: const Duration(milliseconds: 200),
                width: 34,
                height: 34,
                alignment: Alignment.center,
                decoration: BoxDecoration(
                  color: _currentPage == i
                      ? cs.primary
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  '${i + 1}',
                  style: GoogleFonts.inter(
                    fontWeight: _currentPage == i
                        ? FontWeight.w700
                        : FontWeight.w400,
                    color: Colors.white,
                    fontSize: 13,
                  ),
                ),
              ),
            ),
          ),
        IconButton(
          onPressed: _currentPage < totalPages - 1
              ? () => setState(() => _currentPage++)
              : null,
          icon: const Icon(Icons.chevron_right_rounded),
          splashRadius: 18,
        ),
      ],
    );
  }

  void _openDialog(
    BuildContext context,
    ProductoProvider provider, {
    Producto? producto,
  }) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => ProductoDialog(
        producto: producto,
        onSave: (p) async {
          if (producto != null && producto.id != null) {
            return provider.updateProducto(producto.id!, p);
          } else {
            return provider.createProducto(p);
          }
        },
      ),
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
        backgroundColor: const Color(0xFF1E1E34),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Container(
              width: 38,
              height: 38,
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(10),
                color: const Color(0xFFEF5350).withAlpha(40),
              ),
              child: const Icon(
                Icons.warning_rounded,
                color: Color(0xFFEF5350),
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            const Text('Confirmar eliminación'),
          ],
        ),
        content: RichText(
          text: TextSpan(
            style: GoogleFonts.inter(color: Colors.white70, fontSize: 14),
            children: [
              const TextSpan(text: '¿Estás seguro de eliminar '),
              TextSpan(
                text: p.nombre,
                style: const TextStyle(
                  fontWeight: FontWeight.w700,
                  color: Colors.white,
                ),
              ),
              const TextSpan(text: '? Esta acción no se puede deshacer.'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(
              'Cancelar',
              style: GoogleFonts.inter(color: Colors.white54),
            ),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final ok = await provider.deleteProducto(p.id!);
              if (context.mounted && !ok) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Error al eliminar producto'),
                    backgroundColor: Color(0xFFEF5350),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF5350),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
            child: Text(
              'Eliminar',
              style: GoogleFonts.inter(fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Small action icon button ──────────────────────────────
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
            duration: const Duration(milliseconds: 180),
            width: 34,
            height: 34,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(8),
              color: _hovered ? widget.color.withAlpha(30) : Colors.transparent,
            ),
            child: Icon(
              widget.icon,
              size: 18,
              color: _hovered ? widget.color : Colors.white54,
            ),
          ),
        ),
      ),
    );
  }
}

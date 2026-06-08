import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_lucide/flutter_lucide.dart';
import 'package:mercadoshop_app/core/theme/app_theme.dart';
import 'package:mercadoshop_app/domain/entities/producto.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/empty_state.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/error_state.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/producto_card.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/producto_skeleton.dart';
import 'package:mercadoshop_app/presentation/providers/cart_provider.dart';
import 'package:mercadoshop_app/presentation/providers/producto_provider.dart';

class HomePage extends ConsumerStatefulWidget {
  const HomePage({super.key});

  @override
  ConsumerState<HomePage> createState() => _HomePageState();
}

class _HomePageState extends ConsumerState<HomePage> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  double? _precioMin;
  double? _precioMax;
  String? _stockFilter; // null, 'instock'(>5), 'outofstock'(==0), 'lowstock'(<=5)
  String _sortBy = 'nombreAsc'; // 'precioAsc', 'precioDesc', 'nombreAsc', 'nombreDesc'

  bool get _hasActiveFilters =>
      _precioMin != null ||
      _precioMax != null ||
      _stockFilter != null ||
      _sortBy != 'nombreAsc';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  List<Producto> _filtrarYOrdenar(List<Producto> productos) {
    var result = productos.where((p) {
      if (_searchQuery.isNotEmpty) {
        if (!p.nombre.toLowerCase().contains(_searchQuery) &&
            !(p.descripcion?.toLowerCase().contains(_searchQuery) ?? false) &&
            !p.tiendaNombre.toLowerCase().contains(_searchQuery)) {
          return false;
        }
      }
      if (_precioMin != null && p.precio < _precioMin!) return false;
      if (_precioMax != null && p.precio > _precioMax!) return false;
      if (_stockFilter == 'instock' && !(p.stock > 5)) return false;
      if (_stockFilter == 'outofstock' && !(p.stock == 0)) return false;
      if (_stockFilter == 'lowstock' && !(p.stock <= 5)) return false;
      return true;
    }).toList();

    switch (_sortBy) {
      case 'precioAsc':
        result.sort((a, b) => a.precio.compareTo(b.precio));
      case 'precioDesc':
        result.sort((a, b) => b.precio.compareTo(a.precio));
      case 'nombreDesc':
        result.sort((a, b) => b.nombre.compareTo(a.nombre));
      default:
        result.sort((a, b) => a.nombre.compareTo(b.nombre));
    }
    return result;
  }

  void _limpiarFiltros() {
    setState(() {
      _precioMin = null;
      _precioMax = null;
      _stockFilter = null;
      _sortBy = 'nombreAsc';
    });
  }

  Future<void> _showRangoPrecioDialog() async {
    final minController = TextEditingController(
      text: _precioMin?.toStringAsFixed(0) ?? '',
    );
    final maxController = TextEditingController(
      text: _precioMax?.toStringAsFixed(0) ?? '',
    );
    final result = await showDialog<List<double?>?>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Rango de precios'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: minController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'Mínimo',
                prefixText: '\$ ',
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: maxController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(
                hintText: 'Máximo',
                prefixText: '\$ ',
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancelar'),
          ),
          TextButton(
            onPressed: () {
              final min = double.tryParse(minController.text);
              final max = double.tryParse(maxController.text);
              WidgetsBinding.instance.addPostFrameCallback((_) {
                if (ctx.mounted) {
                  if (min != null || max != null) {
                    Navigator.of(ctx).pop([min, max]);
                  } else {
                    Navigator.of(ctx).pop();
                  }
                }
              });
            },
            child: const Text('Aplicar'),
          ),
        ],
      ),
    );
    if (result != null) {
      setState(() {
        _precioMin = result[0];
        _precioMax = result[1];
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final productosAsync = ref.watch(productosProvider);
    final theme = Theme.of(context);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'MercadoShop',
              style: theme.textTheme.headlineMedium?.copyWith(
                fontSize: 24,
                color: AppColors.primaryDark,
              ),
            )
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(LucideIcons.refresh_cw, size: 20),
            onPressed: () => ref.read(productosProvider.notifier).refrescar(),
            tooltip: 'Actualizar productos',
          ),
          const SizedBox(width: 8),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
            child: TextField(
              controller: _searchController,
              onChanged: (value) {
                setState(() {
                  _searchQuery = value.trim().toLowerCase();
                });
              },
              decoration: InputDecoration(
                hintText: 'Buscar productos por nombre...',
                prefixIcon: const Icon(LucideIcons.search, size: 20, color: AppColors.textSecondary),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(LucideIcons.x, size: 18),
                        onPressed: () {
                          _searchController.clear();
                          setState(() {
                            _searchQuery = '';
                          });
                        },
                      )
                    : null,
              ),
            ),
          ),
          _buildFilterBar(),
          Expanded(
            child: RefreshIndicator(
              onRefresh: () => ref.read(productosProvider.notifier).refrescar(),
              color: AppColors.primary,
              backgroundColor: AppColors.surface,
              child: productosAsync.when(
                loading: () => const SingleChildScrollView(
                  child: ProductoSkeletonGrid(),
                ),
                error: (error, stackTrace) => SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Container(
                    height: MediaQuery.of(context).size.height * 0.6,
                    alignment: Alignment.center,
                    child: ErrorState(
                      mensaje: error.toString(),
                      onRetry: () => ref.read(productosProvider.notifier).refrescar(),
                    ),
                  ),
                ),
                data: (productos) {
                  final filtrados = _filtrarYOrdenar(productos);

                  if (filtrados.isEmpty) {
                    return SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      child: Container(
                        height: MediaQuery.of(context).size.height * 0.6,
                        alignment: Alignment.center,
                        child: EmptyState(
                          onRetry: () => ref.read(productosProvider.notifier).refrescar(),
                        ),
                      ),
                    );
                  }

                  return GridView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 14,
                      mainAxisSpacing: 14,
                      childAspectRatio: 0.63,
                    ),
                    itemCount: filtrados.length,
                    itemBuilder: (context, index) {
                      final producto = filtrados[index];
                      return ProductoCard(
                        producto: producto,
                        onTap: () {
                          _showProductoDetail(context, producto);
                        },
                      );
                    },
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFilterBar() {
    final stockLabel = _stockFilter == null
        ? 'Disponibilidad'
        : _stockFilter == 'instock'
            ? 'En stock'
            : _stockFilter == 'outofstock'
                ? 'Agotados'
                : 'Stock bajo';

    final sortLabel = _sortBy == 'precioAsc'
        ? 'Precio ↑'
        : _sortBy == 'precioDesc'
            ? 'Precio ↓'
            : _sortBy == 'nombreDesc'
                ? 'Z-A'
                : 'A-Z';

    return Container(
      height: 48,
      margin: const EdgeInsets.only(top: 12),
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        children: [
          FilterChip(
            label: Text(
              _precioMin != null || _precioMax != null
                  ? 'Precio (${_precioMin != null ? '\$${_precioMin!.toStringAsFixed(0)}' : '0'} - ${_precioMax != null ? '\$${_precioMax!.toStringAsFixed(0)}' : '∞'})'
                  : 'Precio',
              style: const TextStyle(fontSize: 12),
            ),
            selected: _precioMin != null || _precioMax != null,
            onSelected: (_) => _showRangoPrecioDialog(),
            avatar: Icon(
              LucideIcons.dollar_sign,
              size: 14,
              color: _precioMin != null || _precioMax != null
                  ? AppColors.primary
                  : AppColors.textTertiary,
            ),
          ),
          const SizedBox(width: 8),
          FilterChip(
            label: Text(stockLabel, style: const TextStyle(fontSize: 12)),
            selected: _stockFilter != null,
            onSelected: (_) => _showStockBottomSheet(),
            avatar: Icon(
              LucideIcons.box,
              size: 14,
              color: _stockFilter != null ? AppColors.primary : AppColors.textTertiary,
            ),
          ),
          const SizedBox(width: 8),
          FilterChip(
            label: Text(sortLabel, style: const TextStyle(fontSize: 12)),
            selected: _sortBy != 'nombreAsc',
            onSelected: (_) => _showSortBottomSheet(),
            avatar: Icon(
              LucideIcons.arrow_up_down,
              size: 14,
              color: _sortBy != 'nombreAsc' ? AppColors.primary : AppColors.textTertiary,
            ),
          ),
          if (_hasActiveFilters) ...[
            const SizedBox(width: 8),
            ActionChip(
              label: const Text('Limpiar', style: TextStyle(fontSize: 12)),
              avatar: const Icon(LucideIcons.x, size: 14),
              onPressed: _limpiarFiltros,
            ),
          ],
        ],
      ),
    );
  }

  void _showStockBottomSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.border,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Disponibilidad',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 16),
              _StockOption(
                label: 'Todos',
                icon: LucideIcons.boxes,
                selected: _stockFilter == null,
                onTap: () {
                  setState(() => _stockFilter = null);
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _StockOption(
                label: 'En stock (más de 5)',
                icon: LucideIcons.circle_check,
                selected: _stockFilter == 'instock',
                onTap: () {
                  setState(() => _stockFilter = 'instock');
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _StockOption(
                label: 'Stock bajo (5 o menos)',
                icon: LucideIcons.triangle_alert,
                selected: _stockFilter == 'lowstock',
                onTap: () {
                  setState(() => _stockFilter = 'lowstock');
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _StockOption(
                label: 'Agotados (0)',
                icon: LucideIcons.circle_x,
                selected: _stockFilter == 'outofstock',
                onTap: () {
                  setState(() => _stockFilter = 'outofstock');
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showSortBottomSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(24, 12, 24, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppColors.border,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'Ordenar por',
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
              ),
              const SizedBox(height: 16),
              _SortOption(
                label: 'Nombre A-Z',
                icon: LucideIcons.arrow_down_a_z,
                selected: _sortBy == 'nombreAsc',
                onTap: () {
                  setState(() => _sortBy = 'nombreAsc');
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _SortOption(
                label: 'Nombre Z-A',
                icon: LucideIcons.arrow_up_z_a,
                selected: _sortBy == 'nombreDesc',
                onTap: () {
                  setState(() => _sortBy = 'nombreDesc');
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _SortOption(
                label: 'Precio: menor a mayor',
                icon: LucideIcons.arrow_up_narrow_wide,
                selected: _sortBy == 'precioAsc',
                onTap: () {
                  setState(() => _sortBy = 'precioAsc');
                  Navigator.pop(ctx);
                },
              ),
              const SizedBox(height: 8),
              _SortOption(
                label: 'Precio: mayor a menor',
                icon: LucideIcons.arrow_down_wide_narrow,
                selected: _sortBy == 'precioDesc',
                onTap: () {
                  setState(() => _sortBy = 'precioDesc');
                  Navigator.pop(ctx);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showProductoDetail(BuildContext context, dynamic producto) {
    final theme = Theme.of(context);
    int cantidad = 1;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (ctx) {
        final stockLimit = producto.stock > 0 ? producto.stock : 1;
        return StatefulBuilder(
          builder: (ctx, setSheetState) => Container(
            decoration: const BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.vertical(top: Radius.circular(28)),
            ),
            padding: EdgeInsets.fromLTRB(
              24,
              20,
              24,
              20 + MediaQuery.of(context).padding.bottom,
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AppColors.border,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            producto.nombre,
                            style: theme.textTheme.headlineMedium,
                          ),
                          const SizedBox(height: 6),
                          Row(
                            children: [
                              const Icon(LucideIcons.store, size: 14, color: AppColors.primary),
                              const SizedBox(width: 6),
                              Text(
                                producto.tiendaNombre,
                                style: theme.textTheme.bodyMedium?.copyWith(
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.primaryDark,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: producto.stock > 0
                            ? AppColors.success.withValues(alpha: 0.12)
                            : AppColors.error.withValues(alpha: 0.12),
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        producto.stock > 0 ? 'En Stock' : 'Agotado',
                        style: TextStyle(
                          color: producto.stock > 0 ? AppColors.success : AppColors.error,
                          fontWeight: FontWeight.w600,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  ],
                ),
                const Divider(height: 24),
                Text(
                  'Descripción',
                  style: theme.textTheme.titleMedium,
                ),
                const SizedBox(height: 8),
                ConstrainedBox(
                  constraints: const BoxConstraints(maxHeight: 120),
                  child: SingleChildScrollView(
                    child: Text(
                      producto.descripcion ?? 'Este producto no cuenta con una descripción detallada.',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        height: 1.5,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Precio unitario',
                          style: theme.textTheme.bodySmall,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '\$${producto.precio.toStringAsFixed(0)} COP',
                          style: theme.textTheme.headlineMedium?.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w800,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      decoration: BoxDecoration(
                        color: AppColors.surfaceVariant,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          InkWell(
                            onTap: cantidad > 1
                                ? () => setSheetState(() => cantidad--)
                                : null,
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.all(10),
                              child: Icon(
                                LucideIcons.minus,
                                size: 18,
                                color: cantidad > 1
                                    ? AppColors.primary
                                    : AppColors.textTertiary,
                              ),
                            ),
                          ),
                          SizedBox(
                            width: 40,
                            child: Center(
                              child: Text(
                                '$cantidad',
                                style: theme.textTheme.titleMedium?.copyWith(
                                  fontWeight: FontWeight.w700,
                                ),
                              ),
                            ),
                          ),
                          InkWell(
                            onTap: cantidad < stockLimit
                                ? () => setSheetState(() => cantidad++)
                                : null,
                            borderRadius: BorderRadius.circular(12),
                            child: Container(
                              padding: const EdgeInsets.all(10),
                              child: Icon(
                                LucideIcons.plus,
                                size: 18,
                                color: cantidad < stockLimit
                                    ? AppColors.primary
                                    : AppColors.textTertiary,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: producto.stock > 0
                        ? () {
                            Navigator.pop(context);
                            ref.read(cartProvider.notifier).agregarConCantidad(producto, cantidad);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('$cantidad x ${producto.nombre} añadido al carrito'),
                                behavior: SnackBarBehavior.floating,
                                backgroundColor: AppColors.primaryDark,
                                duration: const Duration(seconds: 2),
                              ),
                            );
                          }
                        : null,
                    icon: const Icon(LucideIcons.shopping_cart, size: 18),
                    label: Text(
                      producto.stock > 0 ? 'Añadir al carrito' : 'Agotado',
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      disabledBackgroundColor: AppColors.border,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}

class _StockOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _StockOption({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: selected ? AppColors.primary.withValues(alpha: 0.08) : AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
          border: selected ? Border.all(color: AppColors.primary, width: 1.5) : null,
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 18,
              color: selected ? AppColors.primary : AppColors.textSecondary,
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: TextStyle(
                fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                color: selected ? AppColors.primary : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SortOption extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool selected;
  final VoidCallback onTap;

  const _SortOption({
    required this.label,
    required this.icon,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: selected ? AppColors.primary.withValues(alpha: 0.08) : AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(12),
          border: selected ? Border.all(color: AppColors.primary, width: 1.5) : null,
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 18,
              color: selected ? AppColors.primary : AppColors.textSecondary,
            ),
            const SizedBox(width: 12),
            Text(
              label,
              style: TextStyle(
                fontWeight: selected ? FontWeight.w600 : FontWeight.w400,
                color: selected ? AppColors.primary : AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

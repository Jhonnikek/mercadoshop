import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_lucide/flutter_lucide.dart';
import 'package:shimmer/shimmer.dart';
import 'package:mercadoshop_app/core/theme/app_theme.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/empty_state.dart';
import 'package:mercadoshop_app/presentation/pages/home/widgets/error_state.dart';
import 'package:mercadoshop_app/presentation/pages/tienda/widgets/tienda_card.dart';
import 'package:mercadoshop_app/presentation/providers/tienda_provider.dart';

class TiendasPage extends ConsumerStatefulWidget {
  const TiendasPage({super.key});

  @override
  ConsumerState<TiendasPage> createState() => _TiendasPageState();
}

class _TiendasPageState extends ConsumerState<TiendasPage> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final tiendasAsync = ref.watch(tiendasProvider);
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
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              onChanged: (value) {
                setState(() {
                  _searchQuery = value.trim().toLowerCase();
                });
              },
              decoration: InputDecoration(
                hintText: 'Buscar tiendas por nombre o dirección...',
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
          Expanded(
            child: RefreshIndicator(
              onRefresh: () => ref.read(tiendasProvider.notifier).refrescar(),
              color: AppColors.primary,
              backgroundColor: AppColors.surface,
              child: tiendasAsync.when(
                loading: () => const _TiendaSkeletonList(),
                error: (error, _) => SingleChildScrollView(
                  physics: const AlwaysScrollableScrollPhysics(),
                  child: Container(
                    height: MediaQuery.of(context).size.height * 0.6,
                    alignment: Alignment.center,
                    child: ErrorState(
                      mensaje: error.toString(),
                      onRetry: () => ref.read(tiendasProvider.notifier).refrescar(),
                    ),
                  ),
                ),
                data: (tiendas) {
                  final filtradas = tiendas.where((tienda) {
                    return tienda.nombre.toLowerCase().contains(_searchQuery) ||
                        tienda.direccion.toLowerCase().contains(_searchQuery);
                  }).toList();

                  if (filtradas.isEmpty) {
                    return SingleChildScrollView(
                      physics: const AlwaysScrollableScrollPhysics(),
                      child: Container(
                        height: MediaQuery.of(context).size.height * 0.6,
                        alignment: Alignment.center,
                        child: EmptyState(
                          onRetry: () => ref.read(tiendasProvider.notifier).refrescar(),
                        ),
                      ),
                    );
                  }

                  return ListView.separated(
                    padding: const EdgeInsets.fromLTRB(16, 8, 16, 24),
                    itemCount: filtradas.length,
                    separatorBuilder: (context, index) => const SizedBox(height: 12),
                    itemBuilder: (context, index) {
                      final tienda = filtradas[index];
                      return TiendaCard(
                        tienda: tienda,
                        onTap: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text('Seleccionaste: ${tienda.nombre}'),
                              behavior: SnackBarBehavior.floating,
                              backgroundColor: AppColors.primaryDark,
                            ),
                          );
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
}

class _TiendaSkeletonList extends StatelessWidget {
  const _TiendaSkeletonList();

  @override
  Widget build(BuildContext context) {
    return Shimmer.fromColors(
      baseColor: AppColors.shimmerBase,
      highlightColor: AppColors.shimmerHighlight,
      child: ListView.separated(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        itemCount: 5,
        separatorBuilder: (context, index) => const SizedBox(height: 12),
        itemBuilder: (context, index) => Container(
          height: 80,
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

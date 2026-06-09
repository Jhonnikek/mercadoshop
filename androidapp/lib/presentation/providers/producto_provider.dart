import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mercadoshop_app/data/datasources/producto_remote_datasource.dart';
import 'package:mercadoshop_app/data/repositories/producto_repository_impl.dart';
import 'package:mercadoshop_app/domain/entities/producto.dart';
import 'package:mercadoshop_app/domain/usecases/get_productos.dart';

final productoDatasourceProvider = Provider<ProductoRemoteDatasource>((ref) {
  return ProductoRemoteDatasource();
});

final productoRepositoryProvider = Provider<ProductoRepositoryImpl>((ref) {
  return ProductoRepositoryImpl(
    remoteDatasource: ref.read(productoDatasourceProvider),
  );
});

final getProductosUseCaseProvider = Provider<GetProductos>((ref) {
  return GetProductos(ref.read(productoRepositoryProvider));
});

final productosProvider =
    AsyncNotifierProvider<ProductosNotifier, List<Producto>>(
  ProductosNotifier.new,
);

class ProductosNotifier extends AsyncNotifier<List<Producto>> {
  @override
  Future<List<Producto>> build() async {
    return _cargarProductos();
  }

  Future<List<Producto>> _cargarProductos() async {
    final useCase = ref.read(getProductosUseCaseProvider);
    return await useCase();
  }

  Future<void> refrescar() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _cargarProductos());
  }
}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mercadoshop_app/data/datasources/tienda_remote_datasource.dart';
import 'package:mercadoshop_app/data/repositories/tienda_repository_impl.dart';
import 'package:mercadoshop_app/domain/entities/tienda.dart';
import 'package:mercadoshop_app/domain/repositories/tienda_repository.dart';
import 'package:mercadoshop_app/domain/usecases/get_tiendas.dart';

final tiendaDatasourceProvider = Provider<TiendaRemoteDatasource>((ref) {
  return TiendaRemoteDatasource();
});

final tiendaRepositoryProvider = Provider<TiendaRepository>((ref) {
  return TiendaRepositoryImpl(
    remoteDatasource: ref.read(tiendaDatasourceProvider),
  );
});

final getTiendasUseCaseProvider = Provider<GetTiendas>((ref) {
  return GetTiendas(ref.read(tiendaRepositoryProvider));
});

final tiendasProvider =
    AsyncNotifierProvider<TiendasNotifier, List<Tienda>>(
  TiendasNotifier.new,
);

class TiendasNotifier extends AsyncNotifier<List<Tienda>> {
  @override
  Future<List<Tienda>> build() async {
    return _cargarTiendas();
  }

  Future<List<Tienda>> _cargarTiendas() async {
    final useCase = ref.read(getTiendasUseCaseProvider);
    return await useCase();
  }

  Future<void> refrescar() async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() => _cargarTiendas());
  }
}

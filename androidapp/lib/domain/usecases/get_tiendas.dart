import 'package:mercadoshop_app/domain/entities/tienda.dart';
import 'package:mercadoshop_app/domain/repositories/tienda_repository.dart';

class GetTiendas {
  final TiendaRepository repositorio;

  const GetTiendas(this.repositorio);

  Future<List<Tienda>> call() async {
    return await repositorio.obtenerTiendas();
  }
}

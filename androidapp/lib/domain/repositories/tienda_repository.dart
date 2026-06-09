import 'package:mercadoshop_app/domain/entities/tienda.dart';

abstract class TiendaRepository {
  Future<List<Tienda>> obtenerTiendas();
}

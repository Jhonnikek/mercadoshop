import 'package:mercadoshop_app/domain/entities/producto.dart';

abstract class ProductoRepository {
  Future<List<Producto>> obtenerProductos();
}

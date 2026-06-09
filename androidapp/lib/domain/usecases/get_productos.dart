import 'package:mercadoshop_app/domain/entities/producto.dart';
import 'package:mercadoshop_app/domain/repositories/producto_repository.dart';

class GetProductos {
  final ProductoRepository repositorio;

  const GetProductos(this.repositorio);

  Future<List<Producto>> call() async {
    return await repositorio.obtenerProductos();
  }
}

import 'package:mercadoshop_app/domain/entities/producto.dart';

class ProductoModel extends Producto {
  const ProductoModel({
    required super.id,
    required super.nombre,
    required super.precio,
    required super.stock,
    super.descripcion,
    required super.tiendaId,
    required super.tiendaNombre,
  });

  factory ProductoModel.fromJson(Map<String, dynamic> json) {
    return ProductoModel(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      precio: double.parse(json['precio'].toString()),
      stock: json['stock'] as int,
      descripcion: json['descripcion'] as String?,
      tiendaId: json['tienda_id'] as int,
      tiendaNombre: json['tienda_nombre'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'precio': precio,
      'stock': stock,
      'descripcion': descripcion,
      'tienda_id': tiendaId,
      'tienda_nombre': tiendaNombre,
    };
  }
}

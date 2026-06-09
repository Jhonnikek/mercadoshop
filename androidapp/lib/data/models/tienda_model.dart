import 'package:mercadoshop_app/domain/entities/tienda.dart';

class TiendaModel extends Tienda {
  const TiendaModel({
    required super.id,
    required super.nombre,
    required super.direccion,
  });

  factory TiendaModel.fromJson(Map<String, dynamic> json) {
    return TiendaModel(
      id: json['id'] as int,
      nombre: json['nombre'] as String,
      direccion: json['direccion'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'direccion': direccion,
    };
  }
}

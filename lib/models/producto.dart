class Producto {
  final int? id;
  final String nombre;
  final double precio;
  final int stock;
  final String descripcion;

  Producto({
    this.id,
    required this.nombre,
    required this.precio,
    required this.stock,
    this.descripcion = '',
  });

  factory Producto.fromJson(Map<String, dynamic> json) {
    return Producto(
      id: json['id'] as int?,
      nombre: json['nombre'] as String? ?? '',
      precio: (json['precio'] is String)
          ? double.tryParse(json['precio']) ?? 0.0
          : (json['precio'] as num?)?.toDouble() ?? 0.0,
      stock: (json['stock'] is String)
          ? int.tryParse(json['stock']) ?? 0
          : (json['stock'] as num?)?.toInt() ?? 0,
      descripcion: json['descripcion'] as String? ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nombre': nombre,
      'precio': precio,
      'stock': stock,
      'descripcion': descripcion,
    };
  }

  Producto copyWith({
    int? id,
    String? nombre,
    double? precio,
    int? stock,
    String? descripcion,
  }) {
    return Producto(
      id: id ?? this.id,
      nombre: nombre ?? this.nombre,
      precio: precio ?? this.precio,
      stock: stock ?? this.stock,
      descripcion: descripcion ?? this.descripcion,
    );
  }

  @override
  String toString() =>
      'Producto(id: $id, nombre: $nombre, precio: $precio, stock: $stock)';
}

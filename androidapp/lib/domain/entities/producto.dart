class Producto {
  final int id;
  final String nombre;
  final double precio;
  final int stock;
  final String? descripcion;
  final int tiendaId;
  final String tiendaNombre;

  const Producto({
    required this.id,
    required this.nombre,
    required this.precio,
    required this.stock,
    this.descripcion,
    required this.tiendaId,
    required this.tiendaNombre,
  });
}

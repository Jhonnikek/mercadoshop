import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mercadoshop_app/domain/entities/producto.dart';

class CartItem {
  final Producto producto;
  final int cantidad;

  const CartItem({required this.producto, required this.cantidad});

  CartItem copyWith({Producto? producto, int? cantidad}) {
    return CartItem(
      producto: producto ?? this.producto,
      cantidad: cantidad ?? this.cantidad,
    );
  }
}

class CartState {
  final List<CartItem> items;
  final bool animateTrigger; // Toggle this to notify UI to animate

  const CartState({this.items = const [], this.animateTrigger = false});

  double get totalPrecio => items.fold(0, (sum, item) => sum + (item.producto.precio * item.cantidad));
  int get totalItems => items.fold(0, (sum, item) => sum + item.cantidad);

  CartState copyWith({List<CartItem>? items, bool? animateTrigger}) {
    return CartState(
      items: items ?? this.items,
      animateTrigger: animateTrigger ?? this.animateTrigger,
    );
  }
}

class CartNotifier extends Notifier<CartState> {
  @override
  CartState build() {
    return const CartState();
  }

  void agregarProducto(Producto producto) {
    final index = state.items.indexWhere((item) => item.producto.id == producto.id);
    List<CartItem> newItems;

    if (index >= 0) {
      newItems = List.from(state.items);
      newItems[index] = newItems[index].copyWith(cantidad: newItems[index].cantidad + 1);
    } else {
      newItems = [...state.items, CartItem(producto: producto, cantidad: 1)];
    }

    state = state.copyWith(
      items: newItems,
      animateTrigger: !state.animateTrigger,
    );
  }

  void removerProducto(Producto producto) {
    final index = state.items.indexWhere((item) => item.producto.id == producto.id);
    if (index < 0) return;

    List<CartItem> newItems = List.from(state.items);
    if (newItems[index].cantidad > 1) {
      newItems[index] = newItems[index].copyWith(cantidad: newItems[index].cantidad - 1);
    } else {
      newItems.removeAt(index);
    }

    state = state.copyWith(items: newItems);
  }

  void eliminarDelCarrito(Producto producto) {
    final newItems = state.items.where((item) => item.producto.id != producto.id).toList();
    state = state.copyWith(items: newItems);
  }

  void agregarConCantidad(Producto producto, int cantidad) {
    if (cantidad <= 0) return;
    final index = state.items.indexWhere((item) => item.producto.id == producto.id);
    List<CartItem> newItems;

    if (index >= 0) {
      newItems = List.from(state.items);
      newItems[index] = newItems[index].copyWith(cantidad: newItems[index].cantidad + cantidad);
    } else {
      newItems = [...state.items, CartItem(producto: producto, cantidad: cantidad)];
    }

    state = state.copyWith(
      items: newItems,
      animateTrigger: !state.animateTrigger,
    );
  }

  void limpiar() {
    state = const CartState();
  }
}

final cartProvider = NotifierProvider<CartNotifier, CartState>(CartNotifier.new);

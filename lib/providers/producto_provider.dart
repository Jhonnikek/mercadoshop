import 'dart:async';
import 'package:flutter/material.dart';
import '../models/producto.dart';
import '../services/producto_service.dart';

enum ProductoStatus { initial, loading, loaded, error }

class ProductoProvider extends ChangeNotifier {
  final ProductoService _service;

  ProductoProvider(this._service);

  // ─── State ───────────────────────────────────────────────
  List<Producto> _productos = [];
  ProductoStatus _status = ProductoStatus.initial;
  String _errorMessage = '';
  String _searchQuery = '';

  // ─── Getters ─────────────────────────────────────────────
  List<Producto> get productos {
    if (_searchQuery.isEmpty) return _productos;
    final q = _searchQuery.toLowerCase();
    return _productos.where((p) => p.nombre.toLowerCase().contains(q)).toList();
  }

  List<Producto> get allProductos => _productos;
  ProductoStatus get status => _status;
  String get errorMessage => _errorMessage;
  String get searchQuery => _searchQuery;

  int get totalProductos => _productos.length;

  Producto? get productoMayorStock {
    if (_productos.isEmpty) return null;
    return _productos.reduce((a, b) => a.stock >= b.stock ? a : b);
  }

  Producto? get productoMasCaro {
    if (_productos.isEmpty) return null;
    return _productos.reduce((a, b) => a.precio >= b.precio ? a : b);
  }

  List<Producto> get ultimosCinco {
    if (_productos.length <= 5) return _productos;
    return _productos.sublist(_productos.length - 5);
  }

  // ─── Actions ─────────────────────────────────────────────
  void setSearch(String query) {
    _searchQuery = query;
    notifyListeners();
  }

  Future<void> loadProductos() async {
    _status = ProductoStatus.loading;
    notifyListeners();
    try {
      _productos = await _service.getProductos();
      _status = ProductoStatus.loaded;
    } on TimeoutException {
      _errorMessage = 'Tiempo de conexión agotado';
      _status = ProductoStatus.error;
    } catch (e) {
      _errorMessage = e.toString();
      _status = ProductoStatus.error;
    }
    notifyListeners();
  }

  Future<bool> createProducto(Producto p) async {
    try {
      final created = await _service.createProducto(p);
      _productos.add(created);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      return false;
    }
  }

  Future<bool> updateProducto(int id, Producto p) async {
    try {
      final updated = await _service.updateProducto(id, p);
      final idx = _productos.indexWhere((x) => x.id == id);
      if (idx != -1) {
        _productos[idx] = updated;
      }
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      return false;
    }
  }

  Future<bool> deleteProducto(int id) async {
    try {
      await _service.deleteProducto(id);
      _productos.removeWhere((x) => x.id == id);
      notifyListeners();
      return true;
    } catch (e) {
      _errorMessage = e.toString();
      return false;
    }
  }
}

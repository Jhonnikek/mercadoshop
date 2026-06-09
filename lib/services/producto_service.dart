import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/producto.dart';
import 'auth_service.dart';

class ProductoService {
  final AuthService _authService;

  ProductoService(this._authService);

  Future<List<Producto>> getProductos() async {
    final token = await _authService.getAccessToken();

    if (token == null || token.isEmpty) {
      throw HttpException('401: Token no encontrado');
    }

    var response = await http.get(
      Uri.parse(PRODUCTOS_URL),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 401) {
      final refreshed = await _authService.refreshAccessToken();
      if (refreshed) {
        final newToken = await _authService.getAccessToken();
        response = await http.get(
          Uri.parse(PRODUCTOS_URL),
          headers: {
            'Authorization': 'Bearer $newToken',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        ).timeout(const Duration(seconds: 15));
      } else {
        await _authService.logoutAndRedirect();
      }
    }

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      final List<dynamic> data = body is List
          ? body
          : (body['productos'] as List<dynamic>? ?? []);
      return data.map((json) => Producto.fromJson(json as Map<String, dynamic>)).toList();
    } else if (response.statusCode == 401) {
      throw HttpException('401: Error al obtener productos');
    } else {
      throw HttpException('${response.statusCode}: Error al obtener productos');
    }
  }

  Future<Producto> createProducto(Producto p) async {
    final token = await _authService.getAccessToken();

    if (token == null || token.isEmpty) {
      throw HttpException('401: Token no encontrado');
    }

    final url = PRODUCTOS_URL.endsWith('/') ? PRODUCTOS_URL : '$PRODUCTOS_URL/';
    var response = await http.post(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode(p.toJson()),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 401) {
      final refreshed = await _authService.refreshAccessToken();
      if (refreshed) {
        final newToken = await _authService.getAccessToken();
        response = await http.post(
          Uri.parse(url),
          headers: {
            'Authorization': 'Bearer $newToken',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: jsonEncode(p.toJson()),
        ).timeout(const Duration(seconds: 15));
      } else {
        await _authService.logoutAndRedirect();
      }
    }

    if (response.statusCode == 200 || response.statusCode == 201) {
      return Producto.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    } else if (response.statusCode == 401) {
      throw HttpException('401: Error al crear producto');
    } else {
      throw HttpException('${response.statusCode}: Error al crear producto');
    }
  }

  Future<Producto> updateProducto(int id, Producto p) async {
    final token = await _authService.getAccessToken();

    if (token == null || token.isEmpty) {
      throw HttpException('401: Token no encontrado');
    }

    final detailUrl = productoDetailUrl(id);
    final url = detailUrl.endsWith('/') ? detailUrl : '$detailUrl/';
    var response = await http.put(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: jsonEncode(p.toJson()),
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 401) {
      final refreshed = await _authService.refreshAccessToken();
      if (refreshed) {
        final newToken = await _authService.getAccessToken();
        response = await http.put(
          Uri.parse(url),
          headers: {
            'Authorization': 'Bearer $newToken',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          body: jsonEncode(p.toJson()),
        ).timeout(const Duration(seconds: 15));
      } else {
        await _authService.logoutAndRedirect();
      }
    }

    if (response.statusCode == 200) {
      return Producto.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    } else if (response.statusCode == 401) {
      throw HttpException('401: Error al actualizar producto');
    } else {
      throw HttpException('${response.statusCode}: Error al actualizar producto');
    }
  }

  Future<void> deleteProducto(int id) async {
    final token = await _authService.getAccessToken();

    if (token == null || token.isEmpty) {
      throw HttpException('401: Token no encontrado');
    }

    final detailUrl = productoDetailUrl(id);
    final url = detailUrl.endsWith('/') ? detailUrl : '$detailUrl/';
    var response = await http.delete(
      Uri.parse(url),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ).timeout(const Duration(seconds: 15));

    if (response.statusCode == 401) {
      final refreshed = await _authService.refreshAccessToken();
      if (refreshed) {
        final newToken = await _authService.getAccessToken();
        response = await http.delete(
          Uri.parse(url),
          headers: {
            'Authorization': 'Bearer $newToken',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        ).timeout(const Duration(seconds: 15));
      } else {
        await _authService.logoutAndRedirect();
      }
    }

    if (response.statusCode == 200 || response.statusCode == 204) {
      return;
    } else if (response.statusCode == 401) {
      throw HttpException('401: Error al eliminar producto');
    } else {
      throw HttpException('${response.statusCode}: Error al eliminar producto');
    }
  }
}

class HttpException implements Exception {
  final String message;
  final int? statusCode;
  HttpException(this.message, [this.statusCode]);

  @override
  String toString() => statusCode != null ? 'HttpException($statusCode): $message' : 'HttpException: $message';
}

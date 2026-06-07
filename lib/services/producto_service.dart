import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/producto.dart';
import 'auth_service.dart';

class ProductoService {
  final AuthService _authService;

  ProductoService(this._authService);

  /// Builds auth headers using the stored JWT.
  Future<Map<String, String>> _authHeaders() async {
    final token = await _authService.getAccessToken();
    return {
      'Authorization': 'Bearer $token',
      'Content-Type': 'application/json',
    };
  }

  /// GET all products.
  Future<List<Producto>> getProductos() async {
    final headers = await _authHeaders();
    // Ensuring the trailing slash is present
    final url = PRODUCTOS_URL.endsWith('/') ? PRODUCTOS_URL : '$PRODUCTOS_URL/';
    final response = await http
        .get(Uri.parse(url), headers: headers)
        .timeout(const Duration(seconds: 15));

    print('STATUS: ${response.statusCode}');
    print('BODY: ${response.body}');

    if (response.statusCode == 200) {
      final body = jsonDecode(response.body);
      // Handle both paginated ({ results: [...] }) and plain list responses
      final List<dynamic> list =
          (body is List) ? body : (body['results'] as List<dynamic>? ?? []);
      return list
          .map((e) => Producto.fromJson(e as Map<String, dynamic>))
          .toList();
    }

    throw HttpException(
      'Error al obtener productos',
      response.statusCode,
    );
  }

  /// POST – create a new product.
  Future<Producto> createProducto(Producto p) async {
    final headers = await _authHeaders();
    final url = PRODUCTOS_URL.endsWith('/') ? PRODUCTOS_URL : '$PRODUCTOS_URL/';
    final response = await http
        .post(
          Uri.parse(url),
          headers: headers,
          body: jsonEncode(p.toJson()),
        )
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200 || response.statusCode == 201) {
      return Producto.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }

    throw HttpException('Error al crear producto', response.statusCode);
  }

  /// PUT – update an existing product.
  Future<Producto> updateProducto(int id, Producto p) async {
    final headers = await _authHeaders();
    final detailUrl = productoDetailUrl(id);
    final url = detailUrl.endsWith('/') ? detailUrl : '$detailUrl/';
    final response = await http
        .put(
          Uri.parse(url),
          headers: headers,
          body: jsonEncode(p.toJson()),
        )
        .timeout(const Duration(seconds: 15));

    if (response.statusCode == 200) {
      return Producto.fromJson(
        jsonDecode(response.body) as Map<String, dynamic>,
      );
    }

    throw HttpException('Error al actualizar producto', response.statusCode);
  }

  /// DELETE – remove a product.
  Future<void> deleteProducto(int id) async {
    final headers = await _authHeaders();
    final detailUrl = productoDetailUrl(id);
    final url = detailUrl.endsWith('/') ? detailUrl : '$detailUrl/';
    final response = await http
        .delete(Uri.parse(url), headers: headers)
        .timeout(const Duration(seconds: 15));

    if (response.statusCode != 200 && response.statusCode != 204) {
      throw HttpException('Error al eliminar producto', response.statusCode);
    }
  }
}

/// Simple typed HTTP exception.
class HttpException implements Exception {
  final String message;
  final int statusCode;
  HttpException(this.message, this.statusCode);

  @override
  String toString() => 'HttpException($statusCode): $message';
}

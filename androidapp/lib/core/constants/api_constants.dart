import 'package:flutter_dotenv/flutter_dotenv.dart';

class ApiConstants {
  ApiConstants._();

  static String get baseUrl => dotenv.env['BASE_URL'] ?? 'http://10.0.2.2:8000';

  static const String productos = '/api/clientes/productos/';
  static const String tiendas = '/api/clientes/tiendas/';
}

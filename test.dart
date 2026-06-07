import 'dart:convert';
import 'package:http/http.dart' as http;

void main() async {
  final url = 'http://149.130.191.83/api/tiendas/productos/';
  print('Testing GET $url');
  var response = await http.get(Uri.parse(url));
  print('GET STATUS: ${response.statusCode}');
  print('GET BODY: ${response.body}');
  print('GET HEADERS: ${response.headers}');
}

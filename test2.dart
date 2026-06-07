import 'package:http/http.dart' as http;

void main() async {
  final urls = [
    'http://149.130.191.83/api/tiendas/productos/',
    'http://149.130.191.83/api/productos/',
    'http://149.130.191.83/api/tienda/productos/',
    'http://149.130.191.83/api/tiendas/producto/',
    'http://149.130.191.83/api/tienda/producto/'
  ];
  
  for (final url in urls) {
    print('Testing GET $url');
    var response = await http.get(Uri.parse(url));
    print('GET STATUS: ${response.statusCode}');
    if (response.headers.containsKey('allow')) {
      print('ALLOW: ${response.headers['allow']}');
    }
    print('---');
  }
}

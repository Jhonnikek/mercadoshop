import 'package:http/http.dart' as http;

void main() async {
  var response = await http.get(Uri.parse('http://149.130.191.83/api/'));
  print('API ROOT: ${response.statusCode}');
  print('BODY: ${response.body}');
}

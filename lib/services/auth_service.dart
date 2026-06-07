import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import '../core/constants.dart';

class AuthService {
  static const _storage = FlutterSecureStorage();
  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  /// Attempts login. Returns `true` on success (200), `false` otherwise.
  Future<bool> login(String username, String password) async {
    try {
      final url = LOGIN_URL.endsWith('/') ? LOGIN_URL : '$LOGIN_URL/';
      final response = await http
          .post(
            Uri.parse(url),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'username': username, 'password': password}),
          )
          .timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final access = data['access'] as String?;
        final refresh = data['refresh'] as String?;

        if (access != null && refresh != null) {
          await _storage.write(key: _accessKey, value: access);
          await _storage.write(key: _refreshKey, value: refresh);
          return true;
        }
      }
      return false;
    } catch (_) {
      rethrow;
    }
  }

  /// Clears both tokens from secure storage.
  Future<void> logout() async {
    await _storage.delete(key: _accessKey);
    await _storage.delete(key: _refreshKey);
  }

  /// Returns the stored access token, or `null`.
  Future<String?> getAccessToken() async {
    return _storage.read(key: _accessKey);
  }

  /// Returns `true` when a non-empty access token is present.
  Future<bool> isAuthenticated() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}

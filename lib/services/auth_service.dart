import 'dart:convert';
import 'package:flutter/widgets.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:provider/provider.dart';
import '../core/constants.dart';
import '../providers/auth_provider.dart';

class AuthService {
  static const _storage = FlutterSecureStorage();

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
          await _storage.write(key: 'access_token', value: access);
          await _storage.write(key: 'refresh_token', value: refresh);
          await _storage.write(key: 'username', value: username);
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
    await _storage.delete(key: 'access_token');
    await _storage.delete(key: 'refresh_token');
    await _storage.delete(key: 'username');
  }

  Future<String?> getUsername() async {
    return await _storage.read(key: 'username');
  }

  Future<Map<String, dynamic>> getDashboardInfo() async {
    final token = await getAccessToken();
    final response = await http.get(
      Uri.parse('http://149.130.191.83/api/tiendas/dashboard/'),
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    }
    return {};
  }

  /// Returns the stored access token, or `null`.
  Future<String?> getAccessToken() async {
    return await _storage.read(key: 'access_token');
  }

  /// Returns `true` when a non-empty access token is present.
  Future<bool> isAuthenticated() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  /// Attempts to refresh the access token using the stored refresh token.
  /// Returns `true` if successful, `false` otherwise.
  Future<bool> refreshAccessToken() async {
    try {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken == null || refreshToken.isEmpty) {
        return false;
      }

      final url = REFRESH_URL;
      final response = await http.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body) as Map<String, dynamic>;
        final access = data['access'] as String?;
        final refresh = data['refresh'] as String?;

        if (access != null) {
          await _storage.write(key: 'access_token', value: access);
          if (refresh != null) {
            await _storage.write(key: 'refresh_token', value: refresh);
          }
          return true;
        }
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// Clears tokens and attempts to redirect the user to the login screen
  /// by invoking the logout method of the AuthProvider.
  Future<void> logoutAndRedirect() async {
    await logout();
    // Use WidgetsBinding to find the AuthProvider and call its logout to trigger routing
    WidgetsBinding.instance.addPostFrameCallback((_) {
      try {
        final rootElement = WidgetsBinding.instance.rootElement;
        if (rootElement != null) {
          BuildContext? findDescendant(Element element) {
            BuildContext? found;
            try {
              // Try reading AuthProvider from the current element's context
              Provider.of<AuthProvider>(element, listen: false);
              found = element;
            } catch (_) {
              element.visitChildren((child) {
                if (found != null) return;
                final f = findDescendant(child);
                if (f != null) {
                  found = f;
                }
              });
            }
            return found;
          }

          final context = findDescendant(rootElement);
          if (context != null) {
            Provider.of<AuthProvider>(context, listen: false).logout();
          }
        }
      } catch (_) {}  // ignore: empty_catches
    });
  }
}


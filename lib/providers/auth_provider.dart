import 'dart:async';
import 'package:flutter/material.dart';
import '../services/auth_service.dart';

class AuthProvider extends ChangeNotifier {
  final AuthService _authService;

  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _errorMessage;

  AuthProvider(this._authService);

  // ─── Getters ──────────────────────────────────────────────
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get errorMessage => _errorMessage;

  /// Check persisted session on app start.
  Future<void> checkSession() async {
    _isAuthenticated = await _authService.isAuthenticated();
    notifyListeners();
  }

  /// Login using username/password.
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _errorMessage = null;
    notifyListeners();

    try {
      final success = await _authService.login(username, password);
      if (success) {
        _isAuthenticated = true;
      } else {
        _errorMessage = 'Credenciales incorrectas';
      }
      return success;
    } on TimeoutException {
      _errorMessage = 'Error de conexión: tiempo agotado';
      return false;
    } catch (e) {
      _errorMessage = 'Error de conexión';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Logout – clear tokens.
  Future<void> logout() async {
    await _authService.logout();
    _isAuthenticated = false;
    notifyListeners();
  }
}

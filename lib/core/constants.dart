// ignore_for_file: constant_identifier_names

const String BASE_URL = 'http://149.130.191.83/api';

// Auth endpoints
const String LOGIN_URL = '$BASE_URL/token/';
const String REFRESH_URL = '$BASE_URL/token/refresh/';

// Product endpoints
const String PRODUCTOS_URL = '$BASE_URL/tiendas/productos/';

String productoDetailUrl(int id) => '$PRODUCTOS_URL$id/';

import 'package:dio/dio.dart';
import 'package:mercadoshop_app/core/constants/api_constants.dart';
import 'package:mercadoshop_app/core/network/dio_client.dart';
import 'package:mercadoshop_app/data/models/producto_model.dart';

class ProductoRemoteDatasource {
  final Dio _dio;

  ProductoRemoteDatasource({Dio? dio}) : _dio = dio ?? DioClient.instance;

  Future<List<ProductoModel>> obtenerProductos() async {
    final response = await _dio.get(ApiConstants.productos);
    final List<dynamic> data = response.data as List<dynamic>;
    return data
        .map((json) => ProductoModel.fromJson(json as Map<String, dynamic>))
        .toList();
  }
}

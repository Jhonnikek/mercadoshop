import 'package:dio/dio.dart';
import 'package:mercadoshop_app/core/constants/api_constants.dart';
import 'package:mercadoshop_app/core/network/dio_client.dart';
import 'package:mercadoshop_app/data/models/tienda_model.dart';

class TiendaRemoteDatasource {
  final Dio _dio;

  TiendaRemoteDatasource({Dio? dio}) : _dio = dio ?? DioClient.instance;

  Future<List<TiendaModel>> obtenerTiendas() async {
    final response = await _dio.get(ApiConstants.tiendas);
    final List<dynamic> data = response.data as List<dynamic>;
    return data
        .map((json) => TiendaModel.fromJson(json as Map<String, dynamic>))
        .toList();
  }
}

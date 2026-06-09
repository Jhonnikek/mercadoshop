import 'package:dio/dio.dart';
import 'package:mercadoshop_app/core/errors/failures.dart';
import 'package:mercadoshop_app/data/datasources/tienda_remote_datasource.dart';
import 'package:mercadoshop_app/domain/entities/tienda.dart';
import 'package:mercadoshop_app/domain/repositories/tienda_repository.dart';

class TiendaRepositoryImpl implements TiendaRepository {
  final TiendaRemoteDatasource remoteDatasource;

  const TiendaRepositoryImpl({required this.remoteDatasource});

  @override
  Future<List<Tienda>> obtenerTiendas() async {
    try {
      return await remoteDatasource.obtenerTiendas();
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.connectionTimeout) {
        throw const NetworkFailure();
      }
      throw ServerFailure(
        e.response?.statusMessage ?? 'Error del servidor',
        codigoEstado: e.response?.statusCode,
      );
    } catch (e) {
      throw UnknownFailure(e.toString());
    }
  }
}

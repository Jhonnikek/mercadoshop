import 'package:dio/dio.dart';
import 'package:mercadoshop_app/core/errors/failures.dart';
import 'package:mercadoshop_app/data/datasources/producto_remote_datasource.dart';
import 'package:mercadoshop_app/domain/entities/producto.dart';
import 'package:mercadoshop_app/domain/repositories/producto_repository.dart';

class ProductoRepositoryImpl implements ProductoRepository {
  final ProductoRemoteDatasource remoteDatasource;

  const ProductoRepositoryImpl({required this.remoteDatasource});

  @override
  Future<List<Producto>> obtenerProductos() async {
    try {
      return await remoteDatasource.obtenerProductos();
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

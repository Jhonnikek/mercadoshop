abstract class Failure {
  final String mensaje;
  const Failure(this.mensaje);
}

class ServerFailure extends Failure {
  final int? codigoEstado;
  const ServerFailure(super.mensaje, {this.codigoEstado});
}

class NetworkFailure extends Failure {
  const NetworkFailure([super.mensaje = 'Sin conexión a internet']);
}

class UnknownFailure extends Failure {
  const UnknownFailure([super.mensaje = 'Ocurrió un error inesperado']);
}

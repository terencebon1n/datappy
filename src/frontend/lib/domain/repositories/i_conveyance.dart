import 'package:frontend/domain/conveyance.dart' show Conveyance;


abstract class IConveyanceRepository {
    abstract Map<String, String> headers;

    Future<List<Conveyance>> resolveConveyances();
}

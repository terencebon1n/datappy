import 'package:frontend/domain/city.dart' show City;
import 'package:frontend/domain/conveyance.dart' show Conveyance;


abstract class IConveyanceRepository {
    Future<List<Conveyance>> resolveConveyances(City city);
}

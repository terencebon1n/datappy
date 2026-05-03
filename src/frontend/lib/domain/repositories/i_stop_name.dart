abstract class IStopNameRepository {
    Future<List<String>> resolveStopNames(String routeId);
}

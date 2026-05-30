abstract class IStopNameRepository {
    abstract Map<String, String> headers;

    Future<List<String>> resolveStopNames(String routeId);
}

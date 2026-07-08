import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/route_selection/state.dart';

import '../helpers/fakes.dart';

Future<RouteSelectionCubit> makeCubit({
  FakeCityRepo? cityRepo,
  FakeConveyanceRepo? conveyanceRepo,
  FakeStopNameRepo? stopRepo,
  FakeDirectionRepo? directionRepo,
  InMemorySelectionStore? store,
}) async {
  final cubit = RouteSelectionCubit(
    cityRepo: cityRepo ?? FakeCityRepo(cities: [sampleCity()]),
    conveyanceRepo: conveyanceRepo ?? FakeConveyanceRepo(),
    stopRepo: stopRepo ?? FakeStopNameRepo(),
    directionRepo: directionRepo ?? FakeDirectionRepo(),
    selectionStore: store ?? InMemorySelectionStore(),
  );
  await Future<void>.delayed(Duration.zero);
  return cubit;
}

Future<RouteSelectionCubit> submittable(FakeDirectionRepo directionRepo) async {
  final cubit = await makeCubit(
    cityRepo: FakeCityRepo(cities: [sampleCity()]),
    conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    stopRepo: FakeStopNameRepo(stops: const ['Perrache', 'Debourg']),
    directionRepo: directionRepo,
  );
  cubit.selectCity(sampleCity());
  await Future<void>.delayed(Duration.zero);
  cubit.selectConveyance(sampleConveyance());
  await Future<void>.delayed(Duration.zero);
  cubit.selectSourceStop('Perrache');
  cubit.selectDestStop('Debourg');
  await Future<void>.delayed(Duration.zero);
  return cubit;
}

void main() {
  group('_init', () {
    test('loads cities when nothing is saved', () async {
      final cubit = await makeCubit(cityRepo: FakeCityRepo(cities: [sampleCity('Lyon')]));
      expect(cubit.state.cities.single.name, 'Lyon');
      expect(cubit.state.selectedCity, isNull);
      await cubit.close();
    });

    test('restores the saved selection when present', () async {
      final saved = sampleSelection();
      final cubit = await makeCubit(
        cityRepo: FakeCityRepo(cities: [sampleCity()]),
        store: InMemorySelectionStore(saved),
      );
      expect(cubit.state.selectedCity!.name, saved.city.name);
      expect(cubit.state.selectedConveyance!.id, saved.conveyance.id);
      expect(cubit.state.sourceStop, saved.sourceStop);
      expect(cubit.state.destStop, saved.destStop);
      expect(cubit.state.direction!.directionId, saved.direction.directionId);
      await cubit.close();
    });

    test('tolerates a failing city repository', () async {
      final cubit = await makeCubit(cityRepo: FakeCityRepo(throwError: true));
      expect(cubit.state.cities, isEmpty);
      await cubit.close();
    });
  });

  test('loadSelection emits and persists', () async {
    final store = InMemorySelectionStore();
    final cubit = await makeCubit(store: store);
    final sel = sampleSelection();

    await cubit.loadSelection(sel);

    expect(cubit.state.selectedCity!.name, sel.city.name);
    expect(cubit.state.canSubmit, isTrue);
    expect(store.selection, sel);
    await cubit.close();
  });

  test('reset clears the selection but keeps cities', () async {
    final cubit = await submittable(FakeDirectionRepo());
    expect(cubit.state.canSubmit, isTrue);

    cubit.reset();

    expect(cubit.state.selectedCity, isNull);
    expect(cubit.state.step, FunnelStep.city);
    expect(cubit.state.cities, isNotEmpty);
    await cubit.close();
  });

  group('beginSearch / cancelSearch', () {
    test('snapshots a submittable selection and restores it on cancel', () async {
      final cubit = await submittable(FakeDirectionRepo());

      cubit.beginSearch();
      expect(cubit.state.selectedCity, isNull);

      cubit.cancelSearch();
      expect(cubit.state.canSubmit, isTrue);
      await cubit.close();
    });

    test('with no submittable selection, cancel clears everything', () async {
      final cubit = await makeCubit();

      cubit.beginSearch();
      cubit.cancelSearch();

      expect(cubit.state.selectedCity, isNull);
      expect(cubit.state.selectedConveyance, isNull);
      await cubit.close();
    });
  });

  group('back', () {
    test('returns false at the first step', () async {
      final cubit = await makeCubit();
      expect(cubit.back(), isFalse);
      await cubit.close();
    });

    test('walks back through every step', () async {
      final cubit = await submittable(FakeDirectionRepo());
      expect(cubit.state.step, FunnelStep.dest);

      expect(cubit.back(), isTrue);
      expect(cubit.state.step, FunnelStep.source);
      expect(cubit.back(), isTrue);
      expect(cubit.state.step, FunnelStep.line);
      expect(cubit.back(), isTrue);
      expect(cubit.state.step, FunnelStep.city);
      expect(cubit.back(), isFalse);
      await cubit.close();
    });
  });

  test('selectCity advances to line and loads conveyances', () async {
    final cubit = await makeCubit(
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
    );

    cubit.selectCity(sampleCity());
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.step, FunnelStep.line);
    expect(cubit.state.selectedCity!.name, 'Lyon');
    expect(cubit.state.conveyances, hasLength(1));
    await cubit.close();
  });

  test('selectConveyance advances to source and loads stops', () async {
    final cubit = await makeCubit(
      conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
      stopRepo: FakeStopNameRepo(stops: const ['A', 'B']),
    );
    cubit.selectCity(sampleCity());
    await Future<void>.delayed(Duration.zero);

    cubit.selectConveyance(sampleConveyance());
    await Future<void>.delayed(Duration.zero);

    expect(cubit.state.step, FunnelStep.source);
    expect(cubit.state.stops, const ['A', 'B']);
    await cubit.close();
  });

  group('selectDestStop / _checkAndResolveDirection', () {
    test('resolves the direction and persists a full selection', () async {
      final store = InMemorySelectionStore();
      final directionRepo = FakeDirectionRepo();
      final cubit = await makeCubit(
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: const ['Perrache', 'Debourg']),
        directionRepo: directionRepo,
        store: store,
      );
      cubit.selectCity(sampleCity());
      await Future<void>.delayed(Duration.zero);
      cubit.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
      cubit.selectSourceStop('Perrache');

      cubit.selectDestStop('Debourg');
      await Future<void>.delayed(Duration.zero);

      expect(directionRepo.calls, 1);
      expect(cubit.state.canSubmit, isTrue);
      expect(store.selection, isNotNull);
      await cubit.close();
    });

    test('clears the destination when resolution fails', () async {
      final directionRepo = FakeDirectionRepo(throwError: true);
      final cubit = await makeCubit(
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: const ['Perrache', 'Debourg']),
        directionRepo: directionRepo,
      );
      cubit.selectCity(sampleCity());
      await Future<void>.delayed(Duration.zero);
      cubit.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
      cubit.selectSourceStop('Perrache');

      cubit.selectDestStop('Debourg');
      await Future<void>.delayed(Duration.zero);

      expect(directionRepo.calls, 1);
      expect(cubit.state.destStop, isNull);
      expect(cubit.state.direction, isNull);
      await cubit.close();
    });

    test('does not resolve when destination equals source', () async {
      final directionRepo = FakeDirectionRepo();
      final cubit = await makeCubit(
        conveyanceRepo: FakeConveyanceRepo(conveyances: [sampleConveyance()]),
        stopRepo: FakeStopNameRepo(stops: const ['Perrache']),
        directionRepo: directionRepo,
      );
      cubit.selectCity(sampleCity());
      await Future<void>.delayed(Duration.zero);
      cubit.selectConveyance(sampleConveyance());
      await Future<void>.delayed(Duration.zero);
      cubit.selectSourceStop('Perrache');

      cubit.selectDestStop('Perrache');
      await Future<void>.delayed(Duration.zero);

      expect(directionRepo.calls, 0);
      expect(cubit.state.direction, isNull);
      await cubit.close();
    });
  });

  test('RouteSelectionState.copyWith overrides only given fields', () {
    const base = RouteSelectionState();
    final next = base.copyWith(
      status: RouteSelectionStatus.ready,
      step: FunnelStep.line,
      stops: const ['X'],
    );
    expect(next.status, RouteSelectionStatus.ready);
    expect(next.step, FunnelStep.line);
    expect(next.stops, const ['X']);
    expect(next.cities, base.cities);
  });
}

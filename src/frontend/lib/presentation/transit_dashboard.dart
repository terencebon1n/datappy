import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/domain/saved_selection.dart';
import 'package:frontend/domain/transit_path.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/top_bar.dart';
import 'package:frontend/presentation/widgets/line_card.dart';
import 'package:frontend/presentation/widgets/departure_board.dart';
import 'package:frontend/presentation/widgets/bottom_nav.dart';
import 'package:frontend/presentation/widgets/footer_hint.dart';
import 'package:frontend/presentation/favorites/favorites_page.dart';
import 'package:frontend/presentation/funnel/funnel_page.dart';

class TransitDashboard extends StatefulWidget {
  const TransitDashboard({super.key});

  @override
  State<TransitDashboard> createState() => _TransitDashboardState();
}

class _TransitDashboardState extends State<TransitDashboard> {
  int _navIndex = 0;
  DateTime _now = DateTime.now();
  late final Timer _ticker;

  @override
  void initState() {
    super.initState();
    _ticker = Timer.periodic(
      const Duration(seconds: 1),
      (_) => setState(() => _now = DateTime.now()),
    );
  }

  @override
  void dispose() {
    _ticker.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return AnnotatedRegion<SystemUiOverlayStyle>(
      value: SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: isDark ? Brightness.light : Brightness.dark,
        statusBarBrightness: isDark ? Brightness.dark : Brightness.light,
      ),
      child: Scaffold(
        backgroundColor: TransitColors.bg,
        extendBody: true,
        body: SafeArea(
          child: IndexedStack(
            index: _navIndex,
            children: [
              _buildHome(),
              FavoritesPage(onSelect: _loadFavorite),
            ],
          ),
        ),
        bottomNavigationBar: BottomNav(
          index: _navIndex,
          onTap: (i) => setState(() => _navIndex = i),
        ),
      ),
    );
  }

  Widget _buildHome() {
    return Column(
      children: [
        TopBar(onSearchTap: () => _openFunnel(context)),
        Expanded(
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(14, 0, 14, 100),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                LineCard(now: _now),
                const SizedBox(height: 10),
                DepartureBoard(now: _now),
                const SizedBox(height: 8),
                const FooterHint(),
              ],
            ),
          ),
        ),
      ],
    );
  }

  /// Load a saved favorite: restore it onto the dashboard, (re)connect its live
  /// feed and jump back to Home. Mirrors what the funnel does on completion.
  void _loadFavorite(SavedSelection fav) {
    context.read<RouteSelectionCubit>().loadSelection(fav);
    context.read<StopUpdateCubit>().watchStopUpdates(
      TransitPath(
        city: fav.city.name.toLowerCase(),
        routeId: fav.conveyance.id,
        direction: fav.direction,
      ),
    );
    setState(() => _navIndex = 0);
  }

  void _openFunnel(BuildContext context) {
    // Start a fresh search at the city step, but remember the current selection
    // so it survives a misclick: if the funnel is dismissed without completing
    // a new search, restore what was showing before. The funnel reads the
    // app-level cubits directly, so it needs no providers of its own.
    final cubit = context.read<RouteSelectionCubit>();
    cubit.beginSearch();
    Navigator.of(context)
        .push<bool>(
          MaterialPageRoute(
            fullscreenDialog: true,
            builder: (_) => const FunnelPage(),
          ),
        )
        .then((completed) {
      if (completed != true) cubit.cancelSearch();
    });
  }
}

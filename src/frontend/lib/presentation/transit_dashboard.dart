import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/application/stop_update/cubit.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/top_bar.dart';
import 'package:frontend/presentation/widgets/line_card.dart';
import 'package:frontend/presentation/widgets/departure_board.dart';
import 'package:frontend/presentation/widgets/bottom_nav.dart';
import 'package:frontend/presentation/widgets/footer_hint.dart';
import 'package:frontend/presentation/search/search_sheet.dart';

class TransitDashboard extends StatefulWidget {
  const TransitDashboard({super.key});

  @override
  State<TransitDashboard> createState() => _TransitDashboardState();
}

class _TransitDashboardState extends State<TransitDashboard> {
  int      _navIndex = 0;
  DateTime _now      = DateTime.now();
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
    SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
      statusBarColor: Colors.transparent,
      statusBarIconBrightness: Brightness.light,
    ));

    return Scaffold(
      backgroundColor: TransitColors.bg,
      extendBody: true,
      body: SafeArea(
        child: Column(
          children: [
            TopBar(onSearchTap: () => _openSearchSheet(context)),
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
        ),
      ),
      bottomNavigationBar: BottomNav(
        index: _navIndex,
        onTap: (i) => setState(() => _navIndex = i),
      ),
    );
  }

    void _openSearchSheet(BuildContext context) {
      showModalBottomSheet(
        context: context,
        isScrollControlled: true,
        useSafeArea: true, // Ensures content stays below the status bar/notch
        backgroundColor: Colors.transparent,
        builder: (_) => MultiBlocProvider(
          providers: [
            BlocProvider.value(value: context.read<RouteSelectionCubit>()),
            BlocProvider.value(value: context.read<StopUpdateCubit>()),
          ],
          child: SizedBox(
            // Takes up 95% of the screen height. Change to 1.0 for absolute full screen.
            height: MediaQuery.of(context).size.height * 0.75, 
            child: const SearchSheet(),
          ),
        ),
      );
    }
}

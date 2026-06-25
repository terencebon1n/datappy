import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import 'package:frontend/application/route_selection/cubit.dart';
import 'package:frontend/presentation/theme/colors.dart';
import 'package:frontend/presentation/widgets/top_bar.dart';
import 'package:frontend/presentation/widgets/line_card.dart';
import 'package:frontend/presentation/widgets/departure_board.dart';
import 'package:frontend/presentation/widgets/bottom_nav.dart';
import 'package:frontend/presentation/widgets/footer_hint.dart';
import 'package:frontend/presentation/funnel/funnel_page.dart';

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
        ),
      ),
      bottomNavigationBar: BottomNav(
        index: _navIndex,
        onTap: (i) => setState(() => _navIndex = i),
      ),
    );
  }

    void _openFunnel(BuildContext context) {
      // Start a fresh search at the city step. The funnel reads the app-level
      // cubits directly, so it needs no providers of its own.
      context.read<RouteSelectionCubit>().reset();
      Navigator.of(context).push(
        MaterialPageRoute(
          fullscreenDialog: true,
          builder: (_) => const FunnelPage(),
        ),
      );
    }
}

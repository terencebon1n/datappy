import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'package:frontend/application/route_selection/state.dart' show FunnelStep;
import 'package:frontend/presentation/funnel/funnel_colors.dart';

/// Dark-blue funnel header (mockup `.hdr`) with an optional 3-dot stepper
/// (Ligne · Départ · Arrivée) and an optional [bottom] slot (e.g. a search bar).
class FunnelHeader extends StatelessWidget {
  const FunnelHeader({
    super.key,
    required this.overline,
    required this.title,
    required this.onLeading,
    this.leadingIsClose = false,
    this.stepperFor,
    this.bottom,
  });

  final String overline;
  final String title;
  final VoidCallback onLeading;
  final bool leadingIsClose;

  /// When non-null, renders the funnel stepper with this step as current.
  final FunnelStep? stepperFor;
  final Widget? bottom;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      color: FunnelColors.header,
      padding: EdgeInsets.fromLTRB(16, 12 + MediaQuery.of(context).padding.top, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              _CircleButton(
                icon: leadingIsClose ? Icons.close : Icons.arrow_back,
                onTap: onLeading,
              ),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      overline.toUpperCase(),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: FunnelColors.onHeaderMuted,
                        fontSize: 10,
                        letterSpacing: 0.4,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: GoogleFonts.syne(
                        color: FunnelColors.onHeader,
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (stepperFor != null) ...[
            const SizedBox(height: 14),
            _Stepper(current: stepperFor!),
          ],
          if (bottom != null) ...[
            const SizedBox(height: 12),
            bottom!,
          ],
        ],
      ),
    );
  }
}

class _CircleButton extends StatelessWidget {
  const _CircleButton({required this.icon, required this.onTap});
  final IconData icon;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      customBorder: const CircleBorder(),
      child: Container(
        width: 32,
        height: 32,
        decoration: const BoxDecoration(
          color: FunnelColors.headerFieldBg,
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: Colors.white, size: 16),
      ),
    );
  }
}

class _Stepper extends StatelessWidget {
  const _Stepper({required this.current});
  final FunnelStep current;

  static const _labels = ['Ligne', 'Départ', 'Arrivée'];

  int get _index => switch (current) {
        FunnelStep.city => 0,
        FunnelStep.line => 0,
        FunnelStep.source => 1,
        FunnelStep.dest => 2,
      };

  @override
  Widget build(BuildContext context) {
    final dots = <Widget>[];
    for (var i = 0; i < 3; i++) {
      dots.add(_Dot(i: i, index: _index));
      if (i < 2) {
        dots.add(Expanded(
          child: Container(
            height: 1.5,
            margin: const EdgeInsets.symmetric(horizontal: 6),
            color: i < _index ? Colors.white54 : Colors.white24,
          ),
        ));
      }
    }

    return Column(
      children: [
        Row(children: dots),
        const SizedBox(height: 4),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: List.generate(3, (i) {
            return Text(
              _labels[i],
              style: TextStyle(
                fontSize: 9,
                color: i <= _index
                    ? FunnelColors.onHeaderMuted
                    : FunnelColors.onHeaderFaint,
              ),
            );
          }),
        ),
      ],
    );
  }
}

class _Dot extends StatelessWidget {
  const _Dot({required this.i, required this.index});
  final int i;
  final int index;

  @override
  Widget build(BuildContext context) {
    final done = i < index;
    final current = i == index;

    final Color bg;
    final Color fg;
    if (done) {
      bg = FunnelColors.stepDoneBg;
      fg = FunnelColors.stepDoneFg;
    } else if (current) {
      bg = FunnelColors.header;
      fg = Colors.white;
    } else {
      bg = const Color(0x33FFFFFF);
      fg = FunnelColors.onHeaderFaint;
    }

    return Container(
      width: 22,
      height: 22,
      decoration: BoxDecoration(
        color: bg,
        shape: BoxShape.circle,
        border: current ? Border.all(color: Colors.white70, width: 1.5) : null,
      ),
      alignment: Alignment.center,
      child: done
          ? Icon(Icons.check, size: 12, color: fg)
          : Text(
              '${i + 1}',
              style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: fg),
            ),
    );
  }
}

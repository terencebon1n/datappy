import 'package:flutter/material.dart';
import 'package:frontend/presentation/theme/colors.dart';

class LivePill extends StatefulWidget {
  const LivePill({super.key, required this.isLive});

  final bool isLive;

  @override
  State<LivePill> createState() => _LivePillState();
}

class _LivePillState extends State<LivePill>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double>   _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1100),
    )..repeat(reverse: true);
    _anim = Tween<double>(begin: 1, end: 0.15).animate(_ctrl);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final color = widget.isLive ? TransitColors.live   : TransitColors.textMuted;
    final bg    = widget.isLive ? TransitColors.liveBg : TransitColors.surfaceHigh;
    final bdr   = widget.isLive ? TransitColors.liveBorder : TransitColors.border;
    final label = widget.isLive ? 'Temps réel' : 'En attente';

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 9, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: bdr),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          FadeTransition(
            opacity: widget.isLive ? _anim : const AlwaysStoppedAnimation(1),
            child: Container(
              width: 6, height: 6,
              decoration: BoxDecoration(color: color, shape: BoxShape.circle),
            ),
          ),
          const SizedBox(width: 5),
          Text(
            label.toUpperCase(),
            style: TextStyle(fontSize: 8, color: color, letterSpacing: 0.8),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';

/// Application animation constants and configurations
class AppAnimations {
  AppAnimations._();

  // Duration constants
  static const Duration instant = Duration.zero;
  static const Duration fast = Duration(milliseconds: 150);
  static const Duration normal = Duration(milliseconds: 250);
  static const Duration slow = Duration(milliseconds: 350);
  static const Duration slower = Duration(milliseconds: 500);
  static const Duration slowest = Duration(milliseconds: 750);

  // Page transition duration
  static const Duration pageTransition = Duration(milliseconds: 300);

  // Stagger delays
  static const Duration staggerDelay = Duration(milliseconds: 50);
  static const Duration staggerDelayLong = Duration(milliseconds: 100);

  // Curves
  static const Curve defaultCurve = Curves.easeInOutCubic;
  static const Curve easeOut = Curves.easeOut;
  static const Curve easeIn = Curves.easeIn;
  static const Curve bouncy = Curves.elasticOut;
  static const Curve smooth = Curves.easeInOutQuart;
  static const Curve decelerate = Curves.decelerate;

  /// Get stagger delay for list items
  static Duration staggerDelaFor(int index, {int maxDelay = 10}) {
    return staggerDelay * (index.clamp(0, maxDelay));
  }

  /// Get stagger delay (longer) for list items
  static Duration staggerDelayLongFor(int index, {int maxDelay = 8}) {
    return staggerDelayLong * (index.clamp(0, maxDelay));
  }
}

/// Custom slide transition for page routes
class SlidePageRoute<T> extends PageRouteBuilder<T> {
  final Widget child;
  final AxisDirection direction;

  SlidePageRoute({
    required this.child,
    this.direction = AxisDirection.right,
    super.settings,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => child,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            Offset begin;
            switch (direction) {
              case AxisDirection.up:
                begin = const Offset(0, 1);
                break;
              case AxisDirection.down:
                begin = const Offset(0, -1);
                break;
              case AxisDirection.left:
                begin = const Offset(1, 0);
                break;
              case AxisDirection.right:
                begin = const Offset(-1, 0);
                break;
            }

            final tween = Tween(begin: begin, end: Offset.zero).chain(
              CurveTween(curve: AppAnimations.defaultCurve),
            );

            return SlideTransition(
              position: animation.drive(tween),
              child: child,
            );
          },
          transitionDuration: AppAnimations.pageTransition,
        );
}

/// Custom fade transition for page routes
class FadePageRoute<T> extends PageRouteBuilder<T> {
  final Widget child;

  FadePageRoute({
    required this.child,
    super.settings,
  }) : super(
          pageBuilder: (context, animation, secondaryAnimation) => child,
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(
              opacity: animation,
              child: child,
            );
          },
          transitionDuration: AppAnimations.pageTransition,
        );
}

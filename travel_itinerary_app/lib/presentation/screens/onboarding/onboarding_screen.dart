import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:go_router/go_router.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:cached_network_image/cached_network_image.dart';

import '../../../config/routes/app_router.dart';
import '../../../theme/colors/app_colors.dart';

/// Onboarding welcome screen matching Figma design
class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        fit: StackFit.expand,
        children: [
          // Full-screen background image
          _buildBackgroundImage(),

          // Gradient overlays for readability
          _buildGradientOverlays(),

          // Content
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 28),
              child: Column(
                children: [
                  const SizedBox(height: 48),

                  // Geometric logo
                  _buildLogo()
                      .animate()
                      .fadeIn(duration: 600.ms, curve: Curves.easeOut)
                      .scale(
                        begin: const Offset(0.8, 0.8),
                        end: const Offset(1.0, 1.0),
                        duration: 600.ms,
                        curve: Curves.easeOut,
                      ),

                  const Spacer(),

                  // Heading
                  Text(
                    'Your travel companion,\nwherever you are',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 28,
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                      height: 1.25,
                    ),
                    textAlign: TextAlign.center,
                  )
                      .animate(delay: 200.ms)
                      .fadeIn(duration: 500.ms)
                      .slideY(begin: 0.15, curve: Curves.easeOut),

                  const SizedBox(height: 14),

                  // Subheading
                  Text(
                    'Personalized itineraries and real-time\ntravel support, all in one place',
                    style: GoogleFonts.plusJakartaSans(
                      fontSize: 15,
                      fontWeight: FontWeight.w400,
                      color: AppColors.textSecondary,
                      height: 1.5,
                    ),
                    textAlign: TextAlign.center,
                  )
                      .animate(delay: 350.ms)
                      .fadeIn(duration: 500.ms)
                      .slideY(begin: 0.15, curve: Curves.easeOut),

                  const SizedBox(height: 40),

                  // Primary CTA - "Create an account"
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: ElevatedButton(
                      onPressed: () => context.go(Routes.home),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        foregroundColor: AppColors.textOnPrimary,
                        elevation: 0,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(28),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '✦',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.white.withOpacity(0.5),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Create an account',
                            style: GoogleFonts.plusJakartaSans(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            '✦',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.white.withOpacity(0.5),
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                      .animate(delay: 500.ms)
                      .fadeIn(duration: 500.ms)
                      .slideY(begin: 0.2, curve: Curves.easeOut),

                  const SizedBox(height: 14),

                  // Secondary CTA - "Sign In"
                  SizedBox(
                    width: double.infinity,
                    height: 56,
                    child: OutlinedButton(
                      onPressed: () => context.go(Routes.home),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppColors.primary,
                        side: const BorderSide(
                          color: AppColors.primary,
                          width: 1.5,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(28),
                        ),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            '✦',
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.primary.withOpacity(0.4),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Sign In',
                            style: GoogleFonts.plusJakartaSans(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primary,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            '✦',
                            style: TextStyle(
                              fontSize: 10,
                              color: AppColors.primary.withOpacity(0.4),
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                      .animate(delay: 600.ms)
                      .fadeIn(duration: 500.ms)
                      .slideY(begin: 0.2, curve: Curves.easeOut),

                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBackgroundImage() {
    return CachedNetworkImage(
      imageUrl:
          'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=1200&q=80',
      fit: BoxFit.cover,
      placeholder: (context, url) => _buildFallbackGradient(),
      errorWidget: (context, url, error) => _buildFallbackGradient(),
    );
  }

  Widget _buildFallbackGradient() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFB8D4F0), // Soft blue
            Color(0xFFD4C4E8), // Lavender
            Color(0xFFE8EDF2), // Light blue-gray
          ],
        ),
      ),
    );
  }

  Widget _buildGradientOverlays() {
    return Column(
      children: [
        // Top gradient - subtle white fade for logo readability
        Expanded(
          flex: 3,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.white.withOpacity(0.7),
                  Colors.white.withOpacity(0.1),
                  Colors.transparent,
                ],
                stops: const [0.0, 0.5, 1.0],
              ),
            ),
          ),
        ),
        // Bottom gradient - white fade for text/buttons
        Expanded(
          flex: 4,
          child: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [
                  Colors.transparent,
                  Colors.white.withOpacity(0.6),
                  Colors.white.withOpacity(0.95),
                  Colors.white,
                ],
                stops: const [0.0, 0.25, 0.55, 1.0],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildLogo() {
    return SizedBox(
      width: 60,
      height: 60,
      child: CustomPaint(
        painter: _GeometricLogoPainter(),
      ),
    );
  }
}

/// Geometric abstract logo painter
class _GeometricLogoPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..style = PaintingStyle.fill;

    final cx = size.width / 2;
    final cy = size.height / 2;
    final unit = size.width / 6;

    // Top-left triangle - navy
    paint.color = AppColors.primary;
    final path1 = Path()
      ..moveTo(cx - unit * 2.5, cy - unit * 0.5)
      ..lineTo(cx - unit * 0.5, cy - unit * 2.5)
      ..lineTo(cx - unit * 0.5, cy - unit * 0.5)
      ..close();
    canvas.drawPath(path1, paint);

    // Top-right triangle - blue
    paint.color = AppColors.secondary;
    final path2 = Path()
      ..moveTo(cx + unit * 0.5, cy - unit * 2.5)
      ..lineTo(cx + unit * 2.5, cy - unit * 0.5)
      ..lineTo(cx + unit * 0.5, cy - unit * 0.5)
      ..close();
    canvas.drawPath(path2, paint);

    // Bottom-left triangle - light blue
    paint.color = AppColors.goldLight;
    final path3 = Path()
      ..moveTo(cx - unit * 2.5, cy + unit * 0.5)
      ..lineTo(cx - unit * 0.5, cy + unit * 2.5)
      ..lineTo(cx - unit * 0.5, cy + unit * 0.5)
      ..close();
    canvas.drawPath(path3, paint);

    // Bottom-right triangle - violet
    paint.color = AppColors.accent;
    final path4 = Path()
      ..moveTo(cx + unit * 0.5, cy + unit * 0.5)
      ..lineTo(cx + unit * 2.5, cy + unit * 0.5)
      ..lineTo(cx + unit * 0.5, cy + unit * 2.5)
      ..close();
    canvas.drawPath(path4, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';

class ModernButton extends StatefulWidget {
  final String text;
  final VoidCallback? onPressed;
  final IconData? icon;
  final LinearGradient? gradient;
  final Color? backgroundColor;
  final Color? textColor;
  final double? width;
  final double height;
  final EdgeInsetsGeometry? padding;
  final BorderRadius? borderRadius;
  final bool isLoading;
  final bool isOutlined;
  final double elevation;

  const ModernButton({
    super.key,
    required this.text,
    this.onPressed,
    this.icon,
    this.gradient,
    this.backgroundColor,
    this.textColor,
    this.width,
    this.height = 56,
    this.padding,
    this.borderRadius,
    this.isLoading = false,
    this.isOutlined = false,
    this.elevation = 2,
  });

  @override
  State<ModernButton> createState() => _ModernButtonState();
}

class _ModernButtonState extends State<ModernButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.95,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    return AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: GestureDetector(
            onTapDown: widget.onPressed != null && !widget.isLoading
                ? (_) => _animationController.forward()
                : null,
            onTapUp: widget.onPressed != null && !widget.isLoading
                ? (_) => _animationController.reverse()
                : null,
            onTapCancel: widget.onPressed != null && !widget.isLoading
                ? () => _animationController.reverse()
                : null,
            onTap: widget.onPressed,
            child: Container(
              width: widget.width,
              height: widget.height,
              padding: widget.padding ?? const EdgeInsets.symmetric(horizontal: 24),
              decoration: BoxDecoration(
                gradient: widget.isOutlined ? null : (widget.gradient ?? AppTheme.primaryGradient),
                color: widget.isOutlined ? Colors.transparent : widget.backgroundColor,
                borderRadius: widget.borderRadius ?? BorderRadius.circular(16),
                border: widget.isOutlined
                    ? Border.all(
                        color: widget.backgroundColor ?? theme.colorScheme.primary,
                        width: 1.5,
                      )
                    : null,
                boxShadow: widget.elevation > 0
                    ? [
                        BoxShadow(
                          color: (widget.gradient?.colors[0] ?? widget.backgroundColor ?? theme.colorScheme.primary)
                              .withOpacity(0.3),
                          blurRadius: widget.elevation * 8,
                          offset: Offset(0, widget.elevation * 2),
                        ),
                      ]
                    : null,
              ),
              child: Center(
                child: widget.isLoading
                    ? SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation<Color>(
                            widget.isOutlined
                                ? (widget.backgroundColor ?? theme.colorScheme.primary)
                                : Colors.white,
                          ),
                        ),
                      )
                    : Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          if (widget.icon != null) ...[
                            Icon(
                              widget.icon,
                              color: widget.isOutlined
                                  ? (widget.backgroundColor ?? theme.colorScheme.primary)
                                  : widget.textColor ?? Colors.white,
                              size: 20,
                            ),
                            const SizedBox(width: 8),
                          ],
                          Text(
                            widget.text,
                            style: theme.textTheme.titleMedium?.copyWith(
                              color: widget.isOutlined
                                  ? (widget.backgroundColor ?? theme.colorScheme.primary)
                                  : widget.textColor ?? Colors.white,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ],
                      ),
              ),
            ),
          ),
        );
      },
    );
  }
}

class ModernIconButton extends StatefulWidget {
  final IconData icon;
  final VoidCallback? onPressed;
  final Color? backgroundColor;
  final Color? iconColor;
  final double size;
  final double elevation;
  final String? tooltip;

  const ModernIconButton({
    super.key,
    required this.icon,
    this.onPressed,
    this.backgroundColor,
    this.iconColor,
    this.size = 48,
    this.elevation = 2,
    this.tooltip,
  });

  @override
  State<ModernIconButton> createState() => _ModernIconButtonState();
}

class _ModernIconButtonState extends State<ModernIconButton>
    with SingleTickerProviderStateMixin {
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );
    _scaleAnimation = Tween<double>(
      begin: 1.0,
      end: 0.9,
    ).animate(CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    ));
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    Widget button = AnimatedBuilder(
      animation: _scaleAnimation,
      builder: (context, child) {
        return Transform.scale(
          scale: _scaleAnimation.value,
          child: GestureDetector(
            onTapDown: widget.onPressed != null
                ? (_) => _animationController.forward()
                : null,
            onTapUp: widget.onPressed != null
                ? (_) => _animationController.reverse()
                : null,
            onTapCancel: widget.onPressed != null
                ? () => _animationController.reverse()
                : null,
            onTap: widget.onPressed,
            child: Container(
              width: widget.size,
              height: widget.size,
              decoration: BoxDecoration(
                color: widget.backgroundColor ?? theme.colorScheme.surface,
                borderRadius: BorderRadius.circular(widget.size / 2),
                boxShadow: widget.elevation > 0
                    ? [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: widget.elevation * 4,
                          offset: Offset(0, widget.elevation),
                        ),
                      ]
                    : null,
              ),
              child: Icon(
                widget.icon,
                color: widget.iconColor ?? theme.colorScheme.onSurface,
                size: widget.size * 0.5,
              ),
            ),
          ),
        );
      },
    );

    if (widget.tooltip != null) {
      return Tooltip(
        message: widget.tooltip!,
        child: button,
      );
    }

    return button;
  }
}

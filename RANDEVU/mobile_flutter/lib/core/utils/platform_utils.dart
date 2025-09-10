import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart';
import 'dart:io';

class PlatformUtils {
  static bool get isWeb => kIsWeb;
  static bool get isAndroid => !kIsWeb && Platform.isAndroid;
  static bool get isIOS => !kIsWeb && Platform.isIOS;
  static bool get isWindows => !kIsWeb && Platform.isWindows;
  static bool get isMacOS => !kIsWeb && Platform.isMacOS;
  static bool get isLinux => !kIsWeb && Platform.isLinux;
  static bool get isDesktop => isWindows || isMacOS || isLinux;
  static bool get isMobile => isAndroid || isIOS;
}

class ResponsiveLayout extends StatelessWidget {
  final Widget mobile;
  final Widget? tablet;
  final Widget? desktop;
  final Widget? web;

  const ResponsiveLayout({
    super.key,
    required this.mobile,
    this.tablet,
    this.desktop,
    this.web,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    
    // Web için özel layout
    if (PlatformUtils.isWeb) {
      if (web != null) return web!;
      
      if (screenWidth >= 1200) {
        return desktop ?? tablet ?? mobile;
      } else if (screenWidth >= 768) {
        return tablet ?? mobile;
      } else {
        return mobile;
      }
    }
    
    // Desktop için
    if (PlatformUtils.isDesktop) {
      if (screenWidth >= 1200) {
        return desktop ?? tablet ?? mobile;
      } else if (screenWidth >= 768) {
        return tablet ?? mobile;
      } else {
        return mobile;
      }
    }
    
    // Tablet boyutu kontrolü
    if (screenWidth >= 768 && screenHeight >= 1024) {
      return tablet ?? mobile;
    }
    
    // Mobil
    return mobile;
  }
}

class PlatformSpecificPadding extends StatelessWidget {
  final Widget child;
  final EdgeInsets? mobilePadding;
  final EdgeInsets? tabletPadding;
  final EdgeInsets? desktopPadding;
  final EdgeInsets? webPadding;

  const PlatformSpecificPadding({
    super.key,
    required this.child,
    this.mobilePadding,
    this.tabletPadding,
    this.desktopPadding,
    this.webPadding,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    EdgeInsets padding;
    
    if (PlatformUtils.isWeb) {
      padding = webPadding ?? 
        (screenWidth >= 1200 
          ? const EdgeInsets.all(32)
          : screenWidth >= 768 
            ? const EdgeInsets.all(24)
            : const EdgeInsets.all(16));
    } else if (PlatformUtils.isDesktop) {
      padding = desktopPadding ?? 
        (screenWidth >= 1200 
          ? const EdgeInsets.all(32)
          : const EdgeInsets.all(24));
    } else if (screenWidth >= 768) {
      padding = tabletPadding ?? const EdgeInsets.all(20);
    } else {
      padding = mobilePadding ?? const EdgeInsets.all(16);
    }
    
    return Padding(
      padding: padding,
      child: child,
    );
  }
}

class PlatformSpecificButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final IconData? icon;
  final double? width;
  final double? height;

  const PlatformSpecificButton({
    super.key,
    required this.text,
    this.onPressed,
    this.icon,
    this.width,
    this.height,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    double buttonHeight = height ?? 56;
    double? buttonWidth = width;
    
    // Platform-specific boyutlandırma
    if (PlatformUtils.isWeb) {
      if (screenWidth >= 1200) {
        buttonHeight = height ?? 64;
        buttonWidth = width ?? 200;
      } else if (screenWidth >= 768) {
        buttonHeight = height ?? 60;
        buttonWidth = width ?? 180;
      }
    } else if (PlatformUtils.isDesktop) {
      buttonHeight = height ?? 60;
      buttonWidth = width ?? 200;
    } else if (screenWidth >= 768) {
      buttonHeight = height ?? 58;
    }
    
    return SizedBox(
      width: buttonWidth,
      height: buttonHeight,
      child: ElevatedButton.icon(
        onPressed: onPressed,
        icon: icon != null ? Icon(icon) : const SizedBox.shrink(),
        label: Text(text),
        style: ElevatedButton.styleFrom(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
        ),
      ),
    );
  }
}

class PlatformSpecificCard extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final EdgeInsets? margin;
  final double? elevation;
  final BorderRadius? borderRadius;

  const PlatformSpecificCard({
    super.key,
    required this.child,
    this.padding,
    this.margin,
    this.elevation,
    this.borderRadius,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    double cardElevation = elevation ?? 2;
    EdgeInsets cardPadding = padding ?? const EdgeInsets.all(20);
    EdgeInsets cardMargin = margin ?? EdgeInsets.zero;
    BorderRadius cardBorderRadius = borderRadius ?? BorderRadius.circular(16);
    
    // Platform-specific ayarlar
    if (PlatformUtils.isWeb) {
      if (screenWidth >= 1200) {
        cardElevation = elevation ?? 4;
        cardPadding = padding ?? const EdgeInsets.all(32);
        cardMargin = margin ?? const EdgeInsets.all(16);
        cardBorderRadius = borderRadius ?? BorderRadius.circular(20);
      } else if (screenWidth >= 768) {
        cardElevation = elevation ?? 3;
        cardPadding = padding ?? const EdgeInsets.all(24);
        cardMargin = margin ?? const EdgeInsets.all(12);
        cardBorderRadius = borderRadius ?? BorderRadius.circular(18);
      }
    } else if (PlatformUtils.isDesktop) {
      cardElevation = elevation ?? 3;
      cardPadding = padding ?? const EdgeInsets.all(24);
      cardMargin = margin ?? const EdgeInsets.all(12);
      cardBorderRadius = borderRadius ?? BorderRadius.circular(18);
    } else if (screenWidth >= 768) {
      cardPadding = padding ?? const EdgeInsets.all(22);
      cardMargin = margin ?? const EdgeInsets.all(8);
    }
    
    return Container(
      margin: cardMargin,
      child: Card(
        elevation: cardElevation,
        shape: RoundedRectangleBorder(
          borderRadius: cardBorderRadius,
        ),
        child: Padding(
          padding: cardPadding,
          child: child,
        ),
      ),
    );
  }
}

class PlatformSpecificAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final List<Widget>? actions;
  final Widget? leading;
  final bool centerTitle;
  final double? elevation;

  const PlatformSpecificAppBar({
    super.key,
    required this.title,
    this.actions,
    this.leading,
    this.centerTitle = true,
    this.elevation,
  });

  @override
  Widget build(BuildContext context) {
    final screenWidth = MediaQuery.of(context).size.width;
    
    double appBarElevation = elevation ?? 0;
    double titleFontSize = 20;
    
    // Platform-specific AppBar ayarları
    if (PlatformUtils.isWeb) {
      if (screenWidth >= 1200) {
        appBarElevation = elevation ?? 1;
        titleFontSize = 24;
      } else if (screenWidth >= 768) {
        appBarElevation = elevation ?? 0.5;
        titleFontSize = 22;
      }
    } else if (PlatformUtils.isDesktop) {
      appBarElevation = elevation ?? 0.5;
      titleFontSize = 22;
    }
    
    return AppBar(
      title: Text(
        title,
        style: TextStyle(
          fontSize: titleFontSize,
          fontWeight: FontWeight.w700,
        ),
      ),
      actions: actions,
      leading: leading,
      centerTitle: centerTitle,
      elevation: appBarElevation,
      backgroundColor: Colors.transparent,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

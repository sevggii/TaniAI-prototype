# Platform-specific build configurations

## Android (android/app/build.gradle)
```gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.taniai.randevu"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    buildTypes {
        release {
            minifyEnabled true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

## iOS (ios/Runner/Info.plist)
```xml
<key>CFBundleDisplayName</key>
<string>TanıAI Randevu</string>
<key>CFBundleIdentifier</key>
<string>com.taniai.randevu</string>
<key>CFBundleVersion</key>
<string>1.0.0</string>
<key>CFBundleShortVersionString</key>
<string>1.0.0</string>
```

## Web (web/index.html)
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta content="IE=Edge" http-equiv="X-UA-Compatible">
  <meta name="description" content="TanıAI Randevu - Hızlı ve kolay randevu alma">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TanıAI Randevu</title>
  <link rel="manifest" href="manifest.json">
  <link rel="icon" type="image/png" href="favicon.png"/>
</head>
<body>
  <script src="main.dart.js" type="application/javascript"></script>
</body>
</html>
```

## Windows (windows/runner/main.cpp)
```cpp
#include <flutter/dart_project.h>
#include <flutter/flutter_view_controller.h>
#include <windows.h>

int APIENTRY wWinMain(_In_ HINSTANCE instance, _In_opt_ HINSTANCE prev,
                      _In_ wchar_t *command_line, _In_ int show_command) {
  flutter::DartProject project(L"data");
  
  std::vector<std::string> command_line_arguments =
      GetCommandLineArguments();
  
  project.set_dart_entrypoint_arguments(std::move(command_line_arguments));
  
  FlutterViewController controller(project);
  if (!controller.Create(800, 600, "TanıAI Randevu", instance, SW_SHOWDEFAULT)) {
    return EXIT_FAILURE;
  }
  
  controller.Run();
  controller.Destroy();
  return EXIT_SUCCESS;
}
```

## macOS (macos/Runner/AppDelegate.swift)
```swift
import Cocoa
import FlutterMacOS

class AppDelegate: FlutterAppDelegate {
  override func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
    return true
  }
}

@NSApplicationMain
class AppDelegate: FlutterAppDelegate {
  override func applicationDidFinishLaunching(_ notification: Notification) {
    let controller : FlutterViewController = mainFlutterWindow?.contentViewController as! FlutterViewController
    let channel = FlutterMethodChannel(name: "com.taniai.randevu/platform",
                                      binaryMessenger: controller.engine.binaryMessenger)
    channel.setMethodCallHandler({
      (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
      // Platform-specific method calls
    })
  }
}
```

## Linux (linux/main.cc)
```cpp
#include <flutter_linux/flutter_linux.h>
#include <gtk/gtk.h>

int main(int argc, char** argv) {
  gtk_init(&argc, &argv);
  
  g_autoptr(FlDartProject) project = fl_dart_project_new();
  
  g_autoptr(FlView) view = fl_view_new(project);
  
  g_autoptr(FlWindow) window = fl_window_new(view);
  fl_window_set_title(window, "TanıAI Randevu");
  fl_window_set_default_size(window, 800, 600);
  
  gtk_widget_show(GTK_WIDGET(window));
  gtk_main();
  
  return 0;
}
```

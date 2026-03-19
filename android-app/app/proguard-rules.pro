-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Firebase Analytics - prevent stripping
-keep class com.google.firebase.** { *; }
-keep class com.google.android.gms.** { *; }
-dontwarn com.google.firebase.**
-dontwarn com.google.android.gms.**

# Keep Firebase Analytics classes
-keep class com.google.firebase.analytics.** { *; }
-keep class com.google.firebase.analytics.FirebaseAnalytics { *; }
-keep class com.google.android.gms.measurement.** { *; }
-keep class com.google.android.gms.measurement.internal.** { *; }

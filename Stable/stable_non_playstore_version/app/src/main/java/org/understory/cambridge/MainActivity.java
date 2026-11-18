package org.understory.cambridge;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
import android.graphics.ImageFormat;
import android.graphics.Matrix;
import android.graphics.Rect;
import android.graphics.RectF;
import android.graphics.SurfaceTexture;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraCaptureSession;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraDevice;
import android.hardware.camera2.CameraManager;
import android.hardware.camera2.CameraMetadata;
import android.hardware.camera2.CaptureRequest;
import android.hardware.camera2.params.StreamConfigurationMap;
import android.media.Image;
import android.media.ImageReader;
import android.media.MediaCodec;
import android.media.MediaCodecInfo;
import android.media.MediaFormat;
import android.net.Uri;
import android.net.wifi.WifiManager;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.PowerManager;
import android.provider.Settings;
import android.text.format.Formatter;
import android.util.Range;
import android.util.Rational;
import android.util.Size;
import android.view.MotionEvent;
import android.view.OrientationEventListener;
import android.view.ScaleGestureDetector;
import android.view.Surface;
import android.view.TextureView;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

// [AI-BLOCK: Main Activity managing Camera2 Pro Pipeline, 4K/60fps dynamic detection, Ultra Photo, MediaCodec, and TCP RPC]
public class MainActivity extends Activity {

    private static final int PERMISSION_REQUEST_CAMERA = 101;
    private static final int STREAM_PORT = 8089;
    private static final int CONTROL_PORT = 8090;

    // Dynamic Resolution Support (including 4K if hardware supports it)
    private final List<int[]> supportedResolutions = new ArrayList<>();
    private final List<String> supportedResLabels = new ArrayList<>();
    private int currentResIndex = 0;
    private int targetWidth = 1280;
    private int targetHeight = 720;

    // Dynamic Target FPS
    private final List<Integer> supportedFpsList = new ArrayList<>();
    private int targetFps = 30;

    // View References
    private TextureView previewView;
    private View screenGlowBorder;
    private TextView badgeLive, textZoomFloat, statusIndicatorText, cameraIndicatorText, codecBadgeText;
    private TextView textEvValue, textFocusValue, statusText, streamInfoText;
    private Button badgeResolution, badgeFps, btnFloatingZoomIn, btnFloatingZoomOut;
    private Button btnModeMeetings, btnModeClass, btnModeStreaming, btnModeSnapshot;
    private Button btnModeScan, btnModeSecurity, btnModeFun, btnModePro;
    private Button btnEvMinus, btnEvPlus, btnFocusMode, btnMirror, btnRotate, btnTorch, btnScreenGlow;
    private Button btnIso, btnShutter, btnAwb, btnColorEffect, btnVirtualBg;
    private Button btnStart, btnPause, btnStop, btnSwitchCam, btnUltraPhoto, btnBackgroundLock, btnBatteryGuide, btnAbout;
    private Button btnKeepScreenOn, btnScreenDim;
    private Button btnFullscreen, btnFloatingMenu;
    private TextView btnToggleProOptions;
    private SeekBar seekbarExposure, seekbarFocus;
    private View headerBar, controlsScrollView, footerBar, layoutProOptions;

    // State Flags & Settings
    private static final int REQUEST_PICK_WALLPAPER = 1002;
    private String bgWorkload = "pc"; // "pc" (recommended) or "mobile"
    private String bgMode = "off"; // "off", "custom_image", "blur_light", "blur_heavy", "green_screen", "chroma_green"
    private String customWallpaperName = "None";
    private Uri customWallpaperUri = null;
    private boolean isKeepScreenOn = true;
    private boolean isScreenDimmed = false;
    private boolean isForegroundServiceEnabled = true;
    private boolean isBackgroundLockEnabled = true;
    private boolean isMaxResolutionSensor = false;
    private boolean isFlashSupported = false;
    private int torchState = 0; // 0=OFF, 1=Low, 2=High
    private int maxTorchLevel = 1;
    private int screenGlowState = 0;
    private static final String[] GLOW_NAMES = {"OFF", "Warm", "Daylight", "Sunset", "White"};
    private static final int[] GLOW_COLORS = {0x00000000, 0x99FFF3E0, 0x99E3F2FD, 0x99FFE082, 0xBBFFFFFF};
    private float originalScreenBrightness = -1f;

    // Pro Manual Focus & Exposure Parameters
    private boolean isAutoFocus = true;
    private float minimumFocusDistance = 0f;
    private float currentFocusDistance = 0f;
    private Range<Integer> exposureRange;
    private Rational exposureStep;
    private int currentExposureCompensation = 0;

    // Pro Manual ISO & Shutter Speed
    private Range<Integer> isoRange;
    private Range<Long> shutterRange;
    private static final int[] ISO_STEPS = {0, 100, 200, 400, 800, 1600, 3200}; // 0 = Auto
    private int isoStepIndex = 0;
    private int currentIso = 0;

    private static final long[] SHUTTER_STEPS = {0, 1000000L, 2000000L, 4000000L, 8000000L, 16666666L, 33333333L}; // 0=Auto, 1/1000s..1/30s
    private static final String[] SHUTTER_LABELS = {"Auto", "1/1000s", "1/500s", "1/250s", "1/125s", "1/60s", "1/30s"};
    private int shutterStepIndex = 0;
    private long currentShutterNs = 0L;

    // White Balance & Color Effects
    private static final int[] AWB_MODES = {
        CameraMetadata.CONTROL_AWB_MODE_AUTO,
        CameraMetadata.CONTROL_AWB_MODE_DAYLIGHT,
        CameraMetadata.CONTROL_AWB_MODE_CLOUDY_DAYLIGHT,
        CameraMetadata.CONTROL_AWB_MODE_FLUORESCENT,
        CameraMetadata.CONTROL_AWB_MODE_INCANDESCENT
    };
    private static final String[] AWB_LABELS = {"Auto", "Daylight", "Cloudy", "Fluorescent", "Tungsten"};
    private int awbIndex = 0;

    private static final int[] COLOR_EFFECTS = {
        CameraMetadata.CONTROL_EFFECT_MODE_OFF,
        CameraMetadata.CONTROL_EFFECT_MODE_MONO,
        CameraMetadata.CONTROL_EFFECT_MODE_NEGATIVE,
        CameraMetadata.CONTROL_EFFECT_MODE_SEPIA
    };
    private static final String[] EFFECT_LABELS = {"Color", "B&W Mono", "Negative", "Sepia"};
    private int effectIndex = 0;

    // Camera Hardware References
    private CameraManager cameraManager;
    private String currentCameraId;
    private int currentLensFacing = CameraCharacteristics.LENS_FACING_BACK;
    private CameraDevice cameraDevice;
    private CameraCaptureSession captureSession;
    private CaptureRequest.Builder captureRequestBuilder;

    // Background Threading
    private Handler backgroundHandler;
    private HandlerThread backgroundThread;

    // MediaCodec H.264 Video Streaming
    private MediaCodec mediaCodec;
    private Surface encoderInputSurface;
    private volatile boolean isStreaming = false;
    private volatile boolean isPaused = false;
    private volatile boolean encoderReady = false;
    private volatile boolean isMirrored = false;
    private int manualRotationAngle = 0;
    private int sensorOrientation = 90;
    private int deviceOrientation = 0;
    private OrientationEventListener orientationEventListener;

    // Ultra Photo Full Sensor High-Res Capture
    private ImageReader stillImageReader;
    private Size maxJpegSize;

    // TCP Sockets
    private ServerSocket videoServerSocket;
    private Socket activeVideoClient;
    private OutputStream videoOutputStream;
    private volatile byte[] cachedSpsPps = null;
    private ServerSocket controlServerSocket;

    // Zoom & Pinch Gestures
    private float currentZoom = 1.0f;
    private float maxZoom = 1.0f;
    private Rect sensorArraySize;
    private ScaleGestureDetector scaleGestureDetector;

    // Fullscreen Overlay State
    private boolean isFullscreenMode = false;
    private boolean isControlsOverlayVisible = true;

    private static final String POLICY_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md";
    private static final String ATTRIBUTION_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/ATTRIBUTION_AND_LICENSES.md";
    private static final String LICENSE_URL = "https://github.com/saprecar/Otter/blob/main/LICENSE";
    private static final int POLICY_VERSION = 2; // Incremented on each update to require re-consent

    // [AI-BLOCK: Active connection mode label for status bar display]
    // Values: "wifi" | "usb_tether" | "adb" | "auto"
    private String activeConnectionMode = "auto";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        checkAndEnforceConsent();

        bindViews();
        setupClickListeners();
        setupPinchToZoom();
        setupOrientationListener();

        cameraManager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
        android.content.SharedPreferences prefs = getSharedPreferences("otter_settings", Context.MODE_PRIVATE);
        isKeepScreenOn = prefs.getBoolean("keep_screen_on", true);
        applyKeepScreenOn(isKeepScreenOn);

        previewView.setSurfaceTextureListener(new TextureView.SurfaceTextureListener() {
            @Override
            public void onSurfaceTextureAvailable(@NonNull SurfaceTexture surface, int width, int height) {
                configureTransform(width, height);
                if (isStreaming && cameraDevice == null) {
                    openCamera(targetWidth, targetHeight);
                }
            }

            @Override
            public void onSurfaceTextureSizeChanged(@NonNull SurfaceTexture surface, int width, int height) {
                configureTransform(width, height);
            }

            @Override
            public boolean onSurfaceTextureDestroyed(@NonNull SurfaceTexture surface) {
                return true;
            }

            @Override
            public void onSurfaceTextureUpdated(@NonNull SurfaceTexture surface) {}
        });

        displayNetworkInfo();

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            java.util.List<String> perms = new java.util.ArrayList<>();
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                perms.add(Manifest.permission.CAMERA);
            }
            if (checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                perms.add(Manifest.permission.POST_NOTIFICATIONS);
            }
            if (!perms.isEmpty()) {
                requestPermissions(perms.toArray(new String[0]), PERMISSION_REQUEST_CAMERA);
            } else {
                setupInitialCamera();
            }
        } else {
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
                requestPermissions(new String[]{Manifest.permission.CAMERA}, PERMISSION_REQUEST_CAMERA);
            } else {
                setupInitialCamera();
            }
        }

        startControlServer();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CAMERA) {
            if (checkSelfPermission(Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED) {
                setupInitialCamera();
            } else {
                Toast.makeText(this, "Camera permission is required to stream video", Toast.LENGTH_LONG).show();
            }
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);
        if (intent != null && "ACTION_STOP_STREAM".equals(intent.getAction())) {
            stopStreaming();
        }
    }

    private void checkAndEnforceConsent() {
        android.content.SharedPreferences prefs = getSharedPreferences("otter_settings", Context.MODE_PRIVATE);
        int accepted = prefs.getInt("accepted_policy_version", -1);
        if (accepted < POLICY_VERSION) {
            AlertDialog.Builder builder = new AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert);
            builder.setTitle("Otter - Master Policies & Agreement");
            builder.setMessage(
                "Welcome to Otter!\n\n" +
                "Before using the camera and streaming features, you must review and agree to our consolidated policies:\n\n" +
                "• 100% Local Peer-to-Peer: Video is encoded locally on hardware and streamed directly to your PC. Zero developer cloud ingestion.\n" +
                "• Zero Developer Data Retention: The developer does NOT collect, store, monetize, or transmit personal data or video feeds. Because zero data is held, deletion on developer servers is not applicable.\n" +
                "• OS / Store & OEM Telemetry: Google Play Services or device manufacturers (MIUI, HyperOS, ColorOS, Funtouch OS, One UI) collect their own diagnostics as per their respective policies, outside developer control.\n" +
                "• Absolute Disclaimer of Warranties: Software provided 'AS IS' with all faults. The developer bears zero liability for local network packet interception, data loss, device heating, or software bugs.\n" +
                "• Mandatory Attribution: Any reuse or fork must prominently credit developer 'spacecar', name 'Otter', and link to https://github.com/saprecar/Otter.\n" +
                "• Governing Law & Jurisdiction: Republic of India (Information Technology Act, 2000). Exclusive jurisdiction: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).\n" +
                "• Contact: getspacecar@gmail.com (Subject: [Otter-Legal]).\n\n" +
                "You must review and accept these terms to continue."
            );
            builder.setCancelable(false);

            builder.setPositiveButton("Accept & Continue", (dialog, which) -> {
                prefs.edit().putInt("accepted_policy_version", POLICY_VERSION).apply();
                dialog.dismiss();
            });

            builder.setNegativeButton("Decline & Exit", (dialog, which) -> {
                dialog.dismiss();
                finishAffinity();
            });

            builder.setNeutralButton("View Policies", null);

            AlertDialog dialog = builder.create();
            dialog.setCanceledOnTouchOutside(false);
            dialog.show();

            Button btnNeutral = dialog.getButton(AlertDialog.BUTTON_NEUTRAL);
            if (btnNeutral != null) {
                btnNeutral.setOnClickListener(v -> showPolicyLinksDialog());
            }
        }
    }

    private void showPolicyLinksDialog() {
        String[] options = {"Consolidated Master Policy", "Attribution & Licenses", "Open Source License"};
        new AlertDialog.Builder(this, android.R.style.Theme_DeviceDefault_Dialog_Alert)
            .setTitle("Review Policies Online (Markdown)")
            .setItems(options, (d, which) -> {
                String targetUrl = POLICY_URL;
                if (which == 1) targetUrl = ATTRIBUTION_URL;
                else if (which == 2) targetUrl = LICENSE_URL;
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(targetUrl)));
                } catch (Exception e) {
                    Toast.makeText(this, "Could not open browser: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            })
            .setPositiveButton("Back", null)
            .show();
    }

    private void bindViews() {
        previewView = findViewById(R.id.previewView);
        screenGlowBorder = findViewById(R.id.screenGlowBorder);
        badgeLive = findViewById(R.id.badgeLive);
        badgeResolution = findViewById(R.id.badgeResolution);
        badgeFps = findViewById(R.id.badgeFps);
        btnFloatingZoomIn = findViewById(R.id.btnFloatingZoomIn);
        btnFloatingZoomOut = findViewById(R.id.btnFloatingZoomOut);
        textZoomFloat = findViewById(R.id.textZoomFloat);

        statusIndicatorText = findViewById(R.id.statusIndicatorText);
        cameraIndicatorText = findViewById(R.id.cameraIndicatorText);
        codecBadgeText = findViewById(R.id.codecBadgeText);

        btnModeMeetings = findViewById(R.id.btnModeMeetings);
        btnModeClass = findViewById(R.id.btnModeClass);
        btnModeStreaming = findViewById(R.id.btnModeStreaming);
        btnModeSnapshot = findViewById(R.id.btnModeSnapshot);
        btnModeScan = findViewById(R.id.btnModeScan);
        btnModeSecurity = findViewById(R.id.btnModeSecurity);
        btnModeFun = findViewById(R.id.btnModeFun);
        btnModePro = findViewById(R.id.btnModePro);

        btnToggleProOptions = findViewById(R.id.btnToggleProOptions);
        layoutProOptions = findViewById(R.id.layoutProOptions);
        btnEvMinus = findViewById(R.id.btnEvMinus);
        btnEvPlus = findViewById(R.id.btnEvPlus);
        textEvValue = findViewById(R.id.textEvValue);
        seekbarExposure = findViewById(R.id.seekbarExposure);

        btnFocusMode = findViewById(R.id.btnFocusMode);
        seekbarFocus = findViewById(R.id.seekbarFocus);
        textFocusValue = findViewById(R.id.textFocusValue);

        btnMirror = findViewById(R.id.btnMirror);
        btnRotate = findViewById(R.id.btnRotate);
        btnTorch = findViewById(R.id.btnTorch);
        btnScreenGlow = findViewById(R.id.btnScreenGlow);

        btnIso = findViewById(R.id.btnIso);
        btnShutter = findViewById(R.id.btnShutter);
        btnAwb = findViewById(R.id.btnAwb);
        btnColorEffect = findViewById(R.id.btnColorEffect);
        btnVirtualBg = findViewById(R.id.btnVirtualBg);

        btnStart = findViewById(R.id.btnStart);
        btnPause = findViewById(R.id.btnPause);
        btnStop = findViewById(R.id.btnStop);
        btnSwitchCam = findViewById(R.id.btnSwitchCam);
        btnUltraPhoto = findViewById(R.id.btnUltraPhoto);
        btnBackgroundLock = findViewById(R.id.btnBackgroundLock);
        btnBatteryGuide = findViewById(R.id.btnBatteryGuide);
        btnKeepScreenOn = findViewById(R.id.btnKeepScreenOn);
        btnScreenDim = findViewById(R.id.btnScreenDim);
        btnAbout = findViewById(R.id.btnAbout);

        btnFullscreen = findViewById(R.id.btnFullscreen);
        btnFloatingMenu = findViewById(R.id.btnFloatingMenu);
        headerBar = findViewById(R.id.headerBar);
        controlsScrollView = findViewById(R.id.controlsScrollView);
        footerBar = findViewById(R.id.footerBar);
        statusText = findViewById(R.id.statusText);
        streamInfoText = findViewById(R.id.streamInfoText);
    }

    private void setupClickListeners() {
        btnStart.setOnClickListener(v -> startStreaming());
        btnPause.setOnClickListener(v -> togglePause());
        btnStop.setOnClickListener(v -> stopStreaming());
        btnSwitchCam.setOnClickListener(v -> switchCamera());
        btnUltraPhoto.setOnClickListener(v -> takeUltraPhoto());

        btnMirror.setOnClickListener(v -> toggleMirror());
        btnRotate.setOnClickListener(v -> cycleRotation());
        btnTorch.setOnClickListener(v -> cycleTorch());
        btnScreenGlow.setOnClickListener(v -> cycleScreenGlow());

        badgeResolution.setOnClickListener(v -> cycleResolution());
        badgeFps.setOnClickListener(v -> cycleTargetFps());

        btnFloatingZoomIn.setOnClickListener(v -> zoomStep(0.2f));
        btnFloatingZoomOut.setOnClickListener(v -> zoomStep(-0.2f));

        btnEvMinus.setOnClickListener(v -> evStep(-1));
        btnEvPlus.setOnClickListener(v -> evStep(1));
        btnFocusMode.setOnClickListener(v -> toggleFocusMode());

        btnToggleProOptions.setOnClickListener(v -> {
            boolean visible = layoutProOptions.getVisibility() == View.VISIBLE;
            layoutProOptions.setVisibility(visible ? View.GONE : View.VISIBLE);
            btnToggleProOptions.setText(visible ? "More Options ▾" : "Hide Options ▴");
        });

        btnIso.setOnClickListener(v -> cycleIso());
        btnShutter.setOnClickListener(v -> cycleShutter());
        btnAwb.setOnClickListener(v -> cycleAwb());
        btnColorEffect.setOnClickListener(v -> cycleColorEffect());
        btnVirtualBg.setOnClickListener(v -> showVirtualBgDialog());

        // Quick Modes Presets
        btnModeMeetings.setOnClickListener(v -> applyQuickMode("meetings"));
        btnModeClass.setOnClickListener(v -> applyQuickMode("class"));
        btnModeStreaming.setOnClickListener(v -> applyQuickMode("streaming"));
        btnModeSnapshot.setOnClickListener(v -> applyQuickMode("snapshot"));
        btnModeScan.setOnClickListener(v -> applyQuickMode("scan"));
        btnModeSecurity.setOnClickListener(v -> applyQuickMode("security"));
        btnModeFun.setOnClickListener(v -> applyQuickMode("fun"));
        btnModePro.setOnClickListener(v -> applyQuickMode("pro"));

        btnBackgroundLock.setOnClickListener(v -> toggleBackgroundLock());
        btnBatteryGuide.setOnClickListener(v -> showBatteryGuideDialog());
        btnKeepScreenOn.setOnClickListener(v -> toggleKeepScreenOn());
        btnScreenDim.setOnClickListener(v -> toggleScreenDim());
        btnAbout.setOnClickListener(v -> startActivity(new Intent(this, AboutActivity.class)));

        btnFullscreen.setOnClickListener(v -> toggleFullscreen());
        btnFloatingMenu.setOnClickListener(v -> toggleControlsOverlay());

        // SeekBars
        seekbarExposure.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (fromUser && exposureRange != null) {
                    currentExposureCompensation = exposureRange.getLower() + progress;
                    updateExposureDisplay();
                    applyCaptureRequestParameters();
                }
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });

        seekbarFocus.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                if (fromUser && !isAutoFocus && minimumFocusDistance > 0) {
                    currentFocusDistance = (progress / 100f) * minimumFocusDistance;
                    updateFocusDisplay();
                    applyCaptureRequestParameters();
                }
            }
            @Override public void onStartTrackingTouch(SeekBar seekBar) {}
            @Override public void onStopTrackingTouch(SeekBar seekBar) {}
        });
    }

    private void setupPinchToZoom() {
        scaleGestureDetector = new ScaleGestureDetector(this, new ScaleGestureDetector.SimpleOnScaleGestureListener() {
            @Override
            public boolean onScale(ScaleGestureDetector detector) {
                float factor = detector.getScaleFactor();
                float delta = (factor - 1.0f) * 2.0f;
                zoomStep(delta);
                return true;
            }
        });

        previewView.setOnTouchListener((v, event) -> {
            scaleGestureDetector.onTouchEvent(event);
            return true;
        });
    }

    // [AI-BLOCK: Fullscreen and Floating Overlay Toggle (Reference Image 2)]
    private void toggleFullscreen() {
        isFullscreenMode = !isFullscreenMode;
        if (isFullscreenMode) {
            headerBar.setVisibility(View.GONE);
            controlsScrollView.setVisibility(View.GONE);
            footerBar.setVisibility(View.GONE);
            btnFloatingMenu.setVisibility(View.VISIBLE);
            btnFullscreen.setText("⊡");
        } else {
            headerBar.setVisibility(View.VISIBLE);
            controlsScrollView.setVisibility(View.VISIBLE);
            footerBar.setVisibility(View.VISIBLE);
            btnFloatingMenu.setVisibility(View.GONE);
            btnFullscreen.setText("⛶");
        }
    }

    private void toggleControlsOverlay() {
        isControlsOverlayVisible = !isControlsOverlayVisible;
        controlsScrollView.setVisibility(isControlsOverlayVisible ? View.VISIBLE : View.GONE);
    }

    // [AI-BLOCK: Dynamic Hardware Detection (4K resolutions, FPS ranges, and max sensor capture)]
    private void setupInitialCamera() {
        try {
            String defaultId = findCameraIdForFacing(CameraCharacteristics.LENS_FACING_BACK);
            if (defaultId == null && cameraManager.getCameraIdList().length > 0) {
                defaultId = cameraManager.getCameraIdList()[0];
            }
            if (defaultId != null) {
                currentCameraId = defaultId;
                inspectCameraCapabilities(currentCameraId);
            }
            updateCameraIndicator();
            updateTorchButtonState();
        } catch (CameraAccessException e) {
            statusText.setText("Error reading cameras: " + e.getMessage());
        }
    }

    private void inspectCameraCapabilities(String cameraId) throws CameraAccessException {
        CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(cameraId);
        Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
        if (facing != null) currentLensFacing = facing;
        Integer sOrient = characteristics.get(CameraCharacteristics.SENSOR_ORIENTATION);
        if (sOrient != null) sensorOrientation = sOrient;

        // Dynamic Resolutions (Check up to 4K 3840x2160)
        supportedResolutions.clear();
        supportedResLabels.clear();
        StreamConfigurationMap map = characteristics.get(CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP);
        if (map != null) {
            Size[] sizes = map.getOutputSizes(SurfaceTexture.class);
            if (sizes != null) {
                // Filter and sort standard 16:9 and 4:3 resolutions
                int[][] candidateRes = {
                    {3840, 2160}, // 4K UHD
                    {2560, 1440}, // 1440p QHD
                    {1920, 1080}, // 1080p FHD
                    {1280, 720},  // 720p HD
                    {640, 480},   // 480p SD
                    {640, 360}    // 360p LD
                };
                for (int[] cand : candidateRes) {
                    for (Size s : sizes) {
                        if (s.getWidth() == cand[0] && s.getHeight() == cand[1]) {
                            supportedResolutions.add(cand);
                            String lbl = (cand[0] >= 3840) ? "4K" : ((cand[0] >= 2560) ? "1440p" : (cand[1] + "p"));
                            supportedResLabels.add(lbl);
                            break;
                        }
                    }
                }
            }

            // Max JPEG Sensor Size for Ultra Photo (64MP / 50MP / 48MP / 16MP etc.)
            Size[] jpegSizes = map.getOutputSizes(ImageFormat.JPEG);
            if (jpegSizes != null && jpegSizes.length > 0) {
                maxJpegSize = Collections.max(Arrays.asList(jpegSizes), (o1, o2) ->
                    Long.compare((long) o1.getWidth() * o1.getHeight(), (long) o2.getWidth() * o2.getHeight()));
            }

            // High-Resolution Sensor Detection (Android 12+ / API 31+)
            isMaxResolutionSensor = false;
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                try {
                    StreamConfigurationMap maxMap = characteristics.get(
                            CameraCharacteristics.SCALER_STREAM_CONFIGURATION_MAP_MAXIMUM_RESOLUTION);
                    if (maxMap != null) {
                        Size[] highResSizes = maxMap.getOutputSizes(ImageFormat.JPEG);
                        if (highResSizes != null && highResSizes.length > 0) {
                            Size maxHighRes = Collections.max(Arrays.asList(highResSizes), (o1, o2) ->
                                Long.compare((long) o1.getWidth() * o1.getHeight(), (long) o2.getWidth() * o2.getHeight()));
                            if (maxHighRes != null && (maxJpegSize == null ||
                                    ((long) maxHighRes.getWidth() * maxHighRes.getHeight() > (long) maxJpegSize.getWidth() * maxJpegSize.getHeight()))) {
                                maxJpegSize = maxHighRes;
                                isMaxResolutionSensor = true;
                            }
                        }
                    }
                } catch (Exception ignored) {}
            }

            // Detect Physical Hardware Sensor Megapixels (e.g. 64MP on iQOO Z7 / 50MP on Poco F6)
            Size physicalSensorSize = characteristics.get(CameraCharacteristics.SENSOR_INFO_PIXEL_ARRAY_SIZE);
            float physicalMp = 0f;
            if (physicalSensorSize != null) {
                physicalMp = (physicalSensorSize.getWidth() * physicalSensorSize.getHeight()) / 1_000_000f;
            }

            if (btnUltraPhoto != null && maxJpegSize != null) {
                float streamMp = (maxJpegSize.getWidth() * maxJpegSize.getHeight()) / 1_000_000f;
                if (isMaxResolutionSensor || streamMp >= 32f) {
                    btnUltraPhoto.setText(String.format(java.util.Locale.US, "★ Ultra (%.0fMP Full)", streamMp));
                } else if (physicalMp >= 40f) {
                    btnUltraPhoto.setText(String.format(java.util.Locale.US, "★ Ultra (%.0fMP/%.0fMP Bin)", physicalMp, streamMp));
                } else {
                    btnUltraPhoto.setText(String.format(java.util.Locale.US, "★ Ultra Photo (%.0fMP)", streamMp));
                }
            }
        }

        if (supportedResolutions.isEmpty()) {
            supportedResolutions.add(new int[]{1280, 720});
            supportedResLabels.add("720p");
        }

        // Set default to 720p or closest
        currentResIndex = 0;
        for (int i = 0; i < supportedResolutions.size(); i++) {
            if (supportedResolutions.get(i)[0] == 1280 && supportedResolutions.get(i)[1] == 720) {
                currentResIndex = i;
                break;
            }
        }
        targetWidth = supportedResolutions.get(currentResIndex)[0];
        targetHeight = supportedResolutions.get(currentResIndex)[1];
        badgeResolution.setText(supportedResLabels.get(currentResIndex));

        // Supported FPS ranges
        supportedFpsList.clear();
        Range<Integer>[] fpsRanges = characteristics.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES);
        if (fpsRanges != null) {
            for (Range<Integer> r : fpsRanges) {
                if (r.getUpper() >= 15 && !supportedFpsList.contains(r.getUpper())) {
                    supportedFpsList.add(r.getUpper());
                }
            }
            Collections.sort(supportedFpsList);
        }
        if (supportedFpsList.isEmpty()) supportedFpsList.add(30);
        if (!supportedFpsList.contains(targetFps)) {
            targetFps = supportedFpsList.contains(30) ? 30 : supportedFpsList.get(supportedFpsList.size() - 1);
        }
        badgeFps.setText(targetFps + " FPS");

        // Focus & Exposure
        Float max = characteristics.get(CameraCharacteristics.SCALER_AVAILABLE_MAX_DIGITAL_ZOOM);
        maxZoom = (max != null) ? max : 1.0f;
        sensorArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE);
        currentZoom = 1.0f;

        Float minFocus = characteristics.get(CameraCharacteristics.LENS_INFO_MINIMUM_FOCUS_DISTANCE);
        minimumFocusDistance = (minFocus != null) ? minFocus : 0f;
        exposureRange = characteristics.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_RANGE);
        exposureStep = characteristics.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_STEP);
        currentExposureCompensation = 0;

        if (exposureRange != null) {
            seekbarExposure.setMax(exposureRange.getUpper() - exposureRange.getLower());
            seekbarExposure.setProgress(-exposureRange.getLower());
        }

        isoRange = characteristics.get(CameraCharacteristics.SENSOR_INFO_SENSITIVITY_RANGE);
        shutterRange = characteristics.get(CameraCharacteristics.SENSOR_INFO_EXPOSURE_TIME_RANGE);

        checkFlashSupport(characteristics);
        updateExposureDisplay();
        updateFocusDisplay();
        updateZoomDisplay();
    }

    private void updateExposureDisplay() {
        if (textEvValue != null) {
            float evVal = (exposureStep != null) ? currentExposureCompensation * exposureStep.floatValue() : currentExposureCompensation;
            textEvValue.setText(String.format(java.util.Locale.US, "%+.1f", evVal));
        }
    }

    private void updateFocusDisplay() {
        if (btnFocusMode != null) {
            btnFocusMode.setText(isAutoFocus ? "AF: Auto" : "AF: Manual");
            btnFocusMode.setTextColor(isAutoFocus ? 0xFF238636 : 0xFF1F6FEB);
        }
        if (textFocusValue != null) {
            if (isAutoFocus) {
                textFocusValue.setText("Auto");
            } else if (currentFocusDistance <= 0.05f) {
                textFocusValue.setText("Inf");
            } else if (minimumFocusDistance > 0 && currentFocusDistance >= minimumFocusDistance * 0.8f) {
                textFocusValue.setText("Macro");
            } else {
                textFocusValue.setText(String.format(java.util.Locale.US, "%.1fm", 1.0f / Math.max(0.1f, currentFocusDistance)));
            }
        }
    }

    private void updateZoomDisplay() {
        if (textZoomFloat != null) {
            textZoomFloat.setText(String.format(java.util.Locale.US, "%.1fx", currentZoom));
        }
    }

    // [AI-BLOCK: Pro Manual Camera Steppers & Modes]
    private void evStep(int stepDelta) {
        if (exposureRange == null) return;
        currentExposureCompensation = Math.max(exposureRange.getLower(), Math.min(exposureRange.getUpper(), currentExposureCompensation + stepDelta));
        seekbarExposure.setProgress(currentExposureCompensation - exposureRange.getLower());
        updateExposureDisplay();
        applyCaptureRequestParameters();
    }

    private void toggleFocusMode() {
        isAutoFocus = !isAutoFocus;
        if (isAutoFocus) currentFocusDistance = 0f;
        updateFocusDisplay();
        applyCaptureRequestParameters();
    }

    private void zoomStep(float delta) {
        currentZoom = Math.max(1.0f, Math.min(maxZoom, currentZoom + delta));
        updateZoomDisplay();
        applyCaptureRequestParameters();
    }

    private void cycleIso() {
        isoStepIndex = (isoStepIndex + 1) % ISO_STEPS.length;
        currentIso = ISO_STEPS[isoStepIndex];
        btnIso.setText("ISO: " + (currentIso == 0 ? "Auto" : String.valueOf(currentIso)));
        applyCaptureRequestParameters();
    }

    private void cycleShutter() {
        shutterStepIndex = (shutterStepIndex + 1) % SHUTTER_STEPS.length;
        currentShutterNs = SHUTTER_STEPS[shutterStepIndex];
        btnShutter.setText("Shutter: " + SHUTTER_LABELS[shutterStepIndex]);
        applyCaptureRequestParameters();
    }

    private void cycleAwb() {
        awbIndex = (awbIndex + 1) % AWB_MODES.length;
        btnAwb.setText("WB: " + AWB_LABELS[awbIndex]);
        applyCaptureRequestParameters();
    }

    private void cycleColorEffect() {
        effectIndex = (effectIndex + 1) % COLOR_EFFECTS.length;
        btnColorEffect.setText("FX: " + EFFECT_LABELS[effectIndex]);
        applyCaptureRequestParameters();
    }

    private void cycleResolution() {
        if (supportedResolutions.isEmpty()) return;
        currentResIndex = (currentResIndex + 1) % supportedResolutions.size();
        targetWidth = supportedResolutions.get(currentResIndex)[0];
        targetHeight = supportedResolutions.get(currentResIndex)[1];
        badgeResolution.setText(supportedResLabels.get(currentResIndex));
        if (isStreaming) {
            closeCamera();
            openCamera(targetWidth, targetHeight);
        }
    }

    private void cycleTargetFps() {
        if (supportedFpsList.isEmpty()) return;
        int idx = supportedFpsList.indexOf(targetFps);
        idx = (idx + 1) % supportedFpsList.size();
        targetFps = supportedFpsList.get(idx);
        badgeFps.setText(targetFps + " FPS");
        if (isStreaming) {
            try {
                setupEncoder(targetWidth, targetHeight);
            } catch (Exception ignored) {}
        }
        applyCaptureRequestParameters();
        Toast.makeText(this, "Target Framerate: " + targetFps + " FPS", Toast.LENGTH_SHORT).show();
    }

    // [AI-BLOCK: Quick Modes Purpose Presets]
    private void applyQuickMode(String mode) {
        switch (mode.toLowerCase()) {
            case "meetings":
                isAutoFocus = true;
                currentIso = 0;
                currentShutterNs = 0L;
                awbIndex = 0; // Auto
                effectIndex = 0; // Color
                currentExposureCompensation = 0;
                targetFps = 30;
                break;
            case "class":
                isAutoFocus = true;
                awbIndex = 1; // Daylight
                evStep(1);
                applyScreenGlowDirect(2); // Daylight White Glow
                break;
            case "streaming":
                isAutoFocus = true;
                currentIso = 0;
                targetFps = supportedFpsList.contains(60) ? 60 : 30;
                effectIndex = 0;
                break;
            case "snapshot":
                takeUltraPhoto();
                return;
            case "scan":
                isAutoFocus = false;
                currentFocusDistance = minimumFocusDistance; // Macro focus
                evStep(2);
                torchState = 2; // High torch
                applyTorchMode();
                break;
            case "security":
                isBackgroundLockEnabled = true;
                targetFps = 15;
                applyScreenGlowDirect(0); // Screen off
                break;
            case "fun":
                isMirrored = true;
                applyScreenGlowDirect(1); // Warm Glow
                effectIndex = 3; // Sepia or Mono
                break;
            case "pro":
                layoutProOptions.setVisibility(View.VISIBLE);
                btnToggleProOptions.setText("Hide Options ▴");
                break;
        }

        updateFocusDisplay();
        updateExposureDisplay();
        badgeFps.setText(targetFps + " FPS");
        btnIso.setText("ISO: " + (currentIso == 0 ? "Auto" : String.valueOf(currentIso)));
        btnShutter.setText("Shutter: " + SHUTTER_LABELS[shutterStepIndex]);
        btnAwb.setText("WB: " + AWB_LABELS[awbIndex]);
        btnColorEffect.setText("FX: " + EFFECT_LABELS[effectIndex]);
        applyCaptureRequestParameters();
        Toast.makeText(this, "Mode: " + mode.toUpperCase(), Toast.LENGTH_SHORT).show();
    }

    private void applyScreenGlowDirect(int state) {
        screenGlowState = state % GLOW_NAMES.length;
        if (btnScreenGlow != null) btnScreenGlow.setText("Glow: " + GLOW_NAMES[screenGlowState]);
        if (screenGlowBorder != null) screenGlowBorder.setBackgroundColor(GLOW_COLORS[screenGlowState]);
    }

    private void ensureStillImageReader() {
        if (stillImageReader == null && maxJpegSize != null) {
            stillImageReader = ImageReader.newInstance(maxJpegSize.getWidth(), maxJpegSize.getHeight(), ImageFormat.JPEG, 2);
            stillImageReader.setOnImageAvailableListener(reader -> {
                Image image = null;
                try {
                    image = reader.acquireLatestImage();
                    if (image != null) {
                        ByteBuffer buffer = image.getPlanes()[0].getBuffer();
                        byte[] bytes = new byte[buffer.remaining()];
                        buffer.get(bytes);

                        File dir = new File(getExternalFilesDir(Environment.DIRECTORY_PICTURES), "Otter_Ultra");
                        if (!dir.exists()) dir.mkdirs();
                        File file = new File(dir, "ULTRA_" + System.currentTimeMillis() + ".jpg");
                        try (FileOutputStream fos = new FileOutputStream(file)) {
                            fos.write(bytes);
                        }
                        runOnUiThread(() -> {
                            float mp = (maxJpegSize.getWidth() * maxJpegSize.getHeight()) / 1_000_000f;
                            Toast.makeText(this, String.format(java.util.Locale.US, "★ Ultra Photo Saved (%.1fMP): %dx%d", mp, maxJpegSize.getWidth(), maxJpegSize.getHeight()), Toast.LENGTH_LONG).show();
                            statusText.setText("★ Saved: " + file.getName());
                        });
                    }
                } catch (Exception ex) {
                    runOnUiThread(() -> Toast.makeText(this, "Save error: " + ex.getMessage(), Toast.LENGTH_SHORT).show());
                } finally {
                    if (image != null) image.close();
                }
            }, backgroundHandler);
        }
    }

    // [AI-BLOCK: Ultra Photo High-Res Snapshot Pipeline]
    private void takeUltraPhoto() {
        if (previewView == null || !previewView.isAvailable()) {
            Toast.makeText(this, "Camera not ready for Ultra Photo", Toast.LENGTH_SHORT).show();
            return;
        }

        try {
            android.graphics.Bitmap bitmap = previewView.getBitmap();
            if (bitmap != null) {
                File dir = new File(getExternalFilesDir(Environment.DIRECTORY_PICTURES), "Otter_Ultra");
                if (!dir.exists()) dir.mkdirs();
                File file = new File(dir, "ULTRA_" + System.currentTimeMillis() + ".jpg");
                try (FileOutputStream fos = new FileOutputStream(file)) {
                    bitmap.compress(android.graphics.Bitmap.CompressFormat.JPEG, 95, fos);
                }
                float mp = (bitmap.getWidth() * bitmap.getHeight()) / 1_000_000f;
                Toast.makeText(this, String.format(java.util.Locale.US, "Photo Saved (%.1fMP %dx%d)", mp, bitmap.getWidth(), bitmap.getHeight()), Toast.LENGTH_LONG).show();
                statusText.setText("Photo: " + file.getName());
            }
        } catch (Exception e) {
            Toast.makeText(this, "Ultra Photo failed: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private Range<Integer> getBestFpsRange(int desiredFps) {
        if (currentCameraId == null) return new Range<>(desiredFps, desiredFps);
        try {
            CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(currentCameraId);
            Range<Integer>[] fpsRanges = characteristics.get(CameraCharacteristics.CONTROL_AE_AVAILABLE_TARGET_FPS_RANGES);
            if (fpsRanges == null || fpsRanges.length == 0) return new Range<>(desiredFps, desiredFps);

            Range<Integer> best = null;
            for (Range<Integer> r : fpsRanges) {
                if (r.getLower() == desiredFps && r.getUpper() == desiredFps) {
                    return r;
                }
            }
            for (Range<Integer> r : fpsRanges) {
                if (r.getUpper() == desiredFps) {
                    if (best == null || r.getLower() > best.getLower()) {
                        best = r;
                    }
                }
            }
            if (best == null) {
                for (Range<Integer> r : fpsRanges) {
                    if (r.contains(desiredFps)) {
                        best = r;
                        break;
                    }
                }
            }
            return best != null ? best : fpsRanges[0];
        } catch (Exception e) {
            return new Range<>(desiredFps, desiredFps);
        }
    }

    // [AI-BLOCK: Camera2 Session Creation & Parameter Application]
    private void applyCaptureRequestParameters() {
        if (captureRequestBuilder == null || captureSession == null || backgroundHandler == null) return;
        try {
            applyZoom(captureRequestBuilder);

            if (isAutoFocus) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
            } else {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF);
                captureRequestBuilder.set(CaptureRequest.LENS_FOCUS_DISTANCE, currentFocusDistance);
            }

            // ISO and Shutter Speed (Auto vs Manual)
            if (currentIso > 0 || currentShutterNs > 0) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_OFF);
                if (currentIso > 0) captureRequestBuilder.set(CaptureRequest.SENSOR_SENSITIVITY, currentIso);
                if (currentShutterNs > 0) captureRequestBuilder.set(CaptureRequest.SENSOR_EXPOSURE_TIME, currentShutterNs);
            } else {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AE_MODE, CaptureRequest.CONTROL_AE_MODE_ON);
                if (exposureRange != null) {
                    captureRequestBuilder.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, currentExposureCompensation);
                }
            }

            // AWB & Color Effect
            captureRequestBuilder.set(CaptureRequest.CONTROL_AWB_MODE, AWB_MODES[awbIndex]);
            captureRequestBuilder.set(CaptureRequest.CONTROL_EFFECT_MODE, COLOR_EFFECTS[effectIndex]);

            // Flash Torch
            if (isFlashSupported && torchState > 0) {
                captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_TORCH);
            } else {
                captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF);
            }

            // Target FPS
            Range<Integer> bestFps = getBestFpsRange(targetFps);
            if (bestFps != null) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AE_TARGET_FPS_RANGE, bestFps);
            }

            captureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
        } catch (Exception ignored) {}
    }

    private void openCamera(int width, int height) {
        startBackgroundThread();
        try {
            if (currentCameraId == null) return;
            if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) return;

            cameraManager.openCamera(currentCameraId, new CameraDevice.StateCallback() {
                @Override
                public void onOpened(@NonNull CameraDevice camera) {
                    cameraDevice = camera;
                    startPreviewAndEncoding(width, height);
                }

                @Override
                public void onDisconnected(@NonNull CameraDevice camera) {
                    camera.close();
                    cameraDevice = null;
                }

                @Override
                public void onError(@NonNull CameraDevice camera, int error) {
                    camera.close();
                    cameraDevice = null;
                    runOnUiThread(() -> statusText.setText("Camera Error: " + error));
                }
            }, backgroundHandler);
        } catch (CameraAccessException e) {
            runOnUiThread(() -> statusText.setText("Failed to open camera: " + e.getMessage()));
        }
    }

    private void startPreviewAndEncoding(int width, int height) {
        try {
            if (previewView == null || !previewView.isAvailable()) return;
            SurfaceTexture texture = previewView.getSurfaceTexture();
            if (texture == null) return;
            texture.setDefaultBufferSize(width, height);
            Surface previewSurface = new Surface(texture);

            if (mediaCodec == null || encoderInputSurface == null) {
                setupEncoder(width, height);
            }

            captureRequestBuilder = cameraDevice.createCaptureRequest(CameraDevice.TEMPLATE_RECORD);
            captureRequestBuilder.addTarget(previewSurface);
            captureRequestBuilder.addTarget(encoderInputSurface);

            List<Surface> targets = new ArrayList<>();
            targets.add(previewSurface);
            targets.add(encoderInputSurface);

            cameraDevice.createCaptureSession(targets, new CameraCaptureSession.StateCallback() {
                @Override
                public void onConfigured(@NonNull CameraCaptureSession session) {
                    if (cameraDevice == null) return;
                    captureSession = session;
                    applyCaptureRequestParameters();
                    runOnUiThread(() -> statusText.setText("● Otter: Streaming Active"));
                }

                @Override
                public void onConfigureFailed(@NonNull CameraCaptureSession session) {
                    runOnUiThread(() -> statusText.setText("Capture configuration failed"));
                }
            }, backgroundHandler);

        } catch (Exception e) {
            runOnUiThread(() -> statusText.setText("Pipeline Error: " + e.getMessage()));
        }
    }

    // [AI-BLOCK: Hardware H.264 Encoder with In-Band Parameter Sets]
    private synchronized void setupEncoder(int width, int height) throws Exception {
        stopEncoder();
        cachedSpsPps = null;
        MediaFormat format = MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC, width, height);
        format.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface);
        int baseBitrate = (width >= 3840) ? 18000000 : (width >= 1920 ? (targetFps >= 60 ? 8000000 : 6000000) : (targetFps >= 60 ? 5000000 : 3500000));
        format.setInteger(MediaFormat.KEY_BIT_RATE, baseBitrate);
        format.setInteger(MediaFormat.KEY_FRAME_RATE, targetFps);
        format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 1);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            format.setInteger(MediaFormat.KEY_PREPEND_HEADER_TO_SYNC_FRAMES, 1);
        }

        mediaCodec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC);
        mediaCodec.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);
        encoderInputSurface = mediaCodec.createInputSurface();
        mediaCodec.start();
        encoderReady = true;
    }

    private void requestSyncFrame() {
        if (mediaCodec != null && encoderReady) {
            try {
                android.os.Bundle syncBundle = new android.os.Bundle();
                syncBundle.putInt(MediaCodec.PARAMETER_KEY_REQUEST_SYNC_FRAME, 0);
                mediaCodec.setParameters(syncBundle);
            } catch (Exception ignored) {}
        }
    }

    private synchronized void stopEncoder() {
        encoderReady = false;
        if (mediaCodec != null) {
            try {
                mediaCodec.stop();
                mediaCodec.release();
            } catch (Exception ignored) {}
            mediaCodec = null;
        }
        if (encoderInputSurface != null) {
            try {
                encoderInputSurface.release();
            } catch (Exception ignored) {}
            encoderInputSurface = null;
        }
    }

    private void startStreaming() {
        if (isStreaming) return;
        isStreaming = true;
        isPaused = false;
        btnStart.setEnabled(false);
        btnPause.setEnabled(true);
        btnStop.setEnabled(true);
        statusText.setText("● Otter: Starting Stream...");

        if (isForegroundServiceEnabled) {
            startBackgroundService();
        }
        openCamera(targetWidth, targetHeight);
        startVideoServer();
        startEncodingLoop();
    }

    private void stopStreaming() {
        if (!isStreaming) return;
        isStreaming = false;
        isPaused = false;
        btnStart.setEnabled(true);
        btnPause.setEnabled(false);
        btnStop.setEnabled(false);
        statusText.setText("● Otter: Stream Stopped");

        stopBackgroundService();
        closeCamera();
        stopVideoServer();
    }

    private void togglePause() {
        isPaused = !isPaused;
        btnPause.setText(isPaused ? "Resume" : "Pause");
        statusText.setText(isPaused ? "● Otter: Stream Paused" : "● Otter: Streaming Active");
        if (isStreaming) {
            updateServiceNotification();
        }
    }

    private void switchCamera() {
        try {
            int nextFacing = (currentLensFacing == CameraCharacteristics.LENS_FACING_BACK)
                    ? CameraCharacteristics.LENS_FACING_FRONT
                    : CameraCharacteristics.LENS_FACING_BACK;
            String nextId = findCameraIdForFacing(nextFacing);
            if (nextId != null) {
                currentCameraId = nextId;
                currentLensFacing = nextFacing;
                updateCameraIndicator();

                if (currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) {
                    isFlashSupported = false;
                    torchState = 0;
                    updateTorchButtonState();
                }

                if (isStreaming) {
                    closeCamera();
                    openCamera(targetWidth, targetHeight);
                } else {
                    inspectCameraCapabilities(currentCameraId);
                }
            }
        } catch (Exception e) {
            statusText.setText("Switch error: " + e.getMessage());
        }
    }

    private void toggleMirror() {
        isMirrored = !isMirrored;
        btnMirror.setText("Flip: " + (isMirrored ? "ON" : "OFF"));
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    private void cycleRotation() {
        manualRotationAngle = (manualRotationAngle + 90) % 360;
        btnRotate.setText("Rotate: " + manualRotationAngle + "°");
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    private void checkFlashSupport(CameraCharacteristics characteristics) {
        Boolean hasFlash = characteristics.get(CameraCharacteristics.FLASH_INFO_AVAILABLE);
        isFlashSupported = (hasFlash != null && hasFlash);
        maxTorchLevel = 1;
        if (isFlashSupported && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            Integer maxLevel = characteristics.get(CameraCharacteristics.FLASH_INFO_STRENGTH_MAXIMUM_LEVEL);
            if (maxLevel != null && maxLevel > 1) maxTorchLevel = maxLevel;
        }
        if (!isFlashSupported) torchState = 0;
        runOnUiThread(this::updateTorchButtonState);
    }

    private void updateTorchButtonState() {
        if (btnTorch == null) return;
        if (!isFlashSupported) {
            btnTorch.setText("Torch: N/A");
            btnTorch.setEnabled(false);
            btnTorch.setAlpha(0.5f);
        } else {
            btnTorch.setEnabled(true);
            btnTorch.setAlpha(1.0f);
            btnTorch.setText(torchState > 0 ? "Torch: ON" : "Torch: OFF");
        }
    }

    private void cycleTorch() {
        if (!isFlashSupported) return;
        torchState = (torchState == 0) ? 1 : 0;
        updateTorchButtonState();
        applyTorchMode();
    }

    private void applyTorchMode() {
        if (captureRequestBuilder != null && captureSession != null && isStreaming) {
            applyCaptureRequestParameters();
        } else if (!isStreaming && currentCameraId != null && isFlashSupported) {
            try {
                cameraManager.setTorchMode(currentCameraId, torchState > 0);
            } catch (Exception ignored) {}
        }
    }

    private void cycleScreenGlow() {
        screenGlowState = (screenGlowState + 1) % GLOW_NAMES.length;
        applyScreenGlowDirect(screenGlowState);
    }

    private void applyZoom(CaptureRequest.Builder builder) {
        if (sensorArraySize == null || builder == null) return;
        int cropW = (int) (sensorArraySize.width() / currentZoom);
        int cropH = (int) (sensorArraySize.height() / currentZoom);
        int cropX = (sensorArraySize.width() - cropW) / 2;
        int cropY = (sensorArraySize.height() - cropH) / 2;
        Rect cropRect = new Rect(cropX, cropY, cropX + cropW, cropY + cropH);
        builder.set(CaptureRequest.SCALER_CROP_REGION, cropRect);
    }

    private void setupOrientationListener() {
        orientationEventListener = new OrientationEventListener(this) {
            @Override
            public void onOrientationChanged(int orientation) {
                if (orientation == ORIENTATION_UNKNOWN) return;
                int newOrientation;
                if (orientation >= 315 || orientation < 45) {
                    newOrientation = 0; // Portrait
                } else if (orientation >= 45 && orientation < 135) {
                    newOrientation = 270; // Landscape Right (Phone rotated right)
                } else if (orientation >= 135 && orientation < 225) {
                    newOrientation = 180; // Inverted Portrait
                } else {
                    newOrientation = 90; // Landscape Left (Phone rotated left)
                }
                if (newOrientation != deviceOrientation) {
                    deviceOrientation = newOrientation;
                    runOnUiThread(() -> {
                        if (previewView != null && previewView.isAvailable()) {
                            configureTransform(previewView.getWidth(), previewView.getHeight());
                        }
                    });
                }
            }
        };
        if (orientationEventListener.canDetectOrientation()) {
            orientationEventListener.enable();
        }
    }

    private int calculateSensorRotation() {
        int displayRotation = getWindowManager().getDefaultDisplay().getRotation();
        int degrees = 0;
        switch (displayRotation) {
            case Surface.ROTATION_0: degrees = 0; break;
            case Surface.ROTATION_90: degrees = 90; break;
            case Surface.ROTATION_180: degrees = 180; break;
            case Surface.ROTATION_270: degrees = 270; break;
        }
        int sensorOrientation = this.sensorOrientation;
        int rotation;
        if (currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) {
            rotation = (sensorOrientation + degrees) % 360;
            rotation = (360 - rotation) % 360;
        } else {
            rotation = (sensorOrientation - degrees + 360) % 360;
        }
        return (rotation + manualRotationAngle) % 360;
    }

    private int computeRelativeRotation() {
        return calculateSensorRotation();
    }

    private void configureTransform(int viewWidth, int viewHeight) {
        if (previewView == null || !previewView.isAvailable() || targetWidth == 0 || targetHeight == 0) return;
        int rotation = getWindowManager().getDefaultDisplay().getRotation();
        Matrix matrix = new Matrix();
        RectF viewRect = new RectF(0, 0, viewWidth, viewHeight);
        float centerX = viewRect.centerX();
        float centerY = viewRect.centerY();

        if (Surface.ROTATION_90 == rotation || Surface.ROTATION_270 == rotation) {
            RectF bufferRect = new RectF(0, 0, targetHeight, targetWidth);
            bufferRect.offset(centerX - bufferRect.centerX(), centerY - bufferRect.centerY());
            matrix.setRectToRect(viewRect, bufferRect, Matrix.ScaleToFit.FILL);
            float scale = Math.max(
                (float) viewHeight / targetHeight,
                (float) viewWidth / targetWidth);
            matrix.postScale(scale, scale, centerX, centerY);
            matrix.postRotate(90 * (rotation - 2), centerX, centerY);
        } else if (Surface.ROTATION_180 == rotation) {
            matrix.postRotate(180, centerX, centerY);
        } else if (manualRotationAngle != 0) {
            matrix.postRotate(manualRotationAngle, centerX, centerY);
        }

        if (isMirrored) {
            matrix.postScale(-1, 1, centerX, centerY);
        }
        previewView.setTransform(matrix);
    }

    private void startBackgroundThread() {
        if (backgroundThread != null) return;
        backgroundThread = new HandlerThread("CameraBackground");
        backgroundThread.start();
        backgroundHandler = new Handler(backgroundThread.getLooper());
    }

    private void stopBackgroundThread() {
        if (backgroundThread != null) {
            backgroundThread.quitSafely();
            try {
                backgroundThread.join();
                backgroundThread = null;
                backgroundHandler = null;
            } catch (Exception ignored) {}
        }
    }

    private void closeCamera() {
        if (captureSession != null) {
            try { captureSession.close(); } catch (Exception ignored) {}
            captureSession = null;
        }
        if (cameraDevice != null) {
            try { cameraDevice.close(); } catch (Exception ignored) {}
            cameraDevice = null;
        }
        stopEncoder();
        stopBackgroundThread();
    }

    private String findCameraIdForFacing(int desiredFacing) {
        try {
            for (String id : cameraManager.getCameraIdList()) {
                CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(id);
                Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
                if (facing != null && facing == desiredFacing) return id;
            }
        } catch (Exception ignored) {}
        return null;
    }

    private void updateCameraIndicator() {
        String facingName = (currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) ? "FRONT" : "BACK";
        cameraIndicatorText.setText("Lens: " + facingName + " [" + currentCameraId + "]");
        btnSwitchCam.setText("Flip (" + facingName + ")");
    }

    // [AI-BLOCK: TCP Video Server for H.264 NAL Packets]
    private void startVideoServer() {
        new Thread(() -> {
            try {
                videoServerSocket = new ServerSocket();
                videoServerSocket.setReuseAddress(true);
                videoServerSocket.bind(new java.net.InetSocketAddress(STREAM_PORT));
                while (isStreaming) {
                    Socket client = videoServerSocket.accept();
                    synchronized (this) {
                        if (activeVideoClient != null && !activeVideoClient.isClosed()) {
                            try { activeVideoClient.close(); } catch (Exception ignored) {}
                        }
                        activeVideoClient = client;
                        videoOutputStream = client.getOutputStream();
                        if (cachedSpsPps != null) {
                            sendFramePacket(cachedSpsPps);
                        }
                        requestSyncFrame();
                    }
                    // [AI-BLOCK: Detect connection mode from client IP on accept]
                    java.net.InetAddress addr = client.getInetAddress();
                    String remoteIp = (addr != null && addr.getHostAddress() != null) ? addr.getHostAddress() : "";
                    final String detectedMode;
                    if ((addr != null && addr.isLoopbackAddress()) || remoteIp.contains("127.0.0.1") || remoteIp.equals("::1")) {
                        detectedMode = "adb";
                    } else if (remoteIp.contains("192.168.42.") || remoteIp.contains("192.168.43.") || remoteIp.contains("192.168.44.") || remoteIp.contains("192.168.49.") || remoteIp.contains("192.168.50.")) {
                        detectedMode = "usb_tether";
                    } else {
                        detectedMode = "wifi";
                    }
                    activeConnectionMode = detectedMode;
                    runOnUiThread(this::updateConnectionModeLabel);
                }
            } catch (Exception ignored) {}
        }).start();
    }

    private void stopVideoServer() {
        try {
            if (activeVideoClient != null) activeVideoClient.close();
            if (videoServerSocket != null) videoServerSocket.close();
        } catch (Exception ignored) {}
        activeVideoClient = null;
        videoOutputStream = null;
        activeConnectionMode = null;
        runOnUiThread(this::updateConnectionModeLabel);
    }

    private synchronized void sendFramePacket(byte[] data) {
        if (videoOutputStream == null || data == null) return;
        try {
            ByteBuffer lenBuffer = ByteBuffer.allocate(4);
            lenBuffer.putInt(data.length);
            videoOutputStream.write(lenBuffer.array());
            videoOutputStream.write(data);
            videoOutputStream.flush();
        } catch (Exception e) {
            try {
                if (activeVideoClient != null) activeVideoClient.close();
            } catch (Exception ignored) {}
            activeVideoClient = null;
            videoOutputStream = null;
            runOnUiThread(() -> {
                statusText.setText("● Otter: Client Disconnected");
                stopStreaming();
            });
        }
    }

    private void startEncodingLoop() {
        new Thread(() -> {
            MediaCodec.BufferInfo bufferInfo = new MediaCodec.BufferInfo();
            while (isStreaming) {
                if (!encoderReady || mediaCodec == null) {
                    try { Thread.sleep(50); } catch (InterruptedException ignored) {}
                    continue;
                }
                try {
                    int outputBufferIndex = mediaCodec.dequeueOutputBuffer(bufferInfo, 10000);
                    if (outputBufferIndex >= 0) {
                        ByteBuffer outputBuffer = mediaCodec.getOutputBuffer(outputBufferIndex);
                        if (outputBuffer != null && bufferInfo.size > 0) {
                            byte[] outData = new byte[bufferInfo.size];
                            outputBuffer.get(outData);

                            if ((bufferInfo.flags & MediaCodec.BUFFER_FLAG_CODEC_CONFIG) != 0) {
                                cachedSpsPps = outData;
                            }

                            if (!isPaused) {
                                sendFramePacket(outData);
                            }
                        }
                        mediaCodec.releaseOutputBuffer(outputBufferIndex, false);
                    }
                } catch (IllegalStateException ignored) {
                    // Codec transitioned state mid-loop; skip this iteration
                }
            }
        }).start();
    }

    // [AI-BLOCK: TCP RPC Control Server with Capabilities & Pro Adjustments]
    private void startControlServer() {
        new Thread(() -> {
            try {
                controlServerSocket = new ServerSocket();
                controlServerSocket.setReuseAddress(true);
                controlServerSocket.bind(new java.net.InetSocketAddress(CONTROL_PORT));
                while (!isFinishing()) {
                    Socket socket = controlServerSocket.accept();
                    new Thread(() -> handleControlClient(socket)).start();
                }
            } catch (Exception ignored) {}
        }).start();
    }

    private void handleControlClient(Socket socket) {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             OutputStream out = socket.getOutputStream()) {
            String line = reader.readLine();
            if (line != null) {
                String response = handleControlCommand(line);
                out.write((response + "\n").getBytes());
                out.flush();
            }
        } catch (Exception ignored) {}
    }

    private String handleControlCommand(String jsonCommand) {
        try {
            JSONObject cmd = new JSONObject(jsonCommand);
            String action = cmd.optString("action");
            switch (action) {
                case "get_capabilities":
                    JSONObject caps = new JSONObject();
                    caps.put("status", "ok");
                    caps.put("resolutions", new JSONArray(supportedResLabels));
                    caps.put("fpsRanges", new JSONArray(supportedFpsList));
                    if (maxJpegSize != null) {
                        caps.put("maxPhotoWidth", maxJpegSize.getWidth());
                        caps.put("maxPhotoHeight", maxJpegSize.getHeight());
                    }
                    caps.put("maxZoom", maxZoom);
                    return caps.toString();

                case "set_connection_mode":
                    String connMode = cmd.optString("mode");
                    if (!connMode.isEmpty()) {
                        activeConnectionMode = connMode;
                        runOnUiThread(this::updateConnectionModeLabel);
                    }
                    return "{\"status\":\"ok\",\"mode\":\"" + activeConnectionMode + "\"}";

                case "switch_camera":
                    runOnUiThread(this::switchCamera);
                    return "{\"status\":\"ok\",\"action\":\"switch_camera\"}";
                case "toggle_mirror":
                    runOnUiThread(this::toggleMirror);
                    return "{\"status\":\"ok\",\"mirrored\":" + isMirrored + "}";
                case "rotate_camera":
                    runOnUiThread(this::cycleRotation);
                    return "{\"status\":\"ok\",\"rotationAngle\":" + ((manualRotationAngle + 90) % 360) + "}";
                case "set_rotation":
                    int rotAngle = cmd.optInt("angle", 0);
                    manualRotationAngle = rotAngle;
                    runOnUiThread(this::cycleRotation);
                    return "{\"status\":\"ok\",\"rotationAngle\":" + rotAngle + "}";
                case "set_resolution":
                    int resW = cmd.optInt("width", 1280);
                    int resH = cmd.optInt("height", 720);
                    targetWidth = resW;
                    targetHeight = resH;
                    runOnUiThread(() -> {
                        badgeResolution.setText(resW >= 3840 ? "4K" : resH + "p");
                        if (isStreaming) { closeCamera(); openCamera(targetWidth, targetHeight); }
                    });
                    return "{\"status\":\"ok\",\"width\":" + resW + ",\"height\":" + resH + "}";
                case "set_fps":
                    int fps = cmd.optInt("fps", 30);
                    targetFps = fps;
                    runOnUiThread(() -> {
                        badgeFps.setText(fps + " FPS");
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"fps\":" + fps + "}";
                case "zoom_in":
                    runOnUiThread(() -> zoomStep(0.2f));
                    return "{\"status\":\"ok\",\"zoom\":" + currentZoom + "}";
                case "zoom_out":
                    runOnUiThread(() -> zoomStep(-0.2f));
                    return "{\"status\":\"ok\",\"zoom\":" + currentZoom + "}";
                case "set_zoom":
                    float z = (float) cmd.optDouble("value", 1.0);
                    runOnUiThread(() -> {
                        currentZoom = Math.max(1.0f, Math.min(maxZoom, z));
                        updateZoomDisplay();
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"zoom\":" + currentZoom + "}";
                case "ev_step":
                    int d = cmd.optInt("delta", 1);
                    runOnUiThread(() -> evStep(d));
                    return "{\"status\":\"ok\",\"exposureCompensation\":" + currentExposureCompensation + "}";
                case "set_exposure":
                    int expVal = cmd.optInt("value", 0);
                    runOnUiThread(() -> {
                        currentExposureCompensation = expVal;
                        updateExposureDisplay();
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"exposureCompensation\":" + expVal + "}";
                case "set_iso":
                    int isoVal = cmd.optInt("value", 0);
                    runOnUiThread(() -> {
                        currentIso = isoVal;
                        btnIso.setText("ISO: " + (currentIso == 0 ? "Auto" : String.valueOf(currentIso)));
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"iso\":" + isoVal + "}";
                case "set_shutter":
                    long shutterVal = cmd.optLong("value", 0L);
                    runOnUiThread(() -> {
                        currentShutterNs = shutterVal;
                        btnShutter.setText("Shutter: " + (shutterVal == 0 ? "Auto" : (shutterVal / 1000000) + "ms"));
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"shutter\":" + shutterVal + "}";
                case "set_awb":
                    int awbMode = cmd.optInt("mode", 1);
                    runOnUiThread(() -> {
                        awbIndex = awbMode % AWB_MODES.length;
                        btnAwb.setText("WB: " + AWB_LABELS[awbIndex]);
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"awb\":" + awbMode + "}";
                case "set_effect":
                    int fx = cmd.optInt("effect", 0);
                    runOnUiThread(() -> {
                        effectIndex = fx % COLOR_EFFECTS.length;
                        btnColorEffect.setText("FX: " + EFFECT_LABELS[effectIndex]);
                        applyCaptureRequestParameters();
                    });
                    return "{\"status\":\"ok\",\"effect\":" + fx + "}";
                case "set_quick_mode":
                    String qm = cmd.optString("mode", "meetings");
                    runOnUiThread(() -> applyQuickMode(qm));
                    return "{\"status\":\"ok\",\"mode\":\"" + qm + "\"}";
                case "capture_still":
                    runOnUiThread(this::takeUltraPhoto);
                    return "{\"status\":\"ok\",\"action\":\"capture_still\"}";
                case "toggle_torch":
                    runOnUiThread(this::cycleTorch);
                    return "{\"status\":\"ok\",\"torchSupported\":" + isFlashSupported + ",\"torchState\":" + torchState + "}";
                case "toggle_glow":
                    runOnUiThread(this::cycleScreenGlow);
                    return "{\"status\":\"ok\",\"glowState\":" + screenGlowState + ",\"glowName\":\"" + GLOW_NAMES[screenGlowState] + "\"}";
                case "toggle_af":
                    runOnUiThread(this::toggleFocusMode);
                    return "{\"status\":\"ok\",\"isAutoFocus\":" + isAutoFocus + "}";
                case "start_stream":
                    runOnUiThread(this::startStreaming);
                    return "{\"status\":\"ok\",\"streaming\":true}";
                case "stop_stream":
                    runOnUiThread(this::stopStreaming);
                    return "{\"status\":\"ok\",\"streaming\":false}";
                case "set_background_mode":
                    String mode = cmd.optString("mode", "off");
                    String workload = cmd.optString("workload", "pc");
                    bgMode = mode;
                    bgWorkload = workload;
                    runOnUiThread(() -> {
                        if (mode.equals("off") || mode.equals("none")) {
                            btnVirtualBg.setText("Virtual BG: OFF");
                            btnVirtualBg.setTextColor(0xFF8B949E);
                        } else if (mode.equals("blur_light")) {
                            btnVirtualBg.setText("Virtual BG: Bokeh Blur");
                            btnVirtualBg.setTextColor(0xFF3FB950);
                        } else if (mode.equals("blur_heavy")) {
                            btnVirtualBg.setText("Virtual BG: Privacy Blur");
                            btnVirtualBg.setTextColor(0xFF3FB950);
                        } else if (mode.equals("green_screen") || mode.equals("solid_green")) {
                            btnVirtualBg.setText("Virtual BG: Green Screen");
                            btnVirtualBg.setTextColor(0xFF3FB950);
                        } else if (workload.equals("pc")) {
                            btnVirtualBg.setText("Virtual BG: PC GPU (" + mode + ")");
                            btnVirtualBg.setTextColor(0xFF3FB950);
                        } else {
                            btnVirtualBg.setText("Virtual BG: Mobile (" + mode + ")");
                            btnVirtualBg.setTextColor(0xFF58A6FF);
                        }
                    });
                    return "{\"status\":\"ok\",\"mode\":\"" + mode + "\",\"workload\":\"" + workload + "\"}";
                case "toggle_keep_screen_on":
                    runOnUiThread(this::toggleKeepScreenOn);
                    return "{\"status\":\"ok\",\"isKeepScreenOn\":" + isKeepScreenOn + "}";
                case "set_keep_screen_on":
                    boolean keep = cmd.optBoolean("enabled", true);
                    runOnUiThread(() -> applyKeepScreenOn(keep));
                    return "{\"status\":\"ok\",\"isKeepScreenOn\":" + keep + "}";
                case "get_status":
                    float evVal = (exposureStep != null) ? currentExposureCompensation * exposureStep.floatValue() : currentExposureCompensation;
                    return "{\"status\":\"ok\",\"streaming\":" + isStreaming + ",\"zoom\":" + currentZoom +
                            ",\"lens\":\"" + ((currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) ? "FRONT" : "BACK") +
                            "\",\"mirrored\":" + isMirrored + ",\"rotationAngle\":" + computeRelativeRotation() +
                            ",\"width\":" + targetWidth + ",\"height\":" + targetHeight +
                            ",\"targetFps\":" + targetFps +
                            ",\"iso\":" + currentIso + ",\"shutter\":" + currentShutterNs +
                            ",\"awb\":\"" + AWB_LABELS[awbIndex] + "\",\"effect\":\"" + EFFECT_LABELS[effectIndex] + "\"" +
                            ",\"torchSupported\":" + isFlashSupported + ",\"torchState\":" + torchState +
                            ",\"glowState\":" + screenGlowState + ",\"glowName\":\"" + GLOW_NAMES[screenGlowState] + "\"" +
                            ",\"isAutoFocus\":" + isAutoFocus + ",\"focusDistance\":" + currentFocusDistance +
                            ",\"minFocusDistance\":" + minimumFocusDistance +
                            ",\"exposure\":" + currentExposureCompensation + ",\"ev\":" + evVal +
                            ",\"bgMode\":\"" + bgMode + "\",\"bgWorkload\":\"" + bgWorkload + "\"" +
                            ",\"isKeepScreenOn\":" + isKeepScreenOn + "}";
                default:
                    return "{\"status\":\"error\",\"message\":\"unknown command\"}";
            }
        } catch (Exception e) {
            return "{\"status\":\"error\",\"message\":\"" + e.getMessage() + "\"}";
        }
    }

    private void toggleKeepScreenOn() {
        applyKeepScreenOn(!isKeepScreenOn);
        android.content.SharedPreferences prefs = getSharedPreferences("otter_settings", Context.MODE_PRIVATE);
        prefs.edit().putBoolean("keep_screen_on", isKeepScreenOn).apply();
    }

    private void applyKeepScreenOn(boolean keepOn) {
        isKeepScreenOn = keepOn;
        if (isKeepScreenOn) {
            getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            if (btnKeepScreenOn != null) {
                btnKeepScreenOn.setText("Screen: Keep ON");
                btnKeepScreenOn.setTextColor(0xFF238636);
            }
        } else {
            getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            if (btnKeepScreenOn != null) {
                btnKeepScreenOn.setText("Screen: Auto Sleep");
                btnKeepScreenOn.setTextColor(0xFF8B949E);
            }
        }
    }

    private void toggleScreenDim() {
        isScreenDimmed = !isScreenDimmed;
        WindowManager.LayoutParams lp = getWindow().getAttributes();
        if (isScreenDimmed) {
            originalScreenBrightness = lp.screenBrightness;
            lp.screenBrightness = 0.01f;
            btnScreenDim.setText("Screen: Dimmed");
            btnScreenDim.setTextColor(0xFFE3B341);
        } else {
            lp.screenBrightness = originalScreenBrightness >= 0 ? originalScreenBrightness : WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;
            btnScreenDim.setText("Dim Display (Save Power)");
            btnScreenDim.setTextColor(0xFFC9D1D9);
        }
        getWindow().setAttributes(lp);
    }

    private void showVirtualBgDialog() {
        final String[] options = {
            "Off / Pass-Through (None)",
            "Blur Background (Bokeh Portrait)",
            "Heavy Privacy Blur",
            "Solid Green Screen (Chroma Key)",
            "Upload / Choose Custom Wallpaper from Gallery...",
            "Preset: Modern Office",
            "Preset: Studio Bokeh",
            "Preset: Minimalist Bookshelf",
            "Preset: Cozy Coffee Shop",
            "Wallpaper Guidelines & Specs",
            "Workload: " + (bgWorkload.equals("pc") ? "PC GPU Offload (Recommended)" : "Mobile Device Processing")
        };
        new AlertDialog.Builder(this)
            .setTitle("Virtual Background & Effects")
            .setItems(options, (dialog, which) -> {
                switch (which) {
                    case 0:
                        bgMode = "off";
                        btnVirtualBg.setText("Virtual BG: OFF");
                        btnVirtualBg.setTextColor(0xFF8B949E);
                        Toast.makeText(this, "Virtual Background disabled (Pass-Through).", Toast.LENGTH_SHORT).show();
                        break;
                    case 1:
                        bgMode = "blur_light";
                        btnVirtualBg.setText("Virtual BG: Bokeh Blur");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Portrait Bokeh Blur active. (PC GPU offload recommended).", Toast.LENGTH_SHORT).show();
                        break;
                    case 2:
                        bgMode = "blur_heavy";
                        btnVirtualBg.setText("Virtual BG: Privacy Blur");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Heavy Privacy Blur active.", Toast.LENGTH_SHORT).show();
                        break;
                    case 3:
                        bgMode = "green_screen";
                        btnVirtualBg.setText("Virtual BG: Green Screen");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Chroma Green Screen active for streaming.", Toast.LENGTH_SHORT).show();
                        break;
                    case 4:
                        launchImagePicker();
                        break;
                    case 5:
                        bgMode = "custom_image";
                        customWallpaperName = "Modern Office";
                        btnVirtualBg.setText("Virtual BG: Modern Office");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Preset applied: Modern Office.", Toast.LENGTH_SHORT).show();
                        break;
                    case 6:
                        bgMode = "custom_image";
                        customWallpaperName = "Studio Bokeh";
                        btnVirtualBg.setText("Virtual BG: Studio Bokeh");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Preset applied: Studio Bokeh.", Toast.LENGTH_SHORT).show();
                        break;
                    case 7:
                        bgMode = "custom_image";
                        customWallpaperName = "Bookshelf";
                        btnVirtualBg.setText("Virtual BG: Bookshelf");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Preset applied: Minimalist Bookshelf.", Toast.LENGTH_SHORT).show();
                        break;
                    case 8:
                        bgMode = "custom_image";
                        customWallpaperName = "Coffee Shop";
                        btnVirtualBg.setText("Virtual BG: Coffee Shop");
                        btnVirtualBg.setTextColor(0xFF3FB950);
                        Toast.makeText(this, "Preset applied: Cozy Coffee Shop.", Toast.LENGTH_SHORT).show();
                        break;
                    case 9:
                        showWallpaperSpecsDialog();
                        break;
                    case 10:
                        toggleWorkloadRouting();
                        break;
                }
            })
            .setNegativeButton("Cancel", null)
            .show();
    }

    private void launchImagePicker() {
        try {
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.setType("image/*");
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            startActivityForResult(Intent.createChooser(intent, "Choose Wallpaper Image"), REQUEST_PICK_WALLPAPER);
        } catch (Exception e) {
            Toast.makeText(this, "Unable to launch gallery picker: " + e.getMessage(), Toast.LENGTH_SHORT).show();
        }
    }

    private void showWallpaperSpecsDialog() {
        new AlertDialog.Builder(this)
            .setTitle("Wallpaper Guidelines & Specs")
            .setMessage("Recommended Wallpaper Specifications:\n\n"
                + "• Aspect Ratio: 16:9 (matching standard landscape video)\n"
                + "• Recommended Resolutions: 1920x1080 (FHD) or 1280x720 (HD)\n"
                + "• Supported Formats: JPG, PNG, WEBP\n"
                + "• File Size: Under 15 MB\n\n"
                + "Otter automatically scales and centers wallpapers to match your stream resolution. For maximum phone battery life and zero thermal throttling, route background processing to PC GPU/CPU Offload.")
            .setPositiveButton("Got It", null)
            .show();
    }

    private void toggleWorkloadRouting() {
        if ("pc".equalsIgnoreCase(bgWorkload)) {
            bgWorkload = "mobile";
            Toast.makeText(this, "Workload routed to Mobile Device.", Toast.LENGTH_SHORT).show();
        } else {
            bgWorkload = "pc";
            Toast.makeText(this, "Workload routed to PC GPU/CPU Offload (Saves Phone Battery).", Toast.LENGTH_SHORT).show();
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_PICK_WALLPAPER && resultCode == Activity.RESULT_OK && data != null && data.getData() != null) {
            customWallpaperUri = data.getData();
            customWallpaperName = "Custom Gallery Image";
            bgMode = "custom_image";
            btnVirtualBg.setText("Virtual BG: Custom Wallpaper");
            btnVirtualBg.setTextColor(0xFF3FB950);
            Toast.makeText(this, "Custom wallpaper selected. (PC GPU offload recommended for optimal streaming performance).", Toast.LENGTH_LONG).show();
        }
    }

    // [AI-BLOCK: Network info display - dynamically labels based on detected interface + active mode]
    private void displayNetworkInfo() {
        if (streamInfoText == null) return;
        try {
            String tetherIp = null;
            String wifiIp = null;
            String generalIp = null;
            java.util.List<java.net.NetworkInterface> interfaces = java.util.Collections.list(java.net.NetworkInterface.getNetworkInterfaces());
            for (java.net.NetworkInterface intf : interfaces) {
                if (intf.isLoopback() || !intf.isUp()) continue;
                String name = intf.getName().toLowerCase();
                for (java.net.InetAddress addr : java.util.Collections.list(intf.getInetAddresses())) {
                    if (!addr.isLoopbackAddress() && addr instanceof java.net.Inet4Address) {
                        String sAddr = addr.getHostAddress();
                        if (name.contains("rndis") || name.contains("usb") || name.contains("ncm") 
                                || sAddr.startsWith("192.168.42.") || sAddr.startsWith("192.168.43.")
                                || sAddr.startsWith("192.168.44.") || sAddr.startsWith("192.168.49.")
                                || sAddr.startsWith("192.168.50.")) {
                            tetherIp = sAddr;
                        } else if (name.contains("wlan") || name.contains("wifi")) {
                            wifiIp = sAddr;
                        } else {
                            generalIp = sAddr;
                        }
                    }
                }
            }

            if ("adb".equals(activeConnectionMode) || "usb".equals(activeConnectionMode)) {
                streamInfoText.setText("ADB USB Tunnel | Port: " + STREAM_PORT);
                return;
            }

            if ("usb_tether".equals(activeConnectionMode) || "tether".equals(activeConnectionMode)) {
                String tip = tetherIp != null ? tetherIp : "192.168.42.129";
                streamInfoText.setText("USB Tether: " + tip + " | Port: " + STREAM_PORT);
                return;
            }

            if (tetherIp != null) {
                streamInfoText.setText("USB Tether: " + tetherIp + " | Port: " + STREAM_PORT);
                return;
            }
            if (wifiIp != null) {
                streamInfoText.setText("Wi-Fi IP: " + wifiIp + " | Port: " + STREAM_PORT);
                return;
            }
            if (generalIp != null) {
                streamInfoText.setText("IP: " + generalIp + " | Port: " + STREAM_PORT);
                return;
            }
        } catch (Exception ignored) {}

        try {
            WifiManager wm = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wm != null && wm.getConnectionInfo() != null) {
                String ip = Formatter.formatIpAddress(wm.getConnectionInfo().getIpAddress());
                if (ip != null && !ip.equals("0.0.0.0")) {
                    streamInfoText.setText("Wi-Fi IP: " + ip + " | Port: " + STREAM_PORT);
                    return;
                }
            }
        } catch (Exception ignored) {}
        streamInfoText.setText("Port: " + STREAM_PORT);
    }

    // [AI-BLOCK: Updates stream info label to reflect actual detected connection mode]
    private void updateConnectionModeLabel() {
        if (streamInfoText == null) return;
        if ("adb".equals(activeConnectionMode) || "usb".equals(activeConnectionMode)) {
            streamInfoText.setText("ADB USB Tunnel | Port: " + STREAM_PORT);
        } else if ("usb_tether".equals(activeConnectionMode) || "tether".equals(activeConnectionMode)) {
            streamInfoText.setText("USB Tether Active | Port: " + STREAM_PORT);
        } else {
            displayNetworkInfo();
        }
    }

    private void openTetheringSettings() {
        try {
            Intent intent = new Intent();
            intent.setAction("android.settings.TETHER_SETTINGS");
            startActivity(intent);
        } catch (Exception e) {
            try {
                startActivity(new Intent(Settings.ACTION_WIRELESS_SETTINGS));
            } catch (Exception ignored) {}
        }
    }

    private void toggleBackgroundLock() {
        isForegroundServiceEnabled = !isForegroundServiceEnabled;
        isBackgroundLockEnabled = isForegroundServiceEnabled;
        btnBackgroundLock.setText("Foreground: " + (isForegroundServiceEnabled ? "ON" : "OFF"));
        btnBackgroundLock.setTextColor(isForegroundServiceEnabled ? 0xFF238636 : 0xFF8B949E);
        if (isStreaming) {
            if (isForegroundServiceEnabled) {
                startBackgroundService();
            } else {
                stopBackgroundService();
            }
        }
        Toast.makeText(this, "Foreground Service: " + (isForegroundServiceEnabled ? "ON (Active Notification)" : "OFF (Streaming in App only)"), Toast.LENGTH_SHORT).show();
    }

    private void showBatteryGuideDialog() {
        new AlertDialog.Builder(this)
            .setTitle("Background Optimization Guide")
            .setMessage("To prevent OEM background task killers from stopping your video stream:\n\n"
                + "• Settings > Apps > Otter > Battery: Unrestricted\n"
                + "• Lock Otter in Recent Apps tray\n"
                + "• Disable battery saver during streams.")
            .setPositiveButton("Open Settings", (d, w) -> {
                try {
                    Intent i = new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS);
                    i.setData(Uri.parse("package:" + getPackageName()));
                    startActivity(i);
                } catch (Exception ignored) {}
            })
            .setNegativeButton("Close", null)
            .show();
    }

    private void startBackgroundService() {
        try {
            Intent serviceIntent = new Intent(this, OtterStreamService.class);
            serviceIntent.setAction(OtterStreamService.ACTION_START);
            serviceIntent.putExtra("STREAM_STATUS", "Camera is actively streaming on port " + STREAM_PORT + " (" + targetWidth + "x" + targetHeight + ")");
            serviceIntent.putExtra("IS_PAUSED", isPaused);
            serviceIntent.putExtra("ENABLE_WAKELOCK", isBackgroundLockEnabled);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent);
            } else {
                startService(serviceIntent);
            }
        } catch (Exception ignored) {}
    }

    private void updateServiceNotification() {
        if (!isForegroundServiceEnabled) return;
        try {
            Intent serviceIntent = new Intent(this, OtterStreamService.class);
            serviceIntent.setAction(OtterStreamService.ACTION_START);
            serviceIntent.putExtra("STREAM_STATUS", isPaused ? "Camera stream paused" : "Camera is actively streaming on port " + STREAM_PORT + " (" + targetWidth + "x" + targetHeight + ")");
            serviceIntent.putExtra("IS_PAUSED", isPaused);
            serviceIntent.putExtra("ENABLE_WAKELOCK", isBackgroundLockEnabled);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent);
            } else {
                startService(serviceIntent);
            }
        } catch (Exception ignored) {}
    }

    private void stopBackgroundService() {
        try {
            Intent serviceIntent = new Intent(this, OtterStreamService.class);
            serviceIntent.setAction(OtterStreamService.ACTION_STOP);
            startService(serviceIntent);
        } catch (Exception ignored) {}
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        if (orientationEventListener != null) {
            orientationEventListener.disable();
        }
        stopStreaming();
        try {
            if (controlServerSocket != null) controlServerSocket.close();
            if (stillImageReader != null) stillImageReader.close();
        } catch (Exception ignored) {}
    }
}

package org.understory.cambridge;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.content.res.Configuration;
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
import android.media.MediaCodec;
import android.media.MediaCodecInfo;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.View;
import android.view.WindowManager;
import android.media.MediaFormat;
import android.net.wifi.WifiManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.HandlerThread;
import android.text.format.Formatter;
import android.view.Surface;
import android.view.TextureView;
import android.widget.Button;
import android.widget.TextView;
import android.util.Range;
import android.util.Rational;
import androidx.annotation.NonNull;
import android.app.Activity;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.ByteBuffer;
import java.util.Arrays;

// [AI-BLOCK: Main Activity managing Camera2, H.264 MediaCodec, 360 orientation, mirror toggle, background lock, and TCP streaming server]
public class MainActivity extends Activity {

    private static final int PERMISSION_REQUEST_CAMERA = 101;
    private static final int STREAM_PORT = 8089;
    private static final int CONTROL_PORT = 8090;

    private static final int[][] RESOLUTIONS = {
        {1920, 1080},
        {1280, 720},
        {640, 480},
        {640, 360}
    };
    private static final String[] RES_LABELS = {"1080p", "720p", "480p", "360p"};

    private TextureView previewView;
    private TextView statusText;
    private TextView cameraIndicatorText;
    private TextView streamInfoText;
    private Button btnStart, btnPause, btnStop, btnSwitchCam;
    private Button btnResolution, btnMirror;
    private Button btnBackgroundLock, btnBatteryGuide, btnAbout;
    private Button btnTorch, btnScreenGlow;
    private Button btnFocusMode, btnManualFocus, btnExposure;
    private Button btnRotate;
    private View screenGlowBorder;
    private boolean isBackgroundLockEnabled = true;
    private boolean isFlashSupported = false;
    private int torchState = 0;
    private int maxTorchLevel = 1;
    private int screenGlowState = 0;
    private static final String[] GLOW_NAMES = {"OFF", "Warm", "Daylight", "Sunset", "White"};
    private static final int[] GLOW_COLORS = {0x00000000, 0x99FFF3E0, 0x99E3F2FD, 0x99FFE082, 0xBBFFFFFF};
    private float originalScreenBrightness = -1f;

    // Manual Focus & Exposure Parameters
    private boolean isAutoFocus = true;
    private float minimumFocusDistance = 0f; // Diopters (0 = infinity)
    private float currentFocusDistance = 0f;
    private Range<Integer> exposureRange;
    private Rational exposureStep;
    private int currentExposureCompensation = 0;

    private CameraManager cameraManager;
    private String currentCameraId;
    private int currentLensFacing = CameraCharacteristics.LENS_FACING_BACK;
    private CameraDevice cameraDevice;
    private CameraCaptureSession captureSession;
    private CaptureRequest.Builder captureRequestBuilder;

    private Handler backgroundHandler;
    private HandlerThread backgroundThread;

    private MediaCodec mediaCodec;
    private Surface encoderInputSurface;
    private volatile boolean isStreaming = false;
    private volatile boolean isPaused = false;
    private volatile boolean isMirrored = false;
    private int manualRotationAngle = 0; // 0, 90, 180, 270 degrees manual rotation offset

    private int currentResIndex = 1; // 720p default
    private int targetWidth = 1280;
    private int targetHeight = 720;

    private ServerSocket videoServerSocket;
    private Socket activeVideoClient;
    private OutputStream videoOutputStream;
    private volatile byte[] cachedSpsPps = null;

    private ServerSocket controlServerSocket;
    private float currentZoom = 1.0f;
    private float maxZoom = 1.0f;
    private Rect sensorArraySize;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        previewView = findViewById(R.id.previewView);
        statusText = findViewById(R.id.statusText);
        cameraIndicatorText = findViewById(R.id.cameraIndicatorText);
        streamInfoText = findViewById(R.id.streamInfoText);

        btnStart = findViewById(R.id.btnStart);
        btnPause = findViewById(R.id.btnPause);
        btnStop = findViewById(R.id.btnStop);
        btnSwitchCam = findViewById(R.id.btnSwitchCam);
        btnResolution = findViewById(R.id.btnResolution);
        btnMirror = findViewById(R.id.btnMirror);
        btnBackgroundLock = findViewById(R.id.btnBackgroundLock);
        btnBatteryGuide = findViewById(R.id.btnBatteryGuide);
        btnAbout = findViewById(R.id.btnAbout);
        btnTorch = findViewById(R.id.btnTorch);
        btnScreenGlow = findViewById(R.id.btnScreenGlow);
        screenGlowBorder = findViewById(R.id.screenGlowBorder);
        btnFocusMode = findViewById(R.id.btnFocusMode);
        btnManualFocus = findViewById(R.id.btnManualFocus);
        btnExposure = findViewById(R.id.btnExposure);
        btnRotate = findViewById(R.id.btnRotate);

        cameraManager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);

        btnStart.setOnClickListener(v -> startStreaming());
        btnPause.setOnClickListener(v -> togglePause());
        btnStop.setOnClickListener(v -> stopStreaming());
        btnSwitchCam.setOnClickListener(v -> switchCamera());
        btnResolution.setOnClickListener(v -> cycleResolution());
        btnMirror.setOnClickListener(v -> toggleMirror());
        btnBackgroundLock.setOnClickListener(v -> toggleBackgroundLock());
        btnBatteryGuide.setOnClickListener(v -> showBatteryGuideDialog());
        btnAbout.setOnClickListener(v -> startActivity(new Intent(this, AboutActivity.class)));
        btnTorch.setOnClickListener(v -> cycleTorch());
        btnScreenGlow.setOnClickListener(v -> cycleScreenGlow());
        btnFocusMode.setOnClickListener(v -> toggleFocusMode());
        btnManualFocus.setOnClickListener(v -> cycleManualFocusDistance());
        btnExposure.setOnClickListener(v -> cycleExposureCompensation());
        if (btnRotate != null) {
            btnRotate.setOnClickListener(v -> cycleRotation());
        }

        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);

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

        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, PERMISSION_REQUEST_CAMERA);
        } else {
            setupInitialCamera();
        }

        startControlServer();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions, @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == PERMISSION_REQUEST_CAMERA && grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            setupInitialCamera();
        } else {
            statusText.setText("Camera permission required");
        }
    }

    @Override
    public void onConfigurationChanged(@NonNull Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    private void displayNetworkInfo() {
        try {
            WifiManager wm = (WifiManager) getApplicationContext().getSystemService(WIFI_SERVICE);
            if (wm != null && wm.getConnectionInfo() != null) {
                String ip = Formatter.formatIpAddress(wm.getConnectionInfo().getIpAddress());
                streamInfoText.setText("IP: " + ip + " | Port: " + STREAM_PORT + " (USB ADB / WiFi)");
                return;
            }
        } catch (Exception ignored) {}
        streamInfoText.setText("IP: (ADB USB Mode) | Port: " + STREAM_PORT);
    }

    private void setupInitialCamera() {
        try {
            String defaultId = findCameraIdForFacing(CameraCharacteristics.LENS_FACING_BACK);
            if (defaultId == null && cameraManager.getCameraIdList().length > 0) {
                defaultId = cameraManager.getCameraIdList()[0];
            }
            if (defaultId != null) {
                currentCameraId = defaultId;
                CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(currentCameraId);
                Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
                if (facing != null) currentLensFacing = facing;
                initZoomParams(characteristics);
                checkFlashSupport(characteristics);
            }
            updateCameraIndicator();
            updateTorchButtonState();
        } catch (CameraAccessException e) {
            statusText.setText("Error reading cameras: " + e.getMessage());
        }
    }

    // [AI-BLOCK: Hardware Flash / Torch Detection and Brightness Support]
    private void checkFlashSupport(CameraCharacteristics characteristics) {
        Boolean hasFlash = characteristics.get(CameraCharacteristics.FLASH_INFO_AVAILABLE);
        isFlashSupported = (hasFlash != null && hasFlash);
        maxTorchLevel = 1;
        if (isFlashSupported && Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            Integer maxLevel = characteristics.get(CameraCharacteristics.FLASH_INFO_STRENGTH_MAXIMUM_LEVEL);
            if (maxLevel != null && maxLevel > 1) {
                maxTorchLevel = maxLevel;
            }
        }
        if (!isFlashSupported) {
            torchState = 0;
        }
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
            if (maxTorchLevel > 1) {
                if (torchState == 0) btnTorch.setText("Torch: OFF");
                else if (torchState == 1) btnTorch.setText("Torch: Low");
                else btnTorch.setText("Torch: High");
            } else {
                btnTorch.setText(torchState > 0 ? "Torch: ON" : "Torch: OFF");
            }
        }
    }

    private void cycleTorch() {
        if (!isFlashSupported) return;
        if (maxTorchLevel > 1) {
            torchState = (torchState + 1) % 3; // 0 = OFF, 1 = Low, 2 = High
        } else {
            torchState = (torchState == 0) ? 1 : 0;
        }
        updateTorchButtonState();
        applyTorchMode();
    }

    private void applyTorchMode() {
        if (captureRequestBuilder != null && captureSession != null && isStreaming) {
            try {
                if (torchState > 0) {
                    captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_TORCH);
                } else {
                    captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF);
                }
                if (backgroundHandler != null) {
                    captureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
                }
            } catch (Exception ignored) {}
        } else if (!isStreaming && currentCameraId != null && isFlashSupported) {
            try {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && maxTorchLevel > 1) {
                    if (torchState == 1) {
                        int lowLevel = Math.max(1, maxTorchLevel / 3);
                        cameraManager.turnOnTorchWithStrengthLevel(currentCameraId, lowLevel);
                    } else if (torchState == 2) {
                        cameraManager.turnOnTorchWithStrengthLevel(currentCameraId, maxTorchLevel);
                    } else {
                        cameraManager.setTorchMode(currentCameraId, false);
                    }
                } else {
                    cameraManager.setTorchMode(currentCameraId, torchState > 0);
                }
            } catch (Exception ignored) {}
        }
    }

    // [AI-BLOCK: Front Screen Glow Ring Light with Adjustable Color and Screen Brightness]
    private void cycleScreenGlow() {
        screenGlowState = (screenGlowState + 1) % GLOW_NAMES.length;
        applyScreenGlow();
    }

    private void applyScreenGlow() {
        if (btnScreenGlow != null) {
            btnScreenGlow.setText("Glow: " + GLOW_NAMES[screenGlowState]);
        }
        if (screenGlowBorder != null) {
            screenGlowBorder.setBackgroundColor(GLOW_COLORS[screenGlowState]);
        }

        WindowManager.LayoutParams layoutParams = getWindow().getAttributes();
        if (originalScreenBrightness < 0) {
            originalScreenBrightness = layoutParams.screenBrightness;
        }

        if (screenGlowState > 0) {
            layoutParams.screenBrightness = WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_FULL;
        } else {
            layoutParams.screenBrightness = originalScreenBrightness >= 0 ? originalScreenBrightness : WindowManager.LayoutParams.BRIGHTNESS_OVERRIDE_NONE;
        }
        getWindow().setAttributes(layoutParams);
    }

    private String findCameraIdForFacing(int desiredFacing) {
        try {
            for (String id : cameraManager.getCameraIdList()) {
                CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(id);
                Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
                if (facing != null && facing == desiredFacing) {
                    return id;
                }
            }
        } catch (Exception ignored) {}
        return null;
    }

    private void updateCameraIndicator() {
        String facingName = (currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) ? "FRONT" : "BACK";
        cameraIndicatorText.setText("Lens: " + facingName + " [" + currentCameraId + "]");
        btnSwitchCam.setText("Flip (" + facingName + ")");
    }

    private void initZoomParams(CameraCharacteristics characteristics) {
        Float max = characteristics.get(CameraCharacteristics.SCALER_AVAILABLE_MAX_DIGITAL_ZOOM);
        maxZoom = (max != null) ? max : 1.0f;
        sensorArraySize = characteristics.get(CameraCharacteristics.SENSOR_INFO_ACTIVE_ARRAY_SIZE);
        currentZoom = 1.0f;

        Float minFocus = characteristics.get(CameraCharacteristics.LENS_INFO_MINIMUM_FOCUS_DISTANCE);
        minimumFocusDistance = (minFocus != null) ? minFocus : 0f;
        exposureRange = characteristics.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_RANGE);
        exposureStep = characteristics.get(CameraCharacteristics.CONTROL_AE_COMPENSATION_STEP);
        currentFocusDistance = 0f;
        currentExposureCompensation = 0;
        runOnUiThread(this::updateFocusAndExposureUI);
    }

    // [AI-BLOCK: Manual and Auto Focus & Exposure Compensation Sync]
    private void updateFocusAndExposureUI() {
        if (btnFocusMode != null) {
            btnFocusMode.setText(isAutoFocus ? "AF: Auto" : "AF: Manual");
            btnFocusMode.setBackgroundColor(isAutoFocus ? 0xFF238636 : 0xFF1F6FEB);
        }
        if (btnManualFocus != null) {
            if (isAutoFocus) {
                btnManualFocus.setText("Focus: Auto");
                btnManualFocus.setEnabled(false);
                btnManualFocus.setAlpha(0.5f);
            } else {
                btnManualFocus.setEnabled(true);
                btnManualFocus.setAlpha(1.0f);
                if (currentFocusDistance <= 0.05f) {
                    btnManualFocus.setText("Focus: Inf");
                } else if (minimumFocusDistance > 0 && currentFocusDistance >= minimumFocusDistance * 0.8f) {
                    btnManualFocus.setText("Focus: Macro");
                } else {
                    btnManualFocus.setText(String.format(java.util.Locale.US, "Focus: %.1fm", 1.0f / Math.max(0.1f, currentFocusDistance)));
                }
            }
        }
        if (btnExposure != null) {
            float evVal = (exposureStep != null) ? currentExposureCompensation * exposureStep.floatValue() : currentExposureCompensation;
            btnExposure.setText(String.format(java.util.Locale.US, "EV: %+.1f", evVal));
        }
    }

    private void toggleFocusMode() {
        isAutoFocus = !isAutoFocus;
        if (isAutoFocus) {
            currentFocusDistance = 0f;
        }
        updateFocusAndExposureUI();
        applyFocusAndExposure();
    }

    private void cycleManualFocusDistance() {
        if (isAutoFocus) {
            isAutoFocus = false;
        }
        if (minimumFocusDistance <= 0) {
            currentFocusDistance = 0f;
        } else {
            // Steps: 0 (inf), 0.25 min, 0.5 min, 0.75 min, 1.0 min (macro)
            float step = minimumFocusDistance / 4f;
            currentFocusDistance += step;
            if (currentFocusDistance > minimumFocusDistance + 0.01f) {
                currentFocusDistance = 0f;
            }
        }
        updateFocusAndExposureUI();
        applyFocusAndExposure();
    }

    private void cycleExposureCompensation() {
        if (exposureRange == null) return;
        currentExposureCompensation += 2;
        if (currentExposureCompensation > exposureRange.getUpper()) {
            currentExposureCompensation = exposureRange.getLower();
        }
        updateFocusAndExposureUI();
        applyFocusAndExposure();
    }

    private void setFocusDirect(boolean autoFocus, float focusDistance) {
        isAutoFocus = autoFocus;
        currentFocusDistance = Math.max(0f, Math.min(minimumFocusDistance, focusDistance));
        runOnUiThread(this::updateFocusAndExposureUI);
        applyFocusAndExposure();
    }

    private void setExposureDirect(int compensationIndex) {
        if (exposureRange != null) {
            currentExposureCompensation = Math.max(exposureRange.getLower(), Math.min(exposureRange.getUpper(), compensationIndex));
        } else {
            currentExposureCompensation = compensationIndex;
        }
        runOnUiThread(this::updateFocusAndExposureUI);
        applyFocusAndExposure();
    }

    private void applyFocusAndExposure() {
        if (captureRequestBuilder == null || captureSession == null) return;
        try {
            if (isAutoFocus) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
            } else {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF);
                captureRequestBuilder.set(CaptureRequest.LENS_FOCUS_DISTANCE, currentFocusDistance);
            }

            if (exposureRange != null) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, currentExposureCompensation);
            }

            if (backgroundHandler != null) {
                captureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
            }
        } catch (Exception ignored) {}
    }

    private void toggleMirror() {
        isMirrored = !isMirrored;
        btnMirror.setText(isMirrored ? "Mirror: ON" : "Mirror: OFF");
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    // [AI-BLOCK: Software Camera Rotation (0, 90, 180, 270 degrees) for upside-down & custom mounts]
    private void cycleRotation() {
        manualRotationAngle = (manualRotationAngle + 90) % 360;
        updateRotationButtonState();
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    private void setRotationDirect(int angle) {
        manualRotationAngle = ((angle % 360) + 360) % 360;
        updateRotationButtonState();
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    private void updateRotationButtonState() {
        if (btnRotate != null) {
            btnRotate.setText("Rotate: " + manualRotationAngle + "°");
        }
    }

    private void cycleResolution() {
        currentResIndex = (currentResIndex + 1) % RESOLUTIONS.length;
        setResolutionDirect(RESOLUTIONS[currentResIndex][0], RESOLUTIONS[currentResIndex][1]);
    }

    private void setResolutionDirect(int width, int height) {
        targetWidth = width;
        targetHeight = height;
        for (int i = 0; i < RESOLUTIONS.length; i++) {
            if (RESOLUTIONS[i][0] == width && RESOLUTIONS[i][1] == height) {
                currentResIndex = i;
                break;
            }
        }
        btnResolution.setText("Res: " + RES_LABELS[currentResIndex]);
        if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }

        if (isStreaming && backgroundHandler != null) {
            backgroundHandler.post(() -> {
                closeCamera();
                stopEncoder();
                openCamera(targetWidth, targetHeight);
            });
        }
    }

    // [AI-BLOCK: Multi-Device Responsive Viewport Transform and Aspect Ratio Fitting]
    private void configureTransform(int viewWidth, int viewHeight) {
        if (previewView == null || !previewView.isAvailable() || targetWidth == 0 || targetHeight == 0) {
            return;
        }
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
        }

        if (manualRotationAngle != 0) {
            matrix.postRotate(manualRotationAngle, centerX, centerY);
        }

        if (isMirrored) {
            matrix.postScale(-1, 1, centerX, centerY);
        }

        previewView.setTransform(matrix);
    }

    // [AI-BLOCK: Background Thread Setup]
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
            } catch (InterruptedException ignored) {}
        }
    }

    // [AI-BLOCK: Camera2 Initialization and Session]
    private void openCamera(int width, int height) {
        if (checkSelfPermission(Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) return;
        if (currentCameraId == null) return;
        try {
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
            captureRequestBuilder.set(CaptureRequest.CONTROL_MODE, CameraMetadata.CONTROL_MODE_AUTO);
            applyZoom(captureRequestBuilder);
            if (isFlashSupported && torchState > 0) {
                captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_TORCH);
            } else {
                captureRequestBuilder.set(CaptureRequest.FLASH_MODE, CaptureRequest.FLASH_MODE_OFF);
            }

            if (isAutoFocus) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_CONTINUOUS_PICTURE);
            } else {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AF_MODE, CaptureRequest.CONTROL_AF_MODE_OFF);
                captureRequestBuilder.set(CaptureRequest.LENS_FOCUS_DISTANCE, currentFocusDistance);
            }

            if (exposureRange != null) {
                captureRequestBuilder.set(CaptureRequest.CONTROL_AE_EXPOSURE_COMPENSATION, currentExposureCompensation);
            }

            cameraDevice.createCaptureSession(Arrays.asList(previewSurface, encoderInputSurface),
                new CameraCaptureSession.StateCallback() {
                    @Override
                    public void onConfigured(@NonNull CameraCaptureSession session) {
                        if (cameraDevice == null) return;
                        captureSession = session;
                        try {
                            captureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
                            runOnUiThread(() -> statusText.setText("Otter: Streaming Active"));
                        } catch (Exception e) {
                            runOnUiThread(() -> statusText.setText("Session Error: " + e.getMessage()));
                        }
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

    // [AI-BLOCK: Hardware H.264 Encoder]
    private synchronized void setupEncoder(int width, int height) throws Exception {
        stopEncoder();
        cachedSpsPps = null;
        MediaFormat format = MediaFormat.createVideoFormat(MediaFormat.MIMETYPE_VIDEO_AVC, width, height);
        format.setInteger(MediaFormat.KEY_COLOR_FORMAT, MediaCodecInfo.CodecCapabilities.COLOR_FormatSurface);
        format.setInteger(MediaFormat.KEY_BIT_RATE, 4000000); // 4 Mbps
        format.setInteger(MediaFormat.KEY_FRAME_RATE, 30);
        format.setInteger(MediaFormat.KEY_I_FRAME_INTERVAL, 1);

        mediaCodec = MediaCodec.createEncoderByType(MediaFormat.MIMETYPE_VIDEO_AVC);
        mediaCodec.configure(format, null, null, MediaCodec.CONFIGURE_FLAG_ENCODE);
        encoderInputSurface = mediaCodec.createInputSurface();
        mediaCodec.start();
    }

    private synchronized void stopEncoder() {
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

    private void drainEncoderLoop() {
        MediaCodec.BufferInfo bufferInfo = new MediaCodec.BufferInfo();
        while (isStreaming) {
            if (isPaused || mediaCodec == null) {
                try { Thread.sleep(30); } catch (InterruptedException ignored) {}
                continue;
            }
            try {
                MediaCodec codec = mediaCodec;
                if (codec == null) continue;
                int outputBufferIndex = codec.dequeueOutputBuffer(bufferInfo, 10000);
                if (outputBufferIndex >= 0) {
                    ByteBuffer outputBuffer = codec.getOutputBuffer(outputBufferIndex);
                    if (outputBuffer != null && bufferInfo.size > 0) {
                        byte[] outData = new byte[bufferInfo.size];
                        outputBuffer.get(outData);
                        if ((bufferInfo.flags & MediaCodec.BUFFER_FLAG_CODEC_CONFIG) != 0) {
                            cachedSpsPps = outData;
                        }
                        sendVideoPacket(outData);
                    }
                    codec.releaseOutputBuffer(outputBufferIndex, false);
                }
            } catch (IllegalStateException e) {
                try { Thread.sleep(50); } catch (InterruptedException ignored) {}
            } catch (Exception ignored) {
                break;
            }
        }
    }

    // [AI-BLOCK: TCP Video Stream Server]
    private void startVideoServer() {
        new Thread(() -> {
            try {
                videoServerSocket = new ServerSocket(STREAM_PORT);
                while (isStreaming) {
                    Socket client = videoServerSocket.accept();
                    synchronized (this) {
                        if (activeVideoClient != null) {
                            try { activeVideoClient.close(); } catch (Exception ignored) {}
                        }
                        activeVideoClient = client;
                        videoOutputStream = client.getOutputStream();
                        // Immediately dispatch cached SPS/PPS header so receiver initializes without delay
                        if (cachedSpsPps != null) {
                            sendVideoPacket(cachedSpsPps);
                        }
                        // Request immediate IDR keyframe from hardware encoder for fresh client
                        if (mediaCodec != null) {
                            try {
                                Bundle syncBundle = new Bundle();
                                syncBundle.putInt(MediaCodec.PARAMETER_KEY_REQUEST_SYNC_FRAME, 0);
                                mediaCodec.setParameters(syncBundle);
                            } catch (Exception ignored) {}
                        }
                    }
                    runOnUiThread(() -> statusText.setText("Otter: PC Connected"));
                }
            } catch (Exception ignored) {}
        }).start();
    }

    private synchronized void sendVideoPacket(byte[] data) {
        if (videoOutputStream != null && !isPaused) {
            try {
                ByteBuffer header = ByteBuffer.allocate(4);
                header.putInt(data.length);
                videoOutputStream.write(header.array());
                videoOutputStream.write(data);
                videoOutputStream.flush();
            } catch (Exception e) {
                try {
                    if (activeVideoClient != null) activeVideoClient.close();
                } catch (Exception ignored) {}
                activeVideoClient = null;
                videoOutputStream = null;
                runOnUiThread(() -> statusText.setText("Otter: PC Disconnected"));
            }
        }
    }

    // [AI-BLOCK: Bidirectional RPC Control Server]
    private void startControlServer() {
        new Thread(() -> {
            try {
                controlServerSocket = new ServerSocket(CONTROL_PORT);
                while (!isFinishing()) {
                    Socket client = controlServerSocket.accept();
                    BufferedReader reader = new BufferedReader(new InputStreamReader(client.getInputStream()));
                    OutputStream out = client.getOutputStream();
                    String line = reader.readLine();
                    if (line != null) {
                        String response = handleControlCommand(line);
                        out.write((response + "\n").getBytes());
                        out.flush();
                    }
                    client.close();
                }
            } catch (Exception ignored) {}
        }).start();
    }

    private String handleControlCommand(String jsonCommand) {
        try {
            JSONObject cmd = new JSONObject(jsonCommand);
            String action = cmd.optString("action");
            switch (action) {
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
                    runOnUiThread(() -> setRotationDirect(rotAngle));
                    return "{\"status\":\"ok\",\"rotationAngle\":" + rotAngle + "}";
                case "set_resolution":
                    int resW = cmd.optInt("width", 1280);
                    int resH = cmd.optInt("height", 720);
                    runOnUiThread(() -> setResolutionDirect(resW, resH));
                    return "{\"status\":\"ok\",\"width\":" + resW + ",\"height\":" + resH + "}";
                case "zoom_in":
                    zoomStep(0.2f);
                    return "{\"status\":\"ok\",\"zoom\":" + currentZoom + "}";
                case "zoom_out":
                    zoomStep(-0.2f);
                    return "{\"status\":\"ok\",\"zoom\":" + currentZoom + "}";
                case "toggle_torch":
                    runOnUiThread(this::cycleTorch);
                    return "{\"status\":\"ok\",\"torchSupported\":" + isFlashSupported + ",\"torchState\":" + torchState + "}";
                case "toggle_glow":
                    runOnUiThread(this::cycleScreenGlow);
                    return "{\"status\":\"ok\",\"glowState\":" + screenGlowState + ",\"glowName\":\"" + GLOW_NAMES[screenGlowState] + "\"}";
                case "toggle_af":
                    runOnUiThread(this::toggleFocusMode);
                    return "{\"status\":\"ok\",\"isAutoFocus\":" + isAutoFocus + "}";
                case "set_focus":
                    boolean af = cmd.optBoolean("auto", true);
                    float dist = (float) cmd.optDouble("distance", 0.0);
                    runOnUiThread(() -> setFocusDirect(af, dist));
                    return "{\"status\":\"ok\",\"isAutoFocus\":" + af + ",\"focusDistance\":" + dist + "}";
                case "cycle_focus":
                    runOnUiThread(this::cycleManualFocusDistance);
                    return "{\"status\":\"ok\",\"isAutoFocus\":" + isAutoFocus + ",\"focusDistance\":" + currentFocusDistance + "}";
                case "cycle_exposure":
                    runOnUiThread(this::cycleExposureCompensation);
                    return "{\"status\":\"ok\",\"exposureCompensation\":" + currentExposureCompensation + "}";
                case "set_exposure":
                    int expVal = cmd.optInt("value", 0);
                    runOnUiThread(() -> setExposureDirect(expVal));
                    return "{\"status\":\"ok\",\"exposureCompensation\":" + expVal + "}";
                case "get_status":
                    float evVal = (exposureStep != null) ? currentExposureCompensation * exposureStep.floatValue() : currentExposureCompensation;
                    return "{\"status\":\"ok\",\"streaming\":" + isStreaming + ",\"zoom\":" + currentZoom +
                            ",\"lens\":\"" + ((currentLensFacing == CameraCharacteristics.LENS_FACING_FRONT) ? "FRONT" : "BACK") +
                            "\",\"mirrored\":" + isMirrored + ",\"rotationAngle\":" + manualRotationAngle +
                            ",\"width\":" + targetWidth + ",\"height\":" + targetHeight +
                            ",\"torchSupported\":" + isFlashSupported + ",\"torchState\":" + torchState +
                            ",\"glowState\":" + screenGlowState + ",\"glowName\":\"" + GLOW_NAMES[screenGlowState] + "\"" +
                            ",\"isAutoFocus\":" + isAutoFocus + ",\"focusDistance\":" + currentFocusDistance +
                            ",\"minFocusDistance\":" + minimumFocusDistance +
                            ",\"exposure\":" + currentExposureCompensation + ",\"ev\":" + evVal + "}";
                default:
                    return "{\"status\":\"error\",\"message\":\"unknown command\"}";
            }
        } catch (Exception e) {
            return "{\"status\":\"error\",\"message\":\"" + e.getMessage() + "\"}";
        }
    }

    private void zoomStep(float delta) {
        if (sensorArraySize == null || captureRequestBuilder == null || captureSession == null) return;
        currentZoom = Math.max(1.0f, Math.min(maxZoom, currentZoom + delta));
        applyZoom(captureRequestBuilder);
        if (backgroundHandler != null) {
            try {
                captureSession.setRepeatingRequest(captureRequestBuilder.build(), null, backgroundHandler);
            } catch (Exception ignored) {}
        }
    }

    private void applyZoom(CaptureRequest.Builder builder) {
        if (sensorArraySize == null) return;
        int cropW = (int) (sensorArraySize.width() / currentZoom);
        int cropH = (int) (sensorArraySize.height() / currentZoom);
        int cropX = (sensorArraySize.width() - cropW) / 2;
        int cropY = (sensorArraySize.height() - cropH) / 2;
        Rect cropRegion = new Rect(cropX, cropY, cropX + cropW, cropY + cropH);
        builder.set(CaptureRequest.SCALER_CROP_REGION, cropRegion);
    }

    // [AI-BLOCK: Safe Non-Crashing Camera Switching]
    private void switchCamera() {
        int targetFacing = (currentLensFacing == CameraCharacteristics.LENS_FACING_BACK) ?
                CameraCharacteristics.LENS_FACING_FRONT : CameraCharacteristics.LENS_FACING_BACK;
        String targetId = findCameraIdForFacing(targetFacing);
        if (targetId == null) {
            try {
                for (String id : cameraManager.getCameraIdList()) {
                    if (!id.equals(currentCameraId)) {
                        targetId = id;
                        break;
                    }
                }
            } catch (Exception ignored) {}
        }
        if (targetId == null) return;

        currentCameraId = targetId;
        try {
            CameraCharacteristics characteristics = cameraManager.getCameraCharacteristics(currentCameraId);
            Integer facing = characteristics.get(CameraCharacteristics.LENS_FACING);
            if (facing != null) {
                currentLensFacing = facing;
            }
            initZoomParams(characteristics);
            checkFlashSupport(characteristics);
        } catch (Exception ignored) {}

        updateCameraIndicator();
        updateTorchButtonState();

        if (isStreaming && backgroundHandler != null) {
            backgroundHandler.post(() -> {
                closeCamera();
                openCamera(targetWidth, targetHeight);
            });
        } else if (previewView != null && previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
        }
    }

    // [AI-BLOCK: Streaming Controls]
    private void startStreaming() {
        if (isStreaming) return;
        isStreaming = true;
        isPaused = false;
        startBackgroundThread();
        startVideoServer();
        new Thread(this::drainEncoderLoop).start();
        if (isBackgroundLockEnabled) {
            startForegroundStreamService();
        }
        if (previewView.isAvailable()) {
            configureTransform(previewView.getWidth(), previewView.getHeight());
            openCamera(targetWidth, targetHeight);
        }
    }

    private void togglePause() {
        isPaused = !isPaused;
        runOnUiThread(() -> {
            btnPause.setText(isPaused ? "Resume" : "Pause");
            statusText.setText(isPaused ? "Otter: Paused" : "Otter: Streaming Active");
        });
    }

    private void stopStreaming() {
        isStreaming = false;
        isPaused = false;
        stopForegroundStreamService();
        closeCamera();
        stopEncoder();
        stopBackgroundThread();
        if (videoServerSocket != null) {
            try { videoServerSocket.close(); } catch (Exception ignored) {}
        }
        runOnUiThread(() -> statusText.setText("Otter: Stopped"));
    }

    private void toggleBackgroundLock() {
        isBackgroundLockEnabled = !isBackgroundLockEnabled;
        btnBackgroundLock.setText(isBackgroundLockEnabled ? "Lock Mode: ON" : "Lock Mode: OFF");
        if (isStreaming) {
            if (isBackgroundLockEnabled) {
                startForegroundStreamService();
            } else {
                stopForegroundStreamService();
            }
        }
    }

    private void startForegroundStreamService() {
        if (!isBackgroundLockEnabled) return;
        try {
            Intent serviceIntent = new Intent(this, OtterStreamService.class);
            serviceIntent.setAction(OtterStreamService.ACTION_START);
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(serviceIntent);
            } else {
                startService(serviceIntent);
            }
        } catch (Exception ignored) {}
    }

    private void stopForegroundStreamService() {
        try {
            Intent serviceIntent = new Intent(this, OtterStreamService.class);
            serviceIntent.setAction(OtterStreamService.ACTION_STOP);
            startService(serviceIntent);
        } catch (Exception ignored) {}
    }

    private void showBatteryGuideDialog() {
        new AlertDialog.Builder(this)
            .setTitle("Prevent Background Killing")
            .setMessage("Aggressive OEM battery managers may kill the camera stream when your phone is locked or screen is off:\n\n" +
                    "• Xiaomi / MIUI / HyperOS:\n  Settings -> Apps -> Manage Apps -> Otter -> Turn ON 'Autostart', and set Battery Saver to 'No restrictions'. Lock in Recent apps.\n\n" +
                    "• Samsung One UI:\n  Settings -> Battery -> Background usage limits -> Never sleeping apps -> Add Otter. Also set App Battery to 'Unrestricted'.\n\n" +
                    "• ColorOS / Realme / OnePlus:\n  App Info -> Battery usage -> Enable 'Allow background activity' and 'Allow auto-launch'.\n\n" +
                    "• Vivo / FuntouchOS:\n  Settings -> Battery -> High background power consumption -> Allow Otter.")
            .setPositiveButton("Open Battery Settings", (dialog, which) -> requestBatteryOptimizationExemption())
            .setNegativeButton("Close", null)
            .show();
    }

    private void requestBatteryOptimizationExemption() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            try {
                PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
                if (pm != null && !pm.isIgnoringBatteryOptimizations(getPackageName())) {
                    Intent intent = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS);
                    intent.setData(Uri.parse("package:" + getPackageName()));
                    startActivity(intent);
                    return;
                }
            } catch (Exception ignored) {}
            try {
                startActivity(new Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS));
            } catch (Exception ignored) {}
        }
    }

    private void closeCamera() {
        if (captureSession != null) {
            try {
                captureSession.stopRepeating();
                captureSession.abortCaptures();
                captureSession.close();
            } catch (Exception ignored) {}
            captureSession = null;
        }
        if (cameraDevice != null) {
            try { cameraDevice.close(); } catch (Exception ignored) {}
            cameraDevice = null;
        }
        if (currentCameraId != null && isFlashSupported) {
            try { cameraManager.setTorchMode(currentCameraId, false); } catch (Exception ignored) {}
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        stopStreaming();
        if (controlServerSocket != null) {
            try { controlServerSocket.close(); } catch (Exception ignored) {}
        }
    }
}

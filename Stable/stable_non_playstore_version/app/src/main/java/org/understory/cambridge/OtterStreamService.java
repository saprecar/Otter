package org.understory.cambridge;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;
import android.os.PowerManager;

// [AI-BLOCK: Foreground Service displaying live camera active notification & managing background lock]
public class OtterStreamService extends Service {

    public static final String ACTION_START = "ACTION_START";
    public static final String ACTION_STOP = "ACTION_STOP";
    private static final String CHANNEL_ID = "otter_stream_channel";
    private static final int NOTIFICATION_ID = 1001;

    private PowerManager.WakeLock wakeLock;

    @Override
    public void onCreate() {
        super.onCreate();
        createNotificationChannel();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        if (intent != null && ACTION_STOP.equals(intent.getAction())) {
            stopForegroundService();
            return START_NOT_STICKY;
        }

        startOrUpdateNotification(intent);
        return START_STICKY;
    }

    private void startOrUpdateNotification(Intent intent) {
        boolean enableWakeLock = true;
        boolean isPaused = false;
        String statusText = "Camera is actively streaming on port 8089";

        if (intent != null) {
            enableWakeLock = intent.getBooleanExtra("ENABLE_WAKELOCK", true);
            isPaused = intent.getBooleanExtra("IS_PAUSED", false);
            if (intent.hasExtra("STREAM_STATUS")) {
                statusText = intent.getStringExtra("STREAM_STATUS");
            }
        }

        if (enableWakeLock) {
            acquireWakeLock();
        } else {
            releaseWakeLock();
        }

        Intent notificationIntent = new Intent(this, MainActivity.class);
        notificationIntent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pendingIntent = PendingIntent.getActivity(
                this, 0, notificationIntent,
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0
        );

        Intent stopIntent = new Intent(this, MainActivity.class);
        stopIntent.setAction("ACTION_STOP_STREAM");
        stopIntent.setFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent stopPendingIntent = PendingIntent.getActivity(
                this, 1, stopIntent,
                Build.VERSION.SDK_INT >= Build.VERSION_CODES.M ? PendingIntent.FLAG_IMMUTABLE : 0
        );

        Notification.Builder builder;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            builder = new Notification.Builder(this, CHANNEL_ID);
        } else {
            builder = new Notification.Builder(this);
        }

        String title = isPaused ? "Otter Camera: Paused" : "Otter Camera: LIVE";
        builder.setContentTitle(title)
                .setContentText(statusText)
                .setSmallIcon(R.drawable.ic_otter)
                .setContentIntent(pendingIntent)
                .setOngoing(!isPaused)
                .addAction(android.R.drawable.ic_menu_close_clear_cancel, "Stop Stream", stopPendingIntent);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
            builder.setSubText("Camera in use");
        }

        Notification notification = builder.build();

        if (Build.VERSION.SDK_INT >= 34) { // Android 14+
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA);
        } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) { // Android 10+
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_CAMERA);
        } else {
            startForeground(NOTIFICATION_ID, notification);
        }
    }

    private void acquireWakeLock() {
        if (wakeLock == null) {
            PowerManager powerManager = (PowerManager) getSystemService(Context.POWER_SERVICE);
            if (powerManager != null) {
                wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "otter:streaming_wakelock");
                wakeLock.setReferenceCounted(false);
            }
        }
        if (wakeLock != null && !wakeLock.isHeld()) {
            wakeLock.acquire();
        }
    }

    private void releaseWakeLock() {
        if (wakeLock != null && wakeLock.isHeld()) {
            try {
                wakeLock.release();
            } catch (Exception ignored) {}
        }
    }

    private void stopForegroundService() {
        releaseWakeLock();
        stopForeground(true);
        stopSelf();
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Otter Camera Live Service",
                    NotificationManager.IMPORTANCE_LOW
            );
            channel.setDescription("Notifies user that camera is actively streaming in background");
            NotificationManager manager = getSystemService(NotificationManager.class);
            if (manager != null) {
                manager.createNotificationChannel(channel);
            }
        }
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        stopForegroundService();
    }

    @Override
    public IBinder onBind(Intent intent) {
        return null;
    }
}

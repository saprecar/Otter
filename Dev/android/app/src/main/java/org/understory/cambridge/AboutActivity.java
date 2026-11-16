package org.understory.cambridge;

import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.widget.Button;
import android.widget.Toast;

// [AI-BLOCK: Dedicated About & Troubleshooting Window for Otter mobile app]
public class AboutActivity extends Activity {

    private static final String REPO_URL = "https://github.com/saprecar/Otter";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about);

        Button btnClose = findViewById(R.id.btnCloseAbout);
        Button btnOpenRepo = findViewById(R.id.btnOpenRepo);
        Button btnCopyRepo = findViewById(R.id.btnCopyRepo);
        Button btnOpenBattery = findViewById(R.id.btnOpenBatterySettings);

        btnClose.setOnClickListener(v -> finish());

        btnOpenRepo.setOnClickListener(v -> {
            try {
                Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(REPO_URL));
                startActivity(intent);
            } catch (Exception e) {
                Toast.makeText(this, "Could not open browser: " + e.getMessage(), Toast.LENGTH_SHORT).show();
            }
        });

        btnCopyRepo.setOnClickListener(v -> {
            ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
            ClipData clip = ClipData.newPlainText("Otter Repo", REPO_URL);
            if (clipboard != null) {
                clipboard.setPrimaryClip(clip);
                Toast.makeText(this, "Repo link copied to clipboard!", Toast.LENGTH_SHORT).show();
            }
        });

        btnOpenBattery.setOnClickListener(v -> openBatteryOptimization());
    }

    private void openBatteryOptimization() {
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
}

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
import android.widget.TextView;
import android.widget.Toast;

// [AI-BLOCK: Dedicated About & Troubleshooting Window for Otter mobile app]
public class AboutActivity extends Activity {

    private static final String REPO_URL = "https://github.com/saprecar/Otter";
    private static final String POLICY_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md";
    private static final String ATTRIBUTION_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/ATTRIBUTION_AND_LICENSES.md";
    private static final String LICENSE_URL = "https://github.com/saprecar/Otter/blob/main/LICENSE";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_about);

        // [AI-BLOCK: Populate version from PackageManager at runtime]
        android.widget.TextView tvVersion = findViewById(R.id.tvAboutVersion);
        if (tvVersion != null) {
            try {
                android.content.pm.PackageInfo pInfo = getPackageManager().getPackageInfo(getPackageName(), 0);
                String vName = pInfo.versionName != null ? pInfo.versionName : "1.3.0.0";
                long vCode = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P ? pInfo.getLongVersionCode() : pInfo.versionCode;
                tvVersion.setText("Otter v" + vName + " (build " + vCode + ")");
            } catch (Exception e) {
                tvVersion.setText("Otter v1.3.0.0");
            }
        }
        Button btnClose = findViewById(R.id.btnCloseAbout);
        Button btnOpenRepo = findViewById(R.id.btnOpenRepo);
        Button btnCopyRepo = findViewById(R.id.btnCopyRepo);
        Button btnCopyPc = findViewById(R.id.btnCopyPcInstructions);
        Button btnOpenBattery = findViewById(R.id.btnOpenBatterySettings);

        btnClose.setOnClickListener(v -> finish());

        if (btnCopyPc != null) {
            btnCopyPc.setOnClickListener(v -> {
                String instructions = "Otter PC Desktop Client Setup:\n" +
                        "1. Download Otter on PC: " + REPO_URL + "\n" +
                        "2. Click Code -> Download ZIP and extract on computer.\n" +
                        "3. Run the one-click launcher:\n" +
                        "   - Windows: double-click run_windows.bat\n" +
                        "   - Linux: ./run_linux.sh\n" +
                        "   - macOS: double-click run_macos.command\n" +
                        "   - Or run: python Dev/desktop/otter_app.py\n" +
                        "4. Click 'Connect & Start' on PC controller to register Virtual Webcam.";
                ClipboardManager clipboard = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                if (clipboard != null) {
                    clipboard.setPrimaryClip(ClipData.newPlainText("Otter PC Setup", instructions));
                    Toast.makeText(this, "PC Setup instructions copied to clipboard!", Toast.LENGTH_SHORT).show();
                }
            });
        }

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

        Button btnPrivacy = findViewById(R.id.btnViewPrivacyPolicy);
        if (btnPrivacy != null) {
            btnPrivacy.setOnClickListener(v -> {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(POLICY_URL)));
                } catch (Exception e) {
                    Toast.makeText(this, "Could not open browser: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }

        Button btnTerms = findViewById(R.id.btnViewUserAgreement);
        if (btnTerms != null) {
            btnTerms.setOnClickListener(v -> {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(ATTRIBUTION_URL)));
                } catch (Exception e) {
                    Toast.makeText(this, "Could not open browser: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }

        Button btnLicense = findViewById(R.id.btnViewLicense);
        if (btnLicense != null) {
            btnLicense.setOnClickListener(v -> {
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(LICENSE_URL)));
                } catch (Exception e) {
                    Toast.makeText(this, "Could not open browser: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }

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

import sys
import os

# Ensure local script directory is root of module resolution
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
import subprocess

try:
    from adb_tunnel import ADBTunnel
    from cambridge_control import CamBridgeControl
    from cambridge_receiver import CamBridgeReceiver
    import manage_dependencies
    import manage_adb
    import network_discovery
except ImportError:
    from Dev.desktop.adb_tunnel import ADBTunnel
    from Dev.desktop.cambridge_control import CamBridgeControl
    from Dev.desktop.cambridge_receiver import CamBridgeReceiver
    import Dev.desktop.manage_dependencies as manage_dependencies
    import Dev.desktop.manage_adb as manage_adb
    import Dev.desktop.network_discovery as network_discovery

# [AI-BLOCK: Otter Desktop Controller GUI for Virtual Camera, Controls, Dependency Manager & OEM Anti-Kill]
class OtterApp:
    ISO_VALUES = [100, 200, 400, 800, 1600, 3200]
    SHUTTER_STEPS = [
        (500_000, "1/2000s"),
        (1_000_000, "1/1000s"),
        (2_000_000, "1/500s"),
        (4_000_000, "1/250s"),
        (8_000_000, "1/125s"),
        (16_666_666, "1/60s"),
        (33_333_333, "1/30s"),
        (66_666_666, "1/15s")
    ]
    WB_MODES = [
        (1, "Daylight (5500K)"),
        (2, "Cloudy (6500K)"),
        (3, "Fluorescent (4000K)"),
        (4, "Tungsten (2800K)")
    ]
    FX_MODES = [
        (1, "Mono / B&W"),
        (2, "Negative"),
        (3, "Sepia")
    ]

    MASTER_POLICY_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/POLICIES_AND_AGREEMENT.md"
    ATTRIBUTION_URL = "https://github.com/saprecar/Otter/blob/main/Policies%20And%20Agreement/ATTRIBUTION_AND_LICENSES.md"
    LICENSE_URL = "https://github.com/saprecar/Otter/blob/main/LICENSE"
    POLICY_VERSION = "1.1.0.0"

    def __init__(self, root):
        self.root = root
        self.root.title("Otter - Virtual Camera Controller")
        self.root.geometry("880x780")
        self.root.minsize(820, 640)
        self.root.configure(bg="#0D1117")

        self.receiver = None
        self.receiver_thread = None
        self.adb_tunnel = None
        self.controller = None
        self.is_connected = False
        self.current_zoom = 1.0
        self.is_mirrored = False
        self._debounce_timers = {}

        self.iso_auto_var = tk.BooleanVar(value=True)
        self.shutter_auto_var = tk.BooleanVar(value=True)
        self.wb_auto_var = tk.BooleanVar(value=True)
        self.fx_auto_var = tk.BooleanVar(value=True)

        self._setup_styles()
        self._build_header()
        self._build_notebook()
        self._build_statusbar()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        threading.Thread(target=self._poll_status_loop, daemon=True).start()
        self.root.after(100, self._check_consent_policy)

    def _check_consent_policy(self):
        consent_path = os.path.expanduser("~/.otter_consent.json")
        has_consented = False
        if os.path.exists(consent_path):
            try:
                import json
                with open(consent_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("accepted_version") == self.POLICY_VERSION:
                        has_consented = True
            except Exception:
                has_consented = False

        if not has_consented:
            self._show_consent_modal(consent_path)

    def _show_consent_modal(self, consent_path):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - Terms of Service & Privacy Policy Consent")
        dlg.geometry("640x540")
        dlg.minsize(580, 500)
        dlg.configure(bg="#0D1117")
        dlg.transient(self.root)
        dlg.grab_set()

        def _on_decline():
            dlg.destroy()
            self.root.destroy()
            sys.exit(0)

        dlg.protocol("WM_DELETE_WINDOW", _on_decline)

        card = tk.Frame(dlg, bg="#161B22", padx=20, pady=20)
        card.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        tk.Label(card, text="Welcome to Otter", font=("Segoe UI", 16, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 4))
        tk.Label(card, text="Please review and agree to the Terms of Service & Privacy Policy to continue.", font=("Segoe UI", 10), fg="#8B949E", bg="#161B22").pack(anchor="w", pady=(0, 10))

        summary_box = tk.LabelFrame(card, text=" Operational & Privacy Summary ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 9, "bold"), padx=12, pady=10)
        summary_box.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        summary_text = (
            "• 100% Local Peer-to-Peer Architecture:\n"
            "  All video decoding, remote control, and virtual camera feeds operate strictly\n"
            "  on your local computer and private network. No video or telemetry is sent to external servers.\n\n"
            "• Zero Developer Data Ingestion & Deletion Inapplicability:\n"
            "  We do NOT collect, store, monetize, or transmit personal data or device identifiers.\n"
            "  Because zero data is ingested by developers, data deletion on developer servers is not applicable.\n\n"
            "• Third-Party, Store & OEM Disclaimers:\n"
            "  Any telemetry collected by Google Play Services, Android OS, or device manufacturers\n"
            "  (MIUI/HyperOS, ColorOS, Funtouch OS, One UI) is solely governed by their respective policies.\n\n"
            "• Absolute Disclaimer of Warranties & Liability ('AS-IS'):\n"
            "  The software is provided without warranties. Developers hold zero liability for local network\n"
            "  interception, data loss, packet eavesdropping, hardware stress, or software bugs.\n\n"
            "• Mandatory Attribution Clause:\n"
            "  Any reuse, redistribution, or derivation must prominently credit 'spacecar', name 'Otter',\n"
            "  and link to https://github.com/saprecar/Otter.\n\n"
            "• Governing Law & Exclusive Jurisdiction:\n"
            "  Governed by the Laws of the Republic of India (Information Technology Act, 2000).\n"
            "  Exclusive jurisdiction: Competent Courts of Narmadapuram, Madhya Pradesh, India\n"
            "  (PIN: 461001 / 461005)."
        )
        tk.Label(summary_box, text=summary_text, font=("Segoe UI", 9), fg="#C9D1D9", bg="#161B22", justify=tk.LEFT, anchor="w").pack(fill=tk.BOTH, expand=True)

        links_frame = tk.Frame(card, bg="#161B22")
        links_frame.pack(fill=tk.X, pady=(0, 14))

        tk.Label(links_frame, text="Review Official Consolidated Policy Online (Markdown):", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22").pack(anchor="w", pady=(0, 6))

        btn_links_row = tk.Frame(links_frame, bg="#161B22")
        btn_links_row.pack(fill=tk.X)

        ttk.Button(btn_links_row, text="Consolidated Master Policy", style="Blue.TButton", command=lambda: webbrowser.open(self.MASTER_POLICY_URL)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_links_row, text="Attribution & Licenses", style="Blue.TButton", command=lambda: webbrowser.open(self.ATTRIBUTION_URL)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_links_row, text="Open Source License", style="Dark.TButton", command=lambda: webbrowser.open(self.LICENSE_URL)).pack(side=tk.LEFT)

        action_frame = tk.Frame(card, bg="#161B22")
        action_frame.pack(fill=tk.X, side=tk.BOTTOM)

        def _on_accept():
            try:
                import json
                with open(consent_path, "w", encoding="utf-8") as f:
                    json.dump({"accepted_version": self.POLICY_VERSION, "timestamp": time.time()}, f)
            except Exception:
                pass
            dlg.destroy()

        btn_accept = ttk.Button(action_frame, text="I Agree & Continue", style="Green.TButton", command=_on_accept)
        btn_accept.pack(side=tk.RIGHT, padx=(8, 0))

        btn_decline = ttk.Button(action_frame, text="Decline & Exit", style="Red.TButton", command=_on_decline)
        btn_decline.pack(side=tk.RIGHT)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#0D1117", borderwidth=0)
        style.configure("TNotebook.Tab", background="#161B22", foreground="#8B949E", padding=[14, 8], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#21262D")], foreground=[("selected", "#58A6FF")])

        style.configure("TFrame", background="#161B22")
        style.configure("TLabel", background="#161B22", foreground="#C9D1D9", font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#58A6FF", background="#0D1117")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 9), foreground="#8B949E", background="#0D1117")
        style.configure("Badge.TLabel", font=("Segoe UI", 9, "bold"), background="#21262D", foreground="#3FB950", padding=[8, 4])

        style.configure("Green.TButton", font=("Segoe UI", 9, "bold"), background="#238636", foreground="#FFFFFF")
        style.map("Green.TButton", background=[("active", "#2EA043"), ("disabled", "#30363D")])

        style.configure("Red.TButton", font=("Segoe UI", 9, "bold"), background="#DA3633", foreground="#FFFFFF")
        style.map("Red.TButton", background=[("active", "#F85149"), ("disabled", "#30363D")])

        style.configure("Blue.TButton", font=("Segoe UI", 9, "bold"), background="#1F6FEB", foreground="#FFFFFF")
        style.map("Blue.TButton", background=[("active", "#388BFD"), ("disabled", "#30363D")])

        style.configure("Dark.TButton", font=("Segoe UI", 9), background="#21262D", foreground="#C9D1D9")
        style.map("Dark.TButton", background=[("active", "#30363D"), ("disabled", "#161B22")])

        style.configure("Purple.TButton", font=("Segoe UI", 9, "bold"), background="#8957E5", foreground="#FFFFFF")
        style.map("Purple.TButton", background=[("active", "#A371F7"), ("disabled", "#30363D")])

        style.configure("Orange.TButton", font=("Segoe UI", 9, "bold"), background="#D29922", foreground="#FFFFFF")
        style.map("Orange.TButton", background=[("active", "#E3B341"), ("disabled", "#30363D")])

        style.configure("Cyan.TButton", font=("Segoe UI", 9, "bold"), background="#0366D6", foreground="#FFFFFF")
        style.map("Cyan.TButton", background=[("active", "#2188FF"), ("disabled", "#30363D")])

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg="#0D1117", pady=10, padx=16)
        header_frame.pack(fill=tk.X)

        title_box = tk.Frame(header_frame, bg="#0D1117")
        title_box.pack(side=tk.LEFT)

        title_lbl = tk.Label(title_box, text="Otter", font=("Segoe UI", 20, "bold"), fg="#58A6FF", bg="#0D1117")
        title_lbl.pack(side=tk.LEFT)

        tagline = tk.Label(title_box, text=" | Virtual Webcam & Remote Controller", font=("Segoe UI", 11), fg="#8B949E", bg="#0D1117")
        tagline.pack(side=tk.LEFT, padx=(4, 0), pady=(4, 0))

        self.status_badge = tk.Label(header_frame, text="DISCONNECTED", font=("Segoe UI", 9, "bold"), fg="#DA3633", bg="#21262D", padx=10, pady=4)
        self.status_badge.pack(side=tk.RIGHT)

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 10))

        # Tab 1: Controller
        self.tab_controls = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_controls, text=" Controller ")
        self._build_controls_tab()

        # Tab 2: OBS & Discord Setup
        self.tab_guide = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_guide, text=" OBS & Discord Setup ")
        self._build_guide_tab()

        # Tab 3: Dependencies & OEM Fix
        self.tab_deps_oem = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_deps_oem, text=" Dependencies & OEM Fix ")
        self._build_deps_oem_tab()

        # Tab 4: About & Credits
        self.tab_about = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_about, text=" About & License ")
        self._build_about_tab()

    def _build_controls_tab(self):
        container = tk.Frame(self.tab_controls, bg="#161B22")
        container.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(container, bg="#161B22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#161B22", padx=12, pady=10)

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas_win = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_win, width=event.width)
        canvas.bind("<Configure>", _on_canvas_configure)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

        # --- 1. Connection & Multi-Camera Settings ---
        conn_frame = tk.LabelFrame(scrollable_frame, text=" Connection & Multi-Camera Settings ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = tk.Frame(conn_frame, bg="#161B22")
        row1.pack(fill=tk.X, pady=(0, 6))

        self.conn_mode = tk.StringVar(value="usb")
        r_usb = tk.Radiobutton(row1, text="USB (ADB Auto-Tunnel)", variable=self.conn_mode, value="usb", bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_conn_mode)
        r_usb.pack(side=tk.LEFT, padx=(0, 12))

        r_wifi = tk.Radiobutton(row1, text="Wi-Fi (LAN IP)", variable=self.conn_mode, value="wifi", bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_conn_mode)
        r_wifi.pack(side=tk.LEFT, padx=(0, 12))

        self.btn_auto_detect = ttk.Button(row1, text="Auto Detect IP", style="Blue.TButton", command=self._gui_auto_detect_ip)
        self.btn_auto_detect.pack(side=tk.LEFT, padx=(0, 12))

        self.vcam_var = tk.BooleanVar(value=True)
        chk_vcam = tk.Checkbutton(row1, text="Virtual Camera (OBS/DirectShow)", variable=self.vcam_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22")
        chk_vcam.pack(side=tk.LEFT, padx=(0, 12))

        self.btn_new_instance = ttk.Button(row1, text="+ Multi-Cam Instance", style="Blue.TButton", command=self._spawn_new_instance)
        self.btn_new_instance.pack(side=tk.RIGHT, padx=2)

        row2 = tk.Frame(conn_frame, bg="#161B22")
        row2.pack(fill=tk.X)

        tk.Label(row2, text="IP:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT)
        self.entry_ip = tk.Entry(row2, width=13, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.configure(state=tk.DISABLED)
        self.entry_ip.pack(side=tk.LEFT, padx=(3, 8))

        tk.Label(row2, text="Stream Port:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT)
        self.entry_stream_port = tk.Entry(row2, width=6, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT)
        self.entry_stream_port.insert(0, "8089")
        self.entry_stream_port.pack(side=tk.LEFT, padx=(3, 8))

        tk.Label(row2, text="Ctrl Port:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT)
        self.entry_ctrl_port = tk.Entry(row2, width=6, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT)
        self.entry_ctrl_port.insert(0, "8090")
        self.entry_ctrl_port.pack(side=tk.LEFT, padx=(3, 8))

        tk.Label(row2, text="Camera Name:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT)
        self.entry_cam_name = tk.Entry(row2, width=14, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT)
        self.entry_cam_name.insert(0, "Otter Cam 1")
        self.entry_cam_name.pack(side=tk.LEFT, padx=(3, 10))

        self.btn_connect = ttk.Button(row2, text="Connect & Start", style="Green.TButton", command=self.start_stream)
        self.btn_connect.pack(side=tk.RIGHT, padx=4)

        self.btn_stop = ttk.Button(row2, text="Stop", style="Red.TButton", command=self.stop_stream)
        self.btn_stop.configure(state=tk.DISABLED)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)

        # --- 2. Quick Modes (One-Click Presets) ---
        qm_frame = tk.LabelFrame(scrollable_frame, text=" Quick Modes (One-Click Presets) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        qm_frame.pack(fill=tk.X, pady=(0, 10))

        qm_grid = tk.Frame(qm_frame, bg="#161B22")
        qm_grid.pack(fill=tk.X)

        btn_qm_meetings = ttk.Button(qm_grid, text="Meetings", style="Green.TButton", command=lambda: self.apply_quick_mode("meetings"))
        btn_qm_meetings.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_class = ttk.Button(qm_grid, text="Online Class", style="Blue.TButton", command=lambda: self.apply_quick_mode("class"))
        btn_qm_class.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_stream = ttk.Button(qm_grid, text="Streaming", style="Purple.TButton", command=lambda: self.apply_quick_mode("streaming"))
        btn_qm_stream.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_snapshot = ttk.Button(qm_grid, text="Snapshot", style="Orange.TButton", command=lambda: self.apply_quick_mode("snapshot"))
        btn_qm_snapshot.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_scan = ttk.Button(qm_grid, text="Scan / OCR", style="Cyan.TButton", command=lambda: self.apply_quick_mode("scan"))
        btn_qm_scan.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_sec = ttk.Button(qm_grid, text="Security", style="Dark.TButton", command=lambda: self.apply_quick_mode("security"))
        btn_qm_sec.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_fun = ttk.Button(qm_grid, text="Fun Filter", style="Green.TButton", command=lambda: self.apply_quick_mode("fun"))
        btn_qm_fun.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        btn_qm_pro = ttk.Button(qm_grid, text="Pro Reset", style="Dark.TButton", command=lambda: self.apply_quick_mode("pro"))
        btn_qm_pro.pack(side=tk.LEFT, padx=3, pady=2, expand=True, fill=tk.X)

        # --- 3. Camera Hardware Controls & Format ---
        cam_frame = tk.LabelFrame(scrollable_frame, text=" Remote Camera Hardware & Format ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        cam_frame.pack(fill=tk.X, pady=(0, 10))

        btn_grid = tk.Frame(cam_frame, bg="#161B22")
        btn_grid.pack(fill=tk.X, pady=(0, 6))

        self.btn_flip = ttk.Button(btn_grid, text="Flip Lens (Front/Rear)", style="Dark.TButton", command=self.flip_camera)
        self.btn_flip.pack(side=tk.LEFT, padx=3, pady=2)

        self.btn_mirror = ttk.Button(btn_grid, text="Mirror: OFF", style="Dark.TButton", command=self.toggle_mirror)
        self.btn_mirror.pack(side=tk.LEFT, padx=3, pady=2)

        self.btn_rotate = ttk.Button(btn_grid, text="Rotate: 0°", style="Dark.TButton", command=self.rotate_camera)
        self.btn_rotate.pack(side=tk.LEFT, padx=3, pady=2)

        self.btn_torch = ttk.Button(btn_grid, text="Torch: Cycle", style="Dark.TButton", command=self.toggle_torch)
        self.btn_torch.pack(side=tk.LEFT, padx=3, pady=2)

        self.btn_glow = ttk.Button(btn_grid, text="Front Glow: Cycle", style="Dark.TButton", command=self.toggle_glow)
        self.btn_glow.pack(side=tk.LEFT, padx=3, pady=2)

        self.btn_ultra_photo = ttk.Button(btn_grid, text="Ultra Photo (Full Res)", style="Orange.TButton", command=self.capture_ultra_photo)
        self.btn_ultra_photo.pack(side=tk.LEFT, padx=3, pady=2)

        fmt_row = tk.Frame(cam_frame, bg="#161B22")
        fmt_row.pack(fill=tk.X)

        tk.Label(fmt_row, text="Resolution:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT, padx=(0, 4))
        self.res_combo = ttk.Combobox(fmt_row, values=["4K (3840x2160)", "1080p (1920x1080)", "720p (1280x720)", "480p (640x480)", "360p (640x360)"], state="readonly", width=18)
        self.res_combo.set("720p (1280x720)")
        self.res_combo.pack(side=tk.LEFT, padx=(0, 14))
        self.res_combo.bind("<<ComboboxSelected>>", self.on_res_change)

        tk.Label(fmt_row, text="Target FPS:", bg="#161B22", fg="#8B949E").pack(side=tk.LEFT, padx=(0, 4))
        self.fps_combo = ttk.Combobox(fmt_row, values=["60 FPS", "30 FPS", "15 FPS"], state="readonly", width=10)
        self.fps_combo.set("30 FPS")
        self.fps_combo.pack(side=tk.LEFT, padx=(0, 14))
        self.fps_combo.bind("<<ComboboxSelected>>", self.on_fps_change)

        # --- 4. Zoom Controls (with Slider AND +/- buttons!) ---
        zoom_frame = tk.LabelFrame(scrollable_frame, text=" Zoom Controls (+/- Buttons & Slider) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        zoom_frame.pack(fill=tk.X, pady=(0, 10))

        zoom_row = tk.Frame(zoom_frame, bg="#161B22")
        zoom_row.pack(fill=tk.X)

        btn_zoom_out = ttk.Button(zoom_row, text="Zoom Out (-)", style="Dark.TButton", command=self.zoom_out)
        btn_zoom_out.pack(side=tk.LEFT, padx=(0, 8))

        self.slider_zoom = tk.Scale(
            zoom_row,
            from_=1.0,
            to=8.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=340,
            bg="#161B22",
            fg="#58A6FF",
            troughcolor="#0D1117",
            activebackground="#1F6FEB",
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            showvalue=False,
            command=self._on_zoom_slide
        )
        self.slider_zoom.set(1.0)
        self.slider_zoom.pack(side=tk.LEFT, padx=4)

        btn_zoom_in = ttk.Button(zoom_row, text="Zoom In (+)", style="Dark.TButton", command=self.zoom_in)
        btn_zoom_in.pack(side=tk.LEFT, padx=(8, 12))

        self.lbl_zoom = tk.Label(zoom_row, text="1.0x", font=("Segoe UI", 11, "bold"), fg="#58A6FF", bg="#161B22", width=6)
        self.lbl_zoom.pack(side=tk.LEFT)

        # --- 5. Pro Manual Sliders & Auto Controls ---
        pro_frame = tk.LabelFrame(scrollable_frame, text=" Pro Camera Controls & Auto Sliders ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        pro_frame.pack(fill=tk.X, pady=(0, 10))

        # ISO Row
        iso_row = tk.Frame(pro_frame, bg="#161B22")
        iso_row.pack(fill=tk.X, pady=3)

        tk.Label(iso_row, text="ISO:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=11, anchor="w").pack(side=tk.LEFT)
        chk_iso = tk.Checkbutton(iso_row, text="Auto ISO", variable=self.iso_auto_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_iso_auto)
        chk_iso.pack(side=tk.LEFT, padx=(0, 10))

        self.slider_iso = tk.Scale(
            iso_row,
            from_=0,
            to=len(self.ISO_VALUES) - 1,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=260,
            bg="#161B22",
            fg="#58A6FF",
            troughcolor="#0D1117",
            activebackground="#1F6FEB",
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            showvalue=False,
            state=tk.DISABLED,
            command=self._on_iso_slide
        )
        self.slider_iso.set(1)
        self.slider_iso.pack(side=tk.LEFT, padx=4)

        self.lbl_iso_val = tk.Label(iso_row, text="Auto", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_iso_val.pack(side=tk.LEFT, padx=(6, 0))

        # Shutter Row
        shutter_row = tk.Frame(pro_frame, bg="#161B22")
        shutter_row.pack(fill=tk.X, pady=3)

        tk.Label(shutter_row, text="Shutter:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=11, anchor="w").pack(side=tk.LEFT)
        chk_shutter = tk.Checkbutton(shutter_row, text="Auto Shutter", variable=self.shutter_auto_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_shutter_auto)
        chk_shutter.pack(side=tk.LEFT, padx=(0, 10))

        self.slider_shutter = tk.Scale(
            shutter_row,
            from_=0,
            to=len(self.SHUTTER_STEPS) - 1,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=260,
            bg="#161B22",
            fg="#58A6FF",
            troughcolor="#0D1117",
            activebackground="#1F6FEB",
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            showvalue=False,
            state=tk.DISABLED,
            command=self._on_shutter_slide
        )
        self.slider_shutter.set(4)
        self.slider_shutter.pack(side=tk.LEFT, padx=4)

        self.lbl_shutter_val = tk.Label(shutter_row, text="Auto", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_shutter_val.pack(side=tk.LEFT, padx=(6, 0))

        # White Balance Row
        wb_row = tk.Frame(pro_frame, bg="#161B22")
        wb_row.pack(fill=tk.X, pady=3)

        tk.Label(wb_row, text="White Bal:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=11, anchor="w").pack(side=tk.LEFT)
        chk_wb = tk.Checkbutton(wb_row, text="Auto AWB", variable=self.wb_auto_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_wb_auto)
        chk_wb.pack(side=tk.LEFT, padx=(0, 10))

        self.slider_wb = tk.Scale(
            wb_row,
            from_=0,
            to=len(self.WB_MODES) - 1,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=260,
            bg="#161B22",
            fg="#58A6FF",
            troughcolor="#0D1117",
            activebackground="#1F6FEB",
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            showvalue=False,
            state=tk.DISABLED,
            command=self._on_wb_slide
        )
        self.slider_wb.set(0)
        self.slider_wb.pack(side=tk.LEFT, padx=4)

        self.lbl_wb_val = tk.Label(wb_row, text="Auto (AWB)", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22", width=18, anchor="w")
        self.lbl_wb_val.pack(side=tk.LEFT, padx=(6, 0))

        # Color FX Row
        fx_row = tk.Frame(pro_frame, bg="#161B22")
        fx_row.pack(fill=tk.X, pady=3)

        tk.Label(fx_row, text="Color FX:", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=11, anchor="w").pack(side=tk.LEFT)
        chk_fx = tk.Checkbutton(fx_row, text="Normal FX", variable=self.fx_auto_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22", command=self._toggle_fx_auto)
        chk_fx.pack(side=tk.LEFT, padx=(0, 10))

        self.slider_fx = tk.Scale(
            fx_row,
            from_=0,
            to=len(self.FX_MODES) - 1,
            resolution=1,
            orient=tk.HORIZONTAL,
            length=260,
            bg="#161B22",
            fg="#58A6FF",
            troughcolor="#0D1117",
            activebackground="#1F6FEB",
            highlightthickness=0,
            bd=0,
            sliderrelief=tk.FLAT,
            showvalue=False,
            state=tk.DISABLED,
            command=self._on_fx_slide
        )
        self.slider_fx.set(0)
        self.slider_fx.pack(side=tk.LEFT, padx=4)

        self.lbl_fx_val = tk.Label(fx_row, text="Normal Color", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22", width=18, anchor="w")
        self.lbl_fx_val.pack(side=tk.LEFT, padx=(6, 0))

        # Focus & Exposure Row
        fe_row = tk.Frame(pro_frame, bg="#161B22")
        fe_row.pack(fill=tk.X, pady=(6, 2))

        self.btn_af = ttk.Button(fe_row, text="AF: Auto", style="Green.TButton", command=self.toggle_af)
        self.btn_af.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_focus_dist = ttk.Button(fe_row, text="Focus: Auto", style="Dark.TButton", command=self.cycle_focus)
        self.btn_focus_dist.pack(side=tk.LEFT, padx=4)

        btn_ev_minus = ttk.Button(fe_row, text="EV (-)", style="Dark.TButton", command=lambda: self.ev_step(-1))
        btn_ev_minus.pack(side=tk.LEFT, padx=(8, 2))

        self.lbl_ev = tk.Label(fe_row, text="EV: +0.0", font=("Segoe UI", 9, "bold"), fg="#58A6FF", bg="#161B22", width=9)
        self.lbl_ev.pack(side=tk.LEFT)

        btn_ev_plus = ttk.Button(fe_row, text="EV (+)", style="Dark.TButton", command=lambda: self.ev_step(1))
        btn_ev_plus.pack(side=tk.LEFT, padx=(2, 8))

        self.btn_sync_status = ttk.Button(fe_row, text="Sync State", style="Blue.TButton", command=self.sync_remote_status)
        self.btn_sync_status.pack(side=tk.RIGHT, padx=4)

        # --- 6. Event & Connection Log ---
        log_frame = tk.LabelFrame(scrollable_frame, text=" Event & Connection Log ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=8, pady=6)
        log_frame.pack(fill=tk.BOTH, expand=True)

        log_inner = tk.Frame(log_frame, bg="#0D1117")
        log_inner.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_inner, height=7, bg="#0D1117", fg="#8B949E", insertbackground="#C9D1D9", font=("Consolas", 9), relief=tk.FLAT)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_log = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar_log.set)

        btn_clear_log = ttk.Button(log_frame, text="Clear Log", style="Dark.TButton", command=lambda: self.log_text.delete("1.0", tk.END))
        btn_clear_log.pack(side=tk.RIGHT, pady=(4, 0))

        self.log("Otter Virtual Camera Controller initialized.")
        self.log("Ready. Plug in Android device via USB with USB Debugging enabled, then click 'Connect & Start'.")

    def _build_guide_tab(self):
        guide_box = tk.Frame(self.tab_guide, bg="#161B22", padx=16, pady=14)
        guide_box.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(guide_box, bg="#161B22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(guide_box, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#161B22")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def add_card(parent, title, steps):
            card = tk.LabelFrame(parent, text=f" {title} ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=8)
            card.pack(fill=tk.X, pady=(0, 12))
            for step in steps:
                lbl = tk.Label(card, text=step, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), justify=tk.LEFT, anchor="w", wraplength=680)
                lbl.pack(fill=tk.X, pady=2)

        add_card(scrollable_frame, "Step-by-Step: USB Cable Connection (Recommended for 0-Latency)", [
            "1. Unlock Developer Options: On your phone, go to Settings -> About Phone -> tap 'Build Number' 7 times.",
            "2. Enable USB Debugging: In Settings -> Developer Options, turn ON 'USB Debugging'.",
            "3. Connect Cable: Plug your phone into your PC with a USB data cable.",
            "4. Authorize PC: On your phone prompt 'Allow USB debugging?', check 'Always allow' and tap OK.",
            "5. Select USB Mode: On this PC controller, keep 'USB (ADB Auto-Tunnel)' selected.",
            "6. Start Streaming: In the Otter mobile app, tap 'Start'.",
            "7. Connect PC: Click 'Connect & Start' on this controller.",
            "8. Zero-Latency Ready: Virtual camera is now broadcasting directly to OBS, Discord, Meet and Zoom."
        ])

        add_card(scrollable_frame, "Step-by-Step: Wi-Fi Connection (Wireless Convenience)", [
            "1. Same Network: Ensure both your phone and PC are connected to the SAME Wi-Fi router (5GHz band recommended).",
            "2. Note IP Address: Open Otter on your phone and check the IP shown on screen (e.g. 'IP: 192.168.1.50').",
            "3. Start on Phone: Tap 'Start' on the Otter mobile app.",
            "4. Select Wi-Fi Mode: On this PC controller, select 'Wi-Fi (LAN IP)'.",
            "5. Enter IP: Type your phone's IP address into the IP box.",
            "6. Connect: Click 'Connect & Start'. Your wireless stream is now active."
        ])

        add_card(scrollable_frame, "How to use with OBS Studio", [
            "1. Launch OBS Studio.",
            "2. Under the 'Sources' dock at the bottom, click the '+' (Add) button.",
            "3. Select 'Video Capture Device' from the menu.",
            "4. Choose 'Create New' and name it 'Otter Camera'.",
            "5. Under 'Device', select 'Unity Video Capture' OR 'OBS Virtual Camera'.",
            "6. Set Resolution/FPS Type to 'Device Default' and click OK.",
            "7. Your Android phone camera now feeds directly into OBS scenes."
        ])

        add_card(scrollable_frame, "How to use with Discord", [
            "1. Open Discord and click the Settings gear icon next to your username.",
            "2. In the left navigation sidebar, select 'Voice & Video'.",
            "3. Scroll down to the 'Video Settings' section.",
            "4. In the 'Camera' dropdown, choose 'OBS Virtual Camera' or 'Unity Video Capture'.",
            "5. Click the 'Test Video' preview button to verify the feed.",
            "6. Join any voice channel or direct call and turn on your camera."
        ])

        add_card(scrollable_frame, "How to use with Google Meet, Zoom & MS Teams", [
            "1. Open meeting settings or join a test room.",
            "2. In the audio/video selection panel, navigate to 'Camera'.",
            "3. Select 'OBS Virtual Camera' or 'Unity Video Capture' from the list of available devices.",
            "4. The HD stream from your phone camera is now your active video."
        ])

        add_card(scrollable_frame, "Web Browser Settings (Brave, Chrome, Firefox)", [
            "1. In Brave/Chrome, navigate to: brave://settings/content/camera (or chrome://settings/content/camera).",
            "2. Select 'OBS Virtual Camera' or 'Unity Video Capture' as the preferred video input.",
            "3. Web apps (webcam tests, browser calls) will automatically use Otter."
        ])

    def _build_deps_oem_tab(self):
        box = tk.Frame(self.tab_deps_oem, bg="#161B22", padx=16, pady=14)
        box.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(box, bg="#161B22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(box, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#161B22")

        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Section 1: Python Dependencies
        dep_card = tk.LabelFrame(scrollable_frame, text=" Python Desktop Dependencies ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        dep_card.pack(fill=tk.X, pady=(0, 12))

        self.dep_status_frame = tk.Frame(dep_card, bg="#161B22")
        self.dep_status_frame.pack(fill=tk.X, pady=(0, 8))
        self._refresh_dep_status_labels()

        btn_row = tk.Frame(dep_card, bg="#161B22")
        btn_row.pack(fill=tk.X)

        btn_install = ttk.Button(btn_row, text="Auto-Install (pip)", style="Green.TButton", command=self._gui_install_deps)
        btn_install.pack(side=tk.LEFT, padx=(0, 8))

        btn_manual = ttk.Button(btn_row, text="Manual Instructions", style="Blue.TButton", command=self._gui_manual_instructions)
        btn_manual.pack(side=tk.LEFT, padx=(0, 8))

        btn_uninst = ttk.Button(btn_row, text="Uninstall Dependencies", style="Red.TButton", command=self._gui_uninstall_deps)
        btn_uninst.pack(side=tk.LEFT, padx=(0, 8))

        btn_refresh = ttk.Button(btn_row, text="Refresh Status", style="Dark.TButton", command=self._refresh_dep_status_labels)
        btn_refresh.pack(side=tk.LEFT)

        # Section 2: Standalone Windows DirectShow Virtual Camera Driver
        vcam_card = tk.LabelFrame(scrollable_frame, text=" Windows OS DirectShow Virtual Webcam Driver (Direct Camera Recognition) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        vcam_card.pack(fill=tk.X, pady=(0, 12))

        vcam_desc = (
            "Registers a native DirectShow virtual camera device ('Unity Video Capture') directly in Windows.\n"
            "This allows Zoom, Google Meet, MS Teams, Discord, NVIDIA Broadcast, and OBS to detect Otter\n"
            "as a normal physical webcam from their camera dropdown lists without running OBS Window Capture."
        )
        tk.Label(vcam_card, text=vcam_desc, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=(0, 8))

        vcam_btn_row = tk.Frame(vcam_card, bg="#161B22")
        vcam_btn_row.pack(fill=tk.X)

        btn_install_vcam_driver = ttk.Button(vcam_btn_row, text="Install / Register Virtual Camera", style="Green.TButton", command=self._gui_install_vcam_driver)
        btn_install_vcam_driver.pack(side=tk.LEFT, padx=(0, 8))

        btn_uninstall_vcam_driver = ttk.Button(vcam_btn_row, text="Unregister Driver", style="Red.TButton", command=self._gui_uninstall_vcam_driver)
        btn_uninstall_vcam_driver.pack(side=tk.LEFT)

        # Section 3: ADB & Android Minimal Tools Downloader
        adb_card = tk.LabelFrame(scrollable_frame, text=" ADB & Android Minimal Platform Tools (No Android Studio Needed) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        adb_card.pack(fill=tk.X, pady=(0, 12))

        self.adb_status_frame = tk.Frame(adb_card, bg="#161B22")
        self.adb_status_frame.pack(fill=tk.X, pady=(0, 8))
        self._refresh_adb_status_labels()

        adb_btn_row = tk.Frame(adb_card, bg="#161B22")
        adb_btn_row.pack(fill=tk.X)

        self.btn_download_adb = ttk.Button(adb_btn_row, text="Download ADB Minimal Tools (~15MB)", style="Green.TButton", command=self._gui_download_adb)
        self.btn_download_adb.pack(side=tk.LEFT, padx=(0, 8))

        btn_refresh_adb = ttk.Button(adb_btn_row, text="Check ADB Status", style="Dark.TButton", command=self._refresh_adb_status_labels)
        btn_refresh_adb.pack(side=tk.LEFT, padx=(0, 8))

        btn_uninstall_adb = ttk.Button(adb_btn_row, text="Remove Portable ADB", style="Red.TButton", command=self._gui_uninstall_adb)
        btn_uninstall_adb.pack(side=tk.LEFT)

        adb_desc = (
            "No Android Studio required! This downloads Google's official, lightweight Platform Tools (adb)\n"
            "directly from dl.google.com into Otter's portable directory so USB cable tunneling works immediately.\n"
            "Special thanks to the Google Android Tools team for standalone platform-tools."
        )
        tk.Label(adb_card, text=adb_desc, bg="#161B22", fg="#8B949E", font=("Segoe UI", 8), justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=(6, 0))

        # Section 4: Android 14+ Native USB Webcam (Supported Devices)
        uvc_card = tk.LabelFrame(scrollable_frame, text=" Android 14+ Native USB Webcam Mode (Pixel, Moto, Supported Devices) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        uvc_card.pack(fill=tk.X, pady=(0, 12))

        uvc_desc = (
            "On devices with Android 14 QPR1+ where the manufacturer enabled UVC gadget support (e.g. Google Pixel, Motorola),\n"
            "your phone can transform into a native plug-and-play USB hardware webcam in Windows without needing Otter client.\n"
            "If your manufacturer locked or omitted the driver (e.g. Vivo/iQOO, Samsung), Otter automatically streams via ADB instead."
        )
        tk.Label(uvc_card, text=uvc_desc, bg="#161B22", fg="#8B949E", font=("Segoe UI", 8), justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=(0, 8))

        uvc_btn_row = tk.Frame(uvc_card, bg="#161B22")
        uvc_btn_row.pack(fill=tk.X)

        btn_activate_uvc = ttk.Button(uvc_btn_row, text="Activate Android 14 USB Webcam", style="Green.TButton", command=self._gui_activate_uvc)
        btn_activate_uvc.pack(side=tk.LEFT, padx=(0, 8))

        btn_reset_uvc = ttk.Button(uvc_btn_row, text="Reset USB Mode (MTP)", style="Dark.TButton", command=self._gui_reset_uvc)
        btn_reset_uvc.pack(side=tk.LEFT)

        # Section 5: OEM Anti-Kill & Background Fixes
        oem_card = tk.LabelFrame(scrollable_frame, text=" OEM Background & Anti-Kill Fixes (MIUI / HyperOS / ColorOS / One UI) ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 11, "bold"), padx=12, pady=10)
        oem_card.pack(fill=tk.X, pady=(0, 12))

        oem_info = [
            ("Xiaomi / MIUI / HyperOS", [
                "1. Autostart: Settings -> Apps -> Manage apps -> Otter -> Enable 'Autostart'.",
                "2. Battery Saver: Set to 'No restrictions'.",
                "3. Lock in Recents: Open app switcher, press and hold Otter card, tap the padlock icon."
            ]),
            ("Samsung One UI", [
                "1. Background limits: Settings -> Battery -> Background usage limits -> Never sleeping apps -> Add 'Otter'.",
                "2. Unrestricted Battery: Settings -> Apps -> Otter -> Battery -> Choose 'Unrestricted'."
            ]),
            ("OPPO / OnePlus / Realme (ColorOS / OxygenOS)", [
                "1. Background Activity: Settings -> Apps -> App management -> Otter -> Battery usage -> Enable 'Allow background activity'.",
                "2. Auto-launch: Enable 'Allow auto-launch'.",
                "3. Lock in Recents: Open recent tasks, tap the three dots on Otter, tap 'Lock'."
            ]),
            ("Vivo / iQOO (FuntouchOS)", [
                "1. Settings -> Battery -> High background power consumption -> Turn ON toggle for Otter."
            ]),
            ("Screen-Off & Lock Screen Streaming", [
                "Otter includes an active Foreground Service ('Lock Mode: ON') with PARTIAL_WAKE_LOCK.",
                "When Lock Mode is ON in the mobile app, you can turn off your screen or lock your phone and streaming will stay active."
            ])
        ]

        for title, steps in oem_info:
            sub = tk.LabelFrame(oem_card, text=f" {title} ", bg="#161B22", fg="#3FB950", font=("Segoe UI", 10, "bold"), padx=10, pady=6)
            sub.pack(fill=tk.X, pady=4)
            for s in steps:
                tk.Label(sub, text=s, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), anchor="w", justify=tk.LEFT).pack(fill=tk.X, pady=1)

    def _refresh_dep_status_labels(self):
        for widget in self.dep_status_frame.winfo_children():
            widget.destroy()

        status = manage_dependencies.check_dependencies()
        for pkg, installed in status.items():
            color = "#3FB950" if installed else "#DA3633"
            txt = f"{pkg}: {'INSTALLED' if installed else 'MISSING'}"
            lbl = tk.Label(self.dep_status_frame, text=txt, font=("Segoe UI", 9, "bold"), fg=color, bg="#21262D", padx=8, pady=3)
            lbl.pack(side=tk.LEFT, padx=(0, 8))

    def _refresh_adb_status_labels(self):
        if not hasattr(self, "adb_status_frame"):
            return
        for widget in self.adb_status_frame.winfo_children():
            widget.destroy()

        avail, path, desc = manage_adb.check_adb_status()
        color = "#3FB950" if avail else "#DA3633"
        txt = f"ADB Status: {'READY' if avail else 'MISSING'} ({desc})"
        lbl = tk.Label(self.adb_status_frame, text=txt, font=("Segoe UI", 9, "bold"), fg=color, bg="#21262D", padx=8, pady=3)
        lbl.pack(side=tk.LEFT, padx=(0, 8))

        if path:
            path_lbl = tk.Label(self.adb_status_frame, text=f"Path: {path}", font=("Consolas", 8), fg="#8B949E", bg="#161B22")
            path_lbl.pack(side=tk.LEFT)

    def _gui_download_adb(self):
        disclaimer = (
            "DOWNLOAD OFFICIAL ANDROID PLATFORM TOOLS (~15MB):\n\n"
            "This will download official Google platform-tools (adb) directly from dl.google.com "
            "into Otter's local folder. No Android Studio is required.\n\n"
            "Do you want to proceed?"
        )
        if not messagebox.askyesno("Download Minimal ADB", disclaimer):
            return

        self.btn_download_adb.configure(state=tk.DISABLED)
        self.log("Downloading official Google platform-tools (ADB)...")

        def worker():
            def cb(msg, pct):
                self.log(f"ADB Setup: {msg}")

            try:
                path = manage_adb.download_and_extract_adb(progress_callback=cb)
                self.root.after(0, lambda: self._on_adb_download_completed(True, path))
            except Exception as e:
                self.root.after(0, lambda: self._on_adb_download_completed(False, str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _on_adb_download_completed(self, success, info):
        self.btn_download_adb.configure(state=tk.NORMAL)
        self._refresh_adb_status_labels()
        if success:
            self.log(f"ADB Minimal Tools installed: {info}")
            messagebox.showinfo("ADB Ready", "Minimal Android Platform Tools (adb) installed successfully!\nUSB cable mode is now fully operational.")
        else:
            self.log(f"ADB Download failed: {info}")
            messagebox.showerror("Error", f"Failed to download ADB: {info}")

    def _gui_install_vcam_driver(self):
        bat_path = os.path.join(os.path.dirname(__file__), "driver", "install_virtual_cam.bat")
        if not os.path.exists(bat_path):
            messagebox.showerror("Error", f"Could not find driver installer at:\n{bat_path}")
            return
        try:
            subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
            self.log("Launched DirectShow Virtual Camera Driver registration.")
            messagebox.showinfo("Driver Installer", "Launched DirectShow Driver Registration with Administrator rights.\nCheck the terminal window and accept the UAC prompt to complete setup.")
        except Exception as e:
            self.log(f"Failed to launch driver installer: {e}")
            messagebox.showerror("Error", f"Failed to execute driver installer: {e}")

    def _gui_uninstall_vcam_driver(self):
        bat_path = os.path.join(os.path.dirname(__file__), "driver", "uninstall_virtual_cam.bat")
        if not os.path.exists(bat_path):
            messagebox.showerror("Error", f"Could not find driver uninstaller at:\n{bat_path}")
            return
        try:
            subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
            self.log("Launched DirectShow Virtual Camera Driver unregistration.")
            messagebox.showinfo("Driver Uninstaller", "Launched unregistration script with Administrator rights.")
        except Exception as e:
            self.log(f"Failed to launch driver uninstaller: {e}")
            messagebox.showerror("Error", f"Failed to execute uninstaller: {e}")

    def _gui_uninstall_adb(self):
        if not messagebox.askyesno("Remove Portable ADB", "Remove downloaded portable ADB platform-tools from Otter's folder?"):
            return
        manage_adb.uninstall_adb()
        self._refresh_adb_status_labels()
        self.log("Portable ADB tools removed.")
        messagebox.showinfo("Removed", "Portable ADB platform-tools removed.")

    def _gui_activate_uvc(self):
        self.log("Requesting Android 14 native USB webcam mode via ADB (svc usb setFunctions uvc)...")
        def worker():
            from adb_tunnel import ADBTunnel
            tunnel = ADBTunnel()
            adb_cmd = tunnel.adb_cmd
            try:
                res = subprocess.run([adb_cmd, "shell", "svc", "usb", "setFunctions", "uvc"], capture_output=True, text=True, timeout=5)
                # Check if device has DeviceAsWebcam package
                check_pkg = subprocess.run([adb_cmd, "shell", "pm", "path", "com.android.DeviceAsWebcam"], capture_output=True, text=True, timeout=5)
                has_webcam_app = "package:" in (check_pkg.stdout or "")

                if has_webcam_app:
                    msg = "Native Android 14 USB Webcam activated!\nCheck Windows Device Manager or Camera app — your phone is now an actual USB webcam."
                    self.root.after(0, lambda: messagebox.showinfo("Android 14 Webcam", msg))
                    self.log("Native Android 14 USB webcam activated successfully.")
                else:
                    msg = (
                        "Notice: The command was sent, but your phone manufacturer has stripped the Google DeviceAsWebcam package.\n\n"
                        "Your device does not support native UVC hardware webcam mode.\n"
                        "Otter's standard ADB Tunnel mode is automatically used instead (fully functional on all devices)."
                    )
                    self.root.after(0, lambda: messagebox.showinfo("OEM Locked Notice", msg))
                    self.log("Device manufacturer stripped DeviceAsWebcam; using Otter ADB tunnel instead.")
            except Exception as e:
                self.log(f"UVC mode request error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to send ADB command: {e}"))
        threading.Thread(target=worker, daemon=True).start()

    def _gui_reset_uvc(self):
        self.log("Resetting phone USB mode to standard MTP/charging...")
        def worker():
            from adb_tunnel import ADBTunnel
            tunnel = ADBTunnel()
            try:
                subprocess.run([tunnel.adb_cmd, "shell", "svc", "usb", "setFunctions", "mtp"], capture_output=True, text=True, timeout=5)
                self.log("Phone USB mode restored to MTP.")
                self.root.after(0, lambda: messagebox.showinfo("Reset USB", "Phone USB mode reset to standard file transfer (MTP)."))
            except Exception as e:
                self.log(f"Reset USB error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _gui_install_deps(self):
        disclaimer = (
            "DISCLAIMER & LIABILITY NOTICE:\n\n"
            "Automated package installation runs standard pip commands targeting official PyPI packages (opencv-python, numpy).\n\n"
            "The scripts are provided 'AS IS' without warranty of any kind. Neither developer 'spacecar' nor Otter is responsible for any system breaks, package conflicts, or environment issues.\n\n"
            "Do you accept and wish to proceed?"
        )
        if not messagebox.askyesno("Disclaimer & Install", disclaimer):
            return

        self.log("Starting automated package installation via pip...")
        def worker():
            success, msg = manage_dependencies.install_dependencies(auto_confirm=True, log_callback=self.log)
            self.root.after(0, lambda: self._on_install_completed(success, msg))
        threading.Thread(target=worker, daemon=True).start()

    def _on_install_completed(self, success, msg):
        self._refresh_dep_status_labels()
        if success:
            self.log(f"Dependency setup finished: {msg}")
            messagebox.showinfo("Dependencies Ready", msg)
        else:
            self.log(f"Dependency installation error: {msg}")
            messagebox.showwarning("Notice", msg)

    def _gui_uninstall_deps(self):
        if not messagebox.askyesno("Confirm Uninstall", "Are you sure you want to uninstall Otter dependencies (opencv-python, numpy)?"):
            return

        self.log("Uninstalling Otter dependencies...")
        def worker():
            success = manage_dependencies.uninstall_dependencies(auto_confirm=True)
            self.root.after(0, lambda: self._on_uninstall_completed(success))
        threading.Thread(target=worker, daemon=True).start()

    def _on_uninstall_completed(self, success):
        self._refresh_dep_status_labels()
        self.log("Dependencies uninstalled.")
        messagebox.showinfo("Uninstalled", "Otter packages have been removed.")

    def _gui_manual_instructions(self):
        msg = (
            "Manual Installation via Terminal:\n\n"
            "1. Open Command Prompt or PowerShell.\n"
            "2. Run:\n\n"
            "pip install -r requirements.txt\n\n"
            "OR install individually:\n"
            "pip install opencv-python numpy\n\n"
            "To uninstall later:\n"
            "pip uninstall -y opencv-python numpy"
        )
        messagebox.showinfo("Manual Instructions", msg)

    def _build_about_tab(self):
        about_box = tk.Frame(self.tab_about, bg="#161B22", padx=20, pady=16)
        about_box.pack(fill=tk.BOTH, expand=True)

        lbl_app = tk.Label(about_box, text="Otter", font=("Segoe UI", 22, "bold"), fg="#58A6FF", bg="#161B22")
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(about_box, text="Open-source Android to PC Virtual Camera & Remote Control Suite", font=("Segoe UI", 10), fg="#8B949E", bg="#161B22")
        lbl_sub.pack(anchor="w", pady=(0, 14))

        meta_frame = tk.LabelFrame(about_box, text=" Project Details & Developer Thanks ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        meta_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(meta_frame, text="Developer: spacecar", font=("Segoe UI", 10, "bold"), fg="#3FB950", bg="#161B22").pack(anchor="w", pady=2)
        tk.Label(meta_frame, text="Official Repository: https://github.com/saprecar/Otter", font=("Segoe UI", 10), fg="#58A6FF", bg="#161B22", cursor="hand2").pack(anchor="w", pady=2)

        btn_box = tk.Frame(meta_frame, bg="#161B22", pady=6)
        btn_box.pack(fill=tk.X)

        btn_repo = ttk.Button(btn_box, text="Open GitHub Repository", style="Blue.TButton", command=lambda: webbrowser.open("https://github.com/saprecar/Otter"))
        btn_repo.pack(side=tk.LEFT, padx=(0, 8))

        btn_copy = ttk.Button(btn_box, text="Copy Repo Link", style="Dark.TButton", command=self._copy_repo_link)
        btn_copy.pack(side=tk.LEFT)

        legal_frame = tk.LabelFrame(about_box, text=" Universal Policies, Agreements & Attribution ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        legal_frame.pack(fill=tk.X, pady=(0, 12))

        legal_summary = (
            "Otter operates on a 100% local peer-to-peer architecture with zero developer data retention.\n"
            "Governing Law: Republic of India | Jurisdiction: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005).\n"
            "Official Contact: getspacecar@gmail.com (Mandatory subject line: '[Otter-Legal]' or '[Otter-Inquiry]')."
        )
        tk.Label(legal_frame, text=legal_summary, bg="#161B22", fg="#8B949E", font=("Segoe UI", 9), justify=tk.LEFT, anchor="w").pack(fill=tk.X, pady=(0, 8))

        legal_btn_box = tk.Frame(legal_frame, bg="#161B22")
        legal_btn_box.pack(fill=tk.X)

        ttk.Button(legal_btn_box, text="Consolidated Master Policy", style="Blue.TButton", command=lambda: webbrowser.open(self.MASTER_POLICY_URL)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(legal_btn_box, text="Attribution & Licenses", style="Blue.TButton", command=lambda: webbrowser.open(self.ATTRIBUTION_URL)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(legal_btn_box, text="Open Source License", style="Dark.TButton", command=lambda: webbrowser.open(self.LICENSE_URL)).pack(side=tk.LEFT)

        lic_frame = tk.LabelFrame(about_box, text=" License & Permissive Open Source Terms ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=12, pady=10)
        lic_frame.pack(fill=tk.BOTH, expand=True)

        lic_text = (
            "License: MIT License (Permissive & Free to Use)\n\n"
            "This software is 100% free for everyone to use, modify, and integrate for personal\n"
            "or commercial projects.\n\n"
            "Attribution Requirement:\n"
            "If code or assets from this project are reused in other applications, you are required\n"
            "to retain the original copyright notice, provide the app name ('Otter'), link to the repository\n"
            "(https://github.com/saprecar/Otter), and acknowledge the original developer ('spacecar').\n\n"
            "Special thanks to the open-source community, Google Android Platform Tools developers, "
            "Android Camera2 developers, and OBS Studio."
        )
        tk.Label(lic_frame, text=lic_text, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), justify=tk.LEFT, anchor="w").pack(fill=tk.BOTH, expand=True)

    def _build_statusbar(self):
        self.statusbar = tk.Label(self.root, text="Otter Ready | MIT License | spacecar", font=("Segoe UI", 8), fg="#8B949E", bg="#0D1117", padx=16, pady=4, anchor="w")
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def _copy_repo_link(self):
        self.root.clipboard_clear()
        self.root.clipboard_append("https://github.com/saprecar/Otter")
        messagebox.showinfo("Copied", "Repository link copied to clipboard:\nhttps://github.com/saprecar/Otter")

    def _toggle_conn_mode(self):
        if self.conn_mode.get() == "wifi":
            self.entry_ip.configure(state=tk.NORMAL)
            if self.entry_ip.get().strip() == "127.0.0.1":
                self.entry_ip.delete(0, tk.END)
                self.entry_ip.insert(0, "192.168.1.50")
        else:
            self.entry_ip.configure(state=tk.NORMAL)
            self.entry_ip.delete(0, tk.END)
            self.entry_ip.insert(0, "127.0.0.1")
            self.entry_ip.configure(state=tk.DISABLED)

    def _gui_auto_detect_ip(self):
        self.btn_auto_detect.configure(state=tk.DISABLED)
        self.log("Scanning local Wi-Fi network for Otter camera devices...")

        def scan_worker():
            try:
                try:
                    port = int(self.entry_stream_port.get().strip())
                except ValueError:
                    port = 8089
                found = network_discovery.scan_network_for_cameras(port=port)
                self.root.after(0, lambda: self._on_auto_detect_finished(found))
            except Exception as e:
                self.root.after(0, lambda: self._on_auto_detect_finished([]))

        threading.Thread(target=scan_worker, daemon=True).start()

    def _on_auto_detect_finished(self, found):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        if found:
            self.log(f"Auto-Discovery found {len(found)} active camera(s): {', '.join(found)}")
            self.conn_mode.set("wifi")
            self.entry_ip.configure(state=tk.NORMAL)
            self.entry_ip.delete(0, tk.END)
            self.entry_ip.insert(0, found[0])
            if len(found) > 1:
                messagebox.showinfo("Multiple Cameras Detected", f"Found {len(found)} active cameras on network:\n\n" + "\n".join(found) + f"\n\nSelected first device: {found[0]}.\nUse '+ Multi-Cam Instance' to run others in parallel.")
            else:
                messagebox.showinfo("Camera Found", f"Successfully detected Otter camera at IP:\n{found[0]}")
        else:
            self.log("Auto-Discovery: No active camera detected on standard subnet. Please verify phone Wi-Fi connection and IP.")
            messagebox.showinfo("Scan Complete", "No camera detected automatically.\nPlease ensure the Otter mobile app is running with stream started, or enter the phone's IP manually.")

    def _spawn_new_instance(self):
        try:
            cmd = [sys.executable, os.path.abspath(__file__)]
            subprocess.Popen(cmd)
            self.log("Spawned new parallel Otter desktop instance.")
        except Exception as e:
            self.log(f"Failed to spawn new instance: {e}")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def start_stream(self):
        mode = self.conn_mode.get()
        host = "127.0.0.1"

        try:
            stream_port = int(self.entry_stream_port.get().strip())
        except ValueError:
            stream_port = 8089

        try:
            ctrl_port = int(self.entry_ctrl_port.get().strip())
        except ValueError:
            ctrl_port = 8090

        cam_name = self.entry_cam_name.get().strip() or "Otter Camera"

        if mode == "usb":
            self.log(f"Setting up USB tunnel for Stream Port {stream_port} & Control Port {ctrl_port}...")
            self.adb_tunnel = ADBTunnel(stream_port=stream_port, control_port=ctrl_port)
            if not self.adb_tunnel.is_available():
                self.log("Notice: ADB executable not found on PC.")
                if messagebox.askyesno("Download Minimal ADB", "ADB is needed for USB mode, but neither Android Studio nor ADB is detected.\n\nWould you like Otter to download Google's official minimal platform-tools (~15MB)?"):
                    self._gui_download_adb()
                    return
                else:
                    self.log("ADB download skipped by user. Please install ADB or switch to Wi-Fi mode.")
                    return

            if not self.adb_tunnel.setup_forward():
                self.log("Warning: ADB port forwarding failed. Ensure phone has USB debugging ON and cable connected.")
            else:
                self.log(f"ADB USB forwarding established on ports {stream_port} / {ctrl_port}.")
        else:
            host = self.entry_ip.get().strip()
            if not host:
                messagebox.showerror("Error", "Please enter a valid phone IP address.")
                return
            self.log(f"Configured Wi-Fi connection to {host}:{stream_port}.")

        enable_vcam = self.vcam_var.get()
        self.log(f"Initializing receiver '{cam_name}' (Virtual Cam: {'Enabled' if enable_vcam else 'Disabled'})...")

        res_str = self.res_combo.get()
        width, height = 1280, 720
        if "1920" in res_str:
            width, height = 1920, 1080
        elif "640x480" in res_str:
            width, height = 640, 480
        elif "640x360" in res_str:
            width, height = 640, 360

        self.receiver = CamBridgeReceiver(host=host, stream_port=stream_port, control_port=ctrl_port, width=width, height=height, camera_name=cam_name)
        self.controller = CamBridgeControl(host=host, port=ctrl_port)

        self.receiver_thread = threading.Thread(target=self._run_receiver, args=(enable_vcam,), daemon=True)
        self.receiver_thread.start()

        self.is_connected = True
        self.btn_connect.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        self.status_badge.configure(text=f"ACTIVE: {cam_name}", fg="#3FB950")
        self.log(f"Stream receiver '{cam_name}' active on {host}:{stream_port}.")

    def _run_receiver(self, enable_vcam):
        try:
            # show_preview=False: cv2.imshow must only run on the main thread (Windows limitation)
            # Virtual camera output still works headlessly via DirectShow shared memory
            self.receiver.start_receiver(enable_virtualcam=enable_vcam, show_preview=False)
        except Exception as e:
            self.log(f"Receiver error: {e}")
        finally:
            self.root.after(0, self._on_receiver_stopped)

    def _on_receiver_stopped(self):
        self.is_connected = False
        self.btn_connect.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self.status_badge.configure(text="DISCONNECTED", fg="#DA3633")
        self.log("Stream receiver stopped.")

    def stop_stream(self):
        if self.receiver:
            self.receiver.stop_receiver()
        if self.adb_tunnel:
            self.adb_tunnel.remove_forward()
        self._on_receiver_stopped()

    def _get_active_host(self):
        if self.conn_mode.get() == "usb":
            return "127.0.0.1"
        return self.entry_ip.get().strip() or "127.0.0.1"

    def _get_active_ctrl_port(self):
        try:
            return int(self.entry_ctrl_port.get().strip())
        except Exception:
            return 8090

    def _debounce(self, key, delay_ms, func):
        if key in self._debounce_timers:
            try:
                self.root.after_cancel(self._debounce_timers[key])
            except Exception:
                pass
        self._debounce_timers[key] = self.root.after(delay_ms, func)

    def flip_camera(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.switch_camera()
        self.log(f"Flip Camera sent: {res}")

    def toggle_mirror(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_mirror()
        self.is_mirrored = not self.is_mirrored
        self.btn_mirror.configure(text=f"Mirror: {'ON' if self.is_mirrored else 'OFF'}")
        self.log(f"Toggle Mirror sent: {res}")

    def rotate_camera(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.rotate_camera()
        angle = res.get("rotationAngle", 0)
        self.btn_rotate.configure(text=f"Rotate: {angle}°")
        if self.receiver:
            self.receiver.set_rotation(angle)
        self.log(f"Rotate Camera to {angle}°: {res}")

    def toggle_torch(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_torch()
        self.log(f"Toggle Torch: {res}")

    def toggle_glow(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_glow()
        glow_name = res.get("glowName", "Cycle")
        self.btn_glow.configure(text=f"Front Glow: {glow_name}")
        self.log(f"Toggle Screen Glow: {res}")

    def capture_ultra_photo(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.capture_still()
        self.log(f"Capture Ultra Photo (Full Res): {res}")

    def on_res_change(self, event=None):
        res_str = self.res_combo.get()
        w, h = 1280, 720
        if "3840" in res_str or "4K" in res_str:
            w, h = 3840, 2160
        elif "1920" in res_str or "1080p" in res_str:
            w, h = 1920, 1080
        elif "1280" in res_str or "720p" in res_str:
            w, h = 1280, 720
        elif "640x480" in res_str or "480p" in res_str:
            w, h = 640, 480
        elif "640x360" in res_str or "360p" in res_str:
            w, h = 640, 360

        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_resolution(w, h)
        self.log(f"Set Resolution to {w}x{h}: {res}")

    def on_fps_change(self, event=None):
        fps_str = self.fps_combo.get()
        fps = 30
        if "60" in fps_str:
            fps = 60
        elif "15" in fps_str:
            fps = 15
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_fps(fps)
        self.log(f"Set Target FPS to {fps}: {res}")

    # Zoom controls (+/- Buttons and Slider)
    def _on_zoom_slide(self, val):
        z = float(val)
        self.current_zoom = z
        self.lbl_zoom.configure(text=f"{z:.1f}x")
        self._debounce("zoom", 80, lambda: self._send_zoom(z))

    def _send_zoom(self, z):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_zoom(z)
        self.log(f"Set Zoom to {z:.1f}x: {res}")

    def zoom_in(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.zoom_in()
        if res.get("status") == "ok":
            self.current_zoom = res.get("zoom", self.current_zoom)
            self.lbl_zoom.configure(text=f"{self.current_zoom:.1f}x")
            self.slider_zoom.set(self.current_zoom)
        self.log(f"Zoom In (+): {res}")

    def zoom_out(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.zoom_out()
        if res.get("status") == "ok":
            self.current_zoom = res.get("zoom", self.current_zoom)
            self.lbl_zoom.configure(text=f"{self.current_zoom:.1f}x")
            self.slider_zoom.set(self.current_zoom)
        self.log(f"Zoom Out (-): {res}")

    # Pro Controls: ISO
    def _toggle_iso_auto(self):
        is_auto = self.iso_auto_var.get()
        if is_auto:
            self.slider_iso.configure(state=tk.DISABLED)
            self.lbl_iso_val.configure(text="Auto", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_iso(0)
            self.log(f"Set ISO to Auto: {res}")
        else:
            self.slider_iso.configure(state=tk.NORMAL)
            idx = int(round(self.slider_iso.get()))
            iso_val = self.ISO_VALUES[idx]
            self.lbl_iso_val.configure(text=f"ISO {iso_val}", fg="#58A6FF")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_iso(iso_val)
            self.log(f"Set ISO to {iso_val}: {res}")

    def _on_iso_slide(self, val):
        if self.iso_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.ISO_VALUES):
            iso_val = self.ISO_VALUES[idx]
            self.lbl_iso_val.configure(text=f"ISO {iso_val}", fg="#58A6FF")
            self._debounce("iso", 100, lambda: self._send_iso(iso_val))

    def _send_iso(self, iso_val):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_iso(iso_val)
        self.log(f"Set ISO to {iso_val}: {res}")

    # Pro Controls: Shutter Speed
    def _toggle_shutter_auto(self):
        is_auto = self.shutter_auto_var.get()
        if is_auto:
            self.slider_shutter.configure(state=tk.DISABLED)
            self.lbl_shutter_val.configure(text="Auto", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_shutter(0)
            self.log(f"Set Shutter to Auto: {res}")
        else:
            self.slider_shutter.configure(state=tk.NORMAL)
            idx = int(round(self.slider_shutter.get()))
            ns, label = self.SHUTTER_STEPS[idx]
            self.lbl_shutter_val.configure(text=label, fg="#58A6FF")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_shutter(ns)
            self.log(f"Set Shutter to {label}: {res}")

    def _on_shutter_slide(self, val):
        if self.shutter_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.SHUTTER_STEPS):
            ns, label = self.SHUTTER_STEPS[idx]
            self.lbl_shutter_val.configure(text=label, fg="#58A6FF")
            self._debounce("shutter", 100, lambda: self._send_shutter(ns, label))

    def _send_shutter(self, ns, label):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_shutter(ns)
        self.log(f"Set Shutter to {label}: {res}")

    # Pro Controls: White Balance (WB)
    def _toggle_wb_auto(self):
        is_auto = self.wb_auto_var.get()
        if is_auto:
            self.slider_wb.configure(state=tk.DISABLED)
            self.lbl_wb_val.configure(text="Auto (AWB)", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_awb(0)
            self.log(f"Set WB to Auto: {res}")
        else:
            self.slider_wb.configure(state=tk.NORMAL)
            idx = int(round(self.slider_wb.get()))
            mode, label = self.WB_MODES[idx]
            self.lbl_wb_val.configure(text=label, fg="#58A6FF")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_awb(mode)
            self.log(f"Set WB to {label}: {res}")

    def _on_wb_slide(self, val):
        if self.wb_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.WB_MODES):
            mode, label = self.WB_MODES[idx]
            self.lbl_wb_val.configure(text=label, fg="#58A6FF")
            self._debounce("wb", 100, lambda: self._send_wb(mode, label))

    def _send_wb(self, mode, label):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_awb(mode)
        self.log(f"Set WB to {label}: {res}")

    # Pro Controls: Color FX / Filters
    def _toggle_fx_auto(self):
        is_auto = self.fx_auto_var.get()
        if is_auto:
            self.slider_fx.configure(state=tk.DISABLED)
            self.lbl_fx_val.configure(text="Normal Color", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_effect(0)
            self.log(f"Set Color FX to Normal: {res}")
        else:
            self.slider_fx.configure(state=tk.NORMAL)
            idx = int(round(self.slider_fx.get()))
            fx_mode, label = self.FX_MODES[idx]
            self.lbl_fx_val.configure(text=label, fg="#58A6FF")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_effect(fx_mode)
            self.log(f"Set Color FX to {label}: {res}")

    def _on_fx_slide(self, val):
        if self.fx_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.FX_MODES):
            fx_mode, label = self.FX_MODES[idx]
            self.lbl_fx_val.configure(text=label, fg="#58A6FF")
            self._debounce("fx", 100, lambda: self._send_fx(fx_mode, label))

    def _send_fx(self, fx_mode, label):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_effect(fx_mode)
        self.log(f"Set Color FX to {label}: {res}")

    # Pro Controls: EV Exposure Compensation
    def ev_step(self, delta: int):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.send_command({"action": "ev_step", "delta": delta})
        self.sync_remote_status()
        self.log(f"EV Step {delta:+d}: {res}")

    # Focus Controls
    def toggle_af(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_af()
        is_af = res.get("isAutoFocus", True)
        self.btn_af.configure(text="AF: Auto" if is_af else "AF: Manual", style="Green.TButton" if is_af else "Blue.TButton")
        self.btn_focus_dist.configure(text="Focus: Auto" if is_af else "Focus: Manual")
        self.log(f"Toggle AF: {res}")

    def cycle_focus(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.cycle_focus()
        dist = res.get("focusDistance", 0.0)
        self.btn_af.configure(text="AF: Manual", style="Blue.TButton")
        if dist <= 0.05:
            self.btn_focus_dist.configure(text="Focus: Inf")
        else:
            self.btn_focus_dist.configure(text=f"Focus: {dist:.1f}D")
        self.log(f"Cycle Focus Distance: {res}")

    def cycle_ev(self):
        self.ev_step(1)

    # Quick Mode presets
    def apply_quick_mode(self, mode: str):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_quick_mode(mode)
        self.log(f"Applied Quick Mode '{mode.upper()}': {res}")
        self.root.after(300, self.sync_remote_status)

    def sync_remote_status(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.get_status()
        if res.get("status") == "ok":
            self._apply_synced_status(res)
            self.log(f"Synced Device Status: {res}")
        else:
            self.log(f"Sync failed: {res}")

        try:
            caps = self.controller.get_capabilities()
            if caps.get("status") == "ok":
                res_list = caps.get("resolutions", [])
                if res_list:
                    current_res = self.res_combo.get()
                    self.res_combo.configure(values=res_list)
                    if current_res in res_list:
                        self.res_combo.set(current_res)
                fps_list = caps.get("fpsRanges", [])
                if fps_list:
                    fps_labels = [f"{f} FPS" for f in fps_list]
                    current_fps = self.fps_combo.get()
                    self.fps_combo.configure(values=fps_labels)
                    if current_fps in fps_labels:
                        self.fps_combo.set(current_fps)
                max_z = caps.get("maxZoom")
                if max_z and float(max_z) > 1.0:
                    self.slider_zoom.configure(to=float(max_z))
        except Exception:
            pass

    def _poll_status_loop(self):
        while True:
            time.sleep(3)
            if self.is_connected and self.controller:
                try:
                    res = self.controller.get_status()
                    if res.get("status") == "ok":
                        self.root.after(0, lambda r=res: self._apply_synced_status(r))
                except Exception:
                    pass

    def _apply_synced_status(self, r: dict):
        try:
            # AF
            is_af = r.get("isAutoFocus", True)
            self.btn_af.configure(text="AF: Auto" if is_af else "AF: Manual", style="Green.TButton" if is_af else "Blue.TButton")
            dist = r.get("focusDistance", 0.0)
            if is_af:
                self.btn_focus_dist.configure(text="Focus: Auto")
            elif dist <= 0.05:
                self.btn_focus_dist.configure(text="Focus: Inf")
            else:
                self.btn_focus_dist.configure(text=f"Focus: {dist:.1f}D")

            # EV
            ev = r.get("ev", 0.0)
            self.lbl_ev.configure(text=f"EV: {ev:+.1f}")

            # Zoom
            zoom = r.get("zoom", self.current_zoom)
            self.current_zoom = zoom
            self.lbl_zoom.configure(text=f"{zoom:.1f}x")
            self.slider_zoom.set(zoom)

            # Lens & Mirror & Rotation
            lens = r.get("lens", "BACK")
            self.btn_flip.configure(text=f"Flip ({lens})")

            mirrored = r.get("mirrored", False)
            self.is_mirrored = mirrored
            self.btn_mirror.configure(text=f"Mirror: {'ON' if mirrored else 'OFF'}")

            glow = r.get("glowName", "OFF")
            self.btn_glow.configure(text=f"Front Glow: {glow}")

            angle = r.get("rotationAngle")
            if angle is not None:
                self.btn_rotate.configure(text=f"Rotate: {angle}°")
                if self.receiver and self.receiver.rotation_angle != angle:
                    self.receiver.set_rotation(angle)

            # ISO sync
            iso_val = r.get("iso", 0)
            if iso_val == 0:
                self.iso_auto_var.set(True)
                self.slider_iso.configure(state=tk.DISABLED)
                self.lbl_iso_val.configure(text="Auto", fg="#8B949E")
            else:
                self.iso_auto_var.set(False)
                self.slider_iso.configure(state=tk.NORMAL)
                closest_idx = min(range(len(self.ISO_VALUES)), key=lambda i: abs(self.ISO_VALUES[i] - iso_val))
                self.slider_iso.set(closest_idx)
                self.lbl_iso_val.configure(text=f"ISO {self.ISO_VALUES[closest_idx]}", fg="#58A6FF")

            # Shutter sync
            shutter_val = r.get("shutter", 0)
            if shutter_val == 0:
                self.shutter_auto_var.set(True)
                self.slider_shutter.configure(state=tk.DISABLED)
                self.lbl_shutter_val.configure(text="Auto", fg="#8B949E")
            else:
                self.shutter_auto_var.set(False)
                self.slider_shutter.configure(state=tk.NORMAL)
                closest_idx = min(range(len(self.SHUTTER_STEPS)), key=lambda i: abs(self.SHUTTER_STEPS[i][0] - shutter_val))
                self.slider_shutter.set(closest_idx)
                self.lbl_shutter_val.configure(text=self.SHUTTER_STEPS[closest_idx][1], fg="#58A6FF")

            # AWB sync
            awb_str = r.get("awb", "Auto")
            if awb_str == "Auto":
                self.wb_auto_var.set(True)
                self.slider_wb.configure(state=tk.DISABLED)
                self.lbl_wb_val.configure(text="Auto (AWB)", fg="#8B949E")
            else:
                self.wb_auto_var.set(False)
                self.slider_wb.configure(state=tk.NORMAL)
                for idx, (m, lbl) in enumerate(self.WB_MODES):
                    if awb_str.lower() in lbl.lower():
                        self.slider_wb.set(idx)
                        self.lbl_wb_val.configure(text=lbl, fg="#58A6FF")
                        break

            # Effect sync
            effect_str = r.get("effect", "Color")
            if effect_str == "Color" or effect_str == "Off":
                self.fx_auto_var.set(True)
                self.slider_fx.configure(state=tk.DISABLED)
                self.lbl_fx_val.configure(text="Normal Color", fg="#8B949E")
            else:
                self.fx_auto_var.set(False)
                self.slider_fx.configure(state=tk.NORMAL)
                for idx, (m, lbl) in enumerate(self.FX_MODES):
                    if effect_str.lower() in lbl.lower():
                        self.slider_fx.set(idx)
                        self.lbl_fx_val.configure(text=lbl, fg="#58A6FF")
                        break

        except Exception:
            pass

    def on_close(self):
        self.stop_stream()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OtterApp(root)
    root.mainloop()

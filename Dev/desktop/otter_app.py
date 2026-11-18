import sys
import os

# Ensure local script directory is root of module resolution
_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if _CURRENT_DIR not in sys.path:
    sys.path.insert(0, _CURRENT_DIR)

import threading
import time
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import webbrowser
import subprocess

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

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

# [AI-BLOCK: Custom Material Design 3 Pill Switch]
class MaterialSwitch(tk.Canvas):
    """
    Compact Material Design 3 toggle switch with animated rounded track and circle thumb knob.
    """
    def __init__(self, parent, command=None, initial=False, width=44, height=22, bg="#161B22", active_color="#1F6FEB"):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, cursor="hand2")
        self.command = command
        self.is_on = bool(initial)
        self.width = width
        self.height = height
        self.active_color = active_color
        self.bind("<Button-1>", self.toggle)
        self.draw()

    def set_state(self, is_on):
        self.is_on = bool(is_on)
        self.draw()

    def toggle(self, event=None):
        self.is_on = not self.is_on
        self.draw()
        if self.command:
            self.command(self.is_on)

    def draw(self):
        self.delete("all")
        r = self.height / 2
        track_color = self.active_color if self.is_on else "#21262D"
        border_color = "#388BFD" if self.is_on else "#30363D"
        thumb_color = "#FFFFFF" if self.is_on else "#8B949E"
        thumb_x = (self.width - r - 2) if self.is_on else (r + 2)

        # Draw rounded pill track
        self.create_arc((1, 1, self.height - 1, self.height - 1), start=90, extent=180, fill=track_color, outline=border_color)
        self.create_arc((self.width - self.height, 1, self.width - 1, self.height - 1), start=270, extent=180, fill=track_color, outline=border_color)
        self.create_rectangle((r, 1, self.width - r, self.height - 1), fill=track_color, outline=border_color)
        self.create_rectangle((r, 2, self.width - r, self.height - 2), fill=track_color, outline=track_color)

        # Draw thumb knob
        tr = r - 3
        self.create_oval((thumb_x - tr, r - tr, thumb_x + tr, r + tr), fill=thumb_color, outline="")

# [AI-BLOCK: Custom Material Design 3 Segmented Control]
class SegmentedControl(tk.Frame):
    """
    Material Design 3 segmented button group with active state highlighting.
    """
    def __init__(self, parent, options, command=None, initial=None, bg="#161B22"):
        super().__init__(parent, bg=bg)
        self.options = options
        self.command = command
        self.selected = initial if initial is not None else (options[0][0] if options else None)
        self.buttons = {}

        self.container = tk.Frame(self, bg="#21262D", padx=2, pady=2, highlightbackground="#30363D", highlightthickness=1)
        self.container.pack(fill=tk.BOTH, expand=True)

        for val, label in options:
            btn = tk.Label(
                self.container,
                text=label,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
                padx=11,
                pady=5
            )
            btn.pack(side=tk.LEFT, padx=1)
            btn.bind("<Button-1>", lambda e, v=val: self.select(v))
            self.buttons[val] = btn

        self._refresh()

    def select(self, val, notify=True):
        self.selected = val
        self._refresh()
        if notify and self.command:
            self.command(val)

    def _refresh(self):
        for val, btn in self.buttons.items():
            if val == self.selected:
                btn.configure(bg="#1F6FEB", fg="#FFFFFF")
            else:
                btn.configure(bg="#21262D", fg="#8B949E")

# [AI-BLOCK: Material Card Container with Subtle Border]
class CardFrame(tk.Frame):
    def __init__(self, parent, title=None, icon=None, header_right=None, bg="#161B22", border="#263040", **kwargs):
        super().__init__(parent, bg=bg, highlightbackground=border, highlightthickness=1, padx=12, pady=10, **kwargs)
        if title:
            h_row = tk.Frame(self, bg=bg)
            h_row.pack(fill=tk.X, pady=(0, 8))
            title_text = f"{icon}  {title}" if icon else title
            tk.Label(h_row, text=title_text, font=("Segoe UI", 10, "bold"), fg="#58A6FF", bg=bg).pack(side=tk.LEFT)
            if header_right:
                header_right(h_row)

# [AI-BLOCK: Main Otter Desktop Controller - Material Design 3 Aesthetic]
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
        self.root.geometry("1060x720")
        self.root.minsize(980, 640)
        self.root.configure(bg="#0B0F14")

        self.receiver = None
        self.receiver_thread = None
        self.adb_tunnel = None
        self.controller = None
        self.is_connected = False
        self.active_mode = None
        self.active_host = None
        self.current_zoom = 1.0
        self.current_lens = "BACK"
        self.is_mirrored = False
        self.torch_state = 0
        self.glow_state = 0
        self.keep_screen_on = True
        self._last_preview_time = 0
        self._preview_photo = None
        self._bg_photo = None
        self._debounce_timers = {}

        self.conn_mode = tk.StringVar(value="auto")
        self.vcam_var = tk.BooleanVar(value=True)

        self.iso_auto_var = tk.BooleanVar(value=True)
        self.shutter_auto_var = tk.BooleanVar(value=True)
        self.wb_auto_var = tk.BooleanVar(value=True)
        self.fx_auto_var = tk.BooleanVar(value=True)

        self.bg_workload_var = tk.StringVar(value="pc")
        self.bg_mode_var = tk.StringVar(value="off")
        self.bg_image_path = None

        self._ui_queue = queue.Queue()
        self._poll_ui_queue()

        self._setup_styles()
        self._build_header()
        self._build_main_content()

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
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)
        dlg.grab_set()

        def _on_decline():
            dlg.destroy()
            self.root.destroy()
            sys.exit(0)

        dlg.protocol("WM_DELETE_WINDOW", _on_decline)

        card = tk.Frame(dlg, bg="#161B22", padx=20, pady=20, highlightbackground="#30363D", highlightthickness=1)
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
            "  is solely governed by their respective policies.\n\n"
            "• Absolute Disclaimer of Warranties & Liability ('AS-IS'):\n"
            "  The software is provided without warranties. Developers hold zero liability for local network\n"
            "  interception, data loss, packet eavesdropping, hardware stress, or software bugs.\n\n"
            "• Mandatory Attribution Clause:\n"
            "  Any reuse, redistribution, or derivation must prominently credit 'spacecar', name 'Otter',\n"
            "  and link to https://github.com/saprecar/Otter.\n\n"
            "• Governing Law & Exclusive Jurisdiction:\n"
            "  Governed by the Laws of the Republic of India (Information Technology Act, 2000).\n"
            "  Exclusive jurisdiction: Competent Courts of Narmadapuram, Madhya Pradesh, India (PIN: 461001 / 461005)."
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

        style.configure("TFrame", background="#161B22")
        style.configure("TLabel", background="#161B22", foreground="#C9D1D9", font=("Segoe UI", 9))

        # Buttons
        style.configure("Blue.TButton", font=("Segoe UI", 9, "bold"), background="#1F6FEB", foreground="#FFFFFF", borderwidth=0)
        style.map("Blue.TButton", background=[("active", "#388BFD"), ("disabled", "#30363D")])

        style.configure("Green.TButton", font=("Segoe UI", 9, "bold"), background="#238636", foreground="#FFFFFF", borderwidth=0)
        style.map("Green.TButton", background=[("active", "#2EA043"), ("disabled", "#30363D")])

        style.configure("Red.TButton", font=("Segoe UI", 9, "bold"), background="#DA3633", foreground="#FFFFFF", borderwidth=0)
        style.map("Red.TButton", background=[("active", "#F85149"), ("disabled", "#30363D")])

        style.configure("Dark.TButton", font=("Segoe UI", 9), background="#21262D", foreground="#C9D1D9", borderwidth=0)
        style.map("Dark.TButton", background=[("active", "#30363D"), ("disabled", "#161B22")])

        style.configure("Purple.TButton", font=("Segoe UI", 9, "bold"), background="#8957E5", foreground="#FFFFFF", borderwidth=0)
        style.map("Purple.TButton", background=[("active", "#A371F7"), ("disabled", "#30363D")])

        style.configure("Orange.TButton", font=("Segoe UI", 9, "bold"), background="#D29922", foreground="#FFFFFF", borderwidth=0)
        style.map("Orange.TButton", background=[("active", "#E3B341"), ("disabled", "#30363D")])

        style.configure("Cyan.TButton", font=("Segoe UI", 9, "bold"), background="#008080", foreground="#FFFFFF", borderwidth=0)
        style.map("Cyan.TButton", background=[("active", "#00A0A0"), ("disabled", "#30363D")])

        style.configure("Indigo.TButton", font=("Segoe UI", 9, "bold"), background="#388BFD", foreground="#FFFFFF", borderwidth=0)
        style.map("Indigo.TButton", background=[("active", "#58A6FF"), ("disabled", "#30363D")])

        style.configure("Lime.TButton", font=("Segoe UI", 9, "bold"), background="#2EA043", foreground="#FFFFFF", borderwidth=0)
        style.map("Lime.TButton", background=[("active", "#3FB950"), ("disabled", "#30363D")])

        style.configure("Violet.TButton", font=("Segoe UI", 9, "bold"), background="#6E40C9", foreground="#FFFFFF", borderwidth=0)
        style.map("Violet.TButton", background=[("active", "#8957E5"), ("disabled", "#30363D")])

        # Dark Combobox
        style.configure("TCombobox", fieldbackground="#0D1117", background="#21262D", foreground="#C9D1D9", arrowcolor="#58A6FF", borderwidth=1)
        style.map("TCombobox", fieldbackground=[("readonly", "#0D1117")], foreground=[("readonly", "#C9D1D9")])

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg="#0B0F14", pady=8, padx=16)
        header_frame.pack(fill=tk.X)

        left_box = tk.Frame(header_frame, bg="#0B0F14")
        left_box.pack(side=tk.LEFT)

        # Mascot Avatar
        avatar = tk.Canvas(left_box, width=38, height=38, bg="#0B0F14", highlightthickness=0)
        avatar.pack(side=tk.LEFT, padx=(0, 10))
        avatar.create_oval(2, 2, 36, 36, fill="#1F6FEB", outline="#388BFD", width=2)
        avatar.create_text(19, 19, text="OT", font=("Segoe UI", 12, "bold"), fill="#FFFFFF")

        title_box = tk.Frame(left_box, bg="#0B0F14")
        title_box.pack(side=tk.LEFT)

        title_lbl = tk.Label(title_box, text="Otter", font=("Segoe UI", 18, "bold"), fg="#58A6FF", bg="#0B0F14")
        title_lbl.pack(anchor="w")

        tagline = tk.Label(title_box, text="Virtual Webcam & Remote Controller", font=("Segoe UI", 9), fg="#8B949E", bg="#0B0F14")
        tagline.pack(anchor="w")

        # Connection Status Pill Badge
        self.status_badge = tk.Label(
            header_frame,
            text="● Disconnected",
            font=("Segoe UI", 9, "bold"),
            fg="#DA3633",
            bg="#21262D",
            padx=14,
            pady=5,
            relief=tk.FLAT
        )
        self.status_badge.pack(side=tk.RIGHT)

    def _build_main_content(self):
        # Outer container with canvas for seamless viewport scaling across all screens
        container = tk.Frame(self.root, bg="#0B0F14")
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 6))

        canvas = tk.Canvas(container, bg="#0B0F14", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0B0F14")

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

        # Section 1: Connection Card (Full Width)
        self._build_connection_card(scrollable_frame)

        # Section 2: Quick Modes Card (Full Width)
        self._build_quick_modes_card(scrollable_frame)

        # Section 3: Main 3-Column Responsive Control Grid
        self._build_cards_grid(scrollable_frame)

    # --- 1. Connection Card ---
    def _build_connection_card(self, parent):
        card = CardFrame(parent, title="Connection", icon="[Link]")
        card.pack(fill=tk.X, pady=(0, 8))

        row = tk.Frame(card, bg="#161B22")
        row.pack(fill=tk.X, pady=2)

        # Mode Segmented Control
        mode_options = [
            ("auto", "Auto (USB -> Wi-Fi)"),
            ("tether", "USB Tethering"),
            ("usb", "ADB Tunnel"),
            ("wifi", "Wi-Fi LAN IP")
        ]
        self.seg_mode = SegmentedControl(row, mode_options, command=self._on_seg_mode_change, initial=self.conn_mode.get(), bg="#161B22")
        self.seg_mode.pack(side=tk.LEFT, padx=(0, 14))

        # IP Address input
        tk.Label(row, text="IP Address:", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_ip = tk.Entry(row, width=14, font=("Segoe UI", 9), bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT, highlightbackground="#30363D", highlightthickness=1)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.pack(side=tk.LEFT, padx=(0, 4), ipady=3)

        btn_copy_ip = tk.Button(row, text="Copy", font=("Segoe UI", 8), bg="#21262D", fg="#8B949E", activebackground="#30363D", activeforeground="#FFFFFF", bd=0, padx=6, pady=3, cursor="hand2", command=self._copy_ip_to_clipboard)
        btn_copy_ip.pack(side=tk.LEFT, padx=(0, 10))

        # Auto Detect IP button
        self.btn_auto_detect = ttk.Button(row, text="Auto Detect IP", style="Dark.TButton", command=self._gui_auto_detect_ip)
        self.btn_auto_detect.pack(side=tk.LEFT, padx=(0, 10))

        # Hidden but accessible Ports & Virtual Cam state
        self.entry_stream_port = tk.Entry(row)
        self.entry_stream_port.insert(0, "8089")
        self.entry_ctrl_port = tk.Entry(row)
        self.entry_ctrl_port.insert(0, "8090")
        self.entry_cam_name = tk.Entry(row)
        self.entry_cam_name.insert(0, "Otter Cam 1")

        # Action Buttons
        self.btn_connect = ttk.Button(row, text="Connect & Start", style="Blue.TButton", command=self.start_stream)
        self.btn_connect.pack(side=tk.RIGHT, padx=(4, 0))

        self.btn_stop = ttk.Button(row, text="Stop", style="Red.TButton", command=self.stop_stream)
        self.btn_stop.configure(state=tk.DISABLED)
        self.btn_stop.pack(side=tk.RIGHT, padx=4)

    def _on_seg_mode_change(self, mode):
        self.conn_mode.set(mode)
        self._toggle_conn_mode()

    def _copy_ip_to_clipboard(self):
        ip = self.entry_ip.get().strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(ip)
        self.log(f"Copied IP to clipboard: {ip}")

    # --- 2. Quick Modes Card ---
    def _build_quick_modes_card(self, parent):
        card = CardFrame(parent, title="Quick Modes (One-Click Presets)", icon="[⚡]")
        card.pack(fill=tk.X, pady=(0, 8))

        row = tk.Frame(card, bg="#161B22")
        row.pack(fill=tk.X, pady=2)

        presets = [
            ("Meetings", "Blue.TButton", "meetings"),
            ("Online Class", "Purple.TButton", "class"),
            ("Streaming", "Green.TButton", "streaming"),
            ("Snapshot", "Orange.TButton", "snapshot"),
            ("Scan / OCR", "Cyan.TButton", "scan"),
            ("Security", "Indigo.TButton", "security"),
            ("Fun Filter", "Lime.TButton", "fun"),
            ("Pro Reset", "Violet.TButton", "pro")
        ]

        for text, style_name, mode_val in presets:
            btn = ttk.Button(row, text=text, style=style_name, command=lambda m=mode_val: self.apply_quick_mode(m))
            btn.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)

    # --- 3. Main 3-Column Responsive Grid ---
    def _build_cards_grid(self, parent):
        grid_frame = tk.Frame(parent, bg="#0B0F14")
        grid_frame.pack(fill=tk.BOTH, expand=True)

        for col in range(3):
            grid_frame.columnconfigure(col, weight=1, uniform="col")

        # Row 0
        self._build_camera_card(grid_frame)
        self._build_image_controls_card(grid_frame)
        self._build_lighting_card(grid_frame)

        # Row 1
        self._build_background_card(grid_frame)
        self._build_more_controls_card(grid_frame)
        self._build_event_log_card(grid_frame)

    # --- Card 1: Camera Card ---
    def _build_camera_card(self, parent):
        def _header_right(h_frame):
            # Lens Front/Rear Segmented Button
            self.seg_lens = SegmentedControl(h_frame, [("FRONT", "Front"), ("BACK", "Rear")], command=self._on_lens_toggle, initial="BACK", bg="#161B22")
            self.seg_lens.pack(side=tk.RIGHT, padx=(6, 0))

            # Rotate button
            self.btn_rotate = tk.Button(h_frame, text="Rotate", font=("Segoe UI", 8, "bold"), bg="#21262D", fg="#8B949E", activebackground="#30363D", bd=0, padx=6, pady=3, cursor="hand2", command=self.rotate_camera)
            self.btn_rotate.pack(side=tk.RIGHT, padx=4)

            # Flip lens wrapper button reference
            self.btn_flip = tk.Label(h_frame, text="Flip", fg="#8B949E", bg="#161B22")

        card = CardFrame(parent, title="Camera", icon="[Cam]", header_right=_header_right)
        card.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        body = tk.Frame(card, bg="#161B22")
        body.pack(fill=tk.BOTH, expand=True)

        # Left: Live Preview Canvas
        self.preview_canvas = tk.Canvas(body, width=150, height=110, bg="#0D1117", highlightthickness=1, highlightbackground="#30363D")
        self.preview_canvas.pack(side=tk.LEFT, padx=(0, 10), pady=4)
        self._draw_idle_preview()

        # Right: Resolution, FPS, Zoom, Ultra Photo
        ctrl_box = tk.Frame(body, bg="#161B22")
        ctrl_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Resolution dropdown
        tk.Label(ctrl_box, text="Resolution:", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(anchor="w")
        self.res_combo = ttk.Combobox(
            ctrl_box,
            values=["720p (1280x720)", "1080p (1920x1080)", "4K (3840x2160)", "640x480 (480p)", "640x360 (360p)"],
            state="readonly",
            width=18
        )
        self.res_combo.set("720p (1280x720)")
        self.res_combo.pack(fill=tk.X, pady=(0, 4))
        self.res_combo.bind("<<ComboboxSelected>>", self.on_res_change)

        # Frame Rate dropdown
        tk.Label(ctrl_box, text="Frame Rate:", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(anchor="w")
        self.fps_combo = ttk.Combobox(
            ctrl_box,
            values=["30 FPS", "60 FPS", "15 FPS"],
            state="readonly",
            width=18
        )
        self.fps_combo.set("30 FPS")
        self.fps_combo.pack(fill=tk.X, pady=(0, 4))
        self.fps_combo.bind("<<ComboboxSelected>>", self.on_fps_change)

        # Zoom row
        zoom_row = tk.Frame(ctrl_box, bg="#161B22")
        zoom_row.pack(fill=tk.X, pady=(2, 4))
        tk.Label(zoom_row, text="Zoom:", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(side=tk.LEFT)

        btn_zm_minus = tk.Button(zoom_row, text="-", font=("Segoe UI", 8, "bold"), bg="#21262D", fg="#C9D1D9", bd=0, padx=5, pady=0, command=self.zoom_out)
        btn_zm_minus.pack(side=tk.LEFT, padx=(4, 2))

        self.slider_zoom = tk.Scale(
            zoom_row,
            from_=1.0,
            to=8.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
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
        self.slider_zoom.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btn_zm_plus = tk.Button(zoom_row, text="+", font=("Segoe UI", 8, "bold"), bg="#21262D", fg="#C9D1D9", bd=0, padx=5, pady=0, command=self.zoom_in)
        btn_zm_plus.pack(side=tk.LEFT, padx=(2, 4))

        self.lbl_zoom = tk.Label(zoom_row, text="1.0x", font=("Segoe UI", 8, "bold"), fg="#58A6FF", bg="#161B22", width=4)
        self.lbl_zoom.pack(side=tk.LEFT)

        # Ultra Photo & Mirror row
        act_row = tk.Frame(ctrl_box, bg="#161B22")
        act_row.pack(fill=tk.X, pady=(2, 0))

        self.btn_ultra_photo = ttk.Button(act_row, text="Ultra Photo", style="Orange.TButton", command=self.capture_ultra_photo)
        self.btn_ultra_photo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 4))

        self.btn_mirror = ttk.Button(act_row, text="Mirror: OFF", style="Dark.TButton", command=self.toggle_mirror)
        self.btn_mirror.pack(side=tk.RIGHT)

    def _draw_idle_preview(self):
        self.preview_canvas.delete("all")
        # Camera viewfinder UI layout
        self.preview_canvas.create_rectangle(10, 10, 140, 100, outline="#21262D", width=1)
        # Crosshairs / Viewfinder corners
        self.preview_canvas.create_line(15, 20, 25, 20, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(20, 15, 20, 25, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(125, 20, 135, 20, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(130, 15, 130, 25, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(15, 90, 25, 90, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(20, 85, 20, 95, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(125, 90, 135, 90, fill="#58A6FF", width=2)
        self.preview_canvas.create_line(130, 85, 130, 95, fill="#58A6FF", width=2)
        # Center status
        self.preview_canvas.create_oval(67, 47, 83, 63, outline="#388BFD", width=2)
        self.preview_canvas.create_text(75, 78, text="CAMERA READY", font=("Segoe UI", 7, "bold"), fill="#8B949E")

    def _on_lens_toggle(self, val):
        if val != self.current_lens:
            self.flip_camera()

    # --- Card 2: Image Controls Card ---
    def _build_image_controls_card(self, parent):
        card = CardFrame(parent, title="Image Controls", icon="[FX]")
        card.grid(row=0, column=1, sticky="nsew", padx=4, pady=4)

        box = tk.Frame(card, bg="#161B22")
        box.pack(fill=tk.BOTH, expand=True)

        # Row 1: ISO
        row_iso = tk.Frame(box, bg="#161B22")
        row_iso.pack(fill=tk.X, pady=2)
        tk.Label(row_iso, text="ISO", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=12, anchor="w").pack(side=tk.LEFT)
        self.sw_iso = MaterialSwitch(row_iso, command=self._on_switch_iso, initial=True, bg="#161B22")
        self.sw_iso.pack(side=tk.LEFT, padx=(0, 8))
        self.lbl_iso_val = tk.Label(row_iso, text="Auto", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_iso_val.pack(side=tk.LEFT)

        # Hidden slider for internal math compatibility
        self.slider_iso = tk.Scale(row_iso, from_=0, to=len(self.ISO_VALUES)-1, orient=tk.HORIZONTAL)

        # Row 2: Shutter
        row_sh = tk.Frame(box, bg="#161B22")
        row_sh.pack(fill=tk.X, pady=2)
        tk.Label(row_sh, text="Shutter", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=12, anchor="w").pack(side=tk.LEFT)
        self.sw_shutter = MaterialSwitch(row_sh, command=self._on_switch_shutter, initial=True, bg="#161B22")
        self.sw_shutter.pack(side=tk.LEFT, padx=(0, 8))
        self.lbl_shutter_val = tk.Label(row_sh, text="Auto", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_shutter_val.pack(side=tk.LEFT)
        self.slider_shutter = tk.Scale(row_sh, from_=0, to=len(self.SHUTTER_STEPS)-1, orient=tk.HORIZONTAL)

        # Row 3: White Balance
        row_wb = tk.Frame(box, bg="#161B22")
        row_wb.pack(fill=tk.X, pady=2)
        tk.Label(row_wb, text="White Balance", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=12, anchor="w").pack(side=tk.LEFT)
        self.sw_wb = MaterialSwitch(row_wb, command=self._on_switch_wb, initial=True, bg="#161B22")
        self.sw_wb.pack(side=tk.LEFT, padx=(0, 8))
        self.lbl_wb_val = tk.Label(row_wb, text="Auto (AWB)", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_wb_val.pack(side=tk.LEFT)
        self.slider_wb = tk.Scale(row_wb, from_=0, to=len(self.WB_MODES)-1, orient=tk.HORIZONTAL)

        # Row 4: Color FX
        row_fx = tk.Frame(box, bg="#161B22")
        row_fx.pack(fill=tk.X, pady=2)
        tk.Label(row_fx, text="Color FX", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22", width=12, anchor="w").pack(side=tk.LEFT)
        self.sw_fx = MaterialSwitch(row_fx, command=self._on_switch_fx, initial=True, bg="#161B22")
        self.sw_fx.pack(side=tk.LEFT, padx=(0, 8))
        self.lbl_fx_val = tk.Label(row_fx, text="Normal Color", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=14, anchor="w")
        self.lbl_fx_val.pack(side=tk.LEFT)
        self.slider_fx = tk.Scale(row_fx, from_=0, to=len(self.FX_MODES)-1, orient=tk.HORIZONTAL)

        # Action pills row
        act_row = tk.Frame(box, bg="#161B22")
        act_row.pack(fill=tk.X, pady=(6, 0))

        self.btn_af = ttk.Button(act_row, text="AF: Auto", style="Green.TButton", command=self.toggle_af)
        self.btn_af.pack(side=tk.LEFT, padx=(0, 3), expand=True, fill=tk.X)

        self.btn_focus_dist = ttk.Button(act_row, text="Focus", style="Dark.TButton", command=self.cycle_focus)
        self.btn_focus_dist.pack(side=tk.LEFT, padx=3, expand=True, fill=tk.X)

        self.btn_ev_minus = ttk.Button(act_row, text="EV -", style="Dark.TButton", command=lambda: self.ev_step(-1))
        self.btn_ev_minus.pack(side=tk.LEFT, padx=2)

        self.lbl_ev = tk.Label(act_row, text="+0.0", font=("Segoe UI", 8, "bold"), fg="#58A6FF", bg="#161B22", width=5)
        self.lbl_ev.pack(side=tk.LEFT)

        self.btn_ev_plus = ttk.Button(act_row, text="EV +", style="Dark.TButton", command=lambda: self.ev_step(1))
        self.btn_ev_plus.pack(side=tk.LEFT, padx=2)

        self.btn_sync_status = ttk.Button(act_row, text="Sync", style="Blue.TButton", command=self.sync_remote_status)
        self.btn_sync_status.pack(side=tk.RIGHT, padx=(3, 0))

    def _on_switch_iso(self, is_on):
        self.iso_auto_var.set(is_on)
        self._toggle_iso_auto()

    def _on_switch_shutter(self, is_on):
        self.shutter_auto_var.set(is_on)
        self._toggle_shutter_auto()

    def _on_switch_wb(self, is_on):
        self.wb_auto_var.set(is_on)
        self._toggle_wb_auto()

    def _on_switch_fx(self, is_on):
        self.fx_auto_var.set(is_on)
        self._toggle_fx_auto()

    # --- Card 3: Lighting Card ---
    def _build_lighting_card(self, parent):
        card = CardFrame(parent, title="Lighting", icon="[Light]")
        card.grid(row=0, column=2, sticky="nsew", padx=4, pady=4)

        box = tk.Frame(card, bg="#161B22")
        box.pack(fill=tk.BOTH, expand=True)

        # Torch row
        row_t = tk.Frame(box, bg="#161B22")
        row_t.pack(fill=tk.X, pady=2)
        tk.Label(row_t, text="Torch", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22").pack(side=tk.LEFT)
        self.lbl_torch_val = tk.Label(row_t, text="Off", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=6, anchor="e")
        self.lbl_torch_val.pack(side=tk.RIGHT)
        self.sw_torch = MaterialSwitch(row_t, command=lambda v: self.toggle_torch(), initial=False, bg="#161B22")
        self.sw_torch.pack(side=tk.RIGHT, padx=6)
        self.btn_torch = self.lbl_torch_val # compat reference

        # Front Glow row
        row_g = tk.Frame(box, bg="#161B22")
        row_g.pack(fill=tk.X, pady=2)
        tk.Label(row_g, text="Front Glow", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22").pack(side=tk.LEFT)
        self.lbl_glow_val = tk.Label(row_g, text="Off", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22", width=6, anchor="e")
        self.lbl_glow_val.pack(side=tk.RIGHT)
        self.sw_glow = MaterialSwitch(row_g, command=lambda v: self.toggle_glow(), initial=False, bg="#161B22")
        self.sw_glow.pack(side=tk.RIGHT, padx=6)
        self.btn_glow = self.lbl_glow_val # compat reference

        # Screen Keep ON row
        row_s = tk.Frame(box, bg="#161B22")
        row_s.pack(fill=tk.X, pady=2)
        tk.Label(row_s, text="Screen Keep ON", font=("Segoe UI", 9, "bold"), fg="#C9D1D9", bg="#161B22").pack(side=tk.LEFT)
        self.lbl_keep_screen_val = tk.Label(row_s, text="On", font=("Segoe UI", 8, "bold"), fg="#3FB950", bg="#161B22", width=6, anchor="e")
        self.lbl_keep_screen_val.pack(side=tk.RIGHT)
        self.sw_keep_screen = MaterialSwitch(row_s, command=lambda v: self.toggle_keep_screen(), initial=True, bg="#161B22", active_color="#238636")
        self.sw_keep_screen.pack(side=tk.RIGHT, padx=6)
        self.btn_keep_screen = self.lbl_keep_screen_val # compat reference

        # Brightness / EV Slider
        row_b = tk.Frame(box, bg="#161B22")
        row_b.pack(fill=tk.X, pady=(4, 2))
        tk.Label(row_b, text="Brightness", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(side=tk.LEFT)
        self.slider_ev = tk.Scale(
            row_b, from_=-4, to=4, resolution=1, orient=tk.HORIZONTAL,
            bg="#161B22", fg="#58A6FF", troughcolor="#0D1117", activebackground="#1F6FEB",
            highlightthickness=0, bd=0, sliderrelief=tk.FLAT, showvalue=False,
            command=self._on_brightness_slide
        )
        self.slider_ev.set(0)
        self.slider_ev.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))

        # Color Temp Slider
        row_ct = tk.Frame(box, bg="#161B22")
        row_ct.pack(fill=tk.X, pady=(2, 0))
        tk.Label(row_ct, text="Color Temp", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(side=tk.LEFT)
        self.slider_temp = tk.Scale(
            row_ct, from_=0, to=len(self.WB_MODES)-1, resolution=1, orient=tk.HORIZONTAL,
            bg="#161B22", fg="#58A6FF", troughcolor="#0D1117", activebackground="#1F6FEB",
            highlightthickness=0, bd=0, sliderrelief=tk.FLAT, showvalue=False,
            command=self._on_wb_slide
        )
        self.slider_temp.set(0)
        self.slider_temp.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))

    def _on_brightness_slide(self, val):
        delta = int(val)
        self.ev_step(delta)

    # --- Card 4: Background Card ---
    def _build_background_card(self, parent):
        card = CardFrame(parent, title="Background", icon="[BG]")
        card.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)

        # Top Pills Selector
        pills_row = tk.Frame(card, bg="#161B22")
        pills_row.pack(fill=tk.X, pady=(0, 6))

        bg_options = [
            ("off", "Pass-Through"),
            ("blur_light", "Blur"),
            ("green_screen", "Green Screen"),
            ("custom", "Select Image"),
            ("presets", "Presets")
        ]
        self.seg_bg = SegmentedControl(pills_row, bg_options, command=self._on_bg_pill_select, initial="off", bg="#161B22")
        self.seg_bg.pack(fill=tk.X)

        body = tk.Frame(card, bg="#161B22")
        body.pack(fill=tk.BOTH, expand=True, pady=2)

        # Left: Thumbnail Avatar Canvas
        self.bg_preview_canvas = tk.Canvas(body, width=110, height=75, bg="#0D1117", highlightthickness=1, highlightbackground="#30363D")
        self.bg_preview_canvas.pack(side=tk.LEFT, padx=(0, 10))
        self._draw_bg_preview("off")

        # Right: Workload Processing Options
        opt_box = tk.Frame(body, bg="#161B22")
        opt_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(opt_box, text="Processing Mode:", font=("Segoe UI", 8, "bold"), fg="#8B949E", bg="#161B22").pack(anchor="w", pady=(0, 2))

        r_pc = tk.Radiobutton(
            opt_box, text="GPU (Recommended)", variable=self.bg_workload_var, value="pc",
            font=("Segoe UI", 8), bg="#161B22", fg="#3FB950", selectcolor="#0D1117", activebackground="#161B22",
            command=self._on_bg_workload_change
        )
        r_pc.pack(anchor="w")

        r_mob = tk.Radiobutton(
            opt_box, text="Mobile Processing", variable=self.bg_workload_var, value="mobile",
            font=("Segoe UI", 8), bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22",
            command=self._on_bg_workload_change
        )
        r_mob.pack(anchor="w")

        # Hidden combobox & labels for full backward compatibility
        self.combo_bg_mode = ttk.Combobox(opt_box, values=["Off / None (Pass-Through)", "Light Bokeh Blur (Portrait)", "Heavy Privacy Blur", "Solid Green Screen (Chroma Key)", "Custom Image Background"])
        self.combo_bg_mode.set("Off / None (Pass-Through)")
        self.btn_browse_bg = ttk.Button(opt_box, text="Browse", command=self._browse_bg_image)
        self.lbl_bg_image_file = tk.Label(opt_box, text="", bg="#161B22")

    def _draw_bg_preview(self, mode):
        self.bg_preview_canvas.delete("all")
        if mode == "green_screen":
            self.bg_preview_canvas.create_rectangle(0, 0, 110, 75, fill="#00FF00", outline="")
            self.bg_preview_canvas.create_text(55, 38, text="GREEN SCREEN", font=("Segoe UI", 7, "bold"), fill="#000000")
        elif mode in ("blur_light", "blur_heavy"):
            self.bg_preview_canvas.create_rectangle(0, 0, 110, 75, fill="#1C2333", outline="")
            self.bg_preview_canvas.create_oval(35, 15, 75, 55, fill="#2E3B52", outline="")
            self.bg_preview_canvas.create_text(55, 38, text="PORTRAIT BLUR", font=("Segoe UI", 7, "bold"), fill="#58A6FF")
        elif mode == "custom" and self.bg_image_path:
            self.bg_preview_canvas.create_rectangle(0, 0, 110, 75, fill="#161B22", outline="")
            self.bg_preview_canvas.create_text(55, 38, text="CUSTOM IMAGE", font=("Segoe UI", 7, "bold"), fill="#58A6FF")
        else: # pass through
            # Draw checkerboard avatar
            for y in range(0, 75, 15):
                for x in range(0, 110, 15):
                    fill = "#161B22" if ((x//15 + y//15) % 2 == 0) else "#0D1117"
                    self.bg_preview_canvas.create_rectangle(x, y, x+15, y+15, fill=fill, outline="")
            # Silhouette avatar
            self.bg_preview_canvas.create_oval(45, 16, 65, 36, fill="#388BFD", outline="")
            self.bg_preview_canvas.create_arc(32, 38, 78, 80, start=0, extent=180, fill="#388BFD", outline="")

    def _on_bg_pill_select(self, mode):
        if mode == "off":
            self._set_bg_mode_direct("Off / None (Pass-Through)", "off")
            self._draw_bg_preview("off")
        elif mode == "blur_light":
            self._set_bg_mode_direct("Light Bokeh Blur (Portrait)", "blur_light")
            self._draw_bg_preview("blur_light")
        elif mode == "green_screen":
            self._set_bg_mode_direct("Solid Green Screen (Chroma Key)", "green_screen")
            self._draw_bg_preview("green_screen")
        elif mode == "custom":
            self._browse_bg_image()
            self._draw_bg_preview("custom")
        elif mode == "presets":
            self._show_presets_popup()

    def _show_presets_popup(self):
        menu = tk.Menu(self.root, tearoff=0, bg="#161B22", fg="#C9D1D9", activebackground="#1F6FEB", activeforeground="#FFFFFF")
        menu.add_command(label="Modern Office (1080p)", command=lambda: self._select_preset_item("modern_office.jpg", "Modern Office"))
        menu.add_command(label="Studio Bokeh (1080p)", command=lambda: self._select_preset_item("studio_bokeh.jpg", "Studio Bokeh"))
        menu.add_command(label="Minimalist Bookshelf", command=lambda: self._select_preset_item("minimalist_bookshelf.jpg", "Bookshelf"))
        menu.add_command(label="Cozy Coffee Shop", command=lambda: self._select_preset_item("cozy_coffee_shop.jpg", "Coffee Shop"))
        try:
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _select_preset_item(self, filename, name):
        self._load_preset_wallpaper(filename, name)
        self._draw_bg_preview("custom")

    # --- Card 5: More Controls Card ---
    def _build_more_controls_card(self, parent):
        card = CardFrame(parent, title="More Controls", icon="[Tools]")
        card.grid(row=1, column=1, sticky="nsew", padx=4, pady=4)

        grid = tk.Frame(card, bg="#161B22")
        grid.pack(fill=tk.BOTH, expand=True)

        for c in range(3):
            grid.columnconfigure(c, weight=1)

        # 2x3 modern button matrix
        btn_obs = ttk.Button(grid, text="OBS Setup", style="Dark.TButton", command=self._show_obs_guide_modal)
        btn_obs.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")

        btn_deps = ttk.Button(grid, text="Dependencies", style="Dark.TButton", command=self._show_deps_modal)
        btn_deps.grid(row=0, column=1, padx=3, pady=3, sticky="nsew")

        btn_oem = ttk.Button(grid, text="OEM Fix", style="Dark.TButton", command=self._show_oem_fix_modal)
        btn_oem.grid(row=0, column=2, padx=3, pady=3, sticky="nsew")

        btn_set = ttk.Button(grid, text="Settings", style="Dark.TButton", command=self._show_settings_modal)
        btn_set.grid(row=1, column=0, padx=3, pady=3, sticky="nsew")

        btn_diag = ttk.Button(grid, text="Diagnostics", style="Dark.TButton", command=self._show_diagnostics_modal)
        btn_diag.grid(row=1, column=1, padx=3, pady=3, sticky="nsew")

        btn_abt = ttk.Button(grid, text="About & License", style="Dark.TButton", command=self._show_about_modal)
        btn_abt.grid(row=1, column=2, padx=3, pady=3, sticky="nsew")

    # --- Card 6: Event Log Card ---
    def _build_event_log_card(self, parent):
        def _header_right(h_frame):
            btn_clear = tk.Button(h_frame, text="Clear", font=("Segoe UI", 8, "bold"), bg="#21262D", fg="#8B949E", activebackground="#30363D", activeforeground="#FFFFFF", bd=0, padx=6, pady=2, cursor="hand2", command=lambda: self.log_text.delete("1.0", tk.END))
            btn_clear.pack(side=tk.RIGHT)

        card = CardFrame(parent, title="Event Log", icon="[Log]", header_right=_header_right)
        card.grid(row=1, column=2, sticky="nsew", padx=4, pady=4)

        log_inner = tk.Frame(card, bg="#0D1117", highlightbackground="#21262D", highlightthickness=1)
        log_inner.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_inner, height=5, bg="#0D1117", fg="#8B949E", insertbackground="#C9D1D9", font=("Consolas", 8), relief=tk.FLAT)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4, pady=4)

        scrollbar_log = ttk.Scrollbar(log_inner, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar_log.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar_log.set)

        self.log("Otter Virtual Camera Controller initialized.")
        self.log("Ready. Connect device via USB or Wi-Fi, then click 'Connect & Start'.")

    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)

    def _poll_ui_queue(self):
        try:
            while True:
                cb = self._ui_queue.get_nowait()
                cb()
        except queue.Empty:
            pass
        except Exception:
            pass
        try:
            self.root.after(40, self._poll_ui_queue)
        except Exception:
            pass

    def _post_ui(self, cb):
        self._ui_queue.put(cb)

    # --- Live Preview Callback ---
    def _on_live_frame(self, frame):
        now = time.time()
        if now - self._last_preview_time < 0.065:
            return
        self._last_preview_time = now

        try:
            h, w = frame.shape[:2]
            scale = min(150 / w, 110 / h)
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            small = cv2.resize(frame, (nw, nh), interpolation=cv2.INTER_NEAREST)
            rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
            success, ppm_buf = cv2.imencode('.ppm', rgb)
            if success:
                ppm_data = ppm_buf.tobytes()
                self._post_ui(lambda: self._update_preview_canvas(ppm_data, nw, nh))
        except Exception:
            pass

    def _update_preview_canvas(self, ppm_data, w, h):
        try:
            photo = tk.PhotoImage(data=ppm_data)
            self._preview_photo = photo
            self.preview_canvas.delete("all")
            self.preview_canvas.create_rectangle(0, 0, 150, 110, fill="#0D1117", outline="")
            self.preview_canvas.create_image(75, 55, image=photo, anchor="center")
            if self.is_connected and "Connecting" in self.status_badge.cget("text"):
                cam_name = self.entry_cam_name.get().strip() or "Otter Camera"
                self.status_badge.configure(text=f"● Active: {cam_name}", fg="#3FB950")
        except Exception:
            pass

    # --- Connection & Streaming Handlers ---
    def _toggle_conn_mode(self):
        mode = self.conn_mode.get()
        if mode == "auto":
            self.entry_ip.configure(state=tk.NORMAL)
            # If USB device is attached, hint 127.0.0.1, else suggest LAN fallback
            serial = self.adb_tunnel.usb_serial() if self.adb_tunnel and self.adb_tunnel.is_available() else None
            if serial:
                self.entry_ip.delete(0, tk.END)
                self.entry_ip.insert(0, "127.0.0.1")
            elif not self.entry_ip.get().strip() or self.entry_ip.get().strip() in ("127.0.0.1", "192.168.42.129"):
                lan_adapters = network_discovery.detect_lan_adapters()
                suggested_ip = "192.168.1.50"
                if lan_adapters and lan_adapters[0].get("ips"):
                    parts = lan_adapters[0]["ips"][0].split(".")
                    if len(parts) == 4:
                        suggested_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.50"
                self.entry_ip.delete(0, tk.END)
                self.entry_ip.insert(0, suggested_ip)
            self.log("Auto mode: Probes USB (ADB tunnel) first; seamlessly falls back to Wi-Fi.")
        elif mode == "tether":
            self.entry_ip.configure(state=tk.NORMAL)
            self.entry_ip.delete(0, tk.END)
            tether_ad = network_discovery.detect_tethering_adapter()
            if tether_ad and tether_ad.get("gateways"):
                self.entry_ip.insert(0, tether_ad["gateways"][0])
            else:
                self.entry_ip.insert(0, "192.168.42.129")
            self.log("USB Tethering mode: Plug USB cable, enable 'USB Tethering' on phone, click Connect.")
        elif mode == "wifi":
            self.entry_ip.configure(state=tk.NORMAL)
            if self.entry_ip.get().strip() in ("127.0.0.1", "192.168.42.129") or not self.entry_ip.get().strip():
                lan_adapters = network_discovery.detect_lan_adapters()
                suggested_ip = "192.168.1.50"
                if lan_adapters and lan_adapters[0].get("ips"):
                    parts = lan_adapters[0]["ips"][0].split(".")
                    if len(parts) == 4:
                        suggested_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.50"
                self.entry_ip.delete(0, tk.END)
                self.entry_ip.insert(0, suggested_ip)
            self.log("Wi-Fi mode: Ensure phone and PC are on the same local network.")
        else: # usb
            self.entry_ip.configure(state=tk.NORMAL)
            self.entry_ip.delete(0, tk.END)
            self.entry_ip.insert(0, "127.0.0.1")
            self.entry_ip.configure(state=tk.DISABLED)
            self.log("USB ADB mode: Requires USB debugging enabled on phone.")

    def _gui_auto_detect_ip(self):
        mode = self.conn_mode.get()
        self.btn_auto_detect.configure(state=tk.DISABLED)
        try:
            stream_port = int(self.entry_stream_port.get().strip())
        except ValueError:
            stream_port = 8089
        try:
            ctrl_port = int(self.entry_ctrl_port.get().strip())
        except ValueError:
            ctrl_port = 8090

        self.log(f"Auto-Detect IP started for [{mode.upper()}] connection mode...")

        def detect_worker():
            try:
                if mode == "usb":
                    # Mode 1: USB ADB Tunnel
                    tunnel = ADBTunnel(stream_port=stream_port, control_port=ctrl_port)
                    if not tunnel.is_available():
                        self._post_ui(lambda: self._on_auto_detect_error(
                            "ADB Not Detected",
                            "ADB executable was not found on your PC.\n\nPlease install Android platform-tools or click 'Diagnostics' -> 'Download Platform Tools'."
                        ))
                        return
                    serial = tunnel.usb_serial()
                    if not serial:
                        self._post_ui(lambda: self._on_auto_detect_error(
                            "No USB Device Detected",
                            "No authorized Android device was found via ADB.\n\nPlease check:\n1. Connect phone via USB data cable.\n2. Turn ON 'USB Debugging' in Developer Options.\n3. Tap 'Allow USB Debugging' on phone."
                        ))
                        return
                    # Check for port conflicts on 127.0.0.1
                    dyn_sp, dyn_cp = tunnel.resolve_forward_ports(serial)
                    is_dyn = (dyn_sp != stream_port or dyn_cp != ctrl_port)
                    self._post_ui(lambda: self._on_adb_port_resolved(serial, dyn_sp, dyn_cp, is_dyn))

                elif mode == "tether":
                    # Mode 2: USB Tethering
                    tether_adapter = network_discovery.detect_tethering_adapter()
                    if not tether_adapter:
                        # Probe standard tether gateway IPs in case OS interface description is generic
                        active_tip = None
                        for tip in network_discovery.COMMON_TETHER_IPS:
                            alive, _, _ = network_discovery.check_camera_host(tip, stream_port, timeout=0.25)
                            if alive:
                                active_tip = tip
                                break
                        if active_tip:
                            self._post_ui(lambda: self._on_tether_detected(active_tip, "Unknown", "USB Tethering Gateway"))
                            return
                        self._post_ui(lambda: self._on_auto_detect_error(
                            "USB Tethering Not Found",
                            "No active USB tethering network interface was detected on this PC.\n\nPlease verify:\n1. Connect your phone via USB cable.\n2. In Android Settings -> Network -> Hotspot & Tethering, turn ON 'USB Tethering'."
                        ))
                        return
                    host_ip = tether_adapter["ips"][0] if tether_adapter.get("ips") else "192.168.42.x"
                    adapter_name = tether_adapter.get("name", "USB Tethering Interface")
                    gateway = tether_adapter.get("gateways", [None])[0] or "192.168.42.129"
                    target_ip = gateway
                    # Probe if phone stream is already active on gateway or COMMON_TETHER_IPS
                    for tip in [gateway] + network_discovery.COMMON_TETHER_IPS:
                        alive, _, _ = network_discovery.check_camera_host(tip, stream_port, timeout=0.25)
                        if alive:
                            target_ip = tip
                            break
                    self._post_ui(lambda: self._on_tether_detected(target_ip, host_ip, adapter_name))

                elif mode == "wifi":
                    # Mode 3: Wi-Fi LAN
                    lan_adapters = network_discovery.detect_lan_adapters()
                    if not lan_adapters:
                        self._post_ui(lambda: self._on_auto_detect_error(
                            "No Wi-Fi / LAN Network",
                            "No active physical Wi-Fi or local Ethernet network connection was found on this PC.\n\nPlease connect your PC to a Wi-Fi or wired network."
                        ))
                        return
                    subnets = network_discovery.get_local_ip_subnets()
                    primary_ip = lan_adapters[0]["ips"][0] if lan_adapters[0].get("ips") else "192.168.1.x"
                    found = network_discovery.scan_network_for_cameras(port=stream_port, subnets=subnets)
                    if found:
                        self._post_ui(lambda: self._on_wifi_camera_detected(found[0], primary_ip, subnets))
                    else:
                        self._post_ui(lambda: self._on_wifi_no_camera(primary_ip, subnets, stream_port))

                else:
                    # Mode 4: Auto Mode (USB ADB -> USB Tethering -> Wi-Fi LAN)
                    tunnel = ADBTunnel(stream_port=stream_port, control_port=ctrl_port)
                    if tunnel.is_available() and tunnel.usb_serial():
                        serial = tunnel.usb_serial()
                        dyn_sp, dyn_cp = tunnel.resolve_forward_ports(serial)
                        self._post_ui(lambda: self._on_auto_mode_detected("usb", "127.0.0.1", f"Found USB debugging device ({serial})"))
                        return

                    tether_adapter = network_discovery.detect_tethering_adapter()
                    if tether_adapter:
                        gateway = tether_adapter.get("gateways", [None])[0] or "192.168.42.129"
                        self._post_ui(lambda: self._on_auto_mode_detected("tether", gateway, f"Found USB Tethering adapter ({tether_adapter.get('name', 'Tether')})"))
                        return

                    subnets = network_discovery.get_local_ip_subnets()
                    found = network_discovery.scan_network_for_cameras(port=stream_port, subnets=subnets)
                    if found:
                        self._post_ui(lambda: self._on_auto_mode_detected("wifi", found[0], f"Found Wi-Fi camera at {found[0]}"))
                        return

                    self._post_ui(lambda: self._on_auto_detect_error(
                        "Auto-Detection Failed",
                        "No camera detected across USB ADB, USB Tethering, or Wi-Fi LAN.\n\nPlease check:\n- USB Cable & Tethering/Debugging, OR\n- Connect both devices to the same Wi-Fi and tap 'Start' on the phone app."
                    ))
            except Exception as e:
                self._post_ui(lambda: self._on_auto_detect_error("Auto Detect Error", f"An error occurred while scanning: {e}"))

        threading.Thread(target=detect_worker, daemon=True).start()

    def _on_auto_detect_error(self, title: str, message: str):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        self.log(f"Auto-Detect: {title} - {message.splitlines()[0]}")
        messagebox.showerror(title, message)

    def _on_adb_port_resolved(self, serial: str, stream_p: int, ctrl_p: int, is_dynamic: bool):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        self.entry_ip.configure(state=tk.NORMAL)
        self.entry_ip.delete(0, tk.END)
        self.entry_ip.insert(0, "127.0.0.1")
        self.entry_ip.configure(state=tk.DISABLED)

        if is_dynamic:
            self.entry_stream_port.delete(0, tk.END)
            self.entry_stream_port.insert(0, str(stream_p))
            self.entry_ctrl_port.delete(0, tk.END)
            self.entry_ctrl_port.insert(0, str(ctrl_p))
            self.log(f"Auto-Detect (ADB Tunnel): Device {serial}. Port conflict detected; dynamically assigned Stream Port {stream_p}, Control Port {ctrl_p}.")
            messagebox.showinfo("ADB Device Detected (Dynamic Ports)", f"Detected USB device: {serial}\nHost IP: 127.0.0.1\n\nStandard ports were busy; dynamically assigned:\nStream Port: {stream_p}\nControl Port: {ctrl_p}")
        else:
            self.log(f"Auto-Detect (ADB Tunnel): Device {serial} verified on 127.0.0.1:{stream_p}.")
            messagebox.showinfo("ADB Device Detected", f"Detected USB device: {serial}\nHost IP: 127.0.0.1\nStream Port: {stream_p}\nControl Port: {ctrl_p}")

    def _on_tether_detected(self, target_ip: str, host_ip: str, adapter_name: str):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        self.entry_ip.configure(state=tk.NORMAL)
        self.entry_ip.delete(0, tk.END)
        self.entry_ip.insert(0, target_ip)
        self.log(f"Auto-Detect (USB Tethering): Adapter '{adapter_name}'. Host IP: {host_ip} -> Phone Target IP: {target_ip}.")
        messagebox.showinfo("USB Tethering Detected", f"USB Tethering Network Interface:\n{adapter_name}\n\nPC Host IP: {host_ip}\nPhone / Gateway IP: {target_ip}\n\nIP address set to: {target_ip}")

    def _on_wifi_camera_detected(self, camera_ip: str, host_ip: str, subnets: list):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        self.entry_ip.configure(state=tk.NORMAL)
        self.entry_ip.delete(0, tk.END)
        self.entry_ip.insert(0, camera_ip)
        self.log(f"Auto-Detect (Wi-Fi): Active camera discovered at {camera_ip} (PC Host IP: {host_ip}).")
        messagebox.showinfo("Wi-Fi Camera Discovered", f"Active Otter Camera Discovered!\n\nCamera IP: {camera_ip}\nPC Local IP: {host_ip}\n\nIP address updated to: {camera_ip}")

    def _on_wifi_no_camera(self, host_ip: str, subnets: list, port: int):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        subnet_str = ", ".join(f"{s}.0/24" for s in subnets)
        self.log(f"Auto-Detect (Wi-Fi): No active camera found on subnet(s) {subnet_str}. PC Host IP: {host_ip}.")
        messagebox.showwarning(
            "No Camera Detected on Wi-Fi",
            f"No responsive Otter camera was found on port {port}.\n\n"
            f"PC Local IP: {host_ip}\n"
            f"Scanned Subnets: {subnet_str}\n\n"
            "Please ensure:\n"
            "1. Phone and PC are on the same Wi-Fi router.\n"
            "2. Open Otter on your phone and tap 'Start' to begin streaming.\n"
            "3. If your router has AP Isolation enabled, use USB Tethering instead."
        )

    def _on_auto_mode_detected(self, resolved_mode: str, ip: str, desc: str):
        self.btn_auto_detect.configure(state=tk.NORMAL)
        self.conn_mode.set(resolved_mode)
        self.seg_mode.select(resolved_mode, notify=False)
        self.entry_ip.configure(state=tk.NORMAL)
        self.entry_ip.delete(0, tk.END)
        self.entry_ip.insert(0, ip)
        if resolved_mode == "usb":
            self.entry_ip.configure(state=tk.DISABLED)
        self.log(f"Auto-Detect resolved to [{resolved_mode.upper()}]: {desc} -> IP: {ip}.")
        messagebox.showinfo("Connection Detected", f"Auto-detected connection:\nMode: {resolved_mode.upper()}\n{desc}\n\nIP set to: {ip}")

    def start_stream(self):
        mode = self.conn_mode.get()
        host = "127.0.0.1"
        resolved_mode = mode

        try:
            stream_port = int(self.entry_stream_port.get().strip())
        except ValueError:
            stream_port = 8089

        try:
            ctrl_port = int(self.entry_ctrl_port.get().strip())
        except ValueError:
            ctrl_port = 8090

        cam_name = self.entry_cam_name.get().strip() or "Otter Camera"
        reforward_cb = None

        if mode == "auto":
            self.log("Auto Mode: Checking for connected USB device via ADB...")
            self.adb_tunnel = ADBTunnel(stream_port=stream_port, control_port=ctrl_port)
            serial = self.adb_tunnel.usb_serial() if self.adb_tunnel.is_available() else None
            if serial and self.adb_tunnel.setup_forward(serial):
                host = "127.0.0.1"
                resolved_mode = "usb"
                reforward_cb = lambda: self.adb_tunnel.setup_forward(serial)
                self.log(f"Auto Mode: ADB USB tunnel active on ports {stream_port} / {ctrl_port}.")
            else:
                tether_ad = network_discovery.detect_tethering_adapter()
                if tether_ad and tether_ad.get("gateways"):
                    host = tether_ad["gateways"][0]
                    resolved_mode = "tether"
                    self.entry_ip.delete(0, tk.END)
                    self.entry_ip.insert(0, host)
                    self.log(f"Auto Mode: USB Tethering active on {host}:{stream_port}.")
                else:
                    host = self.entry_ip.get().strip()
                    if not host or host in ("127.0.0.1", "192.168.42.129"):
                        subnets = network_discovery.get_local_ip_subnets()
                        found = network_discovery.scan_network_for_cameras(port=stream_port, subnets=subnets)
                        if found:
                            host = found[0]
                            self.entry_ip.delete(0, tk.END)
                            self.entry_ip.insert(0, host)
                            resolved_mode = "wifi"
                            self.log(f"Auto Mode: Discovered Wi-Fi camera at {host}.")
                        else:
                            self.log("Auto Mode: No camera found via USB ADB, Tethering, or Wi-Fi.")
                            messagebox.showerror("No Camera Detected", "Could not detect a connected Otter camera.\n\nPlease connect phone via USB (with Debugging or Tethering ON) or enter the phone's Wi-Fi IP address.")
                            return
                    else:
                        resolved_mode = "wifi"
                        self.log(f"Auto Mode: Using Wi-Fi target {host}:{stream_port}...")
        elif mode == "usb":
            self.log(f"Setting up USB tunnel for Stream Port {stream_port} & Control Port {ctrl_port}...")
            self.adb_tunnel = ADBTunnel(stream_port=stream_port, control_port=ctrl_port)
            if not self.adb_tunnel.is_available():
                self.log("Notice: ADB executable not found on PC.")
                if messagebox.askyesno("Download Minimal ADB", "ADB is needed for USB mode, but neither Android Studio nor ADB is detected.\n\nWould you like Otter to download Google's official minimal platform-tools (~15MB)?"):
                    self._gui_download_adb()
                    return
                else:
                    return

            serial = self.adb_tunnel.usb_serial()
            if not serial:
                self.log("Error: No USB debugging device detected.")
                messagebox.showerror("Device Not Found", "No Android device detected over USB.\n\nPlease ensure:\n1. Phone is plugged in via USB data cable.\n2. USB Debugging is turned ON in Developer Options.\n3. Tap 'Allow USB Debugging' if prompted on phone.")
                return

            if not self.adb_tunnel.setup_forward(serial):
                self.log(f"Error: ADB port forwarding failed on device {serial}.")
                messagebox.showerror("Port Forward Failed", f"ADB port forwarding failed on device {serial}.\nEnsure USB debugging is authorized on your phone.")
                return

            self.log(f"ADB USB forwarding established on ports {stream_port} / {ctrl_port}.")
            reforward_cb = lambda: self.adb_tunnel.setup_forward(serial)
            host = "127.0.0.1"
            resolved_mode = "usb"
        elif mode == "tether":
            current_ip = self.entry_ip.get().strip()
            tether_ad = network_discovery.detect_tethering_adapter()
            if not current_ip or current_ip in ("127.0.0.1", "192.168.42.129"):
                if tether_ad and tether_ad.get("gateways"):
                    host = tether_ad["gateways"][0]
                    self.entry_ip.delete(0, tk.END)
                    self.entry_ip.insert(0, host)
                elif not tether_ad:
                    self.log("Error: No USB Tethering network interface detected on PC.")
                    messagebox.showerror("USB Tethering Not Found", "No active USB tethering connection was detected.\n\nPlease ensure:\n1. Phone is plugged in via USB cable.\n2. In Android Settings -> Hotspot & Tethering, turn ON 'USB Tethering'.")
                    return
                else:
                    host = current_ip or "192.168.42.129"
            else:
                host = current_ip
            self.log(f"Direct USB Tethering connection to {host}:{stream_port} (No ADB required).")
            resolved_mode = "tether"
        else: # wifi
            host = self.entry_ip.get().strip()
            if not host:
                messagebox.showerror("Error", "Please enter a valid phone IP address.")
                return
            self.log(f"Wi-Fi connection to {host}:{stream_port}.")
            resolved_mode = "wifi"

        self.active_host = host
        self.active_mode = resolved_mode

        enable_vcam = self.vcam_var.get()
        self.log(f"Initializing receiver '{cam_name}' (Mode: {resolved_mode.upper()}, Virtual Cam: {'Enabled' if enable_vcam else 'Disabled'})...")

        res_str = self.res_combo.get()
        width, height = 1280, 720
        if "1920" in res_str:
            width, height = 1920, 1080
        elif "3840" in res_str:
            width, height = 3840, 2160
        elif "640x480" in res_str:
            width, height = 640, 480
        elif "640x360" in res_str:
            width, height = 640, 360

        self.receiver = CamBridgeReceiver(host=host, stream_port=stream_port, control_port=ctrl_port, width=width, height=height, camera_name=cam_name)
        if reforward_cb:
            self.receiver.reforward_cb = reforward_cb
        self.receiver.on_frame_cb = self._on_live_frame
        self.receiver.set_bg_workload(self.bg_workload_var.get())
        self.receiver.set_bg_mode(self.bg_mode_var.get())
        if self.bg_image_path:
            self.receiver.set_bg_image(self.bg_image_path)

        self.controller = CamBridgeControl(host=host, port=ctrl_port)
        try:
            conn_report_mode = "adb" if resolved_mode == "usb" else ("usb_tether" if resolved_mode == "tether" else "wifi")
            self.controller.set_connection_mode(conn_report_mode)
            start_res = self.controller.start_stream()
            self.log(f"Synced Start Stream to mobile app: {start_res}")
            time.sleep(0.3)
        except Exception as ex:
            self.log(f"Notice: Could not sync start to phone control port: {ex}")

        self.receiver_thread = threading.Thread(target=self._run_receiver, args=(enable_vcam,), daemon=True)
        self.receiver_thread.start()

        self.is_connected = True
        self.btn_connect.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        self.status_badge.configure(text="● Connecting...", fg="#DBAB09")
        self.log(f"Connecting to receiver '{cam_name}' on {host}:{stream_port} ({resolved_mode.upper()})...")

    def _run_receiver(self, enable_vcam):
        try:
            self.receiver.start_receiver(enable_virtualcam=enable_vcam, show_preview=False)
        except Exception as e:
            self.log(f"Receiver error: {e}")
        finally:
            self._post_ui(self._on_receiver_stopped)

    def _on_receiver_stopped(self):
        self.is_connected = False
        self.btn_connect.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self.status_badge.configure(text="● Disconnected", fg="#DA3633")
        self.log("Stream receiver stopped.")
        self._draw_idle_preview()

    def stop_stream(self):
        if self.controller:
            try:
                stop_res = self.controller.stop_stream()
                self.log(f"Synced Stop Stream to mobile app: {stop_res}")
            except Exception:
                pass
        if self.receiver:
            self.receiver.stop_receiver()
        if self.adb_tunnel:
            self.adb_tunnel.remove_forward()
        self._on_receiver_stopped()

    def _get_active_host(self):
        if hasattr(self, "active_host") and self.active_host:
            return self.active_host
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

    # --- Camera Actions ---
    def flip_camera(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.switch_camera()
        self.current_lens = "FRONT" if self.current_lens == "BACK" else "BACK"
        if hasattr(self, "seg_lens"):
            self.seg_lens.select(self.current_lens, notify=False)
        self.log(f"Flip Camera ({self.current_lens}): {res}")

    def toggle_mirror(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_mirror()
        self.is_mirrored = not self.is_mirrored
        self.btn_mirror.configure(text=f"Mirror: {'ON' if self.is_mirrored else 'OFF'}")
        self.log(f"Toggle Mirror: {res}")

    def rotate_camera(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.rotate_camera()
        angle = res.get("rotationAngle", 0)
        self.btn_rotate.configure(text=f"Rot: {angle}°")
        if self.receiver:
            self.receiver.set_rotation(angle)
        self.log(f"Rotate Camera to {angle}°: {res}")

    def toggle_torch(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_torch()
        self.torch_state = res.get("torchState", 0)
        is_on = self.torch_state > 0
        self.lbl_torch_val.configure(text="On" if is_on else "Off", fg="#3FB950" if is_on else "#8B949E")
        self.sw_torch.set_state(is_on)
        self.log(f"Toggle Torch: {res}")

    def toggle_glow(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_glow()
        glow_name = res.get("glowName", "Off")
        is_on = glow_name not in ("OFF", "Off", "")
        self.lbl_glow_val.configure(text=glow_name, fg="#58A6FF" if is_on else "#8B949E")
        self.sw_glow.set_state(is_on)
        self.log(f"Toggle Screen Glow: {res}")

    def toggle_keep_screen(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.toggle_keep_screen_on()
        is_on = res.get("isKeepScreenOn", True)
        self.keep_screen_on = is_on
        self.lbl_keep_screen_val.configure(text="On" if is_on else "Auto", fg="#3FB950" if is_on else "#8B949E")
        self.sw_keep_screen.set_state(is_on)
        self.log(f"Toggled phone screen wake lock: {'Keep ON' if is_on else 'Auto Sleep'}: {res}")

    def capture_ultra_photo(self):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.capture_still()
        self.log(f"Capture Ultra Photo (Full Res): {res}")

    def on_res_change(self, event=None):
        res_str = self.res_combo.get()
        w, h = 1280, 720
        if "3840" in res_str:
            w, h = 3840, 2160
        elif "1920" in res_str:
            w, h = 1920, 1080
        elif "1280" in res_str:
            w, h = 1280, 720
        elif "640x480" in res_str:
            w, h = 640, 480
        elif "640x360" in res_str:
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
        self.log(f"Set FPS to {fps}: {res}")

    # Zoom controls
    def zoom_in(self):
        self.current_zoom = min(8.0, self.current_zoom + 0.2)
        self.slider_zoom.set(self.current_zoom)
        self.lbl_zoom.configure(text=f"{self.current_zoom:.1f}x")
        self._send_zoom(self.current_zoom)

    def zoom_out(self):
        self.current_zoom = max(1.0, self.current_zoom - 0.2)
        self.slider_zoom.set(self.current_zoom)
        self.lbl_zoom.configure(text=f"{self.current_zoom:.1f}x")
        self._send_zoom(self.current_zoom)

    def _on_zoom_slide(self, val):
        z = float(val)
        self.current_zoom = z
        self.lbl_zoom.configure(text=f"{z:.1f}x")
        self._debounce("zoom", 100, lambda: self._send_zoom(z))

    def _send_zoom(self, z):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_zoom(z)
        self.log(f"Zoom set to {z:.1f}x: {res}")

    # Pro Controls: ISO
    def _toggle_iso_auto(self):
        is_auto = self.iso_auto_var.get()
        self.sw_iso.set_state(is_auto)
        if is_auto:
            self.lbl_iso_val.configure(text="Auto", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_iso(0)
            self.log(f"Set ISO to Auto: {res}")
        else:
            self.lbl_iso_val.configure(text=f"ISO {self.ISO_VALUES[0]}", fg="#58A6FF")
            self._send_iso(self.ISO_VALUES[0])

    def _on_iso_slide(self, val):
        if self.iso_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.ISO_VALUES):
            iso = self.ISO_VALUES[idx]
            self.lbl_iso_val.configure(text=f"ISO {iso}", fg="#58A6FF")
            self._debounce("iso", 100, lambda: self._send_iso(iso))

    def _send_iso(self, iso):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_iso(iso)
        self.log(f"Set ISO to {iso}: {res}")

    # Pro Controls: Shutter
    def _toggle_shutter_auto(self):
        is_auto = self.shutter_auto_var.get()
        self.sw_shutter.set_state(is_auto)
        if is_auto:
            self.lbl_shutter_val.configure(text="Auto", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_shutter(0)
            self.log(f"Set Shutter to Auto: {res}")
        else:
            ns, label = self.SHUTTER_STEPS[5] # 1/60s
            self.lbl_shutter_val.configure(text=label, fg="#58A6FF")
            self._send_shutter(ns, label)

    def _on_shutter_slide(self, val):
        if self.shutter_auto_var.get():
            return
        idx = int(round(float(val)))
        if 0 <= idx < len(self.SHUTTER_STEPS):
            ns, label = self.SHUTTER_STEPS[idx]
            self.lbl_shutter_val.configure(text=label, fg="#58A6FF")
            self._debounce("shutter", 100, lambda: self._send_shutter(ns, label))

    def _send_shutter(self, shutter_ns, label):
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_shutter(shutter_ns)
        self.log(f"Set Shutter to {label}: {res}")

    # Pro Controls: White Balance
    def _toggle_wb_auto(self):
        is_auto = self.wb_auto_var.get()
        self.sw_wb.set_state(is_auto)
        if is_auto:
            self.lbl_wb_val.configure(text="Auto (AWB)", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_awb(0)
            self.log(f"Set WB to Auto: {res}")
        else:
            mode, label = self.WB_MODES[0]
            self.lbl_wb_val.configure(text=label, fg="#58A6FF")
            self._send_wb(mode, label)

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

    # Pro Controls: Color FX
    def _toggle_fx_auto(self):
        is_auto = self.fx_auto_var.get()
        self.sw_fx.set_state(is_auto)
        if is_auto:
            self.lbl_fx_val.configure(text="Normal Color", fg="#8B949E")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_effect(0)
            self.log(f"Set Color FX to Normal: {res}")
        else:
            fx_mode, label = self.FX_MODES[0]
            self.lbl_fx_val.configure(text=label, fg="#58A6FF")
            self._send_fx(fx_mode, label)

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

    def cycle_ev(self):
        self.ev_step(1)

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
            time.sleep(2)
            if self.is_connected and self.controller:
                try:
                    res = self.controller.get_status()
                    if res.get("status") == "ok":
                        self._post_ui(lambda r=res: self._apply_synced_status(r))
                except Exception:
                    pass

    def _apply_synced_status(self, r: dict):
        try:
            # Sync streaming state from phone
            if "streaming" in r:
                is_phone_streaming = bool(r.get("streaming", False))
                if self.is_connected and not is_phone_streaming:
                    self.log("Mobile app stopped streaming. Syncing desktop client state...")
                    self.stop_stream()
                    return

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
            self.lbl_ev.configure(text=f"{ev:+.1f}")

            # Zoom
            zoom = r.get("zoom", self.current_zoom)
            self.current_zoom = zoom
            self.lbl_zoom.configure(text=f"{zoom:.1f}x")
            self.slider_zoom.set(zoom)

            # Lens & Mirror & Rotation
            lens = r.get("lens", "BACK")
            self.current_lens = lens
            self.seg_lens.select(lens)

            mirrored = r.get("mirrored", False)
            self.is_mirrored = mirrored
            self.btn_mirror.configure(text=f"Mirror: {'ON' if mirrored else 'OFF'}")

            glow = r.get("glowName", "OFF")
            is_glow = glow not in ("OFF", "Off", "")
            self.lbl_glow_val.configure(text=glow, fg="#58A6FF" if is_glow else "#8B949E")
            self.sw_glow.set_state(is_glow)

            if "isKeepScreenOn" in r:
                is_keep = r.get("isKeepScreenOn", True)
                self.keep_screen_on = is_keep
                self.lbl_keep_screen_val.configure(text="On" if is_keep else "Auto", fg="#3FB950" if is_keep else "#8B949E")
                self.sw_keep_screen.set_state(is_keep)

            angle = r.get("rotationAngle")
            if angle is not None:
                self.btn_rotate.configure(text=f"Rot: {angle}°")
                if self.receiver and self.receiver.rotation_angle != angle:
                    self.receiver.set_rotation(angle)

            # ISO sync
            iso_val = r.get("iso", 0)
            if iso_val == 0:
                self.iso_auto_var.set(True)
                self.sw_iso.set_state(True)
                self.lbl_iso_val.configure(text="Auto", fg="#8B949E")
            else:
                self.iso_auto_var.set(False)
                self.sw_iso.set_state(False)
                closest_idx = min(range(len(self.ISO_VALUES)), key=lambda i: abs(self.ISO_VALUES[i] - iso_val))
                self.lbl_iso_val.configure(text=f"ISO {self.ISO_VALUES[closest_idx]}", fg="#58A6FF")

            # Shutter sync
            shutter_val = r.get("shutter", 0)
            if shutter_val == 0:
                self.shutter_auto_var.set(True)
                self.sw_shutter.set_state(True)
                self.lbl_shutter_val.configure(text="Auto", fg="#8B949E")
            else:
                self.shutter_auto_var.set(False)
                self.sw_shutter.set_state(False)
                closest_idx = min(range(len(self.SHUTTER_STEPS)), key=lambda i: abs(self.SHUTTER_STEPS[i][0] - shutter_val))
                self.lbl_shutter_val.configure(text=self.SHUTTER_STEPS[closest_idx][1], fg="#58A6FF")

            # AWB sync
            awb_str = r.get("awb", "Auto")
            if awb_str == "Auto":
                self.wb_auto_var.set(True)
                self.sw_wb.set_state(True)
                self.lbl_wb_val.configure(text="Auto (AWB)", fg="#8B949E")
            else:
                self.wb_auto_var.set(False)
                self.sw_wb.set_state(False)
                for idx, (m, lbl) in enumerate(self.WB_MODES):
                    if awb_str.lower() in lbl.lower():
                        self.lbl_wb_val.configure(text=lbl, fg="#58A6FF")
                        break

            # Effect sync
            effect_str = r.get("effect", "Color")
            if effect_str in ("Color", "Off", "Normal"):
                self.fx_auto_var.set(True)
                self.sw_fx.set_state(True)
                self.lbl_fx_val.configure(text="Normal Color", fg="#8B949E")
            else:
                self.fx_auto_var.set(False)
                self.sw_fx.set_state(False)
                for idx, (m, lbl) in enumerate(self.FX_MODES):
                    if effect_str.lower() in lbl.lower():
                        self.lbl_fx_val.configure(text=lbl, fg="#58A6FF")
                        break
        except Exception:
            pass

    # --- Virtual Background Handlers ---
    def _set_bg_mode_direct(self, combo_label, mode_code):
        self.bg_mode_var.set(mode_code)
        if self.receiver:
            self.receiver.set_bg_mode(mode_code)
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_background_mode(mode_code, self.bg_workload_var.get())
        self.log(f"Virtual Background set to '{combo_label}' ({self.bg_workload_var.get().upper()} workload): {res}")

    def _browse_bg_image(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"), ("All files", "*.*")]
        selected = filedialog.askopenfilename(title="Select Virtual Background Image", filetypes=filetypes)
        if selected and os.path.isfile(selected):
            self.bg_image_path = selected
            self.bg_mode_var.set("custom_image")
            if self.receiver:
                self.receiver.set_bg_image(selected)
                self.receiver.set_bg_mode("custom_image")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_background_mode("custom_image", self.bg_workload_var.get())
            self.log(f"Custom Background loaded: {os.path.basename(selected)}: {res}")
            self._draw_bg_preview("custom")

    def _load_preset_wallpaper(self, filename, name):
        wp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "wallpapers")
        preset_path = os.path.join(wp_dir, filename)
        if os.path.isfile(preset_path):
            self.bg_image_path = preset_path
            self.bg_mode_var.set("custom_image")
            if self.receiver:
                self.receiver.set_bg_image(preset_path)
                self.receiver.set_bg_mode("custom_image")
            if not self.controller:
                self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
            res = self.controller.set_background_mode("custom_image", self.bg_workload_var.get())
            self.log(f"Loaded Preset Wallpaper: {name}: {res}")
            self._draw_bg_preview("custom")
        else:
            self.log(f"Preset wallpaper not found: {filename}")

    def _on_bg_workload_change(self):
        workload = self.bg_workload_var.get()
        if self.receiver:
            self.receiver.set_bg_workload(workload)
        if not self.controller:
            self.controller = CamBridgeControl(host=self._get_active_host(), port=self._get_active_ctrl_port())
        res = self.controller.set_background_mode(self.bg_mode_var.get(), workload)
        self.log(f"Virtual Background workload routed to: {workload.upper()}: {res}")

    def _on_bg_mode_change(self, event=None):
        pass

    # --- Modals for "More Controls" ---
    def _show_obs_guide_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - OBS Studio & Streaming Integration Guide")
        dlg.geometry("740x580")
        dlg.minsize(680, 500)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="OBS Studio, Discord & Meeting Setup", font=("Segoe UI", 14, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 6))

        canvas = tk.Canvas(card, bg="#161B22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(card, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#161B22")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def add_step(title, steps):
            sub = tk.LabelFrame(scroll_frame, text=f" {title} ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
            sub.pack(fill=tk.X, pady=(0, 10))
            for s in steps:
                tk.Label(sub, text=s, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), justify=tk.LEFT, anchor="w", wraplength=620).pack(fill=tk.X, pady=2)

        add_step("Using with OBS Studio as a Virtual Webcam", [
            "1. Launch OBS Studio.",
            "2. Under 'Sources', click the '+' (Add) button.",
            "3. Select 'Video Capture Device' from the menu.",
            "4. Choose 'Unity Video Capture' (DirectShow driver) or 'OBS Virtual Camera'.",
            "5. Instant zero-latency camera stream is live in OBS without Window Capture overhead!"
        ])

        add_step("Using with Zoom, Google Meet & Microsoft Teams", [
            "1. Open Settings -> Video in Zoom or Meet.",
            "2. Select camera: 'Unity Video Capture' or 'OBS Virtual Camera'.",
            "3. Otter automatically feeds your high-res phone camera directly into the meeting."
        ])

        add_step("USB Tethering Mode (Zero ADB or Developer Options Needed)", [
            "1. Connect your phone to your PC with a standard USB data cable.",
            "2. Turn ON 'USB Tethering' on your phone (Settings -> Network -> Hotspot & Tethering).",
            "3. Select 'USB Tethering' on Otter desktop and click 'Connect & Start'."
        ])

        ttk.Button(card, text="Close Guide", style="Dark.TButton", command=dlg.destroy).pack(anchor="e", pady=(8, 0))

    def _show_deps_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - Dependencies & Driver Setup")
        dlg.geometry("680x480")
        dlg.minsize(620, 420)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="Python Dependencies & DirectShow Drivers", font=("Segoe UI", 14, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 6))

        # Status frame
        self.dep_status_frame = tk.Frame(card, bg="#161B22")
        self.dep_status_frame.pack(fill=tk.X, pady=(0, 10))
        self._refresh_dep_status_labels()

        btn_row = tk.Frame(card, bg="#161B22")
        btn_row.pack(fill=tk.X, pady=(0, 12))

        ttk.Button(btn_row, text="Auto-Install (pip)", style="Green.TButton", command=self._gui_install_deps).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Manual Instructions", style="Blue.TButton", command=self._gui_manual_instructions).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Uninstall Dependencies", style="Red.TButton", command=self._gui_uninstall_deps).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(btn_row, text="Refresh Status", style="Dark.TButton", command=self._refresh_dep_status_labels).pack(side=tk.LEFT)

        # Virtual Camera Driver section
        vcam_box = tk.LabelFrame(card, text=" DirectShow Virtual Camera Driver ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        vcam_box.pack(fill=tk.X, pady=(0, 10))

        vcam_desc = (
            "Registers the native DirectShow virtual camera ('Unity Video Capture') directly in Windows.\n"
            "Allows Zoom, Meet, Teams, Discord, and OBS to recognize Otter as a physical webcam."
        )
        tk.Label(vcam_box, text=vcam_desc, font=("Segoe UI", 9), fg="#C9D1D9", bg="#161B22", justify=tk.LEFT).pack(anchor="w", pady=(0, 6))

        vcam_btns = tk.Frame(vcam_box, bg="#161B22")
        vcam_btns.pack(fill=tk.X)
        ttk.Button(vcam_btns, text="Install / Register Driver", style="Green.TButton", command=self._gui_install_vcam_driver).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(vcam_btns, text="Unregister Driver", style="Red.TButton", command=self._gui_uninstall_vcam_driver).pack(side=tk.LEFT)

        ttk.Button(card, text="Close", style="Dark.TButton", command=dlg.destroy).pack(anchor="e", pady=(8, 0))

    def _show_oem_fix_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - OEM Background & Anti-Kill Fixes")
        dlg.geometry("720x540")
        dlg.minsize(640, 460)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="OEM Background & Anti-Kill Configurations", font=("Segoe UI", 14, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 6))

        canvas = tk.Canvas(card, bg="#161B22", highlightthickness=0)
        scrollbar = ttk.Scrollbar(card, orient=tk.VERTICAL, command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#161B22")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
                "Otter includes an active Foreground Service ('Foreground: ON') with PARTIAL_WAKE_LOCK.",
                "When Foreground is ON in the mobile app, you can turn off your screen or lock your phone and streaming stays active."
            ])
        ]

        for title, steps in oem_info:
            sub = tk.LabelFrame(scroll_frame, text=f" {title} ", bg="#161B22", fg="#3FB950", font=("Segoe UI", 10, "bold"), padx=10, pady=6)
            sub.pack(fill=tk.X, pady=4)
            for s in steps:
                tk.Label(sub, text=s, bg="#161B22", fg="#C9D1D9", font=("Segoe UI", 9), anchor="w", justify=tk.LEFT).pack(fill=tk.X, pady=1)

        ttk.Button(card, text="Close", style="Dark.TButton", command=dlg.destroy).pack(anchor="e", pady=(8, 0))

    def _show_settings_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - Application & Multi-Camera Settings")
        dlg.geometry("620x460")
        dlg.minsize(560, 400)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="Ports, Camera Names & Multi-Instance Setup", font=("Segoe UI", 14, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 10))

        # Port configuration
        grid = tk.Frame(card, bg="#161B22")
        grid.pack(fill=tk.X, pady=(0, 12))

        tk.Label(grid, text="Stream Port (TCP):", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22").grid(row=0, column=0, sticky="w", pady=4)
        entry_s = tk.Entry(grid, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT, highlightbackground="#30363D", highlightthickness=1)
        entry_s.insert(0, self.entry_stream_port.get().strip() or "8089")
        entry_s.grid(row=0, column=1, sticky="w", padx=8, pady=4)

        tk.Label(grid, text="Control Port (TCP):", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22").grid(row=1, column=0, sticky="w", pady=4)
        entry_c = tk.Entry(grid, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT, highlightbackground="#30363D", highlightthickness=1)
        entry_c.insert(0, self.entry_ctrl_port.get().strip() or "8090")
        entry_c.grid(row=1, column=1, sticky="w", padx=8, pady=4)

        tk.Label(grid, text="Camera Name:", font=("Segoe UI", 9, "bold"), fg="#8B949E", bg="#161B22").grid(row=2, column=0, sticky="w", pady=4)
        entry_n = tk.Entry(grid, width=20, bg="#0D1117", fg="#C9D1D9", insertbackground="#C9D1D9", relief=tk.FLAT, highlightbackground="#30363D", highlightthickness=1)
        entry_n.insert(0, self.entry_cam_name.get().strip() or "Otter Cam 1")
        entry_n.grid(row=2, column=1, sticky="w", padx=8, pady=4)

        chk_vcam = tk.Checkbutton(grid, text="Register DirectShow / OBS Virtual Camera", variable=self.vcam_var, bg="#161B22", fg="#C9D1D9", selectcolor="#0D1117", activebackground="#161B22")
        chk_vcam.grid(row=3, column=0, columnspan=2, sticky="w", pady=6)

        def _save_settings():
            self.entry_stream_port.delete(0, tk.END)
            self.entry_stream_port.insert(0, entry_s.get().strip())
            self.entry_ctrl_port.delete(0, tk.END)
            self.entry_ctrl_port.insert(0, entry_c.get().strip())
            self.entry_cam_name.delete(0, tk.END)
            self.entry_cam_name.insert(0, entry_n.get().strip())
            self.log(f"Settings saved: Port {entry_s.get().strip()} / Ctrl {entry_c.get().strip()} / '{entry_n.get().strip()}'")
            dlg.destroy()

        # Multi-cam instance
        mc_box = tk.LabelFrame(card, text=" Multi-Camera Parallel Instances ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        mc_box.pack(fill=tk.X, pady=(0, 12))
        tk.Label(mc_box, text="Spawn multiple desktop instances to run 2 or more cameras simultaneously:", font=("Segoe UI", 9), fg="#C9D1D9", bg="#161B22").pack(anchor="w", pady=(0, 6))
        ttk.Button(mc_box, text="+ Multi-Cam Instance", style="Blue.TButton", command=self._spawn_new_instance).pack(anchor="w")

        btn_row = tk.Frame(card, bg="#161B22")
        btn_row.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(btn_row, text="Save & Apply", style="Green.TButton", command=_save_settings).pack(side=tk.RIGHT, padx=(6, 0))
        ttk.Button(btn_row, text="Cancel", style="Dark.TButton", command=dlg.destroy).pack(side=tk.RIGHT)

    def _show_diagnostics_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - System Diagnostics & Platform Tools")
        dlg.geometry("680x480")
        dlg.minsize(600, 400)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="ADB Platform Tools & Hardware Diagnostics", font=("Segoe UI", 14, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=(0, 10))

        # ADB Status
        self.adb_status_frame = tk.Frame(card, bg="#161B22")
        self.adb_status_frame.pack(fill=tk.X, pady=(0, 8))
        self._refresh_adb_status_labels()

        adb_btns = tk.Frame(card, bg="#161B22")
        adb_btns.pack(fill=tk.X, pady=(0, 12))
        self.btn_download_adb = ttk.Button(adb_btns, text="Download ADB Minimal Tools (~15MB)", style="Green.TButton", command=self._gui_download_adb)
        self.btn_download_adb.pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(adb_btns, text="Check ADB Status", style="Dark.TButton", command=self._refresh_adb_status_labels).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(adb_btns, text="Remove Portable ADB", style="Red.TButton", command=self._gui_uninstall_adb).pack(side=tk.LEFT)

        # Android 14 UVC
        uvc_box = tk.LabelFrame(card, text=" Android 14+ Native USB Webcam Mode ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 10, "bold"), padx=10, pady=8)
        uvc_box.pack(fill=tk.X, pady=(0, 12))
        uvc_desc = "On Pixel, Motorola, and supported devices with UVC gadget drivers, transforms phone into a native hardware USB webcam."
        tk.Label(uvc_box, text=uvc_desc, font=("Segoe UI", 8), fg="#8B949E", bg="#161B22").pack(anchor="w", pady=(0, 6))

        uvc_btns = tk.Frame(uvc_box, bg="#161B22")
        uvc_btns.pack(fill=tk.X)
        ttk.Button(uvc_btns, text="Activate Android 14 UVC Webcam", style="Green.TButton", command=self._gui_activate_uvc).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(uvc_btns, text="Reset USB Mode (MTP)", style="Dark.TButton", command=self._gui_reset_uvc).pack(side=tk.LEFT)

        ttk.Button(card, text="Close", style="Dark.TButton", command=dlg.destroy).pack(anchor="e", pady=(8, 0))

    def _show_about_modal(self):
        dlg = tk.Toplevel(self.root)
        dlg.title("Otter - About & Permissive Open Source License")
        dlg.geometry("660x520")
        dlg.minsize(600, 440)
        dlg.configure(bg="#0B0F14")
        dlg.transient(self.root)

        card = tk.Frame(dlg, bg="#161B22", padx=16, pady=14, highlightbackground="#30363D", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)

        tk.Label(card, text="Otter", font=("Segoe UI", 18, "bold"), fg="#58A6FF", bg="#161B22").pack(anchor="w")
        tk.Label(card, text="Open-source Android to PC Virtual Camera & Remote Control Suite", font=("Segoe UI", 9), fg="#8B949E", bg="#161B22").pack(anchor="w", pady=(0, 10))

        meta = tk.LabelFrame(card, text=" Project & Attribution ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 9, "bold"), padx=10, pady=6)
        meta.pack(fill=tk.X, pady=(0, 10))
        tk.Label(meta, text="Developer: spacecar", font=("Segoe UI", 9, "bold"), fg="#3FB950", bg="#161B22").pack(anchor="w")
        tk.Label(meta, text="Official Repository: https://github.com/saprecar/Otter", font=("Segoe UI", 9), fg="#58A6FF", bg="#161B22").pack(anchor="w", pady=2)

        btn_box = tk.Frame(meta, bg="#161B22", pady=4)
        btn_box.pack(fill=tk.X)
        ttk.Button(btn_box, text="Open GitHub Repository", style="Blue.TButton", command=lambda: webbrowser.open("https://github.com/saprecar/Otter")).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_box, text="Consolidated Master Policy", style="Blue.TButton", command=lambda: webbrowser.open(self.MASTER_POLICY_URL)).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(btn_box, text="Attribution & Licenses", style="Dark.TButton", command=lambda: webbrowser.open(self.ATTRIBUTION_URL)).pack(side=tk.LEFT)

        lic_box = tk.LabelFrame(card, text=" MIT License ", bg="#161B22", fg="#58A6FF", font=("Segoe UI", 9, "bold"), padx=10, pady=6)
        lic_box.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        lic_text = (
            "MIT License - Free and Permissive for Personal and Commercial Use.\n\n"
            "Attribution Requirement:\n"
            "If code or assets from this project are reused in other applications, you are required\n"
            "to retain the original copyright notice, name 'Otter', and link to https://github.com/saprecar/Otter.\n\n"
            "Special thanks to the open-source community, Google Android Platform Tools, and OBS Studio."
        )
        tk.Label(lic_box, text=lic_text, font=("Segoe UI", 9), fg="#C9D1D9", bg="#161B22", justify=tk.LEFT, anchor="w").pack(fill=tk.BOTH, expand=True)

        ttk.Button(card, text="Close", style="Dark.TButton", command=dlg.destroy).pack(anchor="e")

    # --- Dependency & Driver Helpers ---
    def _refresh_dep_status_labels(self):
        if not hasattr(self, "dep_status_frame"):
            return
        for widget in self.dep_status_frame.winfo_children():
            widget.destroy()

        status = manage_dependencies.check_dependencies()
        for pkg, installed in status.items():
            color = "#3FB950" if installed else "#DA3633"
            txt = f"{pkg}: {'INSTALLED' if installed else 'MISSING'}"
            lbl = tk.Label(self.dep_status_frame, text=txt, font=("Segoe UI", 9, "bold"), fg=color, bg="#21262D", padx=8, pady=3)
            lbl.pack(side=tk.LEFT, padx=(0, 8))

    def _gui_install_deps(self):
        disclaimer = "Automated package installation runs standard pip commands targeting official PyPI packages (opencv-python, numpy).\n\nProceed?"
        if not messagebox.askyesno("Install Dependencies", disclaimer):
            return
        self.log("Installing Otter dependencies via pip...")
        def worker():
            success, msg = manage_dependencies.install_dependencies(auto_confirm=True, log_callback=self.log)
            self.root.after(0, lambda: self._on_install_completed(success, msg))
        threading.Thread(target=worker, daemon=True).start()

    def _on_install_completed(self, success, msg):
        self._refresh_dep_status_labels()
        if success:
            self.log(f"Dependencies installed: {msg}")
            messagebox.showinfo("Ready", msg)
        else:
            self.log(f"Dependency error: {msg}")
            messagebox.showwarning("Notice", msg)

    def _gui_uninstall_deps(self):
        if not messagebox.askyesno("Uninstall", "Uninstall Otter packages (opencv-python, numpy)?"):
            return
        self.log("Uninstalling Otter dependencies...")
        def worker():
            success = manage_dependencies.uninstall_dependencies(auto_confirm=True)
            self.root.after(0, lambda: self._on_uninstall_completed(success))
        threading.Thread(target=worker, daemon=True).start()

    def _on_uninstall_completed(self, success):
        self._refresh_dep_status_labels()
        self.log("Dependencies uninstalled.")
        messagebox.showinfo("Uninstalled", "Packages removed.")

    def _gui_manual_instructions(self):
        msg = "Manual Installation via Terminal:\n\npip install opencv-python numpy\n\nTo uninstall later:\npip uninstall -y opencv-python numpy"
        messagebox.showinfo("Manual Instructions", msg)

    def _gui_install_vcam_driver(self):
        bat_path = os.path.join(os.path.dirname(__file__), "driver", "install_virtual_cam.bat")
        if not os.path.exists(bat_path):
            messagebox.showerror("Error", f"Could not find driver installer at:\n{bat_path}")
            return
        try:
            subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
            self.log("Launched DirectShow Virtual Camera Driver registration.")
            messagebox.showinfo("Driver Installer", "Launched DirectShow Driver Registration with Administrator rights.\nAccept UAC prompt to complete setup.")
        except Exception as e:
            self.log(f"Failed to launch driver installer: {e}")
            messagebox.showerror("Error", f"Failed: {e}")

    def _gui_uninstall_vcam_driver(self):
        bat_path = os.path.join(os.path.dirname(__file__), "driver", "uninstall_virtual_cam.bat")
        if not os.path.exists(bat_path):
            messagebox.showerror("Error", f"Could not find uninstaller at:\n{bat_path}")
            return
        try:
            subprocess.Popen(["cmd.exe", "/c", bat_path], shell=True)
            self.log("Launched DirectShow Virtual Camera Driver unregistration.")
            messagebox.showinfo("Driver Uninstaller", "Launched unregistration script.")
        except Exception as e:
            self.log(f"Failed to launch uninstaller: {e}")
            messagebox.showerror("Error", f"Failed: {e}")

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

    def _gui_download_adb(self):
        if not messagebox.askyesno("Download ADB", "Download official Google platform-tools (adb) directly from dl.google.com?"):
            return
        self.btn_download_adb.configure(state=tk.DISABLED)
        self.log("Downloading official Google platform-tools (ADB)...")
        def worker():
            try:
                path = manage_adb.download_and_extract_adb(progress_callback=lambda msg, pct: self.log(f"ADB Setup: {msg}"))
                self.root.after(0, lambda: self._on_adb_download_completed(True, path))
            except Exception as e:
                self.root.after(0, lambda: self._on_adb_download_completed(False, str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def _on_adb_download_completed(self, success, info):
        self.btn_download_adb.configure(state=tk.NORMAL)
        self._refresh_adb_status_labels()
        if success:
            self.log(f"ADB Minimal Tools installed: {info}")
            messagebox.showinfo("ADB Ready", "Minimal Android Platform Tools (adb) installed successfully!")
        else:
            self.log(f"ADB Download failed: {info}")
            messagebox.showerror("Error", f"Failed: {info}")

    def _gui_uninstall_adb(self):
        if not messagebox.askyesno("Remove ADB", "Remove downloaded portable ADB tools from Otter folder?"):
            return
        manage_adb.uninstall_adb()
        self._refresh_adb_status_labels()
        self.log("Portable ADB tools removed.")
        messagebox.showinfo("Removed", "Portable ADB removed.")

    def _gui_activate_uvc(self):
        self.log("Requesting Android 14 native USB webcam mode via ADB...")
        def worker():
            tunnel = ADBTunnel()
            adb_cmd = tunnel.adb_bin
            if not adb_cmd:
                self.root.after(0, lambda: messagebox.showerror("ADB Not Found", "ADB executable not found."))
                return
            try:
                subprocess.run([adb_cmd, "shell", "svc", "usb", "setFunctions", "uvc"], capture_output=True, text=True, timeout=5)
                check_pkg = subprocess.run([adb_cmd, "shell", "pm", "path", "com.android.DeviceAsWebcam"], capture_output=True, text=True, timeout=5)
                has_webcam_app = "package:" in (check_pkg.stdout or "")
                if has_webcam_app:
                    msg = "Native Android 14 USB Webcam activated!\nCheck Windows Device Manager or Camera app."
                    self.root.after(0, lambda: messagebox.showinfo("Android 14 Webcam", msg))
                    self.log("Native Android 14 USB webcam activated successfully.")
                else:
                    msg = "Notice: Device manufacturer stripped DeviceAsWebcam; using Otter ADB tunnel instead."
                    self.root.after(0, lambda: messagebox.showinfo("OEM Notice", msg))
                    self.log(msg)
            except Exception as e:
                self.log(f"UVC error: {e}")
                self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        threading.Thread(target=worker, daemon=True).start()

    def _gui_reset_uvc(self):
        self.log("Resetting phone USB mode to standard MTP...")
        def worker():
            tunnel = ADBTunnel()
            adb_bin = tunnel.adb_bin
            if not adb_bin:
                self.root.after(0, lambda: messagebox.showerror("ADB Not Found", "ADB executable not found."))
                return
            try:
                subprocess.run([adb_bin, "shell", "svc", "usb", "setFunctions", "mtp"], capture_output=True, text=True, timeout=5)
                self.log("Phone USB mode restored to MTP.")
                self.root.after(0, lambda: messagebox.showinfo("Reset USB", "Phone USB mode reset to MTP."))
            except Exception as e:
                self.log(f"Reset USB error: {e}")
        threading.Thread(target=worker, daemon=True).start()

    def _spawn_new_instance(self):
        try:
            cmd = [sys.executable, os.path.abspath(__file__)]
            subprocess.Popen(cmd)
            self.log("Spawned new parallel Otter desktop instance.")
        except Exception as e:
            self.log(f"Failed to spawn new instance: {e}")

    def on_close(self):
        self.stop_stream()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = OtterApp(root)
    root.mainloop()

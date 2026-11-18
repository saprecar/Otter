import os
import cv2
import numpy as np

W, H = 1920, 1080

def draw_round_rect(img, pt1, pt2, color, thickness=-1, radius=12):
    x1, y1 = pt1
    x2, y2 = pt2
    if thickness == -1:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, -1)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, -1)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, -1)
    else:
        cv2.line(img, (x1 + radius, y1), (x2 - radius, y1), color, thickness)
        cv2.line(img, (x1 + radius, y2), (x2 - radius, y2), color, thickness)
        cv2.line(img, (x1, y1 + radius), (x1, y2 - radius), color, thickness)
        cv2.line(img, (x2, y1 + radius), (x2, y2 - radius), color, thickness)
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

def draw_otter_logo(img, cx, cy, radius=24):
    scale = radius / 48.0
    cv2.circle(img, (cx, cy), int(48 * scale), (235, 111, 31), -1, cv2.LINE_AA)
    ear_l = np.array([(int(cx + (34-54)*scale), int(cy + (34-54)*scale)), (int(cx + (25-54)*scale), int(cy + (32-54)*scale)), (int(cx + (28-54)*scale), int(cy + (44-54)*scale))], np.int32)
    cv2.fillPoly(img, [ear_l], (35, 68, 107), cv2.LINE_AA)
    ear_r = np.array([(int(cx + (74-54)*scale), int(cy + (34-54)*scale)), (int(cx + (83-54)*scale), int(cy + (32-54)*scale)), (int(cx + (80-54)*scale), int(cy + (44-54)*scale))], np.int32)
    cv2.fillPoly(img, [ear_r], (35, 68, 107), cv2.LINE_AA)
    cv2.ellipse(img, (cx, cy), (int(22 * scale), int(25 * scale)), 0, 0, 360, (76, 91, 141), -1, cv2.LINE_AA)
    cv2.ellipse(img, (int(cx + (54-54)*scale), int(cy + (63-54)*scale)), (int(12 * scale), int(10 * scale)), 0, 0, 360, (157, 181, 215), -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx + (43-54)*scale), int(cy + (46-54)*scale)), int(3.5 * scale), (34, 27, 22), -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx + (65-54)*scale), int(cy + (46-54)*scale)), int(3.5 * scale), (34, 27, 22), -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx + (54-54)*scale), int(cy + (58-54)*scale)), int(5.5 * scale), (34, 27, 22), -1, cv2.LINE_AA)
    cv2.circle(img, (int(cx + (54-54)*scale), int(cy + (58-54)*scale)), int(2.5 * scale), (255, 166, 88), -1, cv2.LINE_AA)

def render_tablet_screen(title_text, subtitle_text, mode_active="meetings", highlight_section=None, virtual_bg_mode="off", res_text="1080p FHD", fps_text="60 FPS", lens_text="Lens: 0 (BACK)", custom_footer=None):
    img = np.zeros((H, W, 3), dtype=np.uint8)

    # 1. Background gradient #0D1117 to #161B22
    for y in range(H):
        factor = y / float(H)
        b = int(23 + factor * 11)
        g = int(17 + factor * 10)
        r = int(13 + factor * 9)
        img[y, :] = (b, g, r)

    # 2. Marketing Top Banner (Y: 0 to 110)
    cv2.rectangle(img, (0, 0), (W, 110), (22, 27, 34), -1)
    cv2.line(img, (0, 110), (W, 110), (48, 54, 61), 2)
    cv2.line(img, (48, 110), (480, 110), (255, 166, 88), 3, cv2.LINE_AA)

    cv2.putText(img, title_text, (48, 52), cv2.FONT_HERSHEY_DUPLEX, 1.10, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, subtitle_text, (48, 90), cv2.FONT_HERSHEY_DUPLEX, 0.68, (88, 166, 255), 1, cv2.LINE_AA)

    cv2.putText(img, 'OTTER 10" TABLET CONSOLE', (W - 460, 50), cv2.FONT_HERSHEY_DUPLEX, 0.72, (201, 209, 217), 1, cv2.LINE_AA)
    cv2.putText(img, '1920x1080 HD Workstation Split View', (W - 460, 80), cv2.FONT_HERSHEY_DUPLEX, 0.55, (139, 148, 158), 1, cv2.LINE_AA)

    # 3. Left Side: Viewfinder Card (X: 40 to 1120, Y: 130 to 1040)
    vx1, vy1, vx2, vy2 = 40, 130, 1120, 1040
    draw_round_rect(img, (vx1, vy1), (vx2, vy2), (18, 22, 28), -1, radius=16)
    draw_round_rect(img, (vx1, vy1), (vx2, vy2), (48, 54, 61), thickness=2, radius=16)

    # Simulated Studio Webcam feed inside Viewfinder
    vw_inner = img[vy1+4:vy2-4, vx1+4:vx2-4]
    ih, iw = vw_inner.shape[:2]

    if virtual_bg_mode == "custom":
        # Custom modern office gradient backdrop
        for y in range(ih):
            factor = y / float(ih)
            vw_inner[y, :] = (int(50 + factor * 20), int(40 + factor * 15), int(30 + factor * 10))
        # Draw window frame in background
        cv2.rectangle(vw_inner, (iw - 350, 40), (iw - 50, ih - 200), (80, 65, 50), 3)
        cv2.line(vw_inner, (iw - 200, 40), (iw - 200, ih - 200), (80, 65, 50), 2)
        cv2.line(vw_inner, (iw - 350, 250), (iw - 50, 250), (80, 65, 50), 2)
    elif virtual_bg_mode == "dim":
        # Dim display mode (70% brightness reduction simulation)
        for y in range(ih):
            vw_inner[y, :] = (15, 12, 10)
    else:
        # Normal studio room background
        for y in range(ih):
            factor = y / float(ih)
            vw_inner[y, :] = (int(35 + factor * 25), int(25 + factor * 20), int(20 + factor * 18))
        # Studio acoustic panels on back wall
        for px in range(80, iw - 100, 180):
            cv2.rectangle(vw_inner, (px, 80), (px + 120, ih - 250), (30, 22, 18), -1)

    # Subject Silhouette in center (Head & Shoulders studio portrait)
    scx, scy = iw // 2, int(ih * 0.58)
    # Body / Shoulders
    cv2.ellipse(vw_inner, (scx, int(ih * 0.92)), (int(iw * 0.35), int(ih * 0.38)), 0, 0, 360, (28, 22, 18), -1, cv2.LINE_AA)
    # Head
    cv2.circle(vw_inner, (scx, scy - 120), int(ih * 0.18), (65, 52, 45), -1, cv2.LINE_AA)
    # Face highlight
    cv2.circle(vw_inner, (scx, scy - 120), int(ih * 0.16), (145, 175, 210), -1, cv2.LINE_AA)
    # Eyes
    cv2.circle(vw_inner, (scx - 45, scy - 130), 8, (34, 27, 22), -1, cv2.LINE_AA)
    cv2.circle(vw_inner, (scx + 45, scy - 130), 8, (34, 27, 22), -1, cv2.LINE_AA)

    # Rule of thirds subtle grid lines
    for gx in [int(iw * 0.33), int(iw * 0.66)]:
        cv2.line(vw_inner, (gx, 0), (gx, ih), (60, 70, 80), 1, cv2.LINE_AA)
    for gy in [int(ih * 0.33), int(ih * 0.66)]:
        cv2.line(vw_inner, (0, gy), (iw, gy), (60, 70, 80), 1, cv2.LINE_AA)

    # Face Detection Focus Tracking Bounding Box
    fb_w, fb_h = int(iw * 0.32), int(ih * 0.44)
    fb_x1, fb_y1 = scx - fb_w // 2, scy - int(ih * 0.32)
    fb_x2, fb_y2 = fb_x1 + fb_w, fb_y1 + fb_h
    corner_len = 28
    box_color = (88, 166, 255) # Cyan
    cv2.line(vw_inner, (fb_x1, fb_y1), (fb_x1 + corner_len, fb_y1), box_color, 2)
    cv2.line(vw_inner, (fb_x1, fb_y1), (fb_x1, fb_y1 + corner_len), box_color, 2)
    cv2.line(vw_inner, (fb_x2, fb_y1), (fb_x2 - corner_len, fb_y1), box_color, 2)
    cv2.line(vw_inner, (fb_x2, fb_y1), (fb_x2, fb_y1 + corner_len), box_color, 2)
    cv2.line(vw_inner, (fb_x1, fb_y2), (fb_x1 + corner_len, fb_y2), box_color, 2)
    cv2.line(vw_inner, (fb_x1, fb_y2), (fb_x1, fb_y2 - corner_len), box_color, 2)
    cv2.line(vw_inner, (fb_x2, fb_y2), (fb_x2 - corner_len, fb_y2), box_color, 2)
    cv2.line(vw_inner, (fb_x2, fb_y2), (fb_x2, fb_y2 - corner_len), box_color, 2)
    cv2.putText(vw_inner, 'AF TRACK [FACE/BODY]', (fb_x1 + 6, fb_y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 0.48, box_color, 1, cv2.LINE_AA)

    # Top Badges inside Viewfinder
    # [LIVE] Badge
    draw_round_rect(vw_inner, (20, 20), (120, 56), (35, 134, 54), -1, radius=6)
    cv2.putText(vw_inner, 'LIVE', (36, 45), cv2.FONT_HERSHEY_DUPLEX, 0.58, (255, 255, 255), 1, cv2.LINE_AA)

    # Resolution Badge
    draw_round_rect(vw_inner, (132, 20), (252, 56), (22, 27, 34), -1, radius=6)
    draw_round_rect(vw_inner, (132, 20), (252, 56), (48, 54, 61), 1, radius=6)
    cv2.putText(vw_inner, res_text, (144, 45), cv2.FONT_HERSHEY_DUPLEX, 0.52, (201, 209, 217), 1, cv2.LINE_AA)

    # FPS Badge
    draw_round_rect(vw_inner, (264, 20), (370, 56), (22, 27, 34), -1, radius=6)
    draw_round_rect(vw_inner, (264, 20), (370, 56), (48, 54, 61), 1, radius=6)
    cv2.putText(vw_inner, fps_text, (278, 45), cv2.FONT_HERSHEY_DUPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

    # Right Floating Zoom Controls inside Viewfinder
    zx = iw - 70
    draw_round_rect(vw_inner, (zx, 120), (zx + 50, 160), (22, 27, 34), -1, radius=6)
    cv2.putText(vw_inner, '+', (zx + 18, 148), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

    draw_round_rect(vw_inner, (zx - 10, 170), (zx + 60, 202), (13, 17, 23), -1, radius=6)
    cv2.putText(vw_inner, '1.0x', (zx, 192), cv2.FONT_HERSHEY_DUPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

    draw_round_rect(vw_inner, (zx, 212), (zx + 50, 252), (22, 27, 34), -1, radius=6)
    cv2.putText(vw_inner, '-', (zx + 20, 240), cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)

    # Bottom Viewfinder Overlay Bar
    draw_round_rect(vw_inner, (20, ih - 54), (iw - 20, ih - 14), (13, 17, 23), -1, radius=6)
    if highlight_section == "network":
        draw_round_rect(vw_inner, (20, ih - 54), (iw - 20, ih - 14), (88, 166, 255), 2, radius=6)
    footer_str = custom_footer if custom_footer else f"Port: 8089  |  {lens_text}  |  H.264 Hardware Encoded  |  USB ADB Tunnel (Active)"
    cv2.putText(vw_inner, footer_str, (34, ih - 26), cv2.FONT_HERSHEY_DUPLEX, 0.48, (139, 148, 158), 1, cv2.LINE_AA)

    # 4. Right Side: Full Tablet Control Console (X: 1140 to 1880, Y: 130 to 1040)
    cx1, cy1, cx2, cy2 = 1140, 130, 1880, 1040
    draw_round_rect(img, (cx1, cy1), (cx2, cy2), (22, 27, 34), -1, radius=16)
    draw_round_rect(img, (cx1, cy1), (cx2, cy2), (48, 54, 61), thickness=2, radius=16)

    # Console Header
    draw_otter_logo(img, cx1 + 38, cy1 + 36, radius=22)
    cv2.putText(img, 'Otter Cam', (cx1 + 72, cy1 + 32), cv2.FONT_HERSHEY_DUPLEX, 0.82, (255, 255, 255), 2, cv2.LINE_AA)
    cv2.putText(img, 'Professional Camera for Every Purpose', (cx1 + 72, cy1 + 52), cv2.FONT_HERSHEY_DUPLEX, 0.48, (139, 148, 158), 1, cv2.LINE_AA)

    # Top Right Console buttons: [About] [Full]
    draw_round_rect(img, (cx2 - 160, cy1 + 20), (cx2 - 90, cy1 + 52), (13, 17, 23), -1, radius=6)
    cv2.putText(img, 'About', (cx2 - 148, cy1 + 42), cv2.FONT_HERSHEY_DUPLEX, 0.46, (201, 209, 217), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx2 - 80, cy1 + 20), (cx2 - 20, cy1 + 52), (13, 17, 23), -1, radius=6)
    cv2.putText(img, '[ ]', (cx2 - 62, cy1 + 42), cv2.FONT_HERSHEY_DUPLEX, 0.50, (201, 209, 217), 1, cv2.LINE_AA)

    cv2.line(img, (cx1 + 20, cy1 + 68), (cx2 - 20, cy1 + 68), (48, 54, 61), 1)

    # 4A. Quick Modes Section
    q_y = cy1 + 92
    cv2.putText(img, 'Quick Modes (One-Click Presets)', (cx1 + 24, q_y), cv2.FONT_HERSHEY_DUPLEX, 0.58, (88, 166, 255), 1, cv2.LINE_AA)

    modes = [
        ('Meetings', (35, 134, 54)),
        ('Online Class', (31, 111, 235)),
        ('Streaming', (137, 87, 229)),
        ('Snapshot', (218, 90, 42)),
        ('Scan/OCR', (199, 107, 24)),
        ('Security', (50, 60, 70)),
        ('Fun Filter', (46, 160, 67)),
        ('Pro Manual', (210, 80, 160))
    ]

    card_w = (cx2 - cx1 - 60) // 4
    card_h = 36
    for idx, (m_name, m_col) in enumerate(modes):
        row = idx // 4
        col = idx % 4
        mx1 = cx1 + 24 + col * (card_w + 8)
        my1 = q_y + 14 + row * (card_h + 8)
        mx2 = mx1 + card_w
        my2 = my1 + card_h
        is_sel = (m_name.lower().replace(' ', '').startswith(mode_active[:4].lower()))
        bg_col = m_col if is_sel else (13, 17, 23)
        draw_round_rect(img, (mx1, my1), (mx2, my2), bg_col, -1, radius=6)
        draw_round_rect(img, (mx1, my1), (mx2, my2), m_col, 2 if is_sel else 1, radius=6)
        cv2.putText(img, m_name, (mx1 + 8, my1 + 24), cv2.FONT_HERSHEY_DUPLEX, 0.44, (255, 255, 255), 1, cv2.LINE_AA)

    if highlight_section == "presets":
        draw_round_rect(img, (cx1 + 16, q_y - 8), (cx2 - 16, q_y + 104), (88, 166, 255), 2, radius=8)

    # 4B. Camera Settings & Optics (Exposure & Focus)
    opt_y = q_y + 115
    cv2.putText(img, 'Camera Settings & Pro Optics', (cx1 + 24, opt_y), cv2.FONT_HERSHEY_DUPLEX, 0.58, (88, 166, 255), 1, cv2.LINE_AA)

    # Exposure Row: [EV -] [===o===] [EV +] +0.0
    ey = opt_y + 16
    draw_round_rect(img, (cx1 + 24, ey), (cx1 + 90, ey + 30), (13, 17, 23), -1, radius=6)
    cv2.putText(img, 'EV -', (cx1 + 42, ey + 21), cv2.FONT_HERSHEY_DUPLEX, 0.48, (201, 209, 217), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 102, ey + 11), (cx2 - 180, ey + 17), (48, 54, 61), -1, radius=3)
    cv2.circle(img, (cx1 + 280, ey + 14), 8, (88, 166, 255), -1, cv2.LINE_AA)

    draw_round_rect(img, (cx2 - 168, ey), (cx2 - 102, ey + 30), (13, 17, 23), -1, radius=6)
    cv2.putText(img, 'EV +', (cx2 - 152, ey + 21), cv2.FONT_HERSHEY_DUPLEX, 0.48, (201, 209, 217), 1, cv2.LINE_AA)

    cv2.putText(img, '+0.5 EV', (cx2 - 85, ey + 22), cv2.FONT_HERSHEY_DUPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

    # Focus Row: [AF: Auto] [===o===] Auto
    fy = ey + 42
    draw_round_rect(img, (cx1 + 24, fy), (cx1 + 120, fy + 30), (35, 134, 54), -1, radius=6)
    cv2.putText(img, 'AF: Auto', (cx1 + 36, fy + 21), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 132, fy + 11), (cx2 - 110, fy + 17), (48, 54, 61), -1, radius=3)
    cv2.circle(img, (cx1 + 340, fy + 14), 8, (35, 134, 54), -1, cv2.LINE_AA)
    cv2.putText(img, 'Continuous', (cx2 - 95, fy + 22), cv2.FONT_HERSHEY_DUPLEX, 0.48, (88, 166, 255), 1, cv2.LINE_AA)

    # Quick Toggles: [Flip] [Rotate 0] [Torch: OFF] [Glow: Warm]
    ty = fy + 42
    btn_w = (cx2 - cx1 - 60) // 4
    btn_labels = ['Flip: OFF', 'Rotate: 0', 'Torch: OFF', 'Glow: Warm']
    for b_i, b_lbl in enumerate(btn_labels):
        bx1 = cx1 + 24 + b_i * (btn_w + 8)
        bx2 = bx1 + btn_w
        draw_round_rect(img, (bx1, ty), (bx2, ty + 32), (13, 17, 23), -1, radius=6)
        draw_round_rect(img, (bx1, ty), (bx2, ty + 32), (48, 54, 61), 1, radius=6)
        cv2.putText(img, b_lbl, (bx1 + 10, ty + 22), cv2.FONT_HERSHEY_DUPLEX, 0.44, (201, 209, 217), 1, cv2.LINE_AA)

    # Pro Manual Sliders: [ISO: 400] [Shutter: 1/250s] [WB: Daylight] [FX: Color]
    py = ty + 44
    pro_btns = ['ISO: 400', 'Shutter: 1/250s', 'WB: 5500K', 'FX: Color']
    for p_i, p_lbl in enumerate(pro_btns):
        px1 = cx1 + 24 + p_i * (btn_w + 8)
        px2 = px1 + btn_w
        draw_round_rect(img, (px1, py), (px2, py + 32), (13, 17, 23), -1, radius=6)
        draw_round_rect(img, (px1, py), (px2, py + 32), (88, 166, 255), 1, radius=6)
        cv2.putText(img, p_lbl, (px1 + 8, py + 22), cv2.FONT_HERSHEY_DUPLEX, 0.42, (88, 166, 255), 1, cv2.LINE_AA)

    if highlight_section == "optics":
        draw_round_rect(img, (cx1 + 16, opt_y - 8), (cx2 - 16, py + 40), (88, 166, 255), 2, radius=8)

    # 4C. Virtual Background & Workload Routing Section
    vbg_y = py + 48
    is_vbg_highlight = (highlight_section == "virtual_bg")
    bg_box_col = (88, 166, 255) if is_vbg_highlight else (48, 54, 61)
    draw_round_rect(img, (cx1 + 20, vbg_y), (cx2 - 20, vbg_y + 82), (13, 17, 23), -1, radius=8)
    draw_round_rect(img, (cx1 + 20, vbg_y), (cx2 - 20, vbg_y + 82), bg_box_col, 2 if is_vbg_highlight else 1, radius=8)

    cv2.putText(img, 'Virtual Background & AI Workload Routing', (cx1 + 32, vbg_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

    # Workload Button: PC GPU Offload (Recommended)
    draw_round_rect(img, (cx1 + 32, vbg_y + 36), (cx2 - 32, vbg_y + 70), (35, 134, 54) if virtual_bg_mode == "custom" else (22, 27, 34), -1, radius=6)
    vbg_text = 'Workload: PC GPU Offload (Custom Image Background Active)' if virtual_bg_mode == "custom" else 'Workload: PC GPU Offload (Recommended - Saves Phone Battery)'
    cv2.putText(img, vbg_text, (cx1 + 44, vbg_y + 59), cv2.FONT_HERSHEY_DUPLEX, 0.46, (255, 255, 255), 1, cv2.LINE_AA)

    # 4D. Screen Wake & Power Management Section
    pwr_y = vbg_y + 96
    is_pwr_highlight = (highlight_section == "power")
    pwr_box_col = (88, 166, 255) if is_pwr_highlight else (48, 54, 61)
    draw_round_rect(img, (cx1 + 20, pwr_y), (cx2 - 20, pwr_y + 78), (13, 17, 23), -1, radius=8)
    draw_round_rect(img, (cx1 + 20, pwr_y), (cx2 - 20, pwr_y + 78), pwr_box_col, 2 if is_pwr_highlight else 1, radius=8)

    cv2.putText(img, 'Screen Wake & Power Management', (cx1 + 32, pwr_y + 24), cv2.FONT_HERSHEY_DUPLEX, 0.52, (88, 166, 255), 1, cv2.LINE_AA)

    # [Screen: Keep ON] and [Dim Display (Save Power)]
    pw_btn_w = (cx2 - cx1 - 68) // 2
    draw_round_rect(img, (cx1 + 32, pwr_y + 34), (cx1 + 32 + pw_btn_w, pwr_y + 68), (35, 134, 54), -1, radius=6)
    cv2.putText(img, 'Screen: Keep ON', (cx1 + 54, pwr_y + 56), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    dim_bg = (218, 90, 42) if virtual_bg_mode == "dim" else (22, 27, 34)
    draw_round_rect(img, (cx1 + 44 + pw_btn_w, pwr_y + 34), (cx2 - 32, pwr_y + 68), dim_bg, -1, radius=6)
    dim_txt = 'Screen: Dimmed (Active)' if virtual_bg_mode == "dim" else 'Dim Display (Save Power)'
    cv2.putText(img, dim_txt, (cx1 + 60 + pw_btn_w, pwr_y + 56), cv2.FONT_HERSHEY_DUPLEX, 0.48, (255, 255, 255), 1, cv2.LINE_AA)

    # 4E. Streaming Transport Actions & Bottom Controls
    act_y = pwr_y + 92
    if highlight_section == "transport":
        draw_round_rect(img, (cx1 + 16, act_y - 6), (cx2 - 16, act_y + 50), (88, 166, 255), 2, radius=8)

    draw_round_rect(img, (cx1 + 24, act_y), (cx1 + 180, act_y + 44), (35, 134, 54), -1, radius=8)
    cv2.putText(img, 'Start Stream', (cx1 + 44, act_y + 28), cv2.FONT_HERSHEY_DUPLEX, 0.54, (255, 255, 255), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 192, act_y), (cx1 + 310, act_y + 44), (22, 27, 34), -1, radius=8)
    cv2.putText(img, 'Pause', (cx1 + 226, act_y + 28), cv2.FONT_HERSHEY_DUPLEX, 0.52, (201, 209, 217), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 322, act_y), (cx1 + 440, act_y + 44), (218, 54, 51), -1, radius=8)
    cv2.putText(img, 'Stop', (cx1 + 360, act_y + 28), cv2.FONT_HERSHEY_DUPLEX, 0.52, (255, 255, 255), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 452, act_y), (cx2 - 24, act_y + 44), (13, 17, 23), -1, radius=8)
    draw_round_rect(img, (cx1 + 452, act_y), (cx2 - 24, act_y + 44), (48, 54, 61), 1, radius=8)
    cv2.putText(img, 'Switch Lens', (cx1 + 510, act_y + 28), cv2.FONT_HERSHEY_DUPLEX, 0.52, (201, 209, 217), 1, cv2.LINE_AA)

    # Bottom Ultra Photo & Lock
    bot_y = act_y + 54
    if highlight_section == "lens":
        draw_round_rect(img, (cx1 + 16, bot_y - 6), (cx2 - 16, bot_y + 44), (88, 166, 255), 2, radius=8)

    draw_round_rect(img, (cx1 + 24, bot_y), (cx1 + 290, bot_y + 38), (218, 90, 42), -1, radius=8)
    cv2.putText(img, 'Ultra Photo (Full Res)', (cx1 + 42, bot_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.50, (255, 255, 255), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 302, bot_y), (cx1 + 510, bot_y + 38), (22, 27, 34), -1, radius=8)
    draw_round_rect(img, (cx1 + 302, bot_y), (cx1 + 510, bot_y + 38), (35, 134, 54), 1, radius=8)
    cv2.putText(img, 'Lock Mode: ON', (cx1 + 338, bot_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.48, (35, 134, 54), 1, cv2.LINE_AA)

    draw_round_rect(img, (cx1 + 522, bot_y), (cx2 - 24, bot_y + 38), (13, 17, 23), -1, radius=8)
    cv2.putText(img, 'Battery Guide', (cx1 + 560, bot_y + 25), cv2.FONT_HERSHEY_DUPLEX, 0.48, (88, 166, 255), 1, cv2.LINE_AA)

    return img

def main():
    screens_config = [
        {
            "num": 1,
            "title": "1080p 60 FPS ULTRA-LOW LATENCY STREAMING",
            "subtitle": "Hardware-accelerated H.264 video pipeline over direct USB ADB tunnel or Wi-Fi",
            "mode": "Meetings",
            "highlight": "transport",
            "vbg": "off",
            "res": "1080p FHD",
            "fps": "60 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "Port: 8089  |  Lens: 0 (BACK)  |  H.264 Hardware Encoded  |  USB ADB Tunnel (Active)"
        },
        {
            "num": 2,
            "title": "PRO MANUAL OPTICS & CAMERA2 CONTROLS",
            "subtitle": "Direct manual ISO (100-3200), Shutter (1/2000s), Exposure EV, and manual focus slider",
            "mode": "Pro Manual",
            "highlight": "optics",
            "vbg": "off",
            "res": "1080p FHD",
            "fps": "60 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "ISO: 400  |  Shutter: 1/250s  |  EV: +0.5  |  AF: Manual Focus Distance 0.35m"
        },
        {
            "num": 3,
            "title": "DUAL VIRTUAL BACKGROUND ENGINE",
            "subtitle": "Real-time background blur & replacement with intelligent PC GPU offload",
            "mode": "Meetings",
            "highlight": "virtual_bg",
            "vbg": "custom",
            "res": "1080p FHD",
            "fps": "60 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "AI Virtual Background: Office Backdrop Loaded  |  Workload: Offloaded to PC GPU"
        },
        {
            "num": 4,
            "title": "8 ONE-TOUCH PURPOSE PRESETS",
            "subtitle": "Instant optimized optical & encoder configurations for Meetings, Streaming, and OCR",
            "mode": "Streaming",
            "highlight": "presets",
            "vbg": "off",
            "res": "1080p FHD",
            "fps": "60 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "Preset: Streaming (OBS Studio / Twitch / YouTube)  |  Bitrate: 8.5 Mbps  |  60 FPS"
        },
        {
            "num": 5,
            "title": "SMART POWER & BATTERY PROTECTION",
            "subtitle": "Screen Keep-ON wake lock control and one-touch OLED dimming for marathon streams",
            "mode": "Online Class",
            "highlight": "power",
            "vbg": "dim",
            "res": "1080p FHD",
            "fps": "30 FPS",
            "lens": "Lens: 1 (FRONT)",
            "footer": "Dim Display Mode Active: Backlight -70%  |  Screen Keep ON Active  |  Battery Cool: 31 C"
        },
        {
            "num": 6,
            "title": "100% PRIVATE ZERO-CLOUD ARCHITECTURE",
            "subtitle": "Strict peer-to-peer streaming directly over local cable or LAN with zero data collection",
            "mode": "Security",
            "highlight": "network",
            "vbg": "off",
            "res": "1080p FHD",
            "fps": "30 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "P2P Direct Sockets: 192.168.1.104:8089  |  Zero Cloud Relays  |  Zero External Telemetry"
        },
        {
            "num": 7,
            "title": "MULTI-LENS SWITCHING & 4K ULTRA PHOTO",
            "subtitle": "Seamlessly toggle Ultra-Wide, Telephoto, and capture uncompressed full-res stills",
            "mode": "Snapshot",
            "highlight": "lens",
            "vbg": "off",
            "res": "4K UHD",
            "fps": "30 FPS",
            "lens": "Lens: 2 (ULTRA-WIDE)",
            "footer": "Sensor: Ultra-Wide (120 FOV)  |  Full-Resolution RAW/JPEG Capture Ready (64 MP)"
        },
        {
            "num": 8,
            "title": "UNIVERSAL COMPATIBILITY FOR PC, OBS & MAC",
            "subtitle": "Native virtual camera driver integration for Zoom, Teams, Google Meet, and OBS Studio",
            "mode": "Meetings",
            "highlight": "transport",
            "vbg": "off",
            "res": "1080p FHD",
            "fps": "60 FPS",
            "lens": "Lens: 0 (BACK)",
            "footer": "Clients Connected: 2 (OBS Studio Virtual Cam + Zoom Client)  |  0 Frame Drops"
        }
    ]

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    dest_dirs = [
        base_dir,
        os.path.join(base_dir, "Stable", "stable_playstore_version"),
        os.path.join(base_dir, "Dev", "android", "app", "src", "main")
    ]

    for cfg in screens_config:
        n = cfg["num"]
        filename = f"playstore_tablet_10inch_screenshot_{n}.png"
        img = render_tablet_screen(
            title_text=cfg["title"],
            subtitle_text=cfg["subtitle"],
            mode_active=cfg["mode"],
            highlight_section=cfg["highlight"],
            virtual_bg_mode=cfg["vbg"],
            res_text=cfg["res"],
            fps_text=cfg["fps"],
            lens_text=cfg["lens"],
            custom_footer=cfg["footer"]
        )

        for d in dest_dirs:
            if os.path.exists(d):
                target_path = os.path.join(d, filename)
                cv2.imwrite(target_path, img)
                file_sz = os.path.getsize(target_path)
                print(f"Rendered {filename} -> {target_path} ({img.shape[1]}x{img.shape[0]}, {file_sz // 1024} KB)")

if __name__ == "__main__":
    main()

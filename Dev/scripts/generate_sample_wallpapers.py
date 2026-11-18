import os
import cv2
import numpy as np

W, H = 1920, 1080

def create_modern_office():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    # Wall gradient (cool slate grey to soft warm navy)
    for y in range(H):
        factor = y / float(H)
        b = int(45 + factor * 20)
        g = int(35 + factor * 15)
        r = int(28 + factor * 10)
        img[y, :] = (b, g, r)
    # Large office window on the right
    win_x1, win_y1, win_x2, win_y2 = int(W * 0.60), 60, W - 60, int(H * 0.75)
    # City sky gradient in window
    for y in range(win_y1, win_y2):
        f = (y - win_y1) / float(win_y2 - win_y1)
        b = int(180 - f * 40)
        g = int(140 - f * 30)
        r = int(110 - f * 25)
        img[y, win_x1:win_x2] = (b, g, r)
    # Window panes / mullions
    cv2.rectangle(img, (win_x1, win_y1), (win_x2, win_y2), (50, 40, 35), 8)
    cv2.line(img, ((win_x1 + win_x2)//2, win_y1), ((win_x1 + win_x2)//2, win_y2), (50, 40, 35), 6)
    cv2.line(img, (win_x1, (win_y1 + win_y2)//2), (win_x2, (win_y1 + win_y2)//2), (50, 40, 35), 6)
    # Left wall acoustic slats
    for px in range(80, int(W * 0.45), 60):
        cv2.rectangle(img, (px, 80), (px + 36, int(H * 0.82)), (30, 22, 18), -1)
    # Warm desk surface on bottom
    for y in range(int(H * 0.82), H):
        f = (y - int(H * 0.82)) / float(H - int(H * 0.82))
        img[y, :] = (int(25 + f * 10), int(35 + f * 15), int(55 + f * 20))
    # Gaussian blur to simulate natural depth of field
    img = cv2.GaussianBlur(img, (45, 45), 0)
    return img

def create_studio_bokeh():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    # Deep charcoal to dark navy gradient
    for y in range(H):
        factor = y / float(H)
        b = int(24 + factor * 14)
        g = int(18 + factor * 8)
        r = int(15 + factor * 6)
        img[y, :] = (b, g, r)
    # Bokeh circles with random subtle glow
    np.random.seed(42)
    colors = [
        (88, 166, 255),   # Cyan
        (255, 166, 88),   # Amber
        (218, 90, 42),    # Warm gold
        (137, 87, 229),   # Soft violet
        (63, 185, 80)     # Emerald
    ]
    overlay = img.copy()
    for _ in range(40):
        cx = np.random.randint(50, W - 50)
        cy = np.random.randint(50, H - 50)
        rad = np.random.randint(35, 140)
        col = colors[np.random.randint(0, len(colors))]
        cv2.circle(overlay, (cx, cy), rad, col, -1)
    # Blend with low alpha for soft bokeh
    cv2.addWeighted(overlay, 0.18, img, 0.82, 0, img)
    img = cv2.GaussianBlur(img, (55, 55), 0)
    return img

def create_minimalist_bookshelf():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    # Warm indoor study room wall
    for y in range(H):
        f = y / float(H)
        img[y, :] = (int(30 + f * 15), int(35 + f * 15), int(42 + f * 18))
    # Bookshelf frames
    shelf_y_positions = [200, 450, 700, 950]
    for sy in shelf_y_positions:
        cv2.rectangle(img, (100, sy), (W - 100, sy + 24), (20, 28, 45), -1)
        # Books on shelf
        bx = 140
        np.random.seed(sy)
        while bx < W - 180:
            bw = np.random.randint(22, 48)
            bh = np.random.randint(120, 210)
            bcol = (np.random.randint(40, 180), np.random.randint(40, 160), np.random.randint(40, 170))
            cv2.rectangle(img, (bx, sy - bh), (bx + bw, sy), bcol, -1)
            bx += bw + np.random.randint(2, 8)
            if np.random.random() < 0.15:
                bx += 40 # Gap between book groups
    img = cv2.GaussianBlur(img, (41, 41), 0)
    return img

def create_cozy_coffee_shop():
    img = np.zeros((H, W, 3), dtype=np.uint8)
    # Warm amber/espresso cafe tones
    for y in range(H):
        f = y / float(H)
        img[y, :] = (int(18 + f * 12), int(28 + f * 18), int(48 + f * 25))
    # Pendant light warm glow circles
    pendant_x = [int(W * 0.25), int(W * 0.50), int(W * 0.75)]
    overlay = img.copy()
    for px in pendant_x:
        # Light wire
        cv2.line(overlay, (px, 0), (px, 220), (40, 40, 40), 2)
        # Hanging warm bulb
        cv2.circle(overlay, (px, 230), 28, (120, 210, 255), -1) # Warm yellow-white
        # Ambient glow
        cv2.circle(overlay, (px, 230), 160, (60, 140, 220), -1)
    cv2.addWeighted(overlay, 0.35, img, 0.65, 0, img)
    # Background brick texture simulation
    for by in range(300, H - 100, 40):
        cv2.line(img, (80, by), (W - 80, by), (25, 35, 55), 2)
    img = cv2.GaussianBlur(img, (49, 49), 0)
    return img

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dirs = [
        os.path.join(base_dir, "Dev", "desktop", "wallpapers"),
        os.path.join(base_dir, "Stable", "Stable_Desktop_Client", "wallpapers")
    ]
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)

    wallpapers = [
        ("modern_office.jpg", create_modern_office),
        ("studio_bokeh.jpg", create_studio_bokeh),
        ("minimalist_bookshelf.jpg", create_minimalist_bookshelf),
        ("cozy_coffee_shop.jpg", create_cozy_coffee_shop)
    ]

    for fname, gen_func in wallpapers:
        img = gen_func()
        for d in out_dirs:
            target = os.path.join(d, fname)
            cv2.imwrite(target, img, [cv2.IMWRITE_JPEG_QUALITY, 92])
            sz = os.path.getsize(target)
            print(f"Generated {fname} -> {target} ({img.shape[1]}x{img.shape[0]}, {sz // 1024} KB)")

if __name__ == "__main__":
    main()

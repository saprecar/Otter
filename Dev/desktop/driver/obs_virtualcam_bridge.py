import ctypes
from ctypes import wintypes
import struct
import time
import numpy as np
import cv2

# [AI-BLOCK: Standalone Native OBS Virtual Camera Shared Memory Bridge]
# Implements the exact IPC shared memory queue protocol used by OBS Studio (plugins/win-dshow/shared-memory-queue.c).
# Outputs directly to the native 'OBS Virtual Camera' DirectShow filter without needing OBS Studio or pyvirtualcam running.

PAGE_READWRITE = 0x04
FILE_MAP_ALL_ACCESS = 0xF001F
FILE_MAP_READ = 0x0004
VIDEO_NAME = "OBSVirtualCamVideo"

SHARED_QUEUE_STATE_INVALID = 0
SHARED_QUEUE_STATE_STARTING = 1
SHARED_QUEUE_STATE_READY = 2
SHARED_QUEUE_STATE_STOPPING = 3
FRAME_HEADER_SIZE = 32

kernel32 = ctypes.windll.kernel32
kernel32.CreateFileMappingW.restype = wintypes.HANDLE
kernel32.CreateFileMappingW.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCWSTR]
kernel32.OpenFileMappingW.restype = wintypes.HANDLE
kernel32.OpenFileMappingW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.MapViewOfFile.restype = ctypes.c_void_p
kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
kernel32.UnmapViewOfFile.restype = wintypes.BOOL
kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

def _align32(size: int) -> int:
    return (size + 31) & (~31)

class OBSVirtualCamBridge:
    """
    Direct shared-memory writer for 'OBS Virtual Camera'.
    Bypasses pyvirtualcam and operates as a standalone producer for the official OBS DirectShow driver.
    """
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.interval = 10_000_000 // fps  # 100ns units
        self.is_connected = False
        self.handle = None
        self.p_buf = None
        self.write_idx = 0
        self.offsets = [0, 0, 0]
        self.frame_size = width * height * 3 // 2  # NV12 format

    def connect(self) -> bool:
        """Create or open the OBSVirtualCamVideo memory-mapped file queue"""
        # Calculate queue layout matching OBS shared-memory-queue.c
        header_size = _align32(76)  # sizeof(struct queue_header)
        size = header_size
        for i in range(3):
            self.offsets[i] = size
            size = _align32(size + self.frame_size + FRAME_HEADER_SIZE)
        total_size = size

        # Try to open existing or create new mapping
        self.handle = kernel32.OpenFileMappingW(FILE_MAP_ALL_ACCESS, False, VIDEO_NAME)
        if not self.handle:
            self.handle = kernel32.CreateFileMappingW(
                wintypes.HANDLE(-1),
                None,
                PAGE_READWRITE,
                0,
                total_size,
                VIDEO_NAME
            )

        if not self.handle:
            return False

        self.p_buf = kernel32.MapViewOfFile(self.handle, FILE_MAP_ALL_ACCESS, 0, 0, 0)
        if not self.p_buf:
            self.close()
            return False

        # Pack header:
        # volatile uint32_t write_idx (0)
        # volatile uint32_t read_idx (0)
        # volatile uint32_t state (SHARED_QUEUE_STATE_STARTING = 1)
        # uint32_t offsets[3]
        # uint32_t type (0)
        # uint32_t cx
        # uint32_t cy
        # uint64_t interval
        # uint32_t reserved[8]
        header = struct.pack(
            "<III3IIIIQ8I",
            0, # write_idx
            0, # read_idx
            SHARED_QUEUE_STATE_STARTING, # state
            self.offsets[0], self.offsets[1], self.offsets[2],
            0, # type: SHARED_QUEUE_TYPE_VIDEO
            self.width,
            self.height,
            self.interval,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        ctypes.memmove(self.p_buf, header, len(header))
        self.is_connected = True
        return True

    def _bgr_to_nv12(self, frame_bgr: np.ndarray) -> bytes:
        """Convert BGR OpenCV image to NV12 byte stream (Y plane + interleaved UV plane)"""
        h, w = frame_bgr.shape[:2]
        yuv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2YUV_I420)
        # In OpenCV I420 layout:
        # Rows 0..h-1 is Y (h x w)
        # Rows h..h + h//4 - 1 is U (h//4 x w == h//2 x w//2)
        # Rows h + h//4..end is V (h//4 x w == h//2 x w//2)
        y_bytes = yuv[:h, :].tobytes()
        u = yuv[h : h + h // 4, :].reshape((h // 2, w // 2))
        v = yuv[h + h // 4 :, :].reshape((h // 2, w // 2))
        uv = np.empty((h // 2, w), dtype=np.uint8)
        uv[:, 0::2] = u
        uv[:, 1::2] = v
        return y_bytes + uv.tobytes()

    def send_frame(self, frame_bgr: np.ndarray) -> bool:
        """Write frame into the ring buffer slot and advance index"""
        if not self.is_connected or not self.p_buf:
            if not self.connect():
                return False

        # Resize if dimensions differ
        h, w = frame_bgr.shape[:2]
        if w != self.width or h != self.height:
            frame_bgr = cv2.resize(frame_bgr, (self.width, self.height))

        nv12_bytes = self._bgr_to_nv12(frame_bgr)
        self.write_idx += 1
        idx = self.write_idx % 3
        slot_offset = self.offsets[idx]

        # Timestamp in 100ns units
        ts = int(time.time() * 10_000_000)
        ts_bytes = struct.pack("<Q", ts)

        # Write timestamp at frame header offset
        ctypes.memmove(self.p_buf + slot_offset, ts_bytes, len(ts_bytes))
        # Write NV12 frame data right after frame header (offset 32)
        ctypes.memmove(self.p_buf + slot_offset + FRAME_HEADER_SIZE, nv12_bytes, len(nv12_bytes))

        # Update write_idx, read_idx, and state in queue_header
        # write_idx is at offset 0 (uint32)
        # read_idx is at offset 4 (uint32)
        # state is at offset 8 (uint32)
        indices_state = struct.pack("<III", self.write_idx, self.write_idx, SHARED_QUEUE_STATE_READY)
        ctypes.memmove(self.p_buf, indices_state, len(indices_state))

        return True

    def close(self):
        if self.p_buf:
            # Mark queue stopping before detaching
            try:
                stop_state = struct.pack("<I", SHARED_QUEUE_STATE_STOPPING)
                ctypes.memmove(self.p_buf + 8, stop_state, 4)
            except Exception:
                pass
            kernel32.UnmapViewOfFile(self.p_buf)
            self.p_buf = None
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None
        self.is_connected = False

import ctypes
from ctypes import wintypes
import struct
import numpy as np

# [AI-BLOCK: Standalone Native DirectShow Shared Memory Virtual Camera Bridge]

PAGE_READWRITE = 0x04
FILE_MAP_WRITE = 0x0002
FILE_MAP_ALL_ACCESS = 0x001F001F
SYNCHRONIZE = 0x00100000
EVENT_MODIFY_STATE = 0x0002
INFINITE = 0xFFFFFFFF
WAIT_OBJECT_0 = 0x00000000
MAX_SHARED_IMAGE_SIZE = 3840 * 2160 * 4 * 2 # 4K max buffer

kernel32 = ctypes.windll.kernel32

class UnityCaptureSharedMemory:
    """
    Direct interface with the Windows DirectShow virtual camera driver (UnityCaptureFilter).
    Bypasses pyvirtualcam and Python C++ compilation completely.
    Streams frames directly into Windows kernel/subsystem shared memory.
    """
    def __init__(self, cap_num=0):
        self.cap_num = cap_num
        self.is_connected = False
        self.h_mutex = None
        self.h_want_event = None
        self.h_sent_event = None
        self.h_shared_file = None
        self.p_buf = None

        cap_char = chr(ord('0') + cap_num) if cap_num > 0 else ""
        self.name_mutex = f"UnityCapture_Mutx{cap_char}".encode("ascii")
        self.name_want = f"UnityCapture_Want{cap_char}".encode("ascii")
        self.name_sent = f"UnityCapture_Sent{cap_char}".encode("ascii")
        self.name_data = f"UnityCapture_Data{cap_char}".encode("ascii")

    def connect(self) -> bool:
        """Connect to the DirectShow filter shared memory created during camera open"""
        # 1. Mutex
        self.h_mutex = kernel32.OpenMutexA(SYNCHRONIZE, False, self.name_mutex)
        if not self.h_mutex:
            # Create if filter hasn't started yet
            self.h_mutex = kernel32.CreateMutexA(None, False, self.name_mutex)
        if not self.h_mutex:
            return False

        # 2. Want Frame Event
        self.h_want_event = kernel32.CreateEventA(None, False, False, self.name_want)
        # 3. Sent Frame Event
        self.h_sent_event = kernel32.OpenEventA(EVENT_MODIFY_STATE, False, self.name_sent)
        if not self.h_sent_event:
            self.h_sent_event = kernel32.CreateEventA(None, False, False, self.name_sent)

        # 4. Shared Memory Buffer
        self.h_shared_file = kernel32.OpenFileMappingA(FILE_MAP_WRITE, False, self.name_data)
        if not self.h_shared_file:
            # Pre-allocate buffer so filter binds immediately upon activation
            header_size = 32
            total_size = header_size + MAX_SHARED_IMAGE_SIZE
            self.h_shared_file = kernel32.CreateFileMappingA(
                -1, None, PAGE_READWRITE, 0, total_size, self.name_data
            )

        if not self.h_shared_file:
            self.close()
            return False

        self.p_buf = kernel32.MapViewOfFile(self.h_shared_file, FILE_MAP_WRITE, 0, 0, 0)
        if not self.p_buf:
            self.close()
            return False

        self.is_connected = True
        return True

    def send_frame(self, frame_bgr: np.ndarray, timeout_ms: int = 1000) -> bool:
        """
        Write frame directly into Windows DirectShow shared memory buffer.
        Accepts BGR frame (standard OpenCV format).
        """
        if not self.is_connected or not self.p_buf:
            if not self.connect():
                return False

        h, w = frame_bgr.shape[:2]
        stride = w * 4  # RGBA / BGRA 4 bytes per pixel

        # Convert BGR to BGRA
        if frame_bgr.shape[2] == 3:
            frame_bgra = np.empty((h, w, 4), dtype=np.uint8)
            frame_bgra[:, :, :3] = frame_bgr
            frame_bgra[:, :, 3] = 255
        else:
            frame_bgra = frame_bgr

        data_bytes = frame_bgra.tobytes()
        data_len = len(data_bytes)

        # Header packing (32 bytes):
        # DWORD maxSize (4), int width (4), int height (4), int stride (4),
        # int format (4: 0=FORMAT_UINT8), int resizemode (4: 1=linear),
        # int mirrormode (4: 0=disabled), int timeout (4)
        header = struct.pack(
            "<Iiiiiiii",
            MAX_SHARED_IMAGE_SIZE,
            w,
            h,
            stride,
            0, # FORMAT_UINT8
            1, # RESIZEMODE_LINEAR
            0, # MIRRORMODE_DISABLED
            timeout_ms
        )

        # Lock mutex
        kernel32.WaitForSingleObject(self.h_mutex, INFINITE)
        try:
            # Write header
            ctypes.memmove(self.p_buf, header, len(header))
            # Write pixel data right after header
            ctypes.memmove(self.p_buf + len(header), data_bytes, data_len)
        finally:
            kernel32.ReleaseMutex(self.h_mutex)

        # Signal that a new frame has been sent
        if self.h_sent_event:
            kernel32.SetEvent(self.h_sent_event)

        return True

    def close(self):
        if self.p_buf:
            kernel32.UnmapViewOfFile(self.p_buf)
            self.p_buf = None
        if self.h_shared_file:
            kernel32.CloseHandle(self.h_shared_file)
            self.h_shared_file = None
        if self.h_mutex:
            kernel32.CloseHandle(self.h_mutex)
            self.h_mutex = None
        if self.h_want_event:
            kernel32.CloseHandle(self.h_want_event)
            self.h_want_event = None
        if self.h_sent_event:
            kernel32.CloseHandle(self.h_sent_event)
            self.h_sent_event = None
        self.is_connected = False

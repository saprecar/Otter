import ctypes
from ctypes import wintypes
import struct
import numpy as np

# [AI-BLOCK: Standalone Native DirectShow Shared Memory Virtual Camera Bridge]

PAGE_READWRITE = 0x04
FILE_MAP_WRITE = 0x0002
SYNCHRONIZE = 0x00100000
EVENT_MODIFY_STATE = 0x0002
INFINITE = 0xFFFFFFFF
MAX_SHARED_IMAGE_SIZE = 3840 * 2160 * 4 * 2 # 4K buffer limit

kernel32 = ctypes.windll.kernel32
kernel32.CreateFileMappingA.restype = wintypes.HANDLE
kernel32.CreateFileMappingA.argtypes = [wintypes.HANDLE, ctypes.c_void_p, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, wintypes.LPCSTR]
kernel32.OpenFileMappingA.restype = wintypes.HANDLE
kernel32.OpenFileMappingA.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCSTR]
kernel32.MapViewOfFile.restype = ctypes.c_void_p
kernel32.MapViewOfFile.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD, ctypes.c_size_t]
kernel32.UnmapViewOfFile.restype = wintypes.BOOL
kernel32.UnmapViewOfFile.argtypes = [ctypes.c_void_p]
kernel32.CreateMutexA.restype = wintypes.HANDLE
kernel32.CreateMutexA.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCSTR]
kernel32.OpenMutexA.restype = wintypes.HANDLE
kernel32.OpenMutexA.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCSTR]
kernel32.CreateEventA.restype = wintypes.HANDLE
kernel32.CreateEventA.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCSTR]
kernel32.OpenEventA.restype = wintypes.HANDLE
kernel32.OpenEventA.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCSTR]
kernel32.SetEvent.argtypes = [wintypes.HANDLE]
kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.ReleaseMutex.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

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

        # For CapNum 0: exact name string terminates before the trailing '0' (compat with original filter)
        cap_suffix = chr(ord('0') + cap_num) if cap_num > 0 else ""
        self.name_mutex = f"UnityCapture_Mutx{cap_suffix}".encode("ascii")
        self.name_want = f"UnityCapture_Want{cap_suffix}".encode("ascii")
        self.name_sent = f"UnityCapture_Sent{cap_suffix}".encode("ascii")
        self.name_data = f"UnityCapture_Data{cap_suffix}".encode("ascii")

    def connect(self) -> bool:
        """Connect to the DirectShow filter shared memory created during camera open"""
        # 1. Mutex
        self.h_mutex = kernel32.OpenMutexA(SYNCHRONIZE, False, self.name_mutex)
        if not self.h_mutex:
            self.h_mutex = kernel32.CreateMutexA(None, False, self.name_mutex)
        if not self.h_mutex:
            return False

        # 2. Want Frame Event (filter creates to signal it wants frames)
        self.h_want_event = kernel32.OpenEventA(EVENT_MODIFY_STATE, False, self.name_want)
        if not self.h_want_event:
            self.h_want_event = kernel32.CreateEventA(None, False, False, self.name_want)

        # 3. Sent Frame Event (sender signals to notify receiver new frame is ready)
        self.h_sent_event = kernel32.OpenEventA(EVENT_MODIFY_STATE, False, self.name_sent)
        if not self.h_sent_event:
            self.h_sent_event = kernel32.CreateEventA(None, False, False, self.name_sent)

        # 4. Shared Memory Buffer
        self.h_shared_file = kernel32.OpenFileMappingA(FILE_MAP_WRITE, False, self.name_data)
        if not self.h_shared_file:
            header_size = 32
            total_size = header_size + MAX_SHARED_IMAGE_SIZE
            self.h_shared_file = kernel32.CreateFileMappingA(
                wintypes.HANDLE(-1), None, PAGE_READWRITE, 0, total_size, self.name_data
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

    def send_frame(self, frame_bgr: np.ndarray, timeout_ms: int = 2000) -> bool:
        """
        Write frame directly into Windows DirectShow shared memory buffer.
        Accepts BGR frame (standard OpenCV format).
        Converts to RGBA and sets stride = width (pixel stride).
        """
        if not self.is_connected or not self.p_buf:
            if not self.connect():
                return False

        h, w = frame_bgr.shape[:2]
        # In UnityCapture, stride is row stride in PIXELS (not bytes)
        stride = w

        # Convert BGR to RGBA (FORMAT_UINT8 in UnityCapture is 8-bit RGBA)
        if frame_bgr.shape[2] == 3:
            import cv2
            frame_rgba = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGBA)
        else:
            frame_rgba = frame_bgr

        data_bytes = frame_rgba.tobytes()
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
            0, # FORMAT_UINT8 (RGBA)
            1, # RESIZEMODE_LINEAR
            0, # MIRRORMODE_DISABLED
            timeout_ms
        )

        # Lock mutex
        kernel32.WaitForSingleObject(self.h_mutex, INFINITE)
        try:
            # Write header
            ctypes.memmove(self.p_buf, header, len(header))
            # Write pixel data right after header (offset 32)
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

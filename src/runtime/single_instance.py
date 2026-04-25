from __future__ import annotations

import ctypes
import logging
import sys
import threading
import time
from ctypes import wintypes

logger = logging.getLogger(__name__)

IS_WINDOWS = sys.platform.startswith("win")

_ERROR_ALREADY_EXISTS = 183
_EVENT_MODIFY_STATE = 0x0002
_GW_OWNER = 4
_SW_RESTORE = 9
_SW_SHOW = 5
_WAIT_OBJECT_0 = 0x00000000
_WAIT_TIMEOUT = 0x00000102
_WAIT_FAILED = 0xFFFFFFFF
_ASFW_ANY = 0xFFFFFFFF

if IS_WINDOWS:
    _kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    _user32 = ctypes.WinDLL("user32", use_last_error=True)

    _kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.CreateMutexW.restype = wintypes.HANDLE
    _kernel32.CreateEventW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.CreateEventW.restype = wintypes.HANDLE
    _kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    _kernel32.OpenEventW.restype = wintypes.HANDLE
    _kernel32.SetEvent.argtypes = [wintypes.HANDLE]
    _kernel32.SetEvent.restype = wintypes.BOOL
    _kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    _kernel32.WaitForSingleObject.restype = wintypes.DWORD
    _kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    _kernel32.CloseHandle.restype = wintypes.BOOL
    _kernel32.GetCurrentProcessId.argtypes = []
    _kernel32.GetCurrentProcessId.restype = wintypes.DWORD

    _enum_windows_proc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    _user32.EnumWindows.argtypes = [_enum_windows_proc, wintypes.LPARAM]
    _user32.EnumWindows.restype = wintypes.BOOL
    _user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    _user32.GetWindowThreadProcessId.restype = wintypes.DWORD
    _user32.IsWindowVisible.argtypes = [wintypes.HWND]
    _user32.IsWindowVisible.restype = wintypes.BOOL
    _user32.IsIconic.argtypes = [wintypes.HWND]
    _user32.IsIconic.restype = wintypes.BOOL
    _user32.ShowWindowAsync.argtypes = [wintypes.HWND, ctypes.c_int]
    _user32.ShowWindowAsync.restype = wintypes.BOOL
    _user32.BringWindowToTop.argtypes = [wintypes.HWND]
    _user32.BringWindowToTop.restype = wintypes.BOOL
    _user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    _user32.SetForegroundWindow.restype = wintypes.BOOL
    _user32.GetWindow.argtypes = [wintypes.HWND, ctypes.c_uint]
    _user32.GetWindow.restype = wintypes.HWND
    _user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
    _user32.GetWindowTextLengthW.restype = ctypes.c_int
    _user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    _user32.GetWindowTextW.restype = ctypes.c_int
    _user32.AllowSetForegroundWindow.argtypes = [wintypes.DWORD]
    _user32.AllowSetForegroundWindow.restype = wintypes.BOOL


class SingleInstanceManager:
    def __init__(self, app_id: str, window_title: str) -> None:
        self.app_id = app_id
        self.window_title = window_title.strip()
        self._mutex_name = f"Local\\{app_id}.Mutex"
        self._event_name = f"Local\\{app_id}.Activate"
        self._mutex_handle: int | None = None
        self._activation_event_handle: int | None = None
        self._listener_thread: threading.Thread | None = None
        self._stop_event = threading.Event()

    def acquire_or_activate_existing(self) -> bool:
        if not IS_WINDOWS:
            return True

        mutex_handle = _kernel32.CreateMutexW(None, False, self._mutex_name)
        if not mutex_handle:
            raise OSError("Could not create the single-instance mutex.")

        if ctypes.get_last_error() == _ERROR_ALREADY_EXISTS:
            self._close_handle(int(mutex_handle))
            self._signal_existing_instance()
            return False

        self._mutex_handle = int(mutex_handle)

        event_handle = _kernel32.CreateEventW(None, False, False, self._event_name)
        if not event_handle:
            self.release()
            raise OSError("Could not create the instance activation event.")

        self._activation_event_handle = int(event_handle)
        return True

    def start_listener(self) -> None:
        if not IS_WINDOWS or not self._activation_event_handle or self._listener_thread:
            return

        self._listener_thread = threading.Thread(
            target=self._listen_for_activation_requests,
            name="single-instance-listener",
            daemon=True,
        )
        self._listener_thread.start()

    def release(self) -> None:
        if not IS_WINDOWS:
            return

        self._stop_event.set()

        if self._activation_event_handle:
            _kernel32.SetEvent(self._activation_event_handle)

        if self._listener_thread and self._listener_thread.is_alive() and threading.current_thread() is not self._listener_thread:
            self._listener_thread.join(timeout=2.0)

        self._listener_thread = None
        self._close_handle(self._activation_event_handle)
        self._close_handle(self._mutex_handle)
        self._activation_event_handle = None
        self._mutex_handle = None

    def _signal_existing_instance(self) -> None:
        logger.info("Application is already running. Requesting focus for the existing instance.")

        if not IS_WINDOWS:
            return

        _user32.AllowSetForegroundWindow(_ASFW_ANY)

        event_handle = _kernel32.OpenEventW(_EVENT_MODIFY_STATE, False, self._event_name)
        if not event_handle:
            logger.warning("Could not find the existing instance event.")
            return

        try:
            _kernel32.SetEvent(event_handle)
        finally:
            self._close_handle(int(event_handle))

    def _listen_for_activation_requests(self) -> None:
        if not self._activation_event_handle:
            return

        while not self._stop_event.is_set():
            wait_result = _kernel32.WaitForSingleObject(self._activation_event_handle, 500)

            if self._stop_event.is_set():
                return

            if wait_result == _WAIT_TIMEOUT:
                continue

            if wait_result == _WAIT_FAILED:
                logger.warning("Failed while waiting for the instance activation event.")
                return

            if wait_result == _WAIT_OBJECT_0:
                self._restore_existing_window()

    def _restore_existing_window(self) -> None:
        for _ in range(24):
            hwnd = self._find_main_window()
            if hwnd:
                if _user32.IsIconic(hwnd):
                    _user32.ShowWindowAsync(hwnd, _SW_RESTORE)
                else:
                    _user32.ShowWindowAsync(hwnd, _SW_SHOW)

                _user32.BringWindowToTop(hwnd)
                _user32.SetForegroundWindow(hwnd)
                logger.info("Existing instance activated.")
                return

            time.sleep(0.25)

        logger.warning("Could not find the main window to activate.")

    def _find_main_window(self) -> int | None:
        if not IS_WINDOWS:
            return None

        current_pid = _kernel32.GetCurrentProcessId()
        windows: list[int] = []

        @_enum_windows_proc
        def enum_windows_callback(hwnd: int, _: int) -> bool:
            if _user32.GetWindow(hwnd, _GW_OWNER):
                return True

            process_id = wintypes.DWORD()
            _user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            if process_id.value != current_pid:
                return True

            if not _user32.IsWindowVisible(hwnd):
                return True

            windows.append(int(hwnd))
            return True

        _user32.EnumWindows(enum_windows_callback, 0)

        if not windows:
            return None

        expected_title = self.window_title.casefold()
        for hwnd in windows:
            title = self._get_window_title(hwnd).casefold()
            if title == expected_title or expected_title in title:
                return hwnd

        return windows[0]

    def _get_window_title(self, hwnd: int) -> str:
        title_length = _user32.GetWindowTextLengthW(hwnd)
        if title_length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(title_length + 1)
        _user32.GetWindowTextW(hwnd, buffer, len(buffer))
        return buffer.value

    def _close_handle(self, handle: int | None) -> None:
        if IS_WINDOWS and handle:
            _kernel32.CloseHandle(handle)

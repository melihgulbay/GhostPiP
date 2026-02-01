import ctypes
from ctypes import wintypes
import time

# Win32 Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
LWA_ALPHA = 0x00000002

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def get_window_title(hwnd):
    length = user32.GetWindowTextLengthW(hwnd)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buff, length + 1)
    return buff.value

def find_pip_windows():
    """Finds window handles for Picture-in-Picture windows."""
    pip_hwnds = []
    
    def enum_handler(hwnd, lParam):
        if user32.IsWindowVisible(hwnd):
            title = get_window_title(hwnd)
            # Chrome/Edge use "Picture-in-Picture" (English) or "Resim içinde resim" (Turkish)
            keywords = ["Picture-in-Picture", "Resim içinde resim"]
            if any(k in title for k in keywords):
                pip_hwnds.append(hwnd)
        return True

    ENUM_WINDOWS_PROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(ENUM_WINDOWS_PROC(enum_handler), 0)
    return pip_hwnds

def apply_click_through(hwnd, enable=True, alpha=255):
    """Applies or removes the click-through style (WS_EX_TRANSPARENT)."""
    styles = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    
    if enable:
        # Add WS_EX_LAYERED and WS_EX_TRANSPARENT
        new_styles = styles | WS_EX_LAYERED | WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_styles)
        # Set opacity (0-255)
        user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
    else:
        # Remove WS_EX_LAYERED and WS_EX_TRANSPARENT
        new_styles = styles & ~WS_EX_LAYERED & ~WS_EX_TRANSPARENT
        user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_styles)
        # Reset to fully opaque when disabled (optional but safer)
        user32.SetLayeredWindowAttributes(hwnd, 0, 255, LWA_ALPHA)

    # Force a redraw
    user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x0020 | 0x0002 | 0x0001 | 0x0004)

if __name__ == "__main__":
    # Quick test logic
    print("Searching for PiP windows...")
    hwnds = find_pip_windows()
    if not hwnds:
        print("No PiP windows found.")
    for h in hwnds:
        print(f"Found PiP Window: {get_window_title(h)} (HWND: {h})")
        print("Applying click-through...")
        apply_click_through(h, True)
        time.sleep(5)
        print("Restoring interaction...")
        apply_click_through(h, False)

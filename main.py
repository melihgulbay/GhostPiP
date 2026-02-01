import flet as ft
import threading
import time
import asyncio
import atexit
from pip_manager import find_pip_windows, apply_click_through, get_window_title

class PiPApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "PiP Collision Lock Pro"
        self.page.window_width = 400
        self.page.window_height = 550
        self.page.window_resizable = False
        self.page.window_prevent_close = True
        self.page.on_window_event = self.on_window_event
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.bgcolor = "#0F172A"  # Deep Slate
        self.page.padding = 20
        self.page.vertical_alignment = ft.MainAxisAlignment.START
        
        # State
        self.is_active = False
        self.opacity_val = 255
        self.managed_hwnds = set()
        
        self.setup_ui()
        
        # Cleanup on exit (atexit for terminal close / crash)
        atexit.register(self.restore_all)
        
        # Background loop
        self.stop_loop = False
        threading.Thread(target=self.scan_loop_threaded, daemon=True).start()

    def setup_ui(self):
        # Header
        self.header = ft.Column(
            [
                ft.Row(
                    [
                        ft.Icon(ft.Icons.VIDEOCAM_ROUNDED, color="#818CF8", size=30),
                        ft.Text("PiP Controller", size=24, weight=ft.FontWeight.BOLD),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Text("Premium Collision Shield", color="#94A3B8", size=14),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
        )

        # Status Card
        self.status_text = ft.Text("INACTIVE", size=16, weight=ft.FontWeight.BOLD, color="#F87171")
        self.status_icon = ft.Icon(ft.Icons.SHIELD_OUTLINED, color="#F87171")
        
        self.status_card = ft.Container(
            content=ft.Row(
                [
                    self.status_icon,
                    ft.Text("System Status:", size=16, color="#E2E8F0"),
                    ft.VerticalDivider(),
                    self.status_text,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=20,
            bgcolor="#1E293B",
            border_radius=15,
            shadow=ft.BoxShadow(blur_radius=10, color="#10000000"),
        )

        # Controls Card
        self.opacity_slider = ft.Slider(
            min=50, max=255, value=255,
            active_color="#818CF8",
            on_change=self.on_opacity_change,
        )
        
        self.windows_count_text = ft.Text("0 Windows Detected", size=14, color="#94A3B8")

        self.controls_card = ft.Container(
            content=ft.Column(
                [
                    ft.Text("Window Opacity", size=14, weight=ft.FontWeight.BOLD, color="#E2E8F0"),
                    self.opacity_slider,
                    ft.Divider(height=10, color="#334155"),
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.LAYERS_ROUNDED, size=18, color="#94A3B8"),
                            self.windows_count_text,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                ],
                spacing=15,
            ),
            padding=20,
            bgcolor="#1E293B",
            border_radius=15,
        )

        # Action Button
        self.toggle_btn = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.LOCK_ROUNDED, size=20),
                    ft.Text("ACTIVATE LOCK", size=16, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10,
            ),
            style=ft.ButtonStyle(
                color="#FFFFFF",
                bgcolor="#4F46E5",
                padding=20,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            on_click=self.toggle_lock,
            width=400,
        )

        # Build Main View
        self.page.add(
            self.header,
            ft.Container(height=20),
            self.status_card,
            ft.Container(height=10),
            self.controls_card,
            ft.Container(height=20),
            self.toggle_btn,
            ft.Container(expand=True),
            ft.Text("v2.0.0 - Powered by Flet", size=10, color="#475569", text_align=ft.TextAlign.CENTER),
        )

    def on_window_event(self, e):
        if e.data == "close":
            self.stop_loop = True
            self.restore_all()
            self.page.window_destroy()

    def on_opacity_change(self, e):
        self.opacity_val = int(e.control.value)
        if self.is_active:
            for hwnd in list(self.managed_hwnds):
                try:
                    apply_click_through(hwnd, True, self.opacity_val)
                except:
                    pass

    def toggle_lock(self, e):
        self.is_active = not self.is_active
        if self.is_active:
            self.status_text.value = "ACTIVE"
            self.status_text.color = "#4ADE80"
            self.status_icon.name = ft.Icons.SHIELD_ROUNDED
            self.status_icon.color = "#4ADE80"
            self.toggle_btn.bgcolor = "#15803D"
            self.toggle_btn.content.controls[1].value = "DEACTIVATE LOCK"
            self.toggle_btn.content.controls[0].name = ft.Icons.LOCK_OPEN_ROUNDED
            self.apply_to_current()
        else:
            self.status_text.value = "INACTIVE"
            self.status_text.color = "#F87171"
            self.status_icon.name = ft.Icons.SHIELD_OUTLINED
            self.status_icon.color = "#F87171"
            self.toggle_btn.bgcolor = "#4F46E5"
            self.toggle_btn.content.controls[1].value = "ACTIVATE LOCK"
            self.toggle_btn.content.controls[0].name = ft.Icons.LOCK_ROUNDED
            self.restore_all()
        
        self.page.update()

    def apply_to_current(self):
        hwnds = find_pip_windows()
        for hwnd in hwnds:
            if hwnd not in self.managed_hwnds:
                apply_click_through(hwnd, True, self.opacity_val)
                self.managed_hwnds.add(hwnd)

    def restore_all(self):
        for hwnd in list(self.managed_hwnds):
            try:
                apply_click_through(hwnd, False)
            except:
                pass
        self.managed_hwnds.clear()

    def scan_loop_threaded(self):
        while not self.stop_loop:
            hwnds = find_pip_windows()
            count = len(hwnds)
            
            # Update UI from thread safely
            def update_ui():
                self.windows_count_text.value = f"{count} {'Window' if count == 1 else 'Windows'} Detected"
                self.page.update()
            
            # Safely schedule UI update
            try:
                # We can't call page.update() directly from thread without issues sometimes
                # But Flet handles it okay if triggered correctly, 
                # or we use page.run_task / asyncio.run_coroutine_threadsafe
                self.windows_count_text.value = f"{count} {'Window' if count == 1 else 'Windows'} Detected"
                
                if self.is_active:
                    for hwnd in hwnds:
                        if hwnd not in self.managed_hwnds:
                            apply_click_through(hwnd, True, self.opacity_val)
                            self.managed_hwnds.add(hwnd)
                    
                    # Cleanup stale
                    current_set = set(hwnds)
                    self.managed_hwnds = self.managed_hwnds.intersection(current_set)
                
                self.page.update()
            except:
                pass
            
            time.sleep(1)

def main(page: ft.Page):
    PiPApp(page)

if __name__ == "__main__":
    ft.app(target=main)

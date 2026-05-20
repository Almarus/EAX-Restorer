import customtkinter as ctk
from customtkinter import filedialog
import tkinter as tk
from tkinter import messagebox
import asyncio
import os
import sys
import shutil
import tempfile
import threading
import json
import ssl
import logging
import subprocess
import ctypes
import webbrowser
import urllib.parse
from PIL import Image
import win32ui
import win32gui
import win32con
import win32api

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

ssl._create_default_https_context = ssl._create_unverified_context
import aiohttp

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

DSOAL_FILES = ["alsoft.ini", "dsoal-aldrv.dll", "dsound.dll"]
DSOAL64_FOLDER = "DSOAL64"
OPENAL_DLL = "openal32.dll"

NATIVE_OPENAL_EXES = {
    "xr_3da.exe", "xrengine.exe", "anomalydx11.exe", "anomalydx9.exe",
    "anomalydx10.exe", "anomalyavx.exe", "doom3.exe", "quake4.exe",
    "prey.exe", "etqw.exe", "bf2.exe", "bf2142.exe", "dirt.exe",
    "dirt2.exe", "dirt3.exe", "dirt_showdown.exe", "grid.exe",
    "ofdr.exe", "ofrr.exe", "f1_2010.exe", "f1_2011.exe",
    "penumbra.exe", "amnesia.exe", "ut2004.exe", "ut3.exe",
    "masseffect.exe", "mirrorsedge.exe", "ffow.exe", "r6vegas.exe",
    "r6vegas2.exe", "bioshock.exe", "hourofvictory.exe",
    "elmatador.exe", "alphaprime.exe", "kaneandlynch.exe",
    "coldwar.exe", "psychonauts.exe", "precursor.exe",
    "ostrov.exe", "vivisector.exe", "cryostasis.exe",
    "precursors.exe", "xenus2.exe", "gorkyzero.exe",
    "aurorawatching.exe", "samhd.exe", "arx.exe", "doom3bfg.exe",
    "eduke32.exe", "gzdoom.exe", "zandronum.exe", "openmw.exe",
    "thief.exe", "thief2.exe", "shock2.exe",
}

_icon_cache = {}

# ---------- Определение языка ----------
def get_system_language():
    try:
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return 'ru' if lang_id in (1049, 1059) else 'en'
    except:
        return 'en'

LANG = get_system_language()

TEXTS = {
    'ru': {
        'title': "EAX Restorer",
        'install_title': "Установка OpenAL",
        'install_status': "Установка OpenAL...",
        'info_title': "EAX Restorer — Информация",
        'info_file_not_found': "Файл Info.txt не найден.",
        'close': "Закрыть",
        'click_for_help': "Нажмите для справки",
        'add_game': "➕ Добавить игру",
        'available_games': "📂 Доступные игры",
        'right_click_menu': "ПКМ — меню",
        'eax_activated': "✅ EAX активирован",
        'empty_left': "Список пуст\nНажмите «Добавить игру»",
        'empty_right': "Нет игр с EAX\nПереместите стрелкой →",
        'openal_required': "Требуется OpenAL",
        'openal_desc': "Для объёмного звука EAX необходимо установить OpenAL.",
        'download_install': "Скачать и установить",
        'no': "Нет",
        'dont_show': "Больше не показывать",
        'install_success': "OpenAL успешно установлен!",
        'install_warning': "Установщик запущен. Возможно, потребуется перезагрузка.",
        'install_error': "Не удалось запустить установщик.\nПопробуйте запустить программу от имени администратора.",
        'download_error': "Ошибка скачивания: HTTP {0}",
        'installer_not_found': "Установщик не найден",
        'error': "Ошибка",
        'success': "Успех",
        'attention': "Внимание",
        'activate_success': "EAX активирован для «{0}»\n(Метод: {1})",
        'deactivate_success': "EAX деактивирован для «{0}»",
        'run_game': "🚀 Запустить игру",
        'learn_eax': "🔍 Узнать о поддержке EAX",
        'use_dsoal': "🔧 Использовать DSOAL (32-bit)",
        'use_dsoal64': "🔧 Использовать DSOAL64 (64-bit)",
        'use_openal': "🔊 Использовать OpenAL",
        'delete': "🗑️ Удалить из списка",
        'no_admin': "Недостаточно прав",
        'admin_prompt': "Папка '{0}' защищена.\nДля копирования файлов нужны права администратора.\nПерезапустить программу от имени администратора?",
        'restart_failed': "Не удалось получить права администратора",
        'file_not_found_err': "Файл не найден:\n{0}",
        'launch_error': "Ошибка запуска",
    },
    'en': {
        'title': "EAX Restorer",
        'install_title': "OpenAL Installation",
        'install_status': "Installing OpenAL...",
        'info_title': "EAX Restorer — Info",
        'info_file_not_found': "Info.txt file not found.",
        'close': "Close",
        'click_for_help': "Click for help",
        'add_game': "➕ Add game",
        'available_games': "📂 Available games",
        'right_click_menu': "RMB — menu",
        'eax_activated': "✅ EAX activated",
        'empty_left': "List is empty\nPress «Add game»",
        'empty_right': "No games with EAX\nMove with arrow →",
        'openal_required': "OpenAL required",
        'openal_desc': "For EAX 3D audio you need to install OpenAL.",
        'download_install': "Download and install",
        'no': "No",
        'dont_show': "Don't show again",
        'install_success': "OpenAL successfully installed!",
        'install_warning': "Installer launched. A reboot may be required.",
        'install_error': "Failed to run installer.\nTry running the program as administrator.",
        'download_error': "Download error: HTTP {0}",
        'installer_not_found': "Installer not found",
        'error': "Error",
        'success': "Success",
        'attention': "Attention",
        'activate_success': "EAX activated for «{0}»\n(Method: {1})",
        'deactivate_success': "EAX deactivated for «{0}»",
        'run_game': "🚀 Run game",
        'learn_eax': "🔍 Learn about EAX support",
        'use_dsoal': "🔧 Use DSOAL (32-bit)",
        'use_dsoal64': "🔧 Use DSOAL64 (64-bit)",
        'use_openal': "🔊 Use OpenAL",
        'delete': "🗑️ Delete from list",
        'no_admin': "Insufficient rights",
        'admin_prompt': "Folder '{0}' is protected.\nCopying files requires administrator rights.\nRestart the program as administrator?",
        'restart_failed': "Failed to obtain administrator rights",
        'file_not_found_err': "File not found:\n{0}",
        'launch_error': "Launch error",
    }
}

def tr(key, *args):
    text = TEXTS[LANG].get(key, key)
    return text.format(*args) if args else text

def set_window_icon(window, icon_path):
    try:
        if os.path.exists(icon_path):
            window.iconbitmap(icon_path)
    except:
        pass

# ---------- Определение битности EXE ----------
def get_exe_architecture(exe_path):
    try:
        binary_type = ctypes.c_uint32()
        if ctypes.windll.kernel32.GetBinaryTypeW(exe_path, ctypes.byref(binary_type)):
            return 64 if binary_type.value == 6 else 32
        return 32
    except:
        return 32

def get_architecture_text(exe_path):
    arch = get_exe_architecture(exe_path)
    return "64 Бит" if arch == 64 else "32 Бит"

# ---------- Остальные функции ----------
def is_native_openal_game(exe_path):
    return os.path.basename(exe_path).lower() in NATIVE_OPENAL_EXES

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    try:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    except:
        messagebox.showerror(tr('error'), tr('restart_failed'))

def check_write_permission(folder_path):
    test_file = os.path.join(folder_path, ".eax_test_write")
    try:
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
        return True
    except:
        return False

def ensure_admin_for_path(folder_path, parent_widget):
    if not check_write_permission(folder_path):
        if messagebox.askyesno(tr('no_admin'), tr('admin_prompt', folder_path)):
            restart_as_admin()
        return False
    return True

def create_backup(file_path):
    if not os.path.exists(file_path) or file_path.endswith(".eax_backup"):
        return None
    backup_path = file_path + ".eax_backup"
    try:
        shutil.copy2(file_path, backup_path)
        return backup_path
    except:
        return None

def restore_backup(file_path):
    backup_path = file_path + ".eax_backup"
    if os.path.exists(backup_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            shutil.move(backup_path, file_path)
            return True
        except:
            return False
    return False

def is_openal_installed():
    system_root = os.environ.get("SystemRoot", "C:\\Windows")
    paths = [
        os.path.join(system_root, "System32", "OpenAL32.dll"),
        os.path.join(system_root, "SysWOW64", "OpenAL32.dll"),
    ]
    return any(os.path.exists(p) for p in paths)

_openal_checked = False
_openal_installed = False

def check_openal_once():
    global _openal_checked, _openal_installed
    if not _openal_checked:
        _openal_installed = is_openal_installed()
        _openal_checked = True
    return _openal_installed

def run_installer_as_admin(installer_path):
    try:
        if is_admin():
            result = subprocess.run([installer_path, "/silent"], capture_output=True, text=True, timeout=60)
            return result.returncode == 0
        else:
            result = ctypes.windll.shell32.ShellExecuteW(None, "runas", installer_path, "/silent", None, 1)
            return result > 32
    except:
        return False

def search_eax_support(game_name):
    query = f"Поддерживает ли игра {game_name} EAX/Хардварный звук (Уже использую DSOAL и OpenAL)"
    webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote(query)}")

def run_game(exe_path):
    if not os.path.exists(exe_path):
        messagebox.showerror(tr('error'), tr('file_not_found_err', exe_path))
        return
    try:
        subprocess.Popen([exe_path], cwd=os.path.dirname(exe_path))
    except Exception as e:
        messagebox.showerror(tr('launch_error'), str(e))

def get_exe_icon(exe_path):
    if exe_path in _icon_cache:
        return _icon_cache[exe_path]
    try:
        large, small = win32gui.ExtractIconEx(exe_path, 0)
        if not large and not small:
            _icon_cache[exe_path] = None
            return None
        hicon = large[0] if large else small[0]
        hdc = win32ui.CreateDCFromHandle(win32gui.GetDC(0))
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(hdc, 32, 32)
        hdc_mem = hdc.CreateCompatibleDC()
        old_bmp = hdc_mem.SelectObject(hbmp)
        hdc_mem.FillSolidRect((0, 0, 32, 32), 0xFFFFFF)
        win32gui.DrawIconEx(hdc_mem.GetHandleOutput(), 0, 0, hicon, 32, 32, 0, None, win32con.DI_NORMAL)
        bmpstr = hbmp.GetBitmapBits(True)
        img = Image.frombuffer('RGBA', (32, 32), bmpstr, 'raw', 'BGRA', 0, 1)
        hdc_mem.SelectObject(old_bmp)
        win32gui.DeleteObject(hbmp.GetHandle())
        hdc_mem.DeleteDC()
        hdc.DeleteDC()
        win32gui.ReleaseDC(0, hdc.GetHandleOutput())
        for icon in large + small:
            if icon:
                win32gui.DestroyIcon(icon)
        _icon_cache[exe_path] = img
        return img
    except:
        _icon_cache[exe_path] = None
        return None

class Colors:
    BG = "#FFFFFF"
    SIDEBAR = "#F8F9FA"
    CARD = "#FFFFFF"
    CARD_HOVER = "#F1F3F5"
    CARD_SELECTED = "#E7F5FF"
    ACCENT = "#228BE6"
    SUCCESS = "#40C057"
    DANGER = "#FA5252"
    WARNING = "#F59E0B"
    TEXT = "#212529"
    TEXT_SECONDARY = "#868E96"

class InstallingDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(tr('install_title'))
        self.geometry("350x150")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 350) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.geometry(f"+{x}+{y}")
        ctk.CTkLabel(self, text="⏳", font=ctk.CTkFont(size=36)).pack(pady=(20, 5))
        self.status_label = ctk.CTkLabel(self, text=tr('install_status'), font=ctk.CTkFont(size=13, weight="bold"), text_color=Colors.TEXT)
        self.status_label.pack()
        self.progress = ctk.CTkProgressBar(self, width=250)
        self.progress.pack(pady=(15, 0))
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        set_window_icon(self, os.path.join(parent.app_dir, "icon.ico"))

    def update_status(self, text):
        self.status_label.configure(text=text)

    def close(self):
        self.progress.stop()
        self.destroy()

class InfoWindow(ctk.CTkToplevel):
    def __init__(self, parent, app_dir):
        super().__init__(parent)
        self.title(tr('info_title'))
        self.geometry("700x550")
        self.minsize(500, 400)
        self.configure(fg_color=Colors.BG)
        self.transient(parent)
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(header, text="🎵 EAX Restorer", font=ctk.CTkFont(size=18, weight="bold"), text_color=Colors.ACCENT).pack(side="left")
        text_container = ctk.CTkFrame(self, fg_color=Colors.SIDEBAR, corner_radius=8)
        text_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.text_widget = tk.Text(text_container, font=("Consolas", 10), bg=Colors.SIDEBAR, fg=Colors.TEXT, relief="flat", borderwidth=0, wrap="word", padx=15, pady=15)
        scrollbar = tk.Scrollbar(text_container, orient="vertical", command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        self.text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        info_path = os.path.join(app_dir, "Info.txt")
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                self.text_widget.insert("1.0", f.read())
        else:
            self.text_widget.insert("1.0", tr('info_file_not_found'))
        self.text_widget.configure(state="disabled")
        self.text_widget.see("1.0")
        self.text_widget.bind("<MouseWheel>", lambda e: self.text_widget.yview_scroll(int(-1*(e.delta/120)), "units"))
        ctk.CTkButton(self, text=tr('close'), font=ctk.CTkFont(size=11), fg_color=Colors.ACCENT, corner_radius=6, width=100, height=30, command=self.destroy).pack(pady=(0, 15))
        set_window_icon(self, os.path.join(app_dir, "icon.ico"))

class GameCard(ctk.CTkFrame):
    def __init__(self, parent, name, exe_path, is_native_openal=False, force_method=None, **kwargs):
        super().__init__(parent, fg_color=Colors.CARD, corner_radius=8, height=55, **kwargs)
        self.pack_propagate(False)
        self.game_name = name
        self.exe_path = exe_path
        self.is_native_openal = is_native_openal
        self.force_method = force_method
        self.is_selected = False
        self.configure(cursor="hand2")
        
        self.icon_label = ctk.CTkLabel(self, text="", width=32, height=32)
        self.icon_label.pack(side="left", padx=(12, 10), pady=10)
        icon = get_exe_icon(exe_path)
        if icon:
            ctk_icon = ctk.CTkImage(light_image=icon, dark_image=icon, size=(32, 32))
            self.icon_label.configure(image=ctk_icon)
            self.icon_label.image = ctk_icon
        else:
            self.icon_label.configure(text="🎮", font=ctk.CTkFont(size=20))
        
        self.name_label = ctk.CTkLabel(self, text=name, font=ctk.CTkFont(size=13, weight="bold"), text_color=Colors.TEXT, anchor="w")
        self.name_label.pack(side="left", fill="x", expand=True, pady=10)
        
        # Метка архитектуры красным цветом
        arch_text = get_architecture_text(exe_path)
        self.arch_label = ctk.CTkLabel(self, text=arch_text, font=ctk.CTkFont(size=9, weight="bold"), text_color=Colors.DANGER)
        self.arch_label.pack(side="right", padx=(0, 5), pady=10)
        
        self.update_badge()

    def update_badge(self):
        if hasattr(self, 'method_badge'):
            self.method_badge.destroy()
        if self.force_method == 'dsoal':
            badge_text, badge_color = "🔧 DSOAL", Colors.ACCENT
        elif self.force_method == 'dsoal64':
            badge_text, badge_color = "🔧 DSOAL64", Colors.ACCENT
        elif self.force_method == 'openal':
            badge_text, badge_color = "🔊 OpenAL", Colors.WARNING
        elif self.is_native_openal:
            badge_text, badge_color = "🔊 OpenAL", Colors.WARNING
        else:
            return
        self.method_badge = ctk.CTkLabel(self, text=badge_text, font=ctk.CTkFont(size=9, weight="bold"), text_color=badge_color)
        self.method_badge.pack(side="right", padx=(0, 12), pady=10)

    def select(self):
        if self.winfo_exists():
            self.is_selected = True
            self.configure(fg_color=Colors.CARD_SELECTED)

    def deselect(self):
        if self.winfo_exists():
            self.is_selected = False
            self.configure(fg_color=Colors.CARD)

class OpenALDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title(tr('title'))
        self.geometry("450x230")
        self.resizable(False, False)
        self.configure(fg_color=Colors.BG)
        self.result = None
        self.dont_show = tk.BooleanVar(value=False)
        self.transient(parent)
        self.grab_set()
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 450) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 230) // 2
        self.geometry(f"+{x}+{y}")
        ctk.CTkLabel(self, text="🔊", font=ctk.CTkFont(size=40)).pack(pady=(20, 5))
        ctk.CTkLabel(self, text=tr('openal_required'), font=ctk.CTkFont(size=14, weight="bold"), text_color=Colors.TEXT).pack()
        ctk.CTkLabel(self, text=tr('openal_desc'), font=ctk.CTkFont(size=11), text_color=Colors.TEXT_SECONDARY).pack(pady=(5, 15))
        btns = ctk.CTkFrame(self, fg_color="transparent")
        btns.pack(fill="x", padx=30)
        ctk.CTkButton(btns, text=tr('download_install'), font=ctk.CTkFont(size=12, weight="bold"), fg_color=Colors.ACCENT, corner_radius=6, width=180, height=35, command=lambda: self.finish(True)).pack(side="left")
        ctk.CTkButton(btns, text=tr('no'), font=ctk.CTkFont(size=12), fg_color="transparent", hover_color=Colors.CARD_HOVER, text_color=Colors.TEXT, border_width=1, border_color="#DEE2E6", corner_radius=6, width=100, height=35, command=lambda: self.finish(False)).pack(side="right")
        ctk.CTkCheckBox(self, text=tr('dont_show'), variable=self.dont_show, font=ctk.CTkFont(size=10), text_color=Colors.TEXT_SECONDARY).pack(pady=(15, 0))
        set_window_icon(self, os.path.join(parent.app_dir, "icon.ico"))

    def finish(self, result):
        self.result = result
        self.destroy()

class EAXRestorer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(tr('title'))
        self.geometry("850x550")
        self.minsize(750, 450)
        self.configure(fg_color=Colors.BG)
        self.games = {}
        self.eax_games = set()
        self.selected_card = None
        self.app_dir = os.path.dirname(os.path.abspath(__file__))
        self.dsoal64_dir = os.path.join(self.app_dir, DSOAL64_FOLDER)
        self.installing_dialog = None
        self.openal_installed = check_openal_once()
        self.left_cards = {}
        self.right_cards = {}
        self.load_data()
        self.setup_ui()
        set_window_icon(self, os.path.join(self.app_dir, "icon.ico"))
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._run_loop, daemon=True).start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        if not self.openal_installed and not self.load_setting('skip_openal'):
            self.after(500, self.show_openal_dialog)

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _on_close(self):
        self.save_data()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.destroy()

    def show_info(self, event=None):
        InfoWindow(self, self.app_dir)

    def show_openal_dialog(self):
        dialog = OpenALDialog(self)
        self.wait_window(dialog)
        if dialog and dialog.dont_show.get():
            self.save_setting('skip_openal', True)
        if dialog and dialog.result:
            asyncio.run_coroutine_threadsafe(self.download_and_install_openal(), self.loop)

    async def download_and_install_openal(self):
        self.after(0, self._show_installing_dialog)
        try:
            self._update_installing_status(tr('install_status'))
            with tempfile.TemporaryDirectory() as tmp:
                zip_path = os.path.join(tmp, "oalinst.zip")
                async with aiohttp.ClientSession() as s:
                    async with s.get("https://openal.org/downloads/oalinst.zip") as r:
                        if r.status != 200:
                            raise Exception(tr('download_error', r.status))
                        with open(zip_path, 'wb') as f:
                            while True:
                                chunk = await r.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                self._update_installing_status(tr('install_status'))
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zf:
                    zf.extractall(tmp)
                installer = None
                for root, dirs, files in os.walk(tmp):
                    for f in files:
                        if f.lower() == "oalinst.exe":
                            installer = os.path.join(root, f)
                            break
                if not installer:
                    raise Exception(tr('installer_not_found'))
                self._update_installing_status(tr('install_status'))
                loop = asyncio.get_event_loop()
                success = await loop.run_in_executor(None, run_installer_as_admin, installer)
                if success:
                    self._update_installing_status(tr('install_status'))
                    await asyncio.sleep(2)
                    self.openal_installed = is_openal_installed()
                    self.after(0, self._close_installing_dialog)
                    if self.openal_installed:
                        self.after(0, lambda: messagebox.showinfo(tr('success'), tr('install_success')))
                    else:
                        self.after(0, lambda: messagebox.showwarning(tr('attention'), tr('install_warning')))
                else:
                    self.after(0, self._close_installing_dialog)
                    self.after(0, lambda: messagebox.showerror(tr('error'), tr('install_error')))
        except Exception as e:
            self.after(0, self._close_installing_dialog)
            self.after(0, lambda: messagebox.showerror(tr('error'), str(e)))

    def _show_installing_dialog(self):
        self.installing_dialog = InstallingDialog(self)

    def _update_installing_status(self, text):
        if self.installing_dialog and self.installing_dialog.winfo_exists():
            self.installing_dialog.update_status(text)

    def _close_installing_dialog(self):
        if self.installing_dialog and self.installing_dialog.winfo_exists():
            self.installing_dialog.close()
            self.installing_dialog = None

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        top = ctk.CTkFrame(self, fg_color="transparent", height=55)
        top.grid(row=0, column=0, sticky="ew", padx=25, pady=(20, 10))
        top.grid_propagate(False)
        title_label = ctk.CTkLabel(top, text="🎵 EAX Restorer", font=ctk.CTkFont(size=20, weight="bold"), text_color=Colors.ACCENT, cursor="hand2")
        title_label.pack(side="left")
        title_label.bind("<Button-1>", self.show_info)
        ctk.CTkLabel(top, text=tr('click_for_help'), font=ctk.CTkFont(size=9), text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(8, 0))
        ctk.CTkButton(top, text=tr('add_game'), font=ctk.CTkFont(size=12, weight="bold"), fg_color=Colors.ACCENT, corner_radius=6, width=150, height=35, command=self.add_game).pack(side="right")
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=25, pady=(0, 20))
        content.grid_columnconfigure(0, weight=1, uniform="panel")
        content.grid_columnconfigure(1, weight=0)
        content.grid_columnconfigure(2, weight=1, uniform="panel")
        content.grid_rowconfigure(0, weight=1)
        left = ctk.CTkFrame(content, fg_color=Colors.SIDEBAR, corner_radius=12)
        left.grid(row=0, column=0, sticky="nsew")
        lh = ctk.CTkFrame(left, fg_color="transparent", height=40)
        lh.pack(fill="x", padx=15, pady=(15, 10))
        lh.pack_propagate(False)
        ctk.CTkLabel(lh, text=tr('available_games'), font=ctk.CTkFont(size=12, weight="bold"), text_color=Colors.TEXT).pack(side="left")
        self.left_count = ctk.CTkLabel(lh, text="(0)", font=ctk.CTkFont(size=10), text_color=Colors.TEXT_SECONDARY)
        self.left_count.pack(side="left", padx=4)
        ctk.CTkLabel(lh, text=tr('right_click_menu'), font=ctk.CTkFont(size=9), text_color=Colors.TEXT_SECONDARY).pack(side="right")
        self.left_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.left_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        center = ctk.CTkFrame(content, fg_color="transparent", width=60)
        center.grid(row=0, column=1, padx=10)
        center.grid_propagate(False)
        center.grid_rowconfigure(0, weight=1)
        center.grid_rowconfigure(1, weight=0)
        center.grid_rowconfigure(2, weight=0)
        center.grid_rowconfigure(3, weight=1)
        self.to_btn = ctk.CTkButton(center, text="→", font=ctk.CTkFont(size=20, weight="bold"), fg_color=Colors.SUCCESS, corner_radius=8, width=50, height=50, state="disabled", command=self.activate_eax)
        self.to_btn.grid(row=1, column=0, pady=8)
        self.from_btn = ctk.CTkButton(center, text="←", font=ctk.CTkFont(size=20, weight="bold"), fg_color=Colors.DANGER, corner_radius=8, width=50, height=50, state="disabled", command=self.deactivate_eax)
        self.from_btn.grid(row=2, column=0, pady=8)
        right = ctk.CTkFrame(content, fg_color=Colors.SIDEBAR, corner_radius=12)
        right.grid(row=0, column=2, sticky="nsew")
        rh = ctk.CTkFrame(right, fg_color="transparent", height=40)
        rh.pack(fill="x", padx=15, pady=(15, 10))
        rh.pack_propagate(False)
        ctk.CTkLabel(rh, text=tr('eax_activated'), font=ctk.CTkFont(size=12, weight="bold"), text_color=Colors.SUCCESS).pack(side="left")
        self.right_count = ctk.CTkLabel(rh, text="(0)", font=ctk.CTkFont(size=10), text_color=Colors.TEXT_SECONDARY)
        self.right_count.pack(side="left", padx=4)
        self.right_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent")
        self.right_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.update_lists()

    def add_game(self):
        exe_path = filedialog.askopenfilename(title=tr('add_game'), filetypes=[("Executable files", "*.exe")])
        if not exe_path:
            return
        name = os.path.splitext(os.path.basename(exe_path))[0].replace('_', ' ').title()
        self.games[name] = {
            'path': os.path.dirname(exe_path),
            'exe': exe_path,
            'native_openal': is_native_openal_game(exe_path),
            'force_method': None
        }
        self.update_lists()
        self.save_data()

    def delete_game(self, name):
        if name in self.eax_games:
            self.eax_games.discard(name)
        self.games.pop(name, None)
        self.update_lists()
        self.save_data()

    def select_card(self, card):
        if not card:
            return
        if self.selected_card and self.selected_card != card:
            self.selected_card.deselect()
        self.selected_card = card
        card.select()
        if card.game_name in self.eax_games:
            self.to_btn.configure(state="disabled")
            self.from_btn.configure(state="normal")
        else:
            self.to_btn.configure(state="normal")
            self.from_btn.configure(state="disabled")

    def update_lists(self):
        for widget in self.left_scroll.winfo_children():
            widget.destroy()
        for widget in self.right_scroll.winfo_children():
            widget.destroy()
        self.left_cards.clear()
        self.right_cards.clear()
        for name, data in sorted(self.games.items()):
            if name in self.eax_games:
                parent = self.right_scroll
                target_dict = self.right_cards
            else:
                parent = self.left_scroll
                target_dict = self.left_cards
            card = GameCard(parent, name, data['exe'], data.get('native_openal', False), data.get('force_method'))
            card.pack(fill="x", padx=5, pady=2)
            self._bind_card_events(card)
            target_dict[name] = card
        if not self.left_cards:
            ctk.CTkLabel(self.left_scroll, text=tr('empty_left'), font=ctk.CTkFont(size=11), text_color=Colors.TEXT_SECONDARY).pack(expand=True, pady=40)
        if not self.right_cards:
            ctk.CTkLabel(self.right_scroll, text=tr('empty_right'), font=ctk.CTkFont(size=11), text_color=Colors.TEXT_SECONDARY).pack(expand=True, pady=40)
        self.left_count.configure(text=f"({len(self.left_cards)})")
        self.right_count.configure(text=f"({len(self.right_cards)})")
        if self.selected_card:
            self.selected_card.deselect()
        self.selected_card = None
        self.to_btn.configure(state="disabled")
        self.from_btn.configure(state="disabled")

    def _bind_card_events(self, card):
        card.bind("<Button-1>", lambda e, c=card: self.select_card(c))
        card.icon_label.bind("<Button-1>", lambda e, c=card: self.select_card(c))
        card.name_label.bind("<Button-1>", lambda e, c=card: self.select_card(c))
        card.bind("<Button-3>", lambda e, c=card: self._show_context_menu(e, c))
        card.icon_label.bind("<Button-3>", lambda e, c=card: self._show_context_menu(e, c))
        card.name_label.bind("<Button-3>", lambda e, c=card: self._show_context_menu(e, c))
        card.bind("<Enter>", lambda e, c=card: c.configure(fg_color=Colors.CARD_HOVER) if not c.is_selected else None)
        card.bind("<Leave>", lambda e, c=card: c.configure(fg_color=Colors.CARD) if not c.is_selected else None)

    def _show_context_menu(self, event, card):
        menu = tk.Menu(self, tearoff=0)
        menu.configure(bg=Colors.SIDEBAR, fg=Colors.TEXT, font=("Segoe UI", 10), activebackground=Colors.ACCENT, activeforeground="white")
        menu.add_command(label=tr('run_game'), command=lambda: run_game(card.exe_path))
        menu.add_separator()
        menu.add_command(label=tr('learn_eax'), command=lambda: search_eax_support(card.game_name))
        menu.add_separator()
        menu.add_command(label=tr('use_dsoal'), command=lambda: self.force_method(card, 'dsoal'))
        menu.add_command(label=tr('use_dsoal64'), command=lambda: self.force_method(card, 'dsoal64'))
        menu.add_command(label=tr('use_openal'), command=lambda: self.force_method(card, 'openal'))
        menu.add_separator()
        menu.add_command(label=tr('delete'), command=lambda: self.delete_game(card.game_name))
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def force_method(self, card, method):
        name = card.game_name
        if name in self.games:
            self.games[name]['force_method'] = method
            self.update_lists()
            self.save_data()

    def get_effective_method(self, game_data):
        force = game_data.get('force_method')
        if force:
            return force
        if game_data.get('native_openal'):
            return 'openal'
        arch = get_exe_architecture(game_data['exe'])
        return 'dsoal64' if arch == 64 else 'dsoal'

    def activate_eax(self):
        if not self.selected_card:
            return
        name = self.selected_card.game_name
        game_data = self.games[name]
        game_path = game_data['path']
        method = self.get_effective_method(game_data)
        if not ensure_admin_for_path(game_path, self):
            return
        try:
            if method == 'openal':
                target = os.path.join(game_path, OPENAL_DLL)
                create_backup(target)
                src = os.path.join(self.app_dir, OPENAL_DLL)
                if os.path.exists(src):
                    shutil.copy2(src, target)
            elif method == 'dsoal64':
                if os.path.exists(self.dsoal64_dir):
                    for f in os.listdir(self.dsoal64_dir):
                        src = os.path.join(self.dsoal64_dir, f)
                        if os.path.isfile(src):
                            target = os.path.join(game_path, f)
                            create_backup(target)
                            shutil.copy2(src, target)
            else:
                for f in DSOAL_FILES:
                    target = os.path.join(game_path, f)
                    create_backup(target)
                    src = os.path.join(self.app_dir, f)
                    if os.path.exists(src):
                        shutil.copy2(src, target)
            self.eax_games.add(name)
            self.update_lists()
            self.save_data()
            messagebox.showinfo(tr('success'), tr('activate_success', name, method.upper()))
        except Exception as e:
            messagebox.showerror(tr('error'), str(e))

    def deactivate_eax(self):
        if not self.selected_card:
            return
        name = self.selected_card.game_name
        game_data = self.games[name]
        game_path = game_data['path']
        method = self.get_effective_method(game_data)
        if not ensure_admin_for_path(game_path, self):
            return
        try:
            if method == 'openal':
                target = os.path.join(game_path, OPENAL_DLL)
                if not restore_backup(target):
                    if os.path.exists(target):
                        os.remove(target)
            elif method == 'dsoal64':
                if os.path.exists(self.dsoal64_dir):
                    for f in os.listdir(self.dsoal64_dir):
                        target = os.path.join(game_path, f)
                        if not restore_backup(target):
                            if os.path.exists(target):
                                os.remove(target)
            else:
                for f in DSOAL_FILES:
                    target = os.path.join(game_path, f)
                    if not restore_backup(target):
                        if os.path.exists(target):
                            os.remove(target)
            self.eax_games.discard(name)
            self.update_lists()
            self.save_data()
            messagebox.showinfo(tr('success'), tr('deactivate_success', name))
        except Exception as e:
            messagebox.showerror(tr('error'), str(e))

    def save_data(self):
        try:
            with open('eax_restorer.json', 'w', encoding='utf-8') as f:
                json.dump({'games': self.games, 'eax_games': list(self.eax_games)}, f)
        except Exception:
            pass

    def load_data(self):
        try:
            if os.path.exists('eax_restorer.json'):
                with open('eax_restorer.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.games = data.get('games', {})
                    self.eax_games = set(data.get('eax_games', []))
                    for info in self.games.values():
                        if 'force_method' not in info:
                            info['force_method'] = None
        except Exception:
            self.games = {}
            self.eax_games = set()

    def load_setting(self, key):
        try:
            if os.path.exists('eax_settings.json'):
                with open('eax_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f).get(key, False)
        except Exception:
            return False
        return False

    def save_setting(self, key, value):
        try:
            settings = {}
            if os.path.exists('eax_settings.json'):
                with open('eax_settings.json', 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            settings[key] = value
            with open('eax_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f)
        except Exception:
            pass

if __name__ == "__main__":
    app = EAXRestorer()
    app.mainloop()
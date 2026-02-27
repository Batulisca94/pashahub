import customtkinter as ctk
from tkinter import filedialog, messagebox
import subprocess, os, ctypes, sys, winreg, threading, time, shutil, tempfile
from PIL import Image
import psutil

# ---------- RESOURCE PATH (PyInstaller uyumlu) ----------
def resource_path(relative_path):
    """PyInstaller exe ile çalışacak şekilde dosya path'i döndürür"""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- CONFIG ----------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ---------- ADMIN ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def relaunch_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# ---------- CORE FUNCTIONS ----------
def lock_pc():
    ctypes.windll.user32.LockWorkStation()

def open_winutil():
    try:
        subprocess.Popen(
            ["powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",
             'Start-Process powershell -ArgumentList "irm \'https://christitus.com/windev\' | iex" -Verb RunAs'],
            shell=False
        )
    except Exception as e:
        messagebox.showerror("WinUTIL Error", str(e))

def open_md_editor():
    path = filedialog.askopenfilename(filetypes=[("Markdown","*.md")])
    if not path: return
    editor = ctk.CTkToplevel()
    editor.geometry("850x650")
    editor.title("Markdown Editor")
    editor.attributes("-topmost", True)
    editor.focus_force()
    textbox = ctk.CTkTextbox(editor)
    textbox.pack(fill="both", expand=True)
    with open(path, "r", encoding="utf-8") as f:
        textbox.insert("1.0", f.read())
    def save():
        with open(path, "w", encoding="utf-8") as f:
            f.write(textbox.get("1.0","end"))
        messagebox.showinfo("Saved", "Dosya kaydedildi.")
    ctk.CTkButton(editor, text="Save", command=save).pack(pady=5)

def toggle_god_mode():
    path = os.path.join(os.path.expanduser("~"), "Desktop\\GodMode.{ED7BA470-8E54-465E-825C-99712043E01C}")
    try:
        if os.path.exists(path):
            os.rmdir(path)
            messagebox.showinfo("God Mode","Disabled.")
        else:
            os.mkdir(path)
            messagebox.showinfo("God Mode","Enabled.")
    except Exception as e:
        messagebox.showerror("Error", f"God Mode hatası: {e}")

def convert_image():
    file_path = filedialog.askopenfilename(filetypes=[("Images","*.png;*.jpg;*.jpeg")])
    if not file_path: return
    try:
        img = Image.open(file_path)
        new_path = file_path.rsplit(".",1)[0]+".jpg"
        img.convert("RGB").save(new_path)
        messagebox.showinfo("Converted", f"Kaydedildi:\n{new_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Conversion hatası: {e}")

def ensure_taskmgr_enabled():
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\System")
        winreg.SetValueEx(key,"DisableTaskMgr",0,winreg.REG_DWORD,0)
        winreg.CloseKey(key)
        messagebox.showinfo("Task Manager","Task Manager etkinleştirildi.")
    except Exception as e:
        messagebox.showerror("Error", f"TaskMgr hatası: {e}")

def reboot_safe_mode():
    try:
        subprocess.run("bcdedit /set {current} safeboot minimal", shell=True, check=True)
        subprocess.run("shutdown /r /t 0", shell=True, check=True)
    except Exception as e:
        messagebox.showerror("Error", f"Safe Mode reboot hatası: {e}")

def disable_safe_mode():
    try:
        subprocess.run("bcdedit /deletevalue {current} safeboot", shell=True, check=True)
        messagebox.showinfo("Safe Mode","Disabled.")
    except Exception as e:
        messagebox.showerror("Error", f"Safe Mode disable hatası: {e}")

# ---------- EXTENDED OEM ----------
def change_oem_full(manufacturer="", model="", support_url="", support_phone="", logo_path=""):
    try:
        key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\OEMInformation"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        if manufacturer:
            winreg.SetValueEx(key,"Manufacturer",0,winreg.REG_SZ,manufacturer)
        if model:
            winreg.SetValueEx(key,"Model",0,winreg.REG_SZ,model)
        if support_url:
            winreg.SetValueEx(key,"SupportURL",0,winreg.REG_SZ,support_url)
        if support_phone:
            winreg.SetValueEx(key,"SupportPhone",0,winreg.REG_SZ,support_phone)
        if logo_path and os.path.exists(logo_path):
            winreg.SetValueEx(key,"Logo",0,winreg.REG_SZ,logo_path)
        winreg.CloseKey(key)
        messagebox.showinfo("OEM","OEM bilgisi güncellendi.")
    except PermissionError:
        messagebox.showerror("Hata","Admin yetkisi gerekli.")
    except Exception as e:
        messagebox.showerror("Hata", f"OEM hatası: {e}")

# ---------- SYSTEM MONITOR ----------
def system_monitor(label):
    def update():
        while True:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
            label.configure(text=f"CPU: {cpu}%  RAM: {ram}%  Disk: {disk}%")
            time.sleep(1)
    threading.Thread(target=update, daemon=True).start()

# ---------- MISC FUNCTIONS ----------
def restart_explorer():
    subprocess.run("taskkill /f /im explorer.exe",shell=True)
    subprocess.Popen("explorer.exe")

def list_services():
    try:
        os.startfile("services.msc")
    except Exception as e:
        messagebox.showerror("Error", f"Service viewer açma hatası: {e}")

def flush_dns():
    subprocess.run("ipconfig /flushdns",shell=True)
    messagebox.showinfo("Network","DNS flushed.")

def defender_scan():
    subprocess.Popen(r"C:\Program Files\Windows Defender\MpCmdRun.exe -Scan -ScanType 1",shell=True)

def open_startup_folder():
    startup_path = os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
    os.startfile(startup_path)

def enable_ultimate_power():
    subprocess.run("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61",shell=True)
    messagebox.showinfo("Power Plan","Ultimate Performance enabled.")

def clean_temp():
    temp = tempfile.gettempdir()
    errors = 0
    for root, dirs, files in os.walk(temp):
        for name in files:
            try: os.remove(os.path.join(root, name))
            except: errors +=1
        for name in dirs:
            try: shutil.rmtree(os.path.join(root, name), ignore_errors=True)
            except: errors +=1
    messagebox.showinfo("Temp Cleaner", f"Temizleme tamamlandı.\nHata sayısı: {errors}")

# ---------- GUI ----------
class PashaHUB(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.iconbitmap(resource_path("pasha.ico"))  # <- burası artık sorunsuz
        self.title("PashaHUB Stable v3")
        self.geometry("1250x750")
        sidebar = ctk.CTkFrame(self,width=320,fg_color="#1f2a38")
        sidebar.pack(side="left",fill="y")
        main = ctk.CTkFrame(self)
        main.pack(fill="both",expand=True)

        buttons = [
            ("Lock PC", lock_pc),
            ("Open WinUTIL", open_winutil),
            ("Markdown Editor", open_md_editor),
            ("Toggle God Mode", toggle_god_mode),
            ("PNG → JPG", convert_image),
            ("Enable TaskMgr", ensure_taskmgr_enabled),
            ("Safe Mode Reboot", reboot_safe_mode),
            ("Disable Safe Mode", disable_safe_mode),
            ("Restart Explorer", restart_explorer),
            ("Services Viewer", list_services),
            ("Flush DNS", flush_dns),
            ("Defender Quick Scan", defender_scan),
            ("Startup Folder", open_startup_folder),
            ("Ultimate Power Plan", enable_ultimate_power),
            ("Clean Temp", clean_temp)
        ]
        for text,cmd in buttons:
            ctk.CTkButton(sidebar,text=text,command=cmd,height=50).pack(pady=5,padx=10,fill="x")

        ctk.CTkLabel(main,text="OEM Full Editor",font=("Segoe UI",20)).pack(pady=10)
        self.manufacturer = ctk.CTkEntry(main,placeholder_text="Manufacturer"); self.manufacturer.pack(pady=3)
        self.model = ctk.CTkEntry(main,placeholder_text="Model"); self.model.pack(pady=3)
        self.support_url = ctk.CTkEntry(main,placeholder_text="Support URL"); self.support_url.pack(pady=3)
        self.support_phone = ctk.CTkEntry(main,placeholder_text="Support Phone"); self.support_phone.pack(pady=3)
        self.logo_path = ctk.CTkEntry(main,placeholder_text="Logo Path (.bmp/.png)"); self.logo_path.pack(pady=3)
        ctk.CTkButton(main,text="Apply OEM",command=lambda: change_oem_full(
            self.manufacturer.get(),
            self.model.get(),
            self.support_url.get(),
            self.support_phone.get(),
            self.logo_path.get()
        )).pack(pady=10)

        self.monitor_label = ctk.CTkLabel(main,text="System Monitor")
        self.monitor_label.pack(pady=15)
        system_monitor(self.monitor_label)

# ---------- START ----------
if __name__ == "__main__":
    relaunch_as_admin()
    app = PashaHUB()
    app.mainloop()

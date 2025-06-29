# StepMania Launcher 0.3.5
# Added downloads.list tags
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import urllib.request
import threading
import re

def find_sm_base_folder():
    # Unchanged, uses original method
    return os.path.join(os.path.expanduser("~/Documents"), ".sm")

def collect_versions():
    sm_base = find_sm_base_folder()
    version_map = {}

    if not os.path.isdir(sm_base):
        messagebox.showerror("Error", f".sm folder not found at:\n{sm_base}")
        return version_map

    for entry in os.listdir(sm_base):
        if entry.startswith("versions-"):
            version_type = entry[len("versions-"):]
            version_folder = os.path.join(sm_base, entry)
            if os.path.isdir(version_folder):
                for version_name in os.listdir(version_folder):
                    full_path = os.path.join(version_folder, version_name)
                    if os.path.isdir(full_path):
                        display_name = version_name if version_type == "vanilla" else f"{version_type}-{version_name}"
                        version_map[display_name] = full_path
    return version_map

def find_exe_files(folder):
    exe_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".exe"):
                exe_files.append(os.path.join(root, file))
    return exe_files

def launch_exe_from_version(version_path):
    exe_files = find_exe_files(version_path)
    if not exe_files:
        messagebox.showerror("Error", f"No EXE files found in:\n{version_path}")
        return

    if len(exe_files) == 1:
        exe_to_run = exe_files[0]
    else:
        exe_names = [os.path.relpath(exe, version_path) for exe in exe_files]
        selection_window = tk.Toplevel()
        selection_window.title("Select EXE to Run")
        selection_window.geometry("400x200")

        tk.Label(selection_window, text="Multiple EXEs found. Select one to launch:").pack(pady=10)
        selected_exe = tk.StringVar(value=exe_names[0])
        exe_dropdown = ttk.Combobox(selection_window, values=exe_names, textvariable=selected_exe, state="readonly")
        exe_dropdown.pack(pady=10)
        exe_dropdown.current(0)

        def on_select():
            selected_path = os.path.join(version_path, selected_exe.get())
            selection_window.destroy()
            try:
                subprocess.Popen([selected_path], shell=True)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch EXE:\n{str(e)}")

        ttk.Button(selection_window, text="Launch", command=on_select).pack(pady=20)
        selection_window.transient()
        selection_window.grab_set()
        selection_window.mainloop()
        return

    try:
        subprocess.Popen([exe_to_run], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch EXE:\n{str(e)}")

def read_download_list(file_path="downloads.list"):
    downloads = {}
    if not os.path.isfile(file_path):
        return downloads
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            match = re.match(r"\[(.*?)\]:\[(.*?)\]", line)
            if match:
                name, url = match.groups()
                downloads[name] = url
    return downloads

def download_file(name, url):
    ext = os.path.splitext(url)[-1].lower()
    sm_base = find_sm_base_folder()
    target_dir = "extract" if ext in [".zip", ".7z", ".smzip"] else "newver"
    full_target_dir = os.path.join(sm_base, target_dir)
    os.makedirs(full_target_dir, exist_ok=True)

    filename = os.path.basename(url.split("?")[0])
    destination = os.path.join(full_target_dir, filename)

    try:
        urllib.request.urlretrieve(url, destination)
        messagebox.showinfo("Download Complete", f"{name} downloaded to:\n{destination}")
    except Exception as e:
        messagebox.showerror("Download Error", f"Failed to download {name}:\n{str(e)}")

def open_download_window():
    downloads = read_download_list()
    window = tk.Toplevel()
    window.title("Download Manager")
    window.geometry("400x200")

    if not downloads:
        ttk.Label(window, text="No downloads found in downloads.list").pack(pady=10)
        return

    ttk.Label(window, text="Select an item to download:").pack(pady=10)

    selected_download = tk.StringVar()
    download_menu = ttk.Combobox(window, textvariable=selected_download, values=list(downloads.keys()), state="readonly")
    download_menu.pack(pady=5)
    download_menu.current(0)

    def start_download():
        name = selected_download.get()
        url = downloads.get(name)
        if not url:
            messagebox.showerror("Error", "Invalid download selection.")
            return
        threading.Thread(target=download_file, args=(name, url), daemon=True).start()

    ttk.Button(window, text="Download!", command=start_download).pack(pady=15)

    window.transient()
    window.grab_set()
    window.mainloop()

def main():
    root = tk.Tk()
    root.title("StepMania Launcher")
    root.geometry("450x280")

    ttk.Label(root, text="Select StepMania Version:").pack(pady=10)

    version_map = collect_versions()
    if not version_map:
        ttk.Label(root, text="No StepMania versions found in .sm folder.").pack(pady=10)
    else:
        version_names = sorted(version_map.keys())
        selected_version = tk.StringVar()
        version_menu = ttk.Combobox(root, textvariable=selected_version, values=version_names, state="readonly")
        version_menu.pack(pady=5)
        version_menu.current(0)

        launch_button = ttk.Button(
            root,
            text="Launch StepMania",
            command=lambda: launch_exe_from_version(version_map[selected_version.get()])
        )
        launch_button.pack(pady=20)

    # Open separate download manager
    ttk.Button(root, text="Open Download Manager", command=open_download_window).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()

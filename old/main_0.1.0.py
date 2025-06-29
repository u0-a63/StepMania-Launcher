# StepMania-Launcher 0.1.0
# Hello, world!
import os
import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def find_versions_folder():
    documents = os.path.expanduser("~/Documents")
    sm_base = os.path.join(documents, ".sm", "versions-vanilla")
    if not os.path.isdir(sm_base):
        messagebox.showerror("Error", f"Couldn't find versions folder at:\n{sm_base}")
        return None
    return sm_base

def get_versions(versions_path):
    return [name for name in os.listdir(versions_path)
            if os.path.isdir(os.path.join(versions_path, name))]

def launch_stepmania(selected_version):
    versions_path = find_versions_folder()
    if not versions_path or not selected_version:
        return
    exe_path = os.path.join(versions_path, selected_version, "Program", "StepMania.exe")
    if not os.path.isfile(exe_path):
        messagebox.showerror("Error", f"'StepMania.exe' not found at:\n{exe_path}")
        return
    try:
        subprocess.Popen([exe_path], shell=True)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch StepMania:\n{str(e)}")

def main():
    root = tk.Tk()
    root.title("StepMania Launcher")
    root.geometry("400x200")

    ttk.Label(root, text="Select StepMania Version:").pack(pady=10)

    versions_path = find_versions_folder()
    if not versions_path:
        root.destroy()
        return

    versions = get_versions(versions_path)
    if not versions:
        messagebox.showinfo("Info", "No versions found in versions-vanilla folder.")
        root.destroy()
        return

    selected_version = tk.StringVar()
    version_menu = ttk.Combobox(root, textvariable=selected_version, values=versions, state="readonly")
    version_menu.pack(pady=5)
    version_menu.current(0)

    launch_button = ttk.Button(root, text="Launch StepMania", command=lambda: launch_stepmania(selected_version.get()))
    launch_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()

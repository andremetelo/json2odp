import json
import os
import subprocess
from tkinter import filedialog, messagebox

def load_json_file(gui):
    path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
    if not path: return
    try:
        with open(path, 'r', encoding='utf-8') as f: p = json.load(f)
        t_s = p.get("global_title_style", {})
        gui.state.title_font = t_s.get("font_name", "Arial")
        gui.state.title_size = t_s.get("font_size", "44pt")
        gui.state.title_weight = t_s.get("font_weight", "bold")
        b_s = p.get("global_body_style", {})
        gui.state.body_font = b_s.get("font_name", "Arial")
        gui.state.body_size = b_s.get("font_size", "22pt")
        gui.state.body_weight = b_s.get("font_weight", "normal")
        gui.state.slides = p.get("slides", list())
        gui.current_json_path = path
        gui.refresh_sidebar()
        gui.s_list.selection_set(0)
        import form_sync
        form_sync.load_fields(gui, 0)
    except Exception as e: messagebox.showerror("Error", f"Failed: {e}")

def save_json_file(gui):
    import form_sync
    form_sync.save_fields(gui)
    if not gui.current_json_path:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not path: return
        gui.current_json_path = path
    try:
        with open(gui.current_json_path, 'w', encoding='utf-8') as f:
            json.dump(gui.state.get_json_data(), f, indent=2)
        messagebox.showinfo("Success", "Saved configurations JSON cleanly.")
    except Exception as e: messagebox.showerror("Error", f"Failed: {e}")

def compile_odp(gui):
    import form_sync
    form_sync.save_fields(gui)
    staging = "gui_runtime_manifest.json"
    with open(staging, 'w', encoding='utf-8') as f: json.dump(gui.state.get_json_data(), f, indent=2)
    out = filedialog.asksaveasfilename(defaultextension=".odp", filetypes=[("ODP Presentations", "*.odp")])
    if not out:
        if os.path.exists(staging): os.remove(staging)
        return
    tpl = filedialog.askopenfilename(filetypes=[("ODP Templates", "*.odp")]) if messagebox.askyesno("Template Base", "Apply template styling background layer?") else None
    backend = "./json2odp.py"
    if not os.path.exists(backend):
        messagebox.showerror("Error", f"Backend processor '{backend}' missing.")
        return
    cmd = ["python3", backend, "-i", staging, "-o", out]
    if tpl: cmd.extend(["-t", tpl])
    try:
        subprocess.run(cmd, check=True)
        messagebox.showinfo("Success", "ODP compiled successfully!")
    except Exception as e: messagebox.showerror("Error", f"Failed: {e}")
    finally:
        if os.path.exists(staging): os.remove(staging)

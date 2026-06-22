#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, filedialog
import os
from state import PresentationState
import form_sync
import file_ops

class JSONPresentationEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("ODP Presentation Schema Studio")
        self.root.geometry("1000x700")
        self.current_json_path = None
        self.state = PresentationState()
        self.active_idx = None
        self.build_ui()
        self.reset_to_default()

    def build_ui(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New", command=self.reset_to_default)
        filemenu.add_command(label="Open JSON...", command=lambda: file_ops.load_json_file(self))
        filemenu.add_command(label="Save JSON", command=lambda: file_ops.save_json_file(self))
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

        main_box = ttk.Frame(self.root, padding=10)
        main_box.pack(fill=tk.BOTH, expand=True)

        l_panel = ttk.Frame(main_box, width=220)
        l_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        l_panel.pack_propagate(False)
        ttk.Label(l_panel, text="Slide Elements").pack(anchor=tk.W, pady=5)
        self.s_list = tk.Listbox(l_panel, selectbackground="#007aff", relief=tk.FLAT, bd=1)
        self.s_list.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.s_list.bind('<<ListboxSelect>>', self.on_slide_select)

        b_box = ttk.Frame(l_panel)
        b_box.pack(fill=tk.X)
        ttk.Button(b_box, text="+ Add", command=self.ui_add).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(b_box, text="- Del", command=self.ui_del).pack(side=tk.RIGHT, fill=tk.X, expand=True)

        r_panel = ttk.Frame(main_box)
        r_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        g_style = ttk.LabelFrame(r_panel, text=" Global Typography Configurations ", padding=10)
        g_style.pack(fill=tk.X, pady=(0, 10))
        self.t_f = ttk.Entry(g_style, width=12); self.t_f.grid(row=0, column=0, padx=2)
        self.t_s = ttk.Entry(g_style, width=5); self.t_s.grid(row=0, column=1, padx=2)
        self.t_w = ttk.Combobox(g_style, values=["normal", "bold"], width=6, state="readonly"); self.t_w.grid(row=0, column=2, padx=2)
        self.b_f = ttk.Entry(g_style, width=12); self.b_f.grid(row=1, column=0, padx=2)
        self.b_s = ttk.Entry(g_style, width=5); self.b_s.grid(row=1, column=1, padx=2)
        self.b_w = ttk.Combobox(g_style, values=["normal", "bold"], width=6, state="readonly"); self.b_w.grid(row=1, column=2, padx=2)

        self.s_work = ttk.LabelFrame(r_panel, text=" Active Slide Fields ", padding=10)
        self.s_work.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.s_title = ttk.Entry(self.s_work, width=40); self.s_title.grid(row=0, column=0, sticky=tk.W, pady=2)
        self.s_title.bind("<KeyRelease>", self.update_listbox_live)
        self.s_sub = ttk.Entry(self.s_work, width=40); self.s_sub.grid(row=1, column=0, sticky=tk.W, pady=2)
        self.s_lay = ttk.Combobox(self.s_work, values=["single_column", "two_column", "text_and_graph", "graph_only"], state="readonly", width=15)
        self.s_lay.grid(row=2, column=0, sticky=tk.W, pady=2)
        self.s_lay.bind("<<ComboboxSelected>>", self.toggle_layout_views)

        self.g_lbl = ttk.Label(self.s_work, text="Chart Image Path:")
        self.g_ent = ttk.Entry(self.s_work, width=25)
        self.g_btn = ttk.Button(self.s_work, text="Browse...", command=self.find_img)

        self.txt_box = ttk.Frame(self.s_work)
        self.txt_box.grid(row=4, column=0, sticky=tk.NSEW, pady=5)
        self.s_work.rowconfigure(4, weight=1); self.s_work.columnconfigure(0, weight=1)
        self.c1_f = ttk.Frame(self.txt_box); self.c1_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.c1_lbl = ttk.Label(self.c1_f, text="Bullets:"); self.c1_lbl.pack(anchor=tk.W)
        self.c1_t = tk.Text(self.c1_f, height=6, width=20, font=("Courier", 10)); self.c1_t.pack(fill=tk.BOTH, expand=True)
        self.c2_f = ttk.Frame(self.txt_box); self.c2_lbl = ttk.Label(self.c2_f, text="Column 2:"); self.c2_lbl.pack(anchor=tk.W)
        self.c2_t = tk.Text(self.c2_f, height=6, width=20, font=("Courier", 10)); self.c2_t.pack(fill=tk.BOTH, expand=True)

        self.s_note = tk.Text(self.s_work, height=2, width=40, font=("Helvetica", 10)); self.s_note.grid(row=5, column=0, sticky=tk.EW, pady=2)

        act_panel = ttk.Frame(r_panel).pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(r_panel, text="💾 Save JSON", command=lambda: file_ops.save_json_file(self)).pack(side=tk.LEFT, padx=5)
        ttk.Button(r_panel, text="🛠️ Compile ODP", command=lambda: file_ops.compile_odp(self)).pack(side=tk.RIGHT, padx=5)

    def toggle_layout_views(self, event=None):
        lay = self.s_lay.get()
        self.g_lbl.grid_remove(); self.g_ent.grid_remove(); self.g_btn.grid_remove()
        self.c2_f.pack_forget(); self.c1_f.pack_forget()
        if lay == "single_column":
            self.c1_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        elif lay == "two_column":
            self.c1_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0,2))
            self.c2_f.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(2,0))
        elif lay in ["text_and_graph", "graph_only"]:
            if lay == "text_and_graph": self.c1_f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.g_lbl.grid(row=3, column=0, sticky=tk.W)
            self.g_ent.grid(row=3, column=1, sticky=tk.EW)
            self.g_btn.grid(row=3, column=2, sticky=tk.W)

    def on_slide_select(self, event):
        sel = self.s_list.curselection()
        if sel: form_sync.save_fields(self); form_sync.load_fields(self, sel[0])

    def update_listbox_live(self, event):
        sel = self.s_list.curselection()
        if sel:
            self.s_list.delete(sel[0]); self.s_list.insert(sel[0], f" Slide {sel[0]+1}: {self.s_title.get()}"); self.s_list.selection_set(sel[0])

    def ui_add(self):
        form_sync.save_fields(self); idx = self.state.add_blank(); self.refresh_sidebar()
        self.s_list.selection_set(idx); form_sync.load_fields(self, idx)

    def ui_del(self):
        sel = self.s_list.curselection()
        if sel and self.state.remove_at(sel[0]):
            self.refresh_sidebar(); nxt = max(0, sel[0]-1); self.s_list.selection_set(nxt); form_sync.load_fields(self, nxt)

    def reset_to_default(self):
        self.current_json_path = None; self.state.slides = list(); self.state.add_blank()
        self.refresh_sidebar(); self.s_list.selection_set(0); form_sync.load_fields(self, 0)

    def refresh_sidebar(self):
        self.s_list.delete(0, tk.END)
        for i, s in enumerate(self.state.slides): self.s_list.insert(tk.END, f" Slide {i+1}: {s.get('title','New Slide')}")

    def find_img(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg")])
        if p:
            self.g_ent.delete(0, tk.END)
            # FIXED: Added .path to commonpath
            self.g_ent.insert(0, os.path.relpath(p, os.getcwd()) if os.path.commonpath([p, os.getcwd()]) == os.getcwd() else p)

if __name__ == "__main__":
    tk_root = tk.Tk()
    app = JSONPresentationEditor(tk_root)
    tk_root.mainloop()

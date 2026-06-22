import tkinter as tk

def save_fields(gui):
    if gui.active_idx is None or gui.active_idx >= len(gui.state.slides):
        return
    gui.state.title_font = gui.t_f.get()
    gui.state.title_size = gui.t_s.get()
    gui.state.title_weight = gui.t_w.get()
    gui.state.body_font = gui.b_f.get()
    gui.state.body_size = gui.b_s.get()
    gui.state.body_weight = gui.b_w.get()

    s = gui.state.slides[gui.active_idx]
    s["title"] = gui.s_title.get()
    s["subtitle"] = gui.s_sub.get()
    s["layout_type"] = gui.s_lay.get()
    s["bullets"] = [l.strip() for l in gui.c1_t.get("1.0", tk.END).split("\n") if l.strip()]
    s["speaker_notes"] = [l.strip() for l in gui.s_note.get("1.0", tk.END).split("\n") if l.strip()]

    if gui.s_lay.get() == "two_column":
        s["bullets_col2"] = [l.strip() for l in gui.c2_t.get("1.0", tk.END).split("\n") if l.strip()]
    if gui.s_lay.get() in ["text_and_graph", "graph_only"]:
        s["graph_path"] = gui.g_ent.get()

def load_fields(gui, idx):
    gui.active_idx = idx
    gui.t_f.delete(0, tk.END); gui.t_f.insert(0, gui.state.title_font)
    gui.t_s.delete(0, tk.END); gui.t_s.insert(0, gui.state.title_size)
    gui.t_w.set(gui.state.title_weight)
    gui.b_f.delete(0, tk.END); gui.b_f.insert(0, gui.state.body_font)
    gui.b_s.delete(0, tk.END); gui.b_s.insert(0, gui.state.body_size)
    gui.b_w.set(gui.state.body_weight)

    s = gui.state.slides[idx]
    gui.s_title.delete(0, tk.END); gui.s_title.insert(0, s.get("title", ""))
    gui.s_sub.delete(0, tk.END); gui.s_sub.insert(0, s.get("subtitle", ""))
    gui.s_lay.set(s.get("layout_type", "single_column"))
    
    gui.c1_t.delete("1.0", tk.END); gui.c1_t.insert(tk.END, "\n".join(s.get("bullets", list())))
    gui.c2_t.delete("1.0", tk.END); gui.c2_t.insert(tk.END, "\n".join(s.get("bullets_col2", list())))
    gui.g_ent.delete(0, tk.END); gui.g_ent.insert(0, s.get("graph_path", ""))
    gui.s_note.delete("1.0", tk.END); gui.s_note.insert(tk.END, "\n".join(s.get("speaker_notes", list())))
    gui.toggle_layout_views()

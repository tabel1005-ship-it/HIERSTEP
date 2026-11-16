#!/usr/bin/env python3
"""
HIERSTEP GUI - Graphical interface for running the Emergy Hierarchy simulation.
Run this script to open the interface (requires hierstep.py in the same folder).

This version has no Nevron Chart viewer dependency. Plots are saved as PNG
via matplotlib when you select Plot checkboxes and run the simulation.
"""

import sys
import os

# Ensure we can import hierstep from the same directory as this script.
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

import hierstep

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox, filedialog
except ImportError:
    sys.exit("Tkinter is required. It is included with standard Python on Windows and macOS.")

# Default parameters (same keys as hierstep.DEFAULTS). Order and labels for display only.
PARAM_SPEC = [
    ("S", "Step size", "1"),
    ("A", "Whole area (used in at, nc, mc, and empd)", "1e9"),
    ("N", "Number of level 1 units and territories", "1000"),
    ("Ca", "Center fraction of territory area (used in aec)", "0.05"),
    ("Cr", "Number of centers converging to higher level center (used in at)", "6"),
    ("Sf", "Area of centers factor change per step (used in ac)", "0.3"),
    ("R", "INITIAL replacement time", "1.0"),
    ("Rf", "Factor changing replacement time with level", "5.0"),
    ("Jeo", "INITIAL energy flow of the whole area (initialize Je)", "1e20"),
    ("eff", "Fraction of energy transformed in each step (used in Je)", "0.1"),
    ("emp", "Empower sej/time of the whole area A (all essential inputs)", "1e20"),
    ("M", "Materials in lowest level (used in mc)", "1e7"),
    ("meo", "INITIAL material coupling to energy flow (used in Jm)", "1e-13"),
    ("fmc", "Factor changing material/energy coupling with level (used in me)", "2.0"),
]

# Parameter group headers for GUI: (header text, param key that follows this header).
PARAM_GROUP_HEADERS = [
    ("Geometry, Space (Scaling)", "A"),
    ("Time (Scaling)", "R"),
    ("Energy", "Jeo"),
    ("Materials", "M"),
]


def parse_param_value(s: str, key: str):
    """Parse a parameter string to int or float."""
    s = s.strip()
    try:
        if "." in s or "e" in s.lower():
            return float(s)
        return int(s)
    except ValueError:
        raise ValueError(f"Invalid number for {key}: {s!r}")


class HierstepApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HIERSTEP - Simulating Emergy and Materials in Hierarchical Steps (all variables are calculated for ONE level at a time)")
        self.root.minsize(960, 640)
        self.root.configure(bg="#add8e6")

        self._setup_styles()
        self._build_ui()
        self._set_initial_window_size()
        self._populate_defaults()
        self.last_rows = None
        self.last_params = None

    def _setup_styles(self):
        style = ttk.Style()
        if "vista" in style.theme_names():
            style.theme_use("vista")
        # Light blue background for desktop/laptop monitors
        bg_blue = "#add8e6"
        for w in ("TFrame", "TLabelframe", "TLabel", "TButton", "TCheckbutton"):
            try:
                style.configure(w, background=bg_blue)
            except tk.TclError:
                pass
        try:
            style.configure("TEntry", fieldbackground="#f0f8ff", background=bg_blue)
        except tk.TclError:
            pass
        style.configure("TLabelframe.Label", background=bg_blue)
        style.configure("Title.TLabel", font=("TkDefaultFont", 10, "bold"), background=bg_blue)
        style.configure("VarRow.TLabel", font=("TkDefaultFont", 8), background=bg_blue)

    def _build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        title_lbl = ttk.Label(main, text="HIERSTEP - Simulating Emergy and Materials in Hierarchical Steps (all variables are calculated for ONE level at a time)", style="Title.TLabel")
        title_lbl.pack(anchor=tk.W)
        ttk.Label(main, text="Odum (2000), Emergy Synthesis I", foreground="gray").pack(anchor=tk.W, pady=(2, 6))

        # Left half: Variables | Right half: Parameters
        content_row = ttk.Frame(main)
        content_row.pack(fill=tk.BOTH, expand=True, pady=(0, 6))
        self._content_row = content_row

        key_vars = hierstep.KEY_VARIABLES
        self.print_vars = {}
        self.plot_vars = {}

        # ---- Left half: Variables (Print | Plot | row labels), buttons directly under list ----
        lf_vars = ttk.LabelFrame(content_row, text=" Variables (Space · Energy · Materials · Emergy) ", padding=6)
        lf_vars.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 6), anchor=tk.N)

        vars_inner = ttk.Frame(lf_vars)
        vars_inner.pack(side=tk.TOP, fill=tk.X, expand=False)
        vars_inner.columnconfigure(2, weight=1)
        ttk.Label(vars_inner, text="Print", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=0, padx=(0, 8), pady=(0, 4), sticky=tk.W)
        ttk.Label(vars_inner, text="Plot", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=1, padx=(0, 8), sticky=tk.W)
        ttk.Label(vars_inner, text="Variable", font=("TkDefaultFont", 9, "bold")).grid(row=0, column=2, sticky=tk.W)

        headers_before = {anchor: text for (text, anchor) in getattr(hierstep, "GROUP_HEADERS", [])}
        row_num = 1
        for v in key_vars:
            if v in headers_before:
                ttk.Label(vars_inner, text=headers_before[v], style="VarRow.TLabel", font=("TkDefaultFont", 8, "bold")).grid(row=row_num, column=0, columnspan=3, padx=0, pady=(4, 2), sticky=tk.W)
                row_num += 1
            self.print_vars[v] = tk.BooleanVar(value=False)
            self.plot_vars[v] = tk.BooleanVar(value=False)
            ttk.Checkbutton(vars_inner, variable=self.print_vars[v]).grid(row=row_num, column=0, padx=(0, 8), pady=0, sticky=tk.W)
            ttk.Checkbutton(vars_inner, variable=self.plot_vars[v]).grid(row=row_num, column=1, padx=(0, 8), pady=0, sticky=tk.W)
            label = hierstep.VARIABLES.get(v, v)
            ttk.Label(vars_inner, text=f"{v} – {label}", anchor=tk.W, style="VarRow.TLabel").grid(row=row_num, column=2, padx=0, pady=0, sticky=tk.W)
            row_num += 1

        btn_row = ttk.Frame(lf_vars)
        btn_row.pack(side=tk.TOP, fill=tk.X, expand=False, pady=(8, 0))
        ttk.Button(btn_row, text="Select all Print", command=lambda: self._set_print_plot(True, "print")).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_row, text="Clear all Print", command=lambda: self._set_print_plot(False, "print")).pack(side=tk.LEFT, padx=(0, 12))
        ttk.Button(btn_row, text="Select all Plot", command=lambda: self._set_print_plot(True, "plot")).pack(side=tk.LEFT, padx=(0, 4))
        ttk.Button(btn_row, text="Clear all Plot", command=lambda: self._set_print_plot(False, "plot")).pack(side=tk.LEFT)
        self.log_scale_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(btn_row, text="Log scale", variable=self.log_scale_var).pack(side=tk.LEFT, padx=(12, 0))

        # ---- Right half: Parameters + me/ens + OOM + Run + Output ----
        # Fills remaining width; height locked to left column (see _match_right_to_left_height).
        right_col = ttk.Frame(content_row)
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(6, 0), anchor=tk.N)
        self._right_col = right_col
        self._lf_vars = lf_vars

        lf_params = ttk.LabelFrame(right_col, text=" Parameters ", padding=4)
        lf_params.pack(fill=tk.X, pady=(0, 4))
        params_inner = ttk.Frame(lf_params)
        params_inner.pack(fill=tk.X)
        self.param_entries = {}

        param_headers_before = {anchor: text for (text, anchor) in PARAM_GROUP_HEADERS}
        for (key, label, default) in PARAM_SPEC:
            if key in param_headers_before:
                group_row = ttk.Frame(params_inner)
                group_row.pack(fill=tk.X, pady=(3, 1))
                ttk.Label(group_row, text=param_headers_before[key], style="VarRow.TLabel", font=("TkDefaultFont", 8, "bold")).pack(side=tk.LEFT)
            row = ttk.Frame(params_inner)
            row.pack(fill=tk.X, pady=0)
            ttk.Label(row, text=f"{key} - {label}", anchor=tk.W, style="VarRow.TLabel").pack(side=tk.LEFT, padx=(0, 8), fill=tk.X, expand=True)
            e = ttk.Entry(row, width=14)
            e.pack(side=tk.RIGHT)
            self.param_entries[key] = e

        me_frame = ttk.Frame(right_col)
        me_frame.pack(fill=tk.X, pady=(2, 4))
        ttk.Label(me_frame, text="me equation:").pack(side=tk.LEFT, padx=(0, 8))
        self.me_equation_var = tk.StringVar(value="linear")
        ttk.Radiobutton(me_frame, text="Linear (default)", variable=self.me_equation_var, value="linear").pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(me_frame, text="Exponential", variable=self.me_equation_var, value="exponential").pack(side=tk.LEFT)
        ttk.Radiobutton(me_frame, text="Constant (me=me)", variable=self.me_equation_var, value="constant").pack(side=tk.LEFT, padx=(10, 0))

        ens_frame = ttk.Frame(right_col)
        ens_frame.pack(fill=tk.X, pady=(0, 4))
        ttk.Label(ens_frame, text="ens equation:").pack(side=tk.LEFT, padx=(0, 8))
        self.ens_equation_var = tk.StringVar(value="multiply")
        ttk.Radiobutton(ens_frame, text="ens=Je/R", variable=self.ens_equation_var, value="divide").pack(side=tk.LEFT, padx=(0, 12))
        ttk.Radiobutton(ens_frame, text="ens=Je*R", variable=self.ens_equation_var, value="multiply").pack(side=tk.LEFT)
        self.oom_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(ens_frame, text=" OOM ", variable=self.oom_var).pack(side=tk.LEFT, padx=(16, 0))
        self.run_btn = ttk.Button(ens_frame, text=" Run simulation ", command=self._run)
        self.run_btn.pack(side=tk.LEFT, padx=(8, 0))

        lf_out = ttk.LabelFrame(right_col, text=" Output ", padding=4)
        lf_out.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
        out_toolbar = ttk.Frame(lf_out)
        out_toolbar.pack(fill=tk.X, pady=(0, 4))
        ttk.Button(out_toolbar, text=" Save as CSV... ", command=self._save_csv).pack(side=tk.RIGHT)
        self.output = scrolledtext.ScrolledText(lf_out, wrap=tk.WORD, height=4, font=("Consolas", 9), bg="#f0f8ff")
        self.output.pack(fill=tk.BOTH, expand=True)
        self._wire_output_clipboard()

    def _wire_output_clipboard(self) -> None:
        """Enable Ctrl+C and a right-click menu for the Output pane."""
        out = self.output

        def copy_selection(_event=None) -> str:
            try:
                text = out.get(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                return "break"
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            return "break"

        def select_all(_event=None) -> str:
            out.tag_add(tk.SEL, "1.0", tk.END)
            out.mark_set(tk.INSERT, tk.END)
            out.see(tk.INSERT)
            return "break"

        def popup_menu(event):
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="Copy", command=lambda: copy_selection())
            menu.add_command(label="Select all", command=lambda: select_all())
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        out.bind("<Control-c>", copy_selection)
        out.bind("<Control-C>", copy_selection)
        out.bind("<Control-a>", select_all)
        out.bind("<Control-A>", select_all)
        out.bind("<Button-3>", popup_menu)

    def _save_csv(self) -> None:
        """Save Print and/or OOM tables to a CSV file."""
        if self.last_rows is None:
            messagebox.showwarning("HIERSTEP", "Run the simulation first, then save.")
            return
        print_keys = [v for v in hierstep.KEY_VARIABLES if self.print_vars[v].get()]
        include_oom = self.oom_var.get()
        if not print_keys and not include_oom:
            messagebox.showwarning(
                "HIERSTEP",
                "Select at least one variable in the Print column and/or turn on OOM, then try again.",
            )
            return
        path = filedialog.asksaveasfilename(
            parent=self.root,
            title="Save table as CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir=_script_dir,
            initialfile="hierstep_export.csv",
        )
        if not path:
            return
        try:
            hierstep.write_csv_export(path, self.last_rows, print_keys, include_oom)
        except Exception as e:
            messagebox.showerror("HIERSTEP", f"Could not save CSV:\n{e}")
            return
        messagebox.showinfo("HIERSTEP", f"Saved:\n{path}")

    def _set_initial_window_size(self):
        # Size the initial window to fit the full control layout, including the
        # buttons directly under the variable columns, while staying on screen.
        self.root.update_idletasks()
        req_width = self.root.winfo_reqwidth()
        req_height = self.root.winfo_reqheight()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        width = min(max(req_width + 20, 980), screen_width - 80)
        height = min(max(req_height + 20, 720), screen_height - 80)
        self.root.geometry(f"{width}x{height}")
        self.root.update_idletasks()
        self._match_right_to_left_height()

    def _match_right_to_left_height(self, _event=None):
        """Match right-column height to the left panel; use all remaining width (no blank strip)."""
        if getattr(self, "_matching_right", False):
            return
        self._matching_right = True
        try:
            self.root.update_idletasks()
            left_h = self._lf_vars.winfo_height()
            if left_h <= 1:
                left_h = self._lf_vars.winfo_reqheight()
            left_w = self._lf_vars.winfo_width()
            if left_w <= 1:
                left_w = self._lf_vars.winfo_reqwidth()
            content_w = self._content_row.winfo_width()
            if content_w <= 1:
                content_w = self._content_row.winfo_reqwidth()
            # Remaining width after left panel + padding between columns.
            right_w = max(content_w - left_w - 18, 520)
            prev = getattr(self, "_right_geom", None)
            if prev == (right_w, left_h):
                return
            self._right_geom = (right_w, left_h)
            self._right_col.configure(width=right_w, height=left_h)
            self._right_col.pack_propagate(False)
            if not getattr(self, "_right_resize_bound", False):
                self._content_row.bind("<Configure>", self._match_right_to_left_height)
                self._right_resize_bound = True
        finally:
            self._matching_right = False

    def _set_print_plot(self, value: bool, which: str):
        d = self.print_vars if which == "print" else self.plot_vars
        for var in d:
            d[var].set(value)

    def _populate_defaults(self):
        for key, _, default in PARAM_SPEC:
            self.param_entries[key].delete(0, tk.END)
            self.param_entries[key].insert(0, default)

    def _get_params(self) -> dict:
        params = {}
        for key in self.param_entries:
            params[key] = parse_param_value(self.param_entries[key].get(), key)
        return params

    def _run(self):
        self.output.delete(1.0, tk.END)
        try:
            params = self._get_params()
        except ValueError as e:
            self.output.insert(tk.END, f"Parameter error: {e}\n")
            return

        params["me_equation"] = self.me_equation_var.get()
        params["ens_equation"] = self.ens_equation_var.get()

        self.output.insert(tk.END, "Running simulation...\n")
        self.root.update_idletasks()

        try:
            rows = hierstep.run_simulation(params)
            n = len(rows)
            self.last_rows = rows
            self.last_params = params
            self.output.insert(tk.END, f"Simulation finished: {n} levels (nc ≥ 1).\n\n")
        except Exception as e:
            self.output.insert(tk.END, f"Simulation error: {e}\n")
            return

        print_keys = [v for v in hierstep.KEY_VARIABLES if self.print_vars[v].get()]
        if print_keys:
            self.output.insert(tk.END, hierstep.format_table(rows, print_keys))
            self.output.insert(tk.END, "\n\n")

        if self.oom_var.get():
            self.output.insert(tk.END, hierstep.format_oom_table(rows))
            self.output.insert(tk.END, "\n\n")

        plot_keys = [v for v in hierstep.KEY_VARIABLES if self.plot_vars[v].get()]
        if plot_keys:
            self.output.insert(tk.END, "Plots (PNG):\n")
            out_dir = os.path.join(_script_dir, "Plots")
            for v in plot_keys:
                try:
                    path = hierstep.plot_variable(rows, v, log_scale=self.log_scale_var.get(), out_dir=out_dir)
                    self.output.insert(tk.END, f"  {path}\n")
                except Exception as e:
                    self.output.insert(tk.END, f"  {v}: error — {e}\n")
            self.output.insert(tk.END, "\n")

        if not print_keys and not plot_keys and not self.oom_var.get():
            self.output.insert(tk.END, "Select OOM and/or at least one variable to print or to plot, then run again.\n")

        self.output.see(tk.END)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = HierstepApp()
    app.run()

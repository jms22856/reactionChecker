import tkinter as tk
from tkinter import filedialog, messagebox
import threading, shutil
import logging
from helper.autocat_check import calc_nodes, setup_logging

LOG_PATH = "PAC.log"



class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Basic Pathways Reaction Checker")
        #Makes screen not resizable (arbitrary)
        self.resizable(False, False)
        self.configure(bg="#F7F7F5") #Default background of app
        self._selected_file = tk.StringVar(value="")
        self._build_ui()
        self._center() #Places app in center of screen
 
    #Layout
    def _build_ui(self):
        PAD = 20 #default x padding

        #Colors for various components
        MAROON = "#500000"
        BG  = "#F7F7F5"
        CARD = "#FFFFFF"
        ACCENT = "#500000"
        MUTED  = "#6B7280"
        BORDER = "#E5E7EB"

        #Various fonts
        FONT_LABEL = ("Helvetica", 10)
        FONT_MONO  = ("Times New Roman", 11)
        FONT_TITLE = ("Helvetica", 15, "bold")
 
        #Title at top
        tk.Label(self, text="Basic Pathways Reaction Checker", font=FONT_TITLE,
                 bg=BG, fg="#111827").pack(pady=(PAD, 4), padx=PAD, anchor="w")
        tk.Label(self, text="Upload a .txt or .csv file to start analysis. The files should contain the reactions and NOTHING ELSE!",
                 font=FONT_LABEL, bg=BG, fg=MUTED).pack(padx=PAD, anchor="w")
 
        #Card to pick input file
        card = tk.Frame(self, bg=CARD, bd=0, highlightthickness=1,
                        highlightbackground=BORDER)
        card.pack(fill="x", padx=PAD, pady=(14, 0))
 
        inner = tk.Frame(card, bg=CARD)
        inner.pack(fill="x", padx=14, pady=12)
 
        tk.Label(inner, text="Input file", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg="#374151").grid(row=0, column=0, sticky="w")
 
        file_row = tk.Frame(inner, bg=CARD)
        file_row.grid(row=1, column=0, sticky="ew", pady=(6, 0))
        inner.columnconfigure(0, weight=1)
 
        self._file_label = tk.Label(
            file_row, textvariable=self._selected_file,
            text="No file selected", font=FONT_LABEL,
            bg="#F3F4F6", fg=MUTED, anchor="w",
            width=46, padx=8, pady=6,
            relief="flat", bd=0,
            highlightthickness=1, highlightbackground=BORDER
        )
        self._file_label.pack(side="left", fill="x", expand=True)
 
        #Button to select file
        tk.Button(
            file_row,
            text="Select File",
            command=self._pick_file,
            font=FONT_LABEL, bg=ACCENT, fg="white",
            activebackground="white", activeforeground=MAROON,
            relief="flat", bd=0, padx=12, pady=6, cursor="hand2"
        ).pack(side="left", padx=(8, 0))
 
        #Run analysis button
        self._run_btn = tk.Button(
            self, text="Run analysis", command=self._run,
            font=("Helvetica", 11, "bold"),
            bg=ACCENT, fg="white",
            activebackground="white", activeforeground=MAROON,
            relief="flat", bd=0, padx=18, pady=9,
            state="disabled", cursor="hand2"
        )
        self._run_btn.pack(anchor="e", padx=PAD, pady=(12, 0))
 
        #Result Card at bottom
        res_card = tk.Frame(self, bg=CARD, bd=0, highlightthickness=1,
                            highlightbackground=BORDER)
        res_card.pack(fill="both", expand=True, padx=PAD, pady=(14, 0))
 
        res_inner = tk.Frame(res_card, bg=CARD)
        res_inner.pack(fill="both", expand=True, padx=14, pady=12)
 
        tk.Label(res_inner, text="Result", font=("Helvetica", 10, "bold"),
                 bg=CARD, fg="#374151").pack(anchor="w")
 
        self._result_box = tk.Text(
            res_inner, height=20, font=FONT_MONO,
            bg="#F3F4F6", fg="#111827",
            relief="flat", bd=0, padx=8, pady=8,
            wrap="word", state="disabled",
            highlightthickness=1, highlightbackground=BORDER
        )
        self._result_box.pack(fill="both", expand=True, pady=(6, 0))

 
        #Bottom row for extra information
        bottom = tk.Frame(self, bg=BG)
        bottom.pack(fill="x", padx=PAD, pady=(10, PAD))
 
        self._status_var = tk.StringVar(value="Ready.")
        tk.Label(bottom, textvariable=self._status_var,
                 font=FONT_LABEL, bg=BG, fg=MUTED).pack(side="left")
 
        self._log_btn = tk.Button(
            bottom, text="Save log…", command=self._save_log,
            font=FONT_LABEL, bg="#F3F4F6", fg="#374151",
            activebackground=BORDER, relief="flat", bd=0,
            padx=10, pady=5, state="disabled", cursor="hand2",
            highlightthickness=1, highlightbackground=BORDER
        )
        self._log_btn.pack(side="right")
 
    #Functions
    def _pick_file(self):
        """Allows the user to select a file for upload"""
        path = filedialog.askopenfilename(
            title="Select input file",
            filetypes=[("Text / CSV files", "*.txt *.csv"), ("All files", "*.*")]
        )
        if path:
            self._selected_file.set(path)
            self._file_label.config(fg="#111827")
            self._run_btn.config(state="normal")
            self._set_result("")
            self._status_var.set("Ready.")
            self._log_btn.config(state="disabled")
 
    def _run(self):
        path = self._selected_file.get()
        if not path:
            return
        self._run_btn.config(state="disabled")
        self._log_btn.config(state="disabled")
        self._status_var.set("Running…")
        self._set_result("")
        threading.Thread(target=self._worker, args=(path,), daemon=True).start()
 
    def _worker(self, path: str):
        setup_logging()
        try:
            result = calc_nodes(path)
            self.after(0, self._on_success, str(result))
        except Exception as exc:
            logging.getLogger("calc").exception("Unhandled error")
            self.after(0, self._on_error, str(exc))
 
    def _on_success(self, result):
        """
        Displays the result in the result card and sets the status
        at the bottom to analysis complete
        """
        self._set_result(result)
        self._status_var.set("Analysis complete.")
        self._run_btn.config(state="normal")
        self._log_btn.config(state="normal")
 
    def _on_error(self, msg: str):
        """
        Displays the error message in the card
        and sets the status at the bottom to an error message
        """
        self._set_result(f"Error: {msg}")
        self._status_var.set("Something went wrong — see the log for details.")
        self._run_btn.config(state="normal")
        self._log_btn.config(state="normal")
 
    def _save_log(self):
        """
        Prompts the user to save the log file under a user-defined
        name
        """
        dest = filedialog.asksaveasfilename(
            title="Save log file", #title of directory when asked to save file
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt")]
        )
        if dest:
            shutil.copy2(LOG_PATH, dest)
            self._status_var.set(f"Log saved.")
 
    #Helper functions
    def _set_result(self, text):
        """
        Sets the text in the result card
        """
        self._result_box.config(state="normal")
        #Delete pre-existing text
        self._result_box.delete("1.0", "end")
        if text:
            self._result_box.insert("end", text)
        self._result_box.config(state="disabled")
 
    def _center(self):
        """
        Center function for the entire app
        """
        self.update_idletasks()
        #Set app width and height
        w, h = 700, self.winfo_reqheight()
        #Get x and y, of user's screen, then set the app location to center
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
 
 
if __name__ == "__main__":
    App().mainloop()
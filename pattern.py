import tkinter as tk
import json
import os
from math import hypot

PATTERN_FILE = "pattern.json"

class PatternLockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pattern Lock (Python Tkinter)")
        self.root.resizable(False, False)

        # Config
        self.size = 360
        self.margin = 40
        self.grid_n = 3
        self.dot_radius = 18
        self.min_points_required = 4

        # State
        self.dots = []              
        self.selected = []          
        self.line_ids = []         
        self.current_line = None    
        self.mode = tk.StringVar(value="verify") 
        
        # UI
        self.build_ui()
        self.load_pattern()
        self.draw_grid()

    # ------------------ UI ------------------
    def build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack()

        # Canvas for pattern
        self.canvas = tk.Canvas(top, width=self.size, height=self.size, bg="#fafafa", highlightthickness=0)
        self.canvas.grid(row=0, column=0, columnspan=3)
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_motion)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Controls
        tk.Label(top, text="Mode:").grid(row=1, column=0, sticky="e", pady=(10,0))
        mode_frame = tk.Frame(top)
        mode_frame.grid(row=1, column=1, pady=(10,0))
        tk.Radiobutton(mode_frame, text="Verify", variable=self.mode, value="verify").pack(side="left")
        tk.Radiobutton(mode_frame, text="Set Pattern", variable=self.mode, value="set").pack(side="left")

        tk.Button(top, text="Clear", command=self.clear_pattern).grid(row=1, column=2, sticky="w", padx=(10,0), pady=(10,0))

        # Info / status
        self.status = tk.Label(self.root, text="Draw pattern to verify or set.", fg="#333")
        self.status.pack(pady=(6,8))

        # Footer buttons
        footer = tk.Frame(self.root)
        footer.pack(pady=(0,10))
        tk.Button(footer, text="Save Pattern (Set Mode)", command=self.save_pattern).pack(side="left", padx=6)
        tk.Button(footer, text="Delete Saved Pattern", command=self.delete_saved_pattern).pack(side="left", padx=6)
        tk.Button(footer, text="Exit", command=self.root.quit).pack(side="left", padx=6)

    # ------------------ Grid & Drawing ------------------
    def draw_grid(self):
        self.canvas.delete("all")
        self.dots.clear()
        w = self.size
        n = self.grid_n
        gap = (w - 2*self.margin) / (n - 1)
        for r in range(n):
            for c in range(n):
                cx = self.margin + c * gap
                cy = self.margin + r * gap
                self.dots.append((cx, cy))
                # draw circle
                self.canvas.create_oval(cx-self.dot_radius, cy-self.dot_radius, cx+self.dot_radius, cy+self.dot_radius,
                                         fill="#ffffff", outline="#333", width=2, tags=("dot", f"dot{r*n+c}"))

        # If a saved pattern exists, show a subtle hint (dashed)
        if hasattr(self, "saved_pattern") and self.saved_pattern:
            self.draw_hint(self.saved_pattern)

    def draw_hint(self, pattern):
        # draw faint lines to show existing pattern (not necessary but helpful)
        coords = [self.dots[i] for i in pattern if 0 <= i < len(self.dots)]
        for i in range(len(coords)-1):
            x1,y1 = coords[i]; x2,y2 = coords[i+1]
            self.canvas.create_line(x1,y1,x2,y2, fill="#d0d0d0", dash=(3,5), width=3)

    def point_index_at(self, x, y):
        # returns index of dot under (x,y) or None
        for idx, (cx, cy) in enumerate(self.dots):
            if hypot(cx - x, cy - y) <= self.dot_radius + 6:
                return idx
        return None

    def on_press(self, event):
        self.clear_lines_temp()
        idx = self.point_index_at(event.x, event.y)
        if idx is not None:
            self.selected = [idx]
            self.highlight_dot(idx)
            self.status.config(text="Drawing pattern...")
        else:
            self.selected = []
            self.status.config(text="Start inside a dot to draw pattern.")

    def on_motion(self, event):
        # temp line from last selected dot to current cursor
        if not self.selected:
            return
        last_idx = self.selected[-1]
        x1,y1 = self.dots[last_idx]
        # remove previous temp line
        if self.current_line:
            self.canvas.delete(self.current_line)
            self.current_line = None
        self.current_line = self.canvas.create_line(x1,y1,event.x,event.y, fill="#007BFF", width=3)
        # check if moving over a new dot
        idx = self.point_index_at(event.x, event.y)
        if idx is not None and idx not in self.selected:
            # add permanent line between last and idx
            x2,y2 = self.dots[idx]
            line_id = self.canvas.create_line(x1,y1,x2,y2, fill="#007BFF", width=6, capstyle="round")
            self.line_ids.append(line_id)
            self.selected.append(idx)
            self.highlight_dot(idx)

    def on_release(self, event):
        # finalize pattern
        if self.current_line:
            self.canvas.delete(self.current_line)
            self.current_line = None
        if not self.selected:
            self.status.config(text="No pattern drawn.")
            return
        # show final result for a moment then verify or set
        pattern = self.selected.copy()
        self.status.config(text=f"Pattern drawn: {pattern}")
        if self.mode.get() == "verify":
            self.verify_pattern(pattern)
        else:
            self.status.config(text=f"Pattern ready to save (press 'Save Pattern (Set Mode)')")

    def highlight_dot(self, idx):
        cx, cy = self.dots[idx]
        # draw a filled circle on top to indicate selection
        self.canvas.create_oval(cx-self.dot_radius+6, cy-self.dot_radius+6, cx+self.dot_radius-6, cy+self.dot_radius-6,
                                fill="#007BFF", outline="", tags="selected")

    def clear_lines_temp(self):
        for lid in self.line_ids:
            self.canvas.delete(lid)
        self.line_ids = []
        self.canvas.delete("selected")
        if self.current_line:
            self.canvas.delete(self.current_line)
            self.current_line = None

    def clear_pattern(self):
        self.selected = []
        self.clear_lines_temp()
        self.draw_grid()
        self.status.config(text="Cleared. Draw pattern to verify or set.")

    # ------------------ Pattern Persistence & Logic ------------------
    def save_pattern(self):
        if not self.selected or len(self.selected) < self.min_points_required:
            self.status.config(text=f"Draw at least {self.min_points_required} points before saving.")
            return
        pattern = self.selected.copy()
        payload = {"pattern": pattern}
        try:
            with open(PATTERN_FILE, "w") as f:
                json.dump(payload, f)
            self.saved_pattern = pattern
            self.status.config(text="Pattern saved successfully!")
            self.clear_pattern()
        except Exception as e:
            self.status.config(text=f"Error saving pattern: {e}")

    def load_pattern(self):
        if os.path.exists(PATTERN_FILE):
            try:
                with open(PATTERN_FILE, "r") as f:
                    payload = json.load(f)
                self.saved_pattern = payload.get("pattern", [])
            except Exception:
                self.saved_pattern = []
        else:
            self.saved_pattern = []

    def delete_saved_pattern(self):
        if os.path.exists(PATTERN_FILE):
            try:
                os.remove(PATTERN_FILE)
                self.saved_pattern = []
                self.draw_grid()
                self.status.config(text="Saved pattern deleted.")
            except Exception as e:
                self.status.config(text=f"Error deleting pattern: {e}")
        else:
            self.status.config(text="No saved pattern to delete.")

    def verify_pattern(self, drawn):
        if not self.saved_pattern:
            self.status.config(text="No saved pattern. Switch to 'Set Pattern' and create one.")
            return
        if drawn == self.saved_pattern:
            self.status.config(text="Pattern correct — UNLOCKED ")
        else:
            self.status.config(text="Incorrect pattern — try again ")
        # auto-clear the drawn pattern after short delay
        self.root.after(800, self.clear_pattern)


if __name__ == "__main__":
    root = tk.Tk()
    app = PatternLockApp(root)
    root.mainloop()

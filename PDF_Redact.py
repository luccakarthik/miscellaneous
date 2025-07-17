import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io

class PDFRedactor:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced PDF Redactor")
        self.root.geometry("1200x800")
        
        # PDF document variables
        self.doc = None
        self.current_page = 0
        self.page_count = 0
        self.page_image = None
        self.tk_page_image = None
        self.zoom = 1.0
        
        # Redaction variables
        self.redaction_mode = None
        self.redaction_color = "black"
        self.redaction_items = []
        self.selected_item = None
        self.start_x = None
        self.start_y = None
        self.dragging = False
        self.drag_offset = (0, 0)
        
        # Signature variables
        self.signature_img = None
        self.signature_tk_img = None
        self.signature_items = []
        
        # Create main frames
        self.create_widgets()
        
        # Bind keyboard shortcuts
        self.root.bind("<Left>", self.prev_page)
        self.root.bind("<Right>", self.next_page)
        self.root.bind("<Control-s>", self.save_pdf)
        self.root.bind("<Delete>", self.delete_selected)

    def create_widgets(self):
        # Main container
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbox frame (left side)
        toolbox_frame = tk.Frame(main_frame, width=200, bg="#f0f0f0")
        toolbox_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        toolbox_frame.pack_propagate(False)
        
        # PDF viewer frame (center)
        viewer_frame = tk.Frame(main_frame, bg="gray")
        viewer_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas with scrollbars
        self.canvas = tk.Canvas(viewer_frame, bg="white", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Vertical scrollbar
        self.v_scroll = tk.Scrollbar(viewer_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Horizontal scrollbar
        self.h_scroll = tk.Scrollbar(viewer_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(yscrollcommand=self.v_scroll.set, xscrollcommand=self.h_scroll.set)
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        
        # Build all UI controls
        self.build_file_controls(toolbox_frame)
        self.build_navigation_controls(toolbox_frame)
        self.build_zoom_controls(toolbox_frame)
        self.build_redaction_controls(toolbox_frame)
        self.build_signature_controls(toolbox_frame)
        
        # Status bar
        self.status_bar = tk.Label(self.root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def build_file_controls(self, parent):
        file_frame = tk.LabelFrame(parent, text="File", padx=5, pady=5)
        file_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(file_frame, text="Open PDF", command=self.open_pdf).pack(fill=tk.X, pady=2)
        tk.Button(file_frame, text="Save PDF", command=self.save_pdf).pack(fill=tk.X, pady=2)

    def build_navigation_controls(self, parent):
        nav_frame = tk.LabelFrame(parent, text="Navigation", padx=5, pady=5)
        nav_frame.pack(fill=tk.X, padx=5, pady=5)
        nav_buttons = tk.Frame(nav_frame)
        nav_buttons.pack(fill=tk.X)
        tk.Button(nav_buttons, text="◄", command=self.prev_page).pack(side=tk.LEFT, expand=True)
        self.page_label = tk.Label(nav_buttons, text="Page: 0/0")
        self.page_label.pack(side=tk.LEFT, expand=True)
        tk.Button(nav_buttons, text="►", command=self.next_page).pack(side=tk.LEFT, expand=True)

    def build_zoom_controls(self, parent):
        zoom_frame = tk.LabelFrame(parent, text="Zoom", padx=5, pady=5)
        zoom_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(zoom_frame, text="Zoom In (+)", command=lambda: self.set_zoom(1.25)).pack(fill=tk.X, pady=2)
        tk.Button(zoom_frame, text="Zoom Out (-)", command=lambda: self.set_zoom(0.8)).pack(fill=tk.X, pady=2)
        tk.Button(zoom_frame, text="Fit Width", command=self.fit_width).pack(fill=tk.X, pady=2)
        tk.Button(zoom_frame, text="Fit Page", command=self.fit_page).pack(fill=tk.X, pady=2)

    def build_redaction_controls(self, parent):
        redact_frame = tk.LabelFrame(parent, text="Redaction Tools", padx=5, pady=5)
        redact_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(redact_frame, text="Rectangle", command=lambda: self.set_redaction_mode("rectangle")).pack(fill=tk.X, pady=2)
        tk.Button(redact_frame, text="Square", command=lambda: self.set_redaction_mode("square")).pack(fill=tk.X, pady=2)
        tk.Button(redact_frame, text="Select/Move", command=lambda: self.set_redaction_mode("select")).pack(fill=tk.X, pady=2)
        tk.Button(redact_frame, text="Delete Selected", command=self.delete_selected).pack(fill=tk.X, pady=2)
        
        color_frame = tk.LabelFrame(parent, text="Redaction Color", padx=5, pady=5)
        color_frame.pack(fill=tk.X, padx=5, pady=5)
        self.color_btn = tk.Button(color_frame, bg=self.redaction_color, command=self.choose_color)
        self.color_btn.pack(fill=tk.X, pady=2)

    def build_signature_controls(self, parent):
        sig_frame = tk.LabelFrame(parent, text="Signature", padx=5, pady=5)
        sig_frame.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(sig_frame, text="Add Signature", command=self.add_signature).pack(fill=tk.X, pady=2)
        tk.Button(sig_frame, text="Place Signature", command=lambda: self.set_redaction_mode("signature")).pack(fill=tk.X, pady=2)

    def on_canvas_motion(self, event):
        """Handle mouse motion on canvas"""
        if not self.doc:
            return
        
        # Get canvas coordinates
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        # Update status bar with position
        self.update_status(f"X: {int(x)}, Y: {int(y)}")
        
        # Change cursor based on mode
        if self.redaction_mode == "select":
            # Check if we're hovering over a selectable item
            hovering_item = False
            for item in self.redaction_items + self.signature_items:
                if item["page"] == self.current_page:
                    if "coords" in item:  # Redaction
                        x1, y1, x2, y2 = item["coords"]
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            hovering_item = True
                            break
                    else:  # Signature
                        sx, sy, sw, sh = item["coords"]
                        if sx <= x <= sx+sw and sy <= y <= sy+sh:
                            hovering_item = True
                            break
            
            self.canvas.config(cursor="hand2" if hovering_item else "arrow")
        elif self.redaction_mode in ["rectangle", "square", "signature"]:
            self.canvas.config(cursor="cross")

    def open_pdf(self):
        filepath = filedialog.askopenfilename(
            title="Open PDF",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        if filepath:
            try:
                self.doc = fitz.open(filepath)
                self.page_count = len(self.doc)
                self.current_page = 0
                self.page_label.config(text=f"Page: {self.current_page+1}/{self.page_count}")
                self.render_page()
                self.update_status(f"Opened: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open PDF:\n{str(e)}")
                self.update_status("Error opening PDF")

    def render_page(self):
        if self.doc is None or self.current_page >= self.page_count:
            return
        
        self.canvas.delete("all")
        page = self.doc.load_page(self.current_page)
        zoom_matrix = fitz.Matrix(self.zoom, self.zoom)
        pix = page.get_pixmap(matrix=zoom_matrix)
        
        img_data = pix.tobytes("ppm")
        img = Image.open(io.BytesIO(img_data))
        self.page_image = img
        self.tk_page_image = ImageTk.PhotoImage(image=img)
        
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_page_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
        
        self.draw_existing_redactions()
        self.draw_existing_signatures()

    def draw_existing_redactions(self):
        for item in self.redaction_items:
            if item["page"] == self.current_page:
                x1, y1, x2, y2 = item["coords"]
                fill = item["color"]
                outline = "red" if item == self.selected_item else "black"
                width = 2 if item == self.selected_item else 1
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=fill,
                    outline=outline,
                    width=width,
                    tags=("redaction", f"redact_{id(item)}")
                )

    def draw_existing_signatures(self):
        for item in self.signature_items:
            if item["page"] == self.current_page:
                x, y, width, height = item["coords"]
                img = item["image"].resize((width, height))
                tk_img = ImageTk.PhotoImage(image=img)
                item["tk_img"] = tk_img
                self.canvas.create_image(
                    x, y,
                    image=tk_img,
                    anchor=tk.NW,
                    tags=("signature", f"sig_{id(item)}")
                )
                if item == self.selected_item:
                    self.canvas.create_rectangle(
                        x, y, x+width, y+height,
                        outline="red",
                        width=2,
                        tags=("selection", f"sel_{id(item)}")
                    )

    def prev_page(self, event=None):
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.page_label.config(text=f"Page: {self.current_page+1}/{self.page_count}")
            self.render_page()

    def next_page(self, event=None):
        if self.doc and self.current_page < self.page_count - 1:
            self.current_page += 1
            self.page_label.config(text=f"Page: {self.current_page+1}/{self.page_count}")
            self.render_page()

    def set_zoom(self, factor):
        self.zoom *= factor
        if self.doc:
            self.render_page()

    def fit_width(self):
        if self.doc and self.page_image:
            canvas_width = self.canvas.winfo_width()
            img_width = self.page_image.width
            self.zoom = canvas_width / img_width
            self.render_page()

    def fit_page(self):
        if self.doc and self.page_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width = self.page_image.width
            img_height = self.page_image.height
            width_ratio = canvas_width / img_width
            height_ratio = canvas_height / img_height
            self.zoom = min(width_ratio, height_ratio)
            self.render_page()

    def set_redaction_mode(self, mode):
        self.redaction_mode = mode
        self.selected_item = None
        self.update_status(f"Mode: {mode.capitalize()}")
        if mode == "select":
            self.canvas.config(cursor="hand2")
        elif mode in ["rectangle", "square", "signature"]:
            self.canvas.config(cursor="cross")

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose redaction color")
        if color[1]:
            self.redaction_color = color[1]
            self.color_btn.config(bg=self.redaction_color)

    def add_signature(self):
        filepath = filedialog.askopenfilename(
            title="Select Signature Image",
            filetypes=(("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*"))
        )
        if filepath:
            try:
                img = Image.open(filepath)
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                self.signature_img = img
                self.update_status(f"Signature loaded: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load signature:\n{str(e)}")

    def on_canvas_click(self, event):
        if not self.doc:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.redaction_mode == "select":
            self.selected_item = None
            self.dragging = False
            
            for item in reversed(self.signature_items + self.redaction_items):
                if item["page"] == self.current_page:
                    if "coords" in item:  # Redaction
                        x1, y1, x2, y2 = item["coords"]
                        if x1 <= x <= x2 and y1 <= y <= y2:
                            self.selected_item = item
                            self.drag_offset = (x - x1, y - y1)
                            self.dragging = True
                            break
                    else:  # Signature
                        sx, sy, sw, sh = item["coords"]
                        if sx <= x <= sx+sw and sy <= y <= sy+sh:
                            self.selected_item = item
                            self.drag_offset = (x - sx, y - sy)
                            self.dragging = True
                            break
            
            self.render_page()
        elif self.redaction_mode in ["rectangle", "square", "signature"]:
            self.start_x = x
            self.start_y = y
            self.dragging = True

    def on_canvas_drag(self, event):
        if not self.doc or not self.dragging:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        
        if self.redaction_mode == "select" and self.selected_item:
            if "coords" in self.selected_item:  # Redaction
                x1, y1, x2, y2 = self.selected_item["coords"]
                dx = x - (x1 + self.drag_offset[0])
                dy = y - (y1 + self.drag_offset[1])
                self.selected_item["coords"] = (x1 + dx, y1 + dy, x2 + dx, y2 + dy)
            else:  # Signature
                sx, sy, sw, sh = self.selected_item["coords"]
                dx = x - (sx + self.drag_offset[0])
                dy = y - (sy + self.drag_offset[1])
                self.selected_item["coords"] = (sx + dx, sy + dy, sw, sh)
            
            self.render_page()
        elif self.redaction_mode in ["rectangle", "square", "signature"] and self.start_x is not None:
            self.canvas.delete("temp")
            
            if self.redaction_mode in ["rectangle", "square"]:
                if self.redaction_mode == "square":
                    size = max(abs(x - self.start_x), abs(y - self.start_y))
                    x = self.start_x + size if x > self.start_x else self.start_x - size
                    y = self.start_y + size if y > self.start_y else self.start_y - size
                
                self.canvas.create_rectangle(
                    self.start_x, self.start_y, x, y,
                    fill=self.redaction_color,
                    outline="black",
                    width=1,
                    tags="temp"
                )
            elif self.redaction_mode == "signature" and self.signature_img:
                width = max(10, abs(x - self.start_x))
                height = max(10, abs(y - self.start_y))
                temp_img = self.signature_img.resize((int(width), int(height)))
                temp_tk_img = ImageTk.PhotoImage(image=temp_img)
                self.canvas.create_image(
                    min(self.start_x, x), min(self.start_y, y),
                    image=temp_tk_img,
                    anchor=tk.NW,
                    tags="temp"
                )
                self.canvas.temp_img = temp_tk_img

    def on_canvas_release(self, event):
        if not self.doc or not self.dragging:
            return
        
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        self.canvas.delete("temp")
        
        if self.redaction_mode in ["rectangle", "square"] and self.start_x is not None:
            if abs(x - self.start_x) > 5 and abs(y - self.start_y) > 5:
                if self.redaction_mode == "square":
                    size = max(abs(x - self.start_x), abs(y - self.start_y))
                    x = self.start_x + size if x > self.start_x else self.start_x - size
                    y = self.start_y + size if y > self.start_y else self.start_y - size
                
                redaction = {
                    "page": self.current_page,
                    "coords": (min(self.start_x, x), min(self.start_y, y), 
                              max(self.start_x, x), max(self.start_y, y)),
                    "color": self.redaction_color,
                    "type": self.redaction_mode
                }
                self.redaction_items.append(redaction)
        
        elif self.redaction_mode == "signature" and self.start_x is not None and self.signature_img:
            width = max(10, abs(x - self.start_x))
            height = max(10, abs(y - self.start_y))
            signature = {
                "page": self.current_page,
                "coords": (min(self.start_x, x), min(self.start_y, y), width, height),
                "image": self.signature_img,
                "tk_img": None
            }
            self.signature_items.append(signature)
        
        self.start_x = None
        self.start_y = None
        self.dragging = False
        self.render_page()

    def delete_selected(self, event=None):
        if self.selected_item:
            if self.selected_item in self.redaction_items:
                self.redaction_items.remove(self.selected_item)
            elif self.selected_item in self.signature_items:
                self.signature_items.remove(self.selected_item)
            self.selected_item = None
            self.render_page()

    def save_pdf(self, event=None):
        if not self.doc:
            messagebox.showerror("Error", "No PDF document is open!")
            return
        
        filepath = filedialog.asksaveasfilename(
            title="Save Redacted PDF",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")))
        
        if filepath:
            try:
                temp_doc = fitz.open()
                
                for page_num in range(self.page_count):
                    page = self.doc.load_page(page_num)
                    new_page = temp_doc.new_page(width=page.rect.width, height=page.rect.height)
                    new_page.show_pdf_page(new_page.rect, self.doc, page_num)
                    
                    # Add redactions
                    for item in self.redaction_items:
                        if item["page"] == page_num:
                            x1, y1, x2, y2 = item["coords"]
                            pdf_x1 = x1 / self.zoom
                            pdf_y1 = y1 / self.zoom
                            pdf_x2 = x2 / self.zoom
                            pdf_y2 = y2 / self.zoom
                            rect = fitz.Rect(pdf_x1, pdf_y1, pdf_x2, pdf_y2)
                            color = fitz.utils.getColor(item["color"])
                            new_page.draw_rect(rect, color=color, fill=color, overlay=True)
                    
                    # Add signatures
                    for item in self.signature_items:
                        if item["page"] == page_num:
                            x, y, width, height = item["coords"]
                            pdf_x = x / self.zoom
                            pdf_y = y / self.zoom
                            pdf_width = width / self.zoom
                            pdf_height = height / self.zoom
                            img_bytes = io.BytesIO()
                            resized_img = item["image"].resize((int(pdf_width), int(pdf_height)))
                            resized_img.save(img_bytes, format="PNG")
                            img_bytes.seek(0)
                            rect = fitz.Rect(pdf_x, pdf_y, pdf_x + pdf_width, pdf_y + pdf_height)
                            new_page.insert_image(rect, stream=img_bytes)
                
                temp_doc.save(filepath)
                temp_doc.close()
                messagebox.showinfo("Success", f"PDF saved successfully to:\n{filepath}")
                self.update_status(f"Saved: {os.path.basename(filepath)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PDF:\n{str(e)}")
                self.update_status("Error saving PDF")

    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()

def main():
    root = tk.Tk()
    
    # This prevents immediate closing
    root.withdraw()  # Hide temporarily
    root.after(100, lambda: root.deiconify())  # Show after short delay
    
    app = PDFRedactor(root)
    
    # Center the window on screen
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()

if __name__ == "__main__":
    # Add error handling
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to close...")  # Keeps window open to see error

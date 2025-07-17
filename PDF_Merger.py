import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PyPDF2 import PdfMerger

class PDFMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Merger")
        self.root.geometry("600x400")
        
        # Variables
        self.pdf_files = []
        self.output_filename = tk.StringVar(value="merged.pdf")
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        # Frame for PDF list
        list_frame = tk.LabelFrame(self.root, text="PDF Files to Merge", padx=5, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Listbox with scrollbar
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.config(command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Add/Remove buttons
        add_btn = tk.Button(control_frame, text="Add PDF(s)", command=self.add_pdfs)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        remove_btn = tk.Button(control_frame, text="Remove Selected", command=self.remove_pdf)
        remove_btn.pack(side=tk.LEFT, padx=5)
        
        move_up_btn = tk.Button(control_frame, text="Move Up", command=self.move_up)
        move_up_btn.pack(side=tk.LEFT, padx=5)
        
        move_down_btn = tk.Button(control_frame, text="Move Down", command=self.move_down)
        move_down_btn.pack(side=tk.LEFT, padx=5)
        
        # Output file frame
        output_frame = tk.LabelFrame(self.root, text="Output File", padx=5, pady=5)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Output file entry and browse button
        output_entry = tk.Entry(output_frame, textvariable=self.output_filename)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_btn = tk.Button(output_frame, text="Browse...", command=self.browse_output)
        browse_btn.pack(side=tk.RIGHT, padx=5)
        
        # Merge button
        merge_btn = tk.Button(self.root, text="Merge PDFs", command=self.merge_pdfs, bg="#4CAF50", fg="white")
        merge_btn.pack(fill=tk.X, padx=10, pady=10)
        
    def add_pdfs(self):
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        if files:
            for file in files:
                if file not in self.pdf_files:
                    self.pdf_files.append(file)
                    self.listbox.insert(tk.END, os.path.basename(file))
    
    def remove_pdf(self):
        selection = self.listbox.curselection()
        if selection:
            index = selection[0]
            self.listbox.delete(index)
            self.pdf_files.pop(index)
    
    def move_up(self):
        selection = self.listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            # Swap in list
            self.pdf_files[index], self.pdf_files[index-1] = self.pdf_files[index-1], self.pdf_files[index]
            # Update listbox
            item1 = self.listbox.get(index)
            item2 = self.listbox.get(index-1)
            self.listbox.delete(index-1, index+1)
            self.listbox.insert(index-1, item1)
            self.listbox.insert(index, item2)
            self.listbox.selection_set(index-1)
    
    def move_down(self):
        selection = self.listbox.curselection()
        if selection and selection[0] < len(self.pdf_files)-1:
            index = selection[0]
            # Swap in list
            self.pdf_files[index], self.pdf_files[index+1] = self.pdf_files[index+1], self.pdf_files[index]
            # Update listbox
            item1 = self.listbox.get(index)
            item2 = self.listbox.get(index+1)
            self.listbox.delete(index, index+2)
            self.listbox.insert(index, item2)
            self.listbox.insert(index+1, item1)
            self.listbox.selection_set(index+1)
    
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*")),
            initialfile=self.output_filename.get()
        )
        if filename:
            self.output_filename.set(filename)
    
    def merge_pdfs(self):
        if not self.pdf_files:
            messagebox.showerror("Error", "No PDF files selected!")
            return
        
        output_path = self.output_filename.get()
        if not output_path:
            messagebox.showerror("Error", "Please specify an output file!")
            return
        
        try:
            merger = PdfMerger()
            
            # Add a progress bar
            progress = tk.Toplevel(self.root)
            progress.title("Merging PDFs...")
            progress.geometry("300x100")
            
            label = tk.Label(progress, text="Merging PDF files...")
            label.pack(pady=5)
            
            progress_bar = ttk.Progressbar(progress, orient="horizontal", length=250, mode="determinate")
            progress_bar.pack(pady=5)
            
            self.root.update()
            
            # Add each PDF to the merger
            for i, pdf in enumerate(self.pdf_files):
                merger.append(pdf)
                progress_bar["value"] = (i + 1) / len(self.pdf_files) * 100
                progress.update()
            
            # Write the merged PDF
            with open(output_path, "wb") as f:
                merger.write(f)
            
            progress.destroy()
            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved to: {output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")
            if 'progress' in locals():
                progress.destroy()

def main():
    root = tk.Tk()
    app = PDFMergerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import PyPDF2
import os

class PasswordRemoverApp:
    """
    A GUI application to remove passwords from multiple PDF files.
    """
    def __init__(self, root):
        """
        Initializes the application window and its widgets.
        """
        self.root = root
        self.root.title("PDF Password Remover")
        self.root.geometry("500x250")
        self.root.configure(bg="#f0f0f0")

        self.file_paths = []

        # --- UI Elements ---
        # Frame for better organization
        main_frame = tk.Frame(self.root, bg="#f0f0f0", padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # Title Label
        title_label = tk.Label(main_frame, text="PDF Password Remover", font=("Helvetica", 18, "bold"), bg="#f0f0f0")
        title_label.pack(pady=(0, 20))

        # Button to select PDF files
        self.select_button = tk.Button(main_frame, text="Select PDF Files", command=self.select_files, font=("Helvetica", 12), bg="#4a90e2", fg="white", relief=tk.FLAT, padx=10, pady=5)
        self.select_button.pack(pady=10)

        # Label to show how many files are selected
        self.status_label = tk.Label(main_frame, text="No files selected.", font=("Helvetica", 10), bg="#f0f0f0")
        self.status_label.pack(pady=5)

        # Button to start the password removal process
        self.remove_button = tk.Button(main_frame, text="Remove Passwords", command=self.start_removal_process, font=("Helvetica", 12, "bold"), bg="#50e3c2", fg="white", relief=tk.FLAT, padx=10, pady=5, state=tk.DISABLED)
        self.remove_button.pack(pady=20)

    def select_files(self):
        """
        Opens a file dialog to select multiple PDF files.
        """
        # Ask the user to select one or more PDF files
        self.file_paths = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=(("PDF files", "*.pdf"), ("All files", "*.*"))
        )
        
        # Update the status label with the number of selected files
        if self.file_paths:
            self.status_label.config(text=f"{len(self.file_paths)} file(s) selected.")
            self.remove_button.config(state=tk.NORMAL) # Enable the remove button
        else:
            self.status_label.config(text="No files selected.")
            self.remove_button.config(state=tk.DISABLED) # Disable if no files are selected

    def start_removal_process(self):
        """
        Initiates the password removal workflow based on user choice.
        """
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select PDF files first.")
            return

        # Ask the user if all PDFs have the same password
        same_password = messagebox.askyesno("Password Option", "Do all the selected PDF files have the same password?")

        if same_password:
            self.process_with_same_password()
        else:
            self.process_with_different_passwords()

    def process_with_same_password(self):
        """
        Handles the case where all PDFs share a single password.
        """
        # Ask for the common password once
        password = simpledialog.askstring("Password", "Enter the password for all PDFs:", show='*')
        
        if not password:
            messagebox.showinfo("Cancelled", "Operation cancelled.")
            return

        successful_unlocks = 0
        failed_files = []

        # Try to unlock each file with the provided password
        for file_path in self.file_paths:
            if self.remove_password(file_path, password):
                successful_unlocks += 1
            else:
                failed_files.append(os.path.basename(file_path))
        
        self.show_summary(successful_unlocks, failed_files)

    def process_with_different_passwords(self):
        """
        Handles the case where each PDF has a different password.
        """
        successful_unlocks = 0
        failed_files = []

        # Loop through each file and ask for its specific password
        for file_path in self.file_paths:
            filename = os.path.basename(file_path)
            password = simpledialog.askstring("Password", f"Enter password for:\n{filename}", show='*')
            
            if password is None: # User cancelled the dialog
                messagebox.showinfo("Cancelled", "Operation cancelled for remaining files.")
                break

            if self.remove_password(file_path, password):
                successful_unlocks += 1
            else:
                failed_files.append(filename)
                
        self.show_summary(successful_unlocks, failed_files)

    def remove_password(self, file_path, password):
        """
        Attempts to decrypt a single PDF file and save an unlocked version.

        Args:
            file_path (str): The path to the PDF file.
            password (str): The password to try for decryption.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                
                # Check if the PDF is actually encrypted
                if not reader.is_encrypted:
                    messagebox.showinfo("Not Encrypted", f"The file '{os.path.basename(file_path)}' is not encrypted.")
                    # We can consider this a "success" as the goal is an unlocked PDF
                    return True

                # Attempt to decrypt with the password
                if reader.decrypt(password):
                    writer = PyPDF2.PdfWriter()
                    # Add all pages from the decrypted reader to the writer
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    # Create the new filename for the unlocked PDF
                    directory, filename = os.path.split(file_path)
                    new_filename = filename.replace(".pdf", "_unlocked.pdf")
                    new_filepath = os.path.join(directory, new_filename)
                    
                    # Save the new, unlocked PDF
                    with open(new_filepath, 'wb') as new_file:
                        writer.write(new_file)
                    return True
                else:
                    # Password was incorrect
                    return False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred with file {os.path.basename(file_path)}:\n{e}")
            return False

    def show_summary(self, successful_count, failed_list):
        """
        Displays a summary of the password removal operation.
        """
        total_files = len(self.file_paths)
        summary_message = f"Operation Complete!\n\nSuccessfully unlocked: {successful_count}/{total_files}\n"
        
        if failed_list:
            summary_message += "\nFailed to unlock (check passwords):\n- " + "\n- ".join(failed_list)
            
        messagebox.showinfo("Summary", summary_message)
        # Reset the state after the operation
        self.file_paths = []
        self.status_label.config(text="No files selected.")
        self.remove_button.config(state=tk.DISABLED)


if __name__ == "__main__":
    # To run this script, you need to have PyPDF2 installed.
    # You can install it using pip:
    # pip install PyPDF2
    
    root = tk.Tk()
    app = PasswordRemoverApp(root)
    root.mainloop()

import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext

# Set up the main window
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Private Key to WIF Converter")

    # Create a frame for content with some padding
    frame = ttk.Frame(root, padding="10")
    frame.grid(row=0, column=0, sticky="nsew")
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)

    # Input label
    input_label = ttk.Label(frame, text="Enter Private Keys (hex, one per line):")
    input_label.grid(row=0, column=0, columnspan=2, sticky="w")

    # Input text area (with scrollbars)
    text_input = scrolledtext.ScrolledText(frame, width=80, height=10, wrap="none")
    text_input.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Checkboxes for options
    compressed_var = tk.BooleanVar(value=True)
    uncompressed_var = tk.BooleanVar(value=True)
    chk_compressed = ttk.Checkbutton(frame, text="Compressed", variable=compressed_var)
    chk_uncompressed = ttk.Checkbutton(frame, text="Uncompressed", variable=uncompressed_var)
    chk_compressed.grid(row=2, column=0, sticky="w", padx=5, pady=5)
    chk_uncompressed.grid(row=2, column=1, sticky="e", padx=5, pady=5)

    # Convert button
    convert_button = ttk.Button(frame, text="Convert", command=convert_keys)
    convert_button.grid(row=3, column=0, columnspan=2, pady=5)

    # Output label
    output_label = ttk.Label(frame, text="Results:")
    output_label.grid(row=4, column=0, columnspan=2, sticky="w")

    # Output text area (with scrollbars)
    output = scrolledtext.ScrolledText(frame, width=80, height=15, wrap="none")
    output.grid(row=5, column=0, columnspan=2, padx=5, pady=5)
    output.configure(state="normal")  # Allow selection and copying

    # Start the GUI event loop
    root.mainloop() 
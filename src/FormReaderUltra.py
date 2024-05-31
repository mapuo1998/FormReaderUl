import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import shutil
import os
import fitz
import requests
import base64
import json
import threading

# Global variables
image_label = None
preview_images = []
current_page = 0
total_pages = 0
google_access_token = ""
successful_ocr_count = 0  # Track successful OCR processing count

# Function to refresh the Google access token
def refresh_access_token():
    global google_access_token
    credentials_data = {
        "client_id": "****",
        "client_secret": "****",
        "refresh_token": "****",
        "grant_type": "refresh_token"
    }
    response = requests.post("https://oauth2.googleapis.com/token", data=credentials_data)
    if response.status_code == 200:
        token_data = response.json()
        google_access_token = token_data.get("access_token", "")
    else:
        messagebox.showerror("Error", f"Failed to refresh access token: {response.text}")

# Refresh Google access token on program start
refresh_access_token() 

# Function to handle file selection
def select_file(event=None):
    global preview_images, current_page, total_pages
    file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
    for file_path in file_paths:
        print("Selected file:", file_path)
        if file_path:
            copy_to_pdf_window(file_path)
            preview_images = extract_preview_images(file_path)
            total_pages = len(preview_images)
            current_page = 0
            display_preview()

# Function to extract preview images from PDF using PyMuPDF
def extract_preview_images(pdf_path):
    images = []
    pdf_document = fitz.open(pdf_path)
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        image = page.get_pixmap()
        img = Image.frombytes("RGB", [image.width, image.height], image.samples)
        max_width = 300
        max_height = 400
        img.thumbnail((max_width, max_height))
        images.append(img)
    return images

# Function to copy selected file to pdf_window folder
def copy_to_pdf_window(file_path):
    try:
        destination_folder = os.path.join(os.path.dirname(__file__), "pdf_window")
        shutil.copy2(file_path, destination_folder)
        populate_file_tree()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy file to pdf_window: {e}")

# Function to perform OCR on a PDF file using Document AI API
def perform_ocr():
    selected_items = file_tree.selection()
    if selected_items:
        for selected_item in selected_items:
            file_name = file_tree.item(selected_item, "text")
            file_path = os.path.join(os.path.dirname(__file__), "pdf_window", file_name)
            loading_screen = create_loading_screen()  # Create loading screen
            threading.Thread(target=process_file_with_loading_screen, args=(file_path, loading_screen)).start()  # Start OCR process in a separate thread
    else:
        messagebox.showwarning("Warning", "Please select file(s) to perform OCR.")

# Function to process file with loading screen
def process_file_with_loading_screen(file_path, loading_screen):
    global successful_ocr_count
    try:
        with open(file_path, "rb") as file:
            encoded_content = base64.b64encode(file.read()).decode('utf-8')

        request_body = {
            "skipHumanReview": True,
            "rawDocument": {
                "mimeType": "application/pdf",
                "content": encoded_content
            }
        }

        endpoint = "****"
        headers = {
            "Authorization": f"Bearer {google_access_token}",
            "Content-Type": "application/json; charset=utf-8"
        }

        response = requests.post(endpoint, headers=headers, json=request_body)
        if response.status_code == 200:
            result = response.json()
            ocr_text = result["document"]["text"]
            pdf_file_name = os.path.splitext(os.path.basename(file_path))[0]
            write_text_to_file(pdf_file_name, ocr_text)
            write_json_response(result, pdf_file_name)
            populate_file_tree_processed()

            # Extract mention text after successful OCR processing
            json_file_path = os.path.join(os.path.dirname(__file__), "text_window", f"{pdf_file_name}.json")
            output_file_path = os.path.join(os.path.dirname(__file__), "text_window", f"{pdf_file_name}.txt")
            extract_mention_text(json_file_path, output_file_path)

            # Increment the counter for successful OCR processing
            successful_ocr_count += 1

        else:
            messagebox.showerror("Error", f"Failed to perform OCR. Error code: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to perform OCR: {e}")

    finally:
        loading_screen.destroy()  # Destroy loading screen when processing is complete

        # Display the success message if all selected files have been processed
        if successful_ocr_count == len(file_tree.selection()):
            messagebox.showinfo("Success", "OCR completed successfully. Please check Processed tab.")

# Function to create a loading screen with progress bar
def create_loading_screen():
    loading_screen = tk.Toplevel(root)
    loading_screen.title("Processing File")
    loading_screen.geometry("300x100")

    loading_label = tk.Label(loading_screen, text="Scanning in process...")
    loading_label.pack(expand=True)

    progress_bar = ttk.Progressbar(loading_screen, orient="horizontal", length=200, mode="indeterminate")
    progress_bar.pack(pady=10)
    progress_bar.start()  # Start the progress bar animation

    # Position loading screen in the middle of the main window
    x_position = root.winfo_x() + root.winfo_width() // 2 - loading_screen.winfo_reqwidth() // 2
    y_position = root.winfo_y() + root.winfo_height() // 2 - loading_screen.winfo_reqheight() // 2
    loading_screen.geometry("+{}+{}".format(x_position, y_position))

    return loading_screen

# Function to write OCR'd text to a text file in text_window folder
def write_text_to_file(pdf_file_name, ocr_text):
    try:
        destination_folder = os.path.join(os.path.dirname(__file__), "text_window")
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        text_file_path = os.path.join(destination_folder, f"{pdf_file_name}.txt")
        with open(text_file_path, 'w') as text_file:
            text_file.write(ocr_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write text file: {e}")

# Function to write JSON response to a file
def write_json_response(json_data, pdf_file_name):
    try:
        destination_folder = os.path.join(os.path.dirname(__file__), "text_window")
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        json_file_path = os.path.join(destination_folder, f"{pdf_file_name}.json")  # Use the PDF file name for the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write JSON file: {e}")

# Function to delete selected files
def delete_files():
    selected_items = file_tree.selection()
    if selected_items:
        for selected_item in selected_items:
            file_name = file_tree.item(selected_item, "text")
            file_path = os.path.join(os.path.dirname(__file__), "pdf_window", file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {file_name}: {e}")
        populate_file_tree()
    else:
        messagebox.showwarning("Warning", "Please select file(s) to delete.")

# Function to delete selected text files
def delete_text_files():
    selected_items = processed_file_tree.selection()
    if selected_items:
        for selected_item in selected_items:
            file_name = processed_file_tree.item(selected_item, "text")
            file_path = os.path.join(os.path.dirname(__file__), "text_window", file_name)
            try:
                os.remove(file_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete {file_name}: {e}")
        populate_file_tree_processed()
    else:
        messagebox.showwarning("Warning", "Please select file(s) to delete.")

# Function to refresh the file tree
def refresh_file_tree():
    populate_file_tree()

# Function to populate the file tree
def populate_file_tree():
    directory = os.path.join(os.path.dirname(__file__), "pdf_window")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_tree.delete(*file_tree.get_children())
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)):
            file_tree.insert("", "end", text=item)

# Function to populate the processed file tree with only text files
def populate_file_tree_processed():
    directory = os.path.join(os.path.dirname(__file__), "text_window")
    if not os.path.exists(directory):
        os.makedirs(directory)
    processed_file_tree.delete(*processed_file_tree.get_children())
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)) and item.endswith(".txt"):
            processed_file_tree.insert("", "end", text=item)

# Function to display preview of selected file
def display_preview(event=None):
    global current_page, preview_images, total_pages
    selected_items = file_tree.selection()
    if not selected_items:
        return
    for selected_item in selected_items:
        file_name = file_tree.item(selected_item, "text")
        file_path = os.path.join(os.path.dirname(__file__), "pdf_window", file_name)
        preview_images = extract_preview_images(file_path)
        total_pages = len(preview_images)
        current_page = 0
        render_preview(preview_images[current_page])

# Function to render the preview image
def render_preview(image):
    global image_label
    if image_label:
        image_label.destroy()
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(preview_frame, image=photo)
    image_label.image = photo
    image_label.pack(padx=10, pady=10)

# Function to handle window close event
def on_closing():
    delete_files_in_directory(os.path.join(os.path.dirname(__file__), "pdf_window"))
    delete_files_in_directory(os.path.join(os.path.dirname(__file__), "text_window"))
    root.destroy()

# Function to delete files in a directory
def delete_files_in_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to delete {file_path}: {e}")

# Function to display preview of selected text file
def display_text_preview(event=None):
    selected_items = processed_file_tree.selection()  # Get selected files from processed file tree
    if selected_items:
        file_name = processed_file_tree.item(selected_items[0], "text")  # Get the name of the selected file
        file_path = os.path.join(os.path.dirname(__file__), "text_window", file_name)  # Construct file path
        try:
            with open(file_path, 'r') as file:
                text_content = file.read()  # Read text content from file
                text_preview.config(state="normal")  # Enable editing temporarily
                text_preview.delete('1.0', tk.END)  # Clear previous content
                text_preview.insert(tk.END, text_content)  # Insert new content
                text_preview.config(state="disabled")  # Disable editing
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open text file: {e}")
    else:
        messagebox.showwarning("Warning", "Please select a text file to preview.")

# Function to extract mention text from JSON data
def extract_mention_text(json_file_path, output_file_path):
    try:
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
            document = data.get('document', {})
            entities = document.get('entities', [])
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Malformed JSON data in file '{json_file_path}'.")
        return

    mention_texts = []
    for field_number in range(4, 35):
        for entity in entities:
            if 'field-' in entity['type']:
                field_num = int(entity['type'].split('-')[1])
                if field_num == field_number:
                    mention_texts.append((entity['type'], entity['mentionText']))
                    break

    with open(output_file_path, 'w') as output_file:
        for field_name, text in mention_texts:
            output_file.write(f"{field_name}: {text}\n")

    print(f"Extracted 'mentionText' values with field names written to {output_file_path}")

# Function to copy selected text to clipboard
def copy_text():
    selected_text = text_preview.get("sel.first", "sel.last")
    if selected_text:
        root.clipboard_clear()  # Clear the clipboard
        root.clipboard_append(selected_text)  # Copy selected text to clipboard
        root.update()  # Update clipboard
        messagebox.showinfo("Copy", "Selected text has been copied to clipboard.")
    else:
        messagebox.showwarning("Warning", "Please select text to copy.")

# Create the main window
root = tk.Tk()
root.title("FormReaderUltra")

# Set the window size and position
window_width = 800
window_height = 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Create a Notebook (Tabbed) interface
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

# Create "Raw" tab
raw_tab = ttk.Frame(notebook)
notebook.add(raw_tab, text="Raw")

# Create a frame for the buttons
button_frame = tk.Frame(raw_tab)
button_frame.pack(side=tk.TOP, padx=10, pady=10)

# Create a button for file selection
select_button = tk.Button(button_frame, text="Select PDF File", command=select_file)
select_button.pack(side=tk.LEFT, padx=10)

# Add buttons for file operations
delete_button = tk.Button(button_frame, text="Delete Selected File(s)", command=delete_files)
delete_button.pack(side=tk.LEFT, padx=10)

# Create a button for reading files
read_button = tk.Button(button_frame, text="Read File(s)", command=perform_ocr)
read_button.pack(side=tk.LEFT, padx=10)

# Create a frame for the file items with a gray border
file_frame = tk.Frame(raw_tab, bd=2, relief="groove")
file_frame.pack(side=tk.LEFT, fill=tk.Y)

# Add a Treeview widget to display files
file_tree = ttk.Treeview(file_frame)
file_tree.heading("#0", text="File Name")

file_tree.pack(side=tk.TOP, expand=True, fill=tk.Y, padx=10, pady=10)

# Bind events
file_tree.bind("<ButtonRelease-1>", lambda event: display_preview())
root.bind("<Delete>", lambda event: delete_files())

# Create a frame for the preview images with a gray border
preview_frame = tk.Frame(raw_tab, bd=2, relief="groove")
preview_frame.pack(fill=tk.BOTH, expand=True)

# Create "Processed" tab
processed_tab = ttk.Frame(notebook)
notebook.add(processed_tab, text="Processed")

# Create a frame for the buttons in the Processed tab
processed_button_frame = tk.Frame(processed_tab, bd=0, relief="flat")
processed_button_frame.pack(side=tk.TOP, padx=10, pady=10)

# Add buttons for file operations in the Processed tab
processed_delete_button = tk.Button(processed_button_frame, text="Delete Selected File(s)", command=delete_text_files)
processed_delete_button.pack(side=tk.LEFT, padx=10)

# Create a Copy button to copy selected text
copy_button = tk.Button(processed_button_frame, text="Copy", command=copy_text)
copy_button.pack(side=tk.LEFT, padx=10)

# Create a frame for the file items with a gray border in the Processed tab
processed_file_frame = tk.Frame(processed_tab, bd=2, relief="groove")
processed_file_frame.pack(side=tk.LEFT, fill=tk.Y)

# Add a Treeview widget to display files in the Processed tab
processed_file_tree = ttk.Treeview(processed_file_frame)
processed_file_tree.heading("#0", text="File Name")

processed_file_tree.pack(side=tk.TOP, expand=True, fill=tk.Y, padx=10, pady=10)

# Create a frame for the preview text with a gray border in the Processed tab
processed_preview_frame = tk.Frame(processed_tab, bd=2, relief="groove")
processed_preview_frame.pack(fill=tk.BOTH, expand=True)

# Create a Text widget to display text preview
text_preview = tk.Text(processed_preview_frame, wrap="word", height=20, width=80)
text_preview.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Bind event to display text preview
processed_file_tree.bind("<ButtonRelease-1>", lambda event: display_text_preview())

# Populate the file trees initially
populate_file_tree()
populate_file_tree_processed()

# Bind window close event to on_closing function
root.protocol("WM_DELETE_WINDOW", on_closing)

# Run the Tkinter event loop
root.mainloop()

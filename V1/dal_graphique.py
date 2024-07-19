# Import necessary libraries
import tkinter as tk
from tkinter import filedialog, Label, Button, Toplevel, Message, Frame
from data_day_by_day import save_dataframe, pbp_data, data_dbd  # Import functions from data_day_by_day module
from data_pass_by_pass import pbp_data, data_cleaned_without_week, data_cleaned_with_week  # Import functions from data_pass_by_pass module
from SIGPA import data_for_sigpa  # Import function from SIGPA module
import pandas as pd  # Import pandas library for data manipulation
from datetime import datetime  # Import datetime module for date handling
import zipfile  # Import zipfile module for ZIP file operations
import csv  # Import csv module for CSV file operations
import os  # Import os module for operating system functionalities

"""
Summary:
This script sets up a graphical user interface (GUI) using tkinter for data modification and extraction related to DAL data. 
It integrates functionalities for extracting day-by-day data, pass-by-pass data, and SIGPA data from raw data files. 
The GUI allows users to input necessary parameters, select files, and trigger data extraction and processing operations.
"""

info_window = None
nb = 0
scrollable_frame = None
aliment = 1

def show_info(info,main=None):
    """Display information in a pop-up window.

    Args:
        info (str): Text to display in the information window.
    """
    global info_window  # Global variable to track the info window

    # Check if info_window is not initialized or if it does not exist anymore
    if info_window is None or not info_window.winfo_exists():
        # Create a new top-level window for displaying information
        info_window = Toplevel(main)
        info_window.title("Information")
        info_window.resizable(False, False)

        # Create a message widget to display the information text
        message = Message(info_window, text=info, width=200)
        message.pack(padx=10, pady=10)

        # Create a button to close the information window
        button = Button(info_window, text="OK", command=close_info)
        button.pack(pady=5)

def close_info(main=None):
    """Close the information window."""
    global info_window
    
    # Check if info_window is not None before attempting to destroy it
    if info_window is not None:
        info_window.destroy()  # Destroy the info_window
        info_window = None  # Reset info_window to None after destruction       

def limit_text_length(event, text_widget, max_length,main=None):
    """Limit the text length in a text widget.

    Args:
        event: The event triggering the text limit check.
        text_widget: The text widget where the text length is limited.
        max_length (int): The maximum allowed length of the text.

    Returns:
        str: "break" to prevent further processing of the event if the text exceeds max_length.
    """
    content = text_widget.get("1.0", "end-1c")  # Get the current content of the text widget
    if len(content) > max_length:
        text_widget.delete("1.0", "end")  # Delete the entire content of the text widget
        text_widget.insert("1.0", content[:max_length])  # Insert only the first max_length characters of the content
        return "break"  # Return "break" to prevent further processing of the event

def browse_files(entry_filename, path,main=None):
    """Open a file dialog to browse and select files or folders.

    Args:
        entry_filename (tk.Entry): Entry widget to display the selected file or folder path.
        path (str): Specifies whether to select a 'file' or a 'folder'.

    Returns:
        None
    """
    # Create a new window for file/folder selection
    selection_window = tk.Tk()
    selection_window.withdraw()  # Hide the main window

    if path == 'file':
        # Open file dialog to select a file
        filename = filedialog.askopenfilename(initialdir="/",
                                              title="Select a File",
                                              filetypes=(("All files", "*.*"), ("ZIP files", "*.zip*"), ("CSV files", "*.csv*")))
    else:
        # Open file dialog to select a folder
        filename = filedialog.askdirectory(initialdir="/", title="Select a Folder")

    entry_filename.delete(0, tk.END)  # Clear previous text in entry widget
    entry_filename.insert(tk.END, filename)  # Insert selected file/folder path into entry widget
    selection_window.destroy()  # Close the file/folder selection window

def desact_lf(name, lf,main=None):
    """Disable or enable widgets within a tkinter frame based on a condition.

    Args:
        name (tk.StringVar): String variable to check for condition.
        lf (tk.Frame): Frame containing widgets to be disabled or enabled.

    Returns:
        None
    """
    # Determine the state based on whether 'name' is empty or not
    state = tk.NORMAL if name.get() else tk.DISABLED
    
    # Loop through all child widgets of the frame
    for widget in lf.winfo_children():
        # Check if the widget type is one that supports the 'state' attribute
        if widget.winfo_class() in ('Entry', 'Text', 'Button', 'Checkbutton', 'Radiobutton', 'Listbox'):
            # Set the state of the widget
            widget.configure(state=state)

def date_group_cow(x, y,main=None):
    """Create a group of date entry widgets in a tkinter frame.

    Args:
        x (int): X-coordinate position for placing the frame.
        y (int): Y-coordinate position for placing the frame.

    Returns:
        None
    """
    global sday, smonth, syear, eday, emonth, eyear
    
    # Create a frame (date_cow) to contain the date entry elements
    date_cow = tk.Frame(main)
    date_cow.pack()

    # Labels and entry widgets for 'From' date
    label = tk.Label(date_cow, text="Du", font=("Helvetica", 14))
    label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
    sday = tk.Text(date_cow, height=1, width=2)
    sday.grid(row=0, column=1)
    sday.bind("<KeyRelease>", lambda event: limit_text_length(event, sday, 2))

    label = tk.Label(date_cow, text="/", font=("Helvetica", 14))
    label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
    smonth = tk.Text(date_cow, height=1, width=2)
    smonth.grid(row=0, column=3)
    smonth.bind("<KeyRelease>", lambda event: limit_text_length(event, smonth, 2))

    label = tk.Label(date_cow, text="/", font=("Helvetica", 14))
    label.grid(row=0, column=4, padx=5, pady=5, sticky=tk.E)
    syear = tk.Text(date_cow, height=1, width=4)
    syear.grid(row=0, column=5)
    syear.bind("<KeyRelease>", lambda event: limit_text_length(event, syear, 4))

    # Labels and entry widgets for 'To' date
    label = tk.Label(date_cow, text="au", font=("Helvetica", 14))
    label.grid(row=0, column=6, padx=5, pady=5, sticky=tk.E)
    eday = tk.Text(date_cow, height=1, width=2)
    eday.grid(row=0, column=7)
    eday.bind("<KeyRelease>", lambda event: limit_text_length(event, eday, 2))

    label = tk.Label(date_cow, text="/", font=("Helvetica", 14))
    label.grid(row=0, column=8, padx=5, pady=5, sticky=tk.E)
    emonth = tk.Text(date_cow, height=1, width=2)
    emonth.grid(row=0, column=9)
    emonth.bind("<KeyRelease>", lambda event: limit_text_length(event, emonth, 2))

    label = tk.Label(date_cow, text="/", font=("Helvetica", 14))
    label.grid(row=0, column=10, padx=5, pady=5, sticky=tk.E)
    eyear = tk.Text(date_cow, height=1, width=4)
    eyear.grid(row=0, column=11)
    eyear.bind("<KeyRelease>", lambda event: limit_text_length(event, eyear, 4))

    date_cow.place(x=x, y=y)

def browse_file(x, y, path,main=None):
    """Create a file browsing interface.

    Args:
        x (int): X-coordinate position for placing the file browsing interface.
        y (int): Y-coordinate position for placing the file browsing interface.
        path (str): Specifies whether to select a 'file' or a 'folder'.

    Returns:
        tk.Entry: Entry widget where the selected file or folder path is displayed.
    """
    browse = tk.Frame(main)
    browse.grid(row=1, column=3, columnspan=4, padx=0, sticky="nsw")  # Place the frame below checkbuttons
    
    entry_filename = tk.Entry(browse, width=40)
    entry_filename.pack(side=tk.LEFT, padx=10)
    
    browse_button = tk.Button(browse, text="Browse", command=lambda: browse_files(entry_filename, path))
    browse_button.pack(side=tk.LEFT)
    
    browse.place(x=x, y=y)
    return entry_filename

def text(x, y,color, text, font, info, parent=None):
    frame = Frame(parent or main)
    frame.place(x=x, y=y)

    title = Label(frame,bg=color, text=text, font=font)
    title.pack(side=tk.RIGHT)

    info_button = Button(
        frame,
        text="ℹ",
        fg="white",
        font=("Helvetica", 7),
        command=lambda: show_info(info,parent),
        width=1,
        height=1,
        bg="#007FFF",
        relief="flat",
        cursor="hand2"
    )
    info_button.pack(side=tk.LEFT)

def label_frame(x, y, width, height, color, text, info ,main=None):
    """Create a labeled frame with a checkbutton and an information button.

    Args:
        x (int): X-coordinate position for placing the labeled frame.
        y (int): Y-coordinate position for placing the labeled frame.
        width (int): Width of the labeled frame.
        height (int): Height of the labeled frame.
        color (str): Background color of the labeled frame.
        text (str): Text content of the label within the frame.
        info (str): Information to display when the info button is clicked.

    Returns:
        tuple: Tuple containing the created LabelFrame and IntVar for checkbutton state.
    """
    name = tk.IntVar()
    lf = tk.LabelFrame(main, text=text, bg=color)
    lf.place(x=x, y=y, width=width, height=height)

    sigpa_check = tk.Checkbutton(main, variable=name, command=lambda: desact_lf(name, lf))
    sigpa_check.place(x=x, y=y-22)

    # Create the info button
    info_button = tk.Button(
        text="ℹ",
        fg="white",
        font=("Helvetica", 7),
        command=lambda: show_info(info,lf),
        width=1,
        height=1,
        bg="#007FFF",
        relief="flat",
        cursor="hand2"
    )
    info_button.place(x=x + 22, y=y - 20)  # Adjust the coordinates as needed

    return lf, name

def easter_egg(main=None):
    """Display an easteregg message window.

    Returns:
        None
    """
    # Create an error window
    easter = Toplevel(main,bg="#F5DF4D")
    easter.title("Easter egg")
    easter.geometry("1000x600")
    easter.resizable(False, False)
    
    # Display the error message
    message = Message(easter,bg="#F5DF4D",font=("Helvetica", 70), text="You find me!!!​", width=700)
    message.pack(padx=10, pady=10)
    message1 = Message(easter,bg="#F5DF4D",font=("Helvetica", 100), text="😉😁​​", width=700)
    message1.pack(padx=2, pady=2)
    
    # Make the error window modal
    easter.grab_set()
    easter.transient(main)
    easter.wait_window(easter)

def tableau(x, y, parent, nb,main=None):
    """Create a scrollable table with labels and entry widgets.

    Args:
        x (int): X-coordinate position for placing the table.
        y (int): Y-coordinate position for placing the table.
        parent (tk.Tk): Parent widget to place the table.
        nb (int): Number of weeks to display in the table.

    Returns:
        None
    """
    global scrollable_frame  # Make sure scrollable_frame is accessible globally
    
    # Create a labeled frame for the table
    frame = tk.LabelFrame(parent, text="Weeks table", padx=3, pady=3)
    frame.pack(padx=10, pady=10, fill="both", expand="yes")
    frame.place(x=x, y=y, height=250)

    # Create a canvas widget for scrolling
    canvas = tk.Canvas(frame)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Configure the scrollable frame to update scroll region when resized
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    # Create a window within the canvas to hold the scrollable frame
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack canvas and scrollbar widgets
    canvas.pack(side="right", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Define columns for the table
    columns = ["Litre", "Passage"]

    # Create labels for columns
    for i, column in enumerate(columns):
        label = tk.Label(scrollable_frame, text=column, borderwidth=1, relief="solid", width=7)
        label.grid(row=0, column=i + 1, sticky="nsew")
    
    # Create labels for weeks
    for i in range(1, nb + 1):
        label = tk.Label(scrollable_frame, text=f"sem{i}", borderwidth=1, relief="solid", width=7)
        label.grid(row=i, column=0, sticky="nsew")
    
    # Create entry widgets for each cell in the table
    for i in range(1, nb + 1):
        for j in range(1, len(columns) + 1):
            entry = tk.Entry(scrollable_frame, width=7)
            entry.grid(row=i, column=j, sticky="nsew")
    
    # Configure grid columns and rows to expand with the window
    for i in range(1, len(columns) + 1):
        scrollable_frame.grid_columnconfigure(i, weight=1)
    for i in range(1, nb + 1):
        scrollable_frame.grid_rowconfigure(i, weight=1)

def confirm(start_date=None, end_date=None, extract_path=None, selected_columns=None, lactation=None, passage=None, clean=None,main=None):
    """Display a confirmation window with summary and buttons for user confirmation.

    Args:
        start_date (str): Start date information to display.
        end_date (str): End date information to display.
        extract_path (str): Extraction path information to display.
        selected_columns (list): List of selected columns to display.
        lactation (str): Lactation plan information to display.
        passage (str): Passage plan information to display.
        clean (bool): Clean incomplete weeks information to display.

    Returns:
        bool: True if user clicks 'Yes', False if 'No'.
    """
    # Use a mutable object to store the result
    result = [False]
    
    # Create a confirmation window
    confirm_window = Toplevel(main)
    confirm_window.title("Confirm Extraction")
    
    # Construct summary based on provided arguments
    summary = "You are trying to extract the data. There is a summary of your entry:\n(If all is ok click yes to finalize the extraction else click no)\n\n"
    if start_date:
        summary += f"Start Date: {start_date}\n"
    if end_date:
        summary += f"End Date: {end_date}\n"
    if extract_path:
        summary += f"Extraction Path: {extract_path}\n"
    if lactation:
        summary += f"Lactation plan: {lactation}\n"
    if passage:
        summary += f"passage plan: {passage}\n"
    if clean is not None:
        summary += f"Clean Incomplete Weeks: {'Yes' if clean else 'No'}\n"
    if selected_columns:
        summary += f"Selected Columns:\n{', '.join(selected_columns)}\n"
    
    # Create label to display summary
    summary_label = Label(confirm_window, text=summary, justify="left")
    summary_label.pack(padx=10, pady=10)

    # Function to set result to True and close window
    def on_yes():
        result[0] = True
        confirm_window.destroy()
    
    # Function to close window without setting result
    def on_no():
        confirm_window.destroy()
    
    # Create 'Yes' and 'No' buttons
    yes_button = Button(confirm_window, text="Yes", command=on_yes)
    yes_button.pack(side="right", padx=100, pady=5)
    
    no_button = Button(confirm_window, text="No", command=on_no)
    no_button.pack(side="left", padx=100, pady=5)
    
    # Make the confirmation window modal
    confirm_window.grab_set()
    confirm_window.transient(main)
    confirm_window.wait_window(confirm_window)
    
    return result[0]

def is_csv(file_path,main=None):
    """Check if a file is a CSV file.

    Args:
        file_path (str): Path to the file to check.

    Returns:
        bool: True if the file is not a CSV file, False if it is a CSV file.
    """
    try:
        with open(file_path, newline='') as csvfile:
            start = csvfile.read(1024)
            dialect = csv.Sniffer().sniff(start)
            csvfile.seek(0)
            reader = csv.reader(csvfile, dialect)
            for _ in reader:
                break
        return False
    except Exception:
        return True

def error(message,main=None):
    """Display an error message window.

    Args:
        message (str): Error message to display.

    Returns:
        None
    """
    # Create an error window
    error_window = Toplevel(main, bg="#F0604D")
    error_window.title("Error")
    error_window.resizable(False, False)
    
    # Display the error message
    message_label = Message(error_window,bg="#F0604D", text=message, width=300)
    message_label.pack(padx=10, pady=10)
    
    # Create a 'OK' button to close the error window
    close_button = Button(error_window,bg="#F0604D", text="OK", command=error_window.destroy)
    close_button.pack(pady=5)
    
    # Make the error window modal
    error_window.grab_set()
    error_window.transient(main)
    error_window.wait_window(error_window)

def header(main):
    # Header text describing the purpose of the program
    text(350, 20,"#ececec", "DAL's data modification", ("Helvetica", 20, "bold"),
        "   This program is designed to input raw data from the DAL, process it, "
        "and generate an Excel file for SIGPA in the correct format.\n\n"
        "   For the experimental phase, the program produces an initial file "
        "to enable human verification of the data for each cow's passage.\n"
        "   After this verification, the program processes the data in a day-by-day "
        "format to produce statistics (SAS).\n\n   The 'i' button next to each input "
        "field provides a description of the required information and the format in which "
        "it should be entered.",main)

    # Text and entry field for importing the ZIP file containing raw DAL data
    text(250, 60,"#ececec", "Zip file :", ("Helvetica", 16, "bold"),
        "   Import the file in .zip format containing the raw DAL data using the search button on the right",main)
    entry_zip = browse_file(470, 65, "file",main)  # Function to create file browse button

    # Text and entry field for entering the date range of the cow block
    text(250, 100,"#ececec", "Date of cow block :", ("Helvetica", 16, "bold"),
        "   Enter the birth date range of the block of cows studied in dd/mm/yyyy format",main)
    date_group_cow(470, 95,main)  # Function to create date entry fields
    # Function calls to set up 3 different parts of the GUI
    pass_by_pass(main)  # Sets up GUI for pass by pass data extraction
    experimentation(main)  # Sets up GUI for experimentation data extraction
    sigpa(main)  # Sets up GUI for SIGPA data extraction
    #Easter egg
    egg = Button(main,relief='flat',command=easter_egg)
    egg.place(x=10,y=10,width=40,height=40)
    return entry_zip

def sigpa(main):
    """
    Sets up a GUI for extracting CSV files for zootechnical data intended for SIGPA.
    Users specify a ZIP file containing raw data, date ranges, an aliment number,
    select an extraction path, and trigger the extraction process.
    """
    global aliment  # Global variable for aliment number

    # Create a labeled frame for the GUI
    lf, name = label_frame(10, 390, 490, 200, "#B4BAFF", "SIGPA",
                           "By checking this button, you activate the part to extract the csv file "
                           "for the zootechnical data which will go into SIGPA.",main)

    # Function to handle data extraction
    def extract():
        """
        Function triggered when 'Extract' button is clicked.
        Processes user inputs, validates them, extracts data, and saves as CSV.
        """
        # Validate path for the ZIP file with raw data
        zip_path = entry_zip.get()
        if not(os.path.isfile(zip_path)):
            error("You have to put the path for a zip file")
            return
        
        # Validate start date of the cow block
        start_date = f"{syear.get('1.0', 'end-1c')}-{smonth.get('1.0', 'end-1c')}-{sday.get('1.0', 'end-1c')}"
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            error("You have to write date to dd/mm/yyyy format")
            return
        
        # Validate end date of the cow block
        end_date = f"{eyear.get('1.0', 'end-1c')}-{emonth.get('1.0', 'end-1c')}-{eday.get('1.0', 'end-1c')}"
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            error("You have to write date to dd/mm/yyyy format")
            return
        
        # get aliment number
        Aliment = aliment.get("1.0", "end-1c").strip()
        
        # get aliment number
        Farming = farming.get("1.0", "end-1c").strip()
        
        # Validate path for extraction
        extract_path = entry_sigpa_extract.get()
        if not(os.path.isdir(extract_path)):
            error("You have to put the path for a directory")
            return
        
        # Confirm extraction with user
        confirmation = confirm(start_date=start_date, end_date=end_date, extract_path=extract_path)
        if confirmation:
            # Call function to create the extract file for SIGPA
            data = data_for_sigpa(zip_path, start_date, end_date, Aliment,Farming)
            save_dataframe(data, extract_path + "\sigpa_data.csv")

    # GUI elements inside the labeled frame

    # Text entry for aliment number
    text(10, 0,"#B4BAFF", "Aliment :", ("Helvetica", 12),
         "You need to put the number for the aliment use in the experimentation.\n"
         "By default it's 1. And this is the list:\n-1 = ... -2 = ...\n-3 = ... -4 = ...",
         parent=lf)
    aliment = tk.Text(lf, height=1, width=20)
    aliment.bind("<KeyRelease>", lambda event: limit_text_length(event, aliment, 4))
    aliment.pack()
    aliment.place(x=100, y=3)
    
    # Text entry for farming number
    text(10, 30,"#B4BAFF", "farming number :", ("Helvetica", 12),
         "You need to put the farmig number to put it before animals number.\n"
         "Ex:FR371783,...",
         parent=lf)
    farming = tk.Text(lf, height=1, width=20)
    farming.bind("<KeyRelease>", lambda event: limit_text_length(event, aliment, 4))
    farming.pack()
    farming.place(x=150, y=33)


    # Entry field for extraction path
    text(10, 150,"#B4BAFF", "Extract path :", ("Helvetica", 10),
         "You have to put the path where you want to put the extract file.",
         parent=lf)
    entry_sigpa_extract = tk.Entry(lf, width=30)
    entry_sigpa_extract.pack()
    entry_sigpa_extract.place(x=110, y=153)
    browse_sigpa_extract = Button(lf,bg="#B4BAFF",activebackground="#81657C", text="Browse", command=lambda: browse_files(entry_sigpa_extract, "directory"))
    browse_sigpa_extract.pack()
    browse_sigpa_extract.place(x=300, y=150)

    # Button to trigger data extraction process
    Extract = Button(lf, text="Extract",activebackground="#81657C", font=("Helvetica", 16, "bold"), command=extract)
    Extract.pack(pady=5)
    Extract.place(x=390, y=135)

    # Disable the label frame after setup
    desact_lf(name, lf)

def pass_by_pass(main):
    """
    Sets up a GUI for managing pass-by-pass data extraction.
    Users can specify a ZIP file containing raw data, date ranges,
    select columns for extraction, choose an extraction path, and opt to clean incomplete weeks.
    """

    # Create a labeled frame for the GUI
    lf, name = label_frame(10, 150, 490, 210, "#FFEFA7", "Pass by pass",
                           "This part extract data pass by pass of each cow with right.\n"
                           "Then you can extract the data in a .csv file to correct them and then "
                           "you put the file in experimentation part to get a .csv file for SAS",main)

    # List of column names
    columns = ["URBAN_ID", "NUM", "Bande", "Date_Naiss", "Age", "Semaine", "Sem",
               "Prog_lait", "Conso_lait", "Conso_mat1", "Conso_mat2", "Conso_eau",
               "Date_debut", "Heure_debut", "Date_fin", "Heure_fin", "Temps_buvee"]

    # List to store BooleanVar variables for checkboxes
    checkbox_vars = []

    # Function to extract data based on user inputs
    def extract():
        """
        Function triggered when 'Extract' button is clicked.
        Processes user inputs, validates them, extracts data, and saves as CSV.
        """
        # Validate path for the ZIP file with raw data
        zip_path = entry_zip.get()
        if not(os.path.isfile(zip_path)):
            error("You have to put the path for a zip file")
            return
        if not zipfile.is_zipfile(zip_path):
            error("The file is not a valid zip file")
            return

        # Validate start date of the cow block
        start_date = f"{syear.get('1.0', 'end-1c')}-{smonth.get('1.0', 'end-1c')}-{sday.get('1.0', 'end-1c')}"
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            error("You have to write date to dd/mm/yyyy format")
            return

        # Validate end date of the cow block
        end_date = f"{eyear.get('1.0', 'end-1c')}-{emonth.get('1.0', 'end-1c')}-{eday.get('1.0', 'end-1c')}"
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            error("You have to write date to dd/mm/yyyy format")
            return

        # Check if start date is before end date
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            error("You have to put a starting date and then a final date. You put prior date after the first date.")
            return

        # Validate extraction path
        extract_path = entry_pass_extract.get()
        if not(os.path.isdir(extract_path)):
            error("You have to put the path for a directory")
            return

        # Check if the user wants to clean incomplete weeks
        clean = clear_incomplete_weeks.get()

        selected_columns = []

        # Collect selected columns based on checkboxes
        for index, var in enumerate(checkbox_vars):
            if var.get():  # Check if the checkbox is selected
                selected_columns.append(columns[index])  # Add the column name to the list

        # Confirm extraction with user and proceed if confirmed
        confirmation = confirm(start_date=start_date, end_date=end_date, extract_path=extract_path,
                               selected_columns=selected_columns, clean=clean)
        if confirmation:
            # Extract and process data based on user inputs
            data = pbp_data(zip_path, start_date, end_date)
            if clean:
                data = data_cleaned_without_week(data, selected_columns)
                save_dataframe(data, extract_path + "\pass_by_pass_without_week.csv")
            else:
                data = data_cleaned_with_week(data, selected_columns)
                save_dataframe(data, extract_path + "\pass_by_pass_with_week.csv")

    # GUI elements inside the label frame

    # Checkbox to select if incomplete weeks should be cleaned
    text(10, 0,"#FFEFA7", "Clear incomplete weeks :", ("Helvetica", 10,),
         "By checking the following button you delete all the week in the data that are not composed by "
         "7 following days except for the first one that starts at day three.", parent=lf)
    clear_incomplete_weeks = tk.BooleanVar()
    check_week = tk.Checkbutton(lf, text="Without weeks",bg="#FFEFA7",activebackground="#FFA29A", variable=clear_incomplete_weeks)
    check_week.pack()
    check_week.place(x=200, y=0)

    # Checkboxes for selecting columns to include in extraction
    text(10, 25,"#FFEFA7" ,"Selected columns :", ("Helvetica", 10),
         "You have to check which columns you want in the extract data.", parent=lf)
    for index, col in enumerate(columns):
        var = tk.BooleanVar(value=True)  # Initialize BooleanVar for each column
        checkbox_vars.append(var)  # Add BooleanVar to the list
        checkbutton = tk.Checkbutton(lf, text=col,bg="#FFEFA7",activebackground="#FFA29A", variable=var)

        # Position checkboxes based on index
        if index < 5:
            checkbutton.place(x=20 + 90 * index, y=49)
        elif index >= 5 and index < 10:
            checkbutton.place(x=20 + 90 * (index - 5), y=76)
        elif index >= 10 and index < 15:
            checkbutton.place(x=20 + 90 * (index - 10), y=103)
        else:
            checkbutton.place(x=20 + 90 * (index - 15), y=130)

    # Entry field for extraction path
    text(10, 165,"#FFEFA7", "Extract path :", ("Helvetica", 10),
         "You have to put the path where you want to put the extract file.", parent=lf)
    entry_pass_extract = tk.Entry(lf, width=30)
    entry_pass_extract.pack()
    entry_pass_extract.place(x=110, y=167)
    browse_pass_extract = Button(lf, text="Browse",bg="#FFEFA7",activebackground="#FFA29A", command=lambda: browse_files(entry_pass_extract, "directory"))
    browse_pass_extract.pack()
    browse_pass_extract.place(x=300, y=162)

    # Button to trigger data extraction process
    Extract = Button(lf, text="Extract",activebackground="#81657C", font=("Helvetica", 16, "bold"), command=extract)
    Extract.pack(pady=5)
    Extract.place(x=390, y=145)

    # Disable the label frame after setup
    desact_lf(name, lf)

def experimentation(main):
    """
    This function sets up a GUI for managing experimentation data.
    It includes options for selecting CSV files, specifying weeks of experimentation,
    filling a data table, selecting columns for extraction, and choosing an extraction path.
    """

    # Create a labeled frame for the GUI
    lf, name = label_frame(510, 150, 480, 440, "#9FCDA8", "Experimentation",
                           "This part is used to create the files with data day by day to use it in SAS.\n"
                           "You will have by checking this button to choose the columns you want in the final .csv "
                           "file before exporting the file to the path you want.",main)
    
    checkbox_vars = []
    columns = ["URBAN_ID","NUM", "Bande","DATE", "JOUR", "Sem", "Conso_lait", "Conso_lait_theorique",
               "Ecart_conso_lait", "Temps_buvee_total", "Nombre_de_visites",
               "Visites_theoriques", "Ecart_visites","Nb_Reffus"]

    def extract():
        """
        Function triggered when 'Extract' button is clicked.
        Processes user inputs, validates them, extracts data, and saves as CSV.
        """
        entry_path = entry_pass.get()

        # Validate file path
        if not(os.path.isfile(entry_path)):
            error("You have to put the path for a file")
            return

        # Validate if the file is a CSV
        if not(is_csv(entry_path)):
            error("The file is not a valid CSV file")
            return

        # Validate the number of weeks input
        week = week_number.get("1.0", "end-1c").strip()
        try:
            int(week)
        except ValueError:
            error("You have to write an integer for the number of week")
            return

        # Initialize lists for selected data
        selected_columns = []
        litre_data = []
        passage_data = []

        # Collect selected columns based on checkboxes
        for index, var in enumerate(checkbox_vars):
            if var.get():  # Check if the checkbox is selected
                selected_columns.append(columns[index])

        # Collect data from the dynamically created table
        for i in range(1, nb + 1):
            litre_entry = scrollable_frame.grid_slaves(row=i, column=1)[0]
            passage_entry = scrollable_frame.grid_slaves(row=i, column=2)[0]

            # Retrieve and validate data from entry widgets
            try:
                litre_value = float(litre_entry.get())
                passage_value = float(passage_entry.get())
            except ValueError:
                error("You have to fill all the case of the table with float value")
                return

            # Append validated data to respective lists
            litre_data.append(litre_value)
            passage_data.append(passage_value)

        # Validate extraction path
        extract_path = entry_sigpa_extract.get()
        if not(os.path.isdir(extract_path)):
            error("You have to put the path for a directory")
            return

        # Confirm extraction with user and proceed if confirmed
        confirmation = confirm(extract_path=extract_path, selected_columns=selected_columns,
                               lactation=litre_data, passage=passage_data)
        if confirmation:
            # Read CSV file and process data
            df = pd.read_csv(entry_path, delimiter=';')
            data = data_dbd(df, litre_data, passage_data, selected_columns)
            save_dataframe(data, extract_path + "\day_by_day.csv")

    # GUI elements inside the label frame

    # Entry field for CSV file path
    text(10, 15,"#9FCDA8", "Select a .csv file:", ("Helvetica", 10),
         "You have to put the path of the corrected file of pass by pass part.", parent=lf)
    entry_pass = tk.Entry(lf, width=30)
    entry_pass.pack()
    entry_pass.place(x=140, y=17)
    browse_pass = Button(lf, text="Browse",bg="#9FCDA8",activebackground="#FFA29A", command=lambda: browse_files(entry_pass, "file"))
    browse_pass.pack()
    browse_pass.place(x=330, y=15)

    # Entry for number of weeks of experimentation
    text(10, 50,"#9FCDA8", "Number of week :", ("Helvetica", 10),
         "Number of week has lasted the experimentation. This data is used to create the table below "
         "to know the lactation or passage plan for the experimentation", parent=lf)
    week_number = tk.Text(lf, height=1, width=4)
    week_number.bind("<KeyRelease>", lambda event: limit_text_length(event, week_number, 4))
    week_number.pack()
    week_number.place(x=140, y=50)

    # Frame for displaying and updating the data table
    text(10, 90,"#9FCDA8", "curve of feeding and passage:", ("Helvetica", 10),
         "Fill the table below with the data of drinking and the number of time cows can come to drink week by week",
         parent=lf)
    table_frame = tk.Frame(lf)
    table_frame.place(x=10, y=120, width=188, height=250)

    def update_table():
        """
        Update the table frame based on the number of weeks input.
        """
        for widget in table_frame.winfo_children():
            widget.destroy()
        try:
            global nb  # Access the global nb variable
            nb = int(week_number.get("1.0", "end-1c").strip())
            tableau(0, 0, table_frame, nb)
        except ValueError:
            pass

    week_number.bind("<KeyRelease>", lambda event: update_table())

    # Checkbox options for selecting columns
    text(270, 40,"#9FCDA8", "Selected columns :", ("Helvetica", 10),
         "You have to check which columns you want in the extract data.", parent=lf)
    for index, col in enumerate(columns):
        var = tk.BooleanVar(value=True)  # Initialize BooleanVar for each column
        checkbox_vars.append(var)  # Append BooleanVar to the list
        checkbutton = tk.Checkbutton(lf, text=col,bg="#9FCDA8",activebackground="#FFA29A", variable=var)
        checkbutton.place(x=285, y=60 + 22 * index)

    # Entry field for extraction path
    text(10, 390,"#9FCDA8", "Extract path :", ("Helvetica", 10),
         "You have to put the path where you want to put the extract file.", parent=lf)
    entry_sigpa_extract = tk.Entry(lf, width=30)
    entry_sigpa_extract.pack()
    entry_sigpa_extract.place(x=110, y=392)
    browse_sigpa_extract = Button(lf, text="Browse",bg="#9FCDA8",activebackground="#FFA29A", command=lambda: browse_files(entry_sigpa_extract, "directory"))
    browse_sigpa_extract.pack()
    browse_sigpa_extract.place(x=300, y=387)

    # Button to trigger the extraction process
    Extract = Button(lf, text="Extract",activebackground="#81657C", font=("Helvetica", 16, "bold"), command=extract)
    Extract.pack(pady=5)
    Extract.place(x=380, y=375)

    # Disable the label frame after setup
    desact_lf(name, lf)


if __name__=="__main__":
    # Create the main window
    main = tk.Tk()
    main.title("DAL")
    main.geometry("1000x600")
    # display the head of the GUI
    entry_zip = header(main)
    # Start the GUI event loop
    main.mainloop()

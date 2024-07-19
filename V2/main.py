import tkinter as tk
from tkinter import ttk, filedialog, Label, Button, Toplevel, Message, Frame, StringVar, OptionMenu, Entry, Text
import json
import os
import sys
import zipfile
from datetime import datetime 
from utils import curve,save_dataframe
from Data import par_jour,par_passage
from Output import sicpa,sem_comp_jour

class InfoWindow:
    """Class to manage information windows."""
    def __init__(self, main=None):
        self.info_window = None
        self.main = main

    def show_info(self, info):
        """Display information in a pop-up window."""
        if self.info_window is None or not self.info_window.winfo_exists():
            self.info_window = Toplevel(self.main)
            self.info_window.title("Information")
            self.info_window.resizable(False, False)

            message = Message(self.info_window, text=info, width=200)
            message.pack(padx=10, pady=10)

            button = Button(self.info_window, text="OK", command=self.close_info)
            button.pack(pady=5)

    def close_info(self):
        """Close the information window."""
        if self.info_window is not None:
            self.info_window.destroy()
            self.info_window = None

class MainApp:
    """Class to manage the main application."""
    def __init__(self, root, texts):
        # Initialize the main window settings
        self.root = root
        self.root.title("DAL")
        self.root.geometry("1000x600")
        self.root.configure(bg="#9FCDA8")
        self.texts = texts

        # Create an instance of InfoWindow
        self.info_window = InfoWindow(self.root)
        
        # Initialize variables for language selection and input fields
        self.language_var = StringVar(value="en")
        self.entries = {}
        self.table_entries = {}
        self.aliment_entries = {}
        
        # Create language selector
        self.create_language_selector()
        
        # Initialize other attributes
        self.courbe = []
        self.tabs = []
        self.weeks_var = StringVar(value="0")

        # Update tables when weeks_var changes, if courbe is set
        self.weeks_var.trace_add("write", lambda *args: self.update_tables() if self.courbe else None)
        
        # Set up header
        self.header()
            
    def create_language_selector(self):
        # Create a frame for the language selector
        languages = ["en", "fr"]
        selector_frame = Frame(self.root, bg="#9FCDA8")
        selector_frame.place(x=900, y=10)
        
        # Add a label and option menu for language selection
        language_label = Label(selector_frame, bg="#9FCDA8")
        language_label.pack(side=tk.LEFT)
        
        language_menu = OptionMenu(selector_frame, self.language_var, *languages, command=self.change_language)
        language_menu.pack(side=tk.LEFT)

    def change_language(self, lang):
        # Save current entries before changing language
        self.save_entries()
        
        # Load text for the selected language
        self.texts = load_texts(lang)
        
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Recreate the UI with the new language settings
        self.create_language_selector()
        self.header()
        
        # Restore previously saved entries
        self.restore_entries()

    def save_entries(self):
        """Save the current values of entry fields."""
        # Save the values of various entry fields to the self.entries dictionary
        self.entries['zip'] = self.entry_zip.get()
        self.entries['sday'] = self.sday.get("1.0", "end-1c")
        self.entries['smonth'] = self.smonth.get("1.0", "end-1c")
        self.entries['syear'] = self.syear.get("1.0", "end-1c")
        self.entries['eday'] = self.eday.get("1.0", "end-1c")
        self.entries['emonth'] = self.emonth.get("1.0", "end-1c")
        self.entries['eyear'] = self.eyear.get("1.0", "end-1c")
        self.entries['IPG'] = self.entry_IPG.get("1.0", "end-1c")
        self.entries['pao'] = self.entry_pao.get()
        self.entries['sicpa'] = self.entry_sicpa.get()
        self.entries['week'] = self.entry_week.get()
        self.entries['comp'] = self.entry_comp.get()

        # Save table entries
        for tab_index, tab in enumerate(self.tabs):
            aliment_entry = tab.grid_slaves(row=0, column=0)
            if aliment_entry:
                self.aliment_entries[f'tab_{tab_index}'] = aliment_entry[0].get()

            tab_entries = []
            for row in range(2, int(self.weeks) + 2):
                row_entries = []
                for col in range(1, len(self.colonnes)):
                    entry = tab.grid_slaves(row=row, column=col)
                    if entry:
                        row_entries.append(entry[0].get())
                tab_entries.append(row_entries)
            self.table_entries[f'tab_{tab_index}'] = tab_entries

    def restore_entries(self):
        """Restore the saved values of entry fields."""
        # Restore values in entry fields
        self.entry_zip.insert(0, self.entries.get('zip', ''))
        self.sday.insert("1.0", self.entries.get('sday', ''))
        self.smonth.insert("1.0", self.entries.get('smonth', ''))
        self.syear.insert("1.0", self.entries.get('syear', ''))
        self.eday.insert("1.0", self.entries.get('eday', ''))
        self.emonth.insert("1.0", self.entries.get('emonth', ''))
        self.eyear.insert("1.0", self.entries.get('eyear', ''))
        self.entry_IPG.insert("1.0", self.entries.get('IPG', ''))
        self.entry_pao.insert(0, self.entries.get('pao', ''))
        self.entry_sicpa.insert(0, self.entries.get('sicpa', ''))
        self.entry_week.insert(0, self.entries.get('week', ''))
        self.entry_comp.insert(0, self.entries.get('comp', ''))

        # Restore table entries
        for tab_index, tab in enumerate(self.tabs):
            if f'tab_{tab_index}' in self.aliment_entries:
                aliment_entry = tab.grid_slaves(row=0, column=0)
                if aliment_entry:
                    aliment_entry[0].delete(0, tk.END)
                    aliment_entry[0].insert(0, self.aliment_entries[f'tab_{tab_index}'])

            if f'tab_{tab_index}' in self.table_entries:
                for row_index, row_values in enumerate(self.table_entries[f'tab_{tab_index}']):
                    for col_index, value in enumerate(row_values):
                        entry = tab.grid_slaves(row=row_index + 2, column=col_index + 1)
                        if entry:
                            entry[0].delete(0, tk.END)
                            entry[0].insert(0, value)
                            # Set text color to black if restored value is not zero
                            if value != '0':
                                entry[0].config(fg='black')

    def text(self, x, y, color, text, font, info):
        # Create a frame with a background color and position it at (x, y)
        frame = Frame(self.root, bg=color)
        frame.place(x=x, y=y)

        # Create a label with specified text and font, and add it to the frame
        title = Label(frame, bg=color, text=text, font=font)
        title.pack(side=tk.RIGHT)

        # Create an info button with a tooltip
        info_button = Button(
            frame,
            text="ℹ",  # Info symbol
            fg="white",
            font=("Helvetica", 7),
            command=lambda: self.info_window.show_info(info),  # Display info when clicked
            width=1,
            height=1,
            bg="#007FFF",  # Button background color
            relief="flat",  # Flat button style
            cursor="hand2"  # Hand cursor on hover
        )
        info_button.pack(side=tk.LEFT)

    def browse_file(self, x, y, path, width=40):
        # Create a frame for file browsing components
        browse = Frame(self.root)
        browse.grid(row=1, column=3, columnspan=4, padx=0, sticky="nsw")

        # Create an entry widget for displaying the file or folder path
        entry_filename = Entry(browse, width=width)
        entry_filename.pack(side=tk.LEFT)

        # Create a button to open file or folder dialog
        browse_button = Button(browse, text=self.texts['browse'], bg="#9FCDA8", activebackground="#FFA29A",
                            command=lambda: self.browse_files(entry_filename, path))
        browse_button.pack(side=tk.LEFT)

        # Position the browse frame at (x, y)
        browse.place(x=x, y=y)
        return entry_filename

    def browse_files(self, entry_filename, path):
        # Create a hidden top-level window for file or folder dialog
        selection_window = tk.Tk()
        selection_window.withdraw()

        # Open file dialog if path is 'file', else open folder dialog
        if path == 'file':
            filename = filedialog.askopenfilename(initialdir="/", title="Select a File",
                                                filetypes=(("All files", "*.*"), ("ZIP files", "*.zip*"), ("CSV files", "*.csv*")))
        else:
            filename = filedialog.askdirectory(initialdir="/", title="Select a Folder")

        # Update the entry widget with the selected file or folder path
        entry_filename.delete(0, tk.END)
        entry_filename.insert(tk.END, filename)
        selection_window.destroy()

    def date_group_cow(self, x, y):
        # Create a frame for date entry fields
        date_cow = Frame(self.root, bg="#9FCDA8")
        date_cow.pack()

        # Helper function to create labels and text widgets for date entry
        def create_label_and_text(row, column, label_text, text_width):
            label = Label(date_cow, bg="#9FCDA8", text=label_text, font=("Helvetica", 14))
            label.grid(row=0, column=column, padx=5, pady=5, sticky=tk.E)
            text_widget = Text(date_cow, height=1, width=text_width)
            text_widget.grid(row=0, column=column + 1)
            text_widget.bind("<KeyRelease>", lambda event: self.limit_text_length(event, text_widget, text_width))
            return text_widget

        # Create date entry fields for start and end dates
        self.sday = create_label_and_text(0, 0, self.texts["from"], 2)
        self.smonth = create_label_and_text(0, 2, "/", 2)
        self.syear = create_label_and_text(0, 4, "/", 4)
        self.eday = create_label_and_text(0, 6, self.texts["to"], 2)
        self.emonth = create_label_and_text(0, 8, "/", 2)
        self.eyear = create_label_and_text(0, 10, "/", 4)

        # Position the date frame at (x, y)
        date_cow.place(x=x, y=y)

    def limit_text_length(self, event, text_widget, max_length):
        # Limit the length of text input in a text widget
        content = text_widget.get("1.0", "end-1c")
        if len(content) > max_length:
            text_widget.delete("1.0", "end")
            text_widget.insert("1.0", content[:max_length])
            return "break"

    def easter_egg(self):

        # Create a top-level window for the easter egg message
        easter = Toplevel(self.root, bg="#F5DF4D")
        easter.title(self.texts["easter_egg_title"])
        easter.geometry("1000x600")
        easter.resizable(False, False)

        # Display messages in the easter egg window
        message = Message(easter, bg="#F5DF4D", font=("Helvetica", 70), text=self.texts["easter_egg_message"], width=700)
        message.pack(padx=10, pady=10)
        message1 = Message(easter, bg="#F5DF4D", font=("Helvetica", 100), text=self.texts["easter_egg_emoji"], width=700)
        message1.pack(padx=2, pady=2)

        # Make the easter egg window modal
        easter.grab_set()
        easter.transient(self.root)
        easter.wait_window(easter)

    def update_tables(self):
        try:
            self.weeks = int(self.weeks_var.get())
            for tab in self.tabs:
                if tab.winfo_exists():
                    for widget in tab.winfo_children():
                        widget.destroy()
            for tab in self.tabs:
                tab.destroy()
            
            self.tabs.clear()

            for cour in self.courbe:
                tab = Frame(self.notebook)
                self.notebook.add(tab, text=cour)
                self.tabs.append(tab)

                self.text(180, 225, "white", self.texts["aliment_label"], ("Helvetica", 13, "bold"), self.texts["aliment_info"])
                aliment_entry = Entry(tab)
                aliment_entry.grid(row=0, column=0, columnspan=len(self.colonnes), pady=5)

                for col in range(len(self.colonnes)):
                    label = Label(tab, text=self.colonnes[col], borderwidth=1, relief='solid', bg='lightgrey')
                    label.grid(row=1, column=col, sticky='nsew')

                for row in range(2, self.weeks + 2):
                    for col in range(len(self.colonnes)):
                        entry = Entry(tab, borderwidth=1, relief='solid', justify='center')
                        entry.grid(row=row, column=col, sticky='nsew')

                        if col == 0:
                            entry.insert(0, f'{self.texts["sem"]} {row-1}')
                            entry.config(fg='black', state='readonly')
                        else:
                            entry.insert(0, '0')
                            entry.config(fg='grey')

                        entry.bind("<FocusIn>", self.on_entry_click)
                        entry.bind("<FocusOut>", self.on_focus_out)

                for col in range(len(self.colonnes)):
                    tab.columnconfigure(col, weight=1)

        except ValueError:
            pass

    def on_entry_click(self, event):
        """Clear the text when the entry is clicked."""
        entry = event.widget
        if entry.get() == '0':
            entry.delete(0, tk.END)
            entry.config(fg='black')

    def on_focus_out(self, event):
        """Reset the text to '0' if the entry field is empty when it loses focus."""
        entry = event.widget
        if entry.get() == '':
            entry.insert(0, '0')
            entry.config(fg='grey')  # Change text color to grey

    def refresh_curves(self):
        """Refresh the list of curves and update the tabs in the notebook.
        """

        zip_path = self.entry_zip.get()

        # Validate the ZIP file path
        if not zipfile.is_zipfile(zip_path):
            self.error(self.texts['zip_path_error'])
            return
        if not zip_path.lower().endswith('.zip'):
            self.error(self.texts['zip_error'])
            return

        # Retrieve and validate date range inputs
        sday = self.sday.get("1.0", "end-1c").strip()
        smonth = self.smonth.get("1.0", "end-1c").strip()
        syear = self.syear.get("1.0", "end-1c").strip()
        eday = self.eday.get("1.0", "end-1c").strip()
        emonth = self.emonth.get("1.0", "end-1c").strip()
        eyear = self.eyear.get("1.0", "end-1c").strip()
        start_date = f"{syear}-{smonth}-{sday}"
        end_date = f"{eyear}-{emonth}-{eday}"

        # Check if the start and end dates are valid
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            self.error(self.texts['date'])
            return
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            self.error(self.texts['date'])
            return
        
        # Ensure the start date is before or equal to the end date
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            self.error(self.texts['date_order'])
            return

        # Initialize curves with the provided ZIP file and date range
        self.courbe = curve(zip_path, start_date, end_date)

        # Clear existing tabs
        for tab in self.tabs:
            tab.destroy()
        self.tabs.clear()

        # Create new tabs for each curve
        for cour in self.courbe:
            tab = Frame(self.notebook, bg='lightyellow')
            self.notebook.add(tab, text=cour)
            self.tabs.append(tab)

        # Update tables and enable extract button
        self.update_tables()
        self.Extract.config(state=tk.NORMAL)

    def error(self, message):
        """Display an error message in a pop-up window.

        Args:
            message (str): The error message to display.
        """
        # Create an error pop-up window
        error_window = Toplevel(bg="#F0604D")
        error_window.title("Error")
        error_window.resizable(False, False)

        # Show the error message
        message_label = Message(error_window, bg="#F0604D", text=message, width=300)
        message_label.pack(padx=10, pady=10)

        # Add an 'OK' button to close the error window
        close_button = Button(error_window, bg="#F0604D", text="OK", command=error_window.destroy)
        close_button.pack(pady=5)

        # Make the error window modal
        error_window.grab_set()
        error_window.transient(self.root)
        error_window.wait_window(error_window)

    def extract(self):
        """Extract data based on user input and save to specified directories."""

        # Get states of checkbuttons for selecting output files
        checkbutton_states = [
            self.pao_var.get(),
            self.sicpa_var.get(),
            self.week_var.get(),
            self.comp_var.get()
        ]

        zip_path = self.entry_zip.get()

        # Validate the ZIP file path
        if not zipfile.is_zipfile(zip_path):
            self.error(self.texts['zip_path_error'])
            return
        if not zip_path.lower().endswith('.zip'):
            self.error(self.texts['zip_error'])
            return

        # Retrieve and validate date range inputs
        sday = self.sday.get("1.0", "end-1c").strip()
        smonth = self.smonth.get("1.0", "end-1c").strip()
        syear = self.syear.get("1.0", "end-1c").strip()
        eday = self.eday.get("1.0", "end-1c").strip()
        emonth = self.emonth.get("1.0", "end-1c").strip()
        eyear = self.eyear.get("1.0", "end-1c").strip()
        start_date = f"{syear}-{smonth}-{sday}"
        end_date = f"{eyear}-{emonth}-{eday}"

        # Validate start and end dates
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            self.error(self.texts['date'])
            return
        try:
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            self.error(self.texts['date'])
            return
        
        # Check if start date is before or equal to end date
        if datetime.strptime(start_date, "%Y-%m-%d") > datetime.strptime(end_date, "%Y-%m-%d"):
            self.error(self.texts['date_order'])
            return

        # Retrieve IPG number
        ipg_number = self.entry_IPG.get("1.0", "end-1c").strip()
        Courbe = self.courbe

        # Validate number of weeks
        num_weeks = self.weeks_var.get()
        try:
            int(num_weeks)
        except ValueError:
            self.error(self.texts['num_week'])
            return
        if int(num_weeks) < 1:
            self.error(self.texts['week'])
            return

        visites = []
        conso_lait = []
        aliment_data = []

        # Process each tab to extract data
        for tab_index, tab in enumerate(self.tabs):
            aliment_entry = tab.grid_slaves(row=0, column=0)
            aliment_name = aliment_entry[0].get() if aliment_entry else ""

            liter_column = []
            passage_column = []

            for row in range(2, int(num_weeks) + 2):
                liter_entry = tab.grid_slaves(row=row, column=1)
                passage_entry = tab.grid_slaves(row=row, column=2)

                liter_value = liter_entry[0].get() if liter_entry else 0
                passage_value = passage_entry[0].get() if passage_entry else 0
                try:
                    liter_value = float(liter_value)
                    passage_value = float(passage_value)
                except ValueError:
                    self.error(self.texts['table_fill'])
                    return

                liter_column.append(liter_value)
                passage_column.append(passage_value)
            
            aliment_data.append(aliment_name)
            conso_lait.append(liter_column)
            visites.append(passage_column)

        # Paths for saving output files
        pao_path = self.entry_pao.get()
        sicpa_path = self.entry_sicpa.get()
        week_path = self.entry_week.get()
        comp_path = self.entry_comp.get()

        # Parse and save data for PAO
        data_pao, all_data = par_passage(zip_path, Courbe, aliment_data, start_date, end_date)
        if checkbutton_states[0]:
            if not os.path.isdir(pao_path):
                self.error(self.texts['directory'])
                return
            save_dataframe(data_pao, os.path.join(pao_path, "DB_PAO.csv"))
        
        # Parse and save weekly data
        data_week = par_jour(data_pao, all_data, Courbe, conso_lait, visites)
        if checkbutton_states[2]:
            if not os.path.isdir(pao_path):
                self.error(self.texts['directory'])
                return
            save_dataframe(data_week, os.path.join(week_path, "Statistiques.csv"))
        
        # Parse and save SICPA data
        data_sicpa = sicpa(data_pao, ipg_number)
        if checkbutton_states[1]:
            if not os.path.isdir(sicpa_path):
                self.error(self.texts['directory'])
                return
            save_dataframe(data_sicpa, os.path.join(sicpa_path, "SICPA.csv"))
        
        # Parse and save complete weeks data
        data_comp = sem_comp_jour(data_week, num_weeks)
        if checkbutton_states[3]:
            if not os.path.isdir(comp_path):
                self.error(self.texts['directory'])
                return
            save_dataframe(data_comp, os.path.join(comp_path, "Semaines_completes.csv"))

    def header(self):
        """Set up the main interface header and controls."""

        # Set column headers for tables
        self.colonnes = [self.texts["weeks"], self.texts["liter"], self.texts["passsage"]]

        # Create header text elements
        self.text(350, 10, "#9FCDA8", self.texts["title"], ("Helvetica", 20, "bold"), self.texts["info_description"])
        self.text(880, 13, "#9FCDA8", "", ("Helvetica", 16, "bold"), self.texts["language_info"])
        self.text(120, 60, "#9FCDA8", self.texts["zip_file_label"], ("Helvetica", 16, "bold"), self.texts["zip_file_info"])
        
        # Add entry for ZIP file path
        self.entry_zip = self.browse_file(250, 65, "file")
        
        # Add date range input fields
        self.text(230, 100, "#9FCDA8", self.texts["cow_block_label"], ("Helvetica", 16, "bold"), self.texts["cow_block_info"])
        self.date_group_cow(490, 95)
        
        # Add IPG entry field
        self.text(600, 60, "#9FCDA8", self.texts["IPG_label"], ("Helvetica", 16, "bold"), self.texts["IPG_info"])
        self.entry_IPG = Text(self.root, height=1, width=20)
        self.entry_IPG.place(x=760, y=65)

        # Add Easter egg button
        egg_button = Button(self.root, bg="#9FCDA8", relief='flat', command=self.easter_egg)
        egg_button.place(x=10, y=10, width=40, height=40)
        
        # Add weeks entry field
        self.text(420, 140, "#9FCDA8", self.texts["nb_sem"], ("Helvetica", 16, "bold"), self.texts["nb_sem_info"])
        weeks_frame = Frame(self.root)
        weeks_frame.place(x=675, y=145)
        self.weeks_entry = Entry(weeks_frame, textvariable=self.weeks_var)
        self.weeks_entry.pack(side=tk.LEFT)
        
        # Add refresh button
        self.text(220, 145, "#9FCDA8", "", ("Helvetica", 16, "bold"), self.texts["refresh_info"])
        refresh_button = Button(self.root, bg="#9FCDA8", activebackground="#FFA29A", text=self.texts["refresh"], command=self.refresh_curves)
        refresh_button.place(x=240, y=145)
        
        # Add notebook for displaying curves
        self.notebook = ttk.Notebook(self.root)
        self.notebook.place(x=100, y=200, width=600, height=360)
        self.update_tables()
        self.text(75, 200, "#9FCDA8", "", ("Helvetica", 16, "bold"), self.texts["table_info"])
        
        # Add extract options and button
        self.text(750, 250, "#9FCDA8", self.texts["extract"], ("Helvetica", 16, "bold"), self.texts["extract_info"])
        
        self.pao_var = tk.BooleanVar(value=True)
        self.pao_check = tk.Checkbutton(self.root, text="1-DB_PAO", bg="#9FCDA8", activebackground="#FFA29A", variable=self.pao_var)
        self.pao_check.place(x=760, y=290)
        self.entry_pao = self.browse_file(760, 320, "directory", 20)
        
        self.sicpa_var = tk.BooleanVar(value=True)
        self.sicpa_check = tk.Checkbutton(self.root, text="2-SICPA", bg="#9FCDA8", activebackground="#FFA29A", variable=self.sicpa_var)
        self.sicpa_check.place(x=760, y=350)
        self.entry_sicpa = self.browse_file(760, 380, "directory", 20)
        
        self.week_var = tk.BooleanVar(value=True)
        self.week_check = tk.Checkbutton(self.root, text="3-Statistiques", bg="#9FCDA8", activebackground="#FFA29A", variable=self.week_var)
        self.week_check.place(x=760, y=410)
        self.entry_week = self.browse_file(760, 440, "directory", 20)
        
        self.comp_var = tk.BooleanVar(value=True)
        self.comp_check = tk.Checkbutton(self.root, text="4-Semaines completes", bg="#9FCDA8", activebackground="#FFA29A", variable=self.comp_var)
        self.comp_check.place(x=760, y=470)
        self.entry_comp = self.browse_file(760, 500, "directory", 20)
        
        # Add extract button
        self.text(830, 540, "#9FCDA8", "", ("Helvetica", 16, "bold"), self.texts["extract_button"])
        self.Extract = Button(text=self.texts["extract"], bg="#1B4B65", fg="white", activebackground="#81657C", font=("Helvetica", 16, "bold"), state=tk.DISABLED, command=self.extract)
        self.Extract.place(x=850, y=530)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_texts(language="en"):
    # Utiliser resource_path pour obtenir le chemin correct du fichier JSON
    json_path = resource_path("languages.json")
    
    with open(json_path, "r", encoding="utf-8") as file:
        texts = json.load(file)
        return texts.get(language, texts["en"])
if __name__ == "__main__":
    texts = load_texts()

    main = tk.Tk()
    app = MainApp(main, texts)
    main.mainloop()

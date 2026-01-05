import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import base64
import sys
import os
import urllib.request
from pathlib import Path

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class AnimalLearningGameGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Learning Game Generator")
        self.root.geometry("900x700")
        
        # Data storage
        self.animals = []
        self.questions = []
        self.dialouges = []
        self.reading_passages = []
        self.animals_per_row = 3
        
        # Create notebook for sections
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Animals frame
        self.animals_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.animals_frame, text="Cards")
        
        # Questions frame
        self.questions_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.questions_frame, text="Questions")

        # dialouges frame
        self.dialouges_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.dialouges_frame, text="Dialouges")

        # reading passages frame
        self.reading_passages_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.reading_passages_frame, text="Reading passages")
        
        # Settings frame
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text="Settings")

        # successAudio
        self.successAudioEncodedString=""
        try:
            success_audio_path = resource_path("successAudio.mp3")
            with open(success_audio_path, "rb") as success_audio_file:
                self.successAudioEncodedString = base64.b64encode(success_audio_file.read()).decode("utf-8")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load success audio: {str(e)}")
        
        self.setup_animals_section()
        self.setup_questions_section()
        self.setup_dialouges_section()
        self.setup_reading_passages_section()
        self.setup_settings_section()
        self.setup_menu()
        self.setup_context_menus()

    def setup_context_menus(self):
        # Create a context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Cut", command=lambda: self.cut_text())
        self.context_menu.add_command(label="Copy", command=lambda: self.copy_text())
        self.context_menu.add_command(label="Paste", command=lambda: self.paste_text())
        
        # Bind right-click event to all entry widgets
        self.root.bind_class("TEntry", "<Button-3>", self.show_context_menu)
        self.root.bind_class("Text", "<Button-3>", self.show_context_menu)
        
    def show_context_menu(self, event):
        # Store the widget that was right-clicked
        self.focused_widget = event.widget
        # Show the context menu at the cursor position
        self.context_menu.post(event.x_root, event.y_root)
        
    def cut_text(self):
        if hasattr(self, 'focused_widget') and isinstance(self.focused_widget, tk.Entry):
            self.focused_widget.event_generate("<<Cut>>")
            
    def copy_text(self):
        if hasattr(self, 'focused_widget') and isinstance(self.focused_widget, tk.Entry):
            self.focused_widget.event_generate("<<Copy>>")
            
    def paste_text(self):
        if hasattr(self, 'focused_widget') and isinstance(self.focused_widget, tk.Entry):
            self.focused_widget.event_generate("<<Paste>>")
        
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_config)
        file_menu.add_command(label="Load", command=self.load_config)
        file_menu.add_command(label="Save", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="Generate HTML", command=self.generate_html)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menubar)
        
    def setup_animals_section(self):
        # Animals per row setting
        ttk.Label(self.animals_frame, text="Cards per row:").grid(row=0, column=0, sticky='w', pady=5)
        self.animals_per_row_var = tk.StringVar(value="3")
        animals_per_row_spinbox = ttk.Spinbox(self.animals_frame, from_=1, to=6, textvariable=self.animals_per_row_var, width=5)
        animals_per_row_spinbox.grid(row=0, column=1, sticky='w', pady=5)
        
        # Add animal button
        ttk.Button(self.animals_frame, text="Add Card", command=self.add_animal_frame).grid(row=0, column=2, pady=5, padx=5)
        
        #  # Create a frame for the canvas and scrollbar
        container = ttk.Frame(self.animals_frame)
        container.grid(row=1, column=0, columnspan=3, sticky='nsew', pady=10)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.animals_container = ttk.Frame(canvas)
        
        # Configure the canvas
        self.animals_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the animals container
        canvas.create_window((0, 0), window=self.animals_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configure grid weights
        self.animals_frame.columnconfigure(0, weight=1)
        self.animals_frame.rowconfigure(1, weight=1)
        
        # Add initial animal frame
        self.add_animal_frame()
        
    def add_animal_frame(self):
        frame = ttk.Frame(self.animals_container, relief='groove', borderwidth=1)
        frame.pack(fill='x', pady=5, padx=5)
        
        # Image URL
        ttk.Label(frame, text="Image URL:").grid(row=0, column=0, sticky='w', pady=2)
        image_url_entry = ttk.Entry(frame, width=40)
        image_url_entry.grid(row=0, column=1, pady=2, padx=5)
        
        # Title
        ttk.Label(frame, text="Title (e.g., 'Cat (قطة)'):").grid(row=1, column=0, sticky='w', pady=2)
        title_entry = ttk.Entry(frame, width=40)
        title_entry.grid(row=1, column=1, pady=2, padx=5)
        
        # Word to speak
        ttk.Label(frame, text="Word to speak (Arabic):").grid(row=2, column=0, sticky='w', pady=2)
        word_entry = ttk.Entry(frame, width=40)
        word_entry.grid(row=2, column=1, pady=2, padx=5)
        
        # Audio file
        ttk.Label(frame, text="Audio file:").grid(row=3, column=0, sticky='w', pady=2)
        audio_frame = ttk.Frame(frame)
        audio_frame.grid(row=3, column=1, sticky='we', pady=2)
        audio_entry = ttk.Entry(audio_frame, width=35)
        audio_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(audio_frame, text="Browse", command=lambda: self.browse_audio(audio_entry)).pack(side='right', padx=5)

        ttk.Button(frame, text="Duplicate", 
           command=lambda: self.duplicate_animal_frame(frame)) \
       .grid(row=4, column=0, sticky='w', pady=5)
        
        # Remove button
        ttk.Button(frame, text="Remove", command=lambda: self.remove_animal_frame(frame)).grid(row=4, column=1, sticky='e', pady=5)
        
        # Store references
        frame.image_url = image_url_entry
        frame.title = title_entry
        frame.word = word_entry
        frame.audio = audio_entry
        
        self.animals.append(frame)

    def duplicate_animal_frame(self, source_frame):
        # 1. Get values from source frame
        image_url = source_frame.image_url.get()
        title = source_frame.title.get()
        word = source_frame.word.get()
        audio = source_frame.audio.get()
        
        # 2. Create new frame (adds at end automatically via pack)
        new_frame = ttk.Frame(self.animals_container, relief='groove', borderwidth=1)
        new_frame.pack(fill='x', pady=5, padx=5)
        
        # Image URL
        ttk.Label(new_frame, text="Image URL:").grid(row=0, column=0, sticky='w', pady=2)
        image_url_entry = ttk.Entry(new_frame, width=40)
        image_url_entry.grid(row=0, column=1, pady=2, padx=5)
        
        # Title
        ttk.Label(new_frame, text="Title (e.g., 'Cat (قطة)'):").grid(row=1, column=0, sticky='w', pady=2)
        title_entry = ttk.Entry(new_frame, width=40)
        title_entry.grid(row=1, column=1, pady=2, padx=5)
        
        # Word to speak
        ttk.Label(new_frame, text="Word to speak (Arabic):").grid(row=2, column=0, sticky='w', pady=2)
        word_entry = ttk.Entry(new_frame, width=40)
        word_entry.grid(row=2, column=1, pady=2, padx=5)
        
        # Audio file
        ttk.Label(new_frame, text="Audio file:").grid(row=3, column=0, sticky='w', pady=2)
        audio_frame = ttk.Frame(new_frame)
        audio_frame.grid(row=3, column=1, sticky='we', pady=2)
        audio_entry = ttk.Entry(audio_frame, width=35)
        audio_entry.pack(side='left', fill='x', expand=True)
        ttk.Button(audio_frame, text="Browse", command=lambda: self.browse_audio(audio_entry)).pack(side='right', padx=5)

        ttk.Button(new_frame, text="Duplicate", 
        command=lambda: self.duplicate_animal_frame(new_frame)) \
    .grid(row=4, column=0, sticky='w', pady=5)
        
        # Remove button
        ttk.Button(new_frame, text="Remove", command=lambda: self.remove_animal_frame(new_frame)).grid(row=4, column=1, sticky='e', pady=5)
        
        # Store references 
        new_frame.image_url = image_url_entry
        new_frame.title = title_entry
        new_frame.word = word_entry
        new_frame.audio = audio_entry
        
        # NOW insert the values
        image_url_entry.insert(0, image_url)
        title_entry.insert(0, title)
        word_entry.insert(0, word)
        audio_entry.insert(0, audio)
        
        # Add to tracking list
        self.animals.append(new_frame)

    def remove_animal_frame(self, frame):
        frame.destroy()
        self.animals.remove(frame)
        
    def browse_audio(self, audio_entry):
        filename = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio files", "*.mp3 *.wav *.ogg *.OPUS"), ("All files", "*.*")]
        )
        if filename:
            audio_entry.delete(0, tk.END)
            audio_entry.insert(0, filename)
            
    def setup_questions_section(self):
        # Add question button
        ttk.Button(self.questions_frame, text="Add Question", command=self.add_question_frame).pack(pady=5)
        
        # Create a frame for the canvas and scrollbar
        container = ttk.Frame(self.questions_frame)
        container.pack(fill='both', expand=True, pady=10)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.questions_container = ttk.Frame(canvas)
        
        # Configure the canvas
        self.questions_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the questions container
        canvas.create_window((0, 0), window=self.questions_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add initial question frame
        self.add_question_frame()
        
    def add_question_frame(self):
        frame = ttk.Frame(self.questions_container, relief='groove', borderwidth=1)
        frame.pack(fill='x', pady=5, padx=5)
        
        # Question image URL
        ttk.Label(frame, text="Question Image URL (optional):").grid(row=0, column=0, sticky='w', pady=2)
        image_url_entry = ttk.Entry(frame, width=50)
        image_url_entry.grid(row=0, column=1, columnspan=2, sticky='we', pady=2, padx=5)
        
        # Question text (moved to row 1)
        ttk.Label(frame, text="Question Text:").grid(row=1, column=0, sticky='w', pady=2)
        question_text_entry = ttk.Entry(frame, width=50)
        question_text_entry.grid(row=1, column=1, columnspan=2, sticky='we', pady=2, padx=5)
        
        # Answers frame (moved to row 2)
        answers_frame = ttk.LabelFrame(frame, text="Answers")
        answers_frame.grid(row=2, column=0, columnspan=3, sticky='we', pady=5, padx=5)
        
        # Correct answer variable
        correct_answer_var = tk.StringVar()
        
        # Store answer entries and radio buttons
        answer_entries = []
        radio_buttons = []
        
        # Function to add answer
        def add_answer_row():
            row = len(answer_entries)
            # Radio button for correct answer
            rb = ttk.Radiobutton(answers_frame, variable=correct_answer_var, value=str(row))
            rb.grid(row=row, column=0, padx=5)
            # Answer entry
            entry = ttk.Entry(answers_frame, width=40)
            entry.grid(row=row, column=1, pady=2, padx=5, sticky='we')
            
            # Create the remove button first
            btn = ttk.Button(answers_frame, text="Remove")
            btn.grid(row=row, column=2, padx=5)
            
            # Now configure the command with the button reference
            btn.configure(command=lambda: remove_answer_row(rb, entry, btn))
            
            answer_entries.append(entry)
            radio_buttons.append(rb)
            
        def remove_answer_row(rb, entry, btn):
            idx = answer_entries.index(entry)
            answer_entries.remove(entry)
            radio_buttons.remove(rb)
            rb.destroy()
            entry.destroy()
            btn.destroy()
            # Update radio button values
            for i, rb in enumerate(radio_buttons):
                rb.config(value=str(i))
            # Update correct answer if needed
            if correct_answer_var.get() == str(idx):
                correct_answer_var.set("")
                
        # Add answer button
        add_answer_btn = ttk.Button(answers_frame, text="Add Answer", command=add_answer_row)
        add_answer_btn.grid(row=0, column=2, padx=5)
        
        # Add initial answers
        for _ in range(2):
            add_answer_row()
            
        # Remove question button
        ttk.Button(frame, text="Remove Question", command=lambda: self.remove_question_frame(frame)).grid(row=4, column=2, sticky='e', pady=5)
        ttk.Button(frame, text="Add Answer", command=lambda: add_answer_row()).grid(row=4, column=3, sticky='e', pady=5)
        
        # Configure grid weights
        frame.columnconfigure(1, weight=1)
        answers_frame.columnconfigure(1, weight=1)
        
        # Store references
        frame.image_url = image_url_entry
        frame.question_text = question_text_entry
        frame.answer_entries = answer_entries
        frame.radio_buttons = radio_buttons
        frame.correct_answer_var = correct_answer_var
        frame.add_answer_row = add_answer_row
        frame.remove_answer_row = remove_answer_row
        
        self.questions.append(frame)
        
    def remove_question_frame(self, frame):
        frame.destroy()
        self.questions.remove(frame)

    ### dialouges ###

    def setup_dialouges_section(self):
        # Add dialouge button
        ttk.Button(self.dialouges_frame, text="Add Dialogue", command=self.add_dialogue_frame).pack(pady=5)
        
        # Create a frame for the canvas and scrollbar
        container = ttk.Frame(self.dialouges_frame)
        container.pack(fill='both', expand=True, pady=10)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.dialouges_container = ttk.Frame(canvas)
        
        # Configure the canvas
        self.dialouges_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the dialogue container
        canvas.create_window((0, 0), window=self.dialouges_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add initial dialogue frame
        self.add_dialogue_frame()

    def add_dialogue_frame(self):
        dialogue_data = {
            "title":"",
            "lines": []
        }
        self.dialouges.append(dialogue_data)

        # ================= Dialogue Frame =================
        dialogue_frame = ttk.LabelFrame(
            self.dialouges_container,
            text=f"Dialogue {len(self.dialouges)}",
            padding=10
        )
        dialogue_frame.pack(fill="x", pady=10, padx=5)

        # ================= Dialogue Title =================
        ttk.Label(dialogue_frame, text="Dialogue Title:").pack(anchor="w", padx=5)
        title_entry = ttk.Entry(dialogue_frame, width=40)
        title_entry.pack(fill="x", padx=5, pady=(0, 10))
        title_entry.bind(
            "<KeyRelease>",
            lambda e: dialogue_data.update({"title": title_entry.get()})
        )

        # ================= Remove Dialogue =================
        def remove_dialogue():
            self.dialouges.remove(dialogue_data)
            dialogue_frame.destroy()

        ttk.Button(
            dialogue_frame,
            text="Delete Dialogue",
            command=remove_dialogue
        ).pack(anchor="e", pady=5)

        # ================= Lines Container =================
        lines_container = ttk.Frame(dialogue_frame)
        lines_container.pack(fill="x")

        # ================= duplicate Line =================
        def duplicate_line(image_url,position,text,translation,audio):

            line_data = {
                "image": image_url,
                "position": position,
                "text": text,
                "translation":translation,
                "audio": audio
            }
            dialogue_data["lines"].append(line_data)

            line_frame = ttk.Frame(lines_container, padding=5, relief="solid")
            line_frame.pack(fill="x", pady=5)

            # ---- Image ----
            ttk.Label(line_frame, text="Image URL:").grid(row=0, column=0, sticky="w")
            image_entry = ttk.Entry(line_frame, width=40)
            image_entry.grid(row=0, column=1, padx=5)
            image_entry.bind(
                "<KeyRelease>",
                lambda e: line_data.update({"image": image_entry.get()})
            )

            # ---- Position ----
            ttk.Label(line_frame, text="Position:").grid(row=0, column=2, padx=5)
            position_var = tk.StringVar(value="left")
            position_menu = ttk.Combobox(
                line_frame,
                textvariable=position_var,
                values=["left", "right"],
                state="readonly",
                width=7
            )
            position_menu.grid(row=0, column=3)
            position_var.trace_add(
                "write",
                lambda *args: line_data.update({"position": position_var.get()})
            )

            # ---- Text ----
            ttk.Label(line_frame, text="Dialogue Text:").grid(row=1, column=0, sticky="nw")
            text_box = tk.Text(line_frame, height=3, width=60)
            text_box.grid(row=1, column=1, columnspan=3, pady=5)

            def update_text(event):
                line_data["text"] = text_box.get("1.0", "end").strip()

            text_box.bind("<KeyRelease>", update_text)

            # ---- Text translation ----
            ttk.Label(line_frame, text="Dialogue Text Translation:").grid(row=2, column=0, sticky="nw")
            text_translation_box = tk.Text(line_frame, height=3, width=60)
            text_translation_box.grid(row=2, column=1, columnspan=3, pady=5)

            def update_translation(event):
                line_data["translation"] = text_translation_box.get("1.0", "end").strip()

            text_translation_box.bind("<KeyRelease>", update_translation)

            # ---- Audio ----
            ttk.Label(line_frame, text="Audio:").grid(row=3, column=0, sticky="w")
            audio_entry = ttk.Entry(line_frame, width=40)
            audio_entry.grid(row=3, column=1, padx=5)

            ttk.Button(
                line_frame,
                text="Browse",
                command=lambda: (
                    self.browse_audio(audio_entry),
                    line_data.update({"audio": audio_entry.get()})
                )
            ).grid(row=3, column=2)

            # ---- Delete Line ----
            def remove_line():
                dialogue_data["lines"].remove(line_data)
                line_frame.destroy()

            ttk.Button(
                line_frame,
                text="Delete Line",
                command=remove_line
            ).grid(row=4, column=3, padx=5)

            # NOW insert the values
            image_entry.insert(0, image_url)
            position_var.set(position)  
            text_box.insert("1.0", text) 
            text_translation_box.insert("1.0", translation)
            audio_entry.insert(0, audio)
            
            ttk.Button(line_frame, text="Duplicate", 
            command=lambda: duplicate_line(image_entry.get(),position_var.get(),text_box.get("1.0", "end-1c"),text_translation_box.get("1.0", "end-1c"),audio_entry.get())) \
        .grid(row=4, column=2, sticky='w', pady=5) 

        # ================= Add Line =================
        def add_line():
            line_data = {
                "image": "",
                "position": "left",
                "text": "",
                "translation":"",
                "audio": ""
            }
            dialogue_data["lines"].append(line_data)

            line_frame = ttk.Frame(lines_container, padding=5, relief="solid")
            line_frame.pack(fill="x", pady=5)

            # ---- Image ----
            ttk.Label(line_frame, text="Image URL:").grid(row=0, column=0, sticky="w")
            image_entry = ttk.Entry(line_frame, width=40)
            image_entry.grid(row=0, column=1, padx=5)
            image_entry.bind(
                "<KeyRelease>",
                lambda e: line_data.update({"image": image_entry.get()})
            )

            # ---- Position ----
            ttk.Label(line_frame, text="Position:").grid(row=0, column=2, padx=5)
            position_var = tk.StringVar(value="left")
            position_menu = ttk.Combobox(
                line_frame,
                textvariable=position_var,
                values=["left", "right"],
                state="readonly",
                width=7
            )
            position_menu.grid(row=0, column=3)
            position_var.trace_add(
                "write",
                lambda *args: line_data.update({"position": position_var.get()})
            )

            # ---- Text ----
            ttk.Label(line_frame, text="Dialogue Text:").grid(row=1, column=0, sticky="nw")
            text_box = tk.Text(line_frame, height=3, width=60)
            text_box.grid(row=1, column=1, columnspan=3, pady=5)

            def update_text(event):
                line_data["text"] = text_box.get("1.0", "end").strip()

            text_box.bind("<KeyRelease>", update_text)

            # ---- Text translation ----
            ttk.Label(line_frame, text="Dialogue Text Translation:").grid(row=2, column=0, sticky="nw")
            text_translation_box = tk.Text(line_frame, height=3, width=60)
            text_translation_box.grid(row=2, column=1, columnspan=3, pady=5)

            def update_translation(event):
                line_data["translation"] = text_translation_box.get("1.0", "end").strip()

            text_translation_box.bind("<KeyRelease>", update_translation)

            # ---- Audio ----
            ttk.Label(line_frame, text="Audio:").grid(row=3, column=0, sticky="w")
            audio_entry = ttk.Entry(line_frame, width=40)
            audio_entry.grid(row=3, column=1, padx=5)

            ttk.Button(
                line_frame,
                text="Browse",
                command=lambda: (
                    self.browse_audio(audio_entry),
                    line_data.update({"audio": audio_entry.get()})
                )
            ).grid(row=3, column=2)

            # ---- Delete Line ----
            def remove_line():
                dialogue_data["lines"].remove(line_data)
                line_frame.destroy()

            ttk.Button(
                line_frame,
                text="Delete Line",
                command=remove_line
            ).grid(row=4, column=3, padx=5)

            ttk.Button(line_frame, text="Duplicate", 
            command=lambda: duplicate_line(image_entry.get(),position_var.get(),text_box.get("1.0", "end-1c"),text_translation_box.get("1.0", "end-1c"),audio_entry.get())) \
        .grid(row=4, column=2, sticky='w', pady=5) 

        # ================= Buttons =================
        ttk.Button(
            dialogue_frame,
            text="Add Dialogue Line",
            command=add_line
        ).pack(pady=5)

        # Add first line by default
        add_line()

    def add_dialogue_frame_loaded_config(self,loaded_title,loaded_lines):
        dialogue_data = {
            "title":loaded_title,
            "lines": []
        }
        self.dialouges.append(dialogue_data)

        # ================= Dialogue Frame =================
        dialogue_frame = ttk.LabelFrame(
            self.dialouges_container,
            text=f"Dialogue {len(self.dialouges)}",
            padding=10
        )
        dialogue_frame.pack(fill="x", pady=10, padx=5)

        # ================= Dialogue Title =================
        ttk.Label(dialogue_frame, text="Dialogue Title:").pack(anchor="w", padx=5)
        title_entry = ttk.Entry(dialogue_frame, width=40)
        title_entry.pack(fill="x", padx=5, pady=(0, 10))
        title_entry.bind(
            "<KeyRelease>",
            lambda e: dialogue_data.update({"title": title_entry.get()})
        )
        # populate with loaded title
        title_entry.insert(0, loaded_title)

        # ================= Remove Dialogue =================
        def remove_dialogue():
            self.dialouges.remove(dialogue_data)
            dialogue_frame.destroy()

        ttk.Button(
            dialogue_frame,
            text="Delete Dialogue",
            command=remove_dialogue
        ).pack(anchor="e", pady=5)

        # ================= Lines Container =================
        lines_container = ttk.Frame(dialogue_frame)
        lines_container.pack(fill="x")

        # ================= duplicate Line =================
        def duplicate_line(image_url,position,text,translation,audio):

            line_data = {
                "image": image_url,
                "position": position,
                "text": text,
                "translation":translation,
                "audio": audio
            }
            dialogue_data["lines"].append(line_data)
            print("first print")
            line_frame = ttk.Frame(lines_container, padding=5, relief="solid")
            line_frame.pack(fill="x", pady=5)
            print("sec print")
            # ---- Image ----
            ttk.Label(line_frame, text="Image URL:").grid(row=0, column=0, sticky="w")
            image_entry = ttk.Entry(line_frame, width=40)
            image_entry.grid(row=0, column=1, padx=5)
            image_entry.bind(
                "<KeyRelease>",
                lambda e: line_data.update({"image": image_entry.get()})
            )
            print("thi print")
            # ---- Position ----
            ttk.Label(line_frame, text="Position:").grid(row=0, column=2, padx=5)
            position_var = tk.StringVar(value="left")
            position_menu = ttk.Combobox(
                line_frame,
                textvariable=position_var,
                values=["left", "right"],
                state="readonly",
                width=7
            )
            position_menu.grid(row=0, column=3)
            position_var.trace_add(
                "write",
                lambda *args: line_data.update({"position": position_var.get()})
            )
            print("four print")
            # ---- Text ----
            ttk.Label(line_frame, text="Dialogue Text:").grid(row=1, column=0, sticky="nw")
            text_box = tk.Text(line_frame, height=3, width=60)
            text_box.grid(row=1, column=1, columnspan=3, pady=5)

            def update_text(event):
                line_data["text"] = text_box.get("1.0", "end").strip()

            text_box.bind("<KeyRelease>", update_text)
            print("fifth print")
            # ---- Text translation ----
            ttk.Label(line_frame, text="Dialogue Text Translation:").grid(row=2, column=0, sticky="nw")
            text_translation_box = tk.Text(line_frame, height=3, width=60)
            text_translation_box.grid(row=2, column=1, columnspan=3, pady=5)

            def update_translation(event):
                line_data["translation"] = text_translation_box.get("1.0", "end").strip()

            text_translation_box.bind("<KeyRelease>", update_translation)
            print("sixth print")
            # ---- Audio ----
            ttk.Label(line_frame, text="Audio:").grid(row=3, column=0, sticky="w")
            audio_entry = ttk.Entry(line_frame, width=40)
            audio_entry.grid(row=3, column=1, padx=5)

            ttk.Button(
                line_frame,
                text="Browse",
                command=lambda: (
                    self.browse_audio(audio_entry),
                    line_data.update({"audio": audio_entry.get()})
                )
            ).grid(row=3, column=2)
            print("seventh print")
            # ---- Delete Line ----
            def remove_line():
                dialogue_data["lines"].remove(line_data)
                line_frame.destroy()

            ttk.Button(
                line_frame,
                text="Delete Line",
                command=remove_line
            ).grid(row=4, column=3, padx=5)
            print("eight print")
            # NOW insert the values
            image_entry.insert(0, image_url)
            position_var.set(position)  
            text_box.insert("1.0", text) 
            text_translation_box.insert("1.0", translation)
            audio_entry.insert(0, audio)
            print("ninth print")
            ttk.Button(line_frame, text="Duplicate", 
            command=lambda: duplicate_line(image_entry.get(),position_var.get(),text_box.get("1.0", "end-1c"),text_translation_box.get("1.0", "end-1c"),audio_entry.get())) \
        .grid(row=4, column=2, sticky='w', pady=5) 

        # ================= Add Line =================
        def add_line():
            line_data = {
                "image": "",
                "position": "left",
                "text": "",
                "translation":"",
                "audio": ""
            }
            dialogue_data["lines"].append(line_data)

            line_frame = ttk.Frame(lines_container, padding=5, relief="solid")
            line_frame.pack(fill="x", pady=5)

            # ---- Image ----
            ttk.Label(line_frame, text="Image URL:").grid(row=0, column=0, sticky="w")
            image_entry = ttk.Entry(line_frame, width=40)
            image_entry.grid(row=0, column=1, padx=5)
            image_entry.bind(
                "<KeyRelease>",
                lambda e: line_data.update({"image": image_entry.get()})
            )

            # ---- Position ----
            ttk.Label(line_frame, text="Position:").grid(row=0, column=2, padx=5)
            position_var = tk.StringVar(value="left")
            position_menu = ttk.Combobox(
                line_frame,
                textvariable=position_var,
                values=["left", "right"],
                state="readonly",
                width=7
            )
            position_menu.grid(row=0, column=3)
            position_var.trace_add(
                "write",
                lambda *args: line_data.update({"position": position_var.get()})
            )

            # ---- Text ----
            ttk.Label(line_frame, text="Dialogue Text:").grid(row=1, column=0, sticky="nw")
            text_box = tk.Text(line_frame, height=3, width=60)
            text_box.grid(row=1, column=1, columnspan=3, pady=5)

            def update_text(event):
                line_data["text"] = text_box.get("1.0", "end").strip()

            text_box.bind("<KeyRelease>", update_text)

            # ---- Text translation ----
            ttk.Label(line_frame, text="Dialogue Text Translation:").grid(row=2, column=0, sticky="nw")
            text_translation_box = tk.Text(line_frame, height=3, width=60)
            text_translation_box.grid(row=2, column=1, columnspan=3, pady=5)

            def update_translation(event):
                line_data["translation"] = text_translation_box.get("1.0", "end").strip()

            text_translation_box.bind("<KeyRelease>", update_translation)

            # ---- Audio ----
            ttk.Label(line_frame, text="Audio:").grid(row=3, column=0, sticky="w")
            audio_entry = ttk.Entry(line_frame, width=40)
            audio_entry.grid(row=3, column=1, padx=5)

            ttk.Button(
                line_frame,
                text="Browse",
                command=lambda: (
                    self.browse_audio(audio_entry),
                    line_data.update({"audio": audio_entry.get()})
                )
            ).grid(row=3, column=2)

            # ---- Delete Line ----
            def remove_line():
                dialogue_data["lines"].remove(line_data)
                line_frame.destroy()

            ttk.Button(
                line_frame,
                text="Delete Line",
                command=remove_line
            ).grid(row=4, column=3, padx=5)

            ttk.Button(line_frame, text="Duplicate", 
            command=lambda: duplicate_line(image_entry.get(),position_var.get(),text_box.get("1.0", "end-1c"),text_translation_box.get("1.0", "end-1c"),audio_entry.get())) \
        .grid(row=4, column=2, sticky='w', pady=5) 

        # ================= Buttons =================
        ttk.Button(
            dialogue_frame,
            text="Add Dialogue Line",
            command=add_line
        ).pack(pady=5)
        for loaded_line in loaded_lines:
            # Add loaded line using function duplicate line
            duplicate_line(loaded_line["image"],loaded_line["position"],loaded_line["text"],loaded_line["translation"],loaded_line["audio"])

    def setup_reading_passages_section(self):
        # Add reading_passage button
        ttk.Button(self.reading_passages_frame, text="Add Dialogue", command=self.add_reading_passage_frame).pack(pady=5)
        
        # Create a frame for the canvas and scrollbar
        container = ttk.Frame(self.reading_passages_frame)
        container.pack(fill='both', expand=True, pady=10)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.reading_passages_container = ttk.Frame(canvas)
        
        # Configure the canvas
        self.reading_passages_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Create a window in the canvas for the reading_passage container
        canvas.create_window((0, 0), window=self.reading_passages_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack the canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add initial reading_passage frame
        self.add_reading_passage_frame()

    def add_reading_passage_frame(self):
        passage_data = {
            "title": "",
            "text": "",
            "questions": []
        }
        self.reading_passages.append(passage_data)

        # ================= Passage Frame =================
        passage_frame = ttk.LabelFrame(
            self.reading_passages_container,
            text=f"Reading Passage {len(self.reading_passages)}",
            padding=10
        )
        passage_frame.pack(fill="x", pady=10, padx=5)

        # ================= Remove Passage =================
        def remove_passage():
            self.reading_passages.remove(passage_data)
            passage_frame.destroy()

        ttk.Button(
            passage_frame,
            text="Delete Passage",
            command=remove_passage
        ).pack(anchor="e", pady=5)

        # ================= Title =================
        ttk.Label(passage_frame, text="Passage Title:").pack(anchor="w")
        title_entry = ttk.Entry(passage_frame, width=60)
        title_entry.pack(fill="x", pady=3)

        title_entry.bind(
            "<KeyRelease>",
            lambda e: passage_data.update({"title": title_entry.get()})
        )

        # ================= Passage Text =================
        ttk.Label(passage_frame, text="Passage Text:").pack(anchor="w")
        text_box = tk.Text(passage_frame, height=6)
        text_box.pack(fill="x", pady=5)

        def update_passage_text(event):
            passage_data["text"] = text_box.get("1.0", "end").strip()

        text_box.bind("<KeyRelease>", update_passage_text)

        # ================= Questions Container ================= 
        questions_container = ttk.Frame(passage_frame)
        questions_container.pack(fill="x", pady=10)

        # ================= Add Question =================
        def add_question():
            question_data = {
                "sentence": "",
                "blank_after_word": 0,
                "choices": [],
                "correct_choice_index": None
            }
            passage_data["questions"].append(question_data)

            question_frame = ttk.Frame(questions_container, padding=5, relief="solid")
            question_frame.pack(fill="x", pady=5)

            # ---- Sentence ----
            ttk.Label(question_frame, text="Sentence:").grid(row=0, column=0, sticky="w")
            sentence_entry = ttk.Entry(question_frame, width=60)
            sentence_entry.grid(row=0, column=1, columnspan=3, pady=3)

            sentence_entry.bind(
                "<KeyRelease>",
                lambda e: question_data.update({"sentence": sentence_entry.get()})
            )

            # ---- Blank position ----
            ttk.Label(question_frame, text="Blank after word #:").grid(row=1, column=0, sticky="w")
            blank_spin = ttk.Spinbox(question_frame, from_=0, to=50, width=5)
            blank_spin.grid(row=1, column=1, sticky="w")

            blank_spin.bind(
                "<KeyRelease>",
                lambda e: question_data.update(
                    {"blank_after_word": int(blank_spin.get() or 0)}
                )
            )

            # ================= Choices Container =================
            choices_container = ttk.Frame(question_frame)
            choices_container.grid(row=2, column=0, columnspan=4, pady=5, sticky="w")

            correct_choice_var = tk.IntVar(value=-1)
            # ---- Add Choice ----
            def add_choice():
                choice_data = {"value": ""}
                question_data["choices"].append(choice_data)

                choice_frame = ttk.Frame(choices_container)
                choice_frame.pack(fill="x", pady=2)

                choice_index = len(question_data["choices"])

                radio = ttk.Radiobutton(
                    choice_frame,
                    variable=correct_choice_var,
                    value=choice_index,
                    command=lambda: question_data.update({
                        "correct_choice_index": correct_choice_var.get()-1
                    })
                )
                radio.pack(side="left")

                choice_entry = ttk.Entry(choice_frame, width=40)
                choice_entry.pack(side="left", padx=3)

                choice_entry.bind(
                    "<KeyRelease>",
                    lambda e: choice_data.update({"value": choice_entry.get()})
                )

                def remove_choice():
                    question_data["choices"].remove(choice_data)
                    choice_frame.destroy()
                    if question_data["correct_choice_index"] == choice_index:
                        question_data["correct_choice_index"] = None
                        correct_choice_var.set(-1)

                ttk.Button(
                    choice_frame,
                    text="Delete",
                    command=remove_choice
                ).pack(side="left")

            ttk.Button(
                question_frame,
                text="Add Choice",
                command=add_choice
            ).grid(row=3, column=0, pady=5, sticky="w")

            # ---- Remove Question ----
            def remove_question():
                passage_data["questions"].remove(question_data)
                question_frame.destroy()

            ttk.Button(
                question_frame,
                text="Delete Question",
                command=remove_question
            ).grid(row=3, column=3, pady=5, sticky="e")

        # ================= Add Question Button =================
        ttk.Button(
            passage_frame,
            text="Add Question",
            command=add_question
        ).pack(pady=5)

        # Add first question by default
        add_question()

        
    def setup_settings_section(self):
        # Output file settings
        ttk.Label(self.settings_frame, text="Output File:").grid(row=0, column=0, sticky='w', pady=5)
        self.output_file_var = tk.StringVar(value="animal_game.html")
        output_entry = ttk.Entry(self.settings_frame, textvariable=self.output_file_var, width=40)
        output_entry.grid(row=0, column=1, pady=5, padx=5, sticky='we')
        ttk.Button(self.settings_frame, text="Browse", command=self.browse_output).grid(row=0, column=2, pady=5, padx=5)
        
        # Configure grid weights
        self.settings_frame.columnconfigure(1, weight=1)

    def setup_readings_section(self):
        return
        
    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Save HTML File",
            defaultextension=".html",
            filetypes=[("HTML files", "*.html"), ("All files", "*.*")]
        )
        if filename:
            self.output_file_var.set(filename)
            
    def new_config(self):
        # Clear all data
        for animal in self.animals:
            animal.destroy()
        self.animals = []
        
        for question in self.questions:
            question.destroy()
        self.questions = []
        #clear dialogues data and ui widgets
        self.dialouges = []
        # Destroy all widgets inside the dialouges_container frame
        for widget in self.dialouges_container.winfo_children():
            widget.destroy()
        # Optional: Update the scroll region
        canvas = self.dialouges_container.master  # Get the parent canvas
        if canvas:
            canvas.configure(scrollregion=canvas.bbox("all"))

        # clear reading passages data and ui widgets
        self.reading_passages = []
        # Destroy all widgets inside the reading_passages_container frame
        for widget in self.reading_passages_container.winfo_children():
            widget.destroy()
        # Optional: Update the scroll region
        canvas = self.reading_passages_container.master  # Get the parent canvas
        if canvas:
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Reset settings
        self.animals_per_row_var.set("3")
        self.output_file_var.set("animal_game.html")
        
    def load_config(self):
        filename = filedialog.askopenfilename(
            title="Load Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            # Clear current data
            self.new_config()
            
            # Load animals
            for animal_data in config.get('animals', []):
                self.add_animal_frame()
                animal_frame = self.animals[-1]
                animal_frame.image_url.insert(0, animal_data.get('image_url', ''))
                animal_frame.title.insert(0, animal_data.get('title', ''))
                animal_frame.word.insert(0, animal_data.get('word', ''))
                animal_frame.audio.insert(0, animal_data.get('audio', ''))
                
            # Load questions
            for question_data in config.get('questions', []):
                self.add_question_frame()
                question_frame = self.questions[-1]
                question_frame.image_url.insert(0, question_data.get('image_url', '')) 
                question_frame.question_text.insert(0, question_data.get('text', ''))
                
                # # Clear default answers - this part gives error 
                # for entry in question_frame.answer_entries[:]:
                #     question_frame.remove_answer_row(
                #         question_frame.radio_buttons[question_frame.answer_entries.index(entry)],
                #         entry,
                #         None  # Button reference not stored, but it's OK for initial load
                #     )
                
                # Add answers from config
                answers = question_data.get('answers', [])
                correct_index = question_data.get('correct_index', 0)
                
                for i, answer in enumerate(answers):
                    question_frame.add_answer_row()
                    question_frame.answer_entries[-1].insert(0, answer)
                    
                # Set correct answer
                if answers and 0 <= correct_index < len(answers):
                    question_frame.correct_answer_var.set(str(correct_index))

            # load dialouges
            for dialouge in config.get('dialogues',[]):
                self.add_dialogue_frame_loaded_config(dialouge['title'],dialouge['lines'])

            # load reading_passages
                    
            # Load settings
            self.animals_per_row_var.set(str(config.get('animals_per_row', 3)))
            self.output_file_var.set(config.get('output_file', 'animal_game.html'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {str(e)}")
            
    def save_config(self):
        filename = filedialog.asksaveasfilename(
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not filename:
            return
            
        try:
            # Prepare animals data
            animals_data = []
            for animal in self.animals:
                animals_data.append({
                    'image_url': animal.image_url.get(),
                    'title': animal.title.get(),
                    'word': animal.word.get(),
                    'audio': animal.audio.get()
                })
                
            # Prepare questions data
            questions_data = []
            for question in self.questions:
                answers = [entry.get() for entry in question.answer_entries]
                correct_index = int(question.correct_answer_var.get()) if question.correct_answer_var.get() else 0
                
                questions_data.append({
                    'image_url': question.image_url.get(),
                    'text': question.question_text.get(),
                    'answers': answers,
                    'correct_index': correct_index
                })
                
            # Prepare config
            config = {
                'animals': animals_data,
                'questions': questions_data,
                'dialogues':self.dialouges,
                'reading_passages':self.reading_passages,
                'animals_per_row': int(self.animals_per_row_var.get()),
                'output_file': self.output_file_var.get()
            }
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")

    def generate_reading_passage_html(self, passage, passage_index):
        """Generate HTML for a reading passage with questions."""
        
        # Generate questions HTML
        questions_html = ""
        for q_index, question in enumerate(passage["questions"]):
            # Split sentence into words
            words = question["sentence"].split()
            
            # Create sentence with dropdown at the specified position
            sentence_parts = []
            for i, word in enumerate(words):
                if i == question["blank_after_word"]:
                    # Create dropdown for choices
                    options_html = '<option value="">اختر إجابة</option>'
                    for idx, choice in enumerate(question["choices"]):
                        options_html += f'<option value="{idx}">{choice["value"]}</option>'
                    
                    dropdown_html = f'''
                    <select class="passage-dropdown" data-correct-index="{question["correct_choice_index"]}">
                        {options_html}
                    </select>
                    '''
                    sentence_parts.append(dropdown_html)
                sentence_parts.append(f'<span>{word}</span>')
            
            # Add dropdown at the end if blank_after_word is after last word
            if question["blank_after_word"] >= len(words):
                options_html = '<option value="">اختر إجابة</option>'
                for idx, choice in enumerate(question["choices"]):
                    options_html += f'<option value="{idx}">{choice["value"]}</option>'
                
                dropdown_html = f'''
                <select class="passage-dropdown" data-correct-index="{question["correct_choice_index"]}">
                    {options_html}
                </select>
                '''
                sentence_parts.append(dropdown_html)
            
            questions_html += f'''
            <div class="passage-question" data-question-index="{q_index}">
                <div class="passage-sentence">
                    {" ".join(sentence_parts)}
                </div>
                <div class="passage-feedback"></div>
            </div>
            '''
        
        # Generate complete passage HTML
        passage_html = f'''
        <div class="passage-item" data-passage-index="{passage_index}">
            <h3 class="passage-title">{passage["title"]}</h3>
            <div class="passage-text">{passage["text"]}</div>
            
            <div class="passage-questions">
                {questions_html}
            </div>
            
            <button class="passage-show-results">عرض النتائج</button>
            <div class="passage-overall-feedback"></div>
        </div>
        '''
        
        return passage_html
    def encode_audio_to_base64(self, audio_file_path):
        """Encode audio file to base64 for embedding in HTML."""
        try:
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                return f"data:audio/mpeg;base64,{audio_base64}"
        except FileNotFoundError:
            # Return empty if file doesn't exist
            return ""
            
    def generate_html(self):
        try:
            # Prepare animals HTML
            animals_html = ""
            animals_per_row = int(self.animals_per_row_var.get())
            
            for i, animal in enumerate(self.animals):
                if i % animals_per_row == 0:
                    if i > 0:
                        animals_html += "</div>\n"
                    animals_html += "<div class=\"animals-container\">\n"
                
                # Encode audio file to base64
                audio_data = ""
                audio_path = animal.audio.get()
                if audio_path and os.path.exists(audio_path):
                    with open(audio_path, 'rb') as audio_file:
                        audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
                
                # Get file extension for MIME type
                audio_ext = os.path.splitext(audio_path)[1].lower() if audio_path else ""
                mime_type = f"audio/{audio_ext[1:]}" if audio_ext else "audio/mpeg"
                
                animals_html += f"""
                <div class="animal-card">
                    <img src="{animal.image_url.get()}" alt="{animal.word.get()}" onclick="playAudio('audio_{i}')">
                    <div class="animal-name">{animal.title.get()}</div>
                    <button class="repeat-btn" onclick="playAudio('audio_{i}')">🔊 Repeat</button>
                    <audio id="audio_{i}">
                        <source src="data:{mime_type};base64,{audio_data}" type="{mime_type}">
                    </audio>
                </div>
                """
            
            if self.animals:
                animals_html += "</div>\n<hr>\n<hr>\n"

            # ----------------- Insert: build dialogues_html here -----------------
            dialogues_html = ""
            for d_idx, dialogue in enumerate(self.dialouges):
                title = dialogue.get("title", "")
                dialogues_html += f'<div class="dialogue" id="dialogue_{d_idx}">\n'
                if title:
                    dialogues_html += f' <div class="dialogue-head"><h3 class="dialogue-title">{title}</h3> <button class="autoplay-dialogue-button" onclick="autoplayDialogue()">▶️ Auto Play Dialogue</button></div> \n'
                else:
                    dialogues_html += f' <div class="dialogue-head"> <button onclick="autoplayDialogue()">▶️ Auto Play Dialogue</button></div>\n'
                dialogues_html += '  <div class="dialogue-container">\n'

                for l_idx, line in enumerate(dialogue.get("lines", [])):
                    img = line.get("image", "") or ""
                    pos = (line.get("position", "") or "left").lower()
                    text = line.get("text", "") or ""
                    translation = line.get("translation", "") or ""

                    # encode audio file to base64 like you did for animals
                    audio_data = ""
                    audio_path = line.get("audio", "") or ""
                    if audio_path and os.path.exists(audio_path):
                        with open(audio_path, "rb") as af:
                            audio_data = base64.b64encode(af.read()).decode("utf-8")

                    audio_ext = os.path.splitext(audio_path)[1].lower() if audio_path else ""
                    mime_type = f"audio/{audio_ext[1:]}" if audio_ext else "audio/mpeg"

                    # dialogue line HTML: clicking calls selectLine(...) and playAudio(...)
                    dialogues_html += f'''
                <div class="dialogue-line-wrapper {pos}" id="dialogue_wrap_{d_idx}_{l_idx}">
                    
                    <!-- MAIN (yellow) -->
                    <div class="dialogue-line main-line {pos}"
                        id="dialogue_line_{d_idx}_{l_idx}"
                        onclick="onDialogueClick({d_idx}, {l_idx})">

                        <div class="dialogue-thumb">
                        {"<img src=\"" + img + "\" alt=\"line image\" />" if img else ""}
                        <span class="mic-icon">🎤</span>
                        </div>

                        <div class="dialogue-body {pos}">
                        <div class="dialogue-text" id="dialogue_text_{d_idx}_{l_idx}" data-fulltext="{text}"></div>
                        </div>
                    </div>

                    <!-- TRANSLATION button -->
                    <button class="show-translation-button" id="line_translation_button_{d_idx}_{l_idx}" onclick="showTranslate({d_idx},{l_idx})">🈯 Translate</button>
                    <!-- TRANSLATION (hidden by default) -->
                    <div class="dialogue-translation" id="dialogue_translation_{d_idx}_{l_idx}">
                        {translation}
                    </div>

                    <audio id="dialogue_audio_{d_idx}_{l_idx}">
                        <source src="data:{mime_type};base64,{audio_data}" type="{mime_type}">
                    </audio>

                    </div>

            '''
                dialogues_html += "  </div>\n</div>\n<hr>\n<hr>\n"
            # ---------------------------------------------------------------------

                
            # Prepare questions HTML
            questions_html = ""
            for i, question in enumerate(self.questions):
                question_text = question.question_text.get()
                image_url = question.image_url.get()
                answers = [entry.get() for entry in question.answer_entries]
                correct_index = int(question.correct_answer_var.get()) if question.correct_answer_var.get() else 0

                # Add image if provided
                image_html = ""
                if image_url:
                    image_html = f'<img src="{image_url}" alt="Question image" style="max-width: 300px; margin-bottom: 15px; border-radius: 15px;">'
                
                answers_html = ""
                for j, answer in enumerate(answers):
                    answers_html += f'<div class="answer" onclick="checkAnswer({i+1}, {j})">{answer}</div>\n'
                
                questions_html += f"""
                <div class="question" id="q{i+1}">
                    {image_html}
                    <div class="question-text">{question_text}</div>
                    <div class="answers-container">
                        {answers_html}
                    </div>
                    <div class="feedback" id="feedback{i+1}"></div>
                </div>
                """
                
            # Prepare correct answers JavaScript
            correct_answers_js = "const correctAnswers = {\n"
            for i, question in enumerate(self.questions):
                correct_index = int(question.correct_answer_var.get()) if question.correct_answer_var.get() else 0
                correct_answers_js += f"    {i+1}: {correct_index},\n"
            correct_answers_js += "};\n"
            
            # Prepare correct answer text for audio
            correct_answer_text_js = "const correctAnswerText = {\n"
            for i, question in enumerate(self.questions):
                answers = [entry.get() for entry in question.answer_entries]
                correct_index = int(question.correct_answer_var.get()) if question.correct_answer_var.get() else 0
                if 0 <= correct_index < len(answers):
                    correct_answer_text_js += f"    {i+1}: \"{answers[correct_index]}\",\n"
            correct_answer_text_js += "};\n"
            
            successAudioEncoded=f""" 
            <audio id="successAudio" controls style="display: none;">
              <source src="data:audio/mp3;base64,{self.successAudioEncodedString}" type="audio/mp3">
              Your browser does not support the audio element.
            </audio>
            """

            # Prepare reading passages HTML
            reading_passages_html = ""
            for i, passage in enumerate(self.reading_passages):
                reading_passages_html += self.generate_reading_passage_html(passage, i)
            
            # Prepare fail audio file
            fail_audio_base64 = self.encode_audio_to_base64("failOne.mp3")

            # Prepare cheer audio file
            cheer_audio_base64 = self.encode_audio_to_base64("cheer.mp3")
            
            # Read HTML template
            html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title> امتحان تعليمي</title>
  <style>
    /* تحسينات التصميم العامة */
    body {{
      font-family: 'Arial', 'Segoe UI', sans-serif;
      text-align: center;
      background: linear-gradient(to bottom, #e0f7fa, #b2ebf2);
      margin: 0;
      padding: 20px;
      color: #01579b;
      min-height: 100vh;
    }}
    
    .container {{
      max-width: 800px;
      margin: 0 auto;
      background-color: rgba(255, 255, 255, 0.9);
      border-radius: 20px;
      padding: 20px;
      box-shadow: 0 8px 25px rgba(2, 62, 118, 0.2);
    }}
    
    h1 {{
      color: #0288d1;
      font-size: 2.5rem;
      margin-bottom: 20px;
      text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }}
    
    /* تحسين صور الحيوانات */
    .animals-container {{
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 15px;
      margin: 20px 0;
    }}
    
    .animal-card {{
      display: flex;
      flex-direction: column;
      align-items: center;
      transition: transform 0.3s;
    }}
    
    .animal-card:hover {{
      transform: translateY(-5px);
    }}
    
    .animal-card img {{
      width: 150px;
      height: 150px;
      object-fit: cover;
      border-radius: 15px;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      cursor: pointer;
      border: 3px solid #81d4fa;
      transition: all 0.3s;
    }}
    
    .animal-card img:hover {{
      border-color: #0288d1;
      box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
    }}
    
    .animal-name {{
      margin-top: 8px;
      font-weight: bold;
      color: #0277bd;
    }}

    /* Dialogues */
    .dialogue-head {{
        display:flex;
        justify-content:space-between;
        margin-bottom:3px;
    }}

    .autoplay-dialogue-button{{
        border-radius:5px;
        cursor:pointer;
    }}

    .dialogue-line-wrapper {{
    display: flex;
    gap: 3%;
    margin-bottom: 14px;
    }}

    /* left / right */
    .dialogue-line-wrapper.left  {{ flex-direction: row-reverse; }}
    .dialogue-line-wrapper.right {{ flex-direction: row; }}

    /* MAIN yellow section */
    .main-line {{
    background: #fff8e1;
    border-radius: 12px;
    padding: 10px;
    display: flex;
    align-items: center;
    gap: 12px;
    width: fit-content;            /* start as image-width */
    max-width: 47%;
    transition: width 0.4s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    }}

    .main-line.expanded {{
    width: 47%;
    }}

    /* text grows vertically after width max */
    .dialogue-body {{
    flex: 1;
    }}

    .dialogue-body.left {{
    text-align:left;
    flex: 1;
    }}

    /* image + mic */
    .dialogue-thumb {{
    position: relative;
    }}
    .dialogue-thumb img {{
    width: 80px;
    height: 80px;
    border-radius: 10px;
    }}
    .mic-icon {{
    position: absolute;
    bottom: -6px;
    right: -6px;
    background: #0288d1;
    color: white;
    border-radius: 50%;
    font-size: 14px;
    padding: 3px;
    }}

    /* translation */
    .show-translation-button{{
        height:fit-content;
        border-radius:5px;
        cursor:pointer;
    }}
    .show-translation-button.hide{{
        display:none;
    }}

    .dialogue-translation {{
    max-width: 47%;
    background: #e1f5fe;
    border-radius: 12px;
    padding: 10px;
    display: none;
    }}

    .dialogue-translation.show {{
    display: flex; 
    justify-content: center; 
    align-items: center; 
    }}

    /* active */
    .main-line.active {{
    box-shadow: 0 10px 25px rgba(2,62,118,0.15);
    }}

    .dialogue {{ margin: 20px 0; text-align: right; }}
    .dialogue-title {{ margin: 0 0 8px 0; color: #0277bd; }}
    .dialogue-container {{ display: flex; flex-direction: column; gap: 8px; }}

    .dialogue-line {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 12px;
    background: #fff8e1;
    cursor: pointer;
    transition: transform 0.18s, box-shadow 0.18s;
    border: 2px solid transparent;
    }}
    .dialogue-line:hover {{ transform: translateY(-3px); box-shadow: 0 6px 14px rgba(0,0,0,0.08); }}

    /* left / right alignment classes */
    .dialogue-line.left  {{ flex-direction: row-reverse; }} /* image on right (RTL page) */
    .dialogue-line.right {{ flex-direction: row; }}         /* image on left */

    .dialogue-thumb img {{
    width: 80px;
    height: 80px;
    object-fit: cover;
    border-radius: 10px;
    border: 3px solid #81d4fa;
    transition: transform 0.18s, border-color 0.18s;
    }}

    /* active (selected) line */
    .dialogue-line.active {{
    transform: scale(1.02);
    border-color: #0288d1;
    box-shadow: 0 10px 30px rgba(2,62,118,0.12);
    }}
    .dialogue-line.active .dialogue-thumb img {{
    transform: scale(1.06);
    border-color: #0288d1;
    }}

    .dialogue-body {{ flex: 1; }}
    .dialogue-text {{ font-size: 1rem; color: #01579b; }}
    @media (max-width: 600px) {{
    .dialogue-thumb img {{ width: 60px; height: 60px; }}
    .main-line {{max-width:90%;}}
    .main-line.expanded{{max-width:90%;}}
    .dialogue-translation {{max-width:90%;align-self:center;}}
    .dialogue-line-wrapper {{flex-direction:column;}}

    }}
    
    /* تحسين الأسئلة والخيارات */
    .questions-container {{
      margin-top: 30px;
    }}
    
    .question {{
      margin: 25px 0;
      padding: 15px;
      background-color: #e1f5fe;
      border-radius: 15px;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    
    .question-text {{
      font-size: 1.3rem;
      font-weight: bold;
      margin-bottom: 15px;
      color: #01579b;
    }}
    
    .answers-container {{
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-top: 15px;
    }}
    
    .answer {{
      padding: 12px 20px;
      background: #f5f5f5;
      cursor: pointer;
      border-radius: 10px;
      transition: all 0.3s;
      border: 2px solid transparent;
      font-size: 1.1rem;
    }}
    
    .answer:hover {{
      background: #e0f2f1;
      border-color: #4db6ac;
    }}
    
    .correct {{
      background-color: #c8e6c9;
      border-color: #2e7d32;
    }}
    
    .incorrect {{
      background-color: #ffcdd2;
      border-color: #c62828;
    }}
    
    /* تحسين الفاصل */
    hr {{
      border: none;
      height: 3px;
      background: linear-gradient(to right, transparent, #0288d1, transparent);
      margin: 30px 0;
    }}
    
    /* زر التكرار */
    .repeat-btn {{
      margin-top: 10px;
      padding: 5px 15px;
      background-color: #4db6ac;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: background-color 0.3s;
    }}
    
    .repeat-btn:hover {{
      background-color: #26a69a;
    }}
    
    /* رسائل التغذية الراجعة */
    .feedback {{
      margin-top: 10px;
      font-weight: bold;
      min-height: 24px;
    }}
    
    /* التكيف مع الشاشات الصغيرة */
    @media (max-width: 600px) {{
      .animal-card img {{
        width: 120px;
        height: 120px;
      }}
      
      .question-text {{
        font-size: 1.1rem;
      }}
      
      .answer {{
        padding: 10px 15px;
        font-size: 1rem;
      }}
    }}

    /* Reading Passages Styles */
    .passages-container {{
      margin: 30px 0;
    }}
    
    .passage-item {{
      background: #ffffff;
      border-radius: 15px;
      padding: 20px;
      margin-bottom: 30px;
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
      border: 2px solid #e3f2fd;
    }}
    
    .passage-title {{
      color: #01579b;
      font-size: 1.5rem;
      margin-bottom: 15px;
      padding-bottom: 10px;
      border-bottom: 2px solid #0288d1;
    }}
    
    .passage-text {{
      text-align: justify;
      line-height: 1.8;
      font-size: 1.1rem;
      margin-bottom: 25px;
      color: #333;
      padding: 15px;
      background: #f8fdff;
      border-radius: 10px;
      border-right: 3px solid #0288d1;
    }}
    
    .passage-question {{
      margin: 20px 0;
      padding: 15px;
      background: #f5f9ff;
      border-radius: 10px;
      border: 1px solid #e1e8f0;
    }}
    
    .passage-sentence {{
      font-size: 1.1rem;
      margin-bottom: 15px;
      line-height: 1.6;
      color: #2c3e50;
    }}
    
    .passage-dropdown {{
      padding: 8px 15px;
      border: 2px solid #bdc3c7;
      border-radius: 8px;
      font-size: 1rem;
      background: white;
      margin: 0 5px;
      cursor: pointer;
      transition: all 0.3s ease;
      min-width: 120px;
    }}
    
    .passage-dropdown:hover {{
      border-color: #3498db;
    }}
    
    .passage-dropdown.correct {{
      background-color: #d4edda;
      border-color: #28a745;
      color: #155724;
    }}
    
    .passage-dropdown.incorrect {{
      background-color: #f8d7da;
      border-color: #dc3545;
      color: #721c24;
    }}
    
    .passage-feedback {{
      margin-top: 10px;
      font-size: 0.95rem;
      font-weight: bold;
      padding: 8px 12px;
      border-radius: 6px;
      display: inline-block;
    }}
    
    .passage-feedback.correct {{
      color: #155724;
      background-color: #d4edda;
      border: 1px solid #c3e6cb;
    }}
    
    .passage-feedback.incorrect {{
      color: #721c24;
      background-color: #f8d7da;
      border: 1px solid #f5c6cb;
    }}
    
    .passage-show-results {{
      background: linear-gradient(to right, #3498db, #2980b9);
      color: white;
      border: none;
      padding: 12px 30px;
      font-size: 1.1rem;
      border-radius: 25px;
      cursor: pointer;
      margin: 20px 0;
      transition: all 0.3s ease;
      box-shadow: 0 4px 10px rgba(52, 152, 219, 0.3);
    }}
    
    .passage-show-results:hover:not(:disabled) {{
      background: linear-gradient(to right, #2980b9, #1c6ea4);
      transform: translateY(-2px);
      box-shadow: 0 6px 15px rgba(52, 152, 219, 0.4);
    }}
    
    .passage-show-results:disabled {{
      background: #95a5a6;
      cursor: not-allowed;
      transform: none;
      box-shadow: none;
    }}
    
    .passage-overall-feedback {{
      margin-top: 20px;
      padding: 15px;
      border-radius: 10px;
      font-size: 1.2rem;
      font-weight: bold;
      display: none;
    }}
    
    .passage-overall-feedback.success {{
      background-color: #d4edda;
      color: #155724;
      border: 2px solid #28a745;
      display: block;
    }}
    
    .passage-overall-feedback.fail {{
      background-color: #f8d7da;
      color: #721c24;
      border: 2px solid #dc3545;
      display: block;
    }}
    
    .correct-symbol {{
      color: #28a745;
      margin-right: 5px;
    }}
    
    .incorrect-symbol {{
      color: #dc3545;
      margin-right: 5px;
    }}
     /* Feelings Feedback Section - Fixed Version */
    .feelings-section {{
    margin: 40px 0 30px 0;
    padding: 25px;
    background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
    border-radius: 15px;
    border: 2px solid #bbdefb;
    }}

    .feelings-title {{
    color: #0288d1;
    font-size: 1.5rem;
    margin-bottom: 20px;
    font-weight: bold;
    }}

    .feelings-container {{
    display: flex;
    justify-content: center;
    gap: 25px;
    flex-wrap: wrap;
    }}

    .feeling-item {{
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    padding: 10px;
    border-radius: 10px;
    }}

    /* Default emoji state - faded and small */
    .feeling-emoji {{
    font-size: 3rem;
    margin-bottom: 8px;
    opacity: 0.6;
    filter: grayscale(0.2);
    transition: all 0.3s ease;
    transform: scale(1);
    }}

    /* Hover effect */
    .feeling-item:hover .feeling-emoji {{
    opacity: 1;
    filter: grayscale(0);
    transform: scale(1.3);
    }}

    .feeling-item:hover {{
    background-color: rgba(255, 255, 255, 0.6);
    }}

    /* ACTIVE STATE - This overrides hover when clicked */
    .feeling-item.active .feeling-emoji {{
    opacity: 1;
    filter: grayscale(0);
    transform: scale(1.4);
    }}

    .feeling-item.active {{
    background-color: rgba(255, 255, 255, 0.8);
    box-shadow: 0 4px 12px rgba(2, 136, 209, 0.2);
    border: 2px solid #0288d1;
    }}

    /* Important: This prevents hover from overriding active state */
    .feeling-item.active:hover .feeling-emoji {{
    transform: scale(1.4); /* Same as active, no hover effect */
    }}

    .feeling-label {{
    font-size: 1rem;
    color: #01579b;
    font-weight: 500;
    transition: all 0.3s ease;
    }}

    .feeling-item:hover .feeling-label {{
    color: #0288d1;
    font-weight: bold;
    }}

    /* Active label style */
    .feeling-item.active .feeling-label,
    .feeling-item.active:hover .feeling-label {{
    color: #0288d1;
    font-weight: bold;
    }}
    
    /* Contact Section */
    .contact-section {{
      margin: 30px 0;
      padding: 20px;
      background: linear-gradient(to right, #0288d1, #03a9f4);
      border-radius: 15px;
      color: white;
      box-shadow: 0 4px 15px rgba(2, 136, 209, 0.3);
    }}
    
    .contact-text {{
      font-size: 1.2rem;
      margin-bottom: 5px;
      font-weight: bold;
    }}
    
    .contact-email {{
      font-size: 1.3rem;
      font-weight: bold;
      color: #ffeb3b;
      text-decoration: none;
      transition: all 0.3s ease;
      padding: 5px 15px;
      border-radius: 5px;
      display: inline-block;
    }}
    
    .contact-email:hover {{
      background-color: rgba(255, 255, 255, 0.2);
      transform: translateY(-2px);
    }}
    
    /* Copyright Section */
    .copyright-section {{
      margin-top: 20px;
      padding: 15px;
      background-color: rgba(255, 255, 255, 0.7);
      border-radius: 10px;
      border-top: 3px solid #0288d1;
    }}
    
    .copyright-text {{
      color: #666;
      font-size: 0.9rem;
      margin: 0;
    }}
    
    .copyright-name {{
      color: #0288d1;
      font-weight: bold;
    }}
    
    /* Footer fixed sections */
    .footer-sections {{
      position: relative;
      margin-top: 40px;
    }}
    
    /* Responsive adjustments */
    @media (max-width: 768px) {{
      .feelings-container {{
        gap: 15px;
      }}
      
      .feeling-emoji {{
        font-size: 2.5rem;
      }}
      
      .feeling-label {{
        font-size: 0.9rem;
      }}
      
      .contact-text {{
        font-size: 1rem;
      }}
      
      .contact-email {{
        font-size: 1.1rem;
      }}
    }}
    
    @media (max-width: 480px) {{
      .feelings-container {{
        gap: 10px;
      }}
      
      .feeling-emoji {{
        font-size: 2rem;
      }}
      
      .feeling-item {{
        padding: 5px;
      }}
  </style>
</head>
<body>
  <audio id="cheerAudio" preload="auto">
    <source src="{cheer_audio_base64}" type="audio/mpeg">
  </audio>
  <audio id="failAudio" preload="auto">
    <source src="{fail_audio_base64}" type="audio/mpeg">
  </audio>
  {successAudioEncoded}
  <div class="container">
    <h1>Learning Test</h1>

    <!-- صور الحيوانات -->
    {animals_html}

    <!-- <-- المحادثات -->
    {dialogues_html}

    <!-- Reading Passages -->
    <div class="passages-container">
      {reading_passages_html}
    </div>

    <hr>
    <hr>

    <!-- الأسئلة -->
    <div class="questions-container">
      {questions_html}
    </div>

    <!-- Feelings Feedback Section -->
    <div class="feelings-section">
    <h3 class="feelings-title">How do you feel?</h3>
    <div class="feelings-container">
        <div class="feeling-item" data-feeling="frustrated">
        <span class="feeling-emoji">😫</span>
        <span class="feeling-label">Frustrated</span>
        </div>
        <div class="feeling-item" data-feeling="neutral">
        <span class="feeling-emoji">😐</span>
        <span class="feeling-label">Neutral</span>
        </div>
        <div class="feeling-item" data-feeling="happy">
        <span class="feeling-emoji">😊</span>
        <span class="feeling-label">Happy</span>
        </div>
        <div class="feeling-item" data-feeling="excited">
        <span class="feeling-emoji">🤩</span>
        <span class="feeling-label">Excited</span>
        </div>
        <div class="feeling-item" data-feeling="proud">
        <span class="feeling-emoji">😎</span>
        <span class="feeling-label"> Proud </span>
        </div>
    </div>
    </div>

    <!-- Contact Section -->
    <div class="contact-section">
      <p class="contact-text">For contact or more information:</p>
      <a href="mailto:a.hossam.contact@gmail.com" class="contact-email">
        a.hossam.contact@gmail.com
      </a>
    </div>

    <!-- Copyright Section -->
    <div class="copyright-section">
      <p class="copyright-text">
       This educational application was developed by <span class="copyright-name"> Ahmad Hossam</span><br>
All rights reserved © 2026 – Educational Design and Development 
      
      </p>
    </div>
  </div>

  <script>
    // الإجابات الصحيحة
    {correct_answers_js}
    
    // نصوص الإجابات الصحيحة للتشغيل
    {correct_answer_text_js}
    
    // تشغيل الصوت
    let currentAudio = null; // keep track of the currently playing audio
    function playAudio(audioId) {{ // Stop the currently playing audio if there is one 
        if (currentAudio && !currentAudio.paused) {{
            currentAudio.pause(); 
            currentAudio.currentTime = 0; 
            }}
        // Get the new audio element 
        const audio = document.getElementById(audioId); 
        if (audio) {{
            currentAudio = audio; // update the reference 
            audio.currentTime = 0; 
            audio.play(); 
            }} 
    }}

    // mark a dialogue line as active (visual) and remove the previous active
    function selectLine(lineId) {{
    // remove active from previous
    const prev = document.querySelector('.dialogue-line.active');
    if (prev && prev.id !== lineId) prev.classList.remove('active');

    // toggle or set active on clicked
    const el = document.getElementById(lineId);
    if (el) {{
        el.classList.add('active');
        // keep it active briefly while audio plays (optional behaviour)
        // you may remove the timeout if you prefer to keep it active until next click
        setTimeout(() => {{
        // if audio finished, we could remove active — but rely on next click for clarity
        // el.classList.remove('active');
        }}, 3000);
    }}
    }}

    function typeText(element, text, duration) {{
        element.textContent = "";
        let i = 0;
        const interval = duration / text.length;

        const typer = setInterval(() => {{
            element.textContent += text[i];
            i++;
            if (i >= text.length) clearInterval(typer);
        }}, interval);
    }}

    const playedLines = new Set();

    function onDialogueClick(d, l) {{
        const key = `${{d}}_${{l}}`;
        const line = document.getElementById(`dialogue_line_${{d}}_${{l}}`);
        const textBox = document.getElementById(`dialogue_text_${{d}}_${{l}}`);
        const audioId = `dialogue_audio_${{d}}_${{l}}`;

        // Always play audio
        playAudio(audioId);

        // Only animate first time
        if (playedLines.has(key)) return;

        playedLines.add(key);
        line.classList.add("active", "expanded");

        const fullText = textBox.dataset.fulltext;
        const audio = document.getElementById(audioId);

        audio.onplay = () => {{
            typeText(textBox, fullText, audio.duration * 300);
        }};
        }}

        async function autoplayDialogue() {{
            const lines = document.querySelectorAll(".dialogue-line-wrapper");
            for (const wrapper of lines) {{
                const main = wrapper.querySelector(".main-line");
                const id = main.id.split("dialogue_line_")[1];
                const [d, l] = id.split("_");

                onDialogueClick(d, l);

                const audio = document.getElementById(`dialogue_audio_${{d}}_${{l}}`);
                await new Promise(res => {{
                audio.onended = res;
                }});
            }}
            }}

        async function showTranslate(d, l) {{
            const translation_line = document.getElementById(`dialogue_translation_${{d}}_${{l}}`);
            translation_line.classList.add("show");
            const translation_line_button = document.getElementById(`line_translation_button_${{d}}_${{l}}`);
            translation_line_button.classList.add("hide");
            
            }}   


    
    // التحقق من الإجابات
    function checkAnswer(questionId, answerIndex) {{
      const question = document.getElementById(`q${{questionId}}`);
      const answers = question.getElementsByClassName('answer');
      const feedback = document.getElementById(`feedback${{questionId}}`);
      
      // إزالة الأنماط السابقة
      for (let answer of answers) {{
        answer.classList.remove('correct', 'incorrect');
      }}
      
      // التحقق من الإجابة
      if (answerIndex === correctAnswers[questionId]) {{
        answers[answerIndex].classList.add('correct');
        feedback.textContent = 'Correct! Well done! 🎉';
        feedback.style.color = '#2e7d32';
        playCorrectAnswer(questionId);
      }} else {{
        answers[answerIndex].classList.add('incorrect');
        answers[correctAnswers[questionId]].classList.add('correct');
        feedback.textContent = 'Try again!';
        feedback.style.color = '#c62828';
      }}
    }}

    function hasEnglishCharacter(text) {{
      return /[a-zA-Z]/.test(text);
    }}
    
    // تشغيل الإجابة الصحيحة
    function playCorrectAnswer(questionId) {{
      // إنشاء عنصر صوت مؤقت للإجابة الصحيحة
      const text = correctAnswerText[questionId];
      if (text) {{
        if (hasEnglishCharacter(text)) {{
          const utterance = new SpeechSynthesisUtterance(text);
          utterance.lang = "en-US";
          utterance.rate = 0.9;
          speechSynthesis.speak(utterance);
        }}else{{
          const successAudio = document.getElementById('successAudio');
          successAudio.currentTime = 0;
          successAudio.play();
        }}
      }}
    }}

    // Reading Passages Functions
    function createPassagesHandlers() {{
        const passages = document.querySelectorAll('.passage-item');
        
        passages.forEach((passage, passageIndex) => {{
            const showResultsBtn = passage.querySelector('.passage-show-results');
            const overallFeedback = passage.querySelector('.passage-overall-feedback');
            const dropdowns = passage.querySelectorAll('.passage-dropdown');
            
            // Store original state
            dropdowns.forEach(dropdown => {{
                dropdown.dataset.originalValue = dropdown.value;
            }});
            
            // Check results function
            function checkPassageResults() {{
                let allCorrect = true;
                const questions = passage.querySelectorAll('.passage-question');
                
                questions.forEach((question, qIndex) => {{
                    const dropdown = question.querySelector('.passage-dropdown');
                    const feedback = question.querySelector('.passage-feedback');
                    const correctIndex = parseInt(dropdown.dataset.correctIndex);
                    const selectedValue = parseInt(dropdown.value);
                    
                    // Reset styles
                    dropdown.classList.remove('correct', 'incorrect');
                    feedback.classList.remove('correct', 'incorrect');
                    feedback.textContent = '';
                    
                    if (selectedValue === correctIndex) {{
                        dropdown.classList.add('correct');
                        feedback.classList.add('correct');
                        feedback.innerHTML = '<span class="correct-symbol">✅</span> الإجابة صحيحة';
                    }} else {{
                        dropdown.classList.add('incorrect');
                        feedback.classList.add('incorrect');
                        feedback.innerHTML = '<span class="incorrect-symbol">❌</span> الإجابة خاطئة';
                        allCorrect = false;
                    }}
                }});
                
                // Show overall feedback
                overallFeedback.classList.remove('success', 'fail');
                if (allCorrect) {{
                    overallFeedback.classList.add('success');
                    overallFeedback.innerHTML = 'جميع الإجابات صحيحة 🎉';
                    playAudio('cheerAudio');
                }} else {{
                    overallFeedback.classList.add('fail');
                    overallFeedback.innerHTML = 'يوجد إجابات خاطئة ⛔';
                    playAudio('failAudio');
                }}
                
                // Disable the button
                showResultsBtn.disabled = true;
            }}
            
            // Reset overall feedback when any dropdown changes
            dropdowns.forEach(dropdown => {{
                dropdown.addEventListener('change', function() {{
                    // Reset overall feedback
                    overallFeedback.classList.remove('success', 'fail');
                    overallFeedback.textContent = '';
                    
                    // Re-enable the button
                    showResultsBtn.disabled = false;
                    
                    // Auto-check the changed question
                    const question = this.closest('.passage-question');
                    const feedback = question.querySelector('.passage-feedback');
                    const correctIndex = parseInt(this.dataset.correctIndex);
                    const selectedValue = parseInt(this.value);
                    
                    // Reset styles
                    this.classList.remove('correct', 'incorrect');
                    feedback.classList.remove('correct', 'incorrect');
                    feedback.textContent = '';
                    
                    
                }});
            }});
            
            // Attach event listener to show results button
            showResultsBtn.addEventListener('click', checkPassageResults);
        }});
    }}
    
    // Initialize when page loads
    document.addEventListener('DOMContentLoaded', createPassagesHandlers);

    // Feelings Section Functionality
    const feelingItems = document.querySelectorAll('.feeling-item');

    feelingItems.forEach(item => {{
        item.addEventListener('click', function() {{
            // Remove active class from all items
            feelingItems.forEach(i => {{
                i.classList.remove('active');
            }});
            
            // Add active class to clicked item
            this.classList.add('active');
            const selectedFeeling = this.dataset.feeling;
            
            // Optional: You can save this selection somewhere
            console.log('Selected feeling:', selectedFeeling);
        }});
    }});

  </script>
</body>
</html>
"""
            
            # Format the HTML
            html_content = html_template.format(
                fail_audio_base64=fail_audio_base64,
                cheer_audio_base64=cheer_audio_base64,
                successAudioEncoded=successAudioEncoded,
                animals_html=animals_html,
                dialogues_html=dialogues_html,
                reading_passages_html=reading_passages_html,
                questions_html=questions_html,
                correct_answers_js=correct_answers_js,
                correct_answer_text_js=correct_answer_text_js
            )
            
            # Save HTML file
            output_file = self.output_file_var.get()
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            messagebox.showinfo("Success", f"HTML file generated successfully!\nSaved as: {output_file}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate HTML: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimalLearningGameGenerator(root)
    root.mainloop()

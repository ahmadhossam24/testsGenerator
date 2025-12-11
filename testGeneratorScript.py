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
        
        # Remove button
        ttk.Button(frame, text="Remove", command=lambda: self.remove_animal_frame(frame)).grid(row=4, column=1, sticky='e', pady=5)
        
        # Store references
        frame.image_url = image_url_entry
        frame.title = title_entry
        frame.word = word_entry
        frame.audio = audio_entry
        
        self.animals.append(frame)
        
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
        
    def setup_settings_section(self):
        # Output file settings
        ttk.Label(self.settings_frame, text="Output File:").grid(row=0, column=0, sticky='w', pady=5)
        self.output_file_var = tk.StringVar(value="animal_game.html")
        output_entry = ttk.Entry(self.settings_frame, textvariable=self.output_file_var, width=40)
        output_entry.grid(row=0, column=1, pady=5, padx=5, sticky='we')
        ttk.Button(self.settings_frame, text="Browse", command=self.browse_output).grid(row=0, column=2, pady=5, padx=5)
        
        # Configure grid weights
        self.settings_frame.columnconfigure(1, weight=1)
        
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
        
        # Reset settings
        self.animals_per_row_var.set("3")
        self.output_file_var.set("animal_game.html")
        
        # Add default frames
        self.add_animal_frame()
        self.add_question_frame()
        
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
                
                # Clear default answers
                for entry in question_frame.answer_entries[:]:
                    question_frame.remove_answer_row(
                        question_frame.radio_buttons[question_frame.answer_entries.index(entry)],
                        entry,
                        None  # Button reference not stored, but it's OK for initial load
                    )
                
                # Add answers from config
                answers = question_data.get('answers', [])
                correct_index = question_data.get('correct_index', 0)
                
                for i, answer in enumerate(answers):
                    question_frame.add_answer_row()
                    question_frame.answer_entries[-1].insert(0, answer)
                    
                # Set correct answer
                if answers and 0 <= correct_index < len(answers):
                    question_frame.correct_answer_var.set(str(correct_index))
                    
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
                    'text': question.question_text.get(),
                    'answers': answers,
                    'correct_index': correct_index
                })
                
            # Prepare config
            config = {
                'animals': animals_data,
                'questions': questions_data,
                'animals_per_row': int(self.animals_per_row_var.get()),
                'output_file': self.output_file_var.get()
            }
            
            # Save to file
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
                
            messagebox.showinfo("Success", "Configuration saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration: {str(e)}")
            
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
                animals_html += "</div>\n"
                
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
  </style>
</head>
<body>
  {successAudioEncoded}
  <div class="container">
    <h1>Learning Test</h1>

    <!-- صور الحيوانات -->
    {animals_html}

    <hr>

    <!-- الأسئلة -->
    <div class="questions-container">
      {questions_html}
    </div>
  </div>

  <script>
    // الإجابات الصحيحة
    {correct_answers_js}
    
    // نصوص الإجابات الصحيحة للتشغيل
    {correct_answer_text_js}
    
    // تشغيل الصوت
    function playAudio(audioId) {{
      const audio = document.getElementById(audioId);
      if (audio) {{
        audio.currentTime = 0;
        audio.play();
      }}
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
  </script>
</body>
</html>
"""
            
            # Format the HTML
            html_content = html_template.format(
                successAudioEncoded=successAudioEncoded,
                animals_html=animals_html,
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
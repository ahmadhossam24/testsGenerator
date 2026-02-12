import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PySide6.QtWidgets import  (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTabWidget, QFrame, QMenuBar, QMenu, QLabel, QSpinBox, 
    QPushButton, QScrollArea, QSizePolicy, QGridLayout,QLineEdit, QFileDialog, QGroupBox,QRadioButton,
    QButtonGroup, QTextEdit, QCheckBox,QComboBox,QMessageBox
) 
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtCore import Qt,QSize,Signal
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

class AnimalLearningGameGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("Learning Game Generator")
        self.setGeometry(100, 100, 900, 700)  # x, y, width, height
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Equivalent to padx/pady
        
        # Data storage
        self.animals = []
        self.questions = []
        self.dialouges = []
        self.reading_passages = []
        
        # Create notebook/tab widget for sections
        self.notebook = QTabWidget()
        self.notebook.setDocumentMode(True)  # Cleaner tab style
        
        # Create frames for each tab
        self.animals_frame = QFrame()
        self.animals_frame.setFrameStyle(QFrame.StyledPanel)
        self.notebook.addTab(self.animals_frame, "Cards")
        
        self.questions_frame = QFrame()
        self.questions_frame.setFrameStyle(QFrame.StyledPanel)
        self.notebook.addTab(self.questions_frame, "Questions")
        
        self.dialogues_frame = QFrame()
        self.dialogues_frame.setFrameStyle(QFrame.StyledPanel)
        self.notebook.addTab(self.dialogues_frame, "Dialogues")
        
        self.reading_passages_frame = QFrame()
        self.reading_passages_frame.setFrameStyle(QFrame.StyledPanel)
        self.notebook.addTab(self.reading_passages_frame, "Reading passages")
        
        self.settings_frame = QFrame()
        self.settings_frame.setFrameStyle(QFrame.StyledPanel)
        self.notebook.addTab(self.settings_frame, "Settings")
        
        # Add notebook to main layout
        main_layout.addWidget(self.notebook)
        
        # Create layouts for each tab's frame
        self.animals_layout = QVBoxLayout(self.animals_frame)
        self.questions_layout = QVBoxLayout(self.questions_frame)
        self.dialogues_layout = QVBoxLayout(self.dialogues_frame)
        self.reading_passages_layout = QVBoxLayout(self.reading_passages_frame)
        # self.settings_layout = QVBoxLayout(self.settings_frame)
        
        # Set margins for each frame's layout (padding)
        padding = 10
        self.animals_layout.setContentsMargins(padding, padding, padding, padding)
        self.questions_layout.setContentsMargins(padding, padding, padding, padding)
        self.dialogues_layout.setContentsMargins(padding, padding, padding, padding)
        self.reading_passages_layout.setContentsMargins(padding, padding, padding, padding)
        # self.settings_layout.setContentsMargins(padding, padding, padding, padding)
        
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
        self.setup_dialogues_section()
        self.setup_reading_passages_section()
        self.setup_settings_section()
        self.setup_menu()

    def setup_menu(self):
        # Create menu bar (automatically added to QMainWindow)
        menubar = self.menuBar()
        
        # Create File menu
        file_menu = menubar.addMenu("&File")
        
        # Add New action
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_config)
        file_menu.addAction(new_action)
        
        # Add Load action
        load_action = QAction("&Load", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.triggered.connect(self.load_config)
        file_menu.addAction(load_action)
        
        # Add Save action
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_config)
        file_menu.addAction(save_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Generate HTML action
        generate_action = QAction("&Generate HTML", self)
        # You can add a shortcut if needed
        # generate_action.setShortcut("Ctrl+G")
        generate_action.triggered.connect(self.generate_html)
        file_menu.addAction(generate_action)
        
        # Add separator
        file_menu.addSeparator()
        
        # Add Exit action
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)  
        file_menu.addAction(exit_action)
        
    def setup_animals_section(self):
            # Create horizontal layout for the first row of controls
            controls_layout = QHBoxLayout()
            
            # Animals per row setting
            animals_label = QLabel("Cards per row:")
            self.animals_per_row_spinbox = QSpinBox()
            self.animals_per_row_spinbox.setRange(1, 6)
            self.animals_per_row_spinbox.setValue(3)
            self.animals_per_row_spinbox.setFixedWidth(75)
            
            # Add animal button
            add_animal_button = QPushButton("Add Card")
            add_animal_button.clicked.connect(self.add_animal_frame)
            
            # Add widgets to controls layout
            controls_layout.addWidget(animals_label)
            controls_layout.addWidget(self.animals_per_row_spinbox)
            controls_layout.addWidget(add_animal_button)
            controls_layout.addStretch()  # Push items to the left
            
            # Add spacing/margins
            controls_layout.setSpacing(10)
            
            # Add controls layout to animals layout
            self.animals_layout.addLayout(controls_layout)
            
            # Create scroll area for animal frames
            self.scroll_area = QScrollArea()
            self.scroll_area.setWidgetResizable(True)
            self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            
            # Create container widget for the scroll area
            self.scroll_container = QWidget()
            self.animals_container_layout = QVBoxLayout(self.scroll_container)
            self.animals_container_layout.setSpacing(10)
            self.animals_container_layout.setContentsMargins(5, 5, 5, 5)
            
            # Add a stretch at the end to push frames to the top
            self.animals_container_layout.addStretch()
            
            # Set the container as the scroll area's widget
            self.scroll_area.setWidget(self.scroll_container)
            
            # Add scroll area to animals layout
            self.animals_layout.addWidget(self.scroll_area)
            
            # Add initial animal frame (you'll implement this later)
            self.add_animal_frame()   

    def add_animal_frame(self):
            # Create a group box with frame styling
            frame = QGroupBox()
            frame.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #999;
                    border-radius: 4px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
            # Create a grid layout for the frame
            frame_layout = QGridLayout(frame)
            frame_layout.setSpacing(5)
            frame_layout.setContentsMargins(10, 10, 10, 10)
            
            # Image URL
            image_label = QLabel("Image URL:")
            image_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.image_url_entry = QLineEdit()
            self.image_url_entry.setFixedWidth(300)
            
            frame_layout.addWidget(image_label, 0, 0)
            frame_layout.addWidget(self.image_url_entry, 0, 1)
            
            # Title
            title_label = QLabel("Title (e.g., 'Cat (قطة)'):")
            title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.title_entry = QLineEdit()
            self.title_entry.setFixedWidth(300)
            
            frame_layout.addWidget(title_label, 1, 0)
            frame_layout.addWidget(self.title_entry, 1, 1)
            
            # Word to speak
            word_label = QLabel("Word to speak (Arabic):")
            word_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.word_entry = QLineEdit()
            self.word_entry.setFixedWidth(300)
            
            frame_layout.addWidget(word_label, 2, 0)
            frame_layout.addWidget(self.word_entry, 2, 1)
            
            # Audio file
            audio_label = QLabel("Audio file:")
            audio_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
            # Create audio frame with horizontal layout
            audio_widget = QWidget()
            audio_layout = QHBoxLayout(audio_widget)
            audio_layout.setContentsMargins(0, 0, 0, 0)
            
            self.audio_entry = QLineEdit()
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(lambda: self.browse_audio(self.audio_entry))
            
            audio_layout.addWidget(self.audio_entry)
            audio_layout.addWidget(browse_button)
            
            frame_layout.addWidget(audio_label, 3, 0)
            frame_layout.addWidget(audio_widget, 3, 1)
            
            # Button row
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            
            # Duplicate button
            duplicate_button = QPushButton("Duplicate")
            duplicate_button.clicked.connect(lambda: self.duplicate_animal_frame(frame))
            
            # Remove button
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda: self.remove_animal_frame(frame))
            
            button_layout.addWidget(duplicate_button)
            button_layout.addStretch()
            button_layout.addWidget(remove_button)
            
            frame_layout.addWidget(button_widget, 4, 0, 1, 2)
            
            # Store references as properties
            frame.image_url = self.image_url_entry
            frame.title = self.title_entry
            frame.word = self.word_entry
            frame.audio = self.audio_entry
            
            # Add the frame to the container
            # Insert before the stretch (second to last position)
            count = self.animals_container_layout.count()
            self.animals_container_layout.insertWidget(count - 1, frame)
            
            # Store in list
            self.animals.append(frame)
            
            return frame
    
    def browse_audio(self, audio_entry):
        """Browse for audio file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg);;All Files (*.*)"
        )
        if file_name:
            audio_entry.setText(file_name)
            
    def duplicate_animal_frame(self, source_frame):
        # 1. Get values from source frame
        image_url = source_frame.image_url.text()
        title = source_frame.title.text()
        word = source_frame.word.text()
        audio = source_frame.audio.text()
        
        # 2. Create new frame
        new_frame = QGroupBox()
        new_frame.setStyleSheet("""
            QGroupBox {
                border: 1px solid #999;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create layout for the new frame
        frame_layout = QGridLayout(new_frame)
        frame_layout.setSpacing(5)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        # Image URL
        image_label = QLabel("Image URL:")
        image_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        image_url_entry = QLineEdit()
        image_url_entry.setFixedWidth(300)
        image_url_entry.setText(image_url)  # Set value immediately
        
        frame_layout.addWidget(image_label, 0, 0)
        frame_layout.addWidget(image_url_entry, 0, 1)
        
        # Title
        title_label = QLabel("Title (e.g., 'Cat (قطة)'):")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_entry = QLineEdit()
        title_entry.setFixedWidth(300)
        title_entry.setText(title)  # Set value immediately
        
        frame_layout.addWidget(title_label, 1, 0)
        frame_layout.addWidget(title_entry, 1, 1)
        
        # Word to speak
        word_label = QLabel("Word to speak (Arabic):")
        word_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        word_entry = QLineEdit()
        word_entry.setFixedWidth(300)
        word_entry.setText(word)  # Set value immediately
        
        frame_layout.addWidget(word_label, 2, 0)
        frame_layout.addWidget(word_entry, 2, 1)
        
        # Audio file
        audio_label = QLabel("Audio file:")
        audio_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        # Create audio widget with horizontal layout
        audio_widget = QWidget()
        audio_layout = QHBoxLayout(audio_widget)
        audio_layout.setContentsMargins(0, 0, 0, 0)
        
        audio_entry = QLineEdit()
        audio_entry.setText(audio)  # Set value immediately
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(lambda: self.browse_audio(audio_entry))
        
        audio_layout.addWidget(audio_entry)
        audio_layout.addWidget(browse_button)
        
        frame_layout.addWidget(audio_label, 3, 0)
        frame_layout.addWidget(audio_widget, 3, 1)
        
        # Button row
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Duplicate button
        duplicate_button = QPushButton("Duplicate")
        duplicate_button.clicked.connect(lambda: self.duplicate_animal_frame(new_frame))
        
        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(lambda: self.remove_animal_frame(new_frame))
        
        button_layout.addWidget(duplicate_button)
        button_layout.addStretch()
        button_layout.addWidget(remove_button)
        
        frame_layout.addWidget(button_widget, 4, 0, 1, 2)
        
        # Store references as properties on the frame
        new_frame.image_url = image_url_entry
        new_frame.title = title_entry
        new_frame.word = word_entry
        new_frame.audio = audio_entry
        
        # 3. Add the new frame to the container (before the stretch)
        count = self.animals_container_layout.count()
        self.animals_container_layout.insertWidget(count - 1, new_frame)
        
        # 4. Add to tracking list
        self.animals.append(new_frame)
        
        return new_frame

    def remove_animal_frame(self, frame):
        """Remove an animal frame"""
        if frame in self.animals:
            # Remove from layout
            self.animals_container_layout.removeWidget(frame)
            # Remove from list
            self.animals.remove(frame)
            # Delete the widget
            frame.deleteLater()

    def setup_questions_section(self):
        # Add question button
        add_question_button = QPushButton("Add Question")
        add_question_button.clicked.connect(self.add_question_frame)
        self.questions_layout.addWidget(add_question_button)
        
        # Create scroll area for questions
        self.questions_scroll_area = QScrollArea()
        self.questions_scroll_area.setWidgetResizable(True)
        self.questions_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for the scroll area
        self.questions_scroll_container = QWidget()
        self.questions_container_layout = QVBoxLayout(self.questions_scroll_container)
        self.questions_container_layout.setSpacing(10)
        self.questions_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add a stretch at the end to push frames to the top
        self.questions_container_layout.addStretch()
        
        # Set the container as the scroll area's widget
        self.questions_scroll_area.setWidget(self.questions_scroll_container)
        
        # Add scroll area to questions layout
        self.questions_layout.addWidget(self.questions_scroll_area)
        
        # Add initial question frame
        self.add_question_frame()
    
    def add_question_frame(self):
        # Create a group box with frame styling
        frame = QGroupBox()
        frame.setStyleSheet("""
            QGroupBox {
                border: 1px solid #999;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create a grid layout for the frame
        frame_layout = QGridLayout(frame)
        frame_layout.setSpacing(5)
        frame_layout.setContentsMargins(10, 10, 10, 10)
        
        # Question image URL (row 0)
        image_label = QLabel("Question Image URL (optional):")
        image_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        image_url_entry = QLineEdit()
        
        frame_layout.addWidget(image_label, 0, 0)
        frame_layout.addWidget(image_url_entry, 0, 1, 1, 2)
        
        # Question text (row 1)
        question_label = QLabel("Question Text:")
        question_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        question_text_entry = QLineEdit()
        
        frame_layout.addWidget(question_label, 1, 0)
        frame_layout.addWidget(question_text_entry, 1, 1, 1, 2)
        
        # Answers section (row 2)
        answers_label = QLabel("Answers:")
        answers_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Create a widget for answers with vertical layout
        answers_widget = QWidget()
        answers_widget.setStyleSheet("border: 1px solid #ccc; border-radius: 3px; padding: 5px;")
        self.answers_layout = QVBoxLayout(answers_widget)
        self.answers_layout.setSpacing(5)
        
        # Create button group for radio buttons
        button_group = QButtonGroup(frame)
        button_group.setExclusive(True)
        
        # Store answer entries and radio buttons
        answer_entries = []
        radio_buttons = []
        
        # Function to add answer row
        def add_answer_row(answer_text=""):
            # Create widget for this answer row
            answer_row = QWidget()
            row_layout = QHBoxLayout(answer_row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            
            # Radio button for correct answer
            radio_button = QRadioButton()
            radio_button.setFixedWidth(20)
            button_group.addButton(radio_button)
            
            # Answer entry
            entry = QLineEdit()
            entry.setPlaceholderText("Enter answer text...")
            if answer_text:
                entry.setText(answer_text)
            
            # Remove button
            remove_button = QPushButton("Remove")
            remove_button.setFixedWidth(80)
            
            # Connect remove button
            remove_button.clicked.connect(lambda: remove_answer_row(answer_row, radio_button, entry))
            
            # Add widgets to row layout
            row_layout.addWidget(radio_button)
            row_layout.addWidget(entry)
            row_layout.addWidget(remove_button)
            row_layout.setStretch(1, 1)  # Make entry expand
            
            # Add to answers layout
            self.answers_layout.addWidget(answer_row)
            
            # Store references
            answer_entries.append(entry)
            radio_buttons.append(radio_button)
            
            return answer_row
        
        # Function to remove answer row
        def remove_answer_row(row_widget, radio_button, entry):
            # Remove from layout
            self.answers_layout.removeWidget(row_widget)
            
            # Remove from lists
            if entry in answer_entries:
                answer_entries.remove(entry)
            if radio_button in radio_buttons:
                radio_buttons.remove(radio_button)
                button_group.removeButton(radio_button)
            
            # Delete widgets
            row_widget.deleteLater()
            
            # Update radio button indices if needed
            # (Not needed in PySide6 as we use QButtonGroup)
        
        # Add answer button
        add_answer_button = QPushButton("Add Answer")
        add_answer_button.clicked.connect(lambda: add_answer_row())
        self.answers_layout.addWidget(add_answer_button)
        
        # Add initial answers
        for _ in range(2):
            add_answer_row()
        
        # Add answers section to main frame layout
        frame_layout.addWidget(answers_label, 2, 0, Qt.AlignTop)
        frame_layout.addWidget(answers_widget, 2, 1, 1, 2)
        
        # Button row (row 3)
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Remove question button
        remove_question_button = QPushButton("Remove Question")
        remove_question_button.clicked.connect(lambda: self.remove_question_frame(frame))
        
        # Another add answer button for convenience
        add_answer_button2 = QPushButton("Add Answer")
        add_answer_button2.clicked.connect(lambda: add_answer_row())
        
        button_layout.addWidget(remove_question_button)
        button_layout.addStretch()
        button_layout.addWidget(add_answer_button2)
        
        frame_layout.addWidget(button_widget, 3, 0, 1, 3)
        
        # Set column stretch
        frame_layout.setColumnStretch(1, 1)
        
        # Store references as properties on the frame
        frame.image_url = image_url_entry
        frame.question_text = question_text_entry
        frame.answer_entries = answer_entries
        frame.radio_buttons = radio_buttons
        frame.button_group = button_group
        frame.answers_widget = answers_widget
        frame.answers_layout = self.answers_layout
        frame.add_answer_row = lambda text="": add_answer_row(text)
        frame.remove_answer_row = lambda row, radio, entry: remove_answer_row(row, radio, entry)
        
        # Add the frame to the container
        count = self.questions_container_layout.count()
        self.questions_container_layout.insertWidget(count - 1, frame)
        
        # Store in list
        self.questions.append(frame)
        
        return frame
    
    def remove_question_frame(self, frame):
        """Remove a question frame"""
        if frame in self.questions:
            # Remove from layout
            self.questions_container_layout.removeWidget(frame)
            # Remove from list
            self.questions.remove(frame)
            # Delete the widget
            frame.deleteLater()

    def setup_dialogues_section(self):
        """Setup the dialogues section with scrollable container"""
        # Add dialogue button
        add_dialogue_button = QPushButton("Add Dialogue")
        add_dialogue_button.clicked.connect(self.add_dialogue_frame)
        self.dialogues_layout.addWidget(add_dialogue_button)
        
        # Create scroll area for dialogues
        self.dialogues_scroll_area = QScrollArea()
        self.dialogues_scroll_area.setWidgetResizable(True)
        self.dialogues_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for the scroll area
        self.dialogues_scroll_container = QWidget()
        self.dialogues_container_layout = QVBoxLayout(self.dialogues_scroll_container)
        self.dialogues_container_layout.setSpacing(10)
        self.dialogues_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add a stretch at the end to push frames to the top
        self.dialogues_container_layout.addStretch()
        
        # Set the container as the scroll area's widget
        self.dialogues_scroll_area.setWidget(self.dialogues_scroll_container)
        
        # Add scroll area to dialogues layout
        self.dialogues_layout.addWidget(self.dialogues_scroll_area)
        
        # Add initial dialogue frame
        self.add_dialogue_frame()
    
    def add_dialogue_frame(self, loaded_title=" ", loaded_lines=None):
        """Add a new dialogue frame (optionally with loaded data)"""
        if loaded_lines is None:
            loaded_lines = []
        
        # Create dialogue data structure
        dialogue_data = {
            "title": loaded_title,
            "lines": []
        }
        self.dialouges.append(dialogue_data)
        
        # Create dialogue group box
        dialogue_frame = QGroupBox(f"Dialogue {len(self.dialouges)}")
        dialogue_frame.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create layout for dialogue frame
        dialogue_layout = QVBoxLayout(dialogue_frame)
        dialogue_layout.setSpacing(10)
        dialogue_layout.setContentsMargins(10, 15, 10, 10)
        
        # Dialogue Title
        title_label = QLabel("Dialogue Title:")
        title_label.setAlignment(Qt.AlignLeft)
        title_entry = QLineEdit()
        title_entry.setText(loaded_title or "")
        
        # Connect title changes to data
        title_entry.textChanged.connect(
            lambda text: dialogue_data.update({"title": text})
        )
        
        dialogue_layout.addWidget(title_label)
        dialogue_layout.addWidget(title_entry)
        
        # Create container for lines
        lines_container = QWidget()
        lines_container_layout = QVBoxLayout(lines_container)
        lines_container_layout.setSpacing(5)
        lines_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Store references
        dialogue_frame.dialogue_data = dialogue_data
        dialogue_frame.title_entry = title_entry
        dialogue_frame.lines_container = lines_container
        dialogue_frame.lines_container_layout = lines_container_layout
        
        # Function to add a line
        def add_line(line_data=None):
            if line_data is None:
                line_data = {
                    "character_name": "",
                    "image": "",
                    "position": "left",
                    "text": "",
                    "translation": "",
                    "audio": ""
                }
            
            dialogue_data["lines"].append(line_data)
            
            # Create line frame
            line_frame = QFrame()
            line_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f8f8f8;
                }
            """)
            
            line_layout = QGridLayout(line_frame)
            line_layout.setSpacing(8)
            line_layout.setContentsMargins(10, 10, 10, 10)
            
            # Character Name
            char_label = QLabel("Character Name:")
            char_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            char_entry = QLineEdit()
            char_entry.setText(line_data.get("character_name", ""))
            char_entry.textChanged.connect(
                lambda text, ld=line_data: ld.update({"character_name": text})
            )
            
            line_layout.addWidget(char_label, 0, 0)
            line_layout.addWidget(char_entry, 0, 1, 1, 3)
            
            # Image URL
            image_label = QLabel("Image URL:")
            image_label.setAlignment(Qt.AlignLeft)
            image_entry = QLineEdit()
            image_entry.setText(line_data.get("image", ""))
            image_entry.textChanged.connect(
                lambda text, ld=line_data: ld.update({"image": text})
            )
            
            line_layout.addWidget(image_label, 1, 0)
            line_layout.addWidget(image_entry, 1, 1)
            
            # Position
            position_label = QLabel("Position:")
            position_label.setAlignment(Qt.AlignLeft)
            position_combo = QComboBox()
            position_combo.addItems(["left", "right"])
            position_combo.setCurrentText(line_data.get("position", "left"))
            position_combo.currentTextChanged.connect(
                lambda text, ld=line_data: ld.update({"position": text})
            )
            
            line_layout.addWidget(position_label, 1, 2)
            line_layout.addWidget(position_combo, 1, 3)
            
            # Dialogue Text
            text_label = QLabel("Dialogue Text:")
            text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            text_edit = QTextEdit()
            text_edit.setMaximumHeight(80)
            text_edit.setPlainText(line_data.get("text", ""))
            text_edit.textChanged.connect(
                lambda ld=line_data: ld.update({"text": text_edit.toPlainText().strip()})
            )
            
            line_layout.addWidget(text_label, 2, 0)
            line_layout.addWidget(text_edit, 2, 1, 1, 3)
            
            # Dialogue Text Translation
            translation_label = QLabel("Translation:")
            translation_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            translation_edit = QTextEdit()
            translation_edit.setMaximumHeight(80)
            translation_edit.setPlainText(line_data.get("translation", ""))
            translation_edit.textChanged.connect(
                lambda ld=line_data: ld.update({"translation": translation_edit.toPlainText().strip()})
            )
            
            line_layout.addWidget(translation_label, 3, 0)
            line_layout.addWidget(translation_edit, 3, 1, 1, 3)
            
            # Audio file
            audio_label = QLabel("Audio:")
            audio_label.setAlignment(Qt.AlignLeft)
            audio_widget = QWidget()
            audio_layout = QHBoxLayout(audio_widget)
            audio_layout.setContentsMargins(0, 0, 0, 0)
            
            audio_entry = QLineEdit()
            audio_entry.setText(line_data.get("audio", ""))
            audio_entry.textChanged.connect(
                lambda text, ld=line_data: ld.update({"audio": text})
            )
            
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(
                lambda checked, entry=audio_entry: self.browse_audio(entry)
            )
            
            audio_layout.addWidget(audio_entry)
            audio_layout.addWidget(browse_button)
            
            line_layout.addWidget(audio_label, 4, 0)
            line_layout.addWidget(audio_widget, 4, 1, 1, 2)
            
            # Button row
            button_widget = QWidget()
            button_layout = QHBoxLayout(button_widget)
            button_layout.setContentsMargins(0, 0, 0, 0)
            
            # Duplicate button
            duplicate_button = QPushButton("Duplicate")
            duplicate_button.clicked.connect(
                lambda: self.duplicate_dialogue_line(
                    line_frame, char_entry.text(), image_entry.text(),
                    position_combo.currentText(), text_edit.toPlainText(),
                    translation_edit.toPlainText(), audio_entry.text()
                )
            )
            
            # Delete button
            delete_button = QPushButton("Delete Line")
            delete_button.clicked.connect(
                lambda: self.remove_dialogue_line(line_frame, dialogue_data, line_data)
            )
            
            button_layout.addWidget(duplicate_button)
            button_layout.addStretch()
            button_layout.addWidget(delete_button)
            
            line_layout.addWidget(button_widget, 5, 0, 1, 4)
            
            # Set column stretch
            line_layout.setColumnStretch(1, 1)
            line_layout.setColumnStretch(3, 1)
            
            # Store references
            line_frame.char_entry = char_entry
            line_frame.image_entry = image_entry
            line_frame.position_combo = position_combo
            line_frame.text_edit = text_edit
            line_frame.translation_edit = translation_edit
            line_frame.audio_entry = audio_entry
            line_frame.line_data = line_data
            
            # Add to lines container
            lines_container_layout.addWidget(line_frame)
            
            return line_frame
        
        # Function to duplicate a line
        def duplicate_line(char_name, image_url, position, text, translation, audio):
            new_line_data = {
                "character_name": char_name,
                "image": image_url,
                "position": position,
                "text": text,
                "translation": translation,
                "audio": audio
            }
            add_line(new_line_data)
        
        # Store duplicate function
        dialogue_frame.duplicate_line = duplicate_line
        
        # Add initial lines if any
        for loaded_line in loaded_lines:
            add_line(loaded_line)
        
        # Add lines container to dialogue layout
        dialogue_layout.addWidget(lines_container)
        
        # Button row for dialogue
        dialogue_button_widget = QWidget()
        dialogue_button_layout = QHBoxLayout(dialogue_button_widget)
        dialogue_button_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add line button
        add_line_button = QPushButton("Add Dialogue Line")
        add_line_button.clicked.connect(lambda: add_line())
        
        # Remove dialogue button
        remove_dialogue_button = QPushButton("Delete Dialogue")
        remove_dialogue_button.clicked.connect(
            lambda: self.remove_dialogue_frame(dialogue_frame, dialogue_data)
        )
        
        dialogue_button_layout.addWidget(add_line_button)
        dialogue_button_layout.addStretch()
        dialogue_button_layout.addWidget(remove_dialogue_button)
        
        dialogue_layout.addWidget(dialogue_button_widget)
        
        # Add dialogue frame to container
        count = self.dialogues_container_layout.count()
        self.dialogues_container_layout.insertWidget(count - 1, dialogue_frame)
        
        return dialogue_frame
    
    def duplicate_dialogue_line(self, source_frame, char_name, image_url, position, text, translation, audio):
        """Duplicate a dialogue line (called from within a line frame)"""
        # Find the parent dialogue frame
        parent_widget = source_frame 
        while parent_widget is not None and not hasattr(parent_widget, "duplicate_line"): 
            parent_widget = parent_widget.parent() 
        if parent_widget is not None: parent_widget.duplicate_line(char_name, image_url, position, text, translation, audio) 
        else: print("No parent with duplicate_line found")
    
    def remove_dialogue_line(self, line_frame, dialogue_data, line_data):
        """Remove a dialogue line"""
        if line_data in dialogue_data["lines"]:
            dialogue_data["lines"].remove(line_data)
            line_frame.setParent(None)
            line_frame.deleteLater()
    
    def remove_dialogue_frame(self, dialogue_frame, dialogue_data):
        """Remove a dialogue frame"""
        if dialogue_data in self.dialouges:
            self.dialouges.remove(dialogue_data)
            dialogue_frame.setParent(None)
            dialogue_frame.deleteLater()
    
    def add_dialogue_frame_loaded_config(self, loaded_title, loaded_lines):
        """Add dialogue frame with loaded configuration"""
        return self.add_dialogue_frame(loaded_title, loaded_lines)
    
    def setup_reading_passages_section(self):
        """Setup the reading passages section with scrollable container"""
        # Add reading passage button (Note: Fixed button text from "Add Dialogue" to "Add Reading Passage")
        add_passage_button = QPushButton("Add Reading Passage")
        add_passage_button.clicked.connect(self.add_reading_passage_frame)
        self.reading_passages_layout.addWidget(add_passage_button)
        
        # Create scroll area for reading passages
        self.reading_passages_scroll_area = QScrollArea()
        self.reading_passages_scroll_area.setWidgetResizable(True)
        self.reading_passages_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for the scroll area
        self.reading_passages_scroll_container = QWidget()
        self.reading_passages_container_layout = QVBoxLayout(self.reading_passages_scroll_container)
        self.reading_passages_container_layout.setSpacing(10)
        self.reading_passages_container_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add a stretch at the end to push frames to the top
        self.reading_passages_container_layout.addStretch()
        
        # Set the container as the scroll area's widget
        self.reading_passages_scroll_area.setWidget(self.reading_passages_scroll_container)
        
        # Add scroll area to reading passages layout
        self.reading_passages_layout.addWidget(self.reading_passages_scroll_area)
        
        # Add initial reading passage frame
        self.add_reading_passage_frame()
    
    def add_reading_passage_frame(self, loaded_title=" ", loaded_text="", loaded_questions=None):
        """Add a new reading passage frame (optionally with loaded data)"""
        if loaded_questions is None:
            loaded_questions = []
        
        # Create passage data structure
        passage_data = {
            "title": loaded_title,
            "text": loaded_text,
            "questions": []
        }
        self.reading_passages.append(passage_data)
        
        # Create passage group box
        passage_frame = QGroupBox(f"Reading Passage {len(self.reading_passages)}")
        passage_frame.setStyleSheet("""
            QGroupBox {
                border: 2px solid #666;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        # Create layout for passage frame
        passage_layout = QVBoxLayout(passage_frame)
        passage_layout.setSpacing(10)
        passage_layout.setContentsMargins(10, 15, 10, 10)
        
        # Remove passage button (at top right)
        remove_passage_widget = QWidget()
        remove_passage_layout = QHBoxLayout(remove_passage_widget)
        remove_passage_layout.setContentsMargins(0, 0, 0, 0)
        
        remove_passage_button = QPushButton("Delete Passage")
        remove_passage_button.clicked.connect(
            lambda: self.remove_reading_passage_frame(passage_frame, passage_data)
        )
        
        remove_passage_layout.addStretch()
        remove_passage_layout.addWidget(remove_passage_button)
        
        passage_layout.addWidget(remove_passage_widget)
        
        # Passage Title
        title_label = QLabel("Passage Title:")
        title_label.setAlignment(Qt.AlignLeft)
        title_entry = QLineEdit()
        title_entry.setText(loaded_title or "")
        title_entry.textChanged.connect(
            lambda text: passage_data.update({"title": text})
        )
        
        passage_layout.addWidget(title_label)
        passage_layout.addWidget(title_entry)
        
        # Passage Text
        text_label = QLabel("Passage Text:")
        text_label.setAlignment(Qt.AlignLeft)
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(200)
        text_edit.setPlainText(loaded_text)
        text_edit.textChanged.connect(
            lambda: passage_data.update({"text": text_edit.toPlainText().strip()})
        )
        
        passage_layout.addWidget(text_label)
        passage_layout.addWidget(text_edit)
        
        # Create container for questions
        questions_container = QWidget()
        questions_container_layout = QVBoxLayout(questions_container)
        questions_container_layout.setSpacing(5)
        questions_container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Store references
        passage_frame.passage_data = passage_data
        passage_frame.title_entry = title_entry
        passage_frame.text_edit = text_edit
        passage_frame.questions_container = questions_container
        passage_frame.questions_container_layout = questions_container_layout
        
        # Function to add a question
        def add_question(question_data=None):
            if question_data is None:
                question_data = {
                    "sentence": "",
                    "blank_after_word": 0,
                    "choices": [],
                    "correct_choice_index": None
                }
            
            passage_data["questions"].append(question_data)
            
            # Create question frame
            question_frame = QFrame()
            question_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    background-color: #f8f8f8;
                }
            """)
            
            question_layout = QGridLayout(question_frame)
            question_layout.setSpacing(8)
            question_layout.setContentsMargins(10, 10, 10, 10)
            
            # Sentence
            sentence_label = QLabel("Sentence:")
            sentence_label.setAlignment(Qt.AlignLeft)
            sentence_entry = QLineEdit()
            sentence_entry.setText(question_data.get("sentence", ""))
            sentence_entry.textChanged.connect(
                lambda text, qd=question_data: qd.update({"sentence": text})
            )
            
            question_layout.addWidget(sentence_label, 0, 0)
            question_layout.addWidget(sentence_entry, 0, 1, 1, 3)
            
            # Blank after word
            blank_label = QLabel("Blank after word #:")
            blank_label.setAlignment(Qt.AlignLeft)
            blank_spinbox = QSpinBox()
            blank_spinbox.setRange(0, 50)
            blank_spinbox.setValue(question_data.get("blank_after_word", 0))
            blank_spinbox.valueChanged.connect(
                lambda value, qd=question_data: qd.update({"blank_after_word": value})
            )
            
            question_layout.addWidget(blank_label, 1, 0)
            question_layout.addWidget(blank_spinbox, 1, 1)
            
            # Choices container
            choices_widget = QWidget()
            choices_layout = QVBoxLayout(choices_widget)
            choices_layout.setSpacing(5)
            choices_layout.setContentsMargins(0, 0, 0, 0)
            
            # Create button group for correct choice
            correct_choice_group = QButtonGroup(question_frame)
            correct_choice_group.setExclusive(True)
            
            # Function to add a choice
            def add_choice(choice_data=None, is_correct=False):
                if choice_data is None:
                    choice_data = {"value": ""}
                
                question_data["choices"].append(choice_data)
                
                choice_widget = QWidget()
                choice_layout = QHBoxLayout(choice_widget)
                choice_layout.setContentsMargins(0, 0, 0, 0)
                
                # Radio button for correct choice
                choice_radio = QRadioButton()
                choice_index = len(question_data["choices"]) - 1
                correct_choice_group.addButton(choice_radio, choice_index)
                
                if is_correct:
                    choice_radio.setChecked(True)
                    question_data["correct_choice_index"] = choice_index
                
                # Connect radio button to update correct_choice_index
                choice_radio.toggled.connect(
                    lambda checked, idx=choice_index: (
                        question_data.update({"correct_choice_index": idx}) 
                        if checked else None
                    )
                )
                
                # Choice entry
                choice_entry = QLineEdit()
                choice_entry.setText(choice_data.get("value", ""))
                choice_entry.textChanged.connect(
                    lambda text, cd=choice_data: cd.update({"value": text})
                )
                
                # Remove choice button
                remove_choice_button = QPushButton("Delete")
                remove_choice_button.clicked.connect(
                    lambda: remove_choice(choice_widget, choice_data, choice_radio)
                )
                
                choice_layout.addWidget(choice_radio)
                choice_layout.addWidget(choice_entry)
                choice_layout.addWidget(remove_choice_button)
                choice_layout.setStretch(1, 1)
                
                # Add to choices layout
                choices_layout.addWidget(choice_widget)
                
                # Store reference
                choice_widget.choice_radio = choice_radio
                choice_widget.choice_entry = choice_entry
                
                return choice_widget
            
            # Function to remove a choice
            def remove_choice(choice_widget, choice_data, choice_radio):
                # Remove from data
                if choice_data in question_data["choices"]:
                    idx = question_data["choices"].index(choice_data)
                    question_data["choices"].remove(choice_data)
                    
                    # Update correct_choice_index if needed
                    if question_data["correct_choice_index"] == idx:
                        question_data["correct_choice_index"] = None
                    
                    # Remove from button group
                    correct_choice_group.removeButton(choice_radio)
                    
                    # Remove from layout
                    choices_layout.removeWidget(choice_widget)
                    choice_widget.deleteLater()
            
            # Add choices if any
            for i, choice in enumerate(question_data.get("choices", [])):
                is_correct = (i == question_data.get("correct_choice_index"))
                add_choice(choice, is_correct)
            
            # Add choice button
            add_choice_button = QPushButton("Add Choice")
            add_choice_button.clicked.connect(lambda: add_choice())
            
            choices_layout.addWidget(add_choice_button)
            
            # Add choices widget to question layout
            question_layout.addWidget(choices_widget, 2, 0, 1, 4)
            
            # Button row
            question_button_widget = QWidget()
            question_button_layout = QHBoxLayout(question_button_widget)
            question_button_layout.setContentsMargins(0, 0, 0, 0)
            
            # Remove question button
            remove_question_button = QPushButton("Delete Question")
            remove_question_button.clicked.connect(
                lambda: remove_question(question_frame, question_data)
            )
            
            question_button_layout.addStretch()
            question_button_layout.addWidget(remove_question_button)
            
            question_layout.addWidget(question_button_widget, 3, 0, 1, 4)
            
            # Set column stretch
            question_layout.setColumnStretch(1, 1)
            question_layout.setColumnStretch(3, 1)
            
            # Store references
            question_frame.question_data = question_data
            question_frame.sentence_entry = sentence_entry
            question_frame.blank_spinbox = blank_spinbox
            question_frame.choices_layout = choices_layout
            question_frame.correct_choice_group = correct_choice_group
            question_frame.add_choice = lambda cd=None: add_choice(cd)
            
            # Add to questions container
            questions_container_layout.addWidget(question_frame)
            
            return question_frame
        
        # Function to remove a question
        def remove_question(question_frame, question_data):
            if question_data in passage_data["questions"]:
                passage_data["questions"].remove(question_data)
                questions_container_layout.removeWidget(question_frame)
                question_frame.deleteLater()
        
        # Add loaded questions
        for loaded_question in loaded_questions:
            add_question(loaded_question)
        
        # Add questions container to passage layout
        passage_layout.addWidget(questions_container)
        
        # Add question button
        add_question_button = QPushButton("Add Question")
        add_question_button.clicked.connect(lambda: add_question())
        passage_layout.addWidget(add_question_button)
        
        # Add passage frame to container
        count = self.reading_passages_container_layout.count()
        self.reading_passages_container_layout.insertWidget(count - 1, passage_frame)
        
        return passage_frame
    
    def remove_reading_passage_frame(self, passage_frame, passage_data):
        """Remove a reading passage frame"""
        if passage_data in self.reading_passages:
            self.reading_passages.remove(passage_data)
            passage_frame.setParent(None)
            passage_frame.deleteLater()
    
    def add_reading_passage_frame_loaded_config(self, title, text, questions):
        """Add reading passage frame with loaded configuration"""
        return self.add_reading_passage_frame(title, text, questions)
        
    def setup_settings_section(self):
        """Setup the settings section"""
        # Create a grid layout for settings
        settings_layout = QGridLayout(self.settings_frame)
        settings_layout.setSpacing(10)
        settings_layout.setContentsMargins(10, 10, 10, 10)
        
        # Output file settings
        output_label = QLabel("Output File:")
        output_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.output_file_edit = QLineEdit()
        self.output_file_edit.setText("animal_game.html")
        self.output_file_edit.setPlaceholderText("Enter output file name...")
        
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_output)
        
        settings_layout.addWidget(output_label, 0, 0)
        settings_layout.addWidget(self.output_file_edit, 0, 1)
        settings_layout.addWidget(browse_button, 0, 2)
        
        # Test title
        test_title_label = QLabel("Test Title:")
        test_title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        self.test_title_edit = QLineEdit()
        self.test_title_edit.setText("Lesson Practice")
        self.test_title_edit.setPlaceholderText("Enter test title...")
        
        settings_layout.addWidget(test_title_label, 1, 0)
        settings_layout.addWidget(self.test_title_edit, 1, 1)
        
        # Set column stretch for responsive resizing
        settings_layout.setColumnStretch(1, 1)
        
        # You can add more settings here as needed
        # For example, add a stretch to push everything to the top
        settings_layout.setRowStretch(2, 1)
    
    def browse_output(self):
        """Browse for output file location"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save HTML File",
            "",
            "HTML Files (*.html *.htm);;All Files (*.*)"
        )
        if file_name:
            # Ensure .html extension if not provided
            if not file_name.lower().endswith(('.html', '.htm')):
                file_name += '.html'
            self.output_file_edit.setText(file_name)

    def clear_dialouges(self):
        """Remove all dialogue frames and clear dialogue data."""
        # 1. Remove all dialogue group boxes from the layout and delete them
        for frame in self.dialogues_scroll_container.findChildren(QGroupBox):
            # Only delete top‑level dialogue frames (they contain the attribute 'dialogue_data')
            if hasattr(frame, 'dialogue_data'):
                # Remove the associated data from the list
                if frame.dialogue_data in self.dialouges:
                    self.dialouges.remove(frame.dialogue_data)
                # Delete the widget
                frame.deleteLater()

        # 2. Clear the entire list (safe even if some entries were missed)
        self.dialouges.clear()

        # 3. Restore the stretch at the bottom of the container layout
        #    (it might have been removed if all frames were deleted)
        #    First, remove any existing stretches
        while True:
            last_item = self.dialogues_container_layout.itemAt(
                self.dialogues_container_layout.count() - 1
            )
            if last_item and last_item.spacerItem():
                self.dialogues_container_layout.removeItem(last_item)
            else:
                break
        # Add a fresh stretch
        self.dialogues_container_layout.addStretch()
        self.dialouges = []

    def remove_all_reading_passages(self):
        """Remove all reading passage frames and clear passage data."""
        # 1. Find and delete every top‑level passage frame
        for frame in self.reading_passages_scroll_container.findChildren(QGroupBox):
            # The main passage frames have the custom attribute 'passage_data'
            if hasattr(frame, 'passage_data'):
                # Remove its data from the list
                if frame.passage_data in self.reading_passages:
                    self.reading_passages.remove(frame.passage_data)
                # Delete the widget (all child widgets, including questions, are auto‑deleted)
                frame.deleteLater()

        # 2. Explicitly clear the data list (catches any missed entries)
        self.reading_passages.clear()

        self.reading_passages = []

        # 3. Restore the stretch at the bottom of the container layout
        while True:
            last_item = self.reading_passages_container_layout.itemAt(
                self.reading_passages_container_layout.count() - 1
            )
            if last_item and last_item.spacerItem():
                self.reading_passages_container_layout.removeItem(last_item)
            else:
                break
        self.reading_passages_container_layout.addStretch()
            
    def new_config(self):
        """Clear all data and reset to default"""
        try:
            # Clear animals
            for animal in self.animals[:]:  # Copy list to avoid modification during iteration
                self.remove_animal_frame(animal)
            self.animals = []
            
            # Clear questions
            for question in self.questions[:]:
                self.remove_question_frame(question)
            self.questions = []
            
            # Clear dialouges data and UI widgets
            self.clear_dialouges()

            # Clear reading passages data and UI widgets
            self.remove_all_reading_passages()
            
            # Reset settings
            if hasattr(self, 'animals_per_row_spinbox'):
                self.animals_per_row_spinbox.setValue(3)
            
            if hasattr(self, 'output_file_edit'):
                self.output_file_edit.setText("animal_game.html")
            
            if hasattr(self, 'test_title_edit'):
                self.test_title_edit.setText("Lesson Practice")
            
            # Add one empty frame to each section for user convenience
            self.add_animal_frame()
            self.add_question_frame()
            self.add_dialogue_frame()
            self.add_reading_passage_frame()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create new configuration: {str(e)}")
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            file_name, _ = QFileDialog.getOpenFileName(
                self,
                "Load Configuration",
                "",
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if not file_name:
                return
            
            with open(file_name, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Clear current data
            self.new_config()
            
            # Remove the default empty frames added by new_config()
            # (We'll replace them with loaded data)
            for animal in self.animals[:]:
                self.remove_animal_frame(animal)
            
            for question in self.questions[:]:
                self.remove_question_frame(question)
            
            self.clear_dialouges()
            
            self.remove_all_reading_passages()
            
            # Load animals
            for animal_data in config.get('animals', []):
                frame = self.add_animal_frame()
                if frame and hasattr(frame, 'image_url'):
                    frame.image_url.setText(animal_data.get('image_url', ''))
                    frame.title.setText(animal_data.get('title', ''))
                    frame.word.setText(animal_data.get('word', ''))
                    frame.audio.setText(animal_data.get('audio', ''))
            
            # Load questions
            for question_data in config.get('questions', []):
                frame = self.add_question_frame()
                if frame and hasattr(frame, 'image_url'):
                    frame.image_url.setText(question_data.get('image_url', ''))
                    frame.question_text.setText(question_data.get('text', ''))
                    
                    # Clear default answers
                    while frame.answer_entries:
                        # We need to simulate removing the first answer
                        # Since we don't have direct access to the row widgets,
                        # we'll need to remove them from the layout
                        if hasattr(frame, 'answers_layout'):
                            item = frame.answers_layout.takeAt(0)
                            if item and item.widget():
                                widget = item.widget()
                                if widget != frame.add_answer_button:  # Don't remove the add button
                                    frame.answers_layout.removeWidget(widget)
                                    widget.deleteLater()
                    
                    # Add answers from config
                    answers = question_data.get('answers', [])
                    correct_index = question_data.get('correct_index', 0)
                    
                    for i, answer in enumerate(answers):
                        if hasattr(frame, 'add_answer_row'):
                            frame.add_answer_row()
                            if frame.answer_entries and i < len(frame.answer_entries):
                                frame.answer_entries[i].setText(answer)
                    
                    # Set correct answer
                    if answers and 0 <= correct_index < len(frame.radio_buttons):
                        frame.radio_buttons[correct_index].setChecked(True)
            
            # Load dialogues
            for dialogue_data in config.get('dialogues', []):
                self.add_dialogue_frame_loaded_config(
                    dialogue_data.get('title', ''),
                    dialogue_data.get('lines', [])
                )
            
            # Load reading passages
            for passage_data in config.get('reading_passages', []):
                self.add_reading_passage_frame_loaded_config(
                    passage_data.get('title', ''),
                    passage_data.get('text', ''),
                    passage_data.get('questions', [])
                )
            
            # Load settings
            if 'animals_per_row' in config and hasattr(self, 'animals_per_row_spinbox'):
                self.animals_per_row_spinbox.setValue(config['animals_per_row'])
            
            if 'output_file' in config and hasattr(self, 'output_file_edit'):
                self.output_file_edit.setText(config.get('output_file', 'animal_game.html'))
            
            if 'test_title' in config and hasattr(self, 'test_title_edit'):
                self.test_title_edit.setText(config.get('test_title', 'Lesson Practice'))
            
            QMessageBox.information(self, "Success", "Configuration loaded successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load configuration: {str(e)}")
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Configuration",
                "",
                "JSON Files (*.json);;All Files (*.*)"
            )
            
            if not file_name:
                return
            
            # Ensure .json extension
            if not file_name.lower().endswith('.json'):
                file_name += '.json'
            
            # Prepare animals data
            animals_data = []
            for animal in self.animals:
                if hasattr(animal, 'image_url') and hasattr(animal, 'title'):
                    animals_data.append({
                        'image_url': animal.image_url.text(),
                        'title': animal.title.text(),
                        'word': animal.word.text() if hasattr(animal, 'word') else '',
                        'audio': animal.audio.text() if hasattr(animal, 'audio') else ''
                    })
            
            # Prepare questions data
            questions_data = []
            for question in self.questions:
                if hasattr(question, 'image_url') and hasattr(question, 'question_text'):
                    # Get answers from entries
                    answers = []
                    for entry in question.answer_entries:
                        if hasattr(entry, 'text'):
                            answers.append(entry.text())
                    
                    # Find correct answer index
                    correct_index = -1
                    for i, radio in enumerate(question.radio_buttons):
                        if radio.isChecked():
                            correct_index = i
                            break
                    
                    questions_data.append({
                        'image_url': question.image_url.text(),
                        'text': question.question_text.text(),
                        'answers': answers,
                        'correct_index': correct_index
                    })
            
            # Prepare dialogues data
            dialogues_data = self.dialouges
            
            # Prepare reading passages data
            reading_passages_data = self.reading_passages
            
            # Prepare config
            config = {
                'animals': animals_data,
                'questions': questions_data,
                'dialogues': dialogues_data,
                'reading_passages': reading_passages_data,
                'animals_per_row': self.animals_per_row_spinbox.value() if hasattr(self, 'animals_per_row_spinbox') else 3,
                'output_file': self.output_file_edit.text() if hasattr(self, 'output_file_edit') else 'animal_game.html',
                'test_title': self.test_title_edit.text() if hasattr(self, 'test_title_edit') else 'Lesson Practice'
            }
            
            # Save to file
            with open(file_name, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "Success", "Configuration saved successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save configuration: {str(e)}")
    
    def remove_animal_frame(self, frame):
        """Remove an animal frame (helper method)"""
        if frame in self.animals:
            # Remove from layout
            self.animals_container_layout.removeWidget(frame)
            # Remove from list
            self.animals.remove(frame)
            # Delete the widget
            frame.deleteLater()

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
                    options_html = '<option value=""> </option>'
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
                options_html = '<option value=""> </option>'
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
        print(self.animals_per_row_spinbox.value())
        print("1")
        for i, frame in enumerate(self.animals, start=1):
            print(f"Animal {i}:")
            print(f"  Image URL: {frame.image_url.text()}")
            print(f"  Title: {frame.title.text()}")
            print(f"  Word to speak: {frame.word.text()}")
            print(f"  Audio file: {frame.audio.text()}")
            print()  # blank line between animals
        print("2")
        for idx, frame in enumerate(self.questions, start=1):
            print(f"Question {idx}:")
            print(f"  Image URL: {frame.image_url.text()}")
            print(f"  Question Text: {frame.question_text.text()}")
            print("  Answers:")

            # Iterate through answer entries and their corresponding radio buttons
            for ans_idx, (entry, radio) in enumerate(zip(frame.answer_entries, frame.radio_buttons), start=1):
                correct = "*" if radio.isChecked() else " "   # mark correct answer
                print(f"    {ans_idx}. [{correct}] {entry.text()}")
            print()  # blank line between questions
        print("3")
        print(self.dialouges)
        print("4")
        print(self.reading_passages)
        return
        try:
            # Prepare animals HTML
            animals_html = ""
            animals_per_row = int(self.animals_per_row_spinbox.value())
            test_title_var=""
            test_title_var+=f"""{self.test_title_var.get()}"""
            
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
                    character_name = line.get("character_name", "") or ""
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
                        <div class="character-name {pos}">{character_name}</div>
                        <div class="dialogue-text" id="dialogue_text_{d_idx}_{l_idx}" data-fulltext="{text}"></div>
                        </div>
                    </div>

                    <!-- TRANSLATION button -->
                    <button class="show-translation-button" id="line_translation_button_{d_idx}_{l_idx}" onclick="showTranslate({d_idx},{l_idx})">🌐👉 Click here to translate</button>
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
        margin-bottom:18px;
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
    width: fit-content;
    }}

    /* text grows vertically after width max */

    .dialogue-body.left {{
    text-align:left;
    align-items:end;
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
        width:fit-content;
        height:fit-content;
        border-radius:5px;
        cursor:pointer;
        margin-top:8px;
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
    }}

    .dialogue {{ margin: 20px 0; text-align: right; }}
    .dialogue-title {{ margin: 0 0 0px 0; color: #0277bd;align-self:center }}
    .dialogue-container {{ display: flex; flex-direction: column; gap: 8px; }}

    .dialogue-line {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px;
    border-radius: 12px;
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
    }}
    .dialogue-line.active .dialogue-thumb img {{
    transform: scale(1.06);
    border-color: #0288d1;
    }}
    .dialogue-line.active .dialogue-body .dialogue-text {{
    font-size: 1rem; 
    color: #01579b; 
    border-color: #0288d1; 
    background: #fff8e1; 
    border-radius: 12px;
    border: 2px solid transparent;
    box-shadow: 0 10px 30px rgba(2,62,118,0.12);
    width:fit-content;
    padding:7px;
    }}

    .dialogue-body {{
    display: flex; 
    flex-direction: column; 
    justify-content: center; 
    min-height: 100%; 
    flex: 1; 
    position: relative;
    }}
    .character-name{{
    font-weight: bold; 
    }}
    .dialogue-line.active .dialogue-body .character-name.right{{
    position: absolute; 
    top: 0; 
    right: 0;
    }}
    .dialogue-line.active .dialogue-body .character-name.left{{
    position: absolute; 
    top: 0; 
    left: 0;
    }}
    .dialogue-text {{ 
    
    }}
    @media (max-width: 600px) {{
    .dialogue-thumb img {{ width: 60px; height: 60px; }}
    .main-line {{max-width:80%;}}
    .main-line.expanded {{width:80%;}}
    .dialogue-translation {{max-width:80%;align-self:center;}}
    .dialogue-line-wrapper {{flex-direction:column;margin-bottom:6px;}}
    .dialogue-line-wrapper.left  {{ flex-direction: column; align-items:self-end}}
    .dialogue-line-wrapper.right {{ flex-direction: column; align-items:self-start}}
    .dialogue-head {{margin-bottom:30px}}
    .dialogue-body {{height:79px}}
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
    <h1>{test_title_var}</h1>

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
    <h3 class="feelings-title">?How do you feel</h3>
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
      <p class="contact-text">:For contact or more information</p>
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
                if (!audio) {{ // No audio element found → resolve immediately 
                res(); 
                return; 
                }} 
                // If audio exists but isn’t playing, you may want to resolve too 
                if (audio.readyState === 0) {{ // No source loaded 
                res(); 
                return; 
                }}
                // Otherwise wait until audio finishes
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
                test_title_var=test_title_var,
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
    app = QApplication(sys.argv)
    window = AnimalLearningGameGenerator()
    window.show()
    sys.exit(app.exec())

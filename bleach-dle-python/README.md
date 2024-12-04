# Bleach-dle

A daily Bleach character guessing game inspired by Wordle and Narutodle. Each day, players try to guess a new Bleach character by comparing various attributes like gender, occupation, affiliations, and more.

## Features

- Daily character changes at 00:00 GMT
- Characters won't repeat until all have been used
- Attribute matching system with full and partial matches
- Character image display in suggestions and grid
- Keyboard navigation support
- Mobile-responsive design
- Countdown timer to next character

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd bleach-dle-python
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Add character images:
Place character images in `static/images/characters/` directory with filenames matching those in `data/characters.json`.

5. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Game Rules

1. Each day, a new character is selected
2. Players guess characters and receive feedback on various attributes:
   - Green: Exact match
   - Yellow: Partial match
   - Red: No match
   - Up/Down arrows: Chronological order for story arcs
3. Game continues until the correct character is guessed
4. A new character becomes available at 00:00 GMT

## Directory Structure

```
bleach-dle-python/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── data/
│   └── characters.json # Character data
├── static/
│   ├── css/
│   │   └── style.css  # Styles
│   ├── js/
│   │   └── game.js    # Frontend logic
│   └── images/        # Image assets
└── templates/
    └── index.html     # Main game template
```

## Technologies Used

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Database: JSON file (characters.json)
- Styling: Custom CSS with animations
- Images: Character portraits and background

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - feel free to use and modify for your own projects! 
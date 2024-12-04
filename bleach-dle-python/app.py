from flask import Flask, render_template, jsonify, request, session, send_from_directory
from datetime import datetime, timedelta
import json
import os
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_session import Session
import tempfile

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure session
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-key-change-this'),
    SESSION_TYPE='filesystem',
    SESSION_FILE_DIR=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flask_session'),
    SESSION_PERMANENT=False,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1)
)
Session(app)

# Configure static files
app.static_folder = 'static'
app.static_url_path = '/static'

# Load character data
try:
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'characters.json'), 'r') as f:
        characters = json.load(f)
except FileNotFoundError:
    print("Error: characters.json not found!")
    characters = []
except json.JSONDecodeError:
    print("Error: Invalid JSON in characters.json!")
    characters = []

def get_daily_character():
    """Get the daily character based on UTC date."""
    if not characters:
        return None
        
    EPOCH_START = datetime(2024, 1, 1).timestamp()
    MS_PER_DAY = 86400000  # Milliseconds in a day
    
    now = datetime.utcnow()
    days_since_epoch = int((now.timestamp() * 1000 - EPOCH_START) / MS_PER_DAY)
    total_characters = len(characters)
    cycle_number = days_since_epoch // total_characters
    index_in_cycle = days_since_epoch % total_characters
    
    # Create deterministic shuffle
    indices = list(range(total_characters))
    for i in range(total_characters - 1, 0, -1):
        hash_val = (i * cycle_number * 2654435761) % (2**32)
        j = hash_val % (i + 1)
        indices[i], indices[j] = indices[j], indices[i]
    
    return characters[indices[index_in_cycle]]

def get_time_until_next():
    """Get time until next character in seconds."""
    now = datetime.utcnow()
    tomorrow = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    return int((tomorrow - now).total_seconds())

@app.route('/')
def index():
    """Render the main game page."""
    try:
        # Clear session if it's a new day
        if 'last_visit' in session:
            last_visit = datetime.fromisoformat(session['last_visit'])
            now = datetime.utcnow()
            if last_visit.date() != now.date():
                session.clear()
        session['last_visit'] = datetime.utcnow().isoformat()
        return render_template('index.html')
    except Exception as e:
        print(f"Error in index route: {str(e)}")
        return render_template('index.html')

@app.route('/api/daily-character')
def daily_character():
    """Get the daily character."""
    try:
        character = get_daily_character()
        if not character:
            return jsonify({'error': 'No characters available'}), 500
            
        time_until_next = get_time_until_next()
        return jsonify({
            'timeUntilNext': time_until_next,
            'character': character
        })
    except Exception as e:
        print(f"Error in daily_character route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/suggestions')
def get_suggestions():
    """Get character suggestions based on search query."""
    try:
        query = request.args.get('query', '').lower()
        if not query:
            return jsonify([])
        
        # Get already guessed characters from session
        guessed_ids = session.get('guessed_ids', [])
        
        # Filter characters based on query and exclude already guessed characters
        suggestions = [
            char for char in characters
            if query in char['name'].lower() and char['id'] not in guessed_ids
        ]
        
        # Limit to top 5 suggestions
        return jsonify(suggestions[:5])
    except Exception as e:
        print(f"Error in suggestions route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/check-guess', methods=['POST'])
def check_guess():
    """Check if a guess matches the daily character."""
    try:
        data = request.json
        if not data or 'guess' not in data:
            return jsonify({'error': 'Invalid request'}), 400
            
        guess_name = data['guess']
        target = get_daily_character()
        
        if not target:
            return jsonify({'error': 'No daily character available'}), 500
        
        # Find guessed character
        guessed = next((char for char in characters if char['name'].lower() == guess_name.lower()), None)
        if not guessed:
            return jsonify({'error': 'Character not found'}), 404
        
        # Track guessed characters in session
        if 'guessed_ids' not in session:
            session['guessed_ids'] = []
        if guessed['id'] not in session['guessed_ids']:
            session['guessed_ids'].append(guessed['id'])
        
        # Check matches
        matches = {
            'character': guessed['id'] == target['id'],
            'gender': guessed['gender'] == target['gender'],
            'occupation': guessed['occupation'] == target['occupation'],
            'affiliations': check_array_match(guessed['affiliations'], target['affiliations']),
            'zanpakutoTypes': check_array_match(guessed['zanpakutoTypes'], target['zanpakutoTypes']),
            'debutArc': check_arc_order(guessed['debutArc'], target['debutArc']),
            'powers': check_array_match(guessed['powers'], target['powers']),
            'locations': check_array_match(guessed['locations'], target['locations'])
        }
        
        return jsonify({
            'matches': matches,
            'character': guessed
        })
    except Exception as e:
        print(f"Error in check_guess route: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def check_array_match(guessed_array, target_array):
    """Check if arrays match fully, partially, or not at all."""
    if not guessed_array and not target_array:
        return {'result': 'match', 'type': 'full'}
    if not guessed_array or not target_array:
        return {'result': 'no-match', 'type': 'none'}
    
    has_full_match = len(guessed_array) == len(target_array) and all(item in target_array for item in guessed_array)
    has_partial_match = any(item in target_array for item in guessed_array)
    
    if has_full_match:
        return {'result': 'match', 'type': 'full'}
    elif has_partial_match:
        return {'result': 'partial-match', 'type': 'partial'}
    return {'result': 'no-match', 'type': 'none'}

def check_arc_order(guessed_arc, target_arc):
    """Check if arcs match and determine chronological order."""
    arc_order = {
        'Agent of the Shinigami Arc': 1,
        'Soul Society Arc': 2,
        'Bount Arc': 3,
        'Arrancar Arc': 4,
        'Hueco Mundo Arc': 5,
        'Turn Back the Pendulum Arc': 6,
        'Fake Karakura Town Arc': 7,
        'Zanpakutō Unknown Tales Arc': 8,
        'Beast Swords Arc': 9,
        'Gotei 13 Invading Army Arc': 10,
        'Lost Substitute Shinigami Arc': 11,
        'The Thousand-Year Blood War Arc': 12
    }
    
    guessed_order = arc_order.get(guessed_arc, 0)
    target_order = arc_order.get(target_arc, 0)
    
    if guessed_arc == target_arc:
        return {'result': 'match', 'arrow': None}
    elif guessed_order < target_order:
        return {'result': 'no-match', 'arrow': '↑'}
    else:
        return {'result': 'no-match', 'arrow': '↓'}

if __name__ == '__main__':
    app.run(debug=True) 
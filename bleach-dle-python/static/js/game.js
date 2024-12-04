let targetCharacter = null;
let guesses = [];
let gameWon = false;
let selectedSuggestionIndex = -1;
let suggestions = [];

// Load saved state from localStorage
function loadSavedState() {
    const today = new Date().toDateString();
    const savedDate = localStorage.getItem('bleachdle_date');
    const savedGuesses = localStorage.getItem('bleachdle_guesses');
    const savedGameWon = localStorage.getItem('bleachdle_gameWon');

    // Clear saved state if it's a new day
    if (savedDate !== today) {
        localStorage.clear();
        localStorage.setItem('bleachdle_date', today);
        return;
    }

    // Load saved guesses and game state
    if (savedGuesses) {
        guesses = JSON.parse(savedGuesses);
        updateGuessGrid(); // Show saved guesses
    }
    if (savedGameWon) {
        gameWon = JSON.parse(savedGameWon);
        if (gameWon) {
            showWinMessage();
        }
    }
}

// Save current state to localStorage
function saveState() {
    localStorage.setItem('bleachdle_date', new Date().toDateString());
    localStorage.setItem('bleachdle_guesses', JSON.stringify(guesses));
    localStorage.setItem('bleachdle_gameWon', JSON.stringify(gameWon));
}

// Initialize game state
fetch('/api/daily-character')
    .then(response => response.json())
    .then(data => {
        targetCharacter = data.character;
        updateCountdown(data.timeUntilNext);
        setInterval(() => updateCountdown(data.timeUntilNext), 1000);
        loadSavedState(); // Load saved state after getting daily character
    })
    .catch(error => console.error('Error:', error));

function updateCountdown(initialSeconds) {
    const countdownElement = document.getElementById('countdown');
    let seconds = initialSeconds;

    function formatTime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
    }

    function tick() {
        if (seconds > 0) {
            seconds--;
            countdownElement.textContent = formatTime(seconds);
        } else {
            window.location.reload();
        }
    }

    tick();
    return setInterval(tick, 1000);
}

const input = document.getElementById('guess-input');
const guessButton = document.getElementById('guess-button');
const suggestionsDropdown = document.getElementById('suggestions-dropdown');

input.addEventListener('input', handleInputChange);
input.addEventListener('keydown', handleKeyDown);
guessButton.addEventListener('click', handleGuess);

function handleInputChange(e) {
    const value = e.target.value;
    selectedSuggestionIndex = -1;

    if (!value.trim()) {
        suggestionsDropdown.style.display = 'none';
        suggestions = [];
        return;
    }

    fetch(`/api/suggestions?query=${encodeURIComponent(value)}`)
        .then(response => response.json())
        .then(data => {
            suggestions = data;
            updateSuggestionsDropdown();
        })
        .catch(error => console.error('Error:', error));
}

function getCharacterImagePath(imageName) {
    // Return a default image if no image name is provided
    if (!imageName) return '/static/images/characters/default.jpg';
    return `/static/images/characters/${imageName}`;
}

function updateSuggestionsDropdown() {
    if (!suggestions.length) {
        suggestionsDropdown.style.display = 'none';
        return;
    }

    suggestionsDropdown.innerHTML = suggestions
        .map((suggestion, index) => `
            <div class="suggestion-item ${index === selectedSuggestionIndex ? 'selected' : ''}"
                 onclick="handleSuggestionClick('${suggestion.name}')">
                <img src="${getCharacterImagePath(suggestion.image)}" 
                     alt="${suggestion.name}"
                     class="character-image"
                     onerror="this.onerror=null; this.src='/static/images/characters/default.jpg';">
                ${suggestion.name}
            </div>
        `)
        .join('');

    suggestionsDropdown.style.display = 'block';
}

function handleSuggestionClick(name) {
    input.value = name;
    suggestionsDropdown.style.display = 'none';
    suggestions = [];
    selectedSuggestionIndex = -1;
}

function handleKeyDown(e) {
    if (!suggestions.length) {
        if (e.key === 'Enter' && input.value.trim()) {
            handleGuess();
        }
        return;
    }

    switch (e.key) {
        case 'ArrowDown':
            e.preventDefault();
            selectedSuggestionIndex = 
                selectedSuggestionIndex < suggestions.length - 1 ? selectedSuggestionIndex + 1 : 0;
            updateSuggestionsDropdown();
            break;
        case 'ArrowUp':
            e.preventDefault();
            selectedSuggestionIndex = 
                selectedSuggestionIndex > 0 ? selectedSuggestionIndex - 1 : suggestions.length - 1;
            updateSuggestionsDropdown();
            break;
        case 'Enter':
            e.preventDefault();
            if (selectedSuggestionIndex >= 0) {
                handleSuggestionClick(suggestions[selectedSuggestionIndex].name);
            } else if (input.value.trim()) {
                handleGuess();
            }
            break;
        case 'Escape':
            suggestionsDropdown.style.display = 'none';
            selectedSuggestionIndex = -1;
            break;
    }
}

function handleGuess() {
    if (!input.value.trim() || gameWon) return;

    fetch('/api/check-guess', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ guess: input.value.trim() })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Character not found!');
                return;
            }

            const guess = {
                character: data.character,
                matches: data.matches
            };

            // Add new guess to the beginning of the array
            guesses.unshift(guess);
            saveState(); // Save state after each guess
            updateGuessGrid();
            input.value = '';
            suggestionsDropdown.style.display = 'none';
            suggestions = [];

            if (data.matches.character) {
                gameWon = true;
                saveState(); // Save state when game is won
                showWinMessage();
            }
        })
        .catch(error => console.error('Error:', error));
}

function updateGuessGrid() {
    const guessesContainer = document.getElementById('guesses');
    
    // Get saved guesses from localStorage if they exist
    const savedGuesses = localStorage.getItem('bleachdle_guesses');
    if (savedGuesses) {
        guesses = JSON.parse(savedGuesses);
    }
    
    // Display all guesses with newest at the top
    guessesContainer.innerHTML = guesses
        .map((guess, guessIndex) => createGuessRow(guess, guessIndex))
        .join('');

    // Start reveal animation for newest guess (first row)
    if (guesses.length > 0) {
        const cells = guessesContainer.querySelector('.guess-row:first-child').children;
        Array.from(cells).forEach((cell, i) => {
            setTimeout(() => cell.classList.add('revealed'), i * 400);
        });
    }
}

function createGuessRow(guess, guessIndex) {
    return `
        <div class="guess-row">
            <div class="grid-cell character-cell ${guess.matches.character ? 'match' : 'no-match'}">
                <img src="${getCharacterImagePath(guess.character.image)}" 
                     alt="${guess.character.name}"
                     onerror="this.onerror=null; this.src='/static/images/characters/default.jpg';">
                <div class="character-name-overlay">${guess.character.name}</div>
            </div>
            <div class="grid-cell ${guess.matches.gender ? 'match' : 'no-match'}"
                 data-long-text="${getTextLengthClass(guess.character.gender)}">
                ${guess.character.gender}
            </div>
            <div class="grid-cell ${guess.matches.occupation ? 'match' : 'no-match'}"
                 data-long-text="${getTextLengthClass(guess.character.occupation)}">
                ${guess.character.occupation}
            </div>
            <div class="grid-cell ${guess.matches.affiliations.result}"
                 data-long-text="${getTextLengthClass(formatArrayToString(guess.character.affiliations))}">
                ${formatArrayToString(guess.character.affiliations)}
            </div>
            <div class="grid-cell ${guess.matches.zanpakutoTypes.result}"
                 data-long-text="${getTextLengthClass(formatArrayToString(guess.character.zanpakutoTypes))}">
                ${formatArrayToString(guess.character.zanpakutoTypes)}
            </div>
            <div class="grid-cell ${guess.matches.debutArc.result}"
                 data-long-text="${getTextLengthClass(guess.character.debutArc)}">
                ${guess.character.debutArc}
                ${guess.matches.debutArc.arrow ? `<span class="arc-arrow">${guess.matches.debutArc.arrow}</span>` : ''}
            </div>
            <div class="grid-cell ${guess.matches.powers.result}"
                 data-long-text="${getTextLengthClass(formatArrayToString(guess.character.powers))}">
                ${formatArrayToString(guess.character.powers)}
            </div>
            <div class="grid-cell ${guess.matches.locations.result}"
                 data-long-text="${getTextLengthClass(formatArrayToString(guess.character.locations))}">
                ${formatArrayToString(guess.character.locations)}
            </div>
        </div>
    `;
}

function formatArrayToString(arr) {
    return arr.length === 0 ? 'None' : arr.join(', ');
}

function getTextLengthClass(text) {
    const length = text.toString().length;
    const wordCount = text.toString().split(',').length;
    
    if (length > 40 || wordCount > 3) return 'very-long-text';
    if (length > 20 || wordCount > 2) return 'long-text';
    return '';
}

function showWinMessage() {
    const message = document.createElement('div');
    message.className = 'win-message';
    message.textContent = `Congratulations! You found the character in ${guesses.length} guesses!`;
    document.querySelector('.guess-section').appendChild(message);
}

// Make handleSuggestionClick globally available for onclick events
window.handleSuggestionClick = handleSuggestionClick;

// Load saved state when the page loads
window.addEventListener('load', () => {
    loadSavedState();
    updateGuessGrid(); // Show any existing guesses
}); 
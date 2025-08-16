// Main Application Controller
class App {
    constructor() {
        this.api = apiService;
        this.manager = flashcardManager;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupKeyboardShortcuts();
        this.loadSavedState();
    }

    // Setup event listeners
    setupEventListeners() {
        // Generate button
        document.getElementById('generateBtn').addEventListener('click', () => this.generateFlashcards());
        
        // URL input enter key
        document.getElementById('youtubeUrl').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.generateFlashcards();
        });

        // Flashcard click to flip
        document.getElementById('flashcard').addEventListener('click', () => this.flipCard());

        // Navigation buttons
        document.getElementById('prevBtn').addEventListener('click', () => this.previousCard());
        document.getElementById('nextBtn').addEventListener('click', () => this.nextCard());
        document.getElementById('flipBtn').addEventListener('click', () => this.flipCard());

        // Control buttons
        document.getElementById('shuffleBtn').addEventListener('click', () => this.shuffleCards());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetProgress());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportCards());

        // Theme toggle
        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
    }

    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if (!this.manager.flashcardsData) return;

            switch(e.key.toLowerCase()) {
                case ' ':
                    e.preventDefault();
                    this.flipCard();
                    break;
                case 'arrowleft':
                    this.previousCard();
                    break;
                case 'arrowright':
                    this.nextCard();
                    break;
                case 'r':
                    if (!e.ctrlKey) this.resetProgress();
                    break;
                case 's':
                    if (!e.ctrlKey) this.shuffleCards();
                    break;
            }
        });
    }

    // Generate flashcards
    async generateFlashcards() {
        const urlInput = document.getElementById('youtubeUrl');
        const url = urlInput.value.trim();
        const numCards = document.getElementById('numCards').value;
        const difficulty = document.getElementById('difficulty').value;

        // Validate input
        if (!url) {
            this.showError('Please enter a YouTube URL');
            return;
        }

        if (!this.api.isValidYouTubeUrl(url)) {
            this.showError('Please enter a valid YouTube URL');
            return;
        }

        // Update UI
        this.hideMessages();
        this.showLoading(true);
        this.disableGenerateButton(true);

        try {
            // Call API
            const data = await this.api.generateFlashcards(url, numCards, difficulty);
            
            // Load flashcards
            this.manager.loadFlashcards(data);
            
            // Update UI
            this.displayFlashcards();
            this.showSuccess('Flashcards generated successfully!');
            
            // Save to local storage
            this.saveToLocalStorage(data);
            
        } catch (error) {
            console.error('Error generating flashcards:', error);
            this.showError(error.message || 'Failed to generate flashcards. Please try again.');
        } finally {
            this.showLoading(false);
            this.disableGenerateButton(false);
        }
    }

    // Display flashcards
    displayFlashcards() {
        const data = this.manager.flashcardsData;
        if (!data || !data.flashcards || data.flashcards.length === 0) {
            this.showError('No flashcards to display');
            return;
        }

        // Update video info
        document.getElementById('videoTitle').textContent = data.video_title || 'Untitled Video';
        document.getElementById('totalCards').textContent = `${data.flashcards.length} cards`;
        document.getElementById('videoLanguage').textContent = `Language: ${data.language || 'en'}`;
        
        // Set video thumbnail if available
        if (data.video_id) {
            const thumbnail = document.getElementById('videoThumbnail');
            thumbnail.style.backgroundImage = `url(${this.api.getVideoThumbnail(data.video_id)})`;
            thumbnail.style.backgroundSize = 'cover';
            thumbnail.style.backgroundPosition = 'center';
        }

        // Show study section
        document.getElementById('studySection').classList.remove('hidden');
        
        // Update card display
        this.updateCard();
    }

    // Update card display
    updateCard() {
        const card = this.manager.getCurrentCard();
        if (!card) return;

        // Update content
        document.getElementById('questionText').textContent = card.question;
        document.getElementById('answerText').textContent = card.answer;

        // Update difficulty badges
        const difficultyClass = `difficulty-${card.difficulty}`;
        const badges = ['difficultyBadge', 'difficultyBadgeBack'];
        badges.forEach(id => {
            const badge = document.getElementById(id);
            badge.className = `difficulty-badge ${difficultyClass}`;
            badge.textContent = card.difficulty.toUpperCase();
        });

        // Update progress
        const stats = this.manager.getStatistics();
        document.getElementById('progressText').textContent = 
            `Card ${stats.current} of ${stats.total}`;
        document.getElementById('progressFill').style.width = `${stats.progress}%`;

        // Update navigation buttons
        document.getElementById('prevBtn').disabled = this.manager.currentCardIndex === 0;
        document.getElementById('nextBtn').disabled = 
            this.manager.currentCardIndex === this.manager.flashcardsData.flashcards.length - 1;

        // Reset flip state
        const flashcard = document.getElementById('flashcard');
        if (flashcard.classList.contains('flipped')) {
            flashcard.classList.remove('flipped');
            this.manager.isFlipped = false;
        }
    }

    // Card navigation
    flipCard() {
        const flashcard = document.getElementById('flashcard');
        flashcard.classList.toggle('flipped');
        this.manager.flipCard();
    }

    nextCard() {
        if (this.manager.nextCard()) {
            this.updateCard();
        }
    }

    previousCard() {
        if (this.manager.previousCard()) {
            this.updateCard();
        }
    }

    shuffleCards() {
        this.manager.shuffleCards();
        this.updateCard();
        this.showSuccess('Cards shuffled!');
    }

    resetProgress() {
        this.manager.resetProgress();
        this.updateCard();
        this.showSuccess('Progress reset!');
    }

    // Export cards
    exportCards() {
        const format = 'json'; // Can be extended to support multiple formats
        const data = this.manager.exportFlashcards(format);
        
        if (!data) {
            this.showError('No flashcards to export');
            return;
        }

        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `flashcards-${this.manager.flashcardsData.video_id || 'export'}.json`;
        link.click();
        URL.revokeObjectURL(url);
        
        this.showSuccess('Flashcards exported successfully!');
    }

    // UI Helper Methods
    showLoading(show) {
        const loadingSection = document.getElementById('loadingSection');
        const generateBtn = document.getElementById('generateBtn');
        
        if (show) {
            loadingSection.classList.remove('hidden');
            generateBtn.querySelector('.btn-text').textContent = 'Generating...';
            generateBtn.querySelector('.spinner').classList.remove('hidden');
            generateBtn.querySelector('.btn-icon').classList.add('hidden');
        } else {
            loadingSection.classList.add('hidden');
            generateBtn.querySelector('.btn-text').textContent = 'Generate Flashcards';
            generateBtn.querySelector('.spinner').classList.add('hidden');
            generateBtn.querySelector('.btn-icon').classList.remove('hidden');
        }
    }

    disableGenerateButton(disable) {
        document.getElementById('generateBtn').disabled = disable;
    }

    showError(message) {
        const errorElement = document.getElementById('errorMessage');
        errorElement.textContent = message;
        errorElement.classList.remove('hidden');
        setTimeout(() => this.hideMessages(), 5000);
    }

    showSuccess(message) {
        const successElement = document.getElementById('successMessage');
        successElement.textContent = message;
        successElement.classList.remove('hidden');
        setTimeout(() => this.hideMessages(), 3000);
    }

    hideMessages() {
        document.getElementById('errorMessage').classList.add('hidden');
        document.getElementById('successMessage').classList.add('hidden');
    }

    // Theme management
    toggleTheme() {
        document.body.classList.toggle('dark-theme');
        const isDark = document.body.classList.contains('dark-theme');
        document.getElementById('themeToggle').textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }

    // Local storage
    saveToLocalStorage(data) {
        try {
            localStorage.setItem('lastFlashcards', JSON.stringify(data));
            localStorage.setItem('lastUrl', data.video_url);
        } catch (e) {
            console.error('Failed to save to local storage:', e);
        }
    }

    loadSavedState() {
        // Load theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
            document.getElementById('themeToggle').textContent = '☀️';
        }

        // Load last flashcards if available
        const savedFlashcards = localStorage.getItem('lastFlashcards');
        if (savedFlashcards) {
            try {
                const data = JSON.parse(savedFlashcards);
                this.manager.loadFlashcards(data);
                this.displayFlashcards();
            } catch (e) {
                console.error('Failed to load saved flashcards:', e);
            }
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
});
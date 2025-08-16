// Flashcard Manager Class
class FlashcardManager {
    constructor() {
        this.flashcardsData = null;
        this.currentCardIndex = 0;
        this.isFlipped = false;
        this.studyHistory = [];
    }

    // Load flashcards data
    loadFlashcards(data) {
        this.flashcardsData = data;
        this.currentCardIndex = 0;
        this.isFlipped = false;
        this.studyHistory = [];
        return this.flashcardsData;
    }

    // Get current card
    getCurrentCard() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) {
            return null;
        }
        return this.flashcardsData.flashcards[this.currentCardIndex];
    }

    // Navigate to next card
    nextCard() {
        if (this.currentCardIndex < this.flashcardsData.flashcards.length - 1) {
            this.currentCardIndex++;
            this.isFlipped = false;
            return true;
        }
        return false;
    }

    // Navigate to previous card
    previousCard() {
        if (this.currentCardIndex > 0) {
            this.currentCardIndex--;
            this.isFlipped = false;
            return true;
        }
        return false;
    }

    // Flip current card
    flipCard() {
        this.isFlipped = !this.isFlipped;
        return this.isFlipped;
    }

    // Shuffle cards
    shuffleCards() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) return;

        const cards = [...this.flashcardsData.flashcards];
        for (let i = cards.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [cards[i], cards[j]] = [cards[j], cards[i]];
        }
        this.flashcardsData.flashcards = cards;
        this.resetProgress();
    }

    // Reset progress
    resetProgress() {
        this.currentCardIndex = 0;
        this.isFlipped = false;
        this.studyHistory = [];
    }

    // Get progress percentage
    getProgress() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) {
            return 0;
        }
        return ((this.currentCardIndex + 1) / this.flashcardsData.flashcards.length) * 100;
    }

    // Get statistics
    getStatistics() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) {
            return null;
        }

        const cards = this.flashcardsData.flashcards;
        const difficulties = cards.reduce((acc, card) => {
            acc[card.difficulty] = (acc[card.difficulty] || 0) + 1;
            return acc;
        }, {});

        return {
            total: cards.length,
            current: this.currentCardIndex + 1,
            progress: this.getProgress(),
            difficulties: difficulties,
            completed: this.studyHistory.length,
            remaining: cards.length - this.studyHistory.length
        };
    }

    // Export flashcards
    exportFlashcards(format = 'json') {
        if (!this.flashcardsData) return null;

        switch (format) {
            case 'json':
                return JSON.stringify(this.flashcardsData, null, 2);
            
            case 'csv':
                return this.exportAsCSV();
            
            case 'anki':
                return this.exportAsAnki();
            
            default:
                return this.flashcardsData;
        }
    }

    // Export as CSV
    exportAsCSV() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) return '';

        const headers = ['Question', 'Answer', 'Difficulty', 'Topic'];
        const rows = this.flashcardsData.flashcards.map(card => [
            `"${card.question.replace(/"/g, '""')}"`,
            `"${card.answer.replace(/"/g, '""')}"`,
            card.difficulty,
            card.topic || ''
        ]);

        return [headers.join(','), ...rows.map(row => row.join(','))].join('\n');
    }

    // Export for Anki
    exportAsAnki() {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) return '';

        return this.flashcardsData.flashcards
            .map(card => `${card.question}\t${card.answer}\t${card.difficulty}`)
            .join('\n');
    }

    // Mark card as studied
    markAsStudied(cardIndex) {
        if (!this.studyHistory.includes(cardIndex)) {
            this.studyHistory.push(cardIndex);
        }
    }

    // Get cards by difficulty
    getCardsByDifficulty(difficulty) {
        if (!this.flashcardsData || !this.flashcardsData.flashcards) return [];
        
        return this.flashcardsData.flashcards.filter(
            card => card.difficulty === difficulty
        );
    }

    // Search cards
    searchCards(query) {
        if (!this.flashcardsData || !this.flashcardsData.flashcards || !query) return [];
        
        const searchTerm = query.toLowerCase();
        return this.flashcardsData.flashcards.filter(card => 
            card.question.toLowerCase().includes(searchTerm) ||
            card.answer.toLowerCase().includes(searchTerm) ||
            (card.topic && card.topic.toLowerCase().includes(searchTerm))
        );
    }
}

// Export for use
const flashcardManager = new FlashcardManager();
// API Configuration and Service
class APIService {
    constructor() {
        this.baseURL = 'http://localhost:8000/api/v1';
        this.headers = {
            'Content-Type': 'application/json',
        };
    }

    // Validate YouTube URL
    isValidYouTubeUrl(url) {
        const patterns = [
            /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|embed\/)|youtu\.be\/)[\w-]+/,
            /^(https?:\/\/)?(www\.)?youtube\.com\/watch\?.*v=[\w-]+/
        ];
        return patterns.some(pattern => pattern.test(url));
    }

    // Extract video ID from URL
    extractVideoId(url) {
        const match = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/);
        return match ? match[1] : null;
    }

    // Generate flashcards from YouTube video
    async generateFlashcards(youtubeUrl, numCards = 10, difficulty = 'mixed') {
        try {
            const response = await fetch(`${this.baseURL}/flashcards/generate`, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({
                    youtube_url: youtubeUrl,
                    num_cards: parseInt(numCards),
                    difficulty_level: difficulty
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Failed to generate flashcards');
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            
            // Return mock data for testing
            if (error.message.includes('Failed to fetch')) {
                console.log('Using mock data for testing');
                return this.getMockData(youtubeUrl);
            }
            
            throw error;
        }
    }

    // Mock data for testing
    getMockData(url) {
        const videoId = this.extractVideoId(url) || 'demo123';
        
        return {
            video_url: url,
            video_title: "Introduction to Machine Learning - Complete Guide",
            video_id: videoId,
            channel_name: "Tech Education",
            language: "en-US",
            duration: 1200,
            flashcards: [
                {
                    id: "1",
                    question: "What is machine learning?",
                    answer: "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
                    difficulty: "easy",
                    topic: "Fundamentals"
                },
                {
                    id: "2",
                    question: "What are the three main types of machine learning?",
                    answer: "The three main types are: 1) Supervised Learning - learning from labeled training data, 2) Unsupervised Learning - finding hidden patterns in unlabeled data, and 3) Reinforcement Learning - learning through interaction with an environment using rewards and penalties.",
                    difficulty: "medium",
                    topic: "ML Types"
                },
                {
                    id: "3",
                    question: "Explain the concept of overfitting in machine learning.",
                    answer: "Overfitting occurs when a model learns the training data too well, including its noise and outliers, resulting in poor generalization to new, unseen data. The model becomes too complex and captures patterns that don't actually exist in the broader dataset.",
                    difficulty: "hard",
                    topic: "Model Evaluation"
                },
                {
                    id: "4",
                    question: "What is a neural network?",
                    answer: "A neural network is a computational model inspired by the human brain, consisting of interconnected nodes (neurons) organized in layers. It processes information by passing signals through these layers, adjusting connection weights to learn patterns from data.",
                    difficulty: "medium",
                    topic: "Deep Learning"
                },
                {
                    id: "5",
                    question: "What is gradient descent?",
                    answer: "Gradient descent is an optimization algorithm used to minimize the loss function in machine learning models. It iteratively adjusts model parameters in the direction of steepest descent of the loss function, gradually finding the optimal values that minimize prediction errors.",
                    difficulty: "hard",
                    topic: "Optimization"
                },
                {
                    id: "6",
                    question: "What is the difference between training and test data?",
                    answer: "Training data is used to teach the model patterns and relationships, while test data is completely separate data used to evaluate the model's performance on unseen examples. This separation helps assess how well the model generalizes to new situations.",
                    difficulty: "easy",
                    topic: "Data Management"
                },
                {
                    id: "7",
                    question: "What is cross-validation?",
                    answer: "Cross-validation is a technique for assessing model performance by dividing data into multiple subsets, training on some subsets and validating on others. K-fold cross-validation is common, where data is split into k parts and the model is trained k times, each time using a different part for validation.",
                    difficulty: "medium",
                    topic: "Model Evaluation"
                },
                {
                    id: "8",
                    question: "Explain the bias-variance tradeoff.",
                    answer: "The bias-variance tradeoff is the balance between two types of errors: bias (error from oversimplified models) and variance (error from models too sensitive to training data). High bias leads to underfitting, high variance leads to overfitting. The goal is to find the sweet spot that minimizes both.",
                    difficulty: "hard",
                    topic: "Model Theory"
                },
                {
                    id: "9",
                    question: "What are features in machine learning?",
                    answer: "Features are individual measurable properties or characteristics of the data being observed. They are the input variables used by machine learning models to make predictions. Good feature selection and engineering are crucial for model performance.",
                    difficulty: "easy",
                    topic: "Data Preparation"
                },
                {
                    id: "10",
                    question: "What is regularization?",
                    answer: "Regularization is a technique used to prevent overfitting by adding a penalty term to the loss function. Common types include L1 regularization (Lasso) which can zero out features, and L2 regularization (Ridge) which shrinks coefficients. This helps create simpler, more generalizable models.",
                    difficulty: "medium",
                    topic: "Model Optimization"
                }
            ],
            transcript_preview: "Welcome to this comprehensive introduction to machine learning. Today we'll explore the fundamental concepts...",
            created_at: new Date().toISOString()
        };
    }

    // Get video thumbnail URL
    getVideoThumbnail(videoId) {
        return `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg`;
    }
}

// Export for use in other files
const apiService = new APIService();
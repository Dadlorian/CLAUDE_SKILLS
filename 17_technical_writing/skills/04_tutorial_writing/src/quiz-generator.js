/**
 * Automated Quiz Generator
 * Generates, manages, and scores quizzes for tutorial assessments
 */

class QuizGenerator {
  constructor() {
    this.quizzes = new Map();
    this.questionBank = new Map();
    this.userResponses = new Map();
    this.scoreHistory = new Map();
  }

  /**
   * Add questions to the question bank
   * @param {string} categoryId - Category identifier
   * @param {Array} questions - Array of question objects
   */
  addQuestionsToBank(categoryId, questions) {
    if (!this.questionBank.has(categoryId)) {
      this.questionBank.set(categoryId, []);
    }

    const validatedQuestions = questions.map((q) => ({
      id: q.id || this.generateQuestionId(),
      category: categoryId,
      type: q.type || 'multiple_choice', // multiple_choice, true_false, short_answer, coding
      difficulty: q.difficulty || 'intermediate', // beginner, intermediate, advanced
      question: q.question,
      options: q.options || [],
      correctAnswer: q.correctAnswer,
      explanation: q.explanation || '',
      tags: q.tags || [],
      points: q.points || 1,
      timeLimit: q.timeLimit || null, // seconds
      hints: q.hints || [],
    }));

    this.questionBank.get(categoryId).push(...validatedQuestions);
    return {
      success: true,
      message: `Added ${validatedQuestions.length} questions to ${categoryId}`,
      questions: validatedQuestions,
    };
  }

  /**
   * Generate a new quiz from the question bank
   * @param {string} quizId - Unique quiz identifier
   * @param {Object} config - Quiz configuration
   */
  generateQuiz(quizId, config) {
    const {
      categories = [],
      numberOfQuestions = 10,
      difficulty = 'mixed',
      randomize = true,
      timeLimit = null,
      passingScore = 70,
      shuffleOptions = true,
    } = config;

    // Collect eligible questions
    let eligibleQuestions = [];

    if (categories.length === 0) {
      // Use all categories
      for (const [, questions] of this.questionBank) {
        eligibleQuestions.push(...questions);
      }
    } else {
      for (const category of categories) {
        if (this.questionBank.has(category)) {
          eligibleQuestions.push(...this.questionBank.get(category));
        }
      }
    }

    // Filter by difficulty
    if (difficulty !== 'mixed') {
      eligibleQuestions = eligibleQuestions.filter(
        (q) => q.difficulty === difficulty
      );
    }

    // Select questions
    if (randomize) {
      eligibleQuestions = this.shuffleArray(eligibleQuestions);
    }

    const selectedQuestions = eligibleQuestions.slice(0, numberOfQuestions);

    if (selectedQuestions.length < numberOfQuestions) {
      return {
        success: false,
        message: `Only ${selectedQuestions.length} questions available`,
      };
    }

    // Shuffle options if enabled
    const quizQuestions = selectedQuestions.map((q) => {
      const question = { ...q };
      if (shuffleOptions && question.options.length > 0) {
        question.displayOptions = this.shuffleArray([...question.options]);
      }
      return question;
    });

    const quiz = {
      id: quizId,
      createdAt: new Date(),
      config: {
        numberOfQuestions,
        difficulty,
        timeLimit,
        passingScore,
      },
      questions: quizQuestions,
      status: 'active',
      attempts: [],
    };

    this.quizzes.set(quizId, quiz);

    return {
      success: true,
      quiz: {
        id: quizId,
        numberOfQuestions: quizQuestions.length,
        totalPoints: quizQuestions.reduce((sum, q) => sum + q.points, 0),
        timeLimit,
        passingScore,
      },
    };
  }

  /**
   * Submit quiz responses and calculate score
   * @param {string} quizId - Quiz identifier
   * @param {string} userId - User identifier
   * @param {Array} responses - Array of user responses
   */
  submitQuizResponses(quizId, userId, responses) {
    if (!this.quizzes.has(quizId)) {
      return { success: false, message: 'Quiz not found' };
    }

    const quiz = this.quizzes.get(quizId);
    const scoring = {
      userId,
      quizId,
      submittedAt: new Date(),
      responses: [],
      totalPoints: 0,
      earnedPoints: 0,
      correctAnswers: 0,
      totalQuestions: quiz.questions.length,
    };

    // Grade each response
    for (let i = 0; i < quiz.questions.length; i++) {
      const question = quiz.questions[i];
      const userResponse = responses[i];

      const graded = this.gradeQuestion(question, userResponse);

      scoring.responses.push({
        questionId: question.id,
        question: question.question,
        type: question.type,
        userAnswer: userResponse?.answer || null,
        correctAnswer: question.correctAnswer,
        isCorrect: graded.correct,
        points: graded.points,
        explanation: question.explanation,
        feedback: graded.feedback,
      });

      scoring.totalPoints += question.points;
      scoring.earnedPoints += graded.points;

      if (graded.correct) {
        scoring.correctAnswers += 1;
      }
    }

    // Calculate score percentage
    scoring.scorePercentage =
      (scoring.earnedPoints / scoring.totalPoints) * 100;
    scoring.passed = scoring.scorePercentage >= quiz.config.passingScore;

    // Store attempt
    if (!quiz.attempts) {
      quiz.attempts = [];
    }
    quiz.attempts.push(scoring);

    // Store user responses
    if (!this.userResponses.has(userId)) {
      this.userResponses.set(userId, []);
    }
    this.userResponses.get(userId).push(scoring);

    // Track score history
    if (!this.scoreHistory.has(userId)) {
      this.scoreHistory.set(userId, []);
    }
    this.scoreHistory.get(userId).push({
      quizId,
      score: scoring.scorePercentage,
      passed: scoring.passed,
      date: scoring.submittedAt,
    });

    return {
      success: true,
      scoring: {
        earnedPoints: scoring.earnedPoints,
        totalPoints: scoring.totalPoints,
        percentage: scoring.scorePercentage.toFixed(2),
        passed: scoring.passed,
        correctAnswers: scoring.correctAnswers,
        totalQuestions: scoring.totalQuestions,
        feedback: this.generateFeedback(scoring),
      },
      detailedResults: scoring.responses,
    };
  }

  /**
   * Grade a single question
   */
  gradeQuestion(question, userResponse) {
    const response = userResponse?.answer;

    if (!response) {
      return {
        correct: false,
        points: 0,
        feedback: 'No answer provided',
      };
    }

    const correct =
      response.toString().toLowerCase() ===
      question.correctAnswer.toString().toLowerCase();

    return {
      correct,
      points: correct ? question.points : 0,
      feedback: correct ? 'Correct!' : 'Incorrect',
    };
  }

  /**
   * Generate feedback based on scoring results
   */
  generateFeedback(scoring) {
    const percentage = scoring.scorePercentage;

    if (percentage === 100) {
      return 'Perfect score! Excellent understanding of the material.';
    } else if (percentage >= 90) {
      return 'Outstanding performance! Minor areas for review.';
    } else if (percentage >= 80) {
      return 'Good understanding. Review the incorrect answers for deeper learning.';
    } else if (percentage >= 70) {
      return 'Passing score achieved. Consider reviewing key concepts.';
    } else if (percentage >= 50) {
      return 'Needs improvement. Review the material and try again.';
    } else {
      return 'Significant gaps identified. Recommend reviewing the full tutorial before retrying.';
    }
  }

  /**
   * Get quiz results for a user
   */
  getUserQuizResults(userId, limit = 10) {
    if (!this.userResponses.has(userId)) {
      return { success: false, message: 'No quiz results found for user' };
    }

    const results = this.userResponses
      .get(userId)
      .slice(-limit)
      .sort((a, b) => new Date(b.submittedAt) - new Date(a.submittedAt));

    return {
      success: true,
      totalAttempts: this.userResponses.get(userId).length,
      results,
      summary: this.calculateUserSummary(userId),
    };
  }

  /**
   * Calculate user quiz summary statistics
   */
  calculateUserSummary(userId) {
    if (!this.userResponses.has(userId)) {
      return null;
    }

    const responses = this.userResponses.get(userId);
    const scores = responses.map((r) => r.scorePercentage);
    const passedQuizzes = responses.filter((r) => r.passed).length;

    return {
      totalAttempts: responses.length,
      passedAttempts: passedQuizzes,
      passRate: ((passedQuizzes / responses.length) * 100).toFixed(2),
      averageScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(
        2
      ),
      highestScore: Math.max(...scores).toFixed(2),
      lowestScore: Math.min(...scores).toFixed(2),
      lastAttempt: responses[responses.length - 1].submittedAt,
    };
  }

  /**
   * Create a custom quiz with specific questions
   */
  createCustomQuiz(quizId, questionIds) {
    const questions = [];

    for (const qId of questionIds) {
      let found = false;
      for (const [, categoryQuestions] of this.questionBank) {
        const q = categoryQuestions.find((q) => q.id === qId);
        if (q) {
          questions.push(q);
          found = true;
          break;
        }
      }
      if (!found) {
        return { success: false, message: `Question ${qId} not found` };
      }
    }

    const quiz = {
      id: quizId,
      createdAt: new Date(),
      questions,
      status: 'active',
      attempts: [],
    };

    this.quizzes.set(quizId, quiz);

    return {
      success: true,
      quiz: {
        id: quizId,
        numberOfQuestions: questions.length,
        totalPoints: questions.reduce((sum, q) => sum + q.points, 0),
      },
    };
  }

  /**
   * Generate quiz analytics
   */
  generateQuizAnalytics(quizId) {
    if (!this.quizzes.has(quizId)) {
      return { success: false, message: 'Quiz not found' };
    }

    const quiz = this.quizzes.get(quizId);
    const attempts = quiz.attempts || [];

    if (attempts.length === 0) {
      return {
        success: true,
        message: 'No attempts yet',
        analytics: null,
      };
    }

    const scores = attempts.map((a) => a.scorePercentage);
    const questionAnalytics = new Map();

    // Analyze each question
    for (const question of quiz.questions) {
      const questionAttempts = attempts.map((a) =>
        a.responses.find((r) => r.questionId === question.id)
      );

      const correctAttempts = questionAttempts.filter(
        (a) => a && a.isCorrect
      ).length;

      questionAnalytics.set(question.id, {
        question: question.question,
        totalAttempts: questionAttempts.length,
        correctAnswers: correctAttempts,
        successRate: ((correctAttempts / questionAttempts.length) * 100).toFixed(
          2
        ),
        difficulty: question.difficulty,
        commonMistakes: this.findCommonMistakes(questionAttempts),
      });
    }

    return {
      success: true,
      analytics: {
        totalAttempts: attempts.length,
        averageScore: (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(
          2
        ),
        highestScore: Math.max(...scores),
        lowestScore: Math.min(...scores),
        passRate: (
          (attempts.filter((a) => a.passed).length / attempts.length) *
          100
        ).toFixed(2),
        questionAnalytics: Object.fromEntries(questionAnalytics),
      },
    };
  }

  /**
   * Find common mistakes in question responses
   */
  findCommonMistakes(attempts) {
    const mistakes = {};

    attempts.forEach((attempt) => {
      if (attempt && !attempt.isCorrect) {
        const answer = attempt.userAnswer;
        mistakes[answer] = (mistakes[answer] || 0) + 1;
      }
    });

    return Object.entries(mistakes)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([answer, count]) => ({ answer, frequency: count }));
  }

  /**
   * Utility: Generate unique question ID
   */
  generateQuestionId() {
    return `q_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Utility: Shuffle array
   */
  shuffleArray(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  /**
   * Export quiz data
   */
  exportQuizData(quizId, format = 'json') {
    if (!this.quizzes.has(quizId)) {
      return { success: false, message: 'Quiz not found' };
    }

    const quiz = this.quizzes.get(quizId);

    if (format === 'json') {
      return {
        success: true,
        data: JSON.stringify(quiz, null, 2),
        format: 'json',
      };
    }

    if (format === 'csv') {
      // Convert to CSV
      let csv = 'Question,Type,Difficulty,Points\n';
      quiz.questions.forEach((q) => {
        csv += `"${q.question}",${q.type},${q.difficulty},${q.points}\n`;
      });

      return {
        success: true,
        data: csv,
        format: 'csv',
      };
    }

    return { success: false, message: 'Unsupported format' };
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = QuizGenerator;
}

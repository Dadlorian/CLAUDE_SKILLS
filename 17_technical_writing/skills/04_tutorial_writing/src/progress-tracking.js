/**
 * Learning Progress Tracker
 * Comprehensive system for tracking and analyzing student learning progress
 */

class ProgressTracker {
  constructor() {
    this.userProgress = new Map();
    this.learningPaths = new Map();
    this.milestones = new Map();
    this.assessments = new Map();
    this.achievements = new Map();
  }

  /**
   * Initialize user progress tracking
   * @param {string} userId - Unique user identifier
   * @param {string} courseId - Course identifier
   */
  initializeUserProgress(userId, courseId) {
    const progress = {
      userId,
      courseId,
      startDate: new Date(),
      modules: new Map(),
      quizzes: new Map(),
      labs: new Map(),
      totalProgress: 0,
      estimatedCompletion: null,
      status: 'in_progress',
      milestones: [],
      achievements: [],
    };

    this.userProgress.set(userId, progress);

    return {
      success: true,
      message: `User ${userId} enrolled in course ${courseId}`,
      progress,
    };
  }

  /**
   * Define learning path structure
   * @param {string} pathId - Learning path identifier
   * @param {Object} config - Path configuration
   */
  defineLearningPath(pathId, config) {
    const {
      name,
      description,
      totalModules,
      estimatedHours,
      difficultyLevel,
      modules = [],
    } = config;

    const learningPath = {
      id: pathId,
      name,
      description,
      totalModules,
      estimatedHours,
      difficultyLevel,
      modules: modules.map((m) => ({
        id: m.id,
        name: m.name,
        duration: m.duration,
        order: m.order,
        required: m.required !== false,
        quizzes: m.quizzes || [],
        labs: m.labs || [],
        readings: m.readings || [],
      })),
      createdAt: new Date(),
    };

    this.learningPaths.set(pathId, learningPath);

    return {
      success: true,
      message: `Learning path ${pathId} created`,
      learningPath,
    };
  }

  /**
   * Track module completion
   * @param {string} userId - User identifier
   * @param {string} courseId - Course identifier
   * @param {string} moduleId - Module identifier
   */
  trackModuleCompletion(userId, courseId, moduleId) {
    if (!this.userProgress.has(userId)) {
      return {
        success: false,
        message: 'User not found',
      };
    }

    const userProgress = this.userProgress.get(userId);

    if (!userProgress.modules.has(moduleId)) {
      userProgress.modules.set(moduleId, {
        id: moduleId,
        startDate: new Date(),
        completionDate: null,
        duration: 0,
        status: 'in_progress',
        assessments: [],
        score: null,
      });
    }

    const module = userProgress.modules.get(moduleId);
    module.completionDate = new Date();
    module.status = 'completed';
    module.duration = Math.round(
      (module.completionDate - module.startDate) / (1000 * 60)
    ); // minutes

    this.updateOverallProgress(userId);

    return {
      success: true,
      message: `Module ${moduleId} marked as completed`,
      module,
    };
  }

  /**
   * Record quiz attempt and score
   * @param {string} userId - User identifier
   * @param {string} quizId - Quiz identifier
   * @param {number} score - Quiz score (0-100)
   * @param {Object} details - Additional attempt details
   */
  recordQuizAttempt(userId, quizId, score, details = {}) {
    if (!this.userProgress.has(userId)) {
      return {
        success: false,
        message: 'User not found',
      };
    }

    const userProgress = this.userProgress.get(userId);
    const attempt = {
      attemptNumber: (userProgress.quizzes.get(quizId)?.attempts || 0) + 1,
      score,
      date: new Date(),
      timeSpent: details.timeSpent || null,
      questionsCorrect: details.questionsCorrect || null,
      totalQuestions: details.totalQuestions || null,
      passed: score >= (details.passingScore || 70),
      details,
    };

    if (!userProgress.quizzes.has(quizId)) {
      userProgress.quizzes.set(quizId, {
        id: quizId,
        attempts: [],
        bestScore: score,
        averageScore: score,
      });
    }

    const quiz = userProgress.quizzes.get(quizId);
    quiz.attempts.push(attempt);
    quiz.bestScore = Math.max(quiz.bestScore, score);
    quiz.averageScore =
      quiz.attempts.reduce((sum, a) => sum + a.score, 0) / quiz.attempts.length;
    quiz.passed = quiz.bestScore >= (details.passingScore || 70);

    this.updateOverallProgress(userId);

    return {
      success: true,
      attempt,
      quiz,
    };
  }

  /**
   * Record hands-on lab completion
   * @param {string} userId - User identifier
   * @param {string} labId - Lab identifier
   * @param {Object} submission - Lab submission details
   */
  recordLabCompletion(userId, labId, submission) {
    if (!this.userProgress.has(userId)) {
      return {
        success: false,
        message: 'User not found',
      };
    }

    const userProgress = this.userProgress.get(userId);
    const labRecord = {
      id: labId,
      completionDate: new Date(),
      status: 'completed',
      submissionLink: submission.link || null,
      score: submission.score || null,
      feedback: submission.feedback || '',
      timeSpent: submission.timeSpent || null, // minutes
      testsPassed: submission.testsPassed || 0,
      totalTests: submission.totalTests || 0,
      codeQuality: submission.codeQuality || null, // 1-5
      documentation: submission.documentation || false,
    };

    if (!userProgress.labs.has(labId)) {
      userProgress.labs.set(labId, []);
    }

    userProgress.labs.get(labId).push(labRecord);
    this.updateOverallProgress(userId);

    return {
      success: true,
      labRecord,
    };
  }

  /**
   * Update overall progress percentage
   */
  updateOverallProgress(userId) {
    const userProgress = this.userProgress.get(userId);

    const completedModules = Array.from(userProgress.modules.values()).filter(
      (m) => m.status === 'completed'
    ).length;

    const completedQuizzes = Array.from(userProgress.quizzes.values()).filter(
      (q) => q.passed
    ).length;

    const completedLabs = Array.from(userProgress.labs.values()).filter(
      (labs) => labs.length > 0
    ).length;

    const totalItems =
      (userProgress.modules.size || 1) +
      (userProgress.quizzes.size || 1) +
      (userProgress.labs.size || 1);

    const completedItems = completedModules + completedQuizzes + completedLabs;
    userProgress.totalProgress =
      Math.round((completedItems / totalItems) * 100) || 0;

    return userProgress.totalProgress;
  }

  /**
   * Define milestone achievements
   * @param {string} milestoneId - Milestone identifier
   * @param {Object} config - Milestone configuration
   */
  defineMilestone(milestoneId, config) {
    const {
      name,
      description,
      condition,
      rewardPoints = 100,
      icon = 'achievement',
    } = config;

    const milestone = {
      id: milestoneId,
      name,
      description,
      condition,
      rewardPoints,
      icon,
      createdAt: new Date(),
    };

    this.milestones.set(milestoneId, milestone);

    return {
      success: true,
      milestone,
    };
  }

  /**
   * Check and award milestones
   */
  checkMilestones(userId) {
    const userProgress = this.userProgress.get(userId);
    if (!userProgress) {
      return { success: false, message: 'User not found' };
    }

    const newAchievements = [];

    for (const [milestoneId, milestone] of this.milestones) {
      // Check if already achieved
      if (
        userProgress.milestones.some((m) => m.id === milestoneId)
      ) {
        continue;
      }

      // Evaluate condition
      if (this.evaluateMilestoneCondition(userId, milestone)) {
        const achievement = {
          id: milestoneId,
          name: milestone.name,
          earnedDate: new Date(),
          points: milestone.rewardPoints,
        };

        userProgress.milestones.push(achievement);
        newAchievements.push(achievement);
      }
    }

    return {
      success: true,
      newAchievements,
      totalPoints: userProgress.milestones.reduce(
        (sum, a) => sum + a.points,
        0
      ),
    };
  }

  /**
   * Evaluate milestone condition
   */
  evaluateMilestoneCondition(userId, milestone) {
    const userProgress = this.userProgress.get(userId);
    const condition = milestone.condition;

    if (condition.type === 'modules_completed') {
      const completed = Array.from(userProgress.modules.values()).filter(
        (m) => m.status === 'completed'
      ).length;
      return completed >= condition.value;
    }

    if (condition.type === 'quiz_passed') {
      const passed = Array.from(userProgress.quizzes.values()).filter(
        (q) => q.passed
      ).length;
      return passed >= condition.value;
    }

    if (condition.type === 'perfect_score') {
      const quiz = userProgress.quizzes.get(condition.quizId);
      return quiz && quiz.bestScore === 100;
    }

    if (condition.type === 'labs_completed') {
      const completed = Array.from(userProgress.labs.values()).filter(
        (labs) => labs.length > 0
      ).length;
      return completed >= condition.value;
    }

    if (condition.type === 'progress_percentage') {
      return userProgress.totalProgress >= condition.value;
    }

    return false;
  }

  /**
   * Get comprehensive progress report
   */
  getProgressReport(userId) {
    const userProgress = this.userProgress.get(userId);

    if (!userProgress) {
      return { success: false, message: 'User not found' };
    }

    const modulesCompleted = Array.from(userProgress.modules.values()).filter(
      (m) => m.status === 'completed'
    );

    const quizzesAttempted = Array.from(userProgress.quizzes.values());

    const quizzesPassed = quizzesAttempted.filter((q) => q.passed);

    const labsCompleted = Array.from(userProgress.labs.values()).filter(
      (labs) => labs.length > 0
    );

    const averageQuizScore =
      quizzesAttempted.length > 0
        ? (quizzesAttempted.reduce((sum, q) => sum + q.bestScore, 0) /
            quizzesAttempted.length).toFixed(2)
        : 0;

    const totalTimeSpent = this.calculateTotalTimeSpent(userProgress);

    const estimatedCompletion = this.estimateCompletionDate(userProgress);

    return {
      success: true,
      summary: {
        userId: userProgress.userId,
        enrollmentDate: userProgress.startDate,
        currentProgress: userProgress.totalProgress,
        status: userProgress.status,
      },
      modules: {
        completed: modulesCompleted.length,
        total: userProgress.modules.size,
        completionRate: (
          (modulesCompleted.length / (userProgress.modules.size || 1)) *
          100
        ).toFixed(2),
      },
      quizzes: {
        attempted: quizzesAttempted.length,
        passed: quizzesPassed.length,
        averageScore: parseFloat(averageQuizScore),
        highestScore: Math.max(
          ...quizzesAttempted.map((q) => q.bestScore),
          0
        ),
      },
      labs: {
        completed: labsCompleted.length,
        total: userProgress.labs.size,
      },
      achievements: {
        total: userProgress.milestones.length,
        points: userProgress.milestones.reduce((sum, a) => sum + a.points, 0),
        list: userProgress.milestones,
      },
      timeTracking: {
        totalMinutes: totalTimeSpent,
        totalHours: (totalTimeSpent / 60).toFixed(2),
        estimatedCompletion,
      },
    };
  }

  /**
   * Calculate total time spent
   */
  calculateTotalTimeSpent(userProgress) {
    let total = 0;

    // Module time
    for (const module of userProgress.modules.values()) {
      if (module.duration) {
        total += module.duration;
      }
    }

    // Quiz time
    for (const quiz of userProgress.quizzes.values()) {
      for (const attempt of quiz.attempts) {
        if (attempt.timeSpent) {
          total += attempt.timeSpent;
        }
      }
    }

    // Lab time
    for (const labs of userProgress.labs.values()) {
      for (const lab of labs) {
        if (lab.timeSpent) {
          total += lab.timeSpent;
        }
      }
    }

    return total;
  }

  /**
   * Estimate completion date
   */
  estimateCompletionDate(userProgress) {
    const now = new Date();
    const daysSinceStart = Math.floor(
      (now - userProgress.startDate) / (1000 * 60 * 60 * 24)
    );

    if (daysSinceStart === 0) {
      return null;
    }

    const progressPerDay = userProgress.totalProgress / daysSinceStart;
    const remainingProgress = 100 - userProgress.totalProgress;
    const estimatedDaysRemaining = Math.ceil(remainingProgress / progressPerDay);

    const estimatedDate = new Date(now);
    estimatedDate.setDate(estimatedDate.getDate() + estimatedDaysRemaining);

    return estimatedDate;
  }

  /**
   * Get learning analytics
   */
  getLearningAnalytics(userId) {
    const userProgress = this.userProgress.get(userId);

    if (!userProgress) {
      return { success: false, message: 'User not found' };
    }

    const quizzes = Array.from(userProgress.quizzes.values());
    const quizScores = quizzes.flatMap((q) => q.attempts.map((a) => a.score));

    const modules = Array.from(userProgress.modules.values());
    const moduleTimings = modules
      .filter((m) => m.duration)
      .map((m) => m.duration);

    return {
      success: true,
      analytics: {
        quiz: {
          averageScore: (
            quizScores.reduce((a, b) => a + b, 0) / quizScores.length
          ).toFixed(2),
          medianScore: this.calculateMedian(quizScores),
          stdDeviation: this.calculateStdDev(quizScores),
          improvementTrend: this.calculateTrend(
            quizzes.flatMap((q) =>
              q.attempts.map((a) => ({ score: a.score, date: a.date }))
            )
          ),
        },
        modules: {
          averageTimePerModule: (
            moduleTimings.reduce((a, b) => a + b, 0) / moduleTimings.length
          ).toFixed(2),
          fastestModule: Math.min(...moduleTimings),
          slowestModule: Math.max(...moduleTimings),
        },
        engagement: {
          consistencyScore: this.calculateConsistency(userProgress),
          estimatedPaceChange: this.estimatePaceChange(userProgress),
        },
      },
    };
  }

  /**
   * Calculate median value
   */
  calculateMedian(values) {
    if (values.length === 0) return 0;
    values.sort((a, b) => a - b);
    const mid = Math.floor(values.length / 2);
    return values.length % 2 !== 0
      ? values[mid]
      : ((values[mid - 1] + values[mid]) / 2).toFixed(2);
  }

  /**
   * Calculate standard deviation
   */
  calculateStdDev(values) {
    if (values.length === 0) return 0;
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance =
      values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) /
      values.length;
    return Math.sqrt(variance).toFixed(2);
  }

  /**
   * Calculate learning trend
   */
  calculateTrend(attempts) {
    if (attempts.length < 2) return 'insufficient_data';

    const early = attempts.slice(0, Math.ceil(attempts.length / 3));
    const late = attempts.slice(-Math.ceil(attempts.length / 3));

    const earlyAvg =
      early.reduce((sum, a) => sum + a.score, 0) / early.length;
    const lateAvg = late.reduce((sum, a) => sum + a.score, 0) / late.length;

    if (lateAvg > earlyAvg + 5) return 'improving';
    if (lateAvg < earlyAvg - 5) return 'declining';
    return 'stable';
  }

  /**
   * Calculate consistency score
   */
  calculateConsistency(userProgress) {
    const modules = Array.from(userProgress.modules.values());
    const completionDates = modules
      .filter((m) => m.completionDate)
      .map((m) => new Date(m.completionDate));

    if (completionDates.length < 2) return 'insufficient_data';

    // Calculate days between completions
    const intervals = [];
    for (let i = 1; i < completionDates.length; i++) {
      intervals.push(
        (completionDates[i] - completionDates[i - 1]) / (1000 * 60 * 60 * 24)
      );
    }

    const avgInterval =
      intervals.reduce((a, b) => a + b, 0) / intervals.length;
    const variance =
      intervals.reduce((sum, val) => sum + Math.pow(val - avgInterval, 2), 0) /
      intervals.length;
    const stdDev = Math.sqrt(variance);

    // Lower variance = higher consistency
    return (100 - Math.min(stdDev * 10, 100)).toFixed(2);
  }

  /**
   * Estimate pace change
   */
  estimatePaceChange(userProgress) {
    const modules = Array.from(userProgress.modules.values()).filter(
      (m) => m.duration
    );

    if (modules.length < 4) return 'insufficient_data';

    const firstHalf = modules
      .slice(0, Math.ceil(modules.length / 2))
      .map((m) => m.duration);
    const secondHalf = modules
      .slice(Math.ceil(modules.length / 2))
      .map((m) => m.duration);

    const avgFirstHalf =
      firstHalf.reduce((a, b) => a + b, 0) / firstHalf.length;
    const avgSecondHalf =
      secondHalf.reduce((a, b) => a + b, 0) / secondHalf.length;

    const percentChange =
      ((avgSecondHalf - avgFirstHalf) / avgFirstHalf) * 100;

    if (percentChange > 10) return 'slowing_down';
    if (percentChange < -10) return 'speeding_up';
    return 'consistent_pace';
  }

  /**
   * Generate comparison report between multiple users
   */
  generateCohortReport(userIds) {
    const cohortData = userIds
      .map((userId) => this.getProgressReport(userId))
      .filter((r) => r.success);

    if (cohortData.length === 0) {
      return {
        success: false,
        message: 'No valid user data found',
      };
    }

    const progressValues = cohortData.map((r) => r.summary.currentProgress);
    const quizScores = cohortData
      .map((r) => r.quizzes.averageScore)
      .filter((s) => s > 0);

    return {
      success: true,
      cohort: {
        totalUsers: userIds.length,
        activeUsers: cohortData.length,
        averageProgress: (
          progressValues.reduce((a, b) => a + b, 0) / progressValues.length
        ).toFixed(2),
        medianProgress: this.calculateMedian(progressValues),
        averageQuizScore: (
          quizScores.reduce((a, b) => a + b, 0) / quizScores.length
        ).toFixed(2),
        completionRate: (
          (cohortData.filter((r) => r.summary.status === 'completed').length /
            cohortData.length) *
          100
        ).toFixed(2),
      },
      topPerformers: cohortData
        .sort((a, b) => b.summary.currentProgress - a.summary.currentProgress)
        .slice(0, 5)
        .map((r) => ({
          userId: r.summary.userId,
          progress: r.summary.currentProgress,
        })),
      needsSupport: cohortData
        .sort((a, b) => a.summary.currentProgress - b.summary.currentProgress)
        .slice(0, 5)
        .map((r) => ({
          userId: r.summary.userId,
          progress: r.summary.currentProgress,
        })),
    };
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ProgressTracker;
}

/**
 * Patient Education Content Delivery System
 * Manages education modules, tracking, and recommendations
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

class EducationContentService {
  async loadEducationContent(condition) {
    const response = await axios.get(
      `/api/education/content?condition=${condition}`
    );
    return response.data;
  }

  async trackContentCompletion(contentId, contentType, completionTime) {
    await axios.post('/api/education/progress', {
      content_id: contentId,
      content_type: contentType,
      completed_at: new Date().toISOString(),
      time_spent: completionTime
    });
  }

  async getPersonalizedRecommendations(userId) {
    const response = await axios.get(
      `/api/education/recommendations?user_id=${userId}`
    );
    return response.data;
  }

  async recordQuizCompletion(quizId, score, answers) {
    await axios.post('/api/education/quiz-results', {
      quiz_id: quizId,
      score: score,
      answers: answers,
      completed_at: new Date().toISOString()
    });
  }
}

const EducationModule = ({ moduleId, title, lessons }) => {
  const [currentLessonIndex, setCurrentLessonIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  const currentLesson = lessons[currentLessonIndex];

  const handleLessonComplete = async () => {
    const newProgress = ((currentLessonIndex + 1) / lessons.length) * 100;
    setProgress(newProgress);

    if (currentLessonIndex < lessons.length - 1) {
      setCurrentLessonIndex(currentLessonIndex + 1);
    } else {
      // Module complete
      await trackModuleCompletion();
    }
  };

  const trackModuleCompletion = async () => {
    const service = new EducationContentService();
    await service.trackContentCompletion(moduleId, 'module', 0);
  };

  return (
    <div className="education-module">
      <h2>{title}</h2>
      <div className="progress-bar">
        <div className="progress" style={{ width: `${progress}%` }}></div>
      </div>

      <LessonContent lesson={currentLesson} />

      <div className="lesson-controls">
        <button
          disabled={currentLessonIndex === 0}
          onClick={() => setCurrentLessonIndex(Math.max(0, currentLessonIndex - 1))}
        >
          Previous
        </button>

        <button onClick={handleLessonComplete}>
          {currentLessonIndex === lessons.length - 1 ? 'Complete' : 'Next'}
        </button>
      </div>
    </div>
  );
};

const LessonContent = ({ lesson }) => {
  return (
    <div className="lesson-content">
      <h3>{lesson.title}</h3>

      {lesson.video && (
        <video controls style={{ width: '100%', maxWidth: '500px' }}>
          <source src={lesson.video} type="video/mp4" />
        </video>
      )}

      {lesson.content && (
        <div className="lesson-text">
          {lesson.content}
        </div>
      )}

      {lesson.infographic && (
        <img src={lesson.infographic} alt="Infographic" style={{ maxWidth: '100%' }} />
      )}

      {lesson.quiz && (
        <Quiz quiz={lesson.quiz} />
      )}
    </div>
  );
};

const Quiz = ({ quiz }) => {
  const [answers, setAnswers] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [score, setScore] = useState(0);

  const handleSubmit = () => {
    // Calculate score
    let correctCount = 0;
    quiz.questions.forEach((q, index) => {
      if (answers[index] === q.correct_answer) {
        correctCount++;
      }
    });

    const quizScore = (correctCount / quiz.questions.length) * 100;
    setScore(quizScore);
    setSubmitted(true);
  };

  return (
    <div className="quiz">
      <h4>{quiz.title}</h4>
      {quiz.questions.map((question, index) => (
        <div key={index} className="question">
          <p>{question.text}</p>
          {question.options.map((option, optIndex) => (
            <label key={optIndex}>
              <input
                type="radio"
                name={`q${index}`}
                value={optIndex}
                disabled={submitted}
                onChange={(e) => {
                  const newAnswers = { ...answers };
                  newAnswers[index] = parseInt(e.target.value);
                  setAnswers(newAnswers);
                }}
              />
              {option}
            </label>
          ))}
        </div>
      ))}

      {!submitted ? (
        <button onClick={handleSubmit}>Submit Quiz</button>
      ) : (
        <div className="quiz-results">
          <p className="score">Score: {score.toFixed(0)}%</p>
          {score >= 80 ? (
            <p className="success">Congratulations! You passed the quiz.</p>
          ) : (
            <p className="retry">Review the material and try again.</p>
          )}
        </div>
      )}
    </div>
  );
};

export { EducationModule, EducationContentService };

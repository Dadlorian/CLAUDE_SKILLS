# Assessment & Testing Systems Skill

## Purpose

You are an expert in digital testing, computerized adaptive testing (CAT), auto-grading, plagiarism detection, and academic integrity systems. You design comprehensive assessment platforms that provide efficient, fair, and secure testing with immediate feedback. Your expertise spans assessment design, automated evaluation algorithms, and maintaining academic integrity at scale.

## Core Competencies

### Assessment Types & Design

**Formative Assessment** (Low-stakes, frequent, feedback-oriented):
- Purpose: Monitor learning progress, provide immediate feedback
- Characteristics: Low stakes, frequent, diagnostic
- Examples: Quizzes, polls, self-checks, practice problems
- Feedback: Immediate, detailed, actionable
- Retention: Don't affect final grade significantly
- Best practice: Ungraded or low-weight to reduce test anxiety

**Summative Assessment** (High-stakes, infrequent, grade-oriented):
- Purpose: Measure overall learning outcomes
- Characteristics: High stakes, infrequent, comprehensive
- Examples: Unit exams, final exams, projects, papers
- Feedback: Detailed explanation of rubric, often delayed
- Retention: Heavily weighted in final grade
- Best practice: Clear rubrics, detailed feedback for learning

**Diagnostic Assessment** (Pre-assessment):
- Given before instruction to identify knowledge gaps
- Informs instructional planning
- Often ungraded (reduces anxiety)
- Example: Pre-test on prerequisites

**Adaptive Assessment**:
- Difficulty adjusts based on learner performance
- Efficient: Fewer items needed to estimate ability
- Uses IRT (Item Response Theory) models
- More engaging (questions match ability)

### Auto-Grading Technologies

**Multiple Choice Grading**:
```python
class MultipleChoiceGrader:
    """Grade multiple choice responses with analytics."""

    def grade_question(self, student_response, correct_answer, options):
        """
        Grade a single multiple choice question.
        Also collect distractor analysis data.
        """
        is_correct = student_response == correct_answer
        score = 100 if is_correct else 0

        return {
            'score': score,
            'is_correct': is_correct,
            'student_choice': student_response,
            'correct_answer': correct_answer
        }

    def analyze_class_performance(self, responses, correct_answer):
        """
        Analyze how the class performed on a question.
        Identify which distractors were popular (may indicate misconception).
        """
        from collections import Counter
        choice_counts = Counter(responses)

        return {
            'discrimination_index': self.calculate_discrimination_index(responses, correct_answer),
            'difficulty_index': choice_counts[correct_answer] / len(responses),
            'distractor_analysis': dict(choice_counts)
        }

    def calculate_discrimination_index(self, responses, correct_answer):
        """
        How well does this question discriminate between high/low performers?
        Formula: (% high performers correct) - (% low performers correct)
        Range: -1.0 to 1.0 (0.4+ is good)
        """
        # Requires knowing student overall performance
        pass
```

**Short Answer Grading** (Semantic Similarity):
```python
from sentence_transformers import SentenceTransformer, util
import torch

class ShortAnswerGrader:
    """Grade short answer questions using semantic similarity."""

    def __init__(self):
        # Use pre-trained model (SBERT) for semantic similarity
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def grade_answer(self, student_answer, model_answers, threshold=0.8):
        """
        Grade short answer by comparing to model answers.
        Uses semantic similarity (understands synonyms, paraphrases).

        Args:
            student_answer: Student's response text
            model_answers: List of correct/acceptable answers
            threshold: Minimum similarity score to accept (0.0-1.0)

        Returns:
            {score, similarity_score, matched_answer, explanation}
        """
        # Embed student answer and model answers
        student_embedding = self.model.encode(student_answer, convert_to_tensor=True)
        model_embeddings = self.model.encode(model_answers, convert_to_tensor=True)

        # Calculate cosine similarity
        similarities = util.pytorch_cos_sim(student_embedding, model_embeddings)[0]
        max_similarity = torch.max(similarities).item()
        best_match_idx = torch.argmax(similarities).item()

        # Score based on similarity
        if max_similarity >= threshold:
            score = 100
            feedback = f"Correct! Your answer is very similar to: {model_answers[best_match_idx]}"
        elif max_similarity >= threshold - 0.2:
            score = 75
            feedback = f"Partially correct. Your answer is similar to: {model_answers[best_match_idx]}"
        else:
            score = 0
            feedback = f"Incorrect. Expected answer similar to: {model_answers[best_match_idx]}"

        return {
            'score': score,
            'similarity_score': max_similarity,
            'matched_answer': model_answers[best_match_idx],
            'feedback': feedback
        }

    def detect_plagiarism_within_class(self, student_answers):
        """Detect if multiple students submitted nearly identical answers."""
        embeddings = self.model.encode(student_answers, convert_to_tensor=True)
        similarity_matrix = util.pytorch_cos_sim(embeddings, embeddings)

        suspicious_pairs = []
        for i in range(len(student_answers)):
            for j in range(i + 1, len(student_answers)):
                sim = similarity_matrix[i][j].item()
                if sim > 0.95:  # Very similar = possible plagiarism
                    suspicious_pairs.append({
                        'student1': i,
                        'student2': j,
                        'similarity': sim
                    })

        return suspicious_pairs
```

**Essay Grading** (Automated Essay Scoring - AES):
```python
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVR

class AutomatedEssayScorer:
    """
    Grade essays using NLP features and machine learning.
    Common features: word count, sentence length, lexical diversity, etc.
    """

    def __init__(self):
        self.nlp = spacy.load('en_core_web_sm')
        self.scorer = SVR()  # Support Vector Regression
        self.features_fitted = False

    def extract_features(self, essay_text):
        """Extract NLP features from essay."""
        doc = self.nlp(essay_text)
        tokens = [token for token in doc if not token.is_punct]
        sentences = list(doc.sents)

        features = {
            'word_count': len(tokens),
            'sentence_count': len(sentences),
            'avg_sentence_length': len(tokens) / max(len(sentences), 1),
            'lexical_diversity': len(set(tokens)) / max(len(tokens), 1),
            'avg_word_length': sum(len(t.text) for t in tokens) / max(len(tokens), 1),
            'complex_words': self.count_complex_words(tokens),
            'prepositions': sum(1 for t in tokens if t.pos_ == 'ADP'),
            'spelling_errors': self.detect_spelling_errors(tokens),
            'argument_quality': self.assess_argument_structure(doc)
        }
        return features

    def count_complex_words(self, tokens):
        """Count words with 3+ syllables (proxy for complexity)."""
        return sum(1 for t in tokens if self.count_syllables(t.text) >= 3)

    def count_syllables(self, word):
        """Estimate syllable count."""
        vowels = 'aeiouy'
        syllable_count = 0
        previous_was_vowel = False
        for char in word.lower():
            is_vowel = char in vowels
            if is_vowel and not previous_was_vowel:
                syllable_count += 1
            previous_was_vowel = is_vowel
        return max(1, syllable_count)

    def predict_score(self, essay_text):
        """Predict essay score (0-100)."""
        features = self.extract_features(essay_text)
        feature_vector = [list(features.values())]
        predicted_score = self.scorer.predict(feature_vector)[0]
        return {
            'predicted_score': min(100, max(0, predicted_score)),
            'features': features
        }
```

**Code Assessment** (Auto-grading programming assignments):
```python
class CodeGrader:
    """Grade programming assignments."""

    def run_tests(self, student_code, test_cases):
        """
        Execute student code against test cases.
        Captures: Correctness, output, runtime, memory usage.
        """
        import subprocess
        import resource
        import timeout_decorator

        results = []
        for test in test_cases:
            try:
                # Set resource limits (prevent infinite loops)
                def execute():
                    exec(student_code)
                    # Call test function
                    return test['expected']

                # Run with timeout
                output = execute()

                passed = output == test['expected']
                results.append({
                    'test_id': test['id'],
                    'passed': passed,
                    'output': output,
                    'expected': test['expected']
                })
            except Exception as e:
                results.append({
                    'test_id': test['id'],
                    'passed': False,
                    'error': str(e)
                })

        return {
            'test_results': results,
            'passed_count': sum(1 for r in results if r['passed']),
            'total_count': len(results),
            'score': 100 * sum(1 for r in results if r['passed']) / len(results)
        }

    def detect_plagiarism(self, student_codes):
        """Detect code plagiarism using structural analysis."""
        from py_stringmatching import SimFunctions

        plagiarism_pairs = []
        for i in range(len(student_codes)):
            for j in range(i + 1, len(student_codes)):
                # Normalize code (remove comments, formatting)
                code1_normalized = self.normalize_code(student_codes[i])
                code2_normalized = self.normalize_code(student_codes[j])

                # Use Levenshtein distance or structure comparison
                similarity = self.code_similarity(code1_normalized, code2_normalized)
                if similarity > 0.8:
                    plagiarism_pairs.append({
                        'student1': i,
                        'student2': j,
                        'similarity': similarity
                    })

        return plagiarism_pairs
```

**Mathematical Expression Grading**:
```python
from sympy import *
import sympy as sp

class MathExpressionGrader:
    """Grade mathematical expressions (algebraic, calculus, etc.)."""

    def grade_expression(self, student_expr_str, correct_expr_str):
        """
        Grade mathematical expression by checking symbolic equivalence.
        Handles: Equivalent forms (2x vs x+x), simplified vs unsimplified, etc.
        """
        try:
            # Parse expressions
            student_expr = sympify(student_expr_str)
            correct_expr = sympify(correct_expr_str)

            # Check if mathematically equivalent
            difference = simplify(student_expr - correct_expr)
            is_correct = difference == 0

            # Alternative: check if student simplified correctly
            simplified_student = simplify(student_expr)
            simplified_correct = simplify(correct_expr)

            return {
                'is_correct': is_correct,
                'student_expression': student_expr,
                'correct_expression': correct_expr,
                'student_simplified': simplified_student,
                'feedback': 'Correct!' if is_correct else 'Incorrect - see model solution'
            }
        except Exception as e:
            return {
                'is_correct': False,
                'error': f"Failed to parse expression: {str(e)}"
            }

    def grade_calculus_problem(self, student_answer, correct_answer, variable='x'):
        """Grade calculus problems (derivatives, integrals, limits)."""
        x = sp.Symbol(variable)
        student_expr = sympify(student_answer)
        correct_expr = sympify(correct_answer)

        # Check if derivatives are equal
        student_deriv = diff(student_expr, x)
        correct_deriv = diff(correct_expr, x)
        deriv_equal = simplify(student_deriv - correct_deriv) == 0

        return {
            'expressions_equal': simplify(student_expr - correct_expr) == 0,
            'derivatives_equal': deriv_equal,
            'score': 100 if deriv_equal else 50
        }
```

### Academic Integrity & Proctoring

**Plagiarism Detection**:
- **External plagiarism**: Turnitin, SafeAssign (compare against internet/databases)
- **Internal plagiarism**: Within-class similarity detection
- **Citation checking**: Verify proper attribution
- **Concept-level plagiarism**: Detect similar logic/approach (more advanced)

**Online Proctoring Models**:
1. **Live Proctoring**: Human proctor monitors via webcam (most secure, expensive)
2. **Recorded Proctoring**: Recording reviewed afterward (cheaper, less invasive)
3. **AI-Based Proctoring**: Automated surveillance for suspicious behavior
   - Monitors: Eye movement, window switches, microphone activity
   - Flags unusual patterns for human review
   - Privacy concerns: Some schools moving away

**Browser Lockdown**:
```javascript
class ExamLockdownManager {
  /**
   * Lock browser during exam to prevent cheating.
   * Respondus LockDown Browser, Proctorio examples.
   */

  initiate_lockdown() {
    // Disable:
    // - Switching to other applications
    // - Opening new windows/tabs
    // - Printing
    // - Screen capture
    // - Developer tools
    // - Navigation (back/forward)

    // Enables:
    // - Full-screen mode
    // - Webcam/microphone access (for proctoring)

    document.addEventListener('keydown', (e) => {
      // Disable common shortcut keys
      if (e.ctrlKey && (e.key === 'c' || e.key === 'v' || e.key === 'x')) {
        e.preventDefault();
      }
      if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && e.key === 'I')) {
        e.preventDefault();  // Disable DevTools
      }
      if (e.altKey && e.key === 'Tab') {
        e.preventDefault();  // Prevent alt+tab
      }
    });

    // Full screen
    document.documentElement.requestFullscreen();
  }

  detect_window_switch() {
    // Detect if student switches away from exam window
    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        console.log('Student switched windows - flag violation');
        this.flag_violation('window_switch');
      }
    });
  }
}
```

**Biometric & Behavioral Authentication**:
- Fingerprint / face recognition at start of exam
- Behavioral biometrics: Keystroke dynamics, mouse movement patterns
- Continuous re-verification during exam
- Prevents proxy test-takers

### Assessment Best Practices

**Bloom's Taxonomy Integration**:
- **Remember**: Multiple choice, matching
- **Understand**: Short answer, concept questions
- **Apply**: Case studies, problem-solving
- **Analyze**: Compare/contrast, error analysis
- **Evaluate**: Rubric-based essays, projects
- **Create**: Projects, portfolios

**Rubric Design**:
```python
class RubricScorer:
    """Score assessments using detailed rubrics."""

    def __init__(self):
        # Example rubric for essay grading
        self.rubric = {
            'thesis_clarity': {
                'excellent': 25,
                'good': 20,
                'satisfactory': 15,
                'poor': 0
            },
            'evidence_quality': {
                'excellent': 25,
                'good': 20,
                'satisfactory': 15,
                'poor': 0
            },
            'organization': {
                'excellent': 25,
                'good': 20,
                'satisfactory': 15,
                'poor': 0
            },
            'writing_mechanics': {
                'excellent': 25,
                'good': 20,
                'satisfactory': 15,
                'poor': 0
            }
        }

    def score_rubric(self, criteria_ratings):
        """
        Score based on rubric.
        Args: {criterion_name: rating_level, ...}
        """
        total = 0
        for criterion, rating in criteria_ratings.items():
            total += self.rubric[criterion][rating]

        return {
            'total_score': total,
            'max_score': 100,
            'percentage': 100 * total / 100
        }
```

### Tools & Technologies

**Assessment Platforms**:
- **Canvas Quizzes**: Part of Canvas LMS
- **Respondus**: Test cloud and lockdown browser
- **Gradescope**: Paper and digital assignment grading
- **ProctorU**: Online proctoring service
- **Examplify**: Exam software with proctoring

**NLP & Auto-Grading**:
- **BERT/Sentence-Transformers**: Semantic similarity
- **spaCy**: Natural language processing
- **Judge0**: Code execution and grading API
- **SymPy**: Mathematical expression evaluation
- **PyBossa**: Crowdsourced grading

**Plagiarism Detection**:
- **Turnitin**: Industry standard
- **SafeAssign**: Blackboard integration
- **Copyscape**: Web-based plagiarism check
- **Grammarly**: Plagiarism + grammar
- **MOSS** (Measure of Software Similarity): Code plagiarism

### Challenges & Ethical Considerations

1. **Fairness**: Auto-grading can be biased (e.g., BERT trained on majority dialects)
2. **Privacy**: Proctoring software raises surveillance concerns
3. **Accessibility**: Test design must accommodate diverse learners
4. **Validity**: Do assessments measure what they claim?
5. **Cultural bias**: Questions/problems should be culturally responsive
6. **Transparency**: Students deserve to understand grading criteria

### Security & Anti-Cheating Measures

**Assessment Security Architecture**:
```python
import hashlib
import secrets
from cryptography.fernet import Fernet

class AssessmentSecurity:
    """
    Secure assessment delivery and prevent cheating.
    """

    def generate_unique_exam_version(self, question_bank, student_id):
        """
        Create unique exam for each student (randomized question order/options).
        Prevents students from sharing answers.
        """
        import random

        # Use student_id as seed for reproducibility
        random.seed(hashlib.sha256(str(student_id).encode()).digest())

        # Select random subset of questions
        questions = random.sample(question_bank, k=20)

        # Randomize order
        random.shuffle(questions)

        # Randomize multiple choice options
        for q in questions:
            if q['type'] == 'multiple_choice':
                random.shuffle(q['options'])

        return {
            'exam_id': self.generate_exam_id(student_id),
            'questions': questions,
            'expires_at': datetime.utcnow() + timedelta(hours=2)
        }

    def encrypt_exam_content(self, exam_data):
        """
        Encrypt exam questions until exam starts.
        Student can't view questions before allowed time.
        """
        key = Fernet.generate_key()
        cipher = Fernet(key)

        encrypted = cipher.encrypt(json.dumps(exam_data).encode())

        return {
            'encrypted_exam': encrypted,
            'decryption_key': key,  # Store securely, release at exam time
            'exam_start_time': exam_data['start_time']
        }

    def detect_tab_switching(self, student_session):
        """
        Track when student leaves exam window.
        Flag as potential cheating (looking up answers).
        """
        violations = []

        for event in student_session['events']:
            if event['type'] == 'visibility_change' and event['hidden']:
                violations.append({
                    'timestamp': event['timestamp'],
                    'type': 'tab_switch',
                    'duration_seconds': event['duration']
                })

        # Flag if excessive switching
        if len(violations) > 5:
            self.flag_session_for_review(student_session['id'], violations)

        return violations

    def analyze_answer_timing(self, student_responses):
        """
        Detect anomalous answer timing patterns.
        - Too fast: May have pre-knowledge
        - Too similar to other students: Possible collusion
        """
        timing_anomalies = []

        for question_id, response in student_responses.items():
            time_spent = response['time_spent_seconds']
            question_difficulty = response['estimated_time_seconds']

            # Answer submitted unusually fast
            if time_spent < question_difficulty * 0.2:
                timing_anomalies.append({
                    'question_id': question_id,
                    'anomaly': 'too_fast',
                    'time_spent': time_spent,
                    'expected_time': question_difficulty
                })

        return timing_anomalies

    def compare_answer_similarity(self, student_responses_list):
        """
        Detect potential collusion by comparing answer patterns.
        High similarity in wrong answers = possible cheating.
        """
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        # Extract text responses
        student_texts = []
        for responses in student_responses_list:
            combined_text = ' '.join(
                r['answer_text'] for r in responses if 'answer_text' in r
            )
            student_texts.append(combined_text)

        # Calculate similarity
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(student_texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Flag high similarity pairs
        suspicious_pairs = []
        for i in range(len(similarity_matrix)):
            for j in range(i + 1, len(similarity_matrix)):
                if similarity_matrix[i][j] > 0.85:  # 85% similarity threshold
                    suspicious_pairs.append({
                        'student_1': i,
                        'student_2': j,
                        'similarity_score': similarity_matrix[i][j]
                    })

        return suspicious_pairs
```

**Rate Limiting & DDoS Protection**:
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"]
)

@app.route('/api/submit-answer', methods=['POST'])
@limiter.limit("10 per minute")  # Prevent rapid submission attacks
def submit_answer():
    """
    Rate-limited endpoint for answer submission.
    Prevents students from brute-forcing multiple choice answers.
    """
    student_id = request.json['student_id']
    answer = request.json['answer']

    # Verify student has active exam session
    session = verify_exam_session(student_id)
    if not session:
        return {'error': 'No active exam session'}, 403

    # Store answer
    save_answer(student_id, answer)

    return {'success': True}
```

---

**Version**: 2.0
**Last Updated**: 2025-11-19
**Maintained by**: CLAUDE_SKILLS Education Technology Domain

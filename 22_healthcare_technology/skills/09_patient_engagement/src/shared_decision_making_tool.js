/**
 * Shared Decision-Making Tool
 * Helps patients and providers collaborate on treatment decisions
 */

import React, { useState } from 'react';

const SharedDecisionMakingTool = ({ condition, options }) => {
  const [currentStep, setCurrentStep] = useState('education');
  const [patientPreferences, setPatientPreferences] = useState({});
  const [selectedOption, setSelectedOption] = useState(null);

  return (
    <div className="sdm-tool">
      <div className="step-indicator">
        {['Education', 'Options', 'Values', 'Decision'].map((step, i) => (
          <div
            key={i}
            className={`step ${currentStep === ['education', 'options', 'values', 'decision'][i] ? 'active' : ''}`}
          >
            {i + 1}. {step}
          </div>
        ))}
      </div>

      {currentStep === 'education' && (
        <EducationPhase
          condition={condition}
          onNext={() => setCurrentStep('options')}
        />
      )}

      {currentStep === 'options' && (
        <OptionsPhase
          options={options}
          selectedOption={selectedOption}
          setSelectedOption={setSelectedOption}
          onNext={() => setCurrentStep('values')}
        />
      )}

      {currentStep === 'values' && (
        <ValuesPhase
          option={selectedOption}
          preferences={patientPreferences}
          setPreferences={setPatientPreferences}
          onNext={() => setCurrentStep('decision')}
        />
      )}

      {currentStep === 'decision' && (
        <DecisionPhase
          option={selectedOption}
          preferences={patientPreferences}
          onComplete={(decision) => handleDecisionComplete(decision)}
        />
      )}

      <div className="navigation">
        {currentStep !== 'education' && (
          <button onClick={() => goToPreviousStep(currentStep)}>
            Back
          </button>
        )}
      </div>
    </div>
  );
};

const EducationPhase = ({ condition, onNext }) => {
  return (
    <div className="phase education-phase">
      <h2>Understanding {condition.name}</h2>
      <div className="education-content">
        <h3>What is {condition.name}?</h3>
        <p>{condition.description}</p>

        <h3>What causes it?</h3>
        <ul>
          {condition.causes.map((cause, i) => (
            <li key={i}>{cause}</li>
          ))}
        </ul>

        <h3>What could happen?</h3>
        <ul>
          {condition.consequences.map((consequence, i) => (
            <li key={i}>{consequence}</li>
          ))}
        </ul>

        <h3>Key Facts</h3>
        <div className="key-facts">
          {condition.keyFacts.map((fact, i) => (
            <div key={i} className="fact">
              <strong>{fact.label}:</strong> {fact.value}
            </div>
          ))}
        </div>
      </div>

      <button className="primary" onClick={onNext}>
        Continue to Treatment Options
      </button>
    </div>
  );
};

const OptionsPhase = ({ options, selectedOption, setSelectedOption, onNext }) => {
  return (
    <div className="phase options-phase">
      <h2>Treatment Options</h2>
      <p>Let's explore your treatment options. Select one to review details.</p>

      <div className="options-grid">
        {options.map((option, i) => (
          <div
            key={i}
            className={`option-card ${selectedOption?.id === option.id ? 'selected' : ''}`}
            onClick={() => setSelectedOption(option)}
          >
            <h3>{option.name}</h3>
            <p className="summary">{option.summary}</p>

            {selectedOption?.id === option.id && (
              <div className="option-details">
                <h4>Benefits</h4>
                <ul>
                  {option.benefits.map((b, j) => <li key={j}>{b}</li>)}
                </ul>

                <h4>Risks/Side Effects</h4>
                <ul>
                  {option.risks.map((r, j) => <li key={j}>{r}</li>)}
                </ul>

                <h4>Time Commitment</h4>
                <p>{option.timeCommitment}</p>

                <h4>Cost</h4>
                <p>{option.cost}</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {selectedOption && (
        <button className="primary" onClick={onNext}>
          Continue to Your Values
        </button>
      )}
    </div>
  );
};

const ValuesPhase = ({ option, preferences, setPreferences, onNext }) => {
  const valueQuestions = [
    {
      id: 'symptom_relief',
      question: 'How important is symptom relief?',
      scale: 'Very Unimportant to Very Important'
    },
    {
      id: 'side_effects',
      question: 'How much do you want to avoid side effects?',
      scale: 'Very Unimportant to Very Important'
    },
    {
      id: 'treatment_burden',
      question: 'How important is minimal treatment burden (pills, appointments)?',
      scale: 'Very Unimportant to Very Important'
    },
    {
      id: 'lifespan',
      question: 'How important is living longer (vs quality of life)?',
      scale: 'Very Unimportant to Very Important'
    }
  ];

  return (
    <div className="phase values-phase">
      <h2>What Matters Most to You?</h2>
      <p>Share your values to help guide the decision about {option.name}.</p>

      {valueQuestions.map((question, i) => (
        <div key={i} className="value-question">
          <p>{question.question}</p>
          <div className="scale-input">
            {[1, 2, 3, 4, 5].map((score) => (
              <label key={score}>
                <input
                  type="radio"
                  name={question.id}
                  value={score}
                  checked={preferences[question.id] === score}
                  onChange={(e) => setPreferences({
                    ...preferences,
                    [question.id]: parseInt(e.target.value)
                  })}
                />
                <span className={score === 1 ? 'unimportant' : score === 5 ? 'important' : ''}>
                  {score}
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}

      <textarea
        placeholder="Any other thoughts or concerns?"
        onChange={(e) => setPreferences({ ...preferences, notes: e.target.value })}
      />

      <button className="primary" onClick={onNext}>
        Make Your Decision
      </button>
    </div>
  );
};

const DecisionPhase = ({ option, preferences, onComplete }) => {
  const handleConfirmDecision = () => {
    const decision = {
      selected_option: option.id,
      preferences: preferences,
      timestamp: new Date().toISOString()
    };

    onComplete(decision);
  };

  return (
    <div className="phase decision-phase">
      <h2>Your Decision</h2>

      <div className="decision-summary">
        <p>Based on our discussion, you've chosen:</p>
        <h3>{option.name}</h3>
        <p className="summary">{option.summary}</p>

        <div className="next-steps">
          <h3>Next Steps:</h3>
          <ol>
            {option.nextSteps.map((step, i) => (
              <li key={i}>{step}</li>
            ))}
          </ol>
        </div>

        <div className="action-items">
          <h3>Questions for Your Provider:</h3>
          <ul>
            {option.questionsForProvider.map((q, i) => (
              <li key={i}>{q}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="confirmation">
        <label>
          <input type="checkbox" />
          I understand my treatment option and am ready to proceed
        </label>
      </div>

      <button className="primary" onClick={handleConfirmDecision}>
        Confirm and Continue
      </button>

      <button className="secondary" onClick={() => window.print()}>
        Print This Summary
      </button>
    </div>
  );
};

function goToPreviousStep(currentStep) {
  const steps = ['education', 'options', 'values', 'decision'];
  const currentIndex = steps.indexOf(currentStep);
  return steps[Math.max(0, currentIndex - 1)];
}

function handleDecisionComplete(decision) {
  // Send to backend
  fetch('/api/sdm/decision', {
    method: 'POST',
    body: JSON.stringify(decision)
  });
}

export default SharedDecisionMakingTool;

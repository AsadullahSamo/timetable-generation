import React, { useState } from 'react';
import styles from './Steps.module.css';
import { FaCheckCircle, FaCircle } from 'react-icons/fa';

const steps = [
  { id: 1, name: 'School Config' },
  { id: 2, name: 'Classes' },
  { id: 3, name: 'Divisions' },
  { id: 4, name: 'Subjects' },
  { id: 5, name: 'Teachers' },
  { id: 6, name: 'Lessons' },
  { id: 7, name: 'Timetable Constraints' }
];

const Steps = () => {
  const [currentStep, setCurrentStep] = useState(1);
  const [completedSteps, setCompletedSteps] = useState([]);

  const handleNextStep = () => {
    if (currentStep < steps.length) {
      setCompletedSteps([...completedSteps, currentStep]);
      setCurrentStep(currentStep + 1);
    }
  };

  const handleStepClick = (stepId) => {
    if (stepId <= currentStep) {
      setCurrentStep(stepId);
      setCompletedSteps(completedSteps.filter((id) => id < stepId)); // Remove checkmarks for future steps
    }
  };

  return (
    <div>
      <div className={styles.stepsContainer}>
        {steps.map((step) => (
          <div
            key={step.id}
            className={styles.step}
            onClick={() => handleStepClick(step.id)}
          >
            <div
              className={`${styles.stepCircle} ${
                currentStep === step.id
                  ? styles.current
                  : completedSteps.includes(step.id)
                  ? styles.completed
                  : ''
              }`}
            >
              {completedSteps.includes(step.id) ? <FaCheckCircle /> : <FaCircle />}
            </div>
            <span className={styles.stepText}>{step.name}</span>
            {step.id !== steps.length && <span className={styles.separator}>—</span>}
          </div>
        ))}
      </div>
      <button className={styles.nextButton} onClick={handleNextStep}>Next</button>
    </div>
  );
};

export default Steps;

import { useState } from 'react';
import styles from './Constraints.module.css';
import { FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Navbar from './Navbar';
import api from "../utils/api";

const Constraints = () => {
  const [constraints, setConstraints] = useState([
    { id: 1, name: 'Commute time', importance: 'Very Important', active: true },
    { id: 2, name: 'Minimize working days for teachers', importance: 'Important', active: true },
    { id: 3, name: 'Lessons grouped by building', importance: 'Less Important', active: true },
    { id: 4, name: 'Uniform distribution of lessons across days', importance: 'Very Important', active: true },
    { id: 5, name: 'Minimize teachers gaps', importance: 'Important', active: true },
    { id: 6, name: 'Early placement of important lessons', importance: 'Very Important', active: true },
    { id: 7, name: 'Consecutive identical lessons', importance: 'Important', active: true },
    { id: 8, name: 'No 3 identical lessons in the same day', importance: 'Very Important', active: true },
    { id: 9, name: 'Appropriate number of days for lesson distribution', importance: 'Important', active: true },
  ]);

  const toggleConstraint = (id) => {
    setConstraints(prev =>
      prev.map(constraint =>
        constraint.id === id
          ? { ...constraint, active: !constraint.active }
          : constraint
      )
    );
  };

  const updateImportance = (id, newImportance) => {
    setConstraints(prev =>
      prev.map(constraint =>
        constraint.id === id
          ? { ...constraint, importance: newImportance }
          : constraint
      )
    );
  };

  const handleGenerateTimetable = async () => {
    try {
      const response = await api.post('/timetable/generate/', {
        constraints: constraints.filter(c => c.active)
      });
      
      if (response.data.task_id) {
        // Poll for task completion
        const pollResult = async () => {
          const task = await api.get(`/timetable/tasks/${response.data.task_id}/`);
          if (task.data.status === 'SUCCESS') {
            router.push('/components/TimetableDisplay');
          } else if (task.data.status === 'FAILURE') {
            throw new Error('Generation failed');
          } else {
            setTimeout(pollResult, 1000);
          }
        };
        await pollResult();
      }
    } catch (error) {
      alert('Timetable generation failed: ' + error.message);
    }
  };
  
  const getImportanceIcon = (importance) => {
    switch (importance) {
      case 'Very Important':
        return <><FaArrowUp /><FaArrowUp style={{ color: '#8b5cf6' }} /></>;
      case 'Important':
        return <FaArrowUp style={{ color: '#3b82f6' }} />;
      case 'Less Important':
        return <FaArrowDown style={{ color: '#ef4444' }} />;
      default:
        return null;
    }
  };

  return (
    <div className={styles.container}>
      
      <Navbar number={6}/>

      <div className={styles.mainContent}>
        <h1 className={styles.mainHeading}>Timetable Constraints</h1>

        <div className={styles.section}>
          <h2 className={styles.sectionHeading}>Configure Constraints</h2>
          
          <div className={styles.constraintsList}>
            {constraints.map((constraint) => (
              <div key={constraint.id} className={styles.constraintItem}>
                <div className={styles.constraintInfo}>
                  <span className={styles.constraintName}>{constraint.name}</span>
                  <div className={styles.importanceSelector}>
                    <select
                      value={constraint.importance}
                      onChange={(e) => updateImportance(constraint.id, e.target.value)}
                      className={`${styles.importanceDropdown} ${styles[constraint.importance.replace(/\s+/g, '')]}`}
                    >
                      <option value="Very Important">Very Important</option>
                      <option value="Important">Important</option>
                      <option value="Less Important">Less Important</option>
                    </select>
                    <div className={styles.importanceIcon}>
                      {getImportanceIcon(constraint.importance)}
                    </div>
                  </div>
                </div>
                <div className={styles.toggleGroup}>
                  <button
                    className={`${styles.toggleButton} ${constraint.active ? styles.active : ''}`}
                    onClick={() => toggleConstraint(constraint.id)}
                  >
                    {constraint.active ? '✓' : '✗'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.navigation}>
          <button className={styles.secondaryButton}>
            Previous Step
          </button>
          <button
            className={styles.primaryButton}
            onClick={handleGenerateTimetable}
          >
            Generate Timetable
          </button>
        </div>
      </div>
    </div>
  );
};

export default Constraints;
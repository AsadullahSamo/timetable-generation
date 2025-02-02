import { useState } from 'react';
import styles from './Constraints.module.css';

const Constraints = () => {
  const [constraints, setConstraints] = useState([
    { id: 1, name: 'Commute time', importance: 'Important', active: true },
    { id: 2, name: 'Minimize working days for teachers', importance: 'Less important', active: true },
    { id: 3, name: 'Lessons grouped by building', importance: 'Less important', active: true },
    { id: 4, name: 'Uniform distribution of lessons across days', importance: 'Important', active: true },
    { id: 5, name: 'Minimize teachers gaps', importance: 'Less important', active: true },
    { id: 6, name: 'Early placement of important lessons', importance: 'Important', active: true },
    { id: 7, name: 'Consecutive identical lessons', importance: 'Important', active: true },
    { id: 8, name: 'No 3 identical lessons in the same day', importance: 'Important', active: true },
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

  const handleGenerateTimetable = () => {
    const activeConstraints = constraints.filter(c => c.active);
    console.log('Generating timetable with constraints:', activeConstraints);
    // Add logic to generate timetable here
  };

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <div className={styles.menu}>
          <div className={styles.menuItem}>School Config</div>
          <div className={styles.menuItem}>Classes</div>
          <div className={styles.menuItem}>Teachers</div>
          <div className={styles.menuItem}>Lessons</div>
          <div className={`${styles.menuItem} ${styles.active}`}>Constraints</div>
          <div className={styles.menuItem}>Timetable</div>
        </div>
      </div>

      <div className={styles.mainContent}>
        <h1 className={styles.mainHeading}>Timetable Constraints</h1>

        <div className={styles.section}>
          <h2 className={styles.sectionHeading}>Configure Constraints</h2>
          
          <div className={styles.constraintsList}>
            {constraints.map((constraint) => (
              <div key={constraint.id} className={styles.constraintItem}>
                <div className={styles.constraintInfo}>
                  <span className={styles.constraintName}>{constraint.name}</span>
                  <span className={`${styles.importance} ${styles[constraint.importance.replace(/\s+/g, '')]}`}>
                    {constraint.importance}
                  </span>
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
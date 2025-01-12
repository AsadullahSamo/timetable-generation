import React, { useState } from 'react';
import styles from './Periods.module.css';

const daysOfWeek = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];

const Periods = () => {
  const [selectedDays, setSelectedDays] = useState([]);

  const toggleDay = (day) => {
    if (selectedDays.includes(day)) {
      setSelectedDays(selectedDays.filter((d) => d !== day));
    } else {
      setSelectedDays([...selectedDays, day]);
    }
  };

  return (
    <div className={styles.periodsContainer}>
      {daysOfWeek.map((day) => (
        <div
          key={day}
          className={`${styles.dayItem} ${selectedDays.includes(day) ? styles.selected : ''}`}
          onClick={() => toggleDay(day)}
        >
          {day}
        </div>
      ))}
    </div>
  );
};

export default Periods;

import React, { useState } from 'react';
import styles from './PeriodGrid.module.css';

const PeriodsGrid = ({ selectedDays, startTime, lessonDuration, periods }) => {
  
  const [selectedSlots, setSelectedSlots] = useState({});
  const [isGenerated, setIsGenerated] = useState(false);

  const generateTimeSlots = () => {
    const slots = [];
    let currentTime = new Date(`1970-01-01T${startTime}:00`);
    for (let i = 0; i < periods; i++) {
      const nextTime = new Date(currentTime.getTime() + lessonDuration * 60000);
      slots.push(
        `${currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} - ${nextTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
      );
      currentTime = nextTime;
    }
    return slots;
  };

  const toggleSlot = (day, slot) => {
    setSelectedSlots((prev) => {
      const key = `${day}-${slot}`;
      const updated = { ...prev };
      if (updated[key]) {
        delete updated[key];
      } else {
        updated[key] = true;
      }
      return updated;
    });
  };

  const timeSlots = generateTimeSlots();

  return (
    <div className={styles.container}>
      {!isGenerated && (
        <button
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            cursor: 'pointer',
            marginBottom: '20px',
          }}
          onClick={() => setIsGenerated(true)}
        >
          Generate Timetable
        </button>
      )}

      {isGenerated && (
        <div className={styles.grid}>
          <div className={styles.header}></div>
          {timeSlots.map((slot, idx) => (
            <div key={`header-${idx}`} className={styles.header}>
              {slot}
            </div>
          ))}

          {selectedDays.map((day) => (
            <React.Fragment key={day}>
              <div className={styles.dayLabel}>{day}</div>
              {timeSlots.map((slot, idx) => (
                <div
                  key={`${day}-${idx}`}
                  className={`${styles.slot} ${selectedSlots[`${day}-${slot}`] ? styles.selected : ''}`}
                  onClick={() => toggleSlot(day, slot)}
                ></div>
              ))}
            </React.Fragment>
          ))}
        </div>
      )}
    </div>
  );
};

export default PeriodsGrid;

import React, { useState } from "react";
import styles from "./SchoolConfig.module.css";

const SchoolConfig = () => {
  const [schoolName, setSchoolName] = useState("");
  const [numPeriods, setNumPeriods] = useState(0);
  const [startTime, setStartTime] = useState("08:00");
  const [days, setDays] = useState(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]);
  const [lessonDuration, setLessonDuration] = useState(60);
  const [periodsGrid, setPeriodsGrid] = useState([]);

  const generatePeriods = () => {
    const grid = [];
    let currentTime = startTime;
    for (let i = 0; i < numPeriods; i++) {
      const row = days.map((day) => ({
        day,
        time: currentTime,
        period: i + 1,
      }));
      grid.push(row);
      currentTime = incrementTime(currentTime, lessonDuration);
    }
    setPeriodsGrid(grid);
  };

  const incrementTime = (time, duration) => {
    let [hours, minutes] = time.split(":").map(Number);
    minutes += duration;  
    
    while (minutes >= 60) {
      minutes -= 60;
      hours += 1;
    }
  
    if (hours >= 24) {
      hours = hours % 24;
    }
    
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  };
  
  
  

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log({ schoolName, periodsGrid });
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.heading}>School Configuration</h2>

        <div className={styles.fieldGroup}>
          <label htmlFor="schoolName" className={styles.label}>
            School Name
          </label>
          <input
            type="text"
            id="schoolName"
            value={schoolName}
            onChange={(e) => setSchoolName(e.target.value)}
            className={styles.input}
            placeholder="Enter your school name"
            required
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="numPeriods" className={styles.label}>
            Number of Periods
          </label>
          <input
            type="number"
            id="numPeriods"
            value={numPeriods}
            onChange={(e) => setNumPeriods(e.target.value)}
            className={styles.input}
            min="1"
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="startTime" className={styles.label}>
            Starting Time
          </label>
          <input
            type="time"
            id="startTime"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className={styles.input}
          />
        </div>

        <div className={styles.fieldGroup}>
          <label htmlFor="lessonDuration" className={styles.label}>
            Lesson Duration (minutes)
          </label>
          <input
            type="number"
            id="lessonDuration"
            value={lessonDuration}
            onChange={(e) => setLessonDuration(e.target.value)}
            className={styles.input}
            max={60}
            min={60}
          />
        </div>

        <div className={styles.fieldGroup}>
          <button type="button" onClick={generatePeriods} className={styles.generateButton}>
            Generate Periods
          </button>
        </div>

        {periodsGrid.length > 0 && (
          <div className={styles.gridContainer}>
            <div className={styles.gridHeader}>
              {days.map((day, index) => (
                <div key={index} className={styles.gridHeaderCell}>
                  {day}
                </div>
              ))}
            </div>
            <div className={styles.gridBody}>
              {periodsGrid.map((row, rowIndex) => (
                <div key={rowIndex} className={styles.gridRow}>
                  {row.map((cell, cellIndex) => (
                    <div key={cellIndex} className={styles.gridCell}>
                      {cell.time}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        )}

        <div className={styles.navigation}>
          <button type="button" className={styles.button}>
            Previous Step
          </button>
          <button type="submit" className={styles.buttonPrimary}>
            Next Step
          </button>
        </div>
      </form>
    </div>
  );
};

export default SchoolConfig;

import React, { useState } from "react";
import styles from "./SchoolConfig.module.css";

const SchoolConfig = () => {
  const [schoolName, setSchoolName] = useState("");
  const [periods, setPeriods] = useState([]);

  const handleAddPeriod = () => {
    setPeriods([...periods, { day: "Monday", start: "", end: "" }]);
  };

  const handlePeriodChange = (index, field, value) => {
    const updatedPeriods = [...periods];
    updatedPeriods[index][field] = value;
    setPeriods(updatedPeriods);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Submit logic here
    console.log({ schoolName, periods });
  };

  return (
    <div className={styles.container}>
      {/* Progress Steps */}
      <div className={styles.progress}>
        <span className={styles.step}>1. School Config</span>
        <span className={styles.step}>2. Classes</span>
        <span className={styles.step}>3. Divisions</span>
        <span className={styles.step}>4. Subjects</span>
        <span className={styles.step}>5. Teachers</span>
        <span className={styles.step}>6. Lessons</span>
        <span className={styles.step}>7. Timetable Constraints</span>
      </div>

      {/* School Config Form */}
      <form onSubmit={handleSubmit} className={styles.form}>
        <h2 className={styles.heading}>School Configuration</h2>

        {/* School Name */}
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
          <p className={styles.helperText}>
            The name of the school will be displayed on printed schedules.
          </p>
        </div>

        {/* Periods */}
        <div className={styles.fieldGroup}>
          <label className={styles.label}>Periods</label>
          <div className={styles.periodsContainer}>
            {periods.map((period, index) => (
              <div key={index} className={styles.periodRow}>
                <select
                  value={period.day}
                  onChange={(e) =>
                    handlePeriodChange(index, "day", e.target.value)
                  }
                  className={styles.select}
                >
                  <option value="Monday">Monday</option>
                  <option value="Tuesday">Tuesday</option>
                  <option value="Wednesday">Wednesday</option>
                  <option value="Thursday">Thursday</option>
                  <option value="Friday">Friday</option>
                </select>
                <input
                  type="time"
                  value={period.start}
                  onChange={(e) =>
                    handlePeriodChange(index, "start", e.target.value)
                  }
                  className={styles.input}
                  placeholder="Start Time"
                  required
                />
                <input
                  type="time"
                  value={period.end}
                  onChange={(e) =>
                    handlePeriodChange(index, "end", e.target.value)
                  }
                  className={styles.input}
                  placeholder="End Time"
                  required
                />
              </div>
            ))}
          </div>
          <button
            type="button"
            className={styles.addButton}
            onClick={handleAddPeriod}
          >
            + Add Period
          </button>
        </div>

        {/* Navigation Buttons */}
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

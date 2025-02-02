// AddTeacher.js
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./AddTeacher.module.css";

const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const dayAbbreviations = {
  Monday: "Mon",
  Tuesday: "Tue",
  Wednesday: "Wed",
  Thursday: "Thu",
  Friday: "Fri"
};

const AddTeacher = () => {
  const router = useRouter();
  const { index } = router.query;
  const [name, setName] = useState("");
  const [mode, setMode] = useState(null);
  const [timetable, setTimetable] = useState({});
  const [unavailability, setUnavailability] = useState({
    mandatory: {},
    preferable: {}
  });

  useEffect(() => {
    const savedTimetable = JSON.parse(localStorage.getItem("timetable")) || {};
    setTimetable(savedTimetable);
  }, []);

  useEffect(() => {
    if (index !== undefined) {
      const teachers = JSON.parse(localStorage.getItem("teachers")) || [];
      const teacher = teachers[index];
      if (teacher) {
        setName(teacher.name);
        setUnavailability({
          mandatory: teacher.mandatory || {},
          preferable: teacher.preferable || {}
        });
      }
    }
  }, [index]);

  const toggleTimeSlot = (day, time) => {
    const key = `${day}-${time}`;
    const newState = { ...unavailability };
    
    if (mode === 'mandatory') {
      newState.mandatory[key] = !newState.mandatory[key];
    } else if (mode === 'preferable') {
      newState.preferable[key] = !newState.preferable[key];
    }
    
    setUnavailability(newState);
  };

  const getPeriodsForDay = (day) => {
    const abbreviatedDay = dayAbbreviations[day];
    return timetable[abbreviatedDay] || [];
  };

  const handleSave = () => {
    if (!name) return alert("Please enter teacher name");
    if (Object.keys(timetable).length === 0) return alert("Please configure timetable first");
    
    const teachers = JSON.parse(localStorage.getItem("teachers")) || [];
    const teacherData = {
      name,
      mandatory: unavailability.mandatory,
      preferable: unavailability.preferable
    };

    if (index !== undefined) {
      teachers[index] = teacherData;
    } else {
      teachers.push(teacherData);
    }

    localStorage.setItem("teachers", JSON.stringify(teachers));
    router.push("/components/TeachersConfig");
  };

  return (
    <div className={styles.container}>
      <div className={styles.sidebar}>
        <div className={styles.menu}>
          <div className={styles.menuItem}>School Config</div>
          <div className={styles.menuItem}>Classes</div>
          <div className={`${styles.menuItem} ${styles.active}`}>Teachers</div>
          <div className={styles.menuItem}>Subjects</div>
          <div className={styles.menuItem}>Timetable</div>
        </div>
      </div>

      <div className={styles.mainContent}>
        <h1>{index !== undefined ? 'Edit Teacher' : 'New Teacher'}</h1>
        
        <div className={styles.formSection}>
          <input
            type="text"
            placeholder="Teacher name..."
            value={name}
            onChange={(e) => setName(e.target.value)}
            className={styles.inputField}
          />

          <div className={styles.modeSelector}>
            <button
              className={`${styles.modeButton} ${mode === 'mandatory' ? styles.active : ''}`}
              onClick={() => setMode('mandatory')}
            >
              Mandatory Unavailability
            </button>
            <button
              className={`${styles.modeButton} ${mode === 'preferable' ? styles.active : ''}`}
              onClick={() => setMode('preferable')}
            >
              Preferable Unavailability
            </button>
          </div>

          <div className={styles.scheduleGrid}>
            <table>
              <thead>
                <tr>
                  <th></th>
                  {Object.keys(timetable).length > 0 && 
                   getPeriodsForDay("Monday").map((time) => (
                    <th key={time}>{time}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {days.map(day => {
                  const periods = getPeriodsForDay(day);
                  return periods.length > 0 ? (
                    <tr key={day}>
                      <td className={styles.dayLabel}>{day}</td>
                      {periods.map(time => {
                        const key = `${day}-${time}`;
                        const isMandatory = unavailability.mandatory[key];
                        const isPreferable = unavailability.preferable[key];
                        
                        return (
                          <td
                            key={time}
                            className={`${styles.timeCell} 
                              ${isMandatory ? styles.mandatory : ''} 
                              ${isPreferable ? styles.preferable : ''}`}
                            onClick={() => toggleTimeSlot(day, time)}
                          />
                        );
                      })}
                    </tr>
                  ) : null;
                })}
              </tbody>
            </table>
          </div>

          {Object.keys(timetable).length === 0 && (
            <div className={styles.error}>
              <i className="fas fa-exclamation-triangle" />
              <p>Please configure the timetable first in School Settings</p>
            </div>
          )}

          <div className={styles.buttonGroup}>
            <button className={styles.secondaryButton} onClick={() => router.back()}>
              Cancel
            </button>
            <button 
              className={styles.primaryButton} 
              onClick={handleSave}
              disabled={Object.keys(timetable).length === 0}
            >
              Save Teacher
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddTeacher;
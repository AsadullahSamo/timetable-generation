import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./AddTeacher.module.css";

const AddTeacher = () => {
  const [teacherName, setTeacherName] = useState("");
  const [mandatoryPeriods, setMandatoryPeriods] = useState({});
  const [preferablePeriods, setPreferablePeriods] = useState({});
  const [isMandatory, setIsMandatory] = useState(false); 
  const [isPreferable, setIsPreferable] = useState(false); 
  const router = useRouter();
  const { teacher, index } = router.query; 

  useEffect(() => {
    if (teacher) {
      const parsedTeacher = JSON.parse(teacher);
      setTeacherName(parsedTeacher.name);
      setMandatoryPeriods(parsedTeacher.mandatory || {});
      setPreferablePeriods(parsedTeacher.preferable || {});
    }
  }, [teacher]);

  const togglePeriodSelection = (day, period) => {
    const key = `${day}-${period}`;
    
    if (isMandatory) {
      
      setMandatoryPeriods((prev) => ({
        ...prev,
        [key]: prev[key] ? null : "mandatory", 
      }));
    }
    
    if (isPreferable) {
      
      setPreferablePeriods((prev) => ({
        ...prev,
        [key]: prev[key] ? null : "preferable", 
      }));
    }
  };

  const handleSave = () => {
    if (!teacherName) {
      alert("Please enter a teacher name.");
      return;
    }

    const teacherData = {
      name: teacherName,
      mandatory: mandatoryPeriods,
      preferable: preferablePeriods,
    };

    const teachers = JSON.parse(localStorage.getItem("teachers")) || [];
    
    if (index !== undefined) {
      teachers[index] = teacherData; 
    } else {
      teachers.push(teacherData); 
    }

    localStorage.setItem("teachers", JSON.stringify(teachers));
    router.push("/components/TeachersConfig");
  };

  const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
  const timeSlots = ["8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM"];

  return (
    <div className={styles.container}>
      <h1 className={styles.header}>{teacher ? "Edit Teacher" : "Add Teacher"}</h1>
      <input
        type="text"
        placeholder="Teacher name..."
        value={teacherName}
        onChange={(e) => setTeacherName(e.target.value)}
        className={styles.inputField}
      />
      
      <div className={styles.checkboxContainer}>
        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={isMandatory}
            onChange={() => {
              setIsMandatory(!isMandatory);
              setIsPreferable(false); 
            }}
            className={styles.checkbox}
          />
          <span className={styles.checkboxText}>Mandatory</span>
        </label>

        <label className={styles.checkboxLabel}>
          <input
            type="checkbox"
            checked={isPreferable}
            onChange={() => {
              setIsPreferable(!isPreferable);
              setIsMandatory(false); 
            }}
            className={styles.checkbox}
          />
          <span className={styles.checkboxText}>Preferable</span>
        </label>
      </div>
      
      <div className={styles.gridContainer}>
        {days.map((day) => (
          <div key={day} className={styles.dayColumn}>
            <h4 className={styles.dayHeader}>{day}</h4>
            {timeSlots.map((time) => {
              const key = `${day}-${time}`;
              const isMandatorySelected = mandatoryPeriods[key];
              const isPreferableSelected = preferablePeriods[key];
              return (
                <div
                  key={key}
                  className={`${styles.gridItem} ${
                    isMandatorySelected ? styles.mandatory : ""
                  } ${isPreferableSelected ? styles.preferable : ""}`}
                  onClick={() => togglePeriodSelection(day, time)}
                >
                  {time}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <button className={styles.saveButton} onClick={handleSave}>
        Save
      </button>
    </div>
  );
};

export default AddTeacher;

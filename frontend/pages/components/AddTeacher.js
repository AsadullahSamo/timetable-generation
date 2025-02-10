import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import styles from "./AddTeacher.module.css";
import api from "../utils/api";

const AddTeacher = () => {
  const router = useRouter();
  const { id } = router.query;
  
  // Form states
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subjects, setSubjects] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]);
  const [maxLessons, setMaxLessons] = useState(4);
  // Internal availability state: { day: { periodIndex: mode } }
  const [availabilityState, setAvailabilityState] = useState({});
  const [timetableConfig, setTimetableConfig] = useState(null);
  
  // Separate loading states:
  const [configLoading, setConfigLoading] = useState(true);
  const [teacherLoading, setTeacherLoading] = useState(false);
  const [error, setError] = useState("");
  
  // Active mode selector: "preferable" or "mandatory"
  const [activeMode, setActiveMode] = useState("preferable");

  // Fetch configuration and subjects once on mount.
  useEffect(() => {
    const fetchConfigAndSubjects = async () => {
      try {
        const configRes = await api.get("/timetable/configs/");
        if (configRes.data.length > 0) {
          setTimetableConfig(configRes.data[0]);
        }
        const subjectsRes = await api.get("/timetable/subjects/");
        setAllSubjects(subjectsRes.data);
      } catch (err) {
        setError("Failed to load configuration or subjects.");
      } finally {
        setConfigLoading(false);
      }
    };
    fetchConfigAndSubjects();
  }, []);

  // If editing, fetch teacher data once configuration is loaded.
  useEffect(() => {
    if (!id || configLoading || !timetableConfig) return;
    const fetchTeacherData = async () => {
      setTeacherLoading(true);
      try {
        const teacherRes = await api.get(`/timetable/teachers/${id}/`);
        const teacher = teacherRes.data;
        setName(teacher.name);
        setEmail(teacher.email);
        setSubjects(teacher.subjects);
        setMaxLessons(teacher.max_lessons_per_day);
        // Convert stored unavailable_periods (expected as arrays) to internal availabilityState.
        // Our final data structure in the backend is expected as:
        // { mandatory: { "Mon": [ "8:00 AM", "9:00 AM" ], ... }, preferable: { "Tue": [ "8:00 AM" ], ... } }
        // We'll convert that into an object: { day: { periodIndex: mode, ... }, ... }
        const internal = {};
        if (teacher.unavailable_periods && timetableConfig.generated_periods) {
          ["mandatory", "preferable"].forEach(mode => {
            if (teacher.unavailable_periods[mode]) {
              Object.entries(teacher.unavailable_periods[mode]).forEach(([day, times]) => {
                // Ensure times is an array (if it's not, wrap it into an array)
                const timesArray = Array.isArray(times) ? times : [times];
                timesArray.forEach(time => {
                  const dayPeriods = timetableConfig.generated_periods[day] || [];
                  const index = dayPeriods.indexOf(time);
                  if (index !== -1) {
                    if (!internal[day]) internal[day] = {};
                    internal[day][index] = mode;
                  }
                });
              });
            }
          });
        }
        setAvailabilityState(internal);
      } catch (err) {
        setError("Failed to load teacher data.");
      } finally {
        setTeacherLoading(false);
      }
    };
    fetchTeacherData();
  }, [id, configLoading, timetableConfig]);

  // Combine loading states for rendering:
  const isLoading = configLoading || teacherLoading;

  const handleSubjectChange = (subjectId) => {
    setSubjects(prev =>
      prev.includes(subjectId)
        ? prev.filter((id) => id !== subjectId)
        : [...prev, subjectId]
    );
  };

  // Toggle the state for a given day and period index.
  const toggleTimeSlot = (day, periodIndex) => {
    setAvailabilityState(prev => {
      const newState = { ...prev };
      const dayState = newState[day] ? { ...newState[day] } : {};
      if (dayState[periodIndex] === activeMode) {
        // If cell is already set to active mode, remove it.
        delete dayState[periodIndex];
      } else {
        // Otherwise, set cell to active mode.
        dayState[periodIndex] = activeMode;
      }
      newState[day] = dayState;
      return newState;
    });
  };

  // Convert internal availabilityState into final JSON format:
  // { mandatory: { day: [time, ...], ... }, preferable: { day: [time, ...], ... } }
  const convertAvailability = () => {
    const result = { mandatory: {}, preferable: {} };
    if (!timetableConfig || !timetableConfig.generated_periods) return result;
    for (const [day, periodsObj] of Object.entries(availabilityState)) {
      for (const [periodIndexStr, cellMode] of Object.entries(periodsObj)) {
        const periodIndex = parseInt(periodIndexStr, 10);
        const dayPeriods = timetableConfig.generated_periods[day] || [];
        const time = dayPeriods[periodIndex];
        if (time) {
          if (!result[cellMode][day]) {
            result[cellMode][day] = [];
          }
          result[cellMode][day].push(time);
        }
      }
    }
    return result;
  };

  const handleSave = async () => {
    if (!name || !email) {
      setError("Name and email are required");
      return;
    }
    const formattedAvailability = convertAvailability();
    const teacherData = {
      name,
      email,
      subjects,
      max_lessons_per_day: maxLessons,
      unavailable_periods: formattedAvailability,
    };
    try {
      if (id) {
        await api.patch(`/timetable/teachers/${id}/`, teacherData);
      } else {
        await api.post("/timetable/teachers/", teacherData);
      }
      router.push("/components/TeachersConfig");
    } catch (err) {
      console.error("Save error:", err.response?.data);
      setError(err.response?.data?.detail || "Failed to save teacher.");
    }
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <i className="fas fa-spinner fa-spin"></i>
        <p>Loading teacher data...</p>
      </div>
    );
  }

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
        <h1>{id ? "Edit Teacher" : "New Teacher"}</h1>
        {error && <div className={styles.errorAlert}>{error}</div>}

        <div className={styles.formSection}>
          <div className={styles.inputGroup}>
            <input
              type="text"
              placeholder="Teacher name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={styles.inputField}
            />
            <input
              type="email"
              placeholder="Teacher email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className={styles.inputField}
            />
          </div>

          <div className={styles.inputGroup}>
            <label>Max Lessons Per Day</label>
            <input
              type="number"
              min="1"
              max="8"
              value={maxLessons}
              onChange={(e) => setMaxLessons(parseInt(e.target.value, 10))}
              className={styles.inputField}
            />
          </div>

          <div className={styles.subjectsSection}>
            <h3>Assigned Subjects</h3>
            <div className={styles.subjectsGrid}>
              {allSubjects.map((subject) => (
                <div
                  key={subject.id}
                  className={`${styles.subjectCard} ${
                    subjects.includes(subject.id) ? styles.selected : ""
                  }`}
                  onClick={() => handleSubjectChange(subject.id)}
                >
                  {subject.name}
                </div>
              ))}
            </div>
          </div>

          {/* Mode selector buttons */}
          <div className={styles.modeSelector}>
            <button
              className={`${styles.modeButton} ${
                activeMode === "preferable" ? styles.active : ""
              }`}
              onClick={() => setActiveMode("preferable")}
            >
              Preferable
            </button>
            <button
              className={`${styles.modeButton} ${
                activeMode === "mandatory" ? styles.active : ""
              }`}
              onClick={() => setActiveMode("mandatory")}
            >
              Mandatory
            </button>
          </div>

          {/* Availability Grid */}
          <div className={styles.availabilitySection}>
            <h3>Unavailability</h3>
            {timetableConfig?.generated_periods ? (
              <div className={styles.scheduleGrid}>
                <table>
                  <thead>
                    <tr>
                      <th></th>
                      {Object.values(timetableConfig.generated_periods)[0].map(
                        (_, index) => (
                          <th key={index}>Period {index + 1}</th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(timetableConfig.generated_periods).map(
                      ([day, periods]) => (
                        <tr key={day}>
                          <td className={styles.dayLabel}>{day}</td>
                          {periods.map((time, periodIndex) => {
                            const key = `${day}-${periodIndex}`;
                            // Look up the mode for this cell in availabilityState.
                            const cellMode =
                              availabilityState[day] && availabilityState[day][periodIndex]
                                ? availabilityState[day][periodIndex]
                                : "none";
                            return (
                              <td
                                key={key}
                                className={`${styles.timeCell} ${
                                  cellMode === "preferable"
                                    ? styles.preferable
                                    : cellMode === "mandatory"
                                    ? styles.mandatory
                                    : ""
                                }`}
                                onClick={() => toggleTimeSlot(day, periodIndex)}
                              >
                                {time}
                                {/* {cellMode !== "none" && (
                                  <div className={styles.cellStateLabel}>
                                    {cellMode}
                                  </div>
                                )} */}
                              </td>
                            );
                          })}
                        </tr>
                      )
                    )}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className={styles.error}>
                <i className="fas fa-exclamation-triangle" />
                <p>
                  Valid timetable configuration not found. Please configure periods first.
                </p>
              </div>
            )}
          </div>

          <div className={styles.buttonGroup}>
            <button
              className={styles.secondaryButton}
              onClick={() => router.push("/components/TeachersConfig")}
            >
              Cancel
            </button>
            <button
              className={styles.primaryButton}
              onClick={handleSave}
              disabled={!timetableConfig?.generated_periods}
            >
              {id ? "Update Teacher" : "Add Teacher"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AddTeacher;

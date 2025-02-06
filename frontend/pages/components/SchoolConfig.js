import React, { useState } from "react";
import { useRouter } from "next/router";
import styles from "./SchoolConfig.module.css";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const SchoolConfig = () => {
  const router = useRouter();
  const [schoolName, setSchoolName] = useState("");
  const [numPeriods, setNumPeriods] = useState(0);
  const [startTime, setStartTime] = useState("08:00");
  const [days] = useState(["Mon", "Tue", "Wed", "Thu", "Fri"]);
  const [lessonDuration, setLessonDuration] = useState(60);
  const [periods, setPeriods] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Time formatting helpers
  const formatTime = (timeString) => {
    const [hours, minutes] = timeString.split(":").map(Number);
    const period = hours >= 12 ? "PM" : "AM";
    const formattedHours = hours % 12 || 12;
    return `${formattedHours}:${String(minutes).padStart(2, "0")} ${period}`;
  };

  const incrementTime = (time, duration) => {
    let [hours, minutes] = time.split(":").map(Number);
    minutes += duration;
    hours += Math.floor(minutes / 60);
    minutes %= 60;
    hours %= 24;
    return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`;
  };

  const generatePeriods = () => {
    if (!numPeriods || !startTime || !lessonDuration) {
      setError("Please fill all required fields before generating periods.");
      return;
    }

    const newPeriods = {};
    let currentTime = startTime;

    days.forEach(day => {
      newPeriods[day] = [];
      let dayTime = startTime;
      for (let i = 0; i < numPeriods; i++) {
        newPeriods[day].push(formatTime(dayTime));
        dayTime = incrementTime(dayTime, lessonDuration);
      }
    });

    setPeriods(newPeriods);
    setError(null); // Clear any previous errors
  };

  const addPeriod = (day) => {
    const lastPeriod = periods[day][periods[day].length - 1];
    const [time, period] = lastPeriod.split(" ");
    let [hours, minutes] = time.split(":").map(Number);

    if (period === "PM" && hours !== 12) hours += 12;
    if (period === "AM" && hours === 12) hours = 0;

    const newTime = incrementTime(`${hours}:${minutes}`, lessonDuration);

    setPeriods(prev => ({
      ...prev,
      [day]: [...prev[day], formatTime(newTime)]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (Object.keys(periods).length === 0) {
      setError("Please generate periods before saving.");
      setLoading(false);
      return;
    }

    try {
      // Convert startTime to HH:mm:ss format
      const formattedStartTime = `${startTime}:00`;

      const response = await api.post("/timetable/configs/", {
        name: schoolName,
        days,
        periods: numPeriods,
        start_time: formattedStartTime,
        lesson_duration: lessonDuration,
        generated_periods: periods
      });

      if (response.status === 201) {
        router.push("/components/ClassesConfig");
      }
    } catch (error) {
      if (error.response) {
        setError(`Error: ${error.response.data.detail || "Failed to save configuration"}`);
      } else if (error.request) {
        setError("No response from server. Please check your connection.");
      } else {
        setError("An unexpected error occurred. Please try again.");
      }
      console.error("Submission error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <Navbar number={1} />

      <form onSubmit={handleSubmit} className={styles.mainContent}>
        <h2 className={styles.mainHeading}>School Configuration</h2>

        {error && <div className={styles.errorMessage}>{error}</div>}

        <section className={styles.section}>
          <h3 className={styles.sectionHeading}>School Name</h3>
          <input
            type="text"
            value={schoolName}
            onChange={(e) => setSchoolName(e.target.value)}
            className={styles.input}
            placeholder="Enter school name"
            required
            disabled={loading}
          />
        </section>

        <section className={styles.section}>
          <h3 className={styles.sectionHeading}>Period Configuration</h3>
          <div className={styles.periodControls}>
            <div className={styles.controlGroup}>
              <label className={styles.label}>Number of Periods</label>
              <input
                type="number"
                value={numPeriods}
                onChange={(e) => setNumPeriods(Number(e.target.value))}
                className={styles.input}
                min="1"
                required
                disabled={loading}
              />
            </div>

            <div className={styles.controlGroup}>
              <label className={styles.label}>Starting Time</label>
              <input
                type="time"
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className={styles.input}
                required
                disabled={loading}
              />
            </div>

            <div className={styles.controlGroup}>
              <label className={styles.label}>Lesson Duration (minutes)</label>
              <input
                type="number"
                value={lessonDuration}
                onChange={(e) => setLessonDuration(Number(e.target.value))}
                className={styles.input}
                min="1"
                required
                disabled={loading}
              />
            </div>

            <button
              type="button"
              onClick={generatePeriods}
              className={styles.generateButton}
              disabled={loading || !numPeriods || !startTime || !lessonDuration}
            >
              {loading ? "Generating..." : "Generate Periods"}
            </button>
          </div>

          {Object.keys(periods).length > 0 && (
            <div className={styles.gridContainer}>
              <div className={styles.gridHeader}>
                {days.map((day) => (
                  <div key={day} className={styles.gridColumn}>
                    <div className={styles.dayHeader}>{day}</div>
                    {periods[day].map((time, i) => (
                      <div key={i} className={styles.timeSlot}>
                        {time}
                      </div>
                    ))}
                    <button
                      type="button"
                      className={styles.addButton}
                      onClick={() => addPeriod(day)}
                      disabled={loading}
                    >
                      +
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>

        <div className={styles.navigation}>
          <Link href="/" className={styles.secondaryButton} legacyBehavior>
            <a>← Back</a>
          </Link>

          <button
            type="submit"
            className={styles.primaryButton}
            disabled={loading || Object.keys(periods).length === 0}
          >
            {loading ? "Saving..." : "Save Configuration"}
          </button>

          <Link href="/components/ClassesConfig" className={styles.primaryButton} legacyBehavior>
            <a>Next →</a>
          </Link>
        </div>
      </form>
    </div>
  );
};

export default SchoolConfig;
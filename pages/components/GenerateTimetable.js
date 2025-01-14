import React, { useState } from 'react';
import Link from 'next/link';
import styles from './GenerateTimetable.module.css';

export default function GenerateTimetable() {
  const [loading, setLoading] = useState(false);

  const handleGenerateTimetable = () => {
    setLoading(true);

    
    setTimeout(() => {
      setLoading(false);
      alert('Timetable generated successfully!');
    }, 2000);
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.heading}>Generate Timetable</h1>
      <p className={styles.description}>
        Provide the necessary inputs below to create an optimized timetable.
      </p>

      <div className={styles.form}>
        <div className={styles.formGroup}>
          <label htmlFor="fixed-classes" className={styles.label}>
            Fixed Classes
          </label>
          <textarea
            id="fixed-classes"
            className={styles.textarea}
            placeholder="Enter details of fixed classes..."
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="teacher-preferences" className={styles.label}>
            Teacher Preferences
          </label>
          <textarea
            id="teacher-preferences"
            className={styles.textarea}
            placeholder="Enter teacher preferences and availability..."
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="room-availability" className={styles.label}>
            Room Availability
          </label>
          <textarea
            id="room-availability"
            className={styles.textarea}
            placeholder="Enter room availability and capacities..."
          />
        </div>

        <button
          className={styles.button}
          onClick={handleGenerateTimetable}
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Timetable'}
        </button>
      </div>

      <Link href="/dashboard" className={styles.backLink}>
        Back to Dashboard
      </Link>
    </div>
  );
}

import React from 'react';
import Link from 'next/link';
import styles from './Dashboard.module.css';

export default function Dashboard() {
  return (
    <div className={styles.dashboardContainer}>
      {/* Hero Section */}
      <header className={styles.heroSection}>
        <div className={styles.heroContent}>
          <h1>Welcome to Your Academic Scheduler</h1>
          <p>Easily manage timetables, teachers, and rooms all in one place.</p>
        </div>
      </header>

      {/* Main Section */}
      <main className={styles.main}>
        <section className={styles.cardContainer}>
          {/* Generate Timetable */}
          <div className={`${styles.card} ${styles.cardPrimary}`}>
            <i className="fas fa-calendar-alt"></i>
            <h3>Generate Timetable</h3>
            <p>Automatically create optimized schedules for your institution.</p>
            <Link href="/generate-timetable">
              <button className={styles.cardButton}>Start Now</button>
            </Link>
          </div>

          {/* Manage Teachers */}
          <div className={`${styles.card} ${styles.cardSecondary}`}>
            <i className="fas fa-chalkboard-teacher"></i>
            <h3>Manage Teachers</h3>
            <p>Organize teacher preferences and availability with ease.</p>
            <Link href="/manage-teachers">
              <button className={styles.cardButton}>Manage</button>
            </Link>
          </div>

          {/* Manage Rooms */}
          <div className={`${styles.card} ${styles.cardTertiary}`}>
            <i className="fas fa-door-open"></i>
            <h3>Manage Rooms</h3>
            <p>Track room availability and ensure proper usage.</p>
            <Link href="/manage-rooms">
              <button className={styles.cardButton}>Update</button>
            </Link>
          </div>

          {/* View Reports */}
          <div className={`${styles.card} ${styles.cardQuaternary}`}>
            <i className="fas fa-chart-bar"></i>
            <h3>View Reports</h3>
            <p>Analyze schedules and performance data effortlessly.</p>
            <Link href="/view-reports">
              <button className={styles.cardButton}>View</button>
            </Link>
          </div>
        </section>
      </main>
    </div>
  );
}

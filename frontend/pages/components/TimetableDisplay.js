import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import styles from './TimetableDisplay.module.css';
import Navbar from './Navbar';
import api from '../utils/api';

const TimetableDisplay = () => {
  const [timetable, setTimetable] = useState([]);
  const [days, setDays] = useState([]);
  const [timeSlots, setTimeSlots] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        const response = await api.get('/timetable/');
        setTimetable(response.data.entries);
        setDays(response.data.days);
        setTimeSlots(response.data.timeSlots);
      } catch (error) {
        console.error('Timetable fetch error:', error);
      }
    };
    fetchTimetable();
  }, []);

  return (
    <div className={styles.container}>
      <Navbar number={7} />
      
      <div className={styles.mainContent}>
        <h1 className={styles.mainHeading}>Generated Timetable</h1>
        
        <div className={styles.timetableGrid}>
          <div className={styles.gridHeader}>
            <div className={styles.timeColumn}></div>
            {days.map(day => (
              <div key={day} className={styles.dayHeader}>{day}</div>
            ))}
          </div>

          {timeSlots.map((timeSlot, index) => (
            <div key={index} className={styles.gridRow}>
              <div className={styles.timeSlot}>{timeSlot}</div>
              {days.map(day => {
                const entry = timetable.find(e => e.day === day && e.period === index + 1);
                return (
                  <div key={`${day}-${index}`} className={styles.gridCell}>
                    {entry && (
                      <>
                        <div className={styles.subject}>{entry.subject}</div>
                        <div className={styles.teacher}>{entry.teacher}</div>
                        <div className={styles.classroom}>{entry.classroom}</div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>

        <div className={styles.navigation}>
          <button 
            className={styles.secondaryButton}
            onClick={() => router.back()}
          >
            ← Back to Constraints
          </button>
        </div>
      </div>
    </div>
  );
};

export default TimetableDisplay;
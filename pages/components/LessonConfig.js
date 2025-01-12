import React, { useState } from 'react';
import PeriodsGrid from './PeriodsGrid';

const LessonConfig = () => {
  const [isTimetableGenerated, setIsTimetableGenerated] = useState(false);
  const [selectedDays, setSelectedDays] = useState(['Monday', 'Tuesday']); // Default selected days
  const [startTime, setStartTime] = useState('08:00'); // Default start time
  const [lessonDuration, setLessonDuration] = useState(60); // Default lesson duration
  const [periods, setPeriods] = useState(6); // Default number of periods

  const generateTimetable = () => {
    setIsTimetableGenerated(true);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Lesson Config</h1>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="startTime">Starting Time</label>
        <input
          type="time"
          id="startTime"
          value={startTime}
          onChange={(e) => setStartTime(e.target.value)}
          style={{ marginLeft: '10px' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="lessonDuration">Default Lesson Duration (minutes)</label>
        <input
          type="number"
          id="lessonDuration"
          value={lessonDuration}
          onChange={(e) => setLessonDuration(parseInt(e.target.value, 10))}
          style={{ marginLeft: '10px' }}
        />
      </div>
      <div style={{ marginBottom: '20px' }}>
        <label htmlFor="periods">Number of Periods</label>
        <input
          type="number"
          id="periods"
          value={periods}
          onChange={(e) => setPeriods(parseInt(e.target.value, 10))}
          style={{ marginLeft: '10px' }}
        />
      </div>
      <button
        style={{
          padding: '10px 20px',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px',
          cursor: 'pointer',
          marginTop: '20px',
        }}
        onClick={generateTimetable}
      >
        Generate Timetable
      </button>

      {isTimetableGenerated && (
        <PeriodsGrid
          selectedDays={selectedDays}
          startTime={startTime}
          lessonDuration={lessonDuration}
          periods={periods}
        />
      )}
    </div>
  );
};

export default LessonConfig;

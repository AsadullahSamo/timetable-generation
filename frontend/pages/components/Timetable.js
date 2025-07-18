import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from './Navbar';
import api from "../utils/api";

const Timetable = () => {
  const router = useRouter();
  const [timetableData, setTimetableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        const { data } = await api.get("/api/timetable/latest/");
        if (!data || !data.entries || !Array.isArray(data.entries)) {
          throw new Error("Invalid timetable data received");
        }
        console.log("Received timetable data:", data); // Debug log
        setTimetableData(data);
      } catch (err) {
        setError("Failed to load timetable. Please try again.");
        console.error("Timetable fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimetable();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={7} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="flex justify-center items-center h-full">
            <div className="text-center text-purple-400 italic">
              <i className="fas fa-spinner fa-spin text-4xl mb-4"></i>
              <p>Loading timetable...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={7} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-3xl text-gray-50 mb-8">Generated Timetable</h1>
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
          <div className="mt-8">
            <button 
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
              onClick={() => router.back()}
            >
              ← Back to Constraints
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!timetableData) return null;

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
      <Navbar number={7} />
      
      <div className="flex-1 p-8 max-w-7xl">
        <h1 className="text-3xl text-gray-50 mb-8">Generated Timetable</h1>
        
        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
          <div className="grid grid-cols-[120px_repeat(5,1fr)] gap-[1px] bg-gray-700 min-w-[1000px]">
            <div className="bg-gray-800 p-4 text-center sticky left-0 z-10"></div>
            {timetableData.days.map(day => (
              <div key={day} className="bg-gray-800 p-4 text-center font-semibold border-b-2 border-purple-500">
                {day}
              </div>
            ))}

            {timetableData.timeSlots.map((timeSlot, index) => (
              <React.Fragment key={index}>
                <div className="bg-gray-800 p-4 text-center sticky left-0 z-10">
                  {timeSlot}
                </div>
                {timetableData.days.map(day => {
                  // Normalize day names for matching
                  const normalizeDay = (dayName) => {
                    if (typeof dayName === 'string') {
                      return dayName.toUpperCase().substring(0, 3);
                    }
                    return dayName;
                  };

                  const entry = timetableData.entries.find(
                    e => normalizeDay(e.day) === normalizeDay(day) && e.period === (index + 1)
                  );
                  console.log(`Looking for entry: day=${day} (normalized: ${normalizeDay(day)}), period=${index + 1}, found:`, entry); // Debug log
                  return (
                    <div 
                      key={`${day}-${index}`} 
                      className={`p-4 min-h-[80px] flex flex-col justify-center gap-1 ${
                        index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'
                      }`}
                    >
                      {entry && (
                        <>
                          <div className="font-medium text-purple-400">{entry.subject}</div>
                          <div className="text-sm text-blue-400">{entry.teacher}</div>
                          <div className="text-xs text-emerald-400">{entry.classroom}</div>
                          <div className="text-xs text-gray-400">{entry.class_group}</div>
                        </>
                      )}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="mt-8">
          <button 
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            onClick={() => router.back()}
          >
            ← Back to Constraints
          </button>
        </div>
      </div>
    </div>
  );
};

export default Timetable;
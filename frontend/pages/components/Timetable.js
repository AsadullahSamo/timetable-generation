import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from './Navbar';
import api from "../utils/api";
import { generateTimetablePDF } from "../utils/pdfGenerator";

const Timetable = () => {
  console.log("Timetable component rendering"); // Debug log
  const router = useRouter();
  const [timetableData, setTimetableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedClassGroup, setSelectedClassGroup] = useState("");
  const [regenerating, setRegenerating] = useState(false);

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams();

        if (selectedClassGroup) {
          params.append('class_group', selectedClassGroup);
        }

        const { data } = await api.get(`/api/timetable/latest/?${params}`);
        console.log("Raw API response:", data); // Debug log
        
        if (!data || !data.entries || !Array.isArray(data.entries)) {
          throw new Error("Invalid timetable data received");
        }
        
        // Validate required fields
        if (!data.days || !data.timeSlots) {
          throw new Error("Missing required timetable structure (days or timeSlots)");
        }
        
        console.log("Received timetable data:", data); // Debug log
        console.log("Days:", data.days); // Debug log
        console.log("Time slots:", data.timeSlots); // Debug log
        console.log("Entries count:", data.entries.length); // Debug log
        
        setTimetableData(data);
        setError("");
      } catch (err) {
        // Handle specific case when no configuration exists (400 error)
        if (err.response?.status === 400) {
          setError("No schedule configuration found. Please set up Department Configuration first.");
        } else {
          setError("Failed to load timetable. Please try again.");
        }
        console.error("Timetable fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimetable();
  }, [selectedClassGroup]);

  const handleRegenerateTimetable = async () => {
    setRegenerating(true);
    try {
      await api.post('/api/timetable/regenerate/');
      setTimetableData(null); // Clear existing data
      setError("");
      setLoading(true); // Set loading state
      
      // Manually fetch new timetable data
      const params = new URLSearchParams();
      if (selectedClassGroup) {
        params.append('class_group', selectedClassGroup);
      }
      
      const { data } = await api.get(`/api/timetable/latest/?${params}`);
      if (!data || !data.entries || !Array.isArray(data.entries)) {
        throw new Error("Invalid timetable data received after regeneration");
      }
      console.log("Received new timetable data after regeneration:", data);
      setTimetableData(data);
      setLoading(false); // Clear loading state
    } catch (err) {
      setError("Failed to regenerate timetable. Please try again.");
      console.error("Regenerate timetable error:", err);
      setLoading(false); // Clear loading state on error
    } finally {
      setRegenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={8} />
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
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-3xl text-gray-50 mb-8">Generated Timetable</h1>
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
          <div className="mt-8 flex justify-between items-center">
            <button
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
              onClick={() => router.back()}
            >
              ← Back to Constraints
            </button>
            
            {/* Download Button (disabled when no data) */}
            <button
              disabled={true}
              className="px-6 py-3 bg-gray-600 text-gray-400 rounded-lg cursor-not-allowed"
            >
              <i className="fas fa-download mr-2"></i>
              Download PDF (No Data)
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!timetableData) return null;

  // Safety check for required properties
  if (!timetableData.days || !timetableData.timeSlots || !timetableData.entries) {
    console.error("Missing required timetable data:", timetableData);
    return (
      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
        <Navbar number={8} />
        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-3xl text-gray-50 mb-8">Generated Timetable</h1>
          <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
            Invalid timetable data structure. Please try refreshing the page.
          </div>
          <button
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            onClick={() => router.back()}
          >
            ← Back to Constraints
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans" suppressHydrationWarning>
      <Navbar number={8} />

      <div className="flex-1 p-8 max-w-7xl">
        <div className="flex justify-between items-start mb-8">
          <div>
            <h1 className="text-3xl text-gray-50 mb-2">Generated Timetable</h1>
            <p className="text-gray-400">
              View and manage your generated class schedules. Use the filter to view specific sections.
            </p>
          </div>
          
          {/* Regenerate Timetable Button */}
          <div className="flex flex-col items-end gap-3">
            <button
              onClick={handleRegenerateTimetable}
              disabled={regenerating}
              className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
                regenerating
                  ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
                  : 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-lg hover:shadow-green-500/25'
              }`}
            >
              {regenerating ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Regenerating...
                </>
              ) : (
                <>
                  <i className="fas fa-sync-alt mr-2"></i>
                  Regenerate Timetable
                </>
              )}
            </button>
            <p className="text-xs text-gray-500 text-right max-w-xs">
              Wipes existing data and generates<br/>a completely new timetable
            </p>
          </div>
        </div>

        {/* Section Filter */}
        {timetableData.pagination && (
          <div className="mb-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-300">Filter by Section:</label>
              <select
                value={selectedClassGroup}
                onChange={(e) => setSelectedClassGroup(e.target.value)}
                className="bg-gray-700 border border-gray-600 text-gray-100 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                {[...new Set(timetableData.pagination.class_groups || [])]
                  .sort((a, b) => {
                    // Sort sections properly (21SW-I, 21SW-II, 21SW-III, 22SW-I, etc.)
                    const [batchA, sectionA] = a.split('-');
                    const [batchB, sectionB] = b.split('-');
                    if (batchA !== batchB) return batchA.localeCompare(batchB);
                    return (sectionA || '').localeCompare(sectionB || '');
                  })
                  .map(group => (
                  <option key={group} value={group}>
                    {group.includes('-') ? `${group.split('-')[0]} Section ${group.split('-')[1]}` : group}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        <div className="bg-gray-800 rounded-lg border border-gray-700 overflow-x-auto">
          <div className="grid grid-cols-[120px_repeat(5,1fr)] gap-[1px] bg-gray-700 min-w-[1000px]">
            <div className="bg-gray-800 p-4 text-center sticky left-0 z-10"></div>
            {(timetableData.days || []).map(day => (
              <div key={day} className="bg-gray-800 p-4 text-center font-semibold border-b-2 border-purple-500">
                {day}
              </div>
            ))}

            {(timetableData.timeSlots || []).map((timeSlot, index) => (
              <React.Fragment key={index}>
                <div className="bg-gray-800 p-4 text-center sticky left-0 z-10">
                  {timeSlot}
                </div>
                {(timetableData.days || []).map(day => {
                  // Normalize day names for matching
                  const normalizeDay = (dayName) => {
                    if (typeof dayName === 'string') {
                      return dayName.toUpperCase().substring(0, 3);
                    }
                    return dayName;
                  };

                  const entry = (timetableData.entries || []).find(
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
                          <div className="font-medium text-purple-400">{entry.subject_code || entry.subject}</div>
                          <div className="text-sm text-blue-400">{entry.teacher}</div>
                          <div className="text-xs text-emerald-400">{entry.classroom}</div>
                          <div className="text-xs text-gray-400">
                            {entry.class_group.includes('-') ?
                              `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
                              entry.class_group
                            }
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="mt-8 flex justify-between items-center">
          <button
            className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            onClick={() => router.back()}
          >
            ← Back to Constraints
          </button>
          
          {/* Bottom Download Button */}
          <button
            onClick={async () => {
              try {
                await generateTimetablePDF(timetableData, selectedClassGroup);
              } catch (error) {
                console.error('Failed to generate PDF:', error);
                // You can add a user notification here if needed
              }
            }}
            className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-all duration-200 hover:shadow-lg hover:shadow-green-500/25"
          >
            <i className="fas fa-download mr-2"></i>
            Download Timetable PDF
          </button>
        </div>
      </div>
    </div>
  );
};

export default Timetable;

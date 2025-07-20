import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from './Navbar';
import api from "../utils/api";

const Timetable = () => {
  const router = useRouter();
  const [timetableData, setTimetableData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(5);
  const [selectedClassGroup, setSelectedClassGroup] = useState("");

  useEffect(() => {
    const fetchTimetable = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          page: currentPage.toString(),
          page_size: pageSize.toString()
        });

        if (selectedClassGroup) {
          params.append('class_group', selectedClassGroup);
        }

        const { data } = await api.get(`/api/timetable/latest/?${params}`);
        if (!data || !data.entries || !Array.isArray(data.entries)) {
          throw new Error("Invalid timetable data received");
        }
        console.log("Received timetable data:", data); // Debug log
        setTimetableData(data);
        setError("");
      } catch (err) {
        setError("Failed to load timetable. Please try again.");
        console.error("Timetable fetch error:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchTimetable();
  }, [currentPage, pageSize, selectedClassGroup]);

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

        {/* Pagination and Filter Controls */}
        {timetableData.pagination && (
          <div className="mb-6 bg-gray-800 rounded-lg border border-gray-700 p-4">
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              {/* Class Group Filter - ENHANCED for Sections */}
              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-300">Filter by Section:</label>
                <select
                  value={selectedClassGroup}
                  onChange={(e) => {
                    setSelectedClassGroup(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="bg-gray-700 border border-gray-600 text-gray-100 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="">All Sections</option>
                  {[...new Set(timetableData.pagination.class_groups)]  // FIXED: Remove duplicates
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

              {/* Page Size Control */}
              <div className="flex items-center gap-3">
                <label className="text-sm text-gray-300">Classes per page:</label>
                <select
                  value={pageSize}
                  onChange={(e) => {
                    setPageSize(parseInt(e.target.value));
                    setCurrentPage(1);
                  }}
                  className="bg-gray-700 border border-gray-600 text-gray-100 px-3 py-2 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value={1}>1</option>
                  <option value={3}>3</option>
                  <option value={5}>5</option>
                  <option value={10}>10</option>
                </select>
              </div>

              {/* Pagination Info */}
              <div className="text-sm text-gray-400">
                Page {timetableData.pagination.current_page} of {timetableData.pagination.total_pages}
                {timetableData.pagination.current_class_groups.length > 0 && (
                  <span className="ml-2">
                    (Showing: {timetableData.pagination.current_class_groups.join(', ')})
                  </span>
                )}
              </div>
            </div>

            {/* Pagination Buttons */}
            <div className="flex justify-center mt-4 gap-2">
              <button
                onClick={() => setCurrentPage(1)}
                disabled={!timetableData.pagination.has_previous}
                className="px-3 py-2 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                First
              </button>
              <button
                onClick={() => setCurrentPage(currentPage - 1)}
                disabled={!timetableData.pagination.has_previous}
                className="px-3 py-2 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Previous
              </button>

              {/* Page Numbers */}
              {Array.from({ length: Math.min(5, timetableData.pagination.total_pages) }, (_, i) => {
                const pageNum = Math.max(1, Math.min(
                  timetableData.pagination.total_pages - 4,
                  currentPage - 2
                )) + i;
                if (pageNum <= timetableData.pagination.total_pages) {
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setCurrentPage(pageNum)}
                      className={`px-3 py-2 rounded-md transition-colors ${
                        pageNum === currentPage
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {pageNum}
                    </button>
                  );
                }
                return null;
              })}

              <button
                onClick={() => setCurrentPage(currentPage + 1)}
                disabled={!timetableData.pagination.has_next}
                className="px-3 py-2 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Next
              </button>
              <button
                onClick={() => setCurrentPage(timetableData.pagination.total_pages)}
                disabled={!timetableData.pagination.has_next}
                className="px-3 py-2 bg-gray-700 text-gray-300 rounded-md hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Last
              </button>
            </div>
          </div>
        )}

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
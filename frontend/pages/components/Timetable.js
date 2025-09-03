import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Navbar from './Navbar';
import BackButton from './BackButton';
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
  const [editMode, setEditMode] = useState(false);
  const [draggingEntry, setDraggingEntry] = useState(null);
  const [message, setMessage] = useState(null);
  const [moveUIForEntry, setMoveUIForEntry] = useState(null);
  const [moveDay, setMoveDay] = useState('');
  const [movePeriod, setMovePeriod] = useState('');
  const [safeSlotsByEntry, setSafeSlotsByEntry] = useState({});
  const [safeSlotsLoadingFor, setSafeSlotsLoadingFor] = useState(null);
  const [safeSlotsErrorFor, setSafeSlotsErrorFor] = useState(null);
  const [downloadingPDF, setDownloadingPDF] = useState(false);

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
            <BackButton href="/components/DepartmentConfig" label="Back: Department Config" />
            
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
          <BackButton href="/components/DepartmentConfig" label="Back: Department Config" />
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
          
          {/* Controls */}
          <div className="flex flex-col items-end gap-3">
            <div className="flex items-center gap-3">
              <label className="text-sm text-gray-300">Edit Mode</label>
              <button
                onClick={() => setEditMode(!editMode)}
                className={`px-4 py-2 rounded-md ${editMode ? 'bg-amber-600' : 'bg-gray-700'} text-white`}
              >
                {editMode ? 'On' : 'Off'}
              </button>
            </div>
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

        {message && (
          <div className={`mb-4 p-3 rounded ${message.type === 'error' ? 'bg-red-900/50 text-red-200' : 'bg-emerald-900/40 text-emerald-200'}`}>
            {message.text}
          </div>
        )}

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

        {/* Extra Classes Legend */}
        <div className="mb-4 bg-yellow-900/20 border border-yellow-400/30 rounded-lg p-3">
          <div className="flex items-center gap-2 text-yellow-300">
            <span className="text-yellow-400 font-bold">*</span>
            <span className="text-sm">Extra Classes: Additional classes scheduled in leftover slots after main classes</span>
          </div>
        </div>

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
                  console.log(`Looking for entry: day=${day} (normalized: ${normalizeDay(day)}), period=${index + 1}, found:`, entry, 'is_extra_class:', entry?.is_extra_class); // Debug log
                  return (
                    <div
                      key={`${day}-${index}`}
                      className={`p-4 min-h-[80px] flex flex-col justify-center gap-1 ${
                        index % 2 === 0 ? 'bg-gray-800' : 'bg-gray-900'
                      } ${editMode ? 'outline outline-1 outline-gray-700' : ''} ${
                        entry && entry.is_extra_class ? 'border-2 border-yellow-400 bg-yellow-900/20 shadow-lg shadow-yellow-400/20' : ''
                      }`}
                      onDragOver={(e) => {
                        if (!editMode) return;
                        e.preventDefault();
                      }}
                      onDrop={async (e) => {
                        if (!editMode || !draggingEntry) return;
                        e.preventDefault();
                        try {
                          const res = await api.post(`/api/timetable/slots/${draggingEntry.id}/move/`, {
                            day: day,
                            period: index + 1,
                          });
                          // Optimistically update UI to clear old slot
                          setTimetableData(prev => {
                            if (!prev) return prev;
                            const updated = { ...prev, entries: [...(prev.entries || [])] };
                            const idx = updated.entries.findIndex(en => en.id === draggingEntry.id);
                            if (idx !== -1) {
                              updated.entries[idx] = { ...updated.entries[idx], day, period: index + 1 };
                            }
                            return updated;
                          });
                          // Refresh entries to keep labels in sync
                          const params = new URLSearchParams();
                          if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                          const latest = await api.get(`/api/timetable/latest/?${params}`);
                          setTimetableData(latest.data);
                          setMessage({ type: 'success', text: 'Slot moved successfully' });
                        } catch (err) {
                          const msg = err.response?.data?.detail || 'Move failed due to constraints';
                          setMessage({ type: 'error', text: msg });
                        } finally {
                          setDraggingEntry(null);
                          setTimeout(() => setMessage(null), 2500);
                        }
                      }}
                    >
                      {entry && (
                        <>
                          <div
                            className={`font-medium text-purple-400 ${editMode ? 'cursor-move' : ''}`}
                            draggable={editMode}
                            onDragStart={() => setDraggingEntry(entry)}
                          >
<<<<<<< HEAD
                            <div className="flex items-center gap-1">
                              {(entry.subject_short_name || entry.subject_code || entry.subject)}
                              {entry.is_extra_class && (
                                <span className="text-yellow-400 font-bold text-lg" title="Extra Class">*</span>
                              )}
                            </div>
=======
                            {entry.subject_code || entry.subject}
>>>>>>> 42e11d456e3c7c354f489a7d48bfd43f88bb2f8d
                          </div>
                          <div className="text-sm text-blue-400">{entry.teacher}</div>
                          <div className="text-xs text-emerald-400">{entry.classroom}</div>
                          <div className="text-xs text-gray-400">
                            {entry.class_group.includes('-') ?
                              `${entry.class_group.split('-')[0]} Sec ${entry.class_group.split('-')[1]}` :
                              entry.class_group
                            }
                          </div>
                          {editMode && (
                            <div className="mt-2 flex gap-2 items-center">
                              {/* Shift arrows removed as requested */}
                              <button
                                className="text-xs px-2 py-1 bg-blue-700 rounded"
                                onClick={async () => {
                                  const open = moveUIForEntry === entry.id
                                  setMoveUIForEntry(open ? null : entry.id)
                                  setSafeSlotsErrorFor(null)
                                  if (!open) {
                                    setMoveDay(entry.day)
                                    setMovePeriod(entry.period)
                                    setSafeSlotsLoadingFor(entry.id || `${entry.day}-${entry.period}`)
                                    try {
                                      let entryId = entry.id
                                      if (!entryId) {
                                        const params = new URLSearchParams();
                                        if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                        const latest = await api.get(`/api/timetable/latest/?${params}`)
                                        setTimetableData(latest.data)
                                        const refreshed = (latest.data.entries || []).find(
                                          e => (e.day?.toUpperCase().substring(0,3) === (entry.day?.toUpperCase().substring(0,3))) && e.period === entry.period
                                        )
                                        entryId = refreshed?.id
                                      }
                                      if (!entryId) throw new Error('Missing entry id')
                                      const res = await api.get(`/api/timetable/slots/${entryId}/safe-moves/`)
                                      const safe = res.data?.safe_slots || []
                                      setSafeSlotsByEntry(prev => ({ ...prev, [entryId]: safe }))
                                    } catch (err) {
                                      setSafeSlotsErrorFor(entry.id || `${entry.day}-${entry.period}`)
                                      setMessage({ type: 'error', text: 'Failed to fetch safe slots' })
                                      setTimeout(() => setMessage(null), 2200)
                                    } finally {
                                      setSafeSlotsLoadingFor(null)
                                    }
                                  }
                                }}
                              >Move…</button>
                              <button
                                className="text-xs px-2 py-1 bg-red-700 rounded"
                                onClick={async () => {
                                  if (!confirm('Delete this slot?')) return
                                  try {
                                    await api.delete(`/api/timetable/slots/${entry.id}/`)
                                    setTimetableData(prev => ({
                                      ...prev,
                                      entries: prev.entries.filter(en => en.id !== entry.id)
                                    }))
                                    setMessage({ type: 'success', text: 'Slot deleted' })
                                  } catch (err) {
                                    const msg = err.response?.data?.detail || 'Delete failed'
                                    setMessage({ type: 'error', text: msg })
                                  } finally {
                                    setTimeout(() => setMessage(null), 2000)
                                  }
                                }}
                              >Delete</button>
                            </div>
                          )}
                          {editMode && moveUIForEntry === entry.id && (
                            <div className="mt-2 p-2 bg-gray-800 rounded border border-gray-700 flex flex-wrap gap-2 items-center">
                              {safeSlotsLoadingFor === entry.id && (
                                <span className="text-xs text-gray-400">Loading safe slots…</span>
                              )}
                              {safeSlotsErrorFor === entry.id && (
                                <span className="text-xs text-red-300">Failed to load safe slots</span>
                              )}
                              {!!safeSlotsByEntry[entry.id]?.length && (
                                <div className="w-full flex flex-wrap gap-2 mt-1">
                                  {safeSlotsByEntry[entry.id].map((s) => (
                                    <button
                                      key={`${s.day}-${s.period}`}
                                      className={`text-xs px-2 py-1 rounded border ${moveDay===s.day && movePeriod===s.period ? 'bg-green-700 border-green-500' : 'bg-gray-700 border-gray-600'}`}
                                onClick={async () => {
                                        // Directly move to the chosen safe slot for a smoother UX
                                        setMoveDay(s.day);
                                        setMovePeriod(s.period);
                                        try {
                                          setMessage({ type: 'info', text: `Moving to ${s.day} · P${s.period}...` })
                                          let entryId = entry.id
                                          if (!entryId) {
                                            const params = new URLSearchParams();
                                            if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                            const latest = await api.get(`/api/timetable/latest/?${params}`)
                                            setTimetableData(latest.data)
                                            const refreshed = (latest.data.entries || []).find(
                                              e => (e.day?.toUpperCase().substring(0,3) === (entry.day?.toUpperCase().substring(0,3))) && e.period === entry.period
                                            )
                                            entryId = refreshed?.id
                                          }
                                          if (!entryId) throw new Error('Missing entry id')
                                          await api.post(`/api/timetable/slots/${entryId}/move/`, { day: s.day, period: s.period })
                                          // Optimistically update UI to clear old slot and show new
                                          setTimetableData(prev => {
                                            if (!prev) return prev;
                                            const updated = { ...prev, entries: [...(prev.entries || [])] };
                                            const idx = updated.entries.findIndex(en => en.id === entryId);
                                            if (idx !== -1) {
                                              updated.entries[idx] = { ...updated.entries[idx], day: s.day, period: s.period };
                                            }
                                            return updated;
                                          });
                                    const params = new URLSearchParams();
                                    if (selectedClassGroup) params.append('class_group', selectedClassGroup);
                                    const latest = await api.get(`/api/timetable/latest/?${params}`);
                                    setTimetableData(latest.data);
                                    setMoveUIForEntry(null)
                                          setMessage({ type: 'success', text: `Moved to ${s.day}, period ${s.period}` })
                                  } catch (err) {
                                          const msg = err.response?.data?.detail || err.message || 'Move failed'
                                    setMessage({ type: 'error', text: msg })
                                  } finally {
                                    setTimeout(() => setMessage(null), 2200)
                                  }
                                }}
                                    >{s.day} · P{s.period}</button>
                                  ))}
                                </div>
                              )}
                              <button
                                className="text-xs px-2 py-1 bg-gray-700 rounded"
                                onClick={() => setMoveUIForEntry(null)}
                              >Cancel</button>
                            </div>
                          )}
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
          <BackButton href="/components/DepartmentConfig" label="Back: Department Config" />
          
          {/* Bottom Download Button */}
          <button
            onClick={async () => {
              try {
                setDownloadingPDF(true);
                await generateTimetablePDF(timetableData, selectedClassGroup);
              } catch (error) {
                console.error('Failed to generate PDF:', error);
                // You can add a user notification here if needed
              } finally {
                setDownloadingPDF(false);
              }
            }}
            disabled={downloadingPDF}
            className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
              downloadingPDF 
                ? 'bg-gray-500 cursor-not-allowed' 
                : 'bg-green-600 hover:bg-green-700 hover:shadow-lg hover:shadow-green-500/25'
            } text-white`}
          >
            {downloadingPDF ? (
              <>
                <i className="fas fa-spinner fa-spin mr-2"></i>
                Generating PDF...
              </>
            ) : (
              <>
                <i className="fas fa-download mr-2"></i>
                Download Timetable PDF
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Timetable;
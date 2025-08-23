import React, { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";
import { Building2, Clock, Plus, ArrowLeft, ArrowRight, Loader2, Info, Coffee, Trash2, BookOpen, Users } from 'lucide-react';

const DepartmentConfig = () => {
  const router = useRouter();
  const [departmentName, setDepartmentName] = useState("");
  const [numPeriods, setNumPeriods] = useState(0);
  const [startTime, setStartTime] = useState("08:00");
  const [days] = useState(["Mon", "Tue", "Wed", "Thu", "Fri"]);
      const [classDuration, setClassDuration] = useState(60);
  const [periods, setPeriods] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState("");

  // New states for subject-batch assignment
  const [subjects, setSubjects] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loadingSubjects, setLoadingSubjects] = useState(true);

  // Fetch subjects and batches on component mount
  useEffect(() => {
    fetchSubjects();
    fetchBatches();
  }, []);

  const fetchSubjects = async () => {
    try {
      const response = await api.get('/api/timetable/subjects/');
      setSubjects(response.data);
    } catch (error) {
      setError('Failed to load subjects');
      console.error('Error fetching subjects:', error);
    } finally {
      setLoadingSubjects(false);
    }
  };

  const fetchBatches = async () => {
    try {
      const response = await api.get('/api/timetable/batches/');
      setBatches(response.data);
    } catch (error) {
      console.error('Error fetching batches:', error);
      setError('Failed to fetch batches');
    }
  };

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

  const addBreakPeriod = (day, index) => {
    const newPeriods = { ...periods };
    const breakTime = "Break";
    newPeriods[day].splice(index + 1, 0, breakTime);
    setPeriods(newPeriods);
  };

  const removePeriod = (day, index) => {
    const newPeriods = { ...periods };
    newPeriods[day].splice(index, 1);
    setPeriods(newPeriods);
  };



  const toggleSubjectForBatch = async (batchName, subjectId) => {
    try {
      const subject = subjects.find(s => s.id === subjectId);
      const newBatch = subject.batch === batchName ? '' : batchName;

      await api.patch(`/api/timetable/subjects/${subjectId}/`, {
        batch: newBatch
      });

      // Update local state
      setSubjects(prev => prev.map(s =>
        s.id === subjectId ? { ...s, batch: newBatch } : s
      ));

      setSuccess(`Subject ${newBatch ? 'assigned to' : 'removed from'} ${batchName}`);
      setTimeout(() => setSuccess(''), 3000);
    } catch (error) {
      console.error('Error updating subject batch:', error);
      setError('Failed to update subject assignment');
      setTimeout(() => setError(''), 3000);
    }
  };

  const isSubjectAssignedToBatch = (batchName, subjectId) => {
    const subject = subjects.find(s => s.id === subjectId);
    return subject?.batch === batchName;
  };

  const validateConfiguration = () => {
    if (!departmentName.trim()) {
      setError("Department name is required.");
      return false;
    }

    if (numPeriods < 1) {
      setError("Number of periods must be at least 1.");
      return false;
    }
            if (classDuration < 30) {
              setError("Class duration should be at least 30 minutes.");
      return false;
    }
    return true;
  };

  const generatePeriods = () => {
    if (!validateConfiguration()) {
      return;
    }

            if (!numPeriods || !startTime || !classDuration) {
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
        dayTime = incrementTime(dayTime, classDuration);
      }
    });

    setPeriods(newPeriods);
    setError(null); // Clear any previous errors
  };

  const addPeriod = (day) => {
    // Find the last non-break period
    const lastNonBreakPeriod = [...periods[day]].reverse().find(period => period !== "Break");
    if (!lastNonBreakPeriod) {
      // If no non-break period found, use the start time
              const newTime = incrementTime(startTime, classDuration);
      setPeriods(prev => ({
        ...prev,
        [day]: [...prev[day], formatTime(newTime)]
      }));
      return;
    }

    const [time, period] = lastNonBreakPeriod.split(" ");
    let [hours, minutes] = time.split(":").map(Number);

    if (period === "PM" && hours !== 12) hours += 12;
    if (period === "AM" && hours === 12) hours = 0;

            const newTime = incrementTime(`${hours}:${minutes}`, classDuration);

    setPeriods(prev => ({
      ...prev,
      [day]: [...prev[day], formatTime(newTime)]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateConfiguration()) {
      return;
    }
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

      const response = await api.post("/api/timetable/schedule-configs/", {
        name: departmentName,
        days,
        periods: Array.from({length: numPeriods}, (_, i) => (i + 1).toString()),
        start_time: formattedStartTime,
        class_duration: classDuration,
        constraints: {},
        semester: "Fall 2024",
        academic_year: "2024-2025"
      });

      if (response.status === 201) {
        // Just show success message, don't redirect to timetable
        setError(null);
        alert("Department Configuration saved successfully!");
        // Stay on the same page so user can continue with other configurations
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
    <div className="flex min-h-screen bg-background text-primary font-sans">
      <Navbar number={6} />

      <div className="flex-1 p-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
            Department Configuration
          </h1>
          <p className="text-secondary/90">Set up your department's basic information and schedule</p>
        </div>

        {error && (
          <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6">
            <p className="text-red-500 text-sm font-medium">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <section className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <Building2 className="h-5 w-5 text-accent-cyan" />
                Department Information
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("department")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "department" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    Enter your department's name and basic schedule information. This will be used throughout the system.
                  </div>
                )}
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-secondary block mb-2">Department Name</label>
                <input
                  type="text"
                  value={departmentName}
                  onChange={(e) => setDepartmentName(e.target.value)}
                  className="w-full pl-4 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  placeholder="Enter department name"
                  required
                  disabled={loading}
                />
              </div>


            </div>
          </section>

          <section className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <Clock className="h-5 w-5 text-accent-cyan" />
                Period Configuration
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("periods")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "periods" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    Configure your daily schedule. You can add breaks between periods and customize the timing for each day.
                  </div>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Number of Periods</label>
                <input
                  type="number"
                  value={numPeriods}
                  onChange={(e) => setNumPeriods(Number(e.target.value))}
                  className="w-full pl-4 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  min="1"
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Starting Time</label>
                <input
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                  className="w-full pl-4 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  required
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Class Duration (minutes)</label>
                <input
                  type="number"
                                      value={classDuration}
                                      onChange={(e) => setClassDuration(Number(e.target.value))}
                  className="w-full pl-4 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  min="1"
                  required
                  disabled={loading}
                />
              </div>

              <div className="flex items-end">
                <button
                  type="button"
                  onClick={generatePeriods}
                  className="w-full py-3 px-4 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={loading || !numPeriods || !startTime || !classDuration}
                >
                  {loading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    "Generate Periods"
                  )}
                </button>
              </div>
            </div>

            {Object.keys(periods).length > 0 && (
              <div className="mt-6">
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  {days.map((day) => (
                    <div key={day} className="bg-background/95 rounded-xl p-4 border border-border">
                      <div className="text-accent-cyan font-medium mb-4">{day}</div>
                      <div className="space-y-2">
                        {periods[day].map((time, i) => (
                          <div
                            key={i}
                            className="group px-3 py-2 bg-surface rounded-lg text-sm text-primary/90 relative hover:bg-surface/80 transition-colors"
                          >
                            <div className="flex items-center justify-between">
                              <span>{time}</span>
                              <div className="opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-2">
                                {time !== "Break" && (
                                  <button
                                    type="button"
                                    onClick={() => addBreakPeriod(day, i)}
                                    className="text-secondary hover:text-accent-cyan transition-colors"
                                    title="Add break after this period"
                                  >
                                    <Coffee className="h-4 w-4" />
                                  </button>
                                )}
                                <button
                                  type="button"
                                  onClick={() => removePeriod(day, i)}
                                  className="text-secondary hover:text-red-500 transition-colors"
                                  title="Remove this period"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </div>
                          </div>
                        ))}
                        <button
                          type="button"
                          className="w-full py-2 border-2 border-dashed border-border text-secondary rounded-lg hover:border-accent-cyan hover:text-accent-cyan transition-colors disabled:opacity-50 group"
                          onClick={() => addPeriod(day)}
                          disabled={loading}
                        >
                          <Plus className="h-4 w-4 mx-auto group-hover:scale-110 transition-transform" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Batch-Subject Assignment Section */}
          {subjects.length > 0 && (
            <section className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                  <BookOpen className="h-5 w-5 text-accent-cyan" />
                  Batch Subject Management
                </h2>
                <div className="text-sm text-secondary">
                  Manage which subjects belong to each batch
                </div>
              </div>

              {loadingSubjects ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin text-accent-cyan" />
                  <span className="ml-2 text-secondary">Loading subjects...</span>
                </div>
              ) : (
                <div className="space-y-6">
                  {batches.map((batch) => (
                    <div key={batch.name} className="bg-background/95 rounded-xl p-4 border border-border">
                      <div className="flex items-center gap-2 mb-4">
                        <Users className="h-4 w-4 text-accent-cyan" />
                        <h3 className="font-medium text-primary">{batch.name}</h3>
                        <span className="text-sm text-secondary">
                          ({subjects.filter(s => s.batch === batch.name).length} subjects assigned)
                        </span>
                        <span className="text-xs text-secondary/70">
                          {batch.description} • {batch.total_sections} sections
                        </span>
                      </div>

                      <div className="space-y-4">
                        {/* Show assigned subjects */}
                        <div>
                          <h4 className="text-sm font-medium text-primary mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 bg-accent-cyan rounded-full"></span>
                            Assigned Subjects ({subjects.filter(subject => subject.batch === batch.name).length})
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                            {subjects
                              .filter(subject => subject.batch === batch.name)
                              .map((subject) => (
                                <div
                                  key={subject.id}
                                  className="p-3 rounded-lg bg-accent-cyan/10 border border-accent-cyan/30 text-accent-cyan group hover:bg-accent-cyan/15 transition-all"
                                >
                                  <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                      <div className="font-medium text-sm">{subject.code}</div>
                                      <div className="text-xs opacity-75 truncate">{subject.name}</div>
                                    </div>
                                    <div className="flex items-center gap-2 ml-2">
                                      <span className="text-xs whitespace-nowrap">
                                        {subject.credits} cr
                                        {subject.is_practical && (
                                          <span className="ml-1 text-accent-pink font-medium">Lab</span>
                                        )}
                                      </span>
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          toggleSubjectForBatch(batch.name, subject.id);
                                        }}
                                        className="opacity-0 group-hover:opacity-100 text-accent-cyan hover:text-red-500 transition-all text-lg leading-none"
                                        title="Remove from batch"
                                      >
                                        ×
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              ))}
                          </div>
                          {subjects.filter(subject => subject.batch === batch.name).length === 0 && (
                            <div className="text-sm text-secondary/70 italic p-4 text-center bg-surface/30 rounded-lg border border-dashed border-border">
                              No subjects assigned to this batch yet
                            </div>
                          )}
                        </div>

                        {/* Show unassigned subjects for assignment */}
                        <div>
                          <h4 className="text-sm font-medium text-primary mb-3 flex items-center gap-2">
                            <span className="w-2 h-2 bg-secondary/50 rounded-full"></span>
                            Available Subjects ({subjects.filter(subject => !subject.batch || subject.batch === '').length})
                          </h4>
                          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                            {subjects
                              .filter(subject => !subject.batch || subject.batch === '')
                              .map((subject) => (
                                <div
                                  key={subject.id}
                                  onClick={() => toggleSubjectForBatch(batch.name, subject.id)}
                                  className="p-3 rounded-lg bg-surface/50 border border-border text-secondary hover:border-accent-cyan/30 hover:text-primary cursor-pointer transition-all hover:bg-surface/70"
                                >
                                  <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                      <div className="font-medium text-sm">{subject.code}</div>
                                      <div className="text-xs opacity-75 truncate">{subject.name}</div>
                                    </div>
                                    <div className="text-xs whitespace-nowrap ml-2">
                                      {subject.credits} cr
                                      {subject.is_practical && (
                                        <span className="ml-1 text-accent-pink font-medium">Lab</span>
                                      )}
                                    </div>
                                  </div>
                                </div>
                              ))}
                          </div>
                          {subjects.filter(subject => !subject.batch || subject.batch === '').length === 0 && (
                            <div className="text-sm text-secondary/70 italic p-4 text-center bg-surface/30 rounded-lg border border-dashed border-border">
                              All subjects are assigned to batches
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </section>
          )}

          <div className="flex justify-between mt-8">
            <Link
              href="/components/Classrooms"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Classrooms
            </Link>

            <div className="flex gap-4">
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={loading || Object.keys(periods).length === 0}
              >
                {loading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  "Save Configuration"
                )}
              </button>

              <Link
                href="/components/Constraints"
                className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
              >
                Next: Constraints
                <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DepartmentConfig;

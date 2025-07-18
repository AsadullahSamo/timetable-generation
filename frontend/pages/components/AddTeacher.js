import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import api from "../utils/api";
import Head from "next/head";
import Link from "next/link";
import { 
  User, 
  Mail, 
  Clock, 
  BookOpen, 
  Save, 
  X, 
  AlertCircle, 
  Loader2, 
  CalendarClock,
  BookMarked,
  Info,
  ArrowLeft,
  Calendar,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';
import Navbar from "./Navbar";

const AddTeacher = () => {
  const router = useRouter();
  const { id } = router.query;
  
  // Form states
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [subjects, setSubjects] = useState([]);
  const [allSubjects, setAllSubjects] = useState([]);
  const [maxLessons, setMaxLessons] = useState(4);
  // Internal availability state: { day: { periodIndex: mode } }
  const [availabilityState, setAvailabilityState] = useState({});
  const [timetableConfig, setTimetableConfig] = useState(null);
  
  // Separate loading states:
  const [configLoading, setConfigLoading] = useState(true);
  const [teacherLoading, setTeacherLoading] = useState(false);
  const [error, setError] = useState("");
  const [showTooltip, setShowTooltip] = useState("");
  
  // Active mode selector: "preferable" or "mandatory"
  const [activeMode, setActiveMode] = useState("preferable");
  const [formErrors, setFormErrors] = useState({});

  // Fetch configuration and subjects once on mount.
  useEffect(() => {
    const fetchConfigAndSubjects = async () => {
      try {
        const configRes = await api.get("/api/timetable/configs/");
        if (configRes.data.length > 0) {
          // Get the latest config (highest ID) that has generated_periods
          const latestConfig = configRes.data
            .filter(config => config.generated_periods && Object.keys(config.generated_periods).length > 0)
            .sort((a, b) => b.id - a.id)[0];

          if (latestConfig) {
            setTimetableConfig(latestConfig);
          } else {
            setError("No timetable configuration with generated periods found. Please complete Department Configuration first.");
          }
        }
        const subjectsRes = await api.get("/api/timetable/subjects/");
        setAllSubjects(subjectsRes.data);
      } catch (err) {
        setError("Failed to load configuration or subjects.");
      } finally {
        setConfigLoading(false);
      }
    };
    fetchConfigAndSubjects();
  }, []);

  // Fetch teacher data if editing
  useEffect(() => {
    const fetchTeacher = async () => {
      if (!id) return;
      try {
        const { data } = await api.get(`/api/timetable/teachers/${id}/`);
        setName(data.name);
        setEmail(data.email);
        setSubjects(data.subjects || []);
        setMaxLessons(data.max_lessons_per_day);
        // Convert availability data to internal state
        const newState = {};
        if (data.unavailable_periods) {
          // Handle both mandatory and preferable slots
          for (const mode of ['mandatory', 'preferable']) {
            const dayData = data.unavailable_periods[mode] || {};
            for (const [day, times] of Object.entries(dayData)) {
              if (!newState[day]) newState[day] = {};
              times.forEach(time => {
                const periodIndex = timetableConfig?.generated_periods[day]?.findIndex(p => p === time);
                if (periodIndex !== -1 && periodIndex !== undefined) {
                  newState[day][periodIndex] = mode;
                }
              });
            }
          }
        }
        setAvailabilityState(newState);
      } catch (err) {
        setError("Failed to load teacher data.");
      }
    };
    if (timetableConfig) {
      fetchTeacher();
    }
  }, [id, timetableConfig]);

  const validateForm = () => {
    const errors = {};
    
    if (!name.trim()) {
      errors.name = "Teacher name is required";
    }
    
    if (!email.trim()) {
      errors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      errors.email = "Please enter a valid email address";
    }
    
    if (maxLessons < 1) {
      errors.maxLessons = "Must be at least 1 lesson per day";
    }
    
    if (subjects.length === 0) {
      errors.subjects = "Please select at least one subject";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!validateForm()) {
      // Scroll to the top to show errors
      window.scrollTo(0, 0);
      return;
    }
    
    setTeacherLoading(true);

    try {
      const availability = convertAvailability();
      const teacherData = {
        name,
        email,
        subjects,
        max_lessons_per_day: maxLessons,
        unavailable_periods: availability
      };

      if (id) {
        await api.put(`/api/timetable/teachers/${id}/`, teacherData);
      } else {
        await api.post("/api/timetable/teachers/", teacherData);
      }
      router.push("/components/Teachers");
    } catch (err) {
      console.error('Error response:', err.response?.data);
      setError(err.response?.data?.detail || "Failed to save teacher.");
      window.scrollTo(0, 0);
    } finally {
      setTeacherLoading(false);
    }
  };

  // Combine loading states for rendering:
  const isLoading = configLoading || teacherLoading;

  const handleSubjectChange = (subjectId) => {
    setSubjects(prev =>
      prev.includes(subjectId)
        ? prev.filter((id) => id !== subjectId)
        : [...prev, subjectId]
    );
    
    // Clear subject error when selection changes
    if (formErrors.subjects) {
      setFormErrors(prev => ({
        ...prev,
        subjects: undefined
      }));
    }
  };

  // Toggle the state for a given day and period index.
  const toggleTimeSlot = (day, periodIndex) => {
    setAvailabilityState(prev => {
      const newState = { ...prev };
      const dayState = newState[day] ? { ...newState[day] } : {};
      if (dayState[periodIndex] === activeMode) {
        // If cell is already set to active mode, remove it.
        delete dayState[periodIndex];
      } else {
        // Otherwise, set cell to active mode.
        dayState[periodIndex] = activeMode;
      }
      newState[day] = dayState;
      return newState;
    });
  };

  // Convert internal availabilityState into final JSON format:
  // { mandatory: { day: [time, ...], ... }, preferable: { day: [time, ...], ... } }
  const convertAvailability = () => {
    const result = { mandatory: {}, preferable: {} };
    if (!timetableConfig || !timetableConfig.generated_periods) return result;
    
    // Then populate the times
    for (const [day, periodsObj] of Object.entries(availabilityState)) {
      for (const [periodIndexStr, cellMode] of Object.entries(periodsObj)) {
        const periodIndex = parseInt(periodIndexStr, 10);
        const dayPeriods = timetableConfig.generated_periods[day] || [];
        const time = dayPeriods[periodIndex];
        if (time) {
          if (!result[cellMode][day]) {
            result[cellMode][day] = [];
          }
          result[cellMode][day].push(time);
        }
      }
    }

    return result;
  };

  // Get time slot class based on its status
  const getTimeSlotClass = (day, periodIndex) => {
    const mode = availabilityState[day]?.[periodIndex];
    
    if (!mode) {
      return "bg-background/80 border border-border hover:border-accent-cyan/30";
    }
    
    if (mode === "mandatory") {
      return "bg-red-500/20 border border-red-500/30 text-red-500";
    }
    
    if (mode === "preferable") {
      return "bg-amber-500/20 border border-amber-500/30 text-amber-500";
    }
    
    return "bg-background/80 border border-border";
  };

  if (isLoading) {
    return (
      <>
        <Head>
          <title>{id ? "Edit Teacher" : "Add New Teacher"}</title>
        </Head>
        <div className="flex min-h-screen bg-background text-primary font-sans">
          <Navbar number={4} />
          <div className="flex-1 p-8 max-w-7xl mx-auto">
            <div className="flex justify-center items-center h-full">
              <div className="text-center">
                <Loader2 className="h-12 w-12 animate-spin text-accent-cyan mx-auto mb-4" />
                <p className="text-secondary">Loading...</p>
              </div>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>{id ? "Edit Teacher" : "Add New Teacher"}</title>
      </Head>
      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={4} />
        <div className="flex-1 p-8 max-w-7xl mx-auto">
          <div className="mb-8">
            <Link 
              href="/components/Teachers"
              className="flex items-center gap-2 text-secondary hover:text-primary transition-colors mb-4"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Teachers
            </Link>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              {id ? "Edit Teacher" : "Add New Teacher"}
            </h1>
            <p className="text-secondary/90">
              {id ? "Update teacher information and availability" : "Create a new teacher and set their availability"}
            </p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}
          
          {formErrors.subjects && (
            <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-500" />
              <p className="text-amber-500 text-sm font-medium">{formErrors.subjects}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                  <User className="h-5 w-5 text-accent-cyan" />
                  Basic Information
                </h2>
                <div className="relative">
                  <button
                    type="button"
                    className="text-secondary hover:text-primary transition-colors"
                    onMouseEnter={() => setShowTooltip("basic")}
                    onMouseLeave={() => setShowTooltip("")}
                  >
                    <Info className="h-5 w-5" />
                  </button>
                  {showTooltip === "basic" && (
                    <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                      Enter teacher's name, email, and maximum number of lessons they can teach per day.
                    </div>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Name*</label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => {
                        setName(e.target.value);
                        if (formErrors.name) {
                          setFormErrors({...formErrors, name: undefined});
                        }
                      }}
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.name ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                      placeholder="Enter teacher name"
                      required
                    />
                  </div>
                  {formErrors.name && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.name}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Email*</label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => {
                        setEmail(e.target.value);
                        if (formErrors.email) {
                          setFormErrors({...formErrors, email: undefined});
                        }
                      }}
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.email ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                      placeholder="email@example.com"
                      required
                    />
                  </div>
                  {formErrors.email && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.email}</p>
                  )}
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Max Lessons per Day*</label>
                  <div className="relative">
                    <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      value={maxLessons}
                      onChange={(e) => {
                        setMaxLessons(Math.max(1, parseInt(e.target.value) || 1));
                        if (formErrors.maxLessons) {
                          setFormErrors({...formErrors, maxLessons: undefined});
                        }
                      }}
                      min="1"
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.maxLessons ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                      required
                    />
                  </div>
                  {formErrors.maxLessons && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.maxLessons}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                  <BookMarked className="h-5 w-5 text-accent-cyan" />
                  Assigned Subjects
                </h2>
                <div className="relative">
                  <button
                    type="button"
                    className="text-secondary hover:text-primary transition-colors"
                    onMouseEnter={() => setShowTooltip("subjects")}
                    onMouseLeave={() => setShowTooltip("")}
                  >
                    <Info className="h-5 w-5" />
                  </button>
                  {showTooltip === "subjects" && (
                    <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                      Select all subjects that this teacher can teach. Click on a subject to select/deselect it.
                    </div>
                  )}
                </div>
              </div>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                {allSubjects.map((subject) => (
                  <div
                    key={subject.id}
                    onClick={() => handleSubjectChange(subject.id)}
                    className={`p-4 text-center rounded-xl border cursor-pointer transition-all flex flex-col items-center justify-center gap-2 ${
                      subjects.includes(subject.id)
                        ? "bg-accent-cyan/10 border-accent-cyan text-primary shadow-sm"
                        : "bg-background/80 border-border hover:border-accent-cyan/30"
                    }`}
                  >
                    <BookOpen className={`h-5 w-5 ${subjects.includes(subject.id) ? 'text-accent-cyan' : 'text-secondary/70'}`} />
                    <span>{subject.name}</span>
                    {subjects.includes(subject.id) && (
                      <CheckCircle2 className="h-4 w-4 text-accent-cyan" />
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                  <Calendar className="h-5 w-5 text-accent-cyan" />
                  Availability
                </h2>
                <div className="relative">
                  <button
                    type="button"
                    className="text-secondary hover:text-primary transition-colors"
                    onMouseEnter={() => setShowTooltip("availability")}
                    onMouseLeave={() => setShowTooltip("")}
                  >
                    <Info className="h-5 w-5" />
                  </button>
                  {showTooltip === "availability" && (
                    <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                      <p>Define when the teacher is unavailable or has preferred teaching times:</p>
                      <ul className="mt-2 list-disc list-inside space-y-1">
                        <li>Click a time slot to mark it</li>
                        <li><span className="text-red-500">Red</span>: Unavailable times</li>
                        <li><span className="text-amber-500">Yellow</span>: Preferred times</li>
                      </ul>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="flex items-center gap-4 mb-6">
                <button
                  type="button"
                  onClick={() => setActiveMode("mandatory")}
                  className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-colors ${
                    activeMode === "mandatory"
                      ? "bg-red-500/20 text-red-500 border border-red-500/30 font-medium"
                      : "bg-background/80 text-secondary border border-border"
                  }`}
                >
                  <X className="h-4 w-4" />
                  Unavailable Times
                </button>
                <button
                  type="button"
                  onClick={() => setActiveMode("preferable")}
                  className={`px-4 py-2 rounded-xl flex items-center gap-2 transition-colors ${
                    activeMode === "preferable"
                      ? "bg-amber-500/20 text-amber-500 border border-amber-500/30 font-medium"
                      : "bg-background/80 text-secondary border border-border"
                  }`}
                >
                  <CheckCircle2 className="h-4 w-4" />
                  Preferred Times
                </button>
              </div>
              
              {timetableConfig && timetableConfig.generated_periods ? (
                <div className="space-y-6">
                  {Object.entries(timetableConfig.generated_periods).map(([day, times]) => (
                    <div key={day}>
                      <h3 className="text-md font-medium text-primary mb-3">{day}</h3>
                      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                        {times.map((time, idx) => (
                          <button
                            key={`${day}-${idx}`}
                            type="button"
                            onClick={() => toggleTimeSlot(day, idx)}
                            className={`py-3 px-4 rounded-lg text-center transition-colors ${getTimeSlotClass(day, idx)}`}
                          >
                            <span className="text-sm">{time}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-secondary">
                  <p>No timetable configuration with generated periods available.</p>
                  <p className="text-sm mt-2">Please complete Department Configuration and generate periods first.</p>
                </div>
              )}
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={teacherLoading}
              >
                {teacherLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Save className="h-5 w-5" />
                )}
                {id ? "Update Teacher" : "Save Teacher"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </>
  );
};

export default AddTeacher;



// frontend/pages/components/TeachersConfig.js
import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";
import { 
  User, 
  Search, 
  Plus, 
  Edit2, 
  Trash2, 
  Info, 
  Loader2, 
  ArrowLeft, 
  ArrowRight,
  AlertCircle,
  X,
  BarChart3,
  BookOpen,
  Clock,
  Mail,
  Filter,
  Users,
  CalendarClock,
  Briefcase,
  Check,
  ChevronDown,
  Calendar,
  CheckCircle2,
  BookMarked
} from 'lucide-react';

const TeachersConfig = () => {
  const [teachers, setTeachers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showTooltip, setShowTooltip] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [activeTeacher, setActiveTeacher] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [filterSubject, setFilterSubject] = useState("");
  const [showFilterMenu, setShowFilterMenu] = useState(false);
  const [weekDays, setWeekDays] = useState(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']);
  const [timetableConfig, setTimetableConfig] = useState(null);
  const [availabilityMode, setAvailabilityMode] = useState('mandatory');
  
  // Stats calculation
  const stats = {
    totalTeachers: teachers.length,
    totalSubjects: [...new Set(teachers.flatMap(t => t.subject_names || []))].length,
    avgLessonsPerDay: teachers.length 
      ? (teachers.reduce((acc, t) => acc + t.max_lessons_per_day, 0) / teachers.length).toFixed(1) 
      : 0
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [teachersRes, subjectsRes, configRes, assignmentsRes] = await Promise.all([
          api.get("/api/timetable/teachers/"),
          api.get("/api/timetable/subjects/"),
          api.get("/api/timetable/schedule-configs/"),
          api.get("/api/timetable/teacher-assignments/")
        ]);
        
        setTeachers(teachersRes.data);
        setSubjects(subjectsRes.data);
        setAssignments(assignmentsRes.data);
        
        if (configRes.data.length > 0) {
          // Get the latest config (highest ID) that has generated_periods
          const latestConfig = configRes.data
            .filter(config => config.generated_periods && Object.keys(config.generated_periods).length > 0)
            .sort((a, b) => b.id - a.id)[0];

          if (latestConfig) {
            setTimetableConfig(latestConfig);
            // Get weekdays from config
            const configDays = Object.keys(latestConfig.generated_periods || {});
            if (configDays.length > 0) {
              setWeekDays(configDays);
            }
          }
        }
      } catch (err) {
        setError("Failed to load data. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Get teacher assignments
  const getTeacherAssignments = (teacherId) => {
    return assignments.filter(assignment => assignment.teacher === teacherId);
  };

  const handleDelete = async (id) => {
    setShowDeleteConfirm(id);
  };
  
  const confirmDelete = async () => {
    try {
      await api.delete(`/api/timetable/teachers/${showDeleteConfirm}/`);
      setTeachers(teachers.filter(teacher => teacher.id !== showDeleteConfirm));
      setShowDeleteConfirm(null);
    } catch (err) {
      setError("Delete failed - teacher might be in use.");
      setShowDeleteConfirm(null);
    }
  };

  const handleEdit = (id) => {
    window.location.href = `/components/AddTeacher?id=${id}`;
  };
  
  const handleViewTeacher = (id) => {
    setActiveTeacher(activeTeacher === id ? null : id);
  };

  // Apply all filters
  const filteredTeachers = teachers.filter(teacher => {
    const matchesSearch = 
      teacher.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      teacher.email.toLowerCase().includes(searchQuery.toLowerCase());
      
    const matchesSubject = 
      !filterSubject || 
      (teacher.subject_names && teacher.subject_names.includes(filterSubject));
      
    return matchesSearch && matchesSubject;
  });
  
  // Get teacher availability for visualization
  const getAvailabilityStatus = (teacher, day, mode = 'mandatory') => {
    if (!teacher.unavailable_periods || !teacher.unavailable_periods[mode]) {
      return { unavailable: false, times: [] };
    }
    
    const unavailableTimes = teacher.unavailable_periods[mode][day] || [];
    return {
      unavailable: unavailableTimes.length > 0,
      times: unavailableTimes
    };
  };

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={3} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Teachers Configuration
            </h1>
            <p className="text-secondary/90">Manage teachers, their subjects, and availability</p>
          </div>
          
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Stats Summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <Users className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Total Teachers</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.totalTeachers}</p>
            </div>
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <BookOpen className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Subjects Covered</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.totalSubjects}</p>
            </div>
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Avg. Lessons/Day</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.avgLessonsPerDay}</p>
            </div>
          </div>

          <div className="flex flex-col md:flex-row justify-between items-start mb-8 gap-4">
            {/* Search & Filter */}
            <div className="flex flex-col md:flex-row gap-4 w-full md:w-auto">
              <div className="relative flex-1 md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search teachers..."
                  className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                />
              </div>
              
              <div className="relative">
                <button 
                  onClick={() => setShowFilterMenu(!showFilterMenu)}
                  className="flex items-center gap-2 px-4 py-3 bg-background/95 border border-border rounded-xl text-primary hover:border-accent-cyan/30 transition-colors"
                >
                  <Filter className="h-4 w-4" />
                  <span>{filterSubject || "Filter by Subject"}</span>
                  <ChevronDown className="h-4 w-4" />
                </button>
                
                {showFilterMenu && (
                  <div className="absolute left-0 top-full mt-2 w-64 bg-surface border border-border rounded-xl shadow-lg z-40">
                    <div className="p-2">
                      <button 
                        onClick={() => {
                          setFilterSubject("");
                          setShowFilterMenu(false);
                        }}
                        className="flex items-center gap-2 w-full p-2 hover:bg-background/50 rounded-lg text-left"
                      >
                        <Check className={`h-4 w-4 ${!filterSubject ? 'opacity-100' : 'opacity-0'}`} />
                        <span>All Subjects</span>
                      </button>
                      {subjects.map(subject => (
                        <button
                          key={subject.id}
                          onClick={() => {
                            setFilterSubject(subject.name);
                            setShowFilterMenu(false);
                          }}
                          className="flex items-center gap-2 w-full p-2 hover:bg-background/50 rounded-lg text-left"
                        >
                          <Check className={`h-4 w-4 ${filterSubject === subject.name ? 'opacity-100' : 'opacity-0'}`} />
                          <span>{subject.name}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="relative">
                <button 
                  onClick={() => setAvailabilityMode(availabilityMode === 'mandatory' ? 'preferable' : 'mandatory')}
                  className={`flex items-center gap-2 px-4 py-3 rounded-xl ${
                    availabilityMode === 'mandatory' 
                      ? 'bg-red-500/20 text-red-500 border border-red-500/30' 
                      : 'bg-amber-500/20 text-amber-500 border border-amber-500/30'
                  }`}
                >
                  <CalendarClock className="h-4 w-4" />
                  <span>{availabilityMode === 'mandatory' ? 'Unavailable' : 'Preferred'}</span>
                </button>
              </div>
            </div>
            
            <Link
              href="/components/AddTeacher"
              className="px-4 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 whitespace-nowrap"
            >
              <Plus className="h-4 w-4" />
              Add New Teacher
            </Link>
          </div>

          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <User className="h-5 w-5 text-accent-cyan" />
                Teacher List
              </h2>
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("table")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-5 w-5" />
                </button>
                {showTooltip === "table" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                    <p>Manage your teachers and view their availability.</p>
                    <ul className="mt-2 list-disc list-inside">
                      <li>Click a row to see teacher details</li>
                      <li>Red cells indicate unavailable times</li>
                      <li>Yellow cells indicate preferred times</li>
                    </ul>
                  </div>
                )}
              </div>
            </div>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-8 w-8 text-accent-cyan animate-spin" />
              </div>
            ) : (
              <div className="overflow-x-auto">
                {filteredTeachers.length === 0 ? (
                  <div className="text-center py-8 text-secondary">
                    <User className="h-12 w-12 mx-auto mb-4 opacity-30" />
                    <p>
                      {searchQuery || filterSubject
                        ? "No teachers found matching your search"
                        : "No teachers added yet"
                      }
                    </p>
                  </div>
                ) : (
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-background/95">
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Teacher Name</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Email</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Subject Assignments</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Max</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Availability</th>
                        <th className="px-4 py-3 text-center border border-border text-secondary font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredTeachers.map((teacher) => (
                        <React.Fragment key={teacher.id}>
                          <tr 
                            className={`hover:bg-background/50 transition-colors cursor-pointer ${
                              activeTeacher === teacher.id ? 'bg-accent-cyan/5' : ''
                            }`}
                            onClick={() => handleViewTeacher(teacher.id)}
                          >
                            <td className="px-4 py-3 border border-border">
                              <div className="flex items-center gap-2">
                                <User className="h-4 w-4 text-accent-cyan" />
                                {teacher.name}
                                {activeTeacher === teacher.id && (
                                  <CheckCircle2 className="h-4 w-4 text-accent-cyan ml-auto" />
                                )}
                              </div>
                            </td>
                            <td className="px-4 py-3 border border-border">
                              <div className="flex items-center gap-2">
                                <Mail className="h-4 w-4 text-secondary/70" />
                                <span className="text-secondary">{teacher.email}</span>
                              </div>
                            </td>
                            <td className="px-4 py-3 border border-border">
                              {(() => {
                                const teacherAssignments = getTeacherAssignments(teacher.id);
                                if (teacherAssignments.length === 0) {
                                  return <span className="text-secondary/60 text-sm">No assignments</span>;
                                }
                                return (
                                  <div className="space-y-1">
                                    {teacherAssignments.map((assignment, index) => (
                                      <div key={index} className="text-sm">
                                        <span className="font-medium text-primary">{assignment.subject_name}</span>
                                        <div className="text-secondary/70 text-xs">
                                          {assignment.batch_name} - Sections: {assignment.sections?.join(', ') || 'All'}
                                        </div>
                                      </div>
                                    ))}
                                  </div>
                                );
                              })()}
                            </td>
                            <td className="px-4 py-3 border border-border text-center">
                              <span className="flex items-center justify-center gap-1">
                                <Clock className="h-4 w-4 text-secondary/70" />
                                {teacher.max_lessons_per_day}
                              </span>
                            </td>
                            <td className="px-4 py-3 border border-border">
                              <div className="flex items-center gap-1">
                                {weekDays.map((day) => {
                                  const { unavailable } = getAvailabilityStatus(teacher, day, availabilityMode);
                                  return (
                                    <div
                                      key={day}
                                      className={`w-5 h-5 rounded-sm flex items-center justify-center text-xs ${
                                        unavailable
                                          ? availabilityMode === 'mandatory'
                                            ? 'bg-red-500/20 border border-red-500/30'
                                            : 'bg-amber-500/20 border border-amber-500/30'
                                          : 'bg-background/50 border border-border'
                                      }`}
                                      title={`${day} - ${unavailable ? 'Unavailable' : 'Available'}`}
                                    >
                                      {day[0]}
                                    </div>
                                  );
                                })}
                              </div>
                            </td>
                            <td className="px-4 py-3 border border-border">
                              <div className="flex items-center justify-center gap-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleEdit(teacher.id);
                                  }}
                                  className="text-secondary hover:text-accent-cyan transition-colors"
                                  title="Edit teacher"
                                >
                                  <Edit2 className="h-4 w-4" />
                                </button>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDelete(teacher.id);
                                  }}
                                  className="text-secondary hover:text-red-500 transition-colors"
                                  title="Delete teacher"
                                >
                                  <Trash2 className="h-4 w-4" />
                                </button>
                              </div>
                            </td>
                          </tr>
                          {activeTeacher === teacher.id && (
                            <tr className="bg-background/30">
                              <td colSpan={6} className="px-4 py-4 border border-border">
                                <div className="space-y-4">
                                  <h3 className="font-medium flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-accent-cyan" />
                                    {availabilityMode === 'mandatory' ? 'Unavailable Times' : 'Preferred Times'}
                                  </h3>
                                  
                                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                                    {weekDays.map((day) => {
                                      const { unavailable, times } = getAvailabilityStatus(teacher, day, availabilityMode);
                                      return (
                                        <div key={day} className="space-y-2">
                                          <h4 className="text-sm font-medium text-secondary">{day}</h4>
                                          {unavailable ? (
                                            <div className="space-y-1">
                                              {times.map((time, idx) => (
                                                <div 
                                                  key={idx} 
                                                  className={`text-sm px-3 py-2 rounded-lg ${
                                                    availabilityMode === 'mandatory'
                                                      ? 'bg-red-500/10 text-red-500 border border-red-500/20'
                                                      : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                                                  }`}
                                                >
                                                  {time}
                                                </div>
                                              ))}
                                            </div>
                                          ) : (
                                            <div className="text-sm text-secondary italic">
                                              {availabilityMode === 'mandatory'
                                                ? 'Available all day'
                                                : 'No preferred times'
                                              }
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/Subjects"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>

            <Link
              href="/components/Classrooms"
              className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
            >
              Next
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-surface p-6 rounded-2xl border border-border shadow-lg max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-primary">Confirm Delete</h3>
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="text-secondary hover:text-primary transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <p className="text-secondary mb-6">
              Are you sure you want to delete this teacher? This action cannot be undone.
            </p>
            <div className="flex justify-end gap-4">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TeachersConfig;


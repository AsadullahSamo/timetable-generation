// frontend/pages/components/TeachersConfig.js
import React, { useState, useEffect } from "react";
import Head from "next/head";
import ResponsiveLayout from "./ResponsiveLayout";
import ResponsiveCard, { ResponsiveGrid } from "./ResponsiveCard";
import ResponsiveTable, { ResponsiveTableRow, ResponsiveTableCell } from "./ResponsiveTable";
import Link from "next/link";
import BackButton from "./BackButton";
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
  Users,
  CalendarClock,
  Briefcase,
  Calendar,
  CheckCircle2,
  BookMarked,
  Shield
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
  const [weekDays, setWeekDays] = useState(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']);
  const [timetableConfig, setTimetableConfig] = useState(null);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [deleteAllLoading, setDeleteAllLoading] = useState(false);
  const [success, setSuccess] = useState("");
  
  // Stats calculation
  const stats = {
    totalTeachers: teachers.length,
    totalSubjects: [...new Set(teachers.flatMap(t => t.subject_names || []))].length,
            avgClassesPerDay: teachers.length
            ? (teachers.reduce((acc, t) => acc + t.max_classes_per_day, 0) / teachers.length).toFixed(1)
            : 0
  };

  // Helper function to generate time slots from config
  const generateTimeSlots = (config) => {
    if (!config || !config.start_time || !config.class_duration || !config.periods) {
      return {};
    }

    const timeSlots = {};
    const days = config.days || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'];
    
    days.forEach(day => {
      timeSlots[day] = [];
      let currentTime = new Date(`2000-01-01T${config.start_time}`);
      
      for (let i = 0; i < config.periods.length; i++) {
        const startTimeString = currentTime.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
        
        // Calculate end time
        const endTime = new Date(currentTime);
        endTime.setMinutes(endTime.getMinutes() + config.class_duration);
        const endTimeString = endTime.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
        
        // Create time range string
        const timeRangeString = `${startTimeString} - ${endTimeString}`;
        timeSlots[day].push(timeRangeString);
        
        // Add class duration for next iteration
        currentTime.setMinutes(currentTime.getMinutes() + config.class_duration);
      }
    });
    
    return timeSlots;
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
          // Get the latest config (highest ID)
          const latestConfig = configRes.data
            .sort((a, b) => b.id - a.id)[0];

          if (latestConfig) {
            setTimetableConfig(latestConfig);
            // Get weekdays from config
            const timeSlots = generateTimeSlots(latestConfig);
            const configDays = Object.keys(timeSlots);
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

  const handleDeleteAllTeachers = async () => {
    try {
      setDeleteAllLoading(true);
      const response = await api.delete('/api/timetable/data-management/teachers/');
      
      if (response.data.success) {
        setTeachers([]);
        setError("");
        setShowDeleteAllConfirm(false);
        setSuccess(`Deleted ${response.data.deleted_counts.teachers} teachers, ${response.data.deleted_counts.teacher_assignments} assignments, ${response.data.deleted_counts.timetable_entries} timetable entries.`);
        setTimeout(() => setSuccess(""), 3000);
      } else {
        setError("Failed to delete all teachers");
      }
    } catch (err) {
      setError("Failed to delete all teachers");
      console.error("Delete all teachers error:", err);
    } finally {
      setDeleteAllLoading(false);
    }
  };

  const handleEdit = (id) => {
    window.location.href = `/components/AddTeacher?id=${id}`;
  };
  
  const handleViewTeacher = (id) => {
    setActiveTeacher(activeTeacher === id ? null : id);
  };

  // Apply all filters
  const filteredTeachers = teachers.filter(teacher => 
    teacher.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
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

      <ResponsiveLayout>
        <div className="space-y-6 sm:space-y-8">
          <div className="mb-6 sm:mb-8">
            <h1 className="text-xl sm:text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Teachers Configuration
            </h1>
            <p className="text-secondary/90 text-sm sm:text-base">Manage teachers, their subjects, and availability</p>
          </div>
          
          {error && (
            <div className="p-3 sm:p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-4 sm:mb-6 flex items-center gap-2">
              <AlertCircle className="h-4 sm:h-5 w-4 sm:w-5 text-red-500 flex-shrink-0" />
              <p className="text-red-500 text-xs sm:text-sm font-medium">{error}</p>
            </div>
          )}

          {success && (
            <div className="p-3 sm:p-4 bg-green-500/10 border border-green-500/20 rounded-xl mb-4 sm:mb-6 flex items-center gap-2">
              <CheckCircle2 className="h-4 sm:h-5 w-4 sm:w-5 text-green-500 flex-shrink-0" />
              <p className="text-green-500 text-xs sm:text-sm font-medium">{success}</p>
            </div>
          )}

          {/* Stats Summary */}
          <ResponsiveGrid cols={{ xs: 1, sm: 2, lg: 3 }} className="mb-6 sm:mb-8">
            <ResponsiveCard>
              <div className="flex items-center gap-3 mb-2">
                <Users className="h-4 sm:h-5 w-4 sm:w-5 text-accent-cyan" />
                <h3 className="text-xs sm:text-sm font-medium text-secondary">Total Teachers</h3>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-primary">{stats.totalTeachers}</p>
            </ResponsiveCard>
            <ResponsiveCard>
              <div className="flex items-center gap-3 mb-2">
                <BookOpen className="h-4 sm:h-5 w-4 sm:w-5 text-accent-cyan" />
                <h3 className="text-xs sm:text-sm font-medium text-secondary">Subjects Covered</h3>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-primary">{stats.totalSubjects}</p>
            </ResponsiveCard>
            <ResponsiveCard>
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-4 sm:h-5 w-4 sm:w-5 text-accent-cyan" />
                <h3 className="text-xs sm:text-sm font-medium text-secondary">Avg. Classes/Day</h3>
              </div>
              <p className="text-xl sm:text-2xl font-bold text-primary">{stats.avgClassesPerDay}</p>
            </ResponsiveCard>
          </ResponsiveGrid>

          <div className="flex flex-col lg:flex-row justify-between items-start mb-6 sm:mb-8 gap-4">
            {/* Search */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full lg:w-auto">
              <div className="relative flex-1 sm:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by teacher name..."
                  className="w-full pl-10 pr-4 py-2.5 sm:py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30 text-sm sm:text-base"
                />
              </div>
              
              <div className="relative">
                <div className="flex items-center gap-2 px-3 sm:px-4 py-2.5 sm:py-3 rounded-xl bg-red-500/20 text-red-500 border border-red-500/30">
                  <CalendarClock className="h-4 w-4" />
                  <span className="text-xs sm:text-sm">Unavailable Times</span>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 w-full lg:w-auto">
              {teachers.length > 0 && (
                <button
                  onClick={() => setShowDeleteAllConfirm(true)}
                  className="flex items-center justify-center gap-2 px-3 sm:px-4 py-2.5 sm:py-3 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 hover:shadow-lg transition-all duration-300 text-sm sm:text-base"
                >
                  <Trash2 className="h-4 w-4" />
                  <span className="hidden sm:inline">Delete All Teachers</span>
                  <span className="sm:hidden">Delete All</span>
                </button>
              )}
              <Link
                href="/components/AddTeacher"
                className="px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 whitespace-nowrap text-sm sm:text-base"
              >
                <Plus className="h-4 w-4" />
                <span className="hidden sm:inline">Add New Teacher</span>
                <span className="sm:hidden">Add Teacher</span>
              </Link>
            </div>
          </div>

          <ResponsiveCard 
            title="Teacher List" 
            headerActions={
              <div className="relative">
                <button
                  type="button"
                  className="text-secondary hover:text-primary transition-colors"
                  onMouseEnter={() => setShowTooltip("table")}
                  onMouseLeave={() => setShowTooltip("")}
                >
                  <Info className="h-4 sm:h-5 w-4 sm:w-5" />
                </button>
                {showTooltip === "table" && (
                  <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-xs sm:text-sm text-secondary w-48 sm:w-64 z-50">
                    <p>Manage your teachers and view their availability.</p>
                    <ul className="mt-2 list-disc list-inside space-y-1">
                      <li>Click a row to see teacher details</li>
                      <li>Red cells indicate unavailable times</li>
                    </ul>
                  </div>
                )}
              </div>
            }
            className="mb-6 sm:mb-8"
          >

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="h-6 sm:h-8 w-6 sm:w-8 text-accent-cyan animate-spin" />
              </div>
            ) : (
              <>
                {filteredTeachers.length === 0 ? (
                  <div className="text-center py-8 text-secondary">
                    <User className="h-8 sm:h-12 w-8 sm:w-12 mx-auto mb-4 opacity-30" />
                    <p className="text-sm sm:text-base">
                      {searchQuery
                        ? "No teachers found matching your search"
                        : "No teachers added yet"
                      }
                    </p>
                  </div>
                ) : (
                  <ResponsiveTable 
                    headers={["Teacher Name", "Subject Assignments", "Max Classes", "Availability", "Actions"]}
                  >
                    {filteredTeachers.map((teacher) => (
                      <React.Fragment key={teacher.id}>
                        <ResponsiveTableRow 
                          className={`cursor-pointer ${
                            activeTeacher === teacher.id ? 'bg-accent-cyan/5' : ''
                          }`}
                          onClick={() => handleViewTeacher(teacher.id)}
                        >
                          <ResponsiveTableCell>
                            <div className="flex items-center gap-2">
                              <User className="h-4 w-4 text-accent-cyan flex-shrink-0" />
                              <span className="text-sm sm:text-base truncate">{teacher.name}</span>
                              {activeTeacher === teacher.id && (
                                <CheckCircle2 className="h-4 w-4 text-accent-cyan ml-auto flex-shrink-0" />
                              )}
                            </div>
                          </ResponsiveTableCell>
                          <ResponsiveTableCell>
                            {(() => {
                              const teacherAssignments = getTeacherAssignments(teacher.id);
                              if (teacherAssignments.length === 0) {
                                return <span className="text-secondary/60 text-xs sm:text-sm">No assignments</span>;
                              }
                              return (
                                <div className="space-y-1">
                                  {teacherAssignments.map((assignment, index) => (
                                    <div key={index} className="text-xs sm:text-sm">
                                      <span className="font-medium text-primary">{assignment.subject_name}</span>
                                      <div className="text-secondary/70 text-xs">
                                        {assignment.batch_name} - Sections: {assignment.sections?.join(', ') || 'All'}
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              );
                            })()}
                          </ResponsiveTableCell>
                          <ResponsiveTableCell className="text-center">
                            <span className="flex items-center justify-center gap-1">
                              <Clock className="h-4 w-4 text-secondary/70" />
                              <span className="text-sm sm:text-base">{teacher.max_classes_per_day}</span>
                            </span>
                          </ResponsiveTableCell>
                          <ResponsiveTableCell>
                            <div className="flex items-center gap-1">
                              {weekDays.map((day) => {
                                const { unavailable } = getAvailabilityStatus(teacher, day, 'mandatory');
                                return (
                                  <div
                                    key={day}
                                    className={`w-4 sm:w-5 h-4 sm:h-5 rounded-sm flex items-center justify-center text-xs ${
                                      unavailable
                                        ? 'bg-red-500/20 border border-red-500/30'
                                        : 'bg-background/50 border border-border'
                                    }`}
                                    title={`${day} - ${unavailable ? 'Unavailable' : 'Available'}`}
                                  >
                                    {day[0]}
                                  </div>
                                );
                              })}
                            </div>
                          </ResponsiveTableCell>
                          <ResponsiveTableCell className="text-center">
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
                          </ResponsiveTableCell>
                        </ResponsiveTableRow>
                          {activeTeacher === teacher.id && (
                            <tr className="bg-background/30">
                              <td colSpan={5} className="px-4 py-4 border border-border">
                                <div className="space-y-4">
                                  <h3 className="font-medium flex items-center gap-2">
                                    <Calendar className="h-4 w-4 text-accent-cyan" />
                                    Unavailable Times
                                  </h3>
                                  
                                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                                    {weekDays.map((day) => {
                                      const { unavailable, times } = getAvailabilityStatus(teacher, day, 'mandatory');
                                      return (
                                        <div key={day} className="space-y-2">
                                          <h4 className="text-sm font-medium text-secondary">{day}</h4>
                                          {unavailable ? (
                                            <div className="space-y-1">
                                              {times.map((time, idx) => (
                                                <div 
                                                  key={idx} 
                                                  className="text-sm px-3 py-2 rounded-lg bg-red-500/10 text-red-500 border border-red-500/20"
                                                >
                                                  {time}
                                                </div>
                                              ))}
                                            </div>
                                          ) : (
                                            <div className="text-sm text-secondary italic">
                                              Available all day
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
                  </ResponsiveTable>
                )}
              </>
            )}
          </ResponsiveCard>

          <div className="flex flex-col sm:flex-row justify-between items-center gap-4 mt-6 sm:mt-8">
            <BackButton href="/components/Subjects" label="Back: Subjects" />

            <Link
              href="/components/Classrooms"
              className="px-4 sm:px-6 py-2.5 sm:py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 text-sm sm:text-base w-full sm:w-auto"
            >
              <span className="hidden sm:inline">Next: Classrooms</span>
              <span className="sm:hidden">Next: Classrooms</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </ResponsiveLayout>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-surface p-4 sm:p-6 rounded-2xl border border-border shadow-lg max-w-md w-full">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base sm:text-lg font-semibold text-primary">Confirm Delete</h3>
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="text-secondary hover:text-primary transition-colors"
              >
                <X className="h-4 sm:h-5 w-4 sm:w-5" />
              </button>
            </div>
            <p className="text-secondary mb-4 sm:mb-6 text-sm sm:text-base">
              Are you sure you want to delete this teacher? This action cannot be undone.
            </p>
            <div className="flex flex-col sm:flex-row justify-end gap-3 sm:gap-4">
              <button
                onClick={() => setShowDeleteConfirm(null)}
                className="px-4 py-2 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors text-sm sm:text-base"
              >
                Cancel
              </button>
              <button
                onClick={confirmDelete}
                className="px-4 py-2 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors text-sm sm:text-base"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete All Confirmation Modal */}
      {showDeleteAllConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-surface border border-border rounded-xl p-4 sm:p-6 max-w-md w-full">
            <div className="flex items-center gap-3 mb-4">
              <Shield className="h-5 sm:h-6 w-5 sm:w-6 text-red-500" />
              <h3 className="text-base sm:text-lg font-semibold text-primary">Confirm Delete All Teachers</h3>
            </div>
            
            <div className="mb-4 p-3 bg-red-700 border border-yellow-200 rounded-lg">
              <div className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4 text-yellow-600 flex-shrink-0" />
                <span className="text-xs sm:text-sm text-white">
                  This will delete ALL teachers and related data including teacher assignments and timetable entries. This action cannot be undone!
                </span>
              </div>
            </div>
            
            <p className="text-secondary mb-4 sm:mb-6 text-sm sm:text-base">
              Are you sure you want to proceed? This will permanently delete {teachers.length} teacher(s) and all related data.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={() => setShowDeleteAllConfirm(false)}
                className="flex-1 py-2 px-4 border border-border rounded-lg text-secondary hover:bg-background transition-colors text-sm sm:text-base"
              >
                Cancel
              </button>
              <button
                onClick={handleDeleteAllTeachers}
                disabled={deleteAllLoading}
                className="flex-1 py-2 px-4 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors disabled:opacity-50 text-sm sm:text-base"
              >
                {deleteAllLoading ? (
                  <div className="flex items-center justify-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Deleting...
                  </div>
                ) : (
                  "Confirm Delete All"
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default TeachersConfig;

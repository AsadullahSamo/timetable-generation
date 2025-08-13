import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import api from "../utils/api";
import {
  Users,
  BookOpen,
  GraduationCap,
  Plus,
  Edit2,
  Trash2,
  Loader2,
  AlertCircle,
  Search,
  X,
  CheckCircle2,
  User,
  Hash,
  BarChart3
} from 'lucide-react';

const TeacherAssignments = () => {
  const [assignments, setAssignments] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [batches, setBatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // New simplified state for easy assignment
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [selectedSubjects, setSelectedSubjects] = useState([]); // Changed to array for multiple selection
  const [selectedBatch, setSelectedBatch] = useState(null);
  const [selectedSections, setSelectedSections] = useState([]);
  const [viewMode, setViewMode] = useState('assign'); // 'assign' or 'manage'
  const [searchTerm, setSearchTerm] = useState("");
  const [teacherFilter, setTeacherFilter] = useState('all'); // 'all', 'unassigned', 'assigned'

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [assignmentsRes, teachersRes, subjectsRes, batchesRes] = await Promise.all([
        api.get('/api/timetable/teacher-assignments/'),
        api.get('/api/timetable/teachers/'),
        api.get('/api/timetable/subjects/'),
        api.get('/api/timetable/batches/')
      ]);

      setAssignments(assignmentsRes.data);
      setTeachers(teachersRes.data);
      setSubjects(subjectsRes.data);
      setBatches(batchesRes.data);
    } catch (error) {
      setError('Failed to fetch data: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  // Enhanced assignment creation for multiple subjects
  const createAssignment = async () => {
    if (!selectedTeacher || selectedSubjects.length === 0 || !selectedBatch || selectedSections.length === 0) {
      setError('Please select teacher, at least one subject, batch, and at least one section');
      setTimeout(() => setError(null), 5000);
      return;
    }

    try {
      setLoading(true);

      // Create assignments for each selected subject
      const assignmentPromises = selectedSubjects.map(subject =>
        api.post('/api/timetable/teacher-assignments/', {
          teacher: selectedTeacher.id,
          subject: subject.id,
          batch: selectedBatch.id,
          sections: selectedSections
        })
      );

      await Promise.all(assignmentPromises);

      // Generate detailed success message
      const subjectNames = selectedSubjects.map(s => s.code).join(', ');
      const sectionNames = selectedSections.join(', ');
      
      // Check if this is adding to existing assignments
      const isAddingToExisting = selectedSubjects.some(subject => 
        getExistingAssignments(selectedTeacher.id, subject.id, selectedBatch.id).length > 0
      );
      
      const message = isAddingToExisting 
        ? `✅ Added sections ${sectionNames} to ${selectedTeacher.name}'s existing assignments for ${subjectNames} in ${selectedBatch.name}`
        : `✅ Assigned ${selectedTeacher.name} to teach ${subjectNames} for ${selectedBatch.name} (${sectionNames})`;
      
      setSuccess(message);

      // Reset selections
      setSelectedTeacher(null);
      setSelectedSubjects([]);
      setSelectedBatch(null);
      setSelectedSections([]);

      // Refresh data
      fetchData();

      setTimeout(() => setSuccess(null), 5000);
    } catch (error) {
      setError('Failed to create assignments');
      setTimeout(() => setError(null), 5000);
      console.error('Error creating assignments:', error);
    } finally {
      setLoading(false);
    }
  };

  // Check if assignment already exists
  const isAssignmentExists = (teacherId, subjectId, batchId) => {
    return assignments.some(assignment =>
      assignment.teacher === teacherId &&
      assignment.subject === subjectId &&
      assignment.batch === batchId
    );
  };

  // Get existing assignments for a teacher-subject-batch combination
  const getExistingAssignments = (teacherId, subjectId, batchId) => {
    return assignments.filter(assignment =>
      assignment.teacher === teacherId &&
      assignment.subject === subjectId &&
      assignment.batch === batchId
    );
  };

  // Get assigned sections for a teacher-subject-batch combination
  const getTeacherAssignedSections = (teacherId, subjectId, batchId) => {
    const teacherAssignments = getExistingAssignments(teacherId, subjectId, batchId);
    const assignedSections = new Set();
    teacherAssignments.forEach(assignment => {
      if (assignment.sections) {
        assignment.sections.forEach(section => assignedSections.add(section));
      }
    });
    return Array.from(assignedSections);
  };

  // Get available sections for a teacher-subject-batch combination
  const getAvailableSectionsForTeacher = (teacherId, subjectId, batchId) => {
    if (!selectedBatch) return [];
    
    const allSections = selectedBatch.get_sections ? 
      selectedBatch.get_sections() : 
      ['I', 'II', 'III'].slice(0, selectedBatch.total_sections);
    
    const teacherAssignedSections = getTeacherAssignedSections(teacherId, subjectId, batchId);
    const otherAssignedSections = getAssignedSections(subjectId, batchId);
    
    // Return sections that are not assigned to anyone
    return allSections.filter(section => 
      !otherAssignedSections.includes(section)
    );
  };

  // Check if a batch is fully assigned (all subjects have all sections covered)
  const isBatchFullyAssigned = (batchId) => {
    if (!batchId) return false;
    
    const batch = batches.find(b => b.id === batchId);
    if (!batch) return false;
    
    const batchSubjects = subjects.filter(subject => subject.batch === batch.name);
    if (batchSubjects.length === 0) return false;
    
    const allSections = batch.get_sections ? 
      batch.get_sections() : 
      ['I', 'II', 'III'].slice(0, batch.total_sections);
    
    // Check if every subject has all sections assigned
    return batchSubjects.every(subject => {
      const assignedSections = getAssignedSections(subject.id, batchId);
      return assignedSections.length === allSections.length;
    });
  };

  // Get available subjects for selected batch
  const getAvailableSubjects = () => {
    if (!selectedBatch) return subjects;
    return subjects.filter(subject => subject.batch === selectedBatch.name);
  };

  // Get teacher assignment statistics
  const getTeacherStats = (teacherId) => {
    const teacherAssignments = assignments.filter(assignment => assignment.teacher === teacherId);
    const totalAssignments = teacherAssignments.length;
    const batchesAssigned = [...new Set(teacherAssignments.map(a => a.batch_name))];
    const subjectsAssigned = [...new Set(teacherAssignments.map(a => a.subject_name))];

    return {
      totalAssignments,
      batchesCount: batchesAssigned.length,
      subjectsCount: subjectsAssigned.length,
      batches: batchesAssigned,
      subjects: subjectsAssigned,
      hasAssignments: totalAssignments > 0
    };
  };

  // Get assignment status for visual indication
  const getTeacherAssignmentStatus = (teacherId) => {
    const stats = getTeacherStats(teacherId);

    if (stats.totalAssignments === 0) {
      return { status: 'unassigned', color: 'border-border', bgColor: 'bg-surface/50', textColor: 'text-secondary' };
    } else {
      return { status: 'assigned', color: 'border-green-500/50', bgColor: 'bg-green-500/10', textColor: 'text-green-600' };
    }
  };

  // Filter teachers based on assignment status
  const getFilteredTeachers = () => {
    return teachers.filter(teacher => {
      const stats = getTeacherStats(teacher.id);

      switch (teacherFilter) {
        case 'unassigned':
          return stats.totalAssignments === 0;
        case 'assigned':
          return stats.totalAssignments > 0;
        default:
          return true;
      }
    });
  };

  // Get filtered assignments based on search term
  const getFilteredAssignments = () => {
    if (!searchTerm.trim()) return assignments;
    
    const searchLower = searchTerm.toLowerCase();
    return assignments.filter(assignment => 
      assignment.teacher_name?.toLowerCase().includes(searchLower) ||
      assignment.subject_name?.toLowerCase().includes(searchLower) ||
      assignment.batch_name?.toLowerCase().includes(searchLower) ||
      assignment.sections?.some(section => section.toLowerCase().includes(searchLower)) ||
      assignment.sections_display?.toLowerCase().includes(searchLower)
    );
  };

  // Check if a subject is completely assigned (all sections taken)
  const isSubjectCompletelyAssigned = (subjectId, batchId) => {
    if (!selectedBatch) return false;
    
    const allSections = selectedBatch.get_sections ? 
      selectedBatch.get_sections() : 
      ['I', 'II', 'III'].slice(0, selectedBatch.total_sections);
    
    const assignedSections = getAssignedSections(subjectId, batchId);
    return assignedSections.length === allSections.length;
  };

  // Check if a subject is partially assigned (some sections taken, some available)
  const isSubjectPartiallyAssigned = (subjectId, batchId) => {
    if (!selectedBatch) return false;
    
    const allSections = selectedBatch.get_sections ? 
      selectedBatch.get_sections() : 
      ['I', 'II', 'III'].slice(0, selectedBatch.total_sections);
    
    const assignedSections = getAssignedSections(subjectId, batchId);
    return assignedSections.length > 0 && assignedSections.length < allSections.length;
  };

  // Check if a subject is already assigned to any teacher for the selected batch
  const isSubjectAssigned = (subjectId, batchId) => {
    return assignments.some(assignment =>
      assignment.subject === subjectId && assignment.batch === batchId
    );
  };

  // Check if a specific section is already assigned for a subject and batch
  const isSectionAssigned = (subjectId, batchId, section) => {
    return assignments.some(assignment =>
      assignment.subject === subjectId &&
      assignment.batch === batchId &&
      assignment.sections &&
      assignment.sections.includes(section)
    );
  };

  // Get assigned sections for a subject and batch
  const getAssignedSections = (subjectId, batchId) => {
    const assignedSections = new Set();
    assignments.forEach(assignment => {
      if (assignment.subject === subjectId && assignment.batch === batchId && assignment.sections) {
        assignment.sections.forEach(section => assignedSections.add(section));
      }
    });
    return Array.from(assignedSections);
  };

  // Delete assignment
  const handleDelete = async (assignmentId) => {
    if (!confirm('Are you sure you want to delete this assignment?')) return;

    try {
      setLoading(true);
      await api.delete(`/api/timetable/teacher-assignments/${assignmentId}/`);
      setSuccess('✅ Assignment deleted successfully');
      fetchData();
      setTimeout(() => setSuccess(null), 3000);
    } catch (error) {
      setError('Failed to delete assignment');
      console.error('Error deleting assignment:', error);
    } finally {
      setLoading(false);
    }
  };





  return (
    <>
      <Head>
        <title>Teacher Assignments - Timetable System</title>
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={5} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Teacher Subject Assignments
            </h1>
            <p className="text-secondary/90">Easy assignment management - Click to select, then assign!</p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex gap-2 mb-6">
            <button
              onClick={() => setViewMode('assign')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                viewMode === 'assign'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-surface text-secondary hover:bg-surface/80'
              }`}
            >
              Assignments
            </button>
            <button
              onClick={() => setViewMode('manage')}
              className={`px-4 py-2 rounded-lg font-medium transition-all ${
                viewMode === 'manage'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'bg-surface text-secondary hover:bg-surface/80'
              }`}
            >
              Manage Existing ({assignments.length})
            </button>
          </div>

          {/* Success/Error Messages */}
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
              <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-400">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-500/10 border border-green-500/20 rounded-xl mb-6 flex items-center gap-2">
              <CheckCircle2 className="h-5 w-5 text-green-500" />
              <p className="text-green-500 text-sm font-medium">{success}</p>
              <button onClick={() => setSuccess(null)} className="ml-auto text-green-500 hover:text-green-400">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {viewMode === 'assign' ? (
            /* NEW EASY ASSIGNMENT INTERFACE */
            <div className="space-y-6">
              {/* Assignment Progress Overview */}
              <div className="bg-gradient-to-r from-surface/50 to-surface/30 rounded-xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                  <BarChart3 className="h-4 w-4 text-accent-cyan" />
                  Assignment Progress Overview
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {(() => {
                    const unassignedTeachers = teachers.filter(t => getTeacherStats(t.id).totalAssignments === 0);
                    const assignedTeachers = teachers.filter(t => getTeacherStats(t.id).totalAssignments > 0);
                    const totalAssignments = assignments.length;

                    return (
                      <>
                        <div className="text-center p-3 bg-red-500/10 rounded-lg border border-red-500/20">
                          <div className="text-2xl font-bold text-red-600">{unassignedTeachers.length}</div>
                          <div className="text-sm text-red-600">Unassigned Teachers</div>
                        </div>
                        <div className="text-center p-3 bg-green-500/10 rounded-lg border border-green-500/20">
                          <div className="text-2xl font-bold text-green-600">{assignedTeachers.length}</div>
                          <div className="text-sm text-green-600">Assigned Teachers</div>
                        </div>
                        <div className="text-center p-3 bg-accent-cyan/10 rounded-lg border border-accent-cyan/20">
                          <div className="text-2xl font-bold text-accent-cyan">{totalAssignments}</div>
                          <div className="text-sm text-accent-cyan">Total Assignments</div>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>
              {/* Selection Summary */}
              {(selectedTeacher || selectedSubjects.length > 0 || selectedBatch || selectedSections.length > 0) && (
                <div className="bg-surface/50 rounded-xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                  <Plus className="h-4 w-4 text-accent-cyan" />
                  Create New Assignment
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-secondary" />
                    <span className="text-secondary">Teacher:</span>
                    <span className="font-medium text-primary">
                      {selectedTeacher ? selectedTeacher.name : 'None selected'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-secondary" />
                    <span className="text-secondary">Subjects:</span>
                    <span className="font-medium text-primary">
                      {selectedSubjects.length > 0
                        ? selectedSubjects.map(s => s.code).join(', ')
                        : 'None selected'
                      }
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-secondary" />
                    <span className="text-secondary">Batch:</span>
                    <span className="font-medium text-primary">
                      {selectedBatch ? selectedBatch.name : 'None selected'}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Hash className="h-4 w-4 text-secondary" />
                    <span className="text-secondary">Sections:</span>
                    <span className="font-medium text-primary">
                      {selectedSections.length > 0 ? selectedSections.join(', ') : 'None selected'}
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 mt-4">
                  <button
                    onClick={createAssignment}
                    disabled={!selectedTeacher || selectedSubjects.length === 0 || !selectedBatch || selectedSections.length === 0 || loading}
                    className="px-6 py-2 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:opacity-90 transition-all flex items-center gap-2"
                  >
                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                    Create Assignment{selectedSubjects.length > 1 ? 's' : ''}
                  </button>
                  <button
                    onClick={() => {
                      setSelectedTeacher(null);
                      setSelectedSubjects([]);
                      setSelectedBatch(null);
                      setSelectedSections([]);
                    }}
                    className="px-4 py-2 bg-surface text-secondary hover:bg-surface/80 rounded-lg transition-all"
                  >
                    Clear All
                  </button>
                </div>
              </div>
              )}

              {/* Step 1: Select Teacher */}
              <div className="bg-surface/30 rounded-xl p-4 border border-border">
                <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                  <User className="h-4 w-4 text-accent-cyan" />
                  Step 1: Select Teacher
                </h3>

                {/* Teacher Filter Buttons */}
                <div className="flex flex-wrap gap-2 mb-4">
                  <button
                    onClick={() => setTeacherFilter('all')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                      teacherFilter === 'all'
                        ? 'bg-slate-700 text-white shadow-sm'
                        : 'bg-surface/50 text-secondary hover:bg-surface/80'
                    }`}
                  >
                    All Teachers ({teachers.length})
                  </button>
                  <button
                    onClick={() => setTeacherFilter('unassigned')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                      teacherFilter === 'unassigned'
                        ? 'bg-orange-600 text-white shadow-sm'
                        : 'bg-orange-500/10 text-orange-600 hover:bg-orange-500/20'
                    }`}
                  >
                    Unassigned ({teachers.filter(t => getTeacherStats(t.id).totalAssignments === 0).length})
                  </button>
                  <button
                    onClick={() => setTeacherFilter('assigned')}
                    className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                      teacherFilter === 'assigned'
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20'
                    }`}
                  >
                    Assigned ({teachers.filter(t => getTeacherStats(t.id).totalAssignments > 0).length})
                  </button>
                </div>

                {/* Assignment Status Legend */}
                <div className="flex items-center gap-4 mb-4 text-xs">
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded border border-border bg-surface/50"></div>
                    <span className="text-secondary">Unassigned</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <div className="w-3 h-3 rounded border border-green-500/50 bg-green-500/10"></div>
                    <span className="text-secondary">Assigned</span>
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                  {getFilteredTeachers().map((teacher) => {
                    const stats = getTeacherStats(teacher.id);
                    const statusStyle = getTeacherAssignmentStatus(teacher.id);
                    const isSelected = selectedTeacher?.id === teacher.id;

                    return (
                      <div
                        key={teacher.id}
                        onClick={() => setSelectedTeacher(teacher)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all relative ${
                          isSelected
                            ? 'bg-accent-cyan/10 border-accent-cyan text-accent-cyan'
                            : statusStyle.status === 'assigned'
                            ? `${statusStyle.bgColor} ${statusStyle.color} text-white hover:border-accent-cyan/30`
                            : `${statusStyle.bgColor} ${statusStyle.color} ${statusStyle.textColor} hover:border-accent-cyan/30 hover:text-primary`
                        }`}
                      >


                        <div className="font-medium text-sm truncate">{teacher.name}</div>
                        <div className="text-xs opacity-75 truncate">{teacher.email}</div>

                        {/* Detailed Assignment Info */}
                        <div className="text-xs mt-2 space-y-1">
                          {stats.hasAssignments ? (
                            <div className="space-y-2">
                              {assignments
                                .filter(assignment => assignment.teacher === teacher.id)
                                .map((assignment, index) => (
                                  <div key={index} className="bg-background/50 rounded p-2 border border-border/50">
                                    <div className="font-medium text-accent-cyan truncate">
                                      {assignment.subject_name}
                                    </div>
                                    <div className="flex items-center justify-between text-xs text-white/80">
                                      <span>{assignment.batch_name}</span>
                                      <span className="font-medium">
                                        {assignment.sections?.length > 0
                                          ? assignment.sections.join(', ')
                                          : 'All sections'
                                        }
                                      </span>
                                    </div>
                                  </div>
                                ))
                              }
                            </div>
                          ) : (
                            <div className="text-center opacity-60 py-2">
                              No assignments yet
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}

                  {getFilteredTeachers().length === 0 && (
                    <div className="col-span-full text-center py-8">
                      <User className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
                      <p className="text-secondary">No teachers found for the selected filter</p>
                      <p className="text-secondary/70 text-sm mt-2">Try selecting a different filter option</p>
                    </div>
                  )}
                </div>
              </div>

              {/* Step 2: Select Batch */}
              {selectedTeacher && (
                <div className="bg-surface/30 rounded-xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                    <GraduationCap className="h-4 w-4 text-accent-cyan" />
                    Step 2: Select Batch
                  </h3>
                                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
                  {batches.map((batch) => {
                    const isFullyAssigned = isBatchFullyAssigned(batch.id);
                    
                    return (
                      <div
                        key={batch.id}
                        onClick={() => setSelectedBatch(batch)}
                        className={`p-3 rounded-lg border cursor-pointer transition-all relative ${
                          selectedBatch?.id === batch.id
                            ? 'bg-accent-cyan/10 border-accent-cyan text-accent-cyan'
                            : isFullyAssigned
                            ? 'bg-green-500/10 border-green-500/50 text-white'
                            : 'bg-surface/50 border-border text-secondary hover:border-accent-cyan/30 hover:text-primary'
                        }`}
                      >
                        {/* Fully assigned indicator */}
                        {isFullyAssigned && (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-green-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-xs font-bold">✓</span>
                          </div>
                        )}
                        
                        <div className="font-medium text-sm">{batch.name}</div>
                        <div className="text-xs opacity-75">{batch.description}</div>
                        <div className="text-xs mt-1 flex items-center gap-2">
                          <span>{batch.total_sections} sections</span>
                          {isFullyAssigned && (
                            <span className="text-white font-medium">Complete</span>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
                </div>
              )}

              {/* Step 3: Select Subjects */}
              {selectedTeacher && selectedBatch && (
                <div className="bg-surface/30 rounded-xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-accent-cyan" />
                    Step 3: Select Subjects for {selectedBatch.name}
                  </h3>

                  {/* Selection Info */}
                  <div className="mb-3 text-sm text-secondary">
                    Select one subject at a time
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {getAvailableSubjects().map((subject) => {
                      const isSelected = selectedSubjects.some(s => s.id === subject.id);
                      const isCompletelyAssigned = isSubjectCompletelyAssigned(subject.id, selectedBatch.id);
                      const isPartiallyAssigned = isSubjectPartiallyAssigned(subject.id, selectedBatch.id);
                      const teacherExistingAssignments = selectedTeacher ? 
                        getExistingAssignments(selectedTeacher.id, subject.id, selectedBatch.id) : [];
                      const teacherAssignedSections = selectedTeacher ? 
                        getTeacherAssignedSections(selectedTeacher.id, subject.id, selectedBatch.id) : [];
                      const availableSections = selectedTeacher ? 
                        getAvailableSectionsForTeacher(selectedTeacher.id, subject.id, selectedBatch.id) : [];

                      // Determine the visual style based on assignment status
                      let cardStyle = 'bg-surface/50 border-border text-secondary hover:border-accent-cyan/30 hover:text-primary';
                      let statusIndicator = null;
                      let statusText = '';

                      if (isSelected) {
                        cardStyle = 'bg-accent-cyan/10 border-accent-cyan text-accent-cyan';
                        statusIndicator = (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-accent-cyan rounded-full flex items-center justify-center">
                            <span className="text-white text-xs font-bold">✓</span>
                          </div>
                        );
                      } else if (isCompletelyAssigned) {
                        cardStyle = 'bg-yellow-500/10 border-yellow-500/50 text-yellow-600';
                        statusIndicator = (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-xs font-bold">✓</span>
                          </div>
                        );
                        statusText = 'Fully Assigned';
                      } else if (isPartiallyAssigned) {
                        cardStyle = 'bg-blue-500/10 border-blue-500/50 text-white';
                        statusIndicator = (
                          <div className="absolute -top-1 -right-1 w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-xs font-bold">!</span>
                          </div>
                        );
                        statusText = 'Partially Assigned';
                      }

                      return (
                        <div
                          key={subject.id}
                          onClick={() => {
                            if (isSelected) {
                              setSelectedSubjects(selectedSubjects.filter(s => s.id !== subject.id));
                            } else {
                              setSelectedSubjects([...selectedSubjects, subject]);
                            }
                          }}
                          className={`p-3 rounded-lg border cursor-pointer transition-all relative ${cardStyle}`}
                        >
                          {/* Status indicator */}
                          {statusIndicator}

                          <div className="font-medium text-sm text-current">{subject.code}</div>
                          <div className="text-xs opacity-90 truncate text-current">{subject.name}</div>
                          <div className="text-xs mt-1 flex items-center gap-2 text-current">
                            <span>{subject.credits} credits</span>
                            {subject.is_practical && (
                              <span className="text-accent-pink font-medium">Lab</span>
                            )}
                            {statusText && (
                              <span className="font-medium">{statusText}</span>
                            )}
                          </div>

                          {/* Show existing teacher assignments */}
                          {teacherExistingAssignments.length > 0 && (
                            <div className="mt-2 p-2 bg-green-500/10 rounded border border-green-500/20">
                              <div className="text-xs text-white font-medium mb-1">
                                Already teaching sections: {teacherAssignedSections.join(', ')}
                              </div>
                              {availableSections.length > 0 && (
                                <div className="text-xs text-white">
                                  Available sections: {availableSections.length} remaining
                                </div>
                              )}
                            </div>
                          )}

                          {/* Show assignment status summary */}
                          {!teacherExistingAssignments.length && (isCompletelyAssigned || isPartiallyAssigned) && (
                            <div className="mt-2 p-2 bg-gray-500/10 rounded border border-gray-500/20">
                              <div className="text-xs text-white font-medium mb-1">
                                Assignment Status
                              </div>
                              <div className="text-xs text-white">
                                {isCompletelyAssigned ? 'All sections assigned' : 'Some sections available'}
                              </div>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Step 4: Select Sections */}
              {selectedTeacher && selectedBatch && selectedSubjects.length > 0 && (
                <div className="bg-surface/30 rounded-xl p-4 border border-border">
                  <h3 className="font-semibold text-primary mb-3 flex items-center gap-2">
                    <Hash className="h-4 w-4 text-accent-cyan" />
                    Step 4: Select Sections for {selectedBatch.name}
                  </h3>

                  {/* Show assignment status info */}
                  <div className="mb-3 space-y-2">
                    {selectedSubjects.map(subject => {
                      const teacherAssignedSections = getTeacherAssignedSections(selectedTeacher.id, subject.id, selectedBatch.id);
                      const otherAssignedSections = getAssignedSections(subject.id, selectedBatch.id);
                      const availableSections = getAvailableSectionsForTeacher(selectedTeacher.id, subject.id, selectedBatch.id);
                      
                      return (
                        <div key={subject.id} className="text-sm">
                          <div className="font-medium text-primary mb-1">{subject.code}:</div>
                          {teacherAssignedSections.length > 0 && (
                            <div className="text-green-600 mb-1">
                              ✓ Already teaching sections: {teacherAssignedSections.join(', ')}
                            </div>
                          )}
                          {availableSections.length > 0 && (
                            <div className="text-accent-cyan mb-1">
                              ➕ Available sections: {availableSections.join(', ')}
                            </div>
                          )}
                          {otherAssignedSections.length > 0 && (
                            <div className="text-yellow-600">
                              ⚠️ Other teachers assigned to: {otherAssignedSections.join(', ')}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex gap-2">
                    {selectedBatch.get_sections ? selectedBatch.get_sections().map((section) => {
                      const isAssignedToAnySubject = selectedSubjects.some(subject =>
                        isSectionAssigned(subject.id, selectedBatch.id, section)
                      );
                      const isAssignedToSelectedTeacher = selectedTeacher && selectedSubjects.some(subject =>
                        getTeacherAssignedSections(selectedTeacher.id, subject.id, selectedBatch.id).includes(section)
                      );
                      const isAvailableForTeacher = selectedTeacher && selectedSubjects.some(subject =>
                        getAvailableSectionsForTeacher(selectedTeacher.id, subject.id, selectedBatch.id).includes(section)
                      );

                      return (
                        <button
                          key={section}
                          onClick={() => {
                            if (selectedSections.includes(section)) {
                              setSelectedSections(selectedSections.filter(s => s !== section));
                            } else if (isAvailableForTeacher || isAssignedToSelectedTeacher) {
                              setSelectedSections([...selectedSections, section]);
                            }
                          }}
                          className={`px-4 py-2 rounded-lg border font-medium transition-all relative ${
                            selectedSections.includes(section)
                              ? 'bg-accent-cyan/10 border-accent-cyan text-accent-cyan'
                              : isAssignedToSelectedTeacher
                              ? 'bg-green-500/10 border-green-500/50 text-green-600'
                              : isAvailableForTeacher
                              ? 'bg-surface/50 border-border text-secondary hover:border-accent-cyan/30 hover:text-primary'
                              : 'bg-red-500/10 border-red-500/50 text-red-600 cursor-not-allowed'
                          }`}
                          disabled={!isAvailableForTeacher && !isAssignedToSelectedTeacher}
                        >
                          {/* Assignment status indicators */}
                          {isAssignedToSelectedTeacher && !selectedSections.includes(section) && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">✓</span>
                            </div>
                          )}
                          {!isAssignedToSelectedTeacher && !isAvailableForTeacher && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">✗</span>
                            </div>
                          )}

                          Section {section}
                          {isAssignedToSelectedTeacher && (
                            <span className="ml-1 text-xs opacity-75">Your sections</span>
                          )}
                          {!isAvailableForTeacher && !isAssignedToSelectedTeacher && (
                            <span className="ml-1 text-xs opacity-75">Unavailable</span>
                          )}
                        </button>
                      );
                    }) : ['I', 'II', 'III'].slice(0, selectedBatch.total_sections).map((section) => {
                      const isAssignedToAnySubject = selectedSubjects.some(subject =>
                        isSectionAssigned(subject.id, selectedBatch.id, section)
                      );
                      const isAssignedToSelectedTeacher = selectedTeacher && selectedSubjects.some(subject =>
                        getTeacherAssignedSections(selectedTeacher.id, subject.id, selectedBatch.id).includes(section)
                      );
                      const isAvailableForTeacher = selectedTeacher && selectedSubjects.some(subject =>
                        getAvailableSectionsForTeacher(selectedTeacher.id, subject.id, selectedBatch.id).includes(section)
                      );

                      return (
                        <button
                          key={section}
                          onClick={() => {
                            if (selectedSections.includes(section)) {
                              setSelectedSections(selectedSections.filter(s => s !== section));
                            } else if (isAvailableForTeacher || isAssignedToSelectedTeacher) {
                              setSelectedSections([...selectedSections, section]);
                            }
                          }}
                          className={`px-4 py-2 rounded-lg border font-medium transition-all relative ${
                            selectedSections.includes(section)
                              ? 'bg-accent-cyan/10 border-accent-cyan text-accent-cyan'
                              : isAssignedToSelectedTeacher
                              ? 'bg-green-500/10 border-green-500/50 text-green-600'
                              : isAvailableForTeacher
                              ? 'bg-surface/50 border-border text-secondary hover:border-accent-cyan/30 hover:text-primary'
                              : 'bg-red-500/10 border-red-500/50 text-red-600 cursor-not-allowed'
                          }`}
                          disabled={!isAvailableForTeacher && !isAssignedToSelectedTeacher}
                        >
                          {/* Assignment status indicators */}
                          {isAssignedToSelectedTeacher && !selectedSections.includes(section) && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">✓</span>
                            </div>
                          )}
                          {!isAssignedToSelectedTeacher && !isAvailableForTeacher && (
                            <div className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 rounded-full flex items-center justify-center">
                              <span className="text-white text-xs font-bold">✗</span>
                            </div>
                          )}

                          Section {section}
                          {isAssignedToSelectedTeacher && (
                            <span className="ml-1 text-xs opacity-75">Your sections</span>
                          )}
                          {!isAvailableForTeacher && !isAssignedToSelectedTeacher && (
                            <span className="ml-1 text-xs opacity-75">Unavailable</span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>
          ) : (
            /* EXISTING ASSIGNMENTS MANAGEMENT */
            <div className="space-y-6">
              <div className="flex flex-col md:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-secondary/70" />
                  </div>
                  <input
                    type="text"
                    placeholder="Search assignments..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-3 bg-background/95 backdrop-blur-sm border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                  />
                </div>
              </div>

              {/* Assignments List */}
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-accent-cyan" />
                </div>
              ) : (
                <div className="space-y-4">
                  {getFilteredAssignments().map((assignment) => (
                    <div key={assignment.id} className="p-6 bg-card/50 backdrop-blur-sm border border-border rounded-xl hover:shadow-lg hover:shadow-accent-cyan/10 transition-all duration-300">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <div className="p-2 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end rounded-lg">
                              <Users className="h-4 w-4 text-white" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-primary">{assignment.teacher_name}</h3>
                              <p className="text-sm text-secondary">{assignment.subject_name}</p>
                            </div>
                          </div>

                          <div className="flex items-center gap-4 text-sm text-secondary/80">
                            <div className="flex items-center gap-1">
                              <GraduationCap className="h-4 w-4" />
                              <span>{assignment.batch_name}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              <Hash className="h-4 w-4" />
                              <span>Sections: {assignment.sections?.join(', ') || 'All'}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex gap-2">
                          <button
                            onClick={() => handleDelete(assignment.id)}
                            className="p-2 text-secondary hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}

                  {getFilteredAssignments().length === 0 && (
                    <div className="text-center py-12">
                      <Users className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
                      {searchTerm.trim() ? (
                        <>
                          <p className="text-secondary">No assignments found for "{searchTerm}"</p>
                          <p className="text-secondary/70 text-sm mt-2">Try a different search term or clear the search</p>
                        </>
                      ) : (
                        <>
                          <p className="text-secondary">No teacher assignments found</p>
                          <p className="text-secondary/70 text-sm mt-2">Switch to "Create Assignments" to add some!</p>
                        </>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}



        </div>
      </div>
    </>
  );
};

export default TeacherAssignments;

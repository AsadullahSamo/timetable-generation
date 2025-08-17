import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";
import { 
  BookOpen, 
  Search, 
  Plus, 
  Edit2, 
  Trash2, 
  Info, 
  Loader2, 
  ArrowLeft, 
  ArrowRight,
  AlertCircle,
  RefreshCw,
  X,
  BarChart3,
  Hash,
  Award,
  CheckCircle2,
  BookMarked
} from 'lucide-react';

const SubjectConfig = () => {
  const [subjects, setSubjects] = useState([]);
  const [batches, setBatches] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    credits: 3,
    batch: ""
  });
  const [showAssignments, setShowAssignments] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showTooltip, setShowTooltip] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [activeSubject, setActiveSubject] = useState(null);
  const [formErrors, setFormErrors] = useState({});

  // Stats calculation
  const stats = {
    totalSubjects: subjects.length,
    totalCredits: subjects.reduce((acc, subject) => acc + subject.credits, 0),
    avgCredits: subjects.length ? (subjects.reduce((acc, subject) => acc + subject.credits, 0) / subjects.length).toFixed(1) : 0,
    duplicateCodes: (() => {
      const codeCounts = {};
      subjects.forEach(subject => {
        const code = subject.code.toLowerCase();
        codeCounts[code] = (codeCounts[code] || 0) + 1;
      });
      return Object.values(codeCounts).filter(count => count > 1).length;
    })()
  };

  // Fetch subjects from backend
  useEffect(() => {
    const fetchSubjects = async () => {
      try {
        const { data } = await api.get("/api/timetable/subjects/");
        setSubjects(data);
      } catch (err) {
        setError("Failed to load subjects. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    const fetchBatches = async () => {
      try {
        const { data } = await api.get("/api/timetable/batches/");
        setBatches(data);
      } catch (err) {
        console.error("Batches fetch error:", err);
        // Fallback to hardcoded batches if API fails
        setBatches([
          { id: 1, name: "21SW", description: "Senior Batch" },
          { id: 2, name: "22SW", description: "Senior Batch" },
          { id: 3, name: "23SW", description: "2nd Year Batch" },
          { id: 4, name: "24SW", description: "1st Year Batch" }
        ]);
      }
    };

    const fetchTeachers = async () => {
      try {
        const { data } = await api.get("/api/timetable/teachers/");
        setTeachers(data);
      } catch (err) {
        console.error("Teachers fetch error:", err);
      }
    };

    const fetchAssignments = async () => {
      try {
        const { data } = await api.get("/api/timetable/teacher-assignments/");
        setAssignments(data);
      } catch (err) {
        console.error("Assignments fetch error:", err);
      }
    };

    fetchSubjects();
    fetchBatches();
    fetchTeachers();
    fetchAssignments();
  }, []);

  // Get teacher assignments for a subject
  const getSubjectAssignments = (subjectId) => {
    return assignments.filter(assignment => assignment.subject === subjectId);
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = "Subject name is required";
    } else if (formData.name.length < 2) {
      errors.name = "Subject name must be at least 2 characters";
    } else if (formData.name.length > 100) {
      errors.name = "Subject name cannot exceed 100 characters";
    }
    // Note: Subject name allows letters, numbers, spaces, and special characters
    
    if (!formData.code.trim()) {
      errors.code = "Subject code is required";
    } else if (!/^[A-Z0-9]+$/i.test(formData.code)) {
      errors.code = "Subject code should only contain letters and numbers (no spaces or special characters)";
    } else {
      // Check for duplicate subject codes (allow max 2 - theory and practical)
      const existingSubjectsWithSameCode = subjects.filter(subject => 
        subject.code.toLowerCase() === formData.code.trim().toLowerCase() && 
        subject.id !== editingId
      );
      
      if (existingSubjectsWithSameCode.length >= 2) {
        errors.code = "Subject code already used twice (max allowed for theory and practical versions)";
      }
    }
    
    if (formData.credits < 1) {
      errors.credits = "Credits must be at least 1";
    } else if (formData.credits > 10) {
      errors.credits = "Credits cannot exceed 10";
    }

    if (!formData.batch.trim()) {
      errors.batch = "Batch is required (e.g., 21SW, 22SW, 23SW, 24SW, 25SW, etc.)";
    } else if (!/^\d{2}[A-Z]{2}$/i.test(formData.batch)) {
      errors.batch = "Batch must be in format: 2 digits + 2 letters (e.g., 21SW, 22SW, 23SW, 24SW, 25SW, etc.)";
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === "credits" ? Math.max(1, parseInt(value) || 1) : value
    }));
    
    // Clear specific error when user types
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: undefined
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    
    if (!validateForm()) {
      return;
    }

    setSubmitting(true);

    try {
      if (editingId) {
        // Update existing subject
        const { data } = await api.put(`/api/timetable/subjects/${editingId}/`, formData);
        setSubjects(subjects.map(subject => 
          subject.id === editingId ? data : subject
        ));
        setActiveSubject(editingId);
      } else {
        // Create new subject
        const { data } = await api.post("/api/timetable/subjects/", formData);
        setSubjects([...subjects, data]);
        setActiveSubject(data.id);
      }
      setFormData({ name: "", code: "", credits: 3, batch: "" });
      setEditingId(null);
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        // Check for specific error messages in the response
        if (errorData.code) {
          setError(`Subject code "${formData.code}" is already in use. Please choose a different code.`);
        } else if (errorData.name) {
          setError(`Subject name "${formData.name}" is already in use. Please choose a different name.`);
        } else if (errorData.detail) {
          setError(errorData.detail);
        } else if (typeof errorData === 'object') {
          // Handle multiple validation errors
          const errorMessages = Object.values(errorData).flat();
          setError(errorMessages.join('. '));
        } else {
          setError("Failed to save subject. Please check your input and try again.");
        }
      } else {
        setError("Failed to connect to the server. Please try again later.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    setShowDeleteConfirm(id);
  };
  
  const confirmDelete = async () => {
    try {
      await api.delete(`/api/timetable/subjects/${showDeleteConfirm}/`);
      setSubjects(subjects.filter(sub => sub.id !== showDeleteConfirm));
      if (editingId === showDeleteConfirm) {
        setFormData({ name: "", code: "", credits: 3, batch: "" });
        setEditingId(null);
      }
      setShowDeleteConfirm(null);
    } catch (err) {
      setError("Delete failed - subject might be in use.");
      setShowDeleteConfirm(null);
    }
  };

  const handleEdit = (subject) => {
    setFormData({
      name: subject.name,
      code: subject.code,
      credits: subject.credits,
      batch: subject.batch || ""
    });
    setEditingId(subject.id);
    setActiveSubject(subject.id);
    setFormErrors({});
  };
  
  const clearForm = () => {
    setFormData({ name: "", code: "", credits: 3, batch: "" });
    setEditingId(null);
    setFormErrors({});
  };

  const filteredSubjects = subjects.filter(subject =>
    subject.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    subject.code.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={2} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Subject Configuration
            </h1>
            <p className="text-secondary/90">Add and manage subjects for your timetable</p>
          </div>
          
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

          {/* Stats Summary */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <BookOpen className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Total Subjects</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.totalSubjects}</p>
            </div>
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <Award className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Total Credits</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.totalCredits}</p>
            </div>
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <BarChart3 className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Avg. Credits</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.avgCredits}</p>
            </div>
            <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
              <div className="flex items-center gap-3 mb-2">
                <Hash className="h-5 w-5 text-accent-cyan" />
                <h3 className="text-sm font-medium text-secondary">Duplicate Codes</h3>
              </div>
              <p className="text-2xl font-bold text-primary">{stats.duplicateCodes}</p>
              {stats.duplicateCodes === 0 && (
                <p className="text-xs text-secondary/70 mt-1">All codes unique</p>
              )}
              {stats.duplicateCodes > 0 && (
                <p className="text-xs text-secondary/70 mt-1">Theory + Practical</p>
              )}
            </div>
          </div>

          {/* Search Bar */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search subjects..."
                className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
              />
            </div>
          </div>

          {/* Add/Edit Subject Form */}
          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <BookMarked className="h-5 w-5 text-accent-cyan" />
                {editingId ? "Edit Subject" : "Add New Subject"}
              </h2>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <button
                    type="button"
                    className="text-secondary hover:text-primary transition-colors"
                    onMouseEnter={() => setShowTooltip("form")}
                    onMouseLeave={() => setShowTooltip("")}
                  >
                    <Info className="h-5 w-5" />
                  </button>
                  {showTooltip === "form" && (
                    <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                      Enter subject details like name, code, and credits. Subject names can include letters, numbers, spaces, and special characters. Subject codes can be used twice (for theory and practical versions) but not more than twice.
                    </div>
                  )}
                </div>
                {editingId && (
                  <button
                    onClick={clearForm}
                    className="text-secondary hover:text-accent-cyan transition-colors flex items-center gap-1"
                    title="Clear form"
                  >
                    <RefreshCw className="h-5 w-5" />
                    <span className="text-sm">Clear form</span>
                  </button>
                )}
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Subject Name</label>
                  <p className="text-xs text-secondary/70">Accepts letters, numbers, spaces, and special characters</p>
                  <div className="relative">
                    <BookOpen className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="e.g. Mathematics 101, Advanced Calculus"
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.name ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                    />
                  </div>
                  {formErrors.name && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.name}</p>
                  )}
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Subject Code</label>
                  <p className="text-xs text-secondary/70">Letters and numbers only. Can be used twice (theory + practical)</p>
                  <div className="relative">
                    <Hash className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="text"
                      name="code"
                      value={formData.code}
                      onChange={handleInputChange}
                      placeholder="e.g. MATH101"
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.code ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                    />
                  </div>
                  {formErrors.code && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.code}</p>
                  )}
                  {!formErrors.code && formData.code && (
                    (() => {
                      const existingCount = subjects.filter(subject => 
                        subject.code.toLowerCase() === formData.code.trim().toLowerCase() && 
                        subject.id !== editingId
                      ).length;
                      if (existingCount === 1) {
                        return (
                          <p className="text-blue-500 text-xs mt-1">
                            This code is used 1 time (can use 1 more time for theory/practical)
                          </p>
                        );
                      } else if (existingCount >= 2) {
                        return (
                          <p className="text-orange-500 text-xs mt-1">
                            This code is used {existingCount} times (maximum allowed reached)
                          </p>
                        );
                      }
                      return null;
                    })()
                  )}
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium text-secondary">Credits</label>
                  <div className="relative">
                    <Award className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                    <input
                      type="number"
                      name="credits"
                      value={formData.credits}
                      onChange={handleInputChange}
                      min="1"
                      max="10"
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.credits ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                    />
                  </div>
                  {formErrors.credits && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.credits}</p>
                  )}
                </div>
              </div>

              {/* Batch Field */}
              <div>
                <label className="block text-sm font-medium text-secondary mb-2">
                  Batch *
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Hash className="h-5 w-5 text-secondary/70" />
                  </div>
                  <select
                    name="batch"
                    value={formData.batch}
                    onChange={handleInputChange}
                    className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.batch ? 'border-red-500' : 'border-border'} rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30`}
                    required
                  >
                    <option value="">Select Batch</option>
                    {batches.map((batch) => (
                      <option key={batch.id} value={batch.name}>
                        {batch.name} ({batch.description})
                      </option>
                    ))}
                  </select>
                </div>
                {formErrors.batch && (
                  <p className="text-red-500 text-xs mt-1">{formErrors.batch}</p>
                )}
              </div>

              <button
                type="submit"
                className="w-full py-3 px-4 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                disabled={submitting}
              >
                {submitting ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <>
                    {editingId ? <Edit2 className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
                    {editingId ? "Update Subject" : "Add Subject"}
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Subjects Table */}
          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-accent-cyan" />
                Subject List
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
                    View and manage your subjects. You can edit or delete existing subjects.
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
                {filteredSubjects.length === 0 ? (
                  <div className="text-center py-8 text-secondary">
                    {searchQuery ? "No subjects found matching your search" : "No subjects added yet"}
                  </div>
                ) : (
                  <table className="w-full border-collapse">
                    <thead>
                      <tr className="bg-background/95">
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Subject Name</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Code</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Credits</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Teacher Assignments</th>
                        <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredSubjects.map((subject) => (
                        <tr 
                          key={subject.id} 
                          className={`hover:bg-background/50 transition-colors ${
                            activeSubject === subject.id ? 'bg-accent-cyan/5' : ''
                          }`}
                        >
                          <td className="px-4 py-3 border border-border">
                            <div className="flex items-center gap-2">
                              <span>{subject.name}</span>
                              {subject.is_practical && (
                                <span className="px-2 py-1 text-xs bg-blue-500/20 text-white rounded-full border border-blue-500/30">
                                  Practical
                                </span>
                              )}
                              {activeSubject === subject.id && (
                                <CheckCircle2 className="h-4 w-4 text-accent-cyan" />
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3 border border-border font-mono">{subject.code}</td>
                          <td className="px-4 py-3 border border-border">{subject.credits}</td>
                          <td className="px-4 py-3 border border-border">
                            {(() => {
                              const subjectAssignments = getSubjectAssignments(subject.id);
                              if (subjectAssignments.length === 0) {
                                return <span className="text-secondary/60 text-sm">No assignments</span>;
                              }
                              return (
                                <div className="space-y-1">
                                  {subjectAssignments.map((assignment, index) => (
                                    <div key={index} className="text-sm">
                                      <span className="font-medium text-primary">{assignment.teacher_name}</span>
                                      <span className="text-secondary/70 ml-2">
                                        ({assignment.batch_name} - {assignment.sections?.join(', ') || 'All'})
                                      </span>
                                    </div>
                                  ))}
                                </div>
                              );
                            })()}
                          </td>
                          <td className="px-4 py-3 border border-border">
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => handleEdit(subject)}
                                className="text-secondary hover:text-accent-cyan transition-colors"
                                title="Edit subject"
                              >
                                <Edit2 className="h-4 w-4" />
                              </button>
                              <button
                                onClick={() => handleDelete(subject.id)}
                                className="text-secondary hover:text-red-500 transition-colors"
                                title="Delete subject"
                              >
                                <Trash2 className="h-4 w-4" />
                              </button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/Classes"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>

            <Link
              href="/components/Teachers"
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
              Are you sure you want to delete this subject? This action cannot be undone.
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

export default SubjectConfig;
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
  Hash
} from 'lucide-react';

const TeacherAssignments = () => {
  const [assignments, setAssignments] = useState([]);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [batches, setBatches] = useState([]);
  const [formData, setFormData] = useState({
    teacher: "",
    subject: "",
    batch: "",
    sections: []
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedBatch, setSelectedBatch] = useState("");

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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSectionChange = (sectionName) => {
    setFormData(prev => ({
      ...prev,
      sections: prev.sections.includes(sectionName)
        ? prev.sections.filter(s => s !== sectionName)
        : [...prev.sections, sectionName]
    }));
  };

  const getAvailableSections = () => {
    const selectedBatchObj = batches.find(b => b.id === parseInt(formData.batch));
    if (!selectedBatchObj) return [];
    
    const sections = [];
    for (let i = 1; i <= selectedBatchObj.total_sections; i++) {
      if (i === 1) sections.push("I");
      else if (i === 2) sections.push("II");
      else if (i === 3) sections.push("III");
      else if (i === 4) sections.push("IV");
      else if (i === 5) sections.push("V");
      else sections.push(i.toString());
    }
    return sections;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (editingId) {
        await api.put(`/api/timetable/teacher-assignments/${editingId}/`, formData);
      } else {
        await api.post('/api/timetable/teacher-assignments/', formData);
      }
      
      await fetchData();
      clearForm();
      setShowForm(false);
    } catch (error) {
      setError('Failed to save assignment: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (assignment) => {
    setFormData({
      teacher: assignment.teacher,
      subject: assignment.subject,
      batch: assignment.batch,
      sections: assignment.sections || []
    });
    setEditingId(assignment.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this assignment?')) return;
    
    setLoading(true);
    try {
      await api.delete(`/api/timetable/teacher-assignments/${id}/`);
      await fetchData();
    } catch (error) {
      setError('Failed to delete assignment: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setFormData({ teacher: "", subject: "", batch: "", sections: [] });
    setEditingId(null);
  };

  const filteredAssignments = assignments.filter(assignment => {
    const matchesSearch = assignment.teacher_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.subject_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         assignment.batch_name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesBatch = !selectedBatch || assignment.batch === parseInt(selectedBatch);
    return matchesSearch && matchesBatch;
  });

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
            <p className="text-secondary/90">Manage teacher assignments to subjects and sections</p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

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
                className="w-full pl-10 pr-4 py-3 bg-card/50 backdrop-blur-sm border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
              />
            </div>
            
            <select
              value={selectedBatch}
              onChange={(e) => setSelectedBatch(e.target.value)}
              className="px-4 py-3 bg-card/50 backdrop-blur-sm border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
            >
              <option value="">All Batches</option>
              {batches.map(batch => (
                <option key={batch.id} value={batch.id}>{batch.name}</option>
              ))}
            </select>
            
            <button
              onClick={() => {
                setShowForm(!showForm);
                if (!showForm) clearForm();
              }}
              className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
            >
              {showForm ? <X className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
              {showForm ? "Cancel" : "Add Assignment"}
            </button>
          </div>

          {/* Assignment Form */}
          {showForm && (
            <div className="mb-8 p-6 bg-card/50 backdrop-blur-sm border border-border rounded-xl">
              <h2 className="text-xl font-semibold text-primary mb-4">
                {editingId ? "Edit Assignment" : "Add New Assignment"}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {/* Teacher Selection */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Teacher *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <User className="h-5 w-5 text-secondary/70" />
                      </div>
                      <select
                        name="teacher"
                        value={formData.teacher}
                        onChange={handleInputChange}
                        required
                        className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      >
                        <option value="">Select Teacher</option>
                        {teachers.map(teacher => (
                          <option key={teacher.id} value={teacher.id}>{teacher.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Subject Selection */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Subject *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <BookOpen className="h-5 w-5 text-secondary/70" />
                      </div>
                      <select
                        name="subject"
                        value={formData.subject}
                        onChange={handleInputChange}
                        required
                        className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      >
                        <option value="">Select Subject</option>
                        {subjects.map(subject => (
                          <option key={subject.id} value={subject.id}>{subject.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  {/* Batch Selection */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Batch *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <GraduationCap className="h-5 w-5 text-secondary/70" />
                      </div>
                      <select
                        name="batch"
                        value={formData.batch}
                        onChange={handleInputChange}
                        required
                        className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      >
                        <option value="">Select Batch</option>
                        {batches.map(batch => (
                          <option key={batch.id} value={batch.id}>{batch.name}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Section Selection */}
                {formData.batch && (
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Sections *
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {getAvailableSections().map(section => (
                        <button
                          key={section}
                          type="button"
                          onClick={() => handleSectionChange(section)}
                          className={`px-4 py-2 rounded-lg border transition-all duration-200 ${
                            formData.sections.includes(section)
                              ? 'bg-accent-cyan/20 border-accent-cyan text-accent-cyan'
                              : 'bg-background/95 border-border text-secondary hover:border-accent-cyan/50'
                          }`}
                        >
                          Section {section}
                        </button>
                      ))}
                    </div>
                    <p className="text-xs text-secondary/70 mt-2">
                      Select one or more sections this teacher will handle for this subject
                    </p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={loading || formData.sections.length === 0}
                  className="w-full py-3 px-4 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <Loader2 className="h-5 w-5 animate-spin" />
                  ) : (
                    <>
                      {editingId ? <Edit2 className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
                      {editingId ? "Update Assignment" : "Add Assignment"}
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Assignments List */}
          {loading && !showForm ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-accent-cyan" />
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAssignments.map((assignment) => (
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
                        onClick={() => handleEdit(assignment)}
                        className="p-2 text-secondary hover:text-accent-cyan hover:bg-accent-cyan/10 rounded-lg transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
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

              {filteredAssignments.length === 0 && (
                <div className="text-center py-12">
                  <Users className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
                  <p className="text-secondary">No teacher assignments found</p>
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

import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import api from "../utils/api";
import {
  GraduationCap,
  Search,
  Plus,
  Edit2,
  Trash2,
  Loader2,
  AlertCircle,
  X,
  Hash,
  Calendar,
  BookOpen,
  Users
} from 'lucide-react';

const BatchManagement = () => {
  const [batches, setBatches] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    semester_number: 1,
    academic_year: "2024-2025",
    total_sections: 1
  });
  const [formErrors, setFormErrors] = useState({});
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchBatches();
  }, []);

  const fetchBatches = async () => {
    try {
      setLoading(true);
      const { data } = await api.get("/api/timetable/batches/");
      setBatches(data);
      setError("");
    } catch (err) {
      setError("Failed to load batches");
      console.error("Batches fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = "Batch name is required";
    } else if (!/^(19|20|21|22|23|24|25|26|27|28|29|30)SW$/i.test(formData.name)) {
      errors.name = "Batch name must be in format: 21SW, 22SW, etc.";
    }
    
    if (!formData.description.trim()) {
      errors.description = "Description is required";
    }
    
    if (formData.semester_number < 1 || formData.semester_number > 8) {
      errors.semester_number = "Semester must be between 1 and 8";
    }
    
    if (!formData.academic_year.trim()) {
      errors.academic_year = "Academic year is required";
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: (name === "semester_number" || name === "total_sections") ? Math.max(1, parseInt(value) || 1) : value
    }));
    
    // Clear specific field error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: ""
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
        // Update existing batch
        const { data } = await api.put(`/api/timetable/batches/${editingId}/`, formData);
        setBatches(batches.map(batch => 
          batch.id === editingId ? data : batch
        ));
      } else {
        // Create new batch
        const { data } = await api.post("/api/timetable/batches/", formData);
        setBatches([...batches, data]);
      }
      setFormData({ name: "", description: "", semester_number: 1, academic_year: "2024-2025", total_sections: 1 });
      setEditingId(null);
      setShowForm(false);
    } catch (err) {
      const errorData = err.response?.data;
      if (errorData) {
        if (errorData.name) {
          setFormErrors(prev => ({ ...prev, name: errorData.name[0] }));
        } else {
          setError("Save failed. Please check your input.");
        }
      } else {
        setError("Network error. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = (batch) => {
    setFormData({
      name: batch.name,
      description: batch.description,
      semester_number: batch.semester_number,
      academic_year: batch.academic_year,
      total_sections: batch.total_sections || 1
    });
    setEditingId(batch.id);
    setShowForm(true);
    setFormErrors({});
  };
  
  const clearForm = () => {
    setFormData({ name: "", description: "", semester_number: 1, academic_year: "2024-2025", total_sections: 1 });
    setEditingId(null);
    setFormErrors({});
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure you want to delete this batch? This will affect all subjects assigned to this batch.")) {
      return;
    }

    try {
      await api.delete(`/api/timetable/batches/${id}/`);
      setBatches(batches.filter(batch => batch.id !== id));
      if (editingId === id) {
        clearForm();
        setShowForm(false);
      }
    } catch (err) {
      setError("Delete failed - batch might be in use by subjects.");
    }
  };

  const filteredBatches = batches.filter(batch =>
    batch.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    batch.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <Head>
        <title>Batch Management - Timetable System</title>
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={1} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Batch Management
            </h1>
            <p className="text-secondary/90">Manage academic batches and semesters</p>
          </div>

          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

          <div className="flex justify-between items-center mb-6">
            <div className="relative flex-1 max-w-md">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-secondary/70" />
              </div>
              <input
                type="text"
                placeholder="Search batches..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-card/50 backdrop-blur-sm border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
              />
            </div>

            <button
              onClick={() => {
                setShowForm(!showForm);
                if (!showForm) {
                  clearForm();
                }
              }}
              className="ml-4 px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
            >
              {showForm ? <X className="h-5 w-5" /> : <Plus className="h-5 w-5" />}
              {showForm ? "Cancel" : "Add Batch"}
            </button>
          </div>

          {/* Add/Edit Form */}
          {showForm && (
            <div className="mb-8 p-6 bg-card/50 backdrop-blur-sm border border-border rounded-xl">
              <h2 className="text-xl font-semibold text-primary mb-4">
                {editingId ? "Edit Batch" : "Add New Batch"}
              </h2>
              
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Batch Name */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Batch Name *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Hash className="h-5 w-5 text-secondary/70" />
                      </div>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleInputChange}
                        placeholder="e.g., 21SW, 22SW"
                        className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.name ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30`}
                        required
                      />
                    </div>
                    {formErrors.name && (
                      <p className="text-red-500 text-xs mt-1">{formErrors.name}</p>
                    )}
                  </div>

                  {/* Semester Number */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Semester Number *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <BookOpen className="h-5 w-5 text-secondary/70" />
                      </div>
                      <input
                        type="number"
                        name="semester_number"
                        value={formData.semester_number}
                        onChange={handleInputChange}
                        min="1"
                        max="8"
                        className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.semester_number ? 'border-red-500' : 'border-border'} rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30`}
                        required
                      />
                    </div>
                    {formErrors.semester_number && (
                      <p className="text-red-500 text-xs mt-1">{formErrors.semester_number}</p>
                    )}
                  </div>

                  {/* Total Sections */}
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Total Sections *
                    </label>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <Users className="h-5 w-5 text-secondary/70" />
                      </div>
                      <input
                        type="number"
                        name="total_sections"
                        value={formData.total_sections}
                        onChange={handleInputChange}
                        min="1"
                        max="5"
                        className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.total_sections ? 'border-red-500' : 'border-border'} rounded-xl text-primary focus:outline-none focus:ring-2 focus:ring-accent-cyan/30`}
                        required
                      />
                    </div>
                    <p className="text-xs text-secondary/70 mt-1">Number of sections (e.g., 3 for I, II, III)</p>
                    {formErrors.total_sections && (
                      <p className="text-red-500 text-xs mt-1">{formErrors.total_sections}</p>
                    )}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">
                    Description *
                  </label>
                  <input
                    type="text"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="e.g., 8th Semester - Final Year"
                    className={`w-full px-4 py-3 bg-background/95 border ${formErrors.description ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30`}
                    required
                  />
                  {formErrors.description && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.description}</p>
                  )}
                </div>

                {/* Academic Year */}
                <div>
                  <label className="block text-sm font-medium text-secondary mb-2">
                    Academic Year *
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <Calendar className="h-5 w-5 text-secondary/70" />
                    </div>
                    <input
                      type="text"
                      name="academic_year"
                      value={formData.academic_year}
                      onChange={handleInputChange}
                      placeholder="e.g., 2024-2025"
                      className={`w-full pl-10 pr-4 py-3 bg-background/95 border ${formErrors.academic_year ? 'border-red-500' : 'border-border'} rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30`}
                      required
                    />
                  </div>
                  {formErrors.academic_year && (
                    <p className="text-red-500 text-xs mt-1">{formErrors.academic_year}</p>
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
                      {editingId ? "Update Batch" : "Add Batch"}
                    </>
                  )}
                </button>
              </form>
            </div>
          )}

          {/* Batches List */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-accent-cyan" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredBatches.map((batch) => (
                <div key={batch.id} className="p-6 bg-card/50 backdrop-blur-sm border border-border rounded-xl hover:shadow-lg hover:shadow-accent-cyan/10 transition-all duration-300">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end rounded-lg">
                        <GraduationCap className="h-5 w-5 text-white" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-primary">{batch.name}</h3>
                        <p className="text-sm text-secondary">Semester {batch.semester_number}</p>
                        <p className="text-xs text-secondary/70">{batch.total_sections || 1} Section{(batch.total_sections || 1) > 1 ? 's' : ''}</p>
                      </div>
                    </div>
                    
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(batch)}
                        className="p-2 text-secondary hover:text-accent-cyan hover:bg-accent-cyan/10 rounded-lg transition-colors"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(batch.id)}
                        className="p-2 text-secondary hover:text-red-500 hover:bg-red-500/10 rounded-lg transition-colors"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <p className="text-secondary text-sm mb-3">{batch.description}</p>
                  <p className="text-xs text-secondary/70">Academic Year: {batch.academic_year}</p>
                </div>
              ))}
            </div>
          )}

          {filteredBatches.length === 0 && !loading && (
            <div className="text-center py-12">
              <GraduationCap className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
              <p className="text-secondary">No batches found</p>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default BatchManagement;

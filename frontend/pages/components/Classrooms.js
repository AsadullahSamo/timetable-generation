import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";
import { 
  Building2, 
  Users, 
  Plus, 
  Edit2, 
  Trash2, 
  Info, 
  Loader2, 
  ArrowLeft,
  CheckCircle2,
  AlertCircle,
  Search,
  X
} from 'lucide-react';

const Classrooms = () => {
  const [classrooms, setClassrooms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  
  const [formData, setFormData] = useState({
    name: "",
    capacity: ""
  });

  useEffect(() => {
    fetchClassrooms();
  }, []);

  const fetchClassrooms = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/timetable/classrooms/');
      setClassrooms(response.data);
    } catch (error) {
      setError('Failed to fetch classrooms');
      console.error('Error fetching classrooms:', error);
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

  const validateForm = () => {
    if (!formData.name.trim()) {
      setError("Classroom name is required");
      return false;
    }
    if (!formData.capacity || formData.capacity <= 0) {
      setError("Valid capacity is required");
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    
    if (!validateForm()) {
      return;
    }

    try {
      const payload = {
        name: formData.name.trim(),
        capacity: parseInt(formData.capacity)
      };

      if (editingId) {
        const response = await api.put(`/api/timetable/classrooms/${editingId}/`, payload);
        setClassrooms(classrooms.map(room => 
          room.id === editingId ? response.data : room
        ));
      } else {
        const response = await api.post('/api/timetable/classrooms/', payload);
        setClassrooms([...classrooms, response.data]);
      }

      // Reset form
      setFormData({ name: "", capacity: "" });
      setShowForm(false);
      setEditingId(null);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to save classroom');
      console.error('Error saving classroom:', error);
    }
  };

  const handleEdit = (classroom) => {
    setFormData({
      name: classroom.name,
      capacity: classroom.capacity.toString()
    });
    setEditingId(classroom.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this classroom?')) {
      return;
    }

    try {
      await api.delete(`/api/timetable/classrooms/${id}/`);
      setClassrooms(classrooms.filter(room => room.id !== id));
    } catch (error) {
      setError('Failed to delete classroom');
      console.error('Error deleting classroom:', error);
    }
  };

  const filteredClassrooms = classrooms.filter(room =>
    room.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <>
      <Head>
        <title>Classrooms - MUET Timetable System</title>
      </Head>
      <Navbar />
      
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-surface/30 pt-20">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-primary mb-2">Classrooms</h1>
              <p className="text-secondary">Manage classrooms and their capacities</p>
            </div>
            <Link href="/components/DepartmentConfig">
              <button className="flex items-center gap-2 px-4 py-2 bg-surface/80 hover:bg-surface text-secondary hover:text-primary rounded-xl border border-border transition-all">
                <ArrowLeft className="h-4 w-4" />
                Back to Config
              </button>
            </Link>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <span className="text-red-500">{error}</span>
              <button 
                onClick={() => setError(null)}
                className="ml-auto text-red-500 hover:text-red-400"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
              <input
                type="text"
                placeholder="Search classrooms..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-surface/80 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
              />
            </div>
            <button
              onClick={() => {
                setShowForm(true);
                setEditingId(null);
                setFormData({ name: "", capacity: "" });
                setError(null);
              }}
              className="flex items-center gap-2 px-6 py-3 bg-accent-cyan hover:bg-accent-cyan/90 text-white rounded-xl transition-all"
            >
              <Plus className="h-4 w-4" />
              Add Classroom
            </button>
          </div>

          {/* Form Modal */}
          {showForm && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="bg-surface rounded-2xl p-6 w-full max-w-md">
                <h2 className="text-xl font-semibold text-primary mb-4">
                  {editingId ? 'Edit Classroom' : 'Add New Classroom'}
                </h2>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Classroom Name *
                    </label>
                    <input
                      type="text"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      placeholder="e.g., Lab. No.1, C.R. 01"
                      className="w-full px-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Capacity *
                    </label>
                    <input
                      type="number"
                      name="capacity"
                      value={formData.capacity}
                      onChange={handleInputChange}
                      placeholder="e.g., 30"
                      min="1"
                      className="w-full px-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      required
                    />
                  </div>



                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowForm(false);
                        setEditingId(null);
                        setFormData({ name: "", capacity: "" });
                        setError(null);
                      }}
                      className="flex-1 px-4 py-3 bg-surface/80 hover:bg-surface text-secondary hover:text-primary rounded-xl border border-border transition-all"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      className="flex-1 px-4 py-3 bg-accent-cyan hover:bg-accent-cyan/90 text-white rounded-xl transition-all"
                    >
                      {editingId ? 'Update' : 'Add'} Classroom
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Classrooms List */}
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-accent-cyan" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredClassrooms.map((classroom) => (
                <div key={classroom.id} className="bg-surface/80 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-accent-cyan/10 rounded-lg">
                        <Building2 className="h-5 w-5 text-accent-cyan" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-primary">{classroom.name}</h3>
                        <p className="text-sm text-secondary">Capacity: {classroom.capacity}</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleEdit(classroom)}
                        className="p-2 text-secondary hover:text-accent-cyan transition-colors"
                        title="Edit classroom"
                      >
                        <Edit2 className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(classroom.id)}
                        className="p-2 text-secondary hover:text-red-500 transition-colors"
                        title="Delete classroom"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-2 text-sm text-secondary">
                    <Users className="h-4 w-4" />
                    <span>Capacity: {classroom.capacity} students</span>
                  </div>
                </div>
              ))}
              
              {filteredClassrooms.length === 0 && !loading && (
                <div className="col-span-full text-center py-12">
                  <Building2 className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
                  <p className="text-secondary">
                    {searchTerm ? 'No classrooms match your search.' : 'No classrooms added yet.'}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Classrooms;

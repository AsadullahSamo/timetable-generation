import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import BackButton from "./BackButton";
import api from "../utils/api";
import {
  Building2,
  Plus,
  Edit2,
  Trash2,
  Loader2,
  ArrowLeft,
  AlertCircle,
  X
} from 'lucide-react';

const Classrooms = () => {
  const [classrooms, setClassrooms] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    building: ""
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  

  useEffect(() => {
    fetchClassrooms();
  }, []);

  const fetchClassrooms = async () => {
    try {
      const response = await api.get('/api/timetable/classrooms/');
      setClassrooms(response.data);
    } catch (error) {
      setError('Failed to load classrooms');
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
    if (!formData.building.trim()) {
      setError("Building name is required");
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
        building: formData.building.trim()
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

      setFormData({ name: "", building: "" });
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
      building: classroom.building || ""
    });
    setEditingId(classroom.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    try {
      await api.delete(`/api/timetable/classrooms/${id}/`);
      setClassrooms(classrooms.filter(room => room.id !== id));
    } catch (error) {
      setError('Failed to delete classroom');
      console.error('Error deleting classroom:', error);
    }
  };

  const filteredClassrooms = classrooms;

  return (
    <>
      <Head>
        <title>Classrooms - MUET Timetable System</title>
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={4} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">Classrooms</h1>
              <p className="text-secondary/90">Manage classrooms and their buildings</p>
            </div>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3">
              <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
              <span className="text-red-500">{error}</span>
              <button onClick={() => setError(null)} className="ml-auto text-red-500 hover:text-red-400">
                <X className="h-4 w-4" />
              </button>
            </div>
          )}

          <div className="flex items-center justify-end mb-6">
            <button
              onClick={() => {
                setShowForm(true);
                setEditingId(null);
                setFormData({ name: "", building: "" });
                setError(null);
              }}
              className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300"
            >
              <Plus className="h-4 w-4" />
              Add Classroom
            </button>
          </div>

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
                      placeholder="e.g., C.R. 01"
                      className="w-full px-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-secondary mb-2">
                      Building *
                    </label>
                    <input
                      type="text"
                      name="building"
                      value={formData.building}
                      onChange={handleInputChange}
                      placeholder="e.g., Main Building, Block A"
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
                        setFormData({ name: "", building: "" });
                        setError(null);
                      }}
                      className="flex-1 px-4 py-3 bg-background/95 hover:bg-surface text-secondary hover:text-primary rounded-xl border border-border transition-all"
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

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-accent-cyan" />
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredClassrooms.map((classroom) => (
                <div key={classroom.id} className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 bg-accent-cyan/10 rounded-lg">
                        <Building2 className="h-5 w-5 text-accent-cyan" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-primary">{classroom.name}</h3>
                        <p className="text-sm text-secondary">{classroom.building}</p>
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
                </div>
              ))}

              {classrooms.length === 0 && !loading && (
                <div className="col-span-full text-center py-12">
                  <Building2 className="h-12 w-12 text-secondary/50 mx-auto mb-4" />
                  <p className="text-secondary">No classrooms added yet.</p>
                </div>
              )}
            </div>
          )}

          {/* Navigation */}
          <div className="flex justify-between mt-8">
            <BackButton href="/components/Teachers" label="Back: Teachers" />
            <Link href="/components/TeacherAssignments">
              <button className="px-6 py-3 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300">
                Next: Teacher Assignments
                <ArrowLeft className="h-4 w-4 rotate-180" />
              </button>
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default Classrooms;
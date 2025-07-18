import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";
import { 
  GraduationCap, 
  Clock, 
  Plus, 
  Edit2, 
  Trash2, 
  Info, 
  Loader2, 
  ArrowLeft, 
  ArrowRight,
  Users,
  AlertCircle,
  Search,
  CheckCircle2,
  BarChart3,
  X,
  RefreshCw
} from 'lucide-react';

const ClassesConfig = () => {
  const [configurations, setConfigurations] = useState([]);
  const [classData, setClassData] = useState({
    start_time: "08:00",
    end_time: "13:00",
    min_lessons: 0,
    max_lessons: 5,
    class_groups: []
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showTooltip, setShowTooltip] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(null);
  const [activeConfig, setActiveConfig] = useState(null);

  // Stats calculation
  const stats = {
    totalClasses: configurations.reduce((acc, config) => acc + config.class_groups.length, 0),
    totalConfigs: configurations.length,
    avgLessons: configurations.reduce((acc, config) => acc + (config.max_lessons + config.min_lessons) / 2, 0) / configurations.length || 0
  };

  useEffect(() => {
    const fetchConfigurations = async () => {
      try {
        const response = await api.get('/api/timetable/class-groups/');
        setConfigurations(response.data);
      } catch (error) {
        setError('Failed to load configurations');
      }
    };
    fetchConfigurations();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setClassData(prev => ({
      ...prev,
      [name]: name.endsWith('_lessons') ? Number(value) : value
    }));
  };

  const validateConfiguration = () => {
    if (classData.class_groups.length === 0) {
      setError("Please select at least one class.");
      return false;
    }
    if (classData.min_lessons < 0) {
      setError("Minimum lessons cannot be negative.");
      return false;
    }
    if (classData.max_lessons < classData.min_lessons) {
      setError("Maximum lessons must be greater than or equal to minimum lessons.");
      return false;
    }
    if (classData.start_time >= classData.end_time) {
      setError("Start time must be before end time.");
      return false;
    }

    return true;
  };

  const handleAddOrUpdateConfiguration = async () => {
    if (!validateConfiguration()) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...classData,
        start_time: `${classData.start_time}:00`,
        end_time: `${classData.end_time}:00`
      };

      let response;
      if (editingId) {
        response = await api.put(`/api/timetable/class-groups/${editingId}/`, payload);
        setConfigurations(configurations.map(config => 
          config.id === editingId ? response.data : config
        ));
      } else {
        response = await api.post('/api/timetable/class-groups/', payload);
        setConfigurations([...configurations, response.data]);
      }

      setClassData({
        start_time: "08:00",
        end_time: "13:00",
        min_lessons: 0,
        max_lessons: 5,
        class_groups: []
      });
      setEditingId(null);
      setActiveConfig(response.data.id);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to save configuration');
    } finally {
      setLoading(false);
    }
  };

  const handleEditConfiguration = (id) => {
    const configToEdit = configurations.find(config => config.id === id);
    setClassData({
      ...configToEdit,
      start_time: configToEdit.start_time.slice(0, 5),
      end_time: configToEdit.end_time.slice(0, 5)
    });
    setEditingId(id);
    setActiveConfig(id);
  };

  const handleDeleteConfiguration = async (id) => {
    setShowDeleteConfirm(id);
  };

  const confirmDelete = async () => {
    try {
      await api.delete(`/api/timetable/class-groups/${showDeleteConfirm}/`);
      setConfigurations(configurations.filter(config => config.id !== showDeleteConfirm));
      setShowDeleteConfirm(null);
    } catch (error) {
      setError('Failed to delete configuration');
    }
  };

  const filteredConfigurations = configurations.filter(config => 
    config.class_groups.some(group => 
      group.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const handleClassGroupsChange = (e) => {
    const value = e.target.value;
    setClassData(prev => ({
      ...prev,
      class_groups: value ? value.split(',').map(c => c.trim()) : []
    }));
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className="flex min-h-screen bg-background text-primary font-sans">
        <Navbar number={2}/>

        <div className="flex-1 p-8 max-w-7xl">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end mb-2">
              Classes Configuration
            </h1>
            <p className="text-secondary/90">Configure class groups and their schedule constraints</p>
          </div>
          
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/20 rounded-xl mb-6 flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <p className="text-red-500 text-sm font-medium">{error}</p>
            </div>
          )}

          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <GraduationCap className="h-5 w-5 text-accent-cyan" />
                Class Settings
              </h2>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <button
                    type="button"
                    className="text-secondary hover:text-primary transition-colors"
                    onMouseEnter={() => setShowTooltip("class")}
                    onMouseLeave={() => setShowTooltip("")}
                  >
                    <Info className="h-5 w-5" />
                  </button>
                  {showTooltip === "class" && (
                    <div className="absolute right-0 top-full mt-2 p-3 bg-surface border border-border rounded-xl shadow-lg text-sm text-secondary w-64 z-50">
                      Configure time constraints and lesson limits for each class group. This affects how the timetable will be generated.
                    </div>
                  )}
                </div>
                <button
                  onClick={() => {
                    setEditingId(null);
                    setClassData({
                      start_time: "08:00",
                      end_time: "13:00",
                      min_lessons: 0,
                      max_lessons: 5,
                      class_groups: []
                    });
                  }}
                  className="text-secondary hover:text-accent-cyan transition-colors flex items-center gap-1"
                  title="Clear all fields"
                >
                  <RefreshCw className="h-5 w-5" />
                  <span className="text-sm">Clear Fields</span>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              {/* Time Inputs */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Starting hour</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                  <input
                    type="time"
                    name="start_time"
                    value={classData.start_time}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Ending hour</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                  <input
                    type="time"
                    name="end_time"
                    value={classData.end_time}
                    onChange={handleInputChange}
                    className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    required
                  />
                </div>
              </div>



              {/* Lessons Inputs */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Min. lessons/day</label>
                <input
                  type="number"
                  name="min_lessons"
                  value={classData.min_lessons}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  min="0"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Max. lessons/day</label>
                <input
                  type="number"
                  name="max_lessons"
                  value={classData.max_lessons}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  min="1"
                  required
                />
              </div>

              {/* Class Groups */}
              <div className="space-y-2">
                <label className="text-sm font-medium text-secondary">Class Groups</label>
                <div className="relative">
                  <Users className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                  <input
                    type="text"
                    name="class_groups"
                    placeholder="Enter classes (e.g., A, B, C)"
                    value={classData.class_groups.join(', ')}
                    onChange={handleClassGroupsChange}
                    className="w-full pl-10 pr-4 py-3 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                    required
                  />
                </div>
              </div>
            </div>

            <button 
              onClick={handleAddOrUpdateConfiguration}
              className="w-full py-3 px-4 bg-gradient-to-r from-gradient-cyan-start to-gradient-pink-end text-white font-medium rounded-xl flex items-center justify-center gap-2 hover:opacity-90 hover:shadow-lg hover:shadow-accent-cyan/30 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <Plus className="h-5 w-5" />
                  {editingId ? "Update" : "Add"} Configuration
                </>
              )}
            </button>

          </div>

          {/* Configured Classes Table */}
          <div className="bg-surface/95 backdrop-blur-sm p-6 rounded-2xl border border-border shadow-soft mb-8">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-primary flex items-center gap-2">
                <Users className="h-5 w-5 text-accent-cyan" />
                Configured Classes
              </h2>
              <div className="flex items-center gap-4">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-secondary/70" />
                  <input
                    type="text"
                    placeholder="Search classes..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 pr-4 py-2 bg-background/95 border border-border rounded-xl text-primary placeholder-secondary/70 focus:outline-none focus:ring-2 focus:ring-accent-cyan/30 focus:border-accent-cyan/30"
                  />
                </div>
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
                      View and manage your configured class groups. You can edit or delete existing configurations.
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-background/95">
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Classes</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Start Time</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">End Time</th>

                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Min Lessons</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Max Lessons</th>
                    <th className="px-4 py-3 text-left border border-border text-secondary font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredConfigurations.map((config) => (
                    <tr 
                      key={config.id} 
                      className={`hover:bg-background/50 transition-colors ${
                        activeConfig === config.id ? 'bg-accent-cyan/5' : ''
                      }`}
                    >
                      <td className="px-4 py-3 border border-border">
                        <div className="flex items-center gap-2">
                          {config.class_groups.join(", ")}
                          {activeConfig === config.id && (
                            <CheckCircle2 className="h-4 w-4 text-accent-cyan" />
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 border border-border">{config.start_time.slice(0, 5)}</td>
                      <td className="px-4 py-3 border border-border">{config.end_time.slice(0, 5)}</td>

                      <td className="px-4 py-3 border border-border">{config.min_lessons}</td>
                      <td className="px-4 py-3 border border-border">{config.max_lessons}</td>
                      <td className="px-4 py-3 border border-border">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleEditConfiguration(config.id)}
                            className="text-secondary hover:text-accent-cyan transition-colors"
                            title="Edit configuration"
                          >
                            <Edit2 className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteConfiguration(config.id)}
                            className="text-secondary hover:text-red-500 transition-colors"
                            title="Delete configuration"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/DepartmentConfig"
              className="px-6 py-3 border border-border text-secondary rounded-xl hover:text-primary hover:border-accent-cyan/30 transition-colors flex items-center gap-2"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </Link>

            <Link
              href="/components/Subjects"
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
              Are you sure you want to delete this configuration? This action cannot be undone.
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

export default ClassesConfig;
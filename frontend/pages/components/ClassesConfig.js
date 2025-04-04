import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const ClassesConfig = () => {
  const [configurations, setConfigurations] = useState([]);
  const [classData, setClassData] = useState({
    start_time: "08:00",
    end_time: "13:00",
    latest_start_time: "08:00",
    min_lessons: 0,
    max_lessons: 5,
    class_groups: []
  });
  const [editingId, setEditingId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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

  const handleAddOrUpdateConfiguration = async () => {
    if (classData.class_groups.length === 0) {
      alert("Please select at least one class.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = {
        ...classData,
        start_time: `${classData.start_time}:00`,
        end_time: `${classData.end_time}:00`,
        latest_start_time: `${classData.latest_start_time}:00`
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
        latest_start_time: "08:00",
        min_lessons: 0,
        max_lessons: 5,
        class_groups: []
      });
      setEditingId(null);
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
      end_time: configToEdit.end_time.slice(0, 5),
      latest_start_time: configToEdit.latest_start_time.slice(0, 5)
    });
    setEditingId(id);
  };

  const handleDeleteConfiguration = async (id) => {
    try {
      await api.delete(`/api/timetable/class-groups/${id}/`);
      setConfigurations(configurations.filter(config => config.id !== id));
    } catch (error) {
      setError('Failed to delete configuration');
    }
  };

  return (
    <>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>

      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
        <Navbar number={2}/>

        <div className="flex-1 p-8 max-w-7xl">
          <h1 className="text-3xl text-gray-50 mb-8">Classes Configuration</h1>
          
          {error && (
            <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            <h2 className="text-xl text-purple-400 mb-4">Class Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
              {/* Time Inputs */}
              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Starting hour:</label>
                <input
                  type="time"
                  name="start_time"
                  value={classData.start_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Ending hour:</label>
                <input
                  type="time"
                  name="end_time"
                  value={classData.end_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Latest start time:</label>
                <input
                  type="time"
                  name="latest_start_time"
                  value={classData.latest_start_time}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>

              {/* Lessons Inputs */}
              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Min. lessons/day:</label>
                <input
                  type="number"
                  name="min_lessons"
                  value={classData.min_lessons}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  min="0"
                  required
                />
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Max. lessons/day:</label>
                <input
                  type="number"
                  name="max_lessons"
                  value={classData.max_lessons}
                  onChange={handleInputChange}
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  min="1"
                  required
                />
              </div>

              {/* Class Groups */}
              <div className="flex flex-col gap-2">
                <label className="text-gray-400 text-sm">Class Groups:</label>
                <input
                  type="text"
                  name="class_groups"
                  placeholder="Enter classes (e.g., A, B, C)"
                  value={classData.class_groups.join(", ")}
                  onChange={(e) =>
                    setClassData({
                      ...classData,
                      class_groups: e.target.value.split(",").map(c => c.trim())
                    })
                  }
                  className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
                  required
                />
              </div>
            </div>

            <button 
              onClick={handleAddOrUpdateConfiguration}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {loading ? "Saving..." : editingId ? "Update" : "Add"} Configuration
            </button>
          </div>

          {/* Configured Classes Table */}
          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            <h2 className="text-xl text-purple-400 mb-4">Configured Classes</h2>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-gray-900">
                    <th className="px-4 py-3 text-left border border-gray-700">Classes</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Start Time</th>
                    <th className="px-4 py-3 text-left border border-gray-700">End Time</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Latest Start</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Min Lessons</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Max Lessons</th>
                    <th className="px-4 py-3 text-left border border-gray-700">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {configurations.map((config) => (
                    <tr key={config.id} className="hover:bg-gray-700/50">
                      <td className="px-4 py-3 border border-gray-700">{config.class_groups.join(", ")}</td>
                      <td className="px-4 py-3 border border-gray-700">{config.start_time.slice(0, 5)}</td>
                      <td className="px-4 py-3 border border-gray-700">{config.end_time.slice(0, 5)}</td>
                      <td className="px-4 py-3 border border-gray-700">{config.latest_start_time.slice(0, 5)}</td>
                      <td className="px-4 py-3 border border-gray-700">{config.min_lessons}</td>
                      <td className="px-4 py-3 border border-gray-700">{config.max_lessons}</td>
                      <td className="px-4 py-3 border border-gray-700">
                        <button
                          onClick={() => handleEditConfiguration(config.id)}
                          className="text-purple-400 hover:text-purple-300 transition-colors mr-4"
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button
                          onClick={() => handleDeleteConfiguration(config.id)}
                          className="text-red-400 hover:text-red-300 transition-colors"
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/SchoolConfig"
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            >
              ← Back
            </Link>

            <Link
              href="/components/SubjectConfig"
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Next →
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default ClassesConfig;
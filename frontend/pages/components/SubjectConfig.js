import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const SubjectConfig = () => {
  const [subjects, setSubjects] = useState([]);
  const [formData, setFormData] = useState({
    name: "",
    code: "",
    credits: 3
  });
  const [searchQuery, setSearchQuery] = useState("");
  const [editingId, setEditingId] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

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
    fetchSubjects();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === "credits" ? Math.max(1, parseInt(value) || 1) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!formData.name.trim() || !formData.code.trim()) {
      setError("Subject name and code are required");
      return;
    }

    try {
      if (editingId) {
        // Update existing subject
        const { data } = await api.put(`/api/timetable/subjects/${editingId}/`, formData);
        setSubjects(subjects.map(subject => 
          subject.id === editingId ? data : subject
        ));
      } else {
        // Create new subject
        const { data } = await api.post("/api/timetable/subjects/", formData);
        setSubjects([...subjects, data]);
      }
      setFormData({ name: "", code: "", credits: 3 });
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
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this subject?")) return;
    
    try {
      await api.delete(`/api/timetable/subjects/${id}/`);
      setSubjects(subjects.filter(sub => sub.id !== id));
    } catch (err) {
      setError("Delete failed - subject might be in use.");
    }
  };

  const handleEdit = (subject) => {
    setFormData({
      name: subject.name,
      code: subject.code,
      credits: subject.credits
    });
    setEditingId(subject.id);
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

      <div className="flex min-h-screen bg-gray-900 text-gray-100 font-sans">
        <Navbar number={3} />
        <div className="flex-1 p-8 max-w-7xl">
          <h2 className="text-3xl text-gray-50 mb-8">Subject Configuration</h2>

          <div className="flex items-center gap-4 mb-6">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search subjects..."
              className="flex-1 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
            />
            <button className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
              <i className="fas fa-search"></i>
            </button>
          </div>

          {error && (
            <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="Subject Name"
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
              />
              <input
                type="text"
                name="code"
                value={formData.code}
                onChange={handleInputChange}
                placeholder="Subject Code"
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
              />
              <input
                type="number"
                name="credits"
                placeholder="Credits"
                value={formData.credits}
                onChange={handleInputChange}
                min="1"
                max="10"
                className="w-full px-4 py-3 bg-gray-900 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
              />
            </div>
            <button
              onClick={handleSubmit}
              className="w-full px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={loading}
            >
              {editingId ? "Update Subject" : "Add Subject"}
            </button>
          </div>

          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            {loading ? (
              <div className="text-center text-purple-400 italic py-8">
                Loading subjects...
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-900">
                      <th className="px-4 py-3 text-left border border-gray-700">Subject Name</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Code</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Credits</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSubjects.map((subject) => (
                      <tr key={subject.id} className="hover:bg-gray-700/50">
                        <td className="px-4 py-3 border border-gray-700">{subject.name}</td>
                        <td className="px-4 py-3 border border-gray-700">{subject.code}</td>
                        <td className="px-4 py-3 border border-gray-700">{subject.credits}</td>
                        <td className="px-4 py-3 border border-gray-700">
                          <button
                            onClick={() => handleEdit(subject)}
                            className="text-purple-400 hover:text-purple-300 transition-colors mr-4"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button
                            onClick={() => handleDelete(subject.id)}
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
            )}
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/ClassesConfig"
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            >
              ← Back
            </Link>

            <Link
              href="/components/TeachersConfig"
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

export default SubjectConfig;
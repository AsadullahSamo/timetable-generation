// frontend/pages/components/TeachersConfig.js
import React, { useState, useEffect } from "react";
import Head from "next/head";
import Navbar from "./Navbar";
import Link from "next/link";
import api from "../utils/api";

const TeachersConfig = () => {
  const [teachers, setTeachers] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const { data } = await api.get("/api/timetable/teachers/");
        setTeachers(data);
      } catch (err) {
        setError("Failed to load teachers. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchTeachers();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this teacher?")) return;
    
    try {
      await api.delete(`/api/timetable/teachers/${id}/`);
      setTeachers(teachers.filter(teacher => teacher.id !== id));
    } catch (err) {
      setError("Delete failed - teacher might be in use.");
    }
  };

  const handleEdit = (id) => {
    window.location.href = `/components/AddTeacher?id=${id}`;
  };

  const filteredTeachers = teachers.filter(teacher =>
    teacher.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    teacher.email.toLowerCase().includes(searchQuery.toLowerCase())
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
        <Navbar number={4} />
        <div className="flex-1 p-8 max-w-7xl">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl text-gray-50">Teachers Configuration</h2>
            <Link
              href="/components/AddTeacher"
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              Add New Teacher
            </Link>
          </div>

          <div className="mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search teachers..."
              className="w-full md:w-96 px-4 py-3 bg-gray-800 border border-gray-700 rounded-lg text-gray-100 focus:outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20"
            />
          </div>

          {error && (
            <div className="bg-red-900/50 text-red-200 p-4 rounded-lg mb-6">
              {error}
            </div>
          )}

          <div className="bg-gray-800 rounded-lg p-6 mb-8 border border-gray-700">
            {loading ? (
              <div className="text-center text-purple-400 italic py-8">
                <i className="fas fa-spinner fa-spin text-2xl mb-4"></i>
                <p>Loading teachers...</p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full border-collapse">
                  <thead>
                    <tr className="bg-gray-900">
                      <th className="px-4 py-3 text-left border border-gray-700">Teacher Name</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Email</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Subjects</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Max Lessons/Day</th>
                      <th className="px-4 py-3 text-left border border-gray-700">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredTeachers.map((teacher) => (
                      <tr key={teacher.id} className="hover:bg-gray-700/50">
                        <td className="px-4 py-3 border border-gray-700">{teacher.name}</td>
                        <td className="px-4 py-3 border border-gray-700">{teacher.email}</td>
                        <td className="px-4 py-3 border border-gray-700">
                          {teacher.subject_names?.join(', ') || 'No subjects'}
                        </td>
                        <td className="px-4 py-3 border border-gray-700">{teacher.max_lessons_per_day}</td>
                        <td className="px-4 py-3 border border-gray-700">
                          <button
                            onClick={() => handleEdit(teacher.id)}
                            className="text-purple-400 hover:text-purple-300 transition-colors mr-4"
                          >
                            <i className="fas fa-edit"></i>
                          </button>
                          <button
                            onClick={() => handleDelete(teacher.id)}
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

            {!loading && teachers.length === 0 && (
              <div className="text-center text-gray-400 py-12">
                <i className="fas fa-user-tie text-4xl mb-4"></i>
                <p>No teachers found. Add your first teacher!</p>
              </div>
            )}
          </div>

          <div className="flex justify-between mt-8">
            <Link
              href="/components/SubjectConfig"
              className="px-6 py-3 border border-gray-700 text-gray-400 rounded-lg hover:border-purple-500 hover:text-purple-400 transition-colors"
            >
              ← Back
            </Link>

            <Link
              href="/components/LessonsConfig"
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

export default TeachersConfig;


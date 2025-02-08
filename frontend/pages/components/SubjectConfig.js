import React, { useState, useEffect } from "react";
import styles from "./SubjectConfig.module.css";
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
        const { data } = await api.get("/timetable/subjects/");
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
        const { data } = await api.put(`/timetable/subjects/${editingId}/`, formData);
        setSubjects(subjects.map(sub => sub.id === editingId ? data : sub));
      } else {
        // Create new subject
        const { data } = await api.post("/timetable/subjects/", formData);
        setSubjects([...subjects, data]);
      }
      setFormData({ name: "", code: "", credits: 3 });
      setEditingId(null);
    } catch (err) {
      setError(err.response?.data?.detail || "Operation failed. Please check your input.");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this subject?")) return;
    
    try {
      await api.delete(`/timetable/subjects/${id}/`);
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

      <div className={styles.container}>
        <Navbar number={4} />
        <div className={styles.mainContent}>
          <h2 className={styles.mainHeading}>Subject Configuration</h2>

          <div className={styles.searchBox}>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search subjects..."
              className={styles.inputSearch}
            />
            <button className={styles.btnSearch}>
              <i className="fas fa-search"></i>
            </button>
          </div>

          {error && <div className={styles.errorAlert}>{error}</div>}

          <div className={styles.inputContainer}>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleInputChange}
              placeholder="Subject Name"
              className={styles.input}
            />
            <input
              type="text"
              name="code"
              value={formData.code}
              onChange={handleInputChange}
              placeholder="Subject Code"
              className={styles.input}
            />
            <input
              type="number"
              name="credits"
              placeholder="Credits"
              value={formData.credits}
              onChange={handleInputChange}
              min="1"
              max="10"
              className={styles.input}
            />
            <button
              onClick={handleSubmit}
              className={styles.primaryButton}
              disabled={loading}
            >
              {editingId ? "Update Subject" : "Add Subject"}
            </button>
          </div>

          <div className={styles.outputContainer}>
            {loading ? (
              <div className={styles.loading}>Loading subjects...</div>
            ) : (
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Subject Name</th>
                    <th>Code</th>
                    <th>Credits</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredSubjects.map((subject) => (
                    <tr key={subject.id}>
                      <td>{subject.name}</td>
                      <td>{subject.code}</td>
                      <td>{subject.credits}</td>
                      <td>
                        <button
                          onClick={() => handleEdit(subject)}
                          className={styles.iconButton}
                        >
                          <i className="fas fa-edit"></i>
                        </button>
                        <button
                          onClick={() => handleDelete(subject.id)}
                          className={styles.iconButton}
                        >
                          <i className="fas fa-trash"></i>
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          <div className={styles.navigation}>
            <Link href="/components/ClassesConfig" className={styles.primaryButton}>
              ← Back
            </Link>
            <Link href="/components/TeachersConfig" className={styles.primaryButton}>
              Next →
            </Link>
          </div>
        </div>
      </div>
    </>
  );
};

export default SubjectConfig;
// frontend/pages/components/TeachersConfig.js
import Link from "next/link";
import styles from "./TeachersConfig.module.css";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Navbar from "./Navbar";
import api from "../utils/api";

const TeachersConfig = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const router = useRouter();

  useEffect(() => {
    const fetchTeachers = async () => {
      try {
        const response = await api.get('/timetable/teachers/');
        setTeachers(response.data);
      } catch (error) {
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
      await api.delete(`/timetable/teachers/${id}/`);
      setTeachers(teachers.filter(teacher => teacher.id !== id));
    } catch (error) {
      setError("Delete failed - teacher might be assigned to classes.");
    }
  };

  const handleEdit = (id) => {
    router.push(`/components/AddTeacher?id=${id}`);
  };

  const filteredTeachers = teachers.filter(teacher =>
    teacher.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    teacher.email.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.container}>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>
      
      <Navbar number={5} />

      <div className={styles.mainContent}>
        <div className={styles.header}>
          <h1>Teachers</h1>
          <Link href="/components/AddTeacher">
            <button className={styles.primaryButton}>+ New Teacher</button>
          </Link>
        </div>

        {error && <div className={styles.errorAlert}>{error}</div>}

        <div className={styles.searchContainer}>
          <input
            type="text"
            placeholder="Search teacher..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={styles.searchInput}
          />
        </div>

        <div className={styles.tableContainer}>
          {loading ? (
            <div className={styles.loading}>
              <i className="fas fa-spinner fa-spin"></i> Loading teachers...
            </div>
          ) : (
            <table className={styles.table}>
              <thead>
                <tr>
                  <th>Teacher Name</th>
                  <th>Email</th>
                  <th>Subjects</th>
                  <th>Max Lessons/Day</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredTeachers.map((teacher) => (
                  <tr key={teacher.id}>
                    <td>{teacher.name}</td>
                    <td>{teacher.email}</td>
                    <td>{teacher.subject_names?.join(', ') || 'No subjects'}</td>
                    <td>{teacher.max_lessons_per_day}</td>
                    <td>
                      <button 
                        onClick={() => handleEdit(teacher.id)} 
                        className={styles.iconButton}
                      >
                        <i className="fas fa-edit" />
                      </button>
                      <button 
                        onClick={() => handleDelete(teacher.id)} 
                        className={styles.iconButton}
                      >
                        <i className="fas fa-trash" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          {!loading && teachers.length === 0 && (
            <div className={styles.emptyState}>
              <i className="fas fa-chalkboard-teacher" />
              <p>No teachers found. Add your first teacher!</p>
            </div>
          )}
        </div>

        <div className={styles.navigation}>
          <Link href="/components/SubjectConfig" className={styles.primaryButton}>
            ← Back
          </Link>
          <Link href="/components/LessonsConfig" className={styles.primaryButton}>
            Next →
          </Link>
        </div>
      </div>
    </div>
  );
};

export default TeachersConfig;

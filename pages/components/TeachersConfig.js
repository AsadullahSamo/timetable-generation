// TeachersConfig.js
import Link from "next/link";
import styles from "./TeachersConfig.module.css";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import Head from "next/head";
import Navbar from "./Navbar";

const TeachersConfig = () => {
  const [searchQuery, setSearchQuery] = useState("");
  const [teachers, setTeachers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const savedTeachers = JSON.parse(localStorage.getItem("teachers")) || [];
    setTeachers(savedTeachers);
  }, []);

  const handleDelete = (index) => {
    const updatedTeachers = teachers.filter((_, i) => i !== index);
    setTeachers(updatedTeachers);
    localStorage.setItem("teachers", JSON.stringify(updatedTeachers));
  };

  const handleEdit = (index) => {
    router.push(`/components/AddTeacher?index=${index}`);
  };

  const filteredTeachers = teachers.filter(teacher =>
    teacher.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className={styles.container}>
      <Head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" />
      </Head>
      
      <Navbar number={5}/>

      <div className={styles.mainContent}>
        <div className={styles.header}>
          <h1>Teachers</h1>
          <Link href="/components/AddTeacher">
            <button className={styles.primaryButton}>+ New Teacher</button>
          </Link>
        </div>

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
          <table className={styles.table}>
            <thead>
              <tr>
                <th>Teacher Name</th>
                <th>Constraints</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredTeachers.map((teacher, index) => (
                <tr key={index}>
                  <td>{teacher.name}</td>
                  <td>
                    {Object.keys(teacher.mandatory || {}).length > 0 && 'Mandatory '}
                    {Object.keys(teacher.preferable || {}).length > 0 && 'Preferable'}
                  </td>
                  <td>
                    <button onClick={() => handleEdit(index)} className={styles.iconButton}>
                      <i className="fas fa-edit" />
                    </button>
                    <button onClick={() => handleDelete(index)} className={styles.iconButton}>
                      <i className="fas fa-trash" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {teachers.length === 0 && (
            <div className={styles.emptyState}>
              <i className="fas fa-chalkboard-teacher" />
              <p>You have not yet added any teachers</p>
            </div>
          )}
        </div>

        <div className={styles.pagination}>
          <span>Items per page: 10</span>
          <div className={styles.pageControls}>
            <button className={styles.navButton}>Previous</button>
            <span>1-1 of 1</span>
            <button className={styles.navButton}>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TeachersConfig;
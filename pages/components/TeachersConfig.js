import Link from "next/link";
import styles from "./TeachersConfig.module.css";
import { useState, useEffect } from "react";
import { useRouter } from "next/router"; // For routing
import Head from "next/head";

const TeachersConfig = () => {
  const [searchQuery, setSearchQuery] = useState(""); // State to hold search query
  const [teachers, setTeachers] = useState([]);
  const router = useRouter();

  useEffect(() => {
    const savedTeachers = JSON.parse(localStorage.getItem("teachers")) || [];
    setTeachers(savedTeachers);
  }, []);

  const handleDelete = (index) => {
    const updatedTeachers = [...teachers];
    updatedTeachers.splice(index, 1);
    setTeachers(updatedTeachers);
    localStorage.setItem("teachers", JSON.stringify(updatedTeachers));
  };

  const handleEdit = (teacherIndex) => {
    const teacherToEdit = teachers[teacherIndex];
    router.push({
      pathname: "/components/AddTeacher",
      query: { teacher: JSON.stringify(teacherToEdit), index: teacherIndex },
    });
  };

  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value); // Update search query state
  };

  // Filter teachers based on the search query
  const filteredTeachers = teachers.filter((teacher) =>
    teacher.name.toLowerCase().includes(searchQuery.toLowerCase())
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
        <div className={styles.headerContainer}>
          <h1 className={styles.header}>Teachers</h1>
          <Link href="/components/AddTeacher" passHref>
            <button className={styles.newTeacherButton}>+ New Teacher</button>
          </Link>
        </div>

        <div className={styles.searchBox}>
          <label className={styles.label}>
            <button className={styles.btnSearch}>
              <i className="fas fa-search"></i>
            </button>
            <input
              type="text"
              value={searchQuery}
              onChange={handleSearchChange}
              placeholder="Search Teacher Name"
              className={styles.inputSearch}
            />
          </label>
        </div>

        <div className={styles.listContainer}>
          {filteredTeachers.length === 0 ? (
            <div className={styles.noTeachersContainer}>
              <img
                src="/images/no-teachers.svg" // Replace with your image asset
                alt="No Teachers"
                className={styles.noTeachersImage}
              />
              <p className={styles.noTeachersText}>
                You have not yet added any teachers.
              </p>
            </div>
          ) : (
            filteredTeachers.map((teacher, index) => (
              <div key={index} className={styles.teacherCard}>
                <div className={styles.teacherDetails}>
                  <span className={styles.teacherName}>{teacher.name}</span>
                  <span className={styles.teacherConstraints}>
                    {Object.keys(teacher.unavailability || {}).length > 0
                      ? "Constraints added"
                      : "-"}
                  </span>
                </div>
                <div className={styles.actionButtons}>
                  <button
                    className={styles.editButton}
                    onClick={() => handleEdit(index)}
                  >
                    <i className="fas fa-pencil-alt"></i>
                  </button>
                  <button
										style={{ marginLeft: "20px" }}
                    className={styles.deleteButton}
                    onClick={() => handleDelete(index)}
                  >
                    <i className="fas fa-trash-alt"></i>
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default TeachersConfig;

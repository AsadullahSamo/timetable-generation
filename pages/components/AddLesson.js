import React from "react";
import styles from "./AddLesson.module.css";
import Link from "next/link";
import Head from "next/head";

const AddLesson = () => {
  return (
    <>
      <Head>
        <link
          rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
        />
      </Head>
      <div className={styles.container}>
        <div className={styles.content}>
          <h1 className={styles.title}>Lessons Configuration</h1>
          <p className={styles.subtitle}>
            Start creating lessons tailored to your needs.
          </p>
          <Link href="/components/AddLessonDetails" passHref>
            <button className={styles.addLessonButton}>
              <i className="fas fa-plus-circle"></i> Add Lesson
            </button>
          </Link>
        </div>
      </div>
    </>
  );
};

export default AddLesson;

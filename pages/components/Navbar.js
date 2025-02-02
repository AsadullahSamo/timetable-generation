import React from 'react'
import styles from "./Navbar.module.css";

export default function Navbar({number}) {
  return (
    <div className={styles.sidebar}>
			<div className={styles.menu}>
				{[1, 2, 3, 4, 5, 6, 7].map((num) => (
					<div
						key={num}
						className={`${styles.menuItem} ${num === number ? styles.active : ""}`}
					>
						{num}. {["School config", "Classes", "Divisions", "Subjects", "Teachers", "Lessons", "Timetable constraints"][num - 1]}
					</div>
				))}
			</div>
    </div>
  )
}

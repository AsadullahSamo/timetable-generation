-- Check all users and their data
SELECT 
    u.id,
    u.username,
    u.email,
    u.is_superuser,
    COUNT(DISTINCT s.id) as subjects_count,
    COUNT(DISTINCT t.id) as teachers_count,
    COUNT(DISTINCT c.id) as classrooms_count,
    COUNT(DISTINCT b.id) as batches_count,
    COUNT(DISTINCT sc.id) as configs_count,
    COUNT(DISTINCT te.id) as entries_count
FROM users_user u
LEFT JOIN timetable_subject s ON u.id = s.owner_id
LEFT JOIN timetable_teacher t ON u.id = t.owner_id
LEFT JOIN timetable_classroom c ON u.id = c.owner_id
LEFT JOIN timetable_batch b ON u.id = b.owner_id
LEFT JOIN timetable_scheduleconfig sc ON u.id = sc.owner_id
LEFT JOIN timetable_timetableentry te ON u.id = te.owner_id
GROUP BY u.id, u.username, u.email, u.is_superuser
ORDER BY u.id; 
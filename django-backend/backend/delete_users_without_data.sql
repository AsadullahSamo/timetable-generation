-- Delete users who don't have any data
-- This script identifies users with no data and deletes them

-- First, let's see which users have no data
SELECT 
    u.id,
    u.username,
    u.email,
    'NO DATA' as status
FROM users_user u
WHERE u.id NOT IN (
    SELECT DISTINCT owner_id FROM timetable_subject WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_teacher WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_classroom WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_batch WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_scheduleconfig WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_timetableentry WHERE owner_id IS NOT NULL
)
AND u.is_superuser = 0;  -- Don't delete superusers

-- To actually delete these users, uncomment the following:
/*
DELETE FROM users_user 
WHERE id NOT IN (
    SELECT DISTINCT owner_id FROM timetable_subject WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_teacher WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_classroom WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_batch WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_scheduleconfig WHERE owner_id IS NOT NULL
    UNION
    SELECT DISTINCT owner_id FROM timetable_timetableentry WHERE owner_id IS NOT NULL
)
AND is_superuser = 0;
*/ 
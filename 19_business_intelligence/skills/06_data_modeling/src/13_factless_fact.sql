-- FACTLESS FACT TABLE
CREATE TABLE FACT_STUDENT_ATTENDANCE (
    attendance_key BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL,
    student_key INTEGER NOT NULL,
    course_key INTEGER NOT NULL,
    classroom_key INTEGER NOT NULL,
    attendance_count INTEGER DEFAULT 1,
    UNIQUE (date_key, student_key, course_key)
);

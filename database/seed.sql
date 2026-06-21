-- ============================================================
-- Sample seed data for development/testing
-- ============================================================
USE club_management;

INSERT INTO user (username, email, password_hash, role) VALUES
('admin', 'admin@club.edu', 'hashed_pw_1', 'admin'),
('president1', 'president@club.edu', 'hashed_pw_2', 'president'),
('mehedi', 'mehedi@club.edu', 'hashed_pw_3', 'member');

INSERT INTO member (user_id, full_name, department, batch, roll_no) VALUES
(2, 'Club President', 'CSE', '2021', 'CSE-21-001'),
(3, 'Mehedi Ashik', 'CSE', '2021', 'CSE-21-045');

INSERT INTO event (title, description, category, event_date, venue, capacity, fee, status, is_public) VALUES
('Tech Fest 2026', 'Annual technology festival with workshops and competitions.', 'Workshop', '2026-08-15', 'Main Auditorium', 200, 100.00, 'upcoming', TRUE),
('Sports Day', 'Inter-department sports competition.', 'Sports', '2026-09-01', 'University Ground', 500, 0.00, 'upcoming', TRUE);

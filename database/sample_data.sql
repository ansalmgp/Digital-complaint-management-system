-- ShaktiDB / PostgreSQL Sample Data Seed Script

-- Truncate existing tables (clean start)
TRUNCATE TABLE Notifications, ComplaintHistory, Complaints, Admins, Students RESTART IDENTITY;

-- 1. Insert Students (Passwords are for 'student123' hashed with Werkzeug pbkdf2:sha256)
INSERT INTO Students (Name, Email, Department, Password) VALUES 
('Amit Sharma', 'amit@college.edu', 'Computer Science & Engineering', 'scrypt:32768:16:1$aIefF28h$a888c3c78df6e25be4df5f9a656644fcfd74e0d79d1fa98b67b140cdfe1fe00c01fa959a72cdb4fe5efc1c911b33390c291240c7490fe428e2194602fbd65cfb'),
('Priya Patel', 'priya@college.edu', 'Electronics & Communication', 'scrypt:32768:16:1$aIefF28h$a888c3c78df6e25be4df5f9a656644fcfd74e0d79d1fa98b67b140cdfe1fe00c01fa959a72cdb4fe5efc1c911b33390c291240c7490fe428e2194602fbd65cfb'),
('Rohan Das', 'rohan@college.edu', 'Mechanical Engineering', 'scrypt:32768:16:1$aIefF28h$a888c3c78df6e25be4df5f9a656644fcfd74e0d79d1fa98b67b140cdfe1fe00c01fa959a72cdb4fe5efc1c911b33390c291240c7490fe428e2194602fbd65cfb');

-- 2. Insert Admins (Password is for 'admin123' hashed with Werkzeug pbkdf2:sha256)
INSERT INTO Admins (Username, Password) VALUES 
('admin', 'scrypt:32768:16:1$K5b8q29z$e93240a233b8a3424d9c493c6fd8829de4bf10c73a696bfcf079c6d3dfeb8bb2563f6ee811568285514f77732a10deba19d3fbc9b7b992147321e8d66df21a22'),
('admin2', 'scrypt:32768:16:1$K5b8q29z$e93240a233b8a3424d9c493c6fd8829de4bf10c73a696bfcf079c6d3dfeb8bb2563f6ee811568285514f77732a10deba19d3fbc9b7b992147321e8d66df21a22');

-- 3. Insert Complaints
INSERT INTO Complaints (StudentID, Title, Category, Description, Status, ImagePath, CreatedDate) VALUES 
(1, 'Lab PC Keyboard & Mouse Broken', 'Academic', 'In the CSE Main Lab, computer number CS-12 has a broken keyboard keys (E, R, T not working) and the mouse optical sensor is faulty. Please replace them.', 'Pending', NULL, CURRENT_TIMESTAMP - INTERVAL '5 days'),
(2, 'Water Leakage in C-Block Hostel Room 304', 'Hostel', 'There is severe water seepage in the ceiling of hostel room 304, C-Block, coming from the bathroom above. It is causing mold and damage to books.', 'Under Review', NULL, CURRENT_TIMESTAMP - INTERVAL '3 days'),
(1, 'Damaged Book Pages in Library Reference Section', 'Library', 'The reference book "Advanced Data Structures" by Cormen (Accession No: L-4829) has several missing pages in Chapter 3. Kindly replace or bind the missing section.', 'In Progress', NULL, CURRENT_TIMESTAMP - INTERVAL '2 days'),
(3, 'Bus Route No. 4 Arriving Late Daily', 'Transport', 'College bus route no. 4 (from Sector 15) has been arriving 20-30 minutes late for the past week, making students miss their first-hour lecture.', 'Resolved', NULL, CURRENT_TIMESTAMP - INTERVAL '10 days'),
(2, 'Leaking Tap in Girls Ground Floor Restroom', 'Facilities', 'The middle tap in the washbasin of the ground floor ladies restroom (near Department office) is leaking continuously. Huge wastage of water.', 'Rejected', NULL, CURRENT_TIMESTAMP - INTERVAL '4 days');

-- 4. Insert Complaint History (To show progress timeline)
-- For Complaint 4 (Bus late): Pending -> Under Review -> In Progress -> Resolved
INSERT INTO ComplaintHistory (ComplaintID, OldStatus, NewStatus, UpdatedBy, UpdatedDate, Remarks) VALUES 
(4, 'Pending', 'Under Review', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '9 days', 'Complaint acknowledged. Checking bus trip logs for Route 4.'),
(4, 'Under Review', 'In Progress', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '8 days', 'Spoke to bus driver. Heavy traffic near junction is causing delay. Discussing alternative route.'),
(4, 'In Progress', 'Resolved', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '7 days', 'Route adjusted slightly to bypass junction. Bus now arriving on time. Verified for two days.');

-- For Complaint 3 (Library Book): Pending -> Under Review -> In Progress
INSERT INTO ComplaintHistory (ComplaintID, OldStatus, NewStatus, UpdatedBy, UpdatedDate, Remarks) VALUES 
(3, 'Pending', 'Under Review', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '2 days', 'Book details retrieved. Checking stock for duplicate copies.'),
(3, 'Under Review', 'In Progress', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '1 days', 'Sent to the binder for repair and page insertion.');

-- For Complaint 5 (Leaking Tap): Pending -> Rejected
INSERT INTO ComplaintHistory (ComplaintID, OldStatus, NewStatus, UpdatedBy, UpdatedDate, Remarks) VALUES 
(5, 'Pending', 'Rejected', 'Admin admin', CURRENT_TIMESTAMP - INTERVAL '3 days', 'Duplicate complaint. A plumber has already been assigned under ticket #12.');

-- 5. Insert Notifications
INSERT INTO Notifications (StudentID, Message, IsRead, CreatedDate) VALUES 
(1, 'Your complaint "Lab PC Keyboard & Mouse Broken" has been successfully submitted.', FALSE, CURRENT_TIMESTAMP - INTERVAL '5 days'),
(2, 'Your complaint "Water Leakage in C-Block Hostel Room 304" status has been updated to Under Review.', FALSE, CURRENT_TIMESTAMP - INTERVAL '3 days'),
(3, 'Your complaint "Bus Route No. 4 Arriving Late Daily" status has been updated to Under Review.', TRUE, CURRENT_TIMESTAMP - INTERVAL '9 days'),
(3, 'Your complaint "Bus Route No. 4 Arriving Late Daily" status has been updated to In Progress.', TRUE, CURRENT_TIMESTAMP - INTERVAL '8 days'),
(3, 'Your complaint "Bus Route No. 4 Arriving Late Daily" has been Resolved. Remarks: Route adjusted slightly to bypass junction. Bus now arriving on time.', FALSE, CURRENT_TIMESTAMP - INTERVAL '7 days');

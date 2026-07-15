-- ShaktiDB (PostgreSQL-compatible) Schema Creation Script

DROP TABLE IF EXISTS Notifications CASCADE;
DROP TABLE IF EXISTS ComplaintHistory CASCADE;
DROP TABLE IF EXISTS Complaints CASCADE;
DROP TABLE IF EXISTS Admins CASCADE;
DROP TABLE IF EXISTS Students CASCADE;

-- 1. Students Table
CREATE TABLE Students (
    StudentID SERIAL PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Department VARCHAR(100) NOT NULL,
    Password VARCHAR(255) NOT NULL
);

-- 2. Admins Table
CREATE TABLE Admins (
    AdminID SERIAL PRIMARY KEY,
    Username VARCHAR(100) UNIQUE NOT NULL,
    Password VARCHAR(255) NOT NULL
);

-- 3. Complaints Table
CREATE TABLE Complaints (
    ComplaintID SERIAL PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES Students(StudentID) ON DELETE CASCADE,
    Title VARCHAR(150) NOT NULL,
    Category VARCHAR(50) NOT NULL, -- Academic, Hostel, Facilities, Library, Transport, Others
    Description TEXT NOT NULL,
    Status VARCHAR(20) DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected')),
    ImagePath VARCHAR(255),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. ComplaintHistory Table
CREATE TABLE ComplaintHistory (
    HistoryID SERIAL PRIMARY KEY,
    ComplaintID INT NOT NULL REFERENCES Complaints(ComplaintID) ON DELETE CASCADE,
    OldStatus VARCHAR(20),
    NewStatus VARCHAR(20) NOT NULL,
    UpdatedBy VARCHAR(100) NOT NULL, -- Admin username or Student name
    UpdatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Remarks TEXT
);

-- 5. Notifications Table
CREATE TABLE Notifications (
    NotificationID SERIAL PRIMARY KEY,
    StudentID INT NOT NULL REFERENCES Students(StudentID) ON DELETE CASCADE,
    Message TEXT NOT NULL,
    IsRead BOOLEAN DEFAULT FALSE,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance optimization
CREATE INDEX idx_complaints_student ON Complaints(StudentID);
CREATE INDEX idx_complaints_status ON Complaints(Status);
CREATE INDEX idx_complaints_category ON Complaints(Category);
CREATE INDEX idx_history_complaint ON ComplaintHistory(ComplaintID);
CREATE INDEX idx_notifications_student ON Notifications(StudentID);

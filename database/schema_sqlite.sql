-- SQLite Schema Creation Script

DROP TABLE IF EXISTS Notifications;
DROP TABLE IF EXISTS ComplaintHistory;
DROP TABLE IF EXISTS Complaints;
DROP TABLE IF EXISTS Admins;
DROP TABLE IF EXISTS Students;

-- 1. Students Table
CREATE TABLE Students (
    StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT NOT NULL,
    Email TEXT UNIQUE NOT NULL,
    Department TEXT NOT NULL,
    Password TEXT NOT NULL
);

-- 2. Admins Table
CREATE TABLE Admins (
    AdminID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
);

-- 3. Complaints Table
CREATE TABLE Complaints (
    ComplaintID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER NOT NULL,
    Title TEXT NOT NULL,
    Category TEXT NOT NULL,
    Description TEXT NOT NULL,
    Status TEXT DEFAULT 'Pending' CHECK (Status IN ('Pending', 'Under Review', 'In Progress', 'Resolved', 'Rejected')),
    ImagePath TEXT,
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE
);

-- 4. ComplaintHistory Table
CREATE TABLE ComplaintHistory (
    HistoryID INTEGER PRIMARY KEY AUTOINCREMENT,
    ComplaintID INTEGER NOT NULL,
    OldStatus TEXT,
    NewStatus TEXT NOT NULL,
    UpdatedBy TEXT NOT NULL,
    UpdatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    Remarks TEXT,
    FOREIGN KEY(ComplaintID) REFERENCES Complaints(ComplaintID) ON DELETE CASCADE
);

-- 5. Notifications Table
CREATE TABLE Notifications (
    NotificationID INTEGER PRIMARY KEY AUTOINCREMENT,
    StudentID INTEGER NOT NULL,
    Message TEXT NOT NULL,
    IsRead INTEGER DEFAULT 0 CHECK (IsRead IN (0, 1)),
    CreatedDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(StudentID) REFERENCES Students(StudentID) ON DELETE CASCADE
);

-- Create indexes for performance optimization
CREATE INDEX idx_complaints_student ON Complaints(StudentID);
CREATE INDEX idx_complaints_status ON Complaints(Status);
CREATE INDEX idx_complaints_category ON Complaints(Category);
CREATE INDEX idx_history_complaint ON ComplaintHistory(ComplaintID);
CREATE INDEX idx_notifications_student ON Notifications(StudentID);

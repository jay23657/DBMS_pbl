CREATE DATABASE IF NOT EXISTS police_db;
USE police_db;

-- Persons involved (Suspects, Victims, Witnesses)
CREATE TABLE Persons (
    person_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    dob DATE,
    address VARCHAR(255),
    contact_number VARCHAR(15),
    role ENUM('suspect', 'victim', 'witness', 'other') DEFAULT 'other'
);

-- Police Officers
CREATE TABLE Officers (
    officer_id INT AUTO_INCREMENT PRIMARY KEY,
    badge_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    rank VARCHAR(50),
    contact_number VARCHAR(15)
);

-- Complaints / Cases
CREATE TABLE Complaints (
    complaint_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    incident_date DATE NOT NULL,
    filed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'under_investigation', 'closed', 'referred_to_court') DEFAULT 'pending',
    closure_details TEXT,
    -- Important business rule: closed cases must have closure details
    CHECK (status != 'closed' OR closure_details IS NOT NULL)
);

-- Track changes in complaint status
CREATE TABLE StatusHistories (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    status ENUM('pending', 'under_investigation', 'closed', 'referred_to_court') NOT NULL,
    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE
);

-- Officers assigned to complaints
CREATE TABLE Assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    officer_id INT,
    assignment_date DATE,
    role VARCHAR(50),
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES Officers(officer_id) ON DELETE CASCADE
);

-- Activity logs for investigations
CREATE TABLE InvestigationActivities (
    activity_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    officer_id INT,
    activity_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES Officers(officer_id) ON DELETE CASCADE
);

-- Evidence tracking
CREATE TABLE EvidenceItems (
    evidence_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    description TEXT NOT NULL,
    collection_date DATE NOT NULL,
    collected_by INT,
    current_location VARCHAR(100),
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (collected_by) REFERENCES Officers(officer_id) ON DELETE SET NULL
);

-- Custody logs for suspects
CREATE TABLE CustodyLogs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    person_id INT,
    officer_id INT,
    check_in_time DATETIME NOT NULL,
    check_out_time DATETIME,
    location VARCHAR(100) NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Persons(person_id) ON DELETE CASCADE,
    FOREIGN KEY (officer_id) REFERENCES Officers(officer_id) ON DELETE SET NULL,
    -- Check for complete custody transfer / no overlapping custody (simplified to check valid times)
    CHECK (check_out_time IS NULL OR check_out_time > check_in_time)
);

-- Witness statements
CREATE TABLE Witnesses (
    witness_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    person_id INT,
    statement TEXT,
    statement_date DATE,
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Persons(person_id) ON DELETE CASCADE
);

-- Court references for referred cases
CREATE TABLE CourtReferences (
    court_ref_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    court_name VARCHAR(100) NOT NULL,
    hearing_date DATE,
    case_number VARCHAR(50),
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE
);

-- Charges filed against persons for specific complaints
CREATE TABLE Charges (
    charge_id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT,
    person_id INT,
    description TEXT NOT NULL,
    FOREIGN KEY (complaint_id) REFERENCES Complaints(complaint_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Persons(person_id) ON DELETE CASCADE
);

-- Insert Sample Data
INSERT INTO Officers (badge_number, first_name, last_name, rank, contact_number) VALUES
('P1001', 'John', 'Doe', 'Inspector', '1234567890'),
('P1002', 'Jane', 'Smith', 'Sergeant', '0987654321'),
('P1003', 'Mike', 'Johnson', 'Detective', '1112223333');

INSERT INTO Persons (first_name, last_name, dob, address, contact_number, role) VALUES
('Alice', 'Brown', '1990-05-15', '123 Elm St', '4445556666', 'victim'),
('Bob', 'White', '1985-08-20', '456 Oak St', '7778889999', 'suspect'),
('Charlie', 'Green', '1992-11-10', '789 Pine St', '2223334444', 'witness');

INSERT INTO Complaints (title, description, incident_date, status) VALUES
('Robbery at Elm St', 'A convenience store was robbed at gunpoint.', '2023-10-01', 'under_investigation'),
('Vandalism in Park', 'Graffiti painted on park statues.', '2023-10-05', 'pending');

INSERT INTO Assignments (complaint_id, officer_id, assignment_date, role) VALUES
(1, 1, '2023-10-02', 'Lead Investigator'),
(1, 3, '2023-10-02', 'Assisting Detective'),
(2, 2, '2023-10-06', 'Lead Investigator');

INSERT INTO EvidenceItems (complaint_id, description, collection_date, collected_by, current_location) VALUES
(1, 'Security Camera Footage', '2023-10-02', 1, 'Evidence Room A'),
(1, 'Abandoned mask', '2023-10-02', 3, 'Evidence Room B');

INSERT INTO Witnesses (complaint_id, person_id, statement, statement_date) VALUES
(1, 3, 'I saw a man running away with a black bag.', '2023-10-03');

INSERT INTO CustodyLogs (person_id, officer_id, check_in_time, location) VALUES
(2, 1, '2023-10-04 14:00:00', 'Holding Cell 1');

INSERT INTO StatusHistories (complaint_id, status, remarks) VALUES
(1, 'pending', 'Case filed'),
(1, 'under_investigation', 'Officers assigned and evidence collected');

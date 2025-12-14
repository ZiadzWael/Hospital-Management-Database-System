
CREATE DATABASE hospital_management_system1;
USE hospital_management_system1;

-- 1. PATIENT AND SUBTYPES
CREATE TABLE Patient (
    Patient_ID INT PRIMARY KEY AUTO_INCREMENT,
    F_name VARCHAR(50),
    M_name VARCHAR(50),
    L_name VARCHAR(50),
    Phone_no VARCHAR(50),
    Gender VARCHAR(10),
    PatientType ENUM('InPatient', 'OutPatient', 'EmergencyPatient') NOT NULL,
    DOB DATE,
    Blood_type VARCHAR(3),
    City VARCHAR(50),
    State VARCHAR(50),
    Gov VARCHAR(50)
);

CREATE TABLE InPatient (
    Patient_ID INT PRIMARY KEY,
    Room_no INT,
    Admission_date DATE,
    Discharge_date DATE,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE OutPatient (
    Patient_ID INT PRIMARY KEY,
    Appointment_date DATETIME,
    ConsultType VARCHAR(50),
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE EmergencyPatient (
    Patient_ID INT PRIMARY KEY,
    Emergency_level VARCHAR(50),
    Arrival_time TIME,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 2. STAFF AND SUBTYPES
CREATE TABLE Staff (
    Staff_ID INT PRIMARY KEY AUTO_INCREMENT,
    F_name VARCHAR(50),
    M_name VARCHAR(50),
    L_name VARCHAR(50),
    StaffType ENUM('Doctor', 'Nurse', 'Technician') NOT NULL,
    Phone_no VARCHAR(15),
    Department VARCHAR(100)
);

CREATE TABLE Doctor (
    Staff_ID INT PRIMARY KEY,
    Specialty VARCHAR(100),
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Nurse (
    Staff_ID INT PRIMARY KEY,
    Shift_time VARCHAR(50),
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 3. APPOINTMENT AND TREATMENT
CREATE TABLE Appointments (
    Appointment_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT,
    Staff_ID INT,
    AppointmentDate DATETIME,
    Status ENUM('Scheduled', 'Completed', 'Cancelled') DEFAULT 'Scheduled',
    Fee DECIMAL(10,2),
    Cause TEXT,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Treatments (
    TreatmentID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT,
    DoctorID INT,
    Diagnosis TEXT,
    Treatment TEXT,
    StartDate DATE,
    EndDate DATE,
    Amount DECIMAL(10,2),
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (DoctorID) REFERENCES Staff(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

-- 4. ADMISSION
CREATE TABLE Admission (
    Admission_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT,
    Admission_date DATE,
    Discharge_date DATE,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID)
);

-- 5. ROOM AND ROOM BOOKING
CREATE TABLE Room (
    Room_no INT PRIMARY KEY AUTO_INCREMENT,
    RoomType ENUM('Regular', 'ICU', 'Operation') NOT NULL,
    Status ENUM('Available', 'Occupied', 'Maintenance') DEFAULT 'Available',
    Floor INT,
    PricePerDay DECIMAL(10,2)
);

CREATE TABLE Regular (
    Room_no INT PRIMARY KEY,
    Bed_count INT,
    Room_size ENUM('Single', 'Double', 'Triple') NOT NULL,
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE ICU (
    Room_no INT PRIMARY KEY,
    ICU_level VARCHAR(10),
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Operation (
    Room_no INT PRIMARY KEY,
    SurgicalSpeciality TEXT,
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Room_Booking (
    Booking_ID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT,
    Room_no INT,
    From_date DATE,
    To_date DATE,
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE RoomAllocations (
    AllocationID INT PRIMARY KEY AUTO_INCREMENT,
    Patient_ID INT,
    Room_no INT,
    Staff_ID INT,
    Status ENUM('Active', 'Discharged') DEFAULT 'Active',
    FOREIGN KEY (Patient_ID) REFERENCES Patient(Patient_ID) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Room_no) REFERENCES Room(Room_no) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID) ON DELETE CASCADE ON UPDATE CASCADE
);

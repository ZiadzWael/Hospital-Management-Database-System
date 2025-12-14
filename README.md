# Hospital Management System

## Overview
A comprehensive hospital management system with MySQL database backend and Tkinter GUI frontend. Features patient management, staff records, appointments, room bookings, treatments, and reporting.

## Features
- **Patient Management**: Add/update/delete patients (InPatient, OutPatient, EmergencyPatient)
- **Staff Management**: Doctor, Nurse, Technician management
- **Appointment System**: Schedule, update, cancel appointments
- **Room Management**: Room booking with Regular, ICU, Operation rooms
- **Treatment Records**: Track patient treatments and diagnoses
- **Reporting System**: Generate CSV/PDF reports for all entities
- **SQL Query Interface**: Execute custom queries and save as views

## Database Schema
- **Patient** (with subtypes: InPatient, OutPatient, EmergencyPatient)
- **Staff** (with subtypes: Doctor, Nurse, Technician)
- **Appointments**, **Treatments**, **Admissions**
- **Rooms** (Regular, ICU, Operation), **Room_Booking**
- **RoomAllocations**

## Setup Instructions

### 1. Database Setup
```sql
-- Run the SQL file to create database and tables
mysql -u root -p < hospital_management_system1.sql

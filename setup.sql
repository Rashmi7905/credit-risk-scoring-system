-- Credit Risk Scoring System - Database Setup
-- Run these queries in order in MySQL

CREATE DATABASE IF NOT EXISTS credit_risk_db;
USE credit_risk_db;

-- Table 1: Applicants
CREATE TABLE applicants (
    applicant_id INT AUTO_INCREMENT PRIMARY KEY,
    age INT,
    monthly_income DECIMAL(12,2),
    years_employed DECIMAL(4,1),
    created_at DATE
);

-- Table 2: Loans
CREATE TABLE loans (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT,
    loan_amount DECIMAL(12,2),
    loan_purpose VARCHAR(50),
    interest_rate DECIMAL(5,2),
    credit_score INT,
    debt_to_income_ratio DECIMAL(5,3),
    status ENUM('Approved','Rejected','Under Review'),
    application_date DATE,
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);

-- Table 3: Credit History
CREATE TABLE credit_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT,
    credit_utilization DECIMAL(5,2),
    on_time_payments INT,
    late_payments INT,
    defaults_count INT,
    bureau VARCHAR(30),
    FOREIGN KEY (applicant_id) REFERENCES applicants(applicant_id)
);

-- Table 4: Risk Assessments
CREATE TABLE risk_assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT,
    income_score DECIMAL(6,2),
    credit_score_factor DECIMAL(6,2),
    dti_score DECIMAL(6,2),
    final_risk_score DECIMAL(6,2),
    recommendation ENUM('Approve','Review','Reject'),
    assessment_date DATE,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);

-- Staging table for CSV import
CREATE TABLE loan_staging (
    person_age INT,
    person_income DECIMAL(12,2),
    person_home_ownership VARCHAR(20),
    person_emp_length DECIMAL(4,1),
    loan_intent VARCHAR(50),
    loan_grade VARCHAR(5),
    loan_amnt DECIMAL(12,2),
    loan_int_rate DECIMAL(5,2),
    loan_status INT,
    loan_percent_income DECIMAL(5,3),
    cb_person_default_on_file VARCHAR(5),
    cb_person_cred_hist_length INT
);

-- After importing CSV into loan_staging, run these:
ALTER TABLE loan_staging ADD COLUMN row_num INT AUTO_INCREMENT PRIMARY KEY;

INSERT INTO applicants (age, monthly_income, years_employed, created_at)
SELECT person_age, person_income, person_emp_length, CURDATE()
FROM loan_staging ORDER BY row_num;

INSERT INTO loans (applicant_id, loan_amount, loan_purpose, interest_rate,
                   credit_score, debt_to_income_ratio, status, application_date)
SELECT s.row_num, s.loan_amnt, s.loan_intent, COALESCE(s.loan_int_rate, 10.0),
    CASE s.loan_grade
        WHEN 'A' THEN FLOOR(750 + RAND() * 100)
        WHEN 'B' THEN FLOOR(670 + RAND() * 80)
        WHEN 'C' THEN FLOOR(600 + RAND() * 70)
        WHEN 'D' THEN FLOOR(540 + RAND() * 60)
        WHEN 'E' THEN FLOOR(480 + RAND() * 60)
        WHEN 'F' THEN FLOOR(400 + RAND() * 80)
        ELSE 500
    END,
    s.loan_percent_income,
    CASE WHEN s.loan_status = 0 THEN 'Approved' ELSE 'Rejected' END,
    CURDATE()
FROM loan_staging s ORDER BY s.row_num;

INSERT INTO credit_history (applicant_id, credit_utilization, on_time_payments,
                             late_payments, defaults_count, bureau)
SELECT s.row_num,
    ROUND(s.loan_percent_income * 100, 2),
    (s.cb_person_cred_hist_length * 12) -
        CASE s.cb_person_default_on_file WHEN 'Y' THEN FLOOR(RAND()*6) ELSE 0 END,
    CASE s.cb_person_default_on_file WHEN 'Y' THEN FLOOR(RAND()*6) ELSE 0 END,
    CASE s.cb_person_default_on_file WHEN 'Y' THEN 1 ELSE 0 END,
    ELT(1 + FLOOR(RAND() * 3), 'CIBIL', 'Equifax', 'Experian')
FROM loan_staging s ORDER BY s.row_num;

INSERT INTO risk_assessments (loan_id, income_score, credit_score_factor,
                               dti_score, final_risk_score, recommendation, assessment_date)
SELECT l.loan_id,
    LEAST(100, (a.monthly_income / 250000) * 100),
    ((l.credit_score - 300) / 6.0),
    GREATEST(0, 100 - (l.debt_to_income_ratio * 133)),
    ROUND(
        LEAST(100, (a.monthly_income / 250000) * 100) * 0.25 +
        ((l.credit_score - 300) / 6.0) * 0.35 +
        GREATEST(0, 100 - (l.debt_to_income_ratio * 133)) * 0.40
    , 2),
    CASE
        WHEN ROUND(
            LEAST(100,(a.monthly_income/250000)*100)*0.25 +
            ((l.credit_score-300)/6.0)*0.35 +
            GREATEST(0,100-(l.debt_to_income_ratio*133))*0.40
        ,2) >= 65 THEN 'Approve'
        WHEN ROUND(
            LEAST(100,(a.monthly_income/250000)*100)*0.25 +
            ((l.credit_score-300)/6.0)*0.35 +
            GREATEST(0,100-(l.debt_to_income_ratio*133))*0.40
        ,2) >= 45 THEN 'Review'
        ELSE 'Reject'
    END,
    CURDATE()
FROM loans l
JOIN applicants a ON l.applicant_id = a.applicant_id;

show databases;
create database Loan_Approval;
use Loan_Approval;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    account_no VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    loan_amount FLOAT,
    loan_term INT,
    application_status ENUM('Submitted', 'Under Review', 'Approved', 'Rejected') DEFAULT 'Submitted',
    prediction_result BOOLEAN,
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
SHOW TABLES;
DESCRIBE user;
INSERT INTO user (account_no, password_hash) VALUES ('user001', 'scrypt:32768:8:1$1a2b3c4d$abc123def456ghi789jkl');
INSERT INTO user (account_no, password_hash) VALUES ('user002', 'scrypt:32768:8:1$1a2b3c4d$def456ghi789jkl012mno');
INSERT INTO user (account_no, password_hash) VALUES ('user003', 'scrypt:32768:8:1$1a2b3c4d$ghi789jkl012mno345pqr');
INSERT INTO user (account_no, password_hash) VALUES ('user004', 'scrypt:32768:8:1$1a2b3c4d$jkl012mno345pqr678stu');
INSERT INTO user (account_no, password_hash) VALUES ('user005', 'scrypt:32768:8:1$1a2b3c4d$mno345pqr678stu901vwx');
INSERT INTO user (account_no, password_hash) VALUES ('user006', 'scrypt:32768:8:1$1a2b3c4d$pqr678stu901vwx234yza');
INSERT INTO user (account_no, password_hash) VALUES ('user007', 'scrypt:32768:8:1$1a2b3c4d$stu901vwx234yza567bcd');
INSERT INTO user (account_no, password_hash) VALUES ('user008', 'scrypt:32768:8:1$1a2b3c4d$vwx234yza567bcd890efg');
INSERT INTO user (account_no, password_hash) VALUES ('user009', 'scrypt:32768:8:1$1a2b3c4d$yzab890efg1234567890');
INSERT INTO user (account_no, password_hash) VALUES ('user010', 'scrypt:32768:8:1$1a2b3c4d$890efg1234567890abcd');



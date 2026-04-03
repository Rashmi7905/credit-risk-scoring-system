# Credit Risk Scoring & Loan Approval System

A DBMS project analyzing 32,581 real loan applications to assess credit risk.

## Tech Stack
- Database: MySQL
- Language: Python 3
- GUI: Tkinter (desktop application)
- Dataset: Credit Risk Dataset (Kaggle - 32,581 rows)

## Database Schema
4 normalized tables:
- applicants — personal and financial info
- loans — loan application details
- credit_history — credit bureau data
- risk_assessments — computed risk scores

## Risk Scoring Formula
Final Score = (Income Score x 0.25) + (Credit Factor x 0.35) + (DTI Score x 0.40)
- Score >= 65 → Approve
- Score 45 to 64 → Review
- Score < 45 → Reject

## How to Run
1. Download dataset from Kaggle: search Credit Risk Dataset
2. Set up MySQL database using setup.sql
3. Install dependency: pip install mysql-connector-python
4. Add your MySQL password in loan_gui.py
5. Run: python loan_gui.py

## Features
- Dashboard showing live stats from MySQL database
- Searchable loan applications table
- Real time risk calculator

## Future Plans
- Add Machine Learning model (Random Forest)
- Train on real loan outcomes for better predictions

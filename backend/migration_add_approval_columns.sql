-- Migration script to add approval columns to examens table
-- Run this if you have an existing database without the approval columns

ALTER TABLE examens 
ADD COLUMN IF NOT EXISTS dept_head_approved INT DEFAULT 0,
ADD COLUMN IF NOT EXISTS vice_dean_approved INT DEFAULT 0;

-- Update existing exams to be pending approval
UPDATE examens 
SET dept_head_approved = 0, vice_dean_approved = 0 
WHERE dept_head_approved IS NULL OR vice_dean_approved IS NULL;

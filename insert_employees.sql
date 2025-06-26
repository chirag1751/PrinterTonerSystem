-- Drop table if it exists (optional but useful for dev)
DROP TABLE IF EXISTS employee;

-- Create the employee table
CREATE TABLE employee (
  id SERIAL PRIMARY KEY,
  employee_name VARCHAR(100)
);

-- Insert dummy employee records
INSERT INTO employee (employee_name) VALUES 
('John Doe'),
('Jane Smith'),
('David Johnson'),
('Emma Williams'),
('Michael Brown'),
('Sophia Miller'),
('Daniel Wilson'),
('Olivia Anderson');

DROP TABLE IF EXISTS employee;

CREATE TABLE employee (
  id SERIAL PRIMARY KEY,
  employee_name VARCHAR(100)
);

INSERT INTO employee (employee_name) VALUES 
('John Doe'),
('Jane Smith'),
('David Johnson'),
('Emma Williams'),
('Michael Brown'),
('Sophia Miller'),
('Daniel Wilson'),
('Olivia Anderson');

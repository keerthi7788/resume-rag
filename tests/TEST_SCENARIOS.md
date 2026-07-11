# Test Scenarios

## Test Case 1 – Extract Requirements

Input:

Senior Backend Engineer

Required Skills:
Python
Docker
AWS

Experience:
5+ years

Expected Result:

- Python extracted
- Docker extracted
- AWS extracted
- Experience 5 years extracted

---

## Test Case 2 – Compare Candidates

Input:

[
"backend_engineer_sneha_iyer_10y.txt",
"devops_engineer_sanjay_kulkarni_3y.txt"
]

Expected Result:

Candidate comparison returned with:

- Skills
- Experience
- Education

---

## Test Case 3 – Generate Interview Questions

Input:

backend_engineer_sneha_iyer_10y.txt

Expected Result:

Interview questions generated from candidate skills.

---

## Test Case 4 – Watch Directory

Input:

watch_directory("resumes")

Expected Result:

Server begins monitoring the folder.

---

## Test Case 5 – Batch Process

Input:

batch_process([
"resume1.pdf",
"resume2.pdf"
])

Expected Result:

Returns processed status for every file.
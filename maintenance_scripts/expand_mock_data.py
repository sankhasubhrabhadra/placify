import json

# More companies for the chart
company_hiring = {
    "Amazon": 150, 
    "Google": 120, 
    "Microsoft": 100, 
    "Fractal Analytics": 80, 
    "Mu Sigma": 75,
    "TCS": 65,
    "Accenture": 60,
    "Infosys": 55,
    "IBM": 50,
    "Capgemini": 45,
    "Wipro": 40,
    "Tiger Analytics": 35,
    "Deloitte": 30
}

with open('frontend/data/company_hiring.json', 'w') as f:
    json.dump(company_hiring, f)

# More roles for the table
salary_by_role = [
    {"company_name": "Amazon", "job_title": "Data Scientist", "min_experience": "3-5 yrs", "min_salary": 15.0, "avg_salary": 22.0, "max_salary": 35.0, "num_of_jobs": 25},
    {"company_name": "Google", "job_title": "Machine Learning Engineer", "min_experience": "2-4 yrs", "min_salary": 18.0, "avg_salary": 26.0, "max_salary": 40.0, "num_of_jobs": 15},
    {"company_name": "Microsoft", "job_title": "Data Analyst", "min_experience": "1-3 yrs", "min_salary": 8.0, "avg_salary": 12.0, "max_salary": 18.0, "num_of_jobs": 30},
    {"company_name": "Fractal Analytics", "job_title": "Senior Data Scientist", "min_experience": "5-8 yrs", "min_salary": 20.0, "avg_salary": 28.0, "max_salary": 45.0, "num_of_jobs": 12},
    {"company_name": "Mu Sigma", "job_title": "Decision Scientist", "min_experience": "0-2 yrs", "min_salary": 6.0, "avg_salary": 8.5, "max_salary": 12.0, "num_of_jobs": 50},
    {"company_name": "TCS", "job_title": "Data Engineer", "min_experience": "3-6 yrs", "min_salary": 10.0, "avg_salary": 14.0, "max_salary": 22.0, "num_of_jobs": 40},
    {"company_name": "Accenture", "job_title": "AI Consultant", "min_experience": "4-7 yrs", "min_salary": 16.0, "avg_salary": 24.0, "max_salary": 38.0, "num_of_jobs": 20},
    {"company_name": "Infosys", "job_title": "Business Analyst", "min_experience": "2-5 yrs", "min_salary": 7.0, "avg_salary": 10.0, "max_salary": 15.0, "num_of_jobs": 35},
    {"company_name": "IBM", "job_title": "AI Research Scientist", "min_experience": "5-10 yrs", "min_salary": 25.0, "avg_salary": 35.0, "max_salary": 55.0, "num_of_jobs": 8},
    {"company_name": "Capgemini", "job_title": "Data Architect", "min_experience": "8-12 yrs", "min_salary": 28.0, "avg_salary": 40.0, "max_salary": 60.0, "num_of_jobs": 5},
    {"company_name": "Tiger Analytics", "job_title": "Data Scientist", "min_experience": "2-5 yrs", "min_salary": 12.0, "avg_salary": 16.5, "max_salary": 25.0, "num_of_jobs": 18},
    {"company_name": "Deloitte", "job_title": "Analytics Manager", "min_experience": "7-10 yrs", "min_salary": 25.0, "avg_salary": 32.0, "max_salary": 48.0, "num_of_jobs": 10}
]

with open('frontend/data/salary_by_role.json', 'w') as f:
    json.dump(salary_by_role, f)

print("Mock data expanded.")

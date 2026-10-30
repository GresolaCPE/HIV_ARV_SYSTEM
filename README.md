# HIV Antiretroviral (ARV) Allocation and Management System

## Object Oriented Programming 2 Final Project
**Course Objective:**
By the end of this course, students will be able to design and implement GUI-based Python applications that solve real-world problems using object-oriented design, logical programming principles, and clean, maintainable code structures. This course aims to contribute towards the attainment of SDG 9.

---

## Key Features
* **Security Authentication and Management**
* **Patient Record Management**
* **Inventory & Stock Control**
* **Allocation & Distribution**
* **Transactiona; Ledger**
* **Security Audit Logging** 
* **GUI Dashboard**

---

## Repository Contents:
```text
HIV_ARV_SYSTEM/
├── backend/
│   ├── __init__.py
│   ├── allocation_service.py
│   ├── auth_service.py
│   ├── base_service.py
│   ├── inventory_service.py
│   ├── patient_service.py
│   ├── security_service.py
│   ├── storage.py
│   └── transaction_service.py           
├── data/
│   ├── allocations.json
│   ├── authorized_staff.json
│   ├── inventory_data.json            
│   ├── login_audit.json
│   ├── patients.json
│   ├── patient_audit.json
│   ├── stock_transactions.json
│   └── users.json
├── allocation_page.py
├── gui.py
├── mail_followup.py
├── main.py
├── schedule_page.py
├── schedule_service.py
├── style.qss
├── system_report.pdf
└── README.md
```

---

## Project Members

| Role | Name |
| :---: | :---: |
| **Lead Full Stack Developer** | Gresola, Aryanna Keith G. |
| **Documentation and Full Stack Developer** | Nacion, Daniela Joy N. |
| **Backend Developer** | Ramirez, Angel Mae C. |
| **Frontend Developer** | Salcedo, Lance Cristopher S. |
| **Full Stack Developer** | Santos, Paterno Miguel R. |

---

## Account registration and printable reports
<p align="justify">
* Open the app and choose **Register** to create a local staff account. Enter a unique Staff ID, full name, username (at least 3 characters, no spaces), and password (at least 8 characters). If the Staff ID is already present in `data/authorized_staff.json`, the listed name and unused status are still checked. Otherwise, self-registration is enabled for this classroom/demo build.
* From **Report**, select a document type and enter a Patient ID where relevant.
* **Patient Record History** lets you select one saved version/audit entry or **All records**.
* **Allocation History** lets you retrieve one allocation or all allocations (optionally filtered by Patient ID).
* **Medicine Stock Movement** summarizes total stock received and issued and lists the underlying stock transaction records.
* Use **EXPORT PDF / PRINT** for a printable PDF, or **SAVE DOCUMENT (HTML)** for a document that can be opened and edited in a browser or word processor.
</p>

The system stores patient and treatment data locally in JSON files. Use only fictional/test data during demonstrations and keep generated reports confidential.

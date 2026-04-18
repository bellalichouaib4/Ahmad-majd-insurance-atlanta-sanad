# Insurance Management System
## Atlanta Sanad — Bureau Direct (BD)

---

### 👨‍💻 Development

**Adapted & Developed by:** [Bellali Chouaib](https://github.com/bellalichouaib4)

This project is being actively developed and adapted for **Atlanta Sanad** insurance agency (Bureau Direct model), covering the full workflow between the agency, its clients, and the insurance company.

> 🙏 **Original base project** by [Sumit Kumar](https://github.com/sumitkumar1503) — [insurancemanagement](https://github.com/sumitkumar1503/insurancemanagement).  
> His foundational work saved significant time and his effort is fully acknowledged here. This adaptation builds on top of it with major modifications for a real production use case. Credit where it's due.

---

## 📋 Project Scope (Bureau Direct — Atlanta Sanad)

This system manages the full production cycle of a Bureau Direct insurance agency:

- **Agency ↔ Client** — policy issuance, premium collection, payment tracking (Reste, Mode de paiement)
- **Agency ↔ Company** — production reporting, remittance of net premiums, commission management
- **Multi-user LAN access** — Admin + multiple workers on the same network
- **Vehicle insurance focus** — Tourisme, 2 Roues, and other categories

---

## ✅ Features (Original Base)

### Admin
- Admin account via `createsuperuser` command
- View/update/delete customers
- Add/update/delete policy categories (Life, Health, Motor, Travel)
- Add/update/delete policies
- View policy holder statistics (total / approved / disapproved)
- Approve customer-applied policies
- Answer customer questions

### Customer
- Create account (no admin approval required)
- Browse all available policies
- Apply for a policy (goes to pending → admin approves)
- Check policy application status under history
- Send questions to admin

---

## 🚀 How to Run

- Install **Python 3.7.6+** (tick "Add to Path" during install)
- Open terminal and run:

```bash
python -m pip install -r requirements.txt
```

- Move to the project folder, then:

```bash
py manage.py makemigrations
py manage.py migrate
py manage.py runserver
```

- Open your browser at:

```
http://127.0.0.1:8000/
```

### For LAN (Multi-machine in the agency)

```bash
py manage.py runserver 0.0.0.0:8000
```

Other machines on the same network access it via:
```
http://[SERVER_LOCAL_IP]:8000
```

---

## ⚙️ Email Setup (Contact Page)

In `settings.py`:

```python
EMAIL_HOST_USER = 'youremail@gmail.com'
EMAIL_HOST_PASSWORD = 'your email password'
EMAIL_RECEIVING_USER = 'youremail@gmail.com'
```

---

## 📸 Screenshots

### Homepage
![homepage](https://github.com/sumitkumar1503/insurancemanagement/blob/master/static/screenshots/homepage.png?raw=true)

### Admin Dashboard
![dashboard](https://github.com/sumitkumar1503/insurancemanagement/blob/master/static/screenshots/dashboard.png?raw=true)

### Policy Record
![policy record](https://github.com/sumitkumar1503/insurancemanagement/blob/master/static/screenshots/policyrecord.png?raw=true)

### Policy
![policy](https://github.com/sumitkumar1503/insurancemanagement/blob/master/static/screenshots/policy.png?raw=true)

---

## ⚠️ Disclaimer

The original base project was developed for demo purposes. This fork is being adapted into a production-grade system for real agency use. Modifications are ongoing.

---

## 📬 Contact

- Developer: [Bellali Chouaib on GitHub](https://github.com/bellalichouaib4)
- Original author: [Sumit Kumar on Facebook](https://fb.com/sumit.luv) | [LazyCoder on YouTube](https://youtube.com/lazycoderonline)

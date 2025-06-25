# 🧠 Stroke Prediction System using Machine Learning

A full-stack intelligent stroke prediction web application built with a Flask backend and integrated machine learning model. The project predicts the probability of a person experiencing a stroke based on health parameters, using logistic regression trained on a real-world dataset. It is accessible through a chatbot-style interface, designed for ease of use and improved engagement.

---

## 🎯 Motivation

Stroke remains a leading cause of death and disability worldwide. According to the World Health Organization (WHO), approximately 15 million people suffer strokes annually, of which 5 million die and another 5 million are left permanently disabled. In India alone, the incidence of stroke is estimated at 119 to 145 per 100,000 people every year.

Despite these alarming statistics, awareness and early intervention remain low due to barriers like cost, limited accessibility to preventive care, and lack of personalized tools.

This project was born out of a need to:

* 📉 **Lower the barrier to early stroke risk detection**
* 🌐 **Provide a web-accessible, privacy-conscious system**
* 🤝 **Help individuals make informed health decisions early on**

We aimed to provide an intuitive tool powered by machine learning and accessible via any browser, integrating medical data science with real-time interactivity.

---

## 🔍 Features

* 🔐 **User, Doctor, and Admin Roles** with role-specific interfaces and secure authentication
* 💬 **Chatbot-style interface** to guide users through data collection
* ⚖️ **BMI Calculation** integrated into risk prediction
* 📊 **Dynamic Stroke Risk Gauge Meter** on the final report
* 📄 **Doctor registration with photo, Aadhar, and degree uploads**
* 🏥 **Interactive report** displaying nearby doctors and hospitals
* 🔐 **Forgot and Reset Password** flow via email (tokenized)
* 🧠 **Machine Learning Model** trained on real-world medical data
* 💾 **MySQL + SQLAlchemy** backend database

---

## 📊 Dataset

**Kaggle - Stroke Prediction Dataset**
Source: [https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

* 🧬 \~5,000 records
* 🧑‍⚕️ Includes features like age, BMI, glucose, hypertension, smoking, gender, and work type
* ✅ Preprocessed with SMOTE balancing, standardization, one-hot encoding

> ⚠️ *Disclaimer: This tool is built for educational and demonstrative purposes. It is not approved for clinical use.*

---

## ⚙️ Technologies Used

| Category             | Stack                                       |
| -------------------- | ------------------------------------------- |
| **Backend**          | Flask, SQLAlchemy, Flask-Mail, Flask-CORS   |
| **Machine Learning** | Scikit-learn, pandas, numpy, joblib         |
| **Frontend**         | HTML5, CSS3, JavaScript (Vanilla), Chart.js |
| **Database**         | MySQL (development), SQLite (fallback/test) |
| **Other Tools**      | Dotenv, UUID, Werkzeug, PlantUML            |

---

## 🧰 Setup and Installation

### Prerequisites

* Python 3.8+
* MySQL Server (or use SQLite for quick testing)

### 🛠 Installation

```bash
# 1. Clone the repository
$ git clone https://github.com/yourusername/stroke-prediction-system.git
$ cd stroke-prediction-system

# 2. Create a virtual environment
$ python -m venv venv
$ source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
$ pip install -r requirements.txt

# 4. Add environment variables in a `.env` file
```

**.env**:

```env
SECRET_KEY=your_secret_key
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_email_password
DATABASE_URL=mysql+pymysql://user:password@localhost/dbname
CSV_PATH=data/stroke_data.csv
UPLOAD_FOLDER=uploads
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf
```

```bash
# 5. Run the application
$ python run.py
```

Access at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🗂 Folder Structure

```
├── app
│   ├── routes/           # Flask Blueprints: prediction, auth, doctor
│   ├── templates/        # Jinja2 HTML templates
│   ├── static/           # CSS, JS, images
│   ├── models.py         # SQLAlchemy DB models
│   ├── utils/            # File, email, and ML utilities
├── models/               # Trained ML model, scaler, features
├── uploads/              # Uploaded doctor files (degree, aadhar, photo)
├── data/                 # CSV dataset (local copy)
├── run.py                # Entry point to the app
├── requirements.txt
├── .env
```

---

## 📋 Observations and Limitations

While developing the system, we noted the following challenges:

* ⚠️ The dataset, while publicly available, has class imbalance — handled using SMOTE, though more clinical-grade data would improve reliability.
* 📶 Prediction performance is only as good as the data quality. Real clinical environments may have more complex variables.
* 🔄 The absence of real-time doctor scheduling or patient record history limits continuity of care but was out of scope for our timeline.
* ⚡ We’ve optimized user flow and performance, but large-scale load testing (concurrent users, deployment scaling) remains to be explored.

---

## 🧠 Model Training (Overview)

* Null value handling (mean/mode)
* One-hot encoding of categorical fields
* Feature scaling using StandardScaler
* Class imbalance resolved using **SMOTE**
* Hyperparameter tuning using **GridSearchCV**
* Logistic Regression with adjusted threshold (0.55)
* Accuracy \~78–81% (F1-optimized)

---

## 📘 License

This project is intended for educational and academic purposes only.

---

## 🔗 References

* Soriano, Federico. "Stroke Prediction Dataset". Kaggle, 2020.
  [https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)
* scikit-learn documentation: [https://scikit-learn.org](https://scikit-learn.org)
* Flask documentation: [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
* Flask-Mail: [https://pythonhosted.org/Flask-Mail/](https://pythonhosted.org/Flask-Mail/)

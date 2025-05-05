# 🧠 Stroke Prediction System using Machine Learning

A full-stack web-based application designed to assess the likelihood of a stroke based on user-inputted health parameters. The system utilizes a machine learning model (Logistic Regression) trained on real-world medical data, integrated seamlessly with an interactive, user-friendly web interface.

---

## 🔍 Features

- **User, Doctor, and Admin Roles** with secure authentication
- **Chatbot-style interface** to guide users through health input collection
- **BMI calculation** and dynamic **stroke risk prediction** via a **gauge meter**
- Real-time **report generation** showing prediction results, doctors, and hospitals
- **Doctor registration with document uploads**
- **Admin dashboard** to manage user and doctor records
- **Forgot and Reset password flow** with secure email tokens (via Flask-Mail)
- Database integration using **MySQL and SQLAlchemy**
- Trained model includes **preprocessing, SMOTE balancing, feature scaling, one-hot encoding**
- Deployed using Flask (Python backend), HTML/CSS/JS frontend

---

## 📊 Dataset

- Based on the publicly available dataset:
  **Kaggle Stroke Prediction Dataset**
  Source: [https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)

> 📌 _Note: The prediction accuracy depends heavily on the quality of the dataset. This system is educational and not medically certified for clinical use._

---

## ⚙️ Technologies Used

- **Backend:** Python, Flask, Flask-Mail, SQLAlchemy
- **Machine Learning:** scikit-learn, pandas, numpy, SMOTE
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Database:** MySQL / SQLite
- **Design Tools:** PlantUML, UML diagrams

---

## 🧰 Setup and Installation

### Prerequisites
- Python 3.8+
- MySQL (optional; SQLite supported by default)

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stroke-prediction-system.git
   cd stroke-prediction-system
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in a `.env` file:
   ```env
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_email_password_or_app_password
   SECRET_KEY=your_secret_key
   DATABASE_URL=sqlite:///stroke.db  # or use a MySQL URI
   ```

5. Run the app:
   ```bash
   python main.py
   ```

6. Access the app at:
   ```
   http://127.0.0.1:5000/
   ```

---

## 🛠 Backend Overview

- **Flask App Structure**: Modular, divided into Blueprints (auth, prediction, admin, doctor)
- **Model Training**: Preprocessed dataset, applied SMOTE for class imbalance, one-hot encoded categorical variables, and trained using logistic regression with grid search for hyperparameter tuning
- **Database Models**: Users, Doctors, Admins, Hospitals
- **Security**: Passwords hashed using Werkzeug, token-based password reset via Flask-Mail
- **Error Handling**: Robust server-side validation with graceful user feedback

---

## 🚧 Limitations

- Not suitable for real-world clinical decisions
- Limited accuracy due to non-clinical dataset
- Does not yet support direct communication or scheduling with doctors

---

## ✨ Future Improvements

- Explore advanced ML models: decision trees, ensemble models, neural networks
- Add direct doctor-patient communication (e.g., messaging, appointment booking)
- Expand data input fields: cholesterol, physical activity, etc.
- Optimize for large-scale deployment: caching, indexing, server scaling
- Improve UI/UX and introduce accessibility features

---

## 📘 License
This project is intended for educational use only.

---

## 🔗 Reference

- Soriano, Federico. "Stroke Prediction Dataset". Kaggle, 2020. [https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset](https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset)
- scikit-learn developers. (2023). scikit-learn: Machine Learning in Python. [https://scikit-learn.org](https://scikit-learn.org)
- Flask Documentation. [https://flask.palletsprojects.com](https://flask.palletsprojects.com)
- Flask-Mail. [https://pythonhosted.org/Flask-Mail/](https://pythonhosted.org/Flask-Mail/)

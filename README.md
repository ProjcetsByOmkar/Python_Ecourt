# New Delhi District Courts – Cause List PDF Downloader

A Flask web application that allows users to download daily cause lists from the **New Delhi District Courts** website as PDF files. The application uses **Selenium** to interact with the website, handles CAPTCHA, and enables users to select Court Complex, Court Number, Date, and Case Type (Civil/Criminal).

---

## 🔗 Features

* Select **Court Complex** and fetch available **Courts dynamically**.
* Choose the **Cause List date** within a valid range.
* Select **Case Type**: Civil or Criminal.
* **CAPTCHA handling** with "Load CAPTCHA" and "Refresh CAPTCHA" buttons.
* Download cause list as **PDF**.
* Persistent **Selenium session** per user to optimize performance.
* Backend logging for debugging.
* Graceful cleanup of Selenium drivers.

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Web Automation:** Selenium WebDriver, ChromeDriver (Headless)
* **Frontend:** HTML, CSS, JavaScript
* **PDF Generation:** Chrome DevTools Protocol (`Page.printToPDF`)
* **Session Management:** Flask Sessions
* **Dependencies:** Webdriver Manager, PIL, Base64

---

## 📂 Repository Structure

```
├── app.py                 # Flask application with Selenium integration
├── templates/
│   └── index.html         # HTML template for form
├── static/
│   └── (optional CSS/JS)  # Any static files if needed
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## ⚡ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/delhi-courts-causelist.git
cd delhi-courts-causelist
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Install dependencies

```bash
pip install flask selenium webdriver-manager pillow
```

```
Flask==2.3.5
selenium==5.9.1
webdriver-manager==4.1.1
pillow==10.1.0
```

---

## 🚀 Usage

1. Start the Flask server:

```bash
python app.py
```

2. Open your browser and navigate to:

```
http://localhost:5000
```

3. Steps on the website:

   * Select **Court Complex** → fetch Courts.
   * Select **Court Number**.
   * Pick the **Date** of the cause list.
   * Select **Case Type** (Civil/Criminal).
   * Click **Load CAPTCHA**, enter the text.
   * Click **Search & Download PDF** to get the cause list.

4. Optionally, click **Refresh CAPTCHA** to generate a new CAPTCHA image.

---

## ⚙️ Session Management

* Each user is assigned a unique session ID.
* A **persistent Selenium driver** is maintained per session.
* Avoids repeated CAPTCHA requests.
* Drivers can be cleaned up via:

```http
GET /cleanup_drivers
```

---

## 📝 Notes

* The application uses **headless Chrome** for automation.
* PDF generation relies on Chrome DevTools Protocol; ensure **Chrome/Chromium** is installed.
* Selenium waits are applied to handle dynamic dropdowns and page load delays.
* Captcha requests are **rate-limited** to avoid overloading the server.
* Always respect the target website’s terms of use.

---

## 💡 Troubleshooting

* **Courts not appearing:** Make sure your network allows access to `https://newdelhi.dcourts.gov.in` and ChromeDriver is compatible with your Chrome version.
* **CAPTCHA failing:** Wait 30 seconds between requests.
* **PDF download fails:** Check the console logs for Selenium errors.

---

## 🛡️ Security

* Flask `secret_key` is used for session management.
* Never hardcode sensitive keys for production; use environment variables.

---

## 📌 License

This project is open-source under the MIT License.

---

## 👨‍💻 Author

**Omkar Madhusudan Ghogare**

* Email: [[your-email@example.com](omkarofficial2107@gmail.com)]

---

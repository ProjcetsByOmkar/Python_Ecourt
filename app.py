from flask import Flask, render_template, request, send_file, jsonify, session
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import base64
from io import BytesIO
from datetime import date
import time
import logging
from uuid import uuid4

# -------------------- Config --------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = "123456"
CAUSE_LIST_URL = "https://newdelhi.dcourts.gov.in/cause-list-%E2%81%84-daily-board/"

# Store Selenium drivers per session
drivers = {}

# -------------------- Selenium Utilities --------------------
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def get_user_driver():
    sid = session.get('sid')
    if not sid:
        sid = str(uuid4())
        session['sid'] = sid
    if sid not in drivers:
        driver = get_driver()
        driver.get(CAUSE_LIST_URL)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "est_code")))
        drivers[sid] = driver
    return drivers[sid]

def fetch_court_complexes(driver):
    select = Select(driver.find_element(By.ID, "est_code"))
    return [{"text": opt.text.strip(), "value": opt.get_attribute("value")} for opt in select.options if opt.get_attribute("value")]

def fetch_courts_for_complex(driver, complex_value):
    Select(driver.find_element(By.ID, "est_code")).select_by_value(complex_value)
    time.sleep(1.5)
    select = Select(driver.find_element(By.ID, "court"))
    return [{"text": opt.text.strip(), "value": opt.get_attribute("value")} for opt in select.options if opt.get_attribute("value")]

def set_date(driver, selected_date):
    date_str = selected_date.strftime("%m/%d/%Y")
    driver.execute_script(f'document.getElementById("date").value="{date_str}";')
    driver.execute_script(f'document.getElementById("date").dispatchEvent(new Event("change"));')

def capture_captcha(driver):
    captcha = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "siwp_captcha_image_0")))
    return captcha.screenshot_as_png

def submit_and_download_pdf(driver, complex_value, court_value, cause_type, captcha_text, selected_date):
    # Select complex
    Select(driver.find_element(By.ID, "est_code")).select_by_value(complex_value)
    time.sleep(1)
    Select(driver.find_element(By.ID, "court")).select_by_value(court_value)
    set_date(driver, selected_date)
    if cause_type.lower() == "civil":
        driver.find_element(By.ID, "chkCauseTypeCivil").click()
    else:
        driver.find_element(By.ID, "chkCauseTypeCriminal").click()
    driver.find_element(By.ID, "siwp_captcha_value_0").clear()
    driver.find_element(By.ID, "siwp_captcha_value_0").send_keys(captcha_text)
    driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="Search"]').click()

    # Wait for results
    WebDriverWait(driver, 60).until(
        lambda d: "hide" in d.find_element(By.CSS_SELECTOR, ".service-loader").get_attribute("class")
    )
    pdf_data = driver.execute_cdp_cmd("Page.printToPDF", {"printBackground": True, "paperWidth": 8.27, "paperHeight": 11.69})
    return base64.b64decode(pdf_data["data"])

# -------------------- Routes --------------------
@app.route('/')
def home():
    driver = get_user_driver()
    complexes = fetch_court_complexes(driver)
    return render_template("index.html", complexes=[c["text"] for c in complexes], today=date.today().isoformat())

@app.route('/get_courts', methods=['POST'])
def get_courts():
    data = request.json
    complex_name = data.get("complex")
    driver = get_user_driver()
    complexes = fetch_court_complexes(driver)
    complex_value = next((c["value"] for c in complexes if c["text"] == complex_name), None)
    if not complex_value:
        return jsonify({"error": "Invalid complex"}), 400
    courts = fetch_courts_for_complex(driver, complex_value)
    return jsonify([c["text"] for c in courts])

@app.route('/prepare_captcha', methods=['POST'])
def prepare_captcha():
    data = request.json
    complex_name = data.get("complex")
    court_name = data.get("court")
    date_str = data.get("date")
    cause_type = data.get("cause_type")

    if not all([complex_name, court_name, date_str, cause_type]):
        return jsonify({"error": "Missing selections"}), 400

    selected_date = date.fromisoformat(date_str)
    driver = get_user_driver()

    # Store selections in session
    complexes = fetch_court_complexes(driver)
    complex_value = next((c["value"] for c in complexes if c["text"] == complex_name), None)
    courts = fetch_courts_for_complex(driver, complex_value)
    court_value = next((c["value"] for c in courts if c["text"] == court_name), None)
    session['form_data'] = {
        'complex_value': complex_value,
        'court_value': court_value,
        'date': date_str,
        'cause_type': cause_type
    }

    img_bytes = capture_captcha(driver)
    captcha_b64 = base64.b64encode(img_bytes).decode('utf-8')
    return jsonify({"captcha": f"data:image/png;base64,{captcha_b64}"})

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    data = request.form
    captcha_text = data.get("captcha")

    form_data = session.get('form_data')
    if not form_data or not captcha_text:
        return jsonify({"error": "Missing form data or CAPTCHA"}), 400

    driver = get_user_driver()
    selected_date = date.fromisoformat(form_data['date'])
    pdf_bytes = submit_and_download_pdf(
        driver,
        form_data['complex_value'],
        form_data['court_value'],
        form_data['cause_type'],
        captcha_text,
        selected_date
    )
    return send_file(BytesIO(pdf_bytes), as_attachment=True, download_name=f"CauseList_{form_data['date']}.pdf", mimetype="application/pdf")

# -------------------- Cleanup --------------------
@app.route('/cleanup_drivers')
def cleanup_drivers():
    for driver in drivers.values():
        try:
            driver.quit()
        except:
            pass
    drivers.clear()
    return "All drivers cleaned up."

# -------------------- Run --------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

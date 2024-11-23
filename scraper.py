from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
from dotenv import find_dotenv, load_dotenv
import mysql.connector

load_dotenv(find_dotenv())

AMAZON_EMAIL = os.environ["AMAZON_EMAIL"]
AMAZON_PASSWORD = os.environ["AMAZON_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]

def connect_to_database():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def save_highlight_to_db(cursor, book_title, highlight):
    try:
        query = "INSERT INTO highlights (bookTitle, highlights) VALUES (%s, %s)"
        cursor.execute(query, (book_title, highlight))
    except Exception as e:
        print(f"Fout bij opslaan in database: {e}")

def scrape_kindle_highlights():
    selenium_url = "http://selenium:4444/wd/hub"
    options = webdriver.ChromeOptions()

    driver = webdriver.Remote(
        command_executor=selenium_url,
        options=options
    )

    db_connection = connect_to_database()
    db_cursor = db_connection.cursor()


    try:
        driver.get("https://read.amazon.com/notebook")

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
        driver.find_element(By.ID, "ap_email").send_keys(AMAZON_EMAIL)
        driver.find_element(By.ID, "continue").click()

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
        driver.find_element(By.ID, "ap_password").send_keys(AMAZON_PASSWORD)
        driver.find_element(By.ID, "signInSubmit").click()

        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".kp-notebook-library-each-book")))

        print("Je highlights per boek:")

        books = driver.find_elements(By.CSS_SELECTOR, ".kp-notebook-library-each-book")
        for i in range(len(books)):
            try:
                books = driver.find_elements(By.CSS_SELECTOR, ".kp-notebook-library-each-book")
                book = books[i]
                book_title = book.find_element(By.CSS_SELECTOR, ".kp-notebook-searchable.a-text-bold").text.strip()
                book.click()
                WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".kp-notebook-highlight")))
                highlights = driver.find_elements(By.CSS_SELECTOR, ".kp-notebook-highlight")
                for highlight in highlights:
                    highlight_text = highlight.text.strip()
                    print(f"- {highlight_text}")
                    save_highlight_to_db(db_cursor, book_title, highlight_text)
                db_connection.commit()
                driver.get("https://read.amazon.com/notebook")
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".kp-notebook-library-each-book")))

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Fout bij verwerken van boek: {e}")

    except TimeoutException:
        print("Er trad een timeout op tijdens het inloggen of laden van de pagina. Controleer je inloggegevens of netwerkverbinding.")

    finally:
        driver.quit()
        db_cursor.close()
        db_connection.close()
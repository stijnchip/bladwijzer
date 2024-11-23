import mysql.connector
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import schedule
import time
from scraper import scrape_kindle_highlights
import os
from mysql.connector import errorcode
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_NAME = os.environ["DB_NAME"]
SENDGRID_API_KEY = os.environ["SENDGRID_API_KEY"]
TO_EMAIL = os.environ["TO_EMAIL"]
FROM_EMAIL = os.environ["FROM_EMAIL"]

def connect_to_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def setup_database_and_table(retries=5, retry_delay=5):
    create_table_query = """
    CREATE TABLE `highlights` (
      `id` int NOT NULL,
      `bookTitle` varchar(255) NOT NULL,
      `highlights` text NOT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

    ALTER TABLE `highlights`
      ADD PRIMARY KEY (`id`),
      ADD UNIQUE KEY `unique_note` (`bookTitle`,`highlights`(255));

    ALTER TABLE `highlights`
      MODIFY `id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=647;
    """

    attempt = 0
    while attempt < retries:
        try:
            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD
            )
            cursor = connection.cursor()

            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()
            database_exists = any(db[0] == DB_NAME for db in databases)

            if not database_exists:
                cursor.execute(f"CREATE DATABASE {DB_NAME}")
                print(f"Database '{DB_NAME}' aangemaakt.")

            cursor.close()
            connection.close()

            connection = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            cursor = connection.cursor()

            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            table_exists = any(tbl[0] == "highlights" for tbl in tables)

            if not table_exists:
                for statement in create_table_query.split(";"):
                    if statement.strip():
                        cursor.execute(statement)
                print(f"Tabel 'highlights' aangemaakt.")

            connection.commit()
            break

        except mysql.connector.Error as err:
            attempt += 1
            print(f"Fout bij verbinding: {err}")
            if attempt < retries:
                print(f"Wachten {retry_delay} seconden en opnieuw proberen... ({attempt}/{retries})")
                time.sleep(retry_delay)
            else:
                print("Maximale pogingen bereikt. Verbinding mislukt.")
                raise

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals() and connection.is_connected():
                connection.close()

def fetch_random_highlight():
    try:
        conn = connect_to_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT bookTitle, highlights FROM highlights ORDER BY RAND() LIMIT 1;")
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result
    except mysql.connector.Error as err:
        print(f"Fout bij verbinden met de database: {err}")
        return None

def send_email(subject, content):
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=TO_EMAIL,
            subject=subject,
            html_content=content
        )
        response = sg.send(message)
        print(f"E-mail verzonden! Statuscode: {response.status_code}")
    except Exception as e:
        print(f"Fout bij versturen van e-mail: {e}")

def daily_highlight_email():
    highlight = fetch_random_highlight()
    if highlight:
        book_title = highlight['bookTitle']
        highlight_text = highlight['highlights']

        subject = f"📚 Highlight of the day from '{book_title}'"
        content = f"""
        <h2>Highlight of the day</h2>
        <p><strong>Boek:</strong> {book_title}</p>
        <blockquote>{highlight_text}</blockquote>
        <p>Keep reading and learning! 📖</p>
        """

        send_email(subject, content)
    else:
        print("Geen highlight gevonden om te versturen.")

schedule.every().day.at("09:00").do(daily_highlight_email)
schedule.every().day.at("12:00").do(scrape_kindle_highlights)

if __name__ == "__main__":
    setup_database_and_table()
    print("Script gestart. Wacht op geplande taken...")
    while True:
        schedule.run_pending()
        time.sleep(1)
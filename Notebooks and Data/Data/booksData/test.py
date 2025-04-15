import json
import time
import os
import traceback
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import clipboard
from pdf2image import convert_from_path

def process_image(image_url, retries=3):
    # Set up Chrome options
    chrome_options = Options()
    # Uncomment the next line if headless mode is necessary
    # chrome_options.add_argument("--headless")  # Disable headless mode to allow file dialog

    # Initialize the WebDriver (running in non-headless mode)
    driver = webdriver.Chrome(options=chrome_options)

    attempt = 0  # Counter for retries

    while attempt < retries:
        try:
            # Step 1: Open Google Lens
            driver.get("https://lens.google.com/")
            time.sleep(5)  # Wait for the page to load

            # Step 2: Locate and click the "Importez un fichier" button
            import_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[jsname="tAPGc"]'))
            )
            ActionChains(driver).move_to_element(import_button).click().perform()

            # Step 3: Select the file
            file_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
            if os.path.exists(image_url):
                file_input.send_keys(image_url)
            else:
                print(f"File does not exist: {image_url}")
                break

            # Step 4: Wait for the image to process
            time.sleep(5)

            # Step 5: Interact with other buttons as necessary
            try:
                new_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@jsname='XPtOyb']//button[@aria-label='Passer en mode Texte']"))
                )
                new_button.click()
                time.sleep(5)
            except Exception:
                print("Error clicking 'Passer en mode Texte' button.")

            # Click the "Sélectionner tout le texte" button
            try:
                select_text_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//span[@jsname='V67aGc' and text()='Sélectionner tout le texte']"))
                )
                select_text_button.click()
                time.sleep(5)
            except Exception:
                print("Error clicking 'Sélectionner tout le texte' button.")

            # Click the "Copier le texte" button
            try:
                copy_text_button = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Copier le texte']"))
                )
                copy_text_button.click()
                time.sleep(5)
            except Exception:
                print("Error clicking 'Copier le texte' button.")

            # Success: Exit the loop
            break

        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            traceback.print_exc()
            attempt += 1  # Increment retry count
            time.sleep(2 ** attempt)  # Exponential backoff

    # Close the driver after all retries or success
    driver.quit()

    if attempt == retries:
        print("Failed to process the image after maximum retries.")




# Initialize the structure for the JSON data
book_name = "3_Hamouda_et_al_21(3).om.fr.fr.ar"
json_data = {"book_name": book_name, "pages": []}

def extract_pdf_pages_as_images(pdf_path, start_page, end_page, output_dir, book_name):
    """
    Extract pages from a PDF as images and save them to the specified directory.
    
    Parameters:
    - pdf_path: Path to the input PDF file.
    - start_page: The starting page number (1-based index).
    - end_page: The ending page number (1-based index).
    - output_dir: Directory where the extracted images will be saved.
    
    Returns:
    - A list of paths to the saved image files.
    """
    # Check if the output directory exists, create it if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Convert PDF to a list of images (one per page)
    try:
        pages = convert_from_path(pdf_path, first_page=start_page, last_page=end_page)
    except Exception as e:
        print(f"Error while converting PDF to images: {e}")
        return []

    # Save the extracted pages as images
    image_paths = []
    for i, page in enumerate(pages, start=start_page):
        image_filename = f"page_{i}.png"  # You can change the format to .jpg or others
        imageDir = os.path.join(output_dir, 'images')
        if not os.path.exists(imageDir):
            os.makedirs(imageDir)
        image_path = os.path.join(imageDir, image_filename)
        page.save(image_path, 'PNG')
        image_paths.append(image_path)
        full_path = os.path.abspath(image_path)
        process_image(full_path)
        text = clipboard.paste()
        # Add the page number and extracted text to the JSON data
        json_data["pages"].append({"page": i, "text": text})
        clipboard.copy('')

    # Save the JSON data to a file
    json_file_path = os.path.join(output_dir, "data.json")
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

        print(f"Saved image: {image_path}")
    
    return image_paths

# Example usage
pdf_path = '/home/billal/NLP Project/Data_books/other books/3_Hamouda_et_al_21(3).om.fr.fr.ar.pdf'
output_dir = '/home/billal/NLP Project/Data_books/other books/3_Hamouda_et_al_21(3).om.fr.fr.ar'
start_page = 1
end_page = 15

extracted_images = extract_pdf_pages_as_images(pdf_path, start_page, end_page, output_dir, book_name)




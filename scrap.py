from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

def scrap(base_url, output_file):
    result = []
    driver = None
    page = 1
    not_found = False
    
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Continue until not_found becomes True
        while not not_found:
            url = f'{base_url}{page}'
            driver.get(url)
            print(f"Processing page {page}: {url}")
            
            # Add a small delay to allow page to load
            time.sleep(1)
            
            # Check if page exists by looking for common "not found" indicators
            try:
                # Adjust these selectors based on the website's structure
                not_found_indicators = [
                    "404",
                    "not found",
                    "page not found",
                    "halaman tidak ditemukan"
                ]
                
                page_text = driver.find_element(By.TAG_NAME, 'body').text.lower()
                if any(indicator in page_text for indicator in not_found_indicators):
                    print(f"Page {page} not found. Stopping scraping.")
                    not_found = True
                    continue
                
                # Find articles or content containers
                selected_elements = driver.find_elements(By.CSS_SELECTOR, 'article, [class*="row"], [class*="col"]')
                
                if not selected_elements:
                    print(f"No content found on page {page}. Checking if this is the last page.")
                    not_found = True
                    continue
                
                for element in selected_elements:
                    try:
                        # Find link within the element
                        a_tag = element.find_element(By.TAG_NAME, 'a')
                        detaillink = a_tag.get_attribute('href')
                        
                        if detaillink:
                            print(f"Processing detail link: {detaillink}")
                            
                            # Open detail page
                            driver.get(detaillink)
                            time.sleep(1)
                            
                            # Get all paragraphs
                            paragraphs = driver.find_elements(By.TAG_NAME, 'p')
                            paragraph_texts = [p.text for p in paragraphs if p.text.strip()]
                            
                            # Store results
                            result.append({
                                'link': detaillink,
                                'text': paragraph_texts
                            })
                            
                            # Go back to the listing page
                            driver.back()
                            time.sleep(1)
                            
                    except Exception as inner_e:
                        print(f"Error processing detail link on page {page}: {inner_e}")
                        continue
                
                page += 1
                
            except Exception as e:
                print(f"Error checking page {page}: {e}")
                not_found = True
                
    except Exception as e:
        print(f"Fatal error: {e}")
        
    finally:
        if driver:
            driver.quit()
        
        # Save results to CSV
        if result:
            with open(output_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(['Link', 'Text'])
                
                for item in result:
                    link = item['link']
                    texts = " ".join(item['text'])
                    writer.writerow([link, texts])
            
            print(f"Results saved to {output_file}")
        
    return result

def scrape_multiple_websites(websites):
    for website in websites:
        base_url = website['url']
        output_file = website['output_file']
        print(f"Scraping from {base_url} and saving to {output_file}...")
        
        # Memanggil fungsi scrap untuk setiap website
        scrap(base_url, output_file)
        print(f"Finished scraping {base_url}, results saved to {output_file}")

websites = [
    {'url': 'https://gunungmaskab.go.id/category/berita/page/', 'output_file': 'gunungmas_kab.csv'},
    {'url': 'https://pemda.lamandaukab.go.id/category/berita/page/', 'output_file': 'lamandau_kab.csv'},
    {'url': 'https://prokopim.mahakamulukab.go.id/category/terkini/page/', 'output_file': 'mahakamulu_kab.csv'},
    {'url': 'https://penajamkab.go.id/category/berita-daerah/page/', 'output_file': 'penajam_kab.csv'},
    {'url': 'https://tanatidungkab.go.id/public/category/berita/page/', 'output_file': 'tanatidung_kab.csv'},
    {'url': 'https://barrukab.go.id/category/berita/page/', 'output_file': 'baru_kab.csv'},
]
scrape_multiple_websites(websites)
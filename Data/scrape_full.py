from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd
import csv
from selenium.webdriver.support.ui import Select


# Set up the Selenium WebDriver with the provided chromedriver path
chromedriver_path = "./chromedriver/path.txt"
chrome_service = ChromeService(executable_path=chromedriver_path)
driver = webdriver.Chrome(service=chrome_service)
f=open('./read_full.txt','r')
a=f.read()
print(a,type(a))
l=int(a)
f.close()


# Configurable values
login_url = "https://go.drugbank.com/public_users/log_in"
drug_url = "https://go.drugbank.com/drugs/DB"
page_5_xpath = '//*[@id="drug-interactions-table_next"]/a'
# Navigate to the login page
driver.get(login_url)

# Handle unexpected alert
try:
    alert = Alert(driver)
    alert.dismiss()
    print("Handled unexpected alert.")

except:
    print("No unexpected alert.")

# Assuming you need to fill in username and password fields
username = "<YOUR_USERNAME>"
password = "<YOUR_PASSWORD>"
username_field = driver.find_element(By.ID, "public_user_email")
password_field = driver.find_element(By.ID, "public_user_password")
username_field.send_keys(username)
password_field.send_keys(password)
wait = WebDriverWait(driver, 10)

# Submit the login form
login_button = driver.find_element(By.XPATH, '//*[@id="public-user-form"]/input[2]')
login_button.click()

try:
    alert = Alert(driver)
    alert.accept()  # Click OK on the alert
    print("Handled warning alert after login.")

except:
    print("No warning alert after login.")

# Wait for the login to complete (you might need to adjust the sleep time or use WebDriverWait)
time.sleep(2)
# Wait for the login to complete using WebDriverWait

# Now, navigate to the desired link after login
for m in range(0,100000):
    name=[]
    drugB=[]
    interaction=[]
    mechanism=[]
    danger=[]
    try:
        if l<100:
            durl=drug_url+'000'+str(l)
        elif l>999 and l<=9999:
            durl=drug_url+'0'+str(l)
        elif l>9999:
            durl=drug_url+str(l)
        else:
            durl=drug_url+'00'+str(l)
        driver.get(durl)
        l=l+1
        g=open('./read_full.txt','w')
        g.write(str(l))
        g.close()
        page_source = driver.page_source
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        heading = soup.select_one('.content-header h1')
        head=str(heading)
        head1=head[35:]
        head_name=head1[:-5]
        print(head_name)
        interactions_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "interactions-sidebar-header"))
        )

        # Click on the "Interactions" link
        interactions_link.click()
    except TimeoutException:
        print(f"Timed out waiting for the element to be clickable on page {m}.")
        continue
    except Exception as e:
        print(f"Error on page {m}: {e}")
        
    
    time.sleep(6)
    if not driver.find_elements(By.ID, 'drug-interactions-table'):
        print("Table not found on page , moving to the next page.")
        continue
    
    dropdown_element = driver.find_element(By.NAME, 'drug-interactions-table_length')
    select = Select(dropdown_element)
    select.select_by_value('100')
    time.sleep(6)
    total_pages_text = driver.find_element(By.ID, "drug-interactions-table_paginate").text.split()[-2]
    total_pages_text = total_pages_text.replace(",", "")  # Remove commas from the number
    total_pages = int(total_pages_text)
    print(total_pages)
    if total_pages==1:
        try:
        
            for d in range(0,total_pages):
                time.sleep(3)
                if total_pages>1:

                    next_button=wait.until(EC.element_to_be_clickable((By.XPATH, page_5_xpath)))
                    
                    # Click on the 5th page
                    ActionChains(driver).move_to_element(next_button).perform()

                    driver.find_element(By.XPATH, page_5_xpath).click()

                    #wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.mini-banner.banner-holder')))
                    # Wait for the page to load after clicking
                    time.sleep(3)
                # Use BeautifulSoup to scrape data from the specified element
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract data column-wise from the table
                drug_column = [a.text for a in soup.select('table#drug-interactions-table tbody td:nth-child(1) a')]
                interaction_column = [td.text for td in soup.select('table#drug-interactions-table tbody td:nth-child(2)')]
                for i in drug_column:
                    drugB.append(i)
                    
                for i in interaction_column:
                    interaction.append(i)
                    if 'risk' in i:
                        danger.append('risk')
                    else:
                        danger.append('no risk')
                    if 'increase' in i:

                        mechanism.append('increase')
                    elif 'increased' in i:
                        mechanism.append('increase')
                    elif 'decrease' in i:
                        mechanism.append('decrease')
                    elif 'decreased' in i:
                        mechanism.append('decrease')
                    else:
                        mechanism.append(' ')
                for i in range(len(drugB)):
                    name.append(head_name)
            

                
            
            
            
        except TimeoutException:
            print("Timed out waiting for the element to be clickable.")
        except NoSuchElementException:
            print("Element not found with the specified XPath.")
        finally:
            rows = zip(name, drugB, interaction, mechanism,danger)

            # Specify the CSV file path
            csv_file_path = './drugs_full.csv'

            # Write the data to the CSV file
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                
                # Write the header
                
                # Write the rows
                writer.writerows(rows)
            print(f"Data has been successfully written to {csv_file_path} from {durl}")
        # Click on the 5th page using Selenium with XPath selector
    else:
        try:
            
            for d in range(0,total_pages-1):
                time.sleep(3)
                if total_pages>1:

                    next_button=wait.until(EC.element_to_be_clickable((By.XPATH, page_5_xpath)))
                    
                    # Click on the 5th page
                    ActionChains(driver).move_to_element(next_button).perform()

                    driver.find_element(By.XPATH, page_5_xpath).click()

                    #wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '.mini-banner.banner-holder')))
                    # Wait for the page to load after clicking
                    time.sleep(3)
                # Use BeautifulSoup to scrape data from the specified element
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extract data column-wise from the table
                drug_column = [a.text for a in soup.select('table#drug-interactions-table tbody td:nth-child(1) a')]
                interaction_column = [td.text for td in soup.select('table#drug-interactions-table tbody td:nth-child(2)')]
                for i in drug_column:
                    drugB.append(i)
                    
                for i in interaction_column:
                    interaction.append(i)
                    if 'risk' in i:
                        danger.append('risk')
                    else:
                        danger.append('no risk')
                    if 'increase' in i:

                        mechanism.append('increase')
                    elif 'increased' in i:
                        mechanism.append('increase')
                    elif 'decrease' in i:
                        mechanism.append('decrease')
                    elif 'decreased' in i:
                        mechanism.append('decrease')
                    else:
                        mechanism.append(' ')
                for i in range(len(drugB)):
                    name.append(head_name)
            

                
            
            
            
        except TimeoutException:
            print("Timed out waiting for the element to be clickable.")
        except NoSuchElementException:
            print("Element not found with the specified XPath.")
        finally:
            rows = zip(name, drugB, interaction, mechanism,danger)

            # Specify the CSV file path
            csv_file_path = './drugs_full.csv'

            # Write the data to the CSV file
            with open(csv_file_path, 'a', newline='') as file:
                writer = csv.writer(file)
                
                # Write the header
                
                # Write the rows
                writer.writerows(rows)

            print(f"Data has been successfully written to {csv_file_path} from {durl}")
driver.quit()



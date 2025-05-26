from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time

# Set up Firefox driver
driver = webdriver.Firefox()

# Go to the page
driver.get("https://flweb.janelia.org/cgi-bin/flew.cgi")

# Wait until the input box is available
wait = WebDriverWait(driver, 10)
input_box = wait.until(EC.presence_of_element_located((By.ID, "lines")))

# Enter genotype and press Enter
#input_box.clear()

# input_box.send_keys("R85C10")
# input_box.send_keys(Keys.RETURN)

# List of genotypes to enter one by one
genotypes = ["R85C10", "R21H11", "R65H02", "R60F09"]

# Load genotypes from CSV
# df = pd.read_csv(r"X:\MU Lab Users\Shiju_sisobhan\Slumber\AB_DBD_Unique_lines.csv")  # Replace with your actual file name
# genotypes = df["Extracted_ID"].dropna().astype(str).tolist()

# Enter each genotype individually and simulate pressing Enter
for genotype in genotypes:
    input_box.clear()
    input_box.send_keys(genotype)
    time.sleep(1.5)  # small delay to enter
    input_box.send_keys(Keys.RETURN)





# --- Step 2: Click the Search button ---
search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Search']")))
search_button.click()


# Get updated page source and parse it
soup = BeautifulSoup(driver.page_source, "html.parser")

# Try finding all tables
tables = soup.find_all("table")
print(f"Found {len(tables)} tables")

# Inspect the table and select intersted- We are interested in the 5th table (index=4)
df = pd.read_html(str(tables))[4]

# Create an empty list to collect rows
expanded_rows = []

import re
# Loop through each row in the original df

for idx, row in df.iterrows():
    expressed = row.get("Expressed in")
    line = row.get("Line")
    tissue = row.get("Tissue")

    # Skip rows with empty or missing expression info
    if pd.isna(expressed) or not isinstance(expressed, str):
        continue

    # Extract all '<region> (int, int)' patterns
    # This pattern matches "region name (int, int)" with optional leading commas/space
    entries = re.findall(r'\s*([^(),]+(?: [^(),]+)*)\s*\((\d),\s*(\d)\)', expressed)

    if not entries:
        print(f"[Warning] No matches found in row {idx}: '{expressed}'")
# collect the neurons that expressed genotypes and its intensity and distribution
    for region, intensity, distribution in entries:
        expanded_rows.append({
            "neuron": region.strip(),
            "intensity": int(intensity),
            "distribution": int(distribution),
            "Line": line,
            "Tissue": tissue
        })

# Create the new dataframe
df_new = pd.DataFrame(expanded_rows)

df_new.to_csv("Gal4_GW_BL_Anatomic_Flylight.csv", index=False)



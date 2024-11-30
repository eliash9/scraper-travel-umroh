from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

# Tentukan path ke chromedriver (sesuaikan dengan path Anda)
chromedriver_path = 'D:/python/chromedriver.exe'  # Ganti dengan path ke chromedriver Anda

# Setup Service untuk ChromeDriver
service = Service(executable_path=chromedriver_path)

# Atur opsi untuk Chrome
options = Options()
#options.add_argument('--headless')  # Menjalankan tanpa membuka jendela browser
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
	  


# Membuat instance browser dengan Service dan Options
driver = webdriver.Chrome(service=service, options=options)

# Akses halaman
url = 'https://umrahcerdas.kemenag.go.id/home/travel'
driver.get(url)

# Tunggu hingga tabel dimuat
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, 'example1'))  # ID tabel, sesuaikan jika perlu
)

# Temukan jumlah total halaman melalui DataTables API
script_total_pages = "return $('#example1').DataTable().page.info().pages;"
total_pages = driver.execute_script(script_total_pages)

# Inisialisasi untuk menyimpan semua data
all_rows = []

# Loop untuk iterasi setiap halaman
for page in range(1, total_pages + 1):
    # Set halaman dengan DataTables API
    script = f"$('#example1').DataTable().page({page - 1}).draw('page');"
    driver.execute_script(script)
    
    # Tunggu hingga halaman berikutnya dimuat
    WebDriverWait(driver, 10).until(
        lambda d: driver.execute_script("return $('#example1').DataTable().page.info().page;") == (page - 1)
    )
    
    # Ambil data tabel
    table = driver.find_element(By.ID, 'example1')
    
    # Ambil header tabel (hanya pada halaman pertama)
    if page == 1:
        headers = [header.text.strip() for header in table.find_elements(By.TAG_NAME, 'th')]
    
    # Ambil baris data dari tabel
    rows = []
    for row in table.find_elements(By.CSS_SELECTOR, "table tbody tr"):
        cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")]
        if len(cols) > 0:  # Pastikan hanya baris yang memiliki data diambil
            rows.append(cols)
    all_rows.extend(rows)

# Ubah ke DataFrame
df = pd.DataFrame(all_rows, columns=headers)

# Tampilkan DataFrame
print(df)

# Simpan ke CSV
df.to_csv('hasil_tabel_pagination_datatables.csv', index=False, encoding='utf-8')  # Menyimpan tanpa index dan menggunakan encoding utf-8

# Tutup browser setelah selesai
driver.quit()

print("Data berhasil disimpan ke 'hasil_tabel_pagination_datatables.csv'")

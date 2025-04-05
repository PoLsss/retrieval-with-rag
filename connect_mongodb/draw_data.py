import requests
from bs4 import BeautifulSoup
import csv

# URL của trang web chứa dữ liệu môn học
url = "https://student.uit.edu.vn/content/bang-tom-tat-mon-hoc"

# Gửi request để lấy nội dung trang web
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Tìm bảng dữ liệu
table = soup.find("table")

# Lấy tiêu đề cột
table = soup.find("table")

# Trích xuất dữ liệu từ bảng
rows = []
for row in table.find_all("tr"):
    cells = row.find_all(["th", "td"])
    row_data = [cell.get_text(strip=True) for cell in cells]
    if row_data:
        rows.append(row_data)

# Lưu vào file CSV
csv_filename = "table_data.csv"
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerows(rows)

print(f"Dữ liệu đã được lưu vào {csv_filename}")
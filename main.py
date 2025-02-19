import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pytrends.request import TrendReq

sheet_id = ""
gid = ""
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
df = pd.read_csv(csv_url)

# เลือกเฉพาะคอลัมน์ที่ต้องการและเปลี่ยนชื่อคอลัมน์
df_selected = df[['product_id', 'product_thumb_image', 'product_title']].rename(
    columns={'product_id': 'รหัสสินค้า', 'product_thumb_image': 'ชื่อรูป', 'product_title': 'ชื่อสินค้า'}
)

prices = []
information = []
keywords = []
prompt1 = []
prompt2 = []
prompt3 = []
prompt4 = []
df_product_url = df['product_url']
df_product_title = df['product_title']
pytrends = TrendReq(hl='th', tz=360)

for product_url, product_title in zip(df_product_url, df_product_title):
    print(f"🌀 กำลังดึงข้อมูลสำหรับ {product_title}...")
    try:
        response = requests.get(product_url)
        response.raise_for_status()  # ตรวจสอบว่าการร้องขอสำเร็จ
        
        soup = BeautifulSoup(response.text, "html.parser")

        # ค้นหาส่วนที่แสดงราคาสินค้า (ปรับ class ให้ตรงกับโครงสร้างเว็บ)
        price_element = soup.find("span", class_="sale-price-detail")
        product_price = price_element.get_text(strip=True) if price_element else ""
        
        info_element = soup.find("div", id="collapse-detail")
        product_info = info_element.get_text("\n", strip=True) if info_element else ""
        time.sleep(3)
        kw_suggestions = product_title.split(" ")[0]
        suggestions = pytrends.suggestions(kw_suggestions)
        product_keyword = ", ".join(item["title"] for item in suggestions)
    except requests.RequestException as e:
        product_price = ""
        product_info = ""
        product_keyword = ""
    print(f"💸 ราคา {product_price}")
    print(f"🔎 คำค้นหาที่เกี่ยวข้อง {product_keyword if product_keyword else 'ไม่มี'}")
    prices.append(product_price)
    information.append(product_info)
    keywords.append(product_keyword)
    prompt1.append(f'ในฐานะที่เป็น Digital Marketing experts on SEO ต้องการตั้งชื่อสินค้า พร้อมรายละเอียดสินค้าที่เน้น SEO ให้ติดหน้าแรกของ Google search ใน Keywords "{product_keyword if product_keyword else kw_suggestions}" โดยเดิม มีรายละเอียดสินค้าดังนี้ {product_info} ช่วยสร้าง Title, Description, keywords ให้เน้น SEO และผู้อ่านรายละเอียดสนใจจะซื้อสินค้านี้')
    prompt2.append(f'Title “{product_title}”  เน้นว่าเป็น {product_keyword if product_keyword else kw_suggestions} อยากเพิ่มรายละเอียดนี้ ช่วยเพิ่มเติมใน SEO content นี้ให้ที')
    prompt3.append("ช่วยรวมเนื้อหา SEO ทั้งสองอันเข้าด้วยกันให้เหมาะสม")
    prompt4.append("[English Version]")

df_selected['ราคาสินค้า'] = prices
df_selected['รายละเอียดสินค้า'] = information
df_selected['คำค้นหาที่เกี่ยวข้อง'] = keywords
df_selected['พรอมต์ที่หนึ่ง'] = prompt1
df_selected['พรอมต์ที่สอง'] = prompt2
df_selected['พรอมต์ที่สาม'] = prompt3
df_selected['พรอมต์ที่สี่'] = prompt4

# บันทึกลงไฟล์ Excel มะม่วงกวน
output_filename = "products-thpm.xlsx"
df_selected.to_excel(output_filename, index=False, engine="openpyxl")

print(f"✅ บันทึกข้อมูลลงไฟล์ {output_filename} สำเร็จ!")
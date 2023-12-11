import threading

from PIL import Image, ImageDraw, ImageFont
import requests
from datetime import datetime, timedelta
import time
import os
from io import BytesIO
import shutil
from zipfile import ZipFile
from concurrent.futures import ThreadPoolExecutor
def find_available_images(base_url, current_time, max_hours_back=24, num_images=10):

    found_urls = []
    checked_hours = 0

    while len(found_urls) < num_images and checked_hours < max_hours_back:
        check_hour = current_time.hour
        check_date = current_time.date()

        url = f"{base_url}{check_date.strftime('%Y-%m-%d')}_{check_hour:02d}-00-00.png"

        response = requests.head(url)
        if response.status_code == 200:
            found_urls.append(url)

        checked_hours += 1
        current_time -= timedelta(hours=1)  # Aktualizacja czasu

    return found_urls if found_urls else None

def download_image(url, file_path):

    if os.path.exists(file_path): #Check if file exists
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with print_lock:
            print(f"{current_time} Obraz {file_path} już istnieje. Pobieranie anulowane.")
        return False

    #Download and save iamge
    try:
        response = requests.get(url, stream=True)
        with Image.open(BytesIO(response.content)).convert('RGB') as image:
            image.save(file_path)
            modification_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            formatted_time = modification_time.strftime("%Y-%m-%d %H:%M:%S")
        with print_lock:
            print(f"Obraz został pobrany i zapisany jako {file_path}, data modyfikacji obrazu: {formatted_time}")
        return True
    except Exception as e:
        print("Wystąpił błąd podczas pobierania lub zapisywania obrazu:", e)
        return False
def cut_image(img):
    width, height = img.size
    gray = img.convert('L')

    left_border = None
    right_border = None
    dark_threshold = 30  # Ustawienie progu dla "ciemnych" pikseli

    for x in range(width):
        for y in range(50, 100):  # Zakres przeszukiwania
            if gray.getpixel((x, y)) < dark_threshold:  # Zmiana warunku na mniej restrykcyjny
                if left_border is None:
                    left_border = max(0, x - 30)
                right_border = min(width, x + 30)

    if left_border is not None and right_border is not None:
        cropped_img = img.crop((left_border, 0, right_border, height))
        return cropped_img
    else:
        print("Nie znaleziono czarnego obramowania.")
        return img

def add_date(image, url):
    date_text = url.replace(base_url, "").replace(".png", "")

    try:
        font = ImageFont.truetype('arial.ttf', 32)
    except IOError:
        font = ImageFont.load_default()

    draw = ImageDraw.Draw(image)
    text_x = 5
    text_y = 0

    draw.text((text_x,text_y), date_text, font=font, fill=(0,0,0))

    return image

def archive_images(save_dir):
    main_dir = os.path.dirname(save_dir)
    archived_dir = os.path.join(main_dir, 'archived_images')

    if not os.path.exists(archived_dir):
        os.makedirs(archived_dir)

    files = os.listdir(save_dir)
    # files.sort(key=lambda x: os.path.getmtime(os.path.join(save_dir, x)))
    files.sort()
    for file_to_archive in files[10:]:
        date = file_to_archive.split('_')[0]
        zip_name = f"{date}.zip"
        zip_path = os.path.join(archived_dir, zip_name)

        # Przenoszenie i archiwizacja pliku
        shutil.move(os.path.join(save_dir, file_to_archive), os.path.join(archived_dir, file_to_archive))
        with ZipFile(zip_path, 'a') as zipf:
            zipf.write(os.path.join(archived_dir, file_to_archive), file_to_archive)
            print(f"Obraz {file_to_archive} przeniesiony do archiwum {zip_name}.")

        os.remove(os.path.join(archived_dir, file_to_archive))
    else:
        print("Nie ma wystarczającej liczby obrazów do archiwizacji.")

def create_animation(save_dir, gif_name='animation.gif',duration=500):
    images = os.listdir(save_dir)
    images.sort()
    frames = [Image.open(os.path.join(save_dir, image)) for image in images]
    frame_one = frames[0]
    frame_one.save(gif_name, format="GIF", append_images=frames[1:], save_all=True, duration=duration, loop=0)

def process_image(url, save_dir):
    date_hour = url.split('/')[-1].split('.')[0]
    file_path = os.path.join(save_dir, f"{date_hour}.png")

    if download_image(url, file_path):  # Check if image is downloaded
        image = Image.open(file_path)
        edited_image = cut_image(image)
        edited_image = add_date(edited_image, url)
        edited_image.save(file_path)

def process_images(urls, save_dir):
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_image, url, save_dir) for url in urls]
        for future in futures:
            future.result()

print_lock = threading.Lock()
# Base URL for images
base_url = "https://www.pogodowecentrum.pl/static/maps/current_weather_maps/temperature/pl/"

current_time = datetime.now()

urls = find_available_images(base_url, current_time, max_hours_back=24, num_images=10) #Find the first available image and generate URLs for 10 images

save_dir = "weather_images"  #Directory to save the images
os.makedirs(save_dir, exist_ok=True)

process_images(urls, save_dir)
create_animation(save_dir)
print("GIF created")

while True:
    time.sleep(5)
    last_image_url = find_available_images(base_url, current_time, max_hours_back=24, num_images=1)
    if last_image_url:
        process_images(last_image_url, save_dir)
    time.sleep(5)
    archive_images(save_dir)
    time.sleep(5)
    create_animation(save_dir)
    time.sleep(60)


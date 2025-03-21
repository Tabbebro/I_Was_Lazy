import os
import re # For Cleaning Text
import eyed3    # For Metadata
import requests # For Image Loading
import subprocess # For 320 kbit/s MP3 Downloading
from PIL import Image   # For image cropping
from tqdm import tqdm   # For Progress Bar
from datetime import datetime   # For Time Stamps
from pytubefix import YouTube   # For Downloading Youtube Video
from colorama import init, Fore, Style # For Text Colors

init(convert=True, autoreset=True)

# Function to handle download progress
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progress_bar.update(bytes_downloaded - progress_bar.n)  # Update progress bar

def get_time():
    current_time = datetime.now().strftime("%H:%M")
    text = f"[{current_time}] "
    return text

def download_audio(videoUrl, audioOutputFolder, imageOutputFolder):
    global progress_bar
    try:
        # Gets The Video From URL
        yt = YouTube(videoUrl, on_progress_callback=on_progress)

        # Extracts Only Audio
        audio = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

        # Check If There Is No Audio
        if not audio:
            raise Exception("No audio stream available for this video")
        
        # Initialize progress bar
        progress_bar = tqdm(total=audio.filesize, unit='B', unit_scale=True, desc=yt.title)

        # Downloads The File
        outFile = audio.download(output_path=audioOutputFolder)

        # Close the progress bar
        progress_bar.close()

        # Convert to MP3 using moviepy
        mp3_file = convert_to_mp3(outFile, audioOutputFolder)

        # Download Thumbnail for Album Art
        thumbnail_path = download_thumbnail(videoUrl, imageOutputFolder)

        # Add Metadata and Album Art
        add_metadata(mp3_file, yt, thumbnail_path)

        # Check If File Exists
        if not os.path.exists(mp3_file):
            raise FileNotFoundError(f"File not found after conversion: {mp3_file}")

        # Show If Success
        print(get_time() + Fore.GREEN + "MP3 Successfully Downloaded: " + yt.title)
    except Exception as e:
        print(get_time() + Fore.RED + "Error downloading audio: " + videoUrl + " : " + str(e))

def convert_to_mp3(video_file, output_folder):
    try:
        # Create the output MP3 file path
        base_name = os.path.splitext(os.path.basename(video_file))[0]
        mp3_file = os.path.join(output_folder, f"{base_name}.mp3")

        # Use ffmpeg to convert the audio file to MP3 with 320 kbps bitrate
        command = ['ffmpeg', '-i', video_file, '-b:a', '320k', mp3_file]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Delete the original video file
        os.remove(video_file)

        print(get_time() + Fore.GREEN + "Converted To MP3 Successfully")
        return mp3_file
    except Exception as e:
        print(get_time() + Fore.RED + "Error converting to MP3: " + str(e))
        raise e

def add_metadata(file_path, yt, thumbnail_path):
    try:
        # Load the MP3 file
        audiofile = eyed3.load(file_path)

        # Ensure the file is valid
        if audiofile is None:
            raise Exception("Failed to load MP3 file for metadata editing.")

        # Initialize ID3 tag if it doesn't exist
        if audiofile.tag is None:
            audiofile.initTag()

        # Add basic metadata
        audiofile.tag.title = yt.title
        audiofile.tag.artist = yt.author

        # Add Album Art
        if thumbnail_path and os.path.exists(thumbnail_path):
            # Determine MIME type based on file extension
            if thumbnail_path.endswith(".jpg") or thumbnail_path.endswith(".jpeg"):
                mime_type = "image/jpeg"
            elif thumbnail_path.endswith(".png"):
                mime_type = "image/png"
            else:
                print(get_time() + Fore.YELLOW + "Unsupported image format: " + thumbnail_path)
                return

            # Read and embed the image
            with open(thumbnail_path, "rb") as img_file:
                image_data = img_file.read()
                audiofile.tag.images.set(3, image_data, mime_type, u"Cover")
        else:
            print(get_time() + Fore.YELLOW + "Thumbnail file not found: " + thumbnail_path)

        # Save the metadata
        audiofile.tag.save()
        print(get_time() + Fore.GREEN + "Metadata and album art added successfully.")
    except Exception as e:
        print(get_time() + Fore.RED + "Error adding metadata: " + str(e))

def download_thumbnail(videoUrl, imageOutputFolder):
    try:
        # Get Thumbnail link from video url
        yt = YouTube(videoUrl)
        id = yt.video_id
        # Use the id to get link to thumbnail image
        url = f"https://img.youtube.com/vi/{id}/maxresdefault.jpg"

        # Clean The Title From Unwanted Symbols
        cleanTitle = re.sub('[#%&\/<>*?$!\'\":@+=|]', '', yt.title)

        # Get Save Location
        savePath = os.path.join(imageOutputFolder, f"{cleanTitle}.jpg")

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in binary write mode and save the image
            with open(savePath, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(get_time() + Fore.GREEN + "Thumbnail Successfully Downloaded: " + yt.title)

            # Crop and resize the image to 1400x1400
            crop_image_to_square(savePath)
            return savePath
        else:
            print(get_time() + Fore.RED + "Failed to download thumbnail. Status code: " + response.status_code)
            return None
    except Exception as e:
        print(get_time() + Fore.RED + "Error downloading thumbnail: " + videoUrl + " : " + str(e))
        return None

def crop_image_to_square(image_path, output_size=(1400, 1400)):
    try:
        # Open the image
        img = Image.open(image_path)

        # Get the dimensions of the image
        width, height = img.size

        # Calculate the dimensions for a square crop
        min_dim = min(width, height)
        left = (width - min_dim) / 2
        top = (height - min_dim) / 2
        right = (width + min_dim) / 2
        bottom = (height + min_dim) / 2

        # Crop the image to a square
        img_cropped = img.crop((left, top, right, bottom))

        # Resize the cropped image to the desired output size
        img_resized = img_cropped.resize(output_size, Image.Resampling.LANCZOS)  # Updated here

        # Save the resized image (overwrite the original)
        img_resized.save(image_path)
        print(get_time() + Fore.GREEN + f"Image cropped and resized to {output_size[0]}x{output_size[1]}.")
    except Exception as e:
        print(get_time() + Fore.RED + "Error cropping image: " + str(e))
    
def main():
    # File containing YouTube URLs
    inputFile = "links.txt"  
    
    # Get script directory
    scriptDir = os.path.dirname(os.path.abspath(__file__))  
    
    # Set output folder for mp3
    audioOutputFolder = os.path.join(scriptDir, "downloads/audio")
    imageOutputFolder = os.path.join(scriptDir, "downloads/image")  
    
    os.makedirs(audioOutputFolder, exist_ok=True)
    os.makedirs(imageOutputFolder, exist_ok=True)
    
    with open(inputFile, "r") as file:
        urls = file.readlines()
    
    input(Fore.YELLOW + "Press Enter to start")
    for url in urls:
        url = url.strip()
        if url:
            print(get_time() + Fore.CYAN + "Download started for: " + url)
            download_audio(url, audioOutputFolder, imageOutputFolder)
            print(get_time() + Fore.YELLOW + "Moving To Next: \n ")
    print(get_time() + Fore.CYAN + "Everything Downloaded")
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
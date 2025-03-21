import os
import re
import requests
from pytubefix import YouTube

def download_audio(videoUrl, outputFolder):
    try:
        # Gets The Video From URL
        yt = YouTube(videoUrl)

        # Extracts Only Audio
        video = yt.streams.filter(only_audio=True).first()

        # Downloads The File
        outFile = video.download(output_path=outputFolder)

        # Save The File
        base, ext = os.path.splitext(outFile)
        new_file = base + '.mp3'
        os.rename(outFile, new_file)

        #Show If Success
        print(yt.title + " has been successfully downloaded.")
    except Exception as e:
        print(f"Error downloading {videoUrl}: {e}")

def download_thumbnail(videoUrl, outputFolder):
    try:
        # Get Thumbnail link from video url
        yt = YouTube(videoUrl)
        id = yt.video_id
        # use the id to get link to thumbnail image
        url = f"https://img.youtube.com/vi/{id}/maxresdefault.jpg"

        # Clean The Title From Unwanted Symbols
        cleanTitle = re.sub(r'[^a-zA-Z0-9\s]', '', yt.title)

        # Get Save Location
        savePath = f"{outputFolder}\\{cleanTitle}.png"

        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in binary write mode and save the image
            with open(savePath, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f"Image successfully downloaded and saved as {savePath}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    # File containing YouTube URLs
    inputFile = "links.txt"  
    
    # Get script directory
    scriptDir = os.path.dirname(os.path.abspath(__file__))  
    
    # Set output folder for mp3
    outputFolder = os.path.join(scriptDir, "downloads")  
    
    os.makedirs(outputFolder, exist_ok=True)
    
    with open(inputFile, "r") as file:
        urls = file.readlines()
    
    for url in urls:
        url = url.strip()
        if url:
            download_audio(url, outputFolder)
            download_thumbnail(url, outputFolder)
    
    #input("Press Enter to exit...")

if __name__ == "__main__":
    main()

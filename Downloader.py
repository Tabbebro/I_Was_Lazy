import os
import re
import requests
from pytubefix import YouTube
from colorama import init, Back, Fore, Style

init(convert=True)


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
        print(Fore.GREEN +"Mp3 Successfully Downloaded: " + Style.RESET_ALL + yt.title)
    except Exception as e:
        print(Fore.RED + "Error downloading audio: " + Style.RESET_ALL + videoUrl + " : " + e)


def download_thumbnail(videoUrl, outputFolder):
    try:
        # Get Thumbnail link from video url
        yt = YouTube(videoUrl)
        id = yt.video_id
        # use the id to get link to thumbnail image
        url = f"https://img.youtube.com/vi/{id}/maxresdefault.jpg"

        # Clean The Title From Unwanted Symbols
        cleanTitle = re.sub('[#%&\/<>*?$!\'\":@+=|]', '', yt.title)

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
            print(Fore.GREEN + "Image Successfully Downloaded: " + Style.RESET_ALL + yt.title)
        else:
            print(Fore.RED + "Failed to download image. Status code: " + Style.RESET_ALL + response.status_code)
    except Exception as e:
        print(Fore.RED + "Error downloading image: " + Style.RESET_ALL + videoUrl + " : " + e)
    
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
    
    for url in urls:
        url = url.strip()
        if url:
            print("Download started for: " + url)
            #download_audio(url, audioOutputFolder)
            download_thumbnail(url, imageOutputFolder)
            print(Fore.YELLOW + "Moving To Next: \n " + Style.RESET_ALL)
    print("Everything Downloaded")
    #input("Press Enter to exit...")

if __name__ == "__main__":
    main()

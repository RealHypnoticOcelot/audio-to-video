import ffmpeg
import argparse
from pathlib import Path
import mutagen
from mutagen.id3 import ID3, TIT2
import tempfile
from PIL import Image, ImageDraw
import io

parser = argparse.ArgumentParser()
parser.add_argument("file_path", type=Path)

p = parser.parse_args()

files = []
if p.file_path.exists():
    if p.file_path.is_dir():
        for i in p.file_path.iterdir():
            if i.suffix == ".mp3":
                files.append(i)
    elif not p.file_path.is_dir() and (p.file_path.suffix == ".mp3"):
        files.append(p.file_path)
else:
    raise Exception("File does not exist!")

if files == []:
    raise Exception("No valid files selected! Select an .mp3 file, or a folder containing .mp3 files.")

useAPIC = (True if input("Use ID3 tags for cover art? y/n: ") == "y" else False)
customCover = False
useID3 = False
manualID3 = False
manulTrack = False
if not useAPIC:
    customCover = (True if input("Use a custom image for cover art(this will apply to all selected files)? y/n: ") == "y" else False)
    if customCover:
        while customCover == True:
            imagepath = Path(input("Path to image file?: "))
            customCover = (imagepath if imagepath.exists() else True)
            print("Path does not exist!") if customCover == True else None
    elif not customCover:
        useID3 = (True if input("Use ID3 tags for placeholder cover(will generate a cover with track information)? y/n: ") == "y" else False)
        if not useID3:
            manualID3 = (True if input("Manually input artist and album information? y/n: ") == "y" else False)
            if manualID3:
                artistName = input("Artist Name: ")
                albumName = input("Album Name: ")
                manualTrack = (True if input("Manually input track information(will use filenames if not)? y/n: ") == "y" else False)

for audiofile in files:
    audio = ffmpeg.input(audiofile)
    metadata = mutagen.File(audiofile).tags
    # Wrap everything in tempfile; FFmpeg expects file paths, and
    # doesn't support bytes, so data pulled from ID3 has to be
    # written to a tempfile. Even if the tempfile is unused(if APIC data
    # isn't present, or isn't in use), it's more efficient than
    # having multiple FFmpeg commands for different cases
    with tempfile.NamedTemporaryFile() as fp:
        image = None # Define it here, and convert to a different ffmpeg input based on which options are selected
        if metadata.getall("APIC") != [] and useAPIC:
            fp.write(metadata.getall("APIC")[0].data) # Create a temporary file for the cover art from the ID3 tags of the audio
            fp.flush()
            image = ffmpeg.input(fp.name, loop=1, framerate=2)
            print(fp.name)
            breakpoint()
        else: # If no APIC data, or if APIC tags aren't being used
            if customCover:
                image = ffmpeg.input(customCover, loop=1, framerate=2)
            else: # Create placeholder image for the file
                placeholder = Image.new(mode="RGB", size=(512, 512), color="#fff")
                albuminfo = ImageDraw.Draw(im=placeholder)
                text = []
                if useID3:
                    text.append(f"Artist: {metadata.getall('TPE1')[0]}" if metadata.getall('TPE1')[0] != "None" else "")
                    text.append(f"Album: {metadata.getall('TALB')[0]}" if metadata.getall('TALB')[0] != "None" else "")
                    text.append(f"Track: {metadata.getall('TIT2')[0]}" if metadata.getall('TIT2')[0] != "None" else "")
                if manualID3:
                    text.append(f"Artist: {artistName}")
                    text.append(f"Album: {albumName}")
                    if manualTrack:
                        text.append(f"Track: {input(f"Track Name for \'{audiofile.name}\': ")}")
                if text == []:
                    text.append(audiofile.name)
                text = '\n'.join(text)
                albuminfo.multiline_text(xy=(256, 256), text=text, fill="#000", font_size=16, anchor="mm")
                output_buffer = io.BytesIO()
                placeholder.save(output_buffer, "png")
                fp.write(output_buffer.getvalue())
                fp.flush()
                image = ffmpeg.input(fp.name, loop=1, framerate=2)
        imagevideo = (
            ffmpeg
            .output(
                image,
                audio['a'],
                f"{audiofile.parent}/{audiofile.stem}.mkv", # won't output to .mp4 for weird codec reasons, at least on my machine
                tune="stillimage",
                vf="scale=-1:720",
                t=ffmpeg.probe(audiofile)["format"]["duration"], # duration of the audio file
            )
            .run()
        )

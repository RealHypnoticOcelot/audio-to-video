# audio-to-video
###### Convert .mp3 files to videos!

## How to use:

### (Optional: create a virtual environment)
Navigate to the directory the script was downloaded in, and run the following command:
```python
python3 -m venv env && source env/bin/activate
```
### (Required Steps)
Install the dependencies required with the following command:

```python
pip3 install -r requirements.txt
```

Install ffmpeg at [ffmpeg.org](https://www.ffmpeg.org/download.html), if you don't have it already.

If you're on MacOS and have brew installed, you can just run `brew install ffmpeg`.

```python
python3 main.py [file_path]
```
`[file_path]` must be the path to either an .mp3 file or a folder containing .mp3 files.
Answer the prompts it gives you, and the script will output your files in the same directory!

## Current Feature List:

- Select custom image for the video to use

- Create placeholder image using ID3 tags or manual input


###### If you have any issues, questions, concerns or suggestions, [DM me](<https://discord.com/users/404053132910395393>) or create an issue

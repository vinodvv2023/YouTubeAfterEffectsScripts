# Simple tool for Youtubers to create subtitles using AfterEffect, Open AI Whisper to Transcript 

A simple tool for Youtubers who want to create subtitles for faceless video and videos which are ready for upload to YouTube. This tool is not full automation since you will need to check the transcripted script files for transcripted text corrections, if needed. Helps in saving time to manually create a text layer on the timeline. 

Automatically transcribe audio from videos and generate After Effects `.jsx` marker scripts for both sentences and words. Perfect for users who want to sync audio with text effects in After Effects using Monkey Scripts (available on [AEscripts.com](https://aescripts.com/)).

## Features

- Batch process videos from the `Videos/` folder.
- Generates transcripts and After Effects `.jsx` files with markers for sentences and words.
- Output organized by video in the `Output/` directory.

## Project Structure

```
aftereffect-transcriber/
│
├── process_videos.py
├── requirements.txt
├── README.md
├── .gitignore
├── Videos/ # Input videos
└── Output/ # Output folder
```
## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/vinodvv2023/YouTubeAfterEffectsScripts.git
    cd aftereffect-transcriber
    ```

2. Install dependencies:

-  The generated jsx scripts work on Adobe After Effect 2019 onwards, you will need to install AdobeExtendScriptToolkit3.5.0-mul

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Place your video files in the `Videos/` folder.
2. Run the script:
    ```bash
    python process_videos.py
    ```
3. Find the output in the `Output/` folder, organized by video name. Each folder contains:
    - The processed video (if applicable)
    - Sentence-level `.jsx` marker file
    - Word-level `.jsx` marker file

4. To run JSX files in Adobe After Effects, you can use the following methods:

- Using the File Menu:
- Open Adobe After Effects.
- Go to File > Scripts > Run Script File...
- Navigate to your .jsx file and select it.
- The script will execute in the current After Effects project.

- DO NOT Place Scripts in the Script Folder: Since the generated .jsx files are transcripted for each video.


## Requirements

See `requirements.txt` for Python dependencies.

## Notes

- This script is designed for users who want to use Monkey Scripts in After Effects for advanced text/audio syncing.
- For more on Monkey Scripts, visit [AEscripts.com](https://aescripts.com/).

## Suggestions
- Your script uses word_timestamps=True in Whisper, which is only supported in some models. If you get errors, try MODEL_SIZE = "medium" or "large".

## License

MIT License
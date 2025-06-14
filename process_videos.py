import os
import shutil
import whisper
import torch

# usage -  python .\process_videos.py

# CONFIGURATION
SOURCE_FOLDER = "videos"
OUTPUT_FOLDER = "output"
MODEL_SIZE = "base" #"base"  # or "small", "medium", "large"
USE_CUDA = False  # Set to False to force CPU

def get_device():
    if USE_CUDA and torch.cuda.is_available():
        print("Using CUDA (GPU)")
        return "cuda"
    print("Using CPU")
    return "cpu"

def move_video_to_folder(video_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    new_path = os.path.join(out_dir, os.path.basename(video_path))
    shutil.move(video_path, new_path)
    return new_path

def transcribe_video(model, video_path):
    print(f"Transcribing: {video_path}")
    result = model.transcribe(video_path, word_timestamps=True)
    return result  # Return the full result, not just text

def generate_jsx_script(segments, jsx_path):
    jsx_lines = [
        'var comp = app.project.activeItem;',
        'if (!comp || !(comp instanceof CompItem)) { alert("Please select a composition."); }',
        'var fadeDuration = 15;',  # frames
        'var bgOpacity = 80;',
        'var fontSize = 80;',
        'var yPos = comp.height * 0.85;',
        'var margin = 40;',
        'var textColor = [1,1,1];',
        'var bgColor = [0,0,0];',
        'var compWidth = comp.width;',
        'var compHeight = comp.height;',
    ]
    for i, seg in enumerate(segments):
        safe_text = seg['text'].replace('"', '\\"')
        start = seg['start']
        end = seg['end']
        jsx_lines += [
            f'// Sentence {i+1}',
            f'var textLayer = comp.layers.addText("{safe_text}");',
            'textLayer.property("Position").setValue([compWidth/2, yPos]);',
            f'var marker = new MarkerValue("{safe_text}");',
            f'marker.duration = {end} - {start};',
            f'adjLayer.property("Marker").setValueAtTime({start}, marker);',
            'var textProp = textLayer.property("Source Text");',
            'var textDocument = textProp.value;',
            'textDocument.fontSize = fontSize;',
            'textDocument.fillColor = textColor;',
            'textDocument.justification = ParagraphJustification.CENTER_JUSTIFY;',
            'textProp.setValue(textDocument);',
            'var bgLayer = comp.layers.addSolid(bgColor, "BG", compWidth, fontSize*2, 1);',
            'bgLayer.property("Transform").property("Position").setValue([compWidth/2, yPos]);',
            'bgLayer.property("Transform").property("Opacity").setValue(bgOpacity);',
            'bgLayer.moveAfter(textLayer);',
            f'textLayer.inPoint = {start};',
            f'bgLayer.inPoint = {start};',
            f'textLayer.outPoint = {end};',
            f'bgLayer.outPoint = {end};',
            f'textLayer.opacity.setValueAtTime({start}, 0);',
            f'textLayer.opacity.setValueAtTime({start} + (fadeDuration/comp.frameRate), 100);',
            f'textLayer.opacity.setValueAtTime({end} - (fadeDuration/comp.frameRate), 100);',
            f'textLayer.opacity.setValueAtTime({end}, 0);',
            f'bgLayer.opacity.setValueAtTime({start}, 0);',
            f'bgLayer.opacity.setValueAtTime({start} + (fadeDuration/comp.frameRate), bgOpacity);',
            f'bgLayer.opacity.setValueAtTime({end} - (fadeDuration/comp.frameRate), bgOpacity);',
            f'bgLayer.opacity.setValueAtTime({end}, 0);',
        ]
    print(f"Generated JSX script: {jsx_path}")
    with open(jsx_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(jsx_lines))
    

def generate_jsx_script_word_by_word(segments, jsx_path):
    jsx_lines = [
        'var comp = app.project.activeItem;',
        'if (!comp || !(comp instanceof CompItem)) { alert("Please select a composition."); }',
        'var fadeDuration = 10;',
        'var bgOpacity = 80;',
        'var fontSize = 80;',
        'var yPos = 200;',
        'var margin = 40;',
        'var textColor = [1,1,1];',
        'var bgColor = [0,0,0];',
        'var compWidth = comp.width;',
        'var compHeight = comp.height;',
    ]
    for i, seg in enumerate(segments):
        words = seg.get('words', [])
        if not words:
            continue
        total_chars = sum(len(w['word']) for w in words)
        bg_width_expr = f"Math.min(compWidth, {60 * total_chars + 100})"
        bg_height = int(1.8 * 80)
        seg_start = words[0]['start']
        seg_end = words[-1]['end']
        jsx_lines += [
            f'// Sentence {i+1} background',
            f'var bgLayer = comp.layers.addSolid(bgColor, "BG_{i+1}", {bg_width_expr}, {bg_height}, 1);',
            'bgLayer.property("Transform").property("Position").setValue([compWidth/2, yPos]);',
            'bgLayer.property("Transform").property("Opacity").setValue(bgOpacity);',
            f'bgLayer.inPoint = {seg_start};',
            f'bgLayer.outPoint = {seg_end};',
            f'bgLayer.opacity.setValueAtTime({seg_start}, 0);',
            f'bgLayer.opacity.setValueAtTime({seg_start} + (fadeDuration/comp.frameRate), bgOpacity);',
            f'bgLayer.opacity.setValueAtTime({seg_end} - (fadeDuration/comp.frameRate), bgOpacity);',
            f'bgLayer.opacity.setValueAtTime({seg_end}, 0);',
        ]
        word_spacing = 60
        total_width = (len(words) - 1) * word_spacing
        for j, word in enumerate(words):
            safe_word = word['word'].replace('"', '\\"')
            w_start = word['start']
            w_end = word['end']
            x_pos = f'compWidth/2 - {int(total_width/2)} + {j}*{word_spacing}'
            jsx_lines += [
                f'// Word {j+1} of sentence {i+1}',
                f'var textLayer = comp.layers.addText("{safe_word}");',
                f'textLayer.property("Position").setValue([{x_pos}, yPos]);',
                f'var marker = new MarkerValue("{safe_word}");',
                f'marker.duration = {w_end} - {w_start};',
                f'adjLayer.property("Marker").setValueAtTime({w_start}, marker);',
                'var textProp = textLayer.property("Source Text");',
                'var textDocument = textProp.value;',
                'textDocument.fontSize = fontSize;',
                'textDocument.fillColor = textColor;',
                'textDocument.justification = ParagraphJustification.CENTER_JUSTIFY;',
                'textProp.setValue(textDocument);',
                f'textLayer.inPoint = {w_start};',
                f'textLayer.outPoint = {w_end};',
                f'textLayer.opacity.setValueAtTime({w_start}, 0);',
                f'textLayer.opacity.setValueAtTime({w_start} + (fadeDuration/comp.frameRate), 100);',
                f'textLayer.opacity.setValueAtTime({w_end} - (fadeDuration/comp.frameRate), 100);',
                f'textLayer.opacity.setValueAtTime({w_end}, 0);',
                'textLayer.moveBefore(bgLayer);',
            ]
        jsx_lines += [
            'yPos += fontSize + margin;',
        ]
    print(f"Generated JSX script (word by word): {jsx_path}")
    with open(jsx_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(jsx_lines))
    

def main():
    device = get_device()
    model = whisper.load_model(MODEL_SIZE, device=device)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    for filename in os.listdir(SOURCE_FOLDER):
        if not filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            continue
        video_path = os.path.join(SOURCE_FOLDER, filename)
        base_name = os.path.splitext(filename)[0]
        out_dir = os.path.join(OUTPUT_FOLDER, base_name)
        new_video_path = move_video_to_folder(video_path, out_dir)
        result = transcribe_video(model, new_video_path)
        segments = result['segments']
        transcript_path = os.path.join(out_dir, f"{base_name}.txt")
        with open(transcript_path, "w", encoding="utf-8") as f:
            for seg in segments:
                f.write(seg['text'].strip() + "\n")
        jsx_path = os.path.join(out_dir, f"{base_name}.jsx")
        generate_jsx_script(segments, jsx_path)
        jsx_path_word = os.path.join(out_dir, f"{base_name}_word.jsx")
        generate_jsx_script_word_by_word(segments, jsx_path_word)
        print(f"Processed: {filename}")

if __name__ == "__main__":
    main()
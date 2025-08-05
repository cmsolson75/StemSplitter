#!/usr/bin/env python3
"""
Generate audio test files in various formats using ffmpeg
"""

import subprocess
import sys
from pathlib import Path

def run_ffmpeg(input_file, output_file, codec_args):
    """Run ffmpeg command with error handling"""
    cmd = ["ffmpeg", "-i", str(input_file)] + codec_args + [str(output_file), "-y"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✓ Created {output_file.name}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to create {output_file.name}: {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Please install ffmpeg first.")
        return False

def generate_audio_formats():
    """Generate various audio formats for testing"""
    assets_dir = Path("tests/e2e/assets")
    base_file = assets_dir / "test_audio.wav"
    
    # Create assets directory if it doesn't exist
    assets_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if base file exists
    if not base_file.exists():
        print(f"Error: Base audio file {base_file} not found")
        print("Please ensure you have a test_audio.wav file in the assets directory")
        return False
    
    print(f"Generating audio formats from {base_file.name}...")
    
    # Define format conversions
    formats = [
        ("test_audio.mp3", ["-codec:a", "libmp3lame", "-b:a", "128k"]),
        ("test_audio.aif", ["-codec:a", "pcm_s16be"]),
        ("test_audio.aiff", ["-codec:a", "pcm_s16be"]),
        ("test_audio.m4a", ["-codec:a", "aac", "-b:a", "128k"]),
        ("test_audio.flac", ["-codec:a", "flac"]),
        ("test_audio.ogg", ["-codec:a", "libvorbis", "-b:a", "128k"]),
    ]
    
    success_count = 0
    total_count = len(formats)
    
    for filename, codec_args in formats:
        output_file = assets_dir / filename
        if run_ffmpeg(base_file, output_file, codec_args):
            success_count += 1
    
    print(f"\nGeneration complete: {success_count}/{total_count} files created successfully")
    
    # List generated files
    print("\nGenerated files:")
    for file_path in sorted(assets_dir.glob("test_audio.*")):
        size = file_path.stat().st_size
        print(f"  {file_path.name:15} ({size:,} bytes)")
    
    return success_count == total_count

if __name__ == "__main__":
    success = generate_audio_formats()
    sys.exit(0 if success else 1)
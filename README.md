# mai2dat
Convert any video to CRIWARE's video file format.

## Installation
mai2dat uses [uv](https://docs.astral.sh/uv/) as the package manager. If you don't have it, please run the following command:  
Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`  
Linux & macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`  
  
For video processing, mai2dat uses [ffmpeg](https://ffmpeg.org/). To install:  
Windows: `winget install --id=Gyan.FFmpeg -e`  
macOS: `brew install ffmpeg` (requires Homebrew)  
Linux: uhh. i assume you know what to do.  
  
If you got all of the requirements satisfied, install the dependencies by:  
```
uv sync
```
  
## Usage
```
uv run main.py <input file> <output file> [optional flags]
```  
Optional flags:  
- `--ffmpeg-path`: Specify the path to ffmpeg executable. (Default: ffmpeg)
- `--ffprobe-path`: Specify the path to ffprobe executable. (Default: ffprobe)
- `--key`: Specify the USM encryption key, in hexadecimal format. (Default: 0x7F4551499DF55E68)
- `--usm-version`: Specify the USM version to use. (Default: 16777984)
  
Or if you are on Windows, you can just drag the video file you want to convert onto "run.bat", and mai2dat will generate a "(original file name).dat" file in the same directory.  
Made with ❤️ by 0x24a
from typing import Iterable
from subprocess import STDOUT, Popen, PIPE
from rich import print
from rich.live import Live
from rich.text import Text
from wannacri.wannacri import Vp9, Usm, OpMode
from os import path
import shutil
from tempfile import mkdtemp
from typer import run
from time import time

__VERSION__ = "1.0.0"

def check_ffmpeg(ffmpeg_path: str = "ffmpeg") -> bool:
    try:
        assert Popen([ffmpeg_path, "-version"], stdout=PIPE, stderr=PIPE).wait() == 0
        return True
    except Exception as _:
        return False

def check_ffprobe(ffprobe_path: str = "ffprobe") -> bool:
    try:
        assert Popen([ffprobe_path, "-version"], stdout=PIPE, stderr=PIPE).wait() == 0
        return True
    except Exception as _:
        return False

class FFMpegTask:
    def __init__(self, ffmpeg_path: str = "ffmpeg", *args: str):
        self.ffmpeg_path = ffmpeg_path
        self.args = args
        self.return_code = -1

    def run(self) -> Iterable[str]:
        try:
            stream = Popen([self.ffmpeg_path] + list(self.args), stdout=PIPE, stderr=STDOUT)
            assert stream.stdout is not None
            buffer = bytes()
            while True:
                output = stream.stdout.read(1)
                if output == b'' and stream.poll() is not None:
                    break
                if output == b"\r":
                    if buffer.startswith(b"frame"):
                        yield buffer.decode("utf-8").strip()
                    buffer = bytes()
                else:
                    buffer += output
            self.return_code = stream.wait()
        except Exception as _:
            self.return_code = 1

def main(
    source: str,
    destination: str,
    ffmpeg_path: str = "ffmpeg",
    ffprobe_path: str = "ffprobe",
    key: str = "0x7F4551499DF55E68", # Hello miamia xd
    usm_version: int = 16777984 # miamia xd again
):
    print(f"[bold][cyan]mai2dat {__VERSION__}[/cyan][/bold]")
    print("[cyan]Convert any video to CRIWARE's video file format.[/cyan]")
    print()
    if not path.exists(source):
        print("[red]ˣ  Source file not found.[/red]")
        exit(1)
    try:
        int(key, 16)
    except ValueError:
        print("[red]ˣ  Invalid key format. It should be a hexadecimal string.[/red]")
        exit(1)
    print("[yellow](1/7)[/yellow] Checking FFMpeg... ", end="")
    if check_ffmpeg(ffmpeg_path):
        print("[green]OK[/green]")
    else:
        print("[red]NG[/red]")
        print("[red]ˣ  Failed to find FFMpeg executable.[/red]")
        print("[red]   Please install FFMpeg from https://ffmpeg.org/download.html[/red]")
        print("[red]   Or specify the path to the executable using the --ffmpeg-path option.[/red]")
        exit(1)
    print("[yellow](2/7)[/yellow] Checking FFProbe... ", end="")
    if check_ffprobe(ffprobe_path):
        print("[green]OK[/green]")
    else:
        print("[red]NG[/red]")
        print("[red]ˣ  Failed to find FFProbe executable.[/red]")
        print("[red]   Please install FFProbe from https://ffmpeg.org/download.html[/red]")
        print("[red]   Or specify the path to the executable using the --ffprobe-path option.[/red]")
        exit(1)
    print("[yellow](3/7)[/yellow] Copying file to the temporary folder... ", end="")
    temp_folder = mkdtemp()
    shutil.copy(source, path.join(temp_folder, path.basename(source)))
    print("[green]OK[/green]")
    print("[yellow](4/7)[/yellow] Converting the source file to VP9 (IVF) encoding...")
    task = FFMpegTask(
        ffmpeg_path,
        "-i", path.join(temp_folder, path.basename(source)),
        "-c:v", "libvpx-vp9",
        "-vf", "crop=min(iw\\,ih):min(iw\\,ih),scale=1080:1080",
        path.join(temp_folder, "source.ivf")
    )
    with Live(Text(""), refresh_per_second=16) as live:
        live.update("-  Waiting for FFMpeg startup...")
        start_time = time()
        for chunk in task.run():
            # Update the display content
            live.update(f"-  {chunk}")
        end_time = time()
        if task.return_code != 0:
            print("[red]ˣ  Failed to convert the source file to VP9 (IVF) encoding.[/red]")
            print("[red]   Please check the source file and try again.[/red]")
            print("[red]   Or specify the path to the executable using the --ffmpeg-path option.[/red]")
            exit(1)
        else:
            live.update(f"-  [green]Finished in {end_time - start_time:.2f} seconds[/green]")
    with Live(Text(""), refresh_per_second=16) as live:
        live.update("[bold][yellow](5/7)[/yellow][/bold] Converting to USM (.dat)... Pending")
        video = Vp9(path.join(temp_folder, "source.ivf"), ffprobe_path=ffprobe_path) # pyright: ignore[reportAbstractUsage]
        usm = Usm(videos=[video], audios=None, key=int(key, 16), version=usm_version)
        chunk_n = 1
        with open(path.join(temp_folder, "target.usm"), "wb") as f:
            for chunk in usm.stream(OpMode.ENCRYPT, encoding="shift-jis"):
                live.update(f"[bold][yellow](5/7)[/yellow][/bold] Converting to USM (.dat)... Chunk {chunk_n}")
                chunk_n += 1
                f.write(chunk)
        live.update("[bold][yellow](5/7)[/yellow][/bold] Converting to USM (.dat)... [green]Done[/green]")
    print("[yellow](6/7)[/yellow] Copying back the result... ", end="")
    shutil.copy(path.join(temp_folder, "target.usm"), destination)
    print("[green]OK[/green]")
    print("[yellow](7/7)[/yellow] Cleaning up... ", end="")
    shutil.rmtree(temp_folder)
    print("[green]OK[/green]")
    print(f"[green]Successfully converted {source} to {destination}.[/green]")

if __name__ == "__main__":
    run(main)
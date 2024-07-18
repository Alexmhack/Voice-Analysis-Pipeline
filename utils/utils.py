import os
import json
import requests
import urllib
import contextlib
import wave
import cgi
import shutil
import subprocess

from typing import Union
from pydub import AudioSegment


def _is_correct_mime_type(target_file: str) -> bool:
    """Use magic mime to check file contents are of type audio/video"""
    try:
        probe_output = f"/tmp/{os.path.basename(target_file)}.json"
        os.system(
            f"ffprobe -loglevel error -show_entries stream=codec_type -of json {target_file} > {probe_output}"
        )
        data = {}
        with open(probe_output) as fd:
            data = json.load(fd)
        os.remove(probe_output)
        return any(
            stream.get("codec_type", None) in ["audio", "video"]
            for stream in data.get("streams", [])
        )

    except Exception:
        return False


def get_wav_duration(wav):
    with contextlib.closing(wave.open(wav, "r")) as fd:
        frames = fd.getnframes()
        rate = fd.getframerate()
        return frames / float(rate)


def _is_complete_wav_file(target_file: str) -> bool:
    """Uses duration of wav file to check if wav file is complete"""
    try:
        get_wav_duration(target_file)
        return True
    except Exception:
        return False


## GENERAL UTILS
def download_audio_from_url(
    audio_url, working_dir, target_file_name=None, custom_get=None
) -> Union[bool, str]:
    # TODO can we use tmp file for this ?
    try:
        resp = (
            requests.get(audio_url, verify=False)
            if custom_get is None
            else custom_get(audio_url)
        )
        if resp.status_code not in [200, 201]:
            print(f"File does not exist on Server {resp.status_code}")
            return False
        if not resp.content:
            print(f"No contents found in audio file: {audio_url}")
            return False

        try:
            if (
                "content-disposition" in resp.headers
                or "Content-Disposition" in resp.headers
                and target_file_name is None
            ):
                ctd = resp.headers.get("content-disposition") or resp.headers.get(
                    "Content-Disposition"
                )
                value, params = cgi.parse_header(ctd)
                if "filename" in params:
                    target_file_name = os.path.basename(
                        urllib.parse.urlparse(params.get("filename")).path
                    )
        except Exception as e:
            print(f"Error while getting filename from content dispositoin {e}")

        _target_file_name = target_file_name
        if not _target_file_name:
            _target_file_name = os.path.basename(urllib.parse.urlparse(resp.url).path)
            path_data = _target_file_name.strip().split(".")
            if len(path_data) == 1 or path_data[-1] not in ["wav", "mp3"]:
                content_type = resp.headers.get("Content-Type") or resp.headers.get(
                    "content-type"
                )
                if content_type:
                    if "wav" in content_type:
                        _target_file_name = f"{_target_file_name}.wav"
                    elif "mp3" in content_type:
                        _target_file_name = f"{_target_file_name}.mp3"

        target_file = os.path.join(working_dir, _target_file_name)

        with open(target_file, "wb") as fd:
            fd.write(resp.content)

        if (
            os.path.splitext(target_file)[1] != ".wav"
            and _is_correct_mime_type(target_file)
        ) or _is_complete_wav_file(target_file):
            return target_file
        print("incomplete file")
        os.remove(target_file)
        return False
    except Exception as e:
        print(f"Unable to download audio file: {audio_url}, exception {e}")
        return False


def get_wav_duration(wav):
    try:
        with contextlib.closing(wave.open(wav, "r")) as fd:
            frames = fd.getnframes()
            rate = fd.getframerate()
            return frames / float(rate)
    except wave.Error as e:
        print(f"error occured while finding duration through wave {e}")

    try:
        sound = AudioSegment.from_file(wav)
        return sound.duration_seconds
    except Exception as e:
        return 0


def clean_and_return(duration, wav_file, file):
    # remove original file
    try:
        if wav_file != file:
            os.remove(file)
    except Exception as e:
        pass
    return {"success": True, "duration": duration, "output": wav_file}


def get_num_channels(wav):
    latest_exception = None
    try:
        s = AudioSegment.from_wav(wav)
        return s.channels
    except Exception as e:
        latest_exception = e

    try:
        s = AudioSegment.from_mp3(wav)
        return s.channels
    except Exception as e:
        latest_exception = e

    raise latest_exception


def convert_to_wav(audio_path: str) -> str:
    sample_rate = 8000
    channels = 1
    filename = os.path.basename(audio_path)
    base_file, ext = os.path.splitext(filename)
    out_file = f"/tmp/{os.path.basename(filename)}"

    if ext == ".wav":
        try:
            file_channels = get_num_channels(f"/tmp/{filename}")
        except Exception as e:
            os.remove(f"/tmp/{filename}")
            return {
                "success": False,
                "msg": f"Error getting file channels, error -> {e}",
            }
    else:
        file_channels = channels

    if ext != ".wav" or file_channels != channels:
        out_file = f"/tmp/{base_file}_converted.wav"
        command = (
            f"ffmpeg -y -i '/tmp/{filename}' -ar {sample_rate} -ac {channels} '{out_file}'"
            if sample_rate
            else f"ffmpeg -y -i '/tmp/{filename}' -ac {channels} '{out_file}'"
        )

        completed_process = subprocess.run(command, shell=True)
        if completed_process.returncode != 0:
            os.remove(f"/tmp/{filename}")
            return {"success": False, "msg": "Not able to convert uploaded file to wav"}

        duration = None  # get_wav_duration(out_file)
        return clean_and_return(duration, wav_file=out_file, file=f"/tmp/{filename}")

    if out_file is not None and os.path.normpath(
        f"/tmp/{filename}"
    ) != os.path.normpath(out_file):
        shutil.copyfile(f"/tmp/{filename}", out_file)

        duration = None  # get_wav_duration(out_file)
        return clean_and_return(duration, wav_file=out_file, file=f"/tmp/{filename}")

    duration = None  # get_wav_duration(out_file)
    return clean_and_return(duration, wav_file=out_file, file=f"/tmp/{filename}")

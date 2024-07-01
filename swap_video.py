import os
import subprocess
from facefusion.ffmpeg import run_ffmpeg
from workflow.update_settings import update_config
from workflow.utils import get_image_paths
from facefusion import core
from tqdm import tqdm
import re
from typing import List
from facefusion import config
from facefusion.vision import count_video_frame_total
from termcolor import colored

def get_duration(input_path: str) -> float:
    if not os.path.isfile(input_path):
        print("Input file does not exist.")
        return None

    # 获取视频时长
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    try:
        total_duration = float(result.stdout)
    except ValueError:
        print("Error reading total duration of the video.")
        print(result.stdout.decode())
        return None
    return total_duration

def split_video_by_seconds(input_path: str, output_dir: str, segment_duration: int) -> bool:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.isfile(input_path):
        print("Input file does not exist.")
        return None

    total_duration = get_duration(input_path)
    if total_duration is None:
        return None

    input_file_name_without_extension = os.path.splitext(os.path.basename(input_path))[0]
    parts = []
    # 生成分割命令并调用run_ffmpeg
    current_time = 0
    index = 0
    segments = int(total_duration // segment_duration) + 1
    with tqdm(total=segments, desc="Splitting Video") as pbar:
        while current_time < total_duration:
            output_file = os.path.join(output_dir, f'{input_file_name_without_extension}_part{index:04d}.mp4').replace('\\', '/')
            parts.append(output_file)
            args = ['-ss', str(current_time), '-i', input_path, '-t', str(segment_duration), '-c', 'copy', output_file]
            process = subprocess.Popen(['ffmpeg'] + args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Failed to process segment starting at {current_time} seconds")
                print(stderr.decode())
                return
            current_time += segment_duration
            index += 1
            pbar.update(1)

    return parts

def get_frame_rate_and_total_frames(input_path: str):
    result = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames,r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', input_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    output = result.stdout.decode().split()
    if len(output) < 2:
        raise ValueError("Error reading video information.")
    
    # 解析帧率
    frame_rate_str = output[0]
    match = re.match(r"(\d+)/(\d+)", frame_rate_str)
    if match:
        num = int(match.group(1))
        denom = int(match.group(2))
        frame_rate = num / denom
    else:
        frame_rate = float(frame_rate_str)
    
    # 解析总帧数
    total_frames_str = output[1]
    if total_frames_str.isdigit():
        total_frames = int(total_frames_str)
    else:
        match = re.match(r"(\d+)/(\d+)", total_frames_str)
        if match:
            num = int(match.group(1))
            denom = int(match.group(2))
            total_frames = num // denom
        else:
            total_frames = int(total_frames_str)
    
    return frame_rate, total_frames

def split_video_by_frames(input_path: str, output_dir: str, segment_frames: int) -> bool:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.isfile(input_path):
        print("Input file does not exist.")
        return False

    # 获取视频总帧数和帧率
    try:
        frame_rate, total_frames = get_frame_rate_and_total_frames(input_path)
    except ValueError as e:
        print(e)
        return False

    input_file_name_without_extension = os.path.splitext(os.path.basename(input_path))[0]
    parts = []
    # 生成分割命令并调用run_ffmpeg
    current_frame = 0
    index = 0
    segments = (total_frames // segment_frames) + 1
    with tqdm(total=segments, desc="Splitting Video") as pbar:
        while current_frame < total_frames:
            output_file = os.path.join(output_dir, f'{input_file_name_without_extension}_part{index:04d}.mp4').replace('\\', '/')
            parts.append(output_file)
            start_time = current_frame / frame_rate
            args = ['-ss', str(start_time), '-i', input_path, '-frames:v', str(segment_frames), '-c', 'copy', output_file]
            process = subprocess.Popen(['ffmpeg'] + args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                print(f"Failed to process segment starting at frame {current_frame}")
                print(stderr.decode())
                return False
            current_frame += segment_frames
            index += 1
            pbar.update(1)

    return parts

def merge_videos(video_paths: List[str], output_path: str) -> bool:
    if not video_paths:
        print("No video paths provided.")
        return False

    # 创建一个临时文本文件，用于存储要合并的视频文件列表
    list_file_path = 'temp_video_list.txt'
    with open(list_file_path, 'w') as list_file:
        for video_path in video_paths:
            if not os.path.isfile(video_path):
                print(f"File does not exist: {video_path}")
                return False
            list_file.write(f"file '{os.path.abspath(video_path)}'\n")

    # 使用FFmpeg合并视频
    args = ['-f', 'concat', '-safe', '0', '-i', list_file_path, '-c', 'copy', output_path]
    success = run_ffmpeg(args)

    # 删除临时文件
    # os.remove(list_file_path)

    if not success:
        print("Failed to merge videos.")
    return success

def main():
    src_dir = 'D:/test_faces/source/yy'.replace('\\', '/')
    target_video_path = "D:\Download\Movie\KIDM\KIDM-460-1.mp4".replace('\\', '/')
    # target_video_path = 'F:/test_faces/output/test_full.mp4'.replace('\\', '/')

    temp_directory = 'D:/test_faces/output/KIDM-460-1'.replace('\\', '/')
    output_dir = 'D:/test_faces/output/KIDM-460-1'.replace('\\', '/')
    config_path = 'D:/aitools/facefusion/facefusion.ini'.replace('\\', '/')
    # segment_duration_in_seconds = 24
    segment_frames = 10000
    src_limit = 100

    src_paths, cnt = get_image_paths(src_dir, src_limit)
    tqdm.write(f"样本数量：{cnt}")
    if cnt == 0:
        tqdm.write("样本数量为0，退出")
        exit()

    total_frames = count_video_frame_total(target_video_path)

    segements = []
    for start_frame in range(0, total_frames, segment_frames):
        end_frame = min(start_frame + segment_frames - 1, total_frames - 1)
        segements.append((start_frame, end_frame))

    outputs = []
    for index, segement in enumerate(segements):
        seg_output = os.path.join(output_dir, f'seg[{segement[0]}-{segement[1]}].mp4')
        tqdm.write(colored(f'处理视频片段 {index+1}/{len(segements) } [{segement[0]}-{segement[1]}], 临时文件：{seg_output}', 'green'))
        updates = [
            ('general', 'source_paths', src_paths),
            ('general', 'target_path', target_video_path),
            ('general', 'output_path', seg_output),
            ('frame_extraction', 'trim_frame_start', f'{segement[0]}'),
            ('frame_extraction', 'trim_frame_end', f'{segement[1]}'),
            ('misc', 'headless', 'True')
            ]
        update_config(config_path, updates)
        # tqdm.write(f'处理视频片段 {part}, 输出目录 {output_dir}')
        try:
            config.clear_config()
            core.cli()
            outputs.append(seg_output)
        except Exception as e:
            tqdm.write(f"处理文件失败: {e}")

    target_file_name_without_extension = os.path.splitext(os.path.basename(target_video_path))[0]
    output_video_path = os.path.join(output_dir, f'{target_file_name_without_extension}_output.mp4').replace('\\', '/')
    merge_videos(outputs, output_video_path)

    # 删除parts中所有文件
    # for output in outputs:
        # os.remove(output)
    updates = [
        ('general', 'source_paths', ''),
        ('general', 'target_path', ''),
        ('general', 'output_path', ''),
        ('frame_extraction', 'trim_frame_start', ''),
        ('frame_extraction', 'trim_frame_end', ''),
        ('misc', 'headless', '')
        ]
    update_config(config_path, updates)

    tqdm.write(f"处理完成，输出文件：{output_video_path}")

main()
# def diff_video():
#     def get_video_info(file_path):
#         result = subprocess.run(
#             ['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size,bit_rate', 
#             '-show_streams', '-print_format', 'json', file_path],
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE
#         )
#         return result.stdout.decode('utf-8')

#     def print_video_info(info, label):
#         import json
#         data = json.loads(info)
#         print(f"=== {label} ===")
#         format_info = data['format']
#         print(f"Duration: {format_info['duration']} seconds")
#         print(f"Size: {format_info['size']} bytes")
#         print(f"Bit rate: {format_info['bit_rate']} bits per second")
        
#         for stream in data['streams']:
#             if stream['codec_type'] == 'video':
#                 print(f"Video Stream: {stream['codec_name']} - {stream['width']}x{stream['height']} - {stream['bit_rate']} bits per second")
#             elif stream['codec_type'] == 'audio':
#                 print(f"Audio Stream: {stream['codec_name']} - {stream['sample_rate']} Hz - {stream['bit_rate']} bits per second")

#     original_file = 'F:/test_faces/output/test_full.mp4'
#     processed_file = 'F:/test_faces/output/test_full_output.mp4'

#     original_info = get_video_info(original_file)
#     processed_info = get_video_info(processed_file)

#     print_video_info(original_info, "Original File")
#     print_video_info(processed_info, "Processed File")

# diff_video()
import os
import time
from workflow.update_settings import update_config
from workflow.utils import get_image_paths
from tqdm import tqdm
from facefusion import core

src_dir = 'D:/test_faces/source/yy'
dst_dir = 'D:/test_faces/target/wodehezunvyou/2'
output_dir = 'D:/test_faces/output'
config_path = 'D:/aitools/facefusion/facefusion.ini'
output_dir = os.path.join(output_dir, dst_dir.split('/')[-1], src_dir.split('/')[-1]).replace('\\', '/')
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

src_limit = 100

src_paths, cnt = get_image_paths(src_dir, src_limit)
tqdm.write(f"样本数量：{cnt}")
if cnt == 0:
    tqdm.write("样本数量为0，退出")
    exit()

updates = [
    ('general', 'source_paths', src_paths),
    ('general', 'target_path', dst_dir),
    ('general', 'output_path', output_dir),
    ('misc', 'headless', 'True')
    ]
update_config(config_path, updates)
tqdm.write(f'处理图片 {dst_dir}, 输出目录 {output_dir}')
try:
    core.cli()
except Exception as e:
    tqdm.write(f"处理文件失败: {e}")
updates = [
    ('general', 'source_paths', ''),
    ('general', 'target_path', ''),
    ('general', 'output_path', ''),
    ('misc', 'headless', '')
    ]
update_config(config_path, updates)
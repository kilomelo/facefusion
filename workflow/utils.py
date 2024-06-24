import os

def get_image_paths(directory, limit):
    # 定义支持的图片文件扩展名
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    
    # 初始化路径字符串
    pics = ''
    cnt = 0
    # 遍历指定目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.startswith('.'):
                continue
            if file.endswith(supported_extensions):
                # 构建文件的完整路径
                full_path = os.path.join(root, file)
                
                # 将路径中的反斜杠替换为正斜杠
                full_path = full_path.replace('\\', '/')
                
                # 将路径添加到字符串中，后面跟一个空格
                pics += full_path + ' '
                cnt += 1
                if cnt >= limit:
                    break
    
    # 去除最后一个多余的空格
    pics = pics.strip()
    
    return pics, cnt

# 示例调用
# directory = 'D:/test_faces/lzl'
# image_paths = get_image_paths(directory)
# print(f"pics ='{image_paths}'")
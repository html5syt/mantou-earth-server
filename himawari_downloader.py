import os
import sys
from datetime import datetime, timedelta
import requests
from PIL import Image
from io import BytesIO
import math

def round_down_time():
    """获取当前GMT时间并向上取整到上一个10分钟"""
    now = datetime.utcnow()
    # 减去30分钟延迟
    adjusted = now - timedelta(minutes=30)
    # 向下取整到10分钟
    minute = (adjusted.minute // 10) * 10
    return adjusted.replace(minute=minute, second=0, microsecond=0)

def get_nearest_d(resolution):
    """获取最接近的分辨率倍数d值（只允许2^n倍）"""
    # 计算最接近的2的n次幂
    exponent = max(0, min(5, round(math.log2(max(1, resolution / 550)))))
    d = 2 ** exponent
    
    # 确保d在有效范围内（1-20）
    return max(1, min(20, d))

def download_tile(d, date, time_str, x, y):
    """下载单个图片瓦片"""
    url = (
        f"http://himawari8-dl.nict.go.jp/img/D531106/"
        f"{d}d/550/{date.year}/{date.month:02d}/{date.day:02d}/"
        f"{time_str}00_{x}_{y}.png"
    )
    response = requests.get(url)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))

def create_composite_image(d, date, time_str, target_res):
    """下载并拼接所有瓦片，然后缩放到目标分辨率"""
    # 创建基础画布
    base_size = 550 * d
    composite = Image.new('RGB', (base_size, base_size))
    
    # 下载并粘贴所有分块
    for y in range(d):
        for x in range(d):
            tile = download_tile(d, date, time_str, x, y)
            composite.paste(tile, (x*550, y*550))
    
    # 缩放到目标分辨率
    if base_size != target_res:
        composite = composite.resize((target_res, target_res), Image.LANCZOS)
    
    return composite

def save_webp(image, path):
    """保存为WebP格式"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    image.save(path, 'WEBP', quality=85)

def delete_old_images(base_dir, retention_days):
    """删除超过保留期限的图片"""
    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    for dir_name in os.listdir(base_dir):
        dir_path = os.path.join(base_dir, dir_name)
        if os.path.isdir(dir_path):
            try:
                dir_date = datetime.strptime(dir_name, "%Y-%m-%d")
                if dir_date < cutoff_date:
                    shutil.rmtree(dir_path)
                    print(f"Deleted directory: {dir_name}")
            except ValueError:
                continue  # 忽略非日期格式的目录

def main():
    # 从环境变量获取配置
    resolutions = [int(r) for r in os.environ['RESOLUTIONS'].split(',')]
    retention_days = int(os.environ.get('RETENTION_DAYS', 1))
    base_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

    # 计算图片时间
    img_time = round_down_time()
    date_str = img_time.strftime("%Y-%m-%d")
    time_str = img_time.strftime("%H%M")
    
    # 处理每个分辨率
    for res in resolutions:
        d = get_nearest_d(res)
        print(f"Processing {res}px resolution using d={d} (base size={550*d}px)")
        
        composite = create_composite_image(d, img_time, time_str, res)
        
        # 保存路径格式: /2025-07-01/0310_2160.webp
        filename = f"{time_str}_{res}.webp"
        save_path = os.path.join(base_dir, date_str, filename)
        save_webp(composite, save_path)
        print(f"Saved: {save_path}")
    
    # 清理旧图片
    delete_old_images(base_dir, retention_days)

if __name__ == "__main__":
    main()
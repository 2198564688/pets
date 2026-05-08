from PIL import Image
import os

os.makedirs("f:/pets/assets/idle", exist_ok=True)
os.makedirs("f:/pets/assets/walk", exist_ok=True)

def split_sprites(image_path, output_dir, frame_count, prefix):
    img = Image.open(image_path)
    width, height = img.size
    
    # 找到非白色内容的边界框
    # 将白色背景视为 (255,255,255)
    bbox = None
    if img.mode == 'RGBA':
        # 找非透明且非白色的区域
        for y in range(height):
            for x in range(width):
                r, g, b, a = img.getpixel((x, y))
                if a > 10 and not (r > 240 and g > 240 and b > 240):
                    if bbox is None:
                        bbox = [x, y, x, y]
                    else:
                        bbox[0] = min(bbox[0], x)
                        bbox[1] = min(bbox[1], y)
                        bbox[2] = max(bbox[2], x)
                        bbox[3] = max(bbox[3], y)
    else:
        # RGB模式，找非白色区域
        for y in range(height):
            for x in range(width):
                pixel = img.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                else:
                    r = g = b = pixel[0]
                if not (r > 240 and g > 240 and b > 240):
                    if bbox is None:
                        bbox = [x, y, x, y]
                    else:
                        bbox[0] = min(bbox[0], x)
                        bbox[1] = min(bbox[1], y)
                        bbox[2] = max(bbox[2], x)
                        bbox[3] = max(bbox[3], y)
    
    if bbox is None:
        print(f"未找到内容: {image_path}")
        return
    
    content_x, content_y, content_x2, content_y2 = bbox
    content_width = content_x2 - content_x + 1
    content_height = content_y2 - content_y + 1
    
    print(f"{prefix}: 图片尺寸 {width}x{height}, 内容区域 ({content_x},{content_y})-({content_x2},{content_y2}), 内容大小 {content_width}x{content_height}")
    
    frame_width = content_width // frame_count
    
    for i in range(frame_count):
        left = content_x + i * frame_width
        right = left + frame_width
        
        # 稍微扩展一点边界，避免切到边缘
        # 找这一帧的实际内容边界
        frame_bbox = None
        for y in range(content_y, content_y2 + 1):
            for x in range(left, right):
                pixel = img.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[0], pixel[1], pixel[2]
                else:
                    r = g = b = pixel[0]
                if not (r > 240 and g > 240 and b > 240):
                    if frame_bbox is None:
                        frame_bbox = [x, y, x, y]
                    else:
                        frame_bbox[0] = min(frame_bbox[0], x)
                        frame_bbox[1] = min(frame_bbox[1], y)
                        frame_bbox[2] = max(frame_bbox[2], x)
                        frame_bbox[3] = max(frame_bbox[3], y)
        
        if frame_bbox:
            # 增加一点padding
            pad = 2
            fl = max(0, frame_bbox[0] - pad)
            ft = max(0, frame_bbox[1] - pad)
            fr = min(width, frame_bbox[2] + pad + 1)
            fb = min(height, frame_bbox[3] + pad + 1)
            frame = img.crop((fl, ft, fr, fb))
        else:
            frame = img.crop((left, content_y, right, content_y2 + 1))
        
        output_path = os.path.join(output_dir, f"{prefix}_{i:02d}.png")
        
        # 转为RGBA并去除白色背景（可选）
        if frame.mode != 'RGBA':
            frame = frame.convert('RGBA')
        
        datas = frame.getdata()
        newData = []
        for item in datas:
            # 如果接近白色，设为透明
            if item[0] > 240 and item[1] > 240 and item[2] > 240:
                newData.append((255, 255, 255, 0))
            else:
                newData.append(item)
        frame.putdata(newData)
        
        frame.save(output_path)
        print(f"  保存: {output_path} ({frame.size[0]}x{frame.size[1]})")

# 切割 IDLE 动画 (5帧)
split_sprites(
    "f:/pets/ChatGPT Image 2026年5月5日 01_14_13.png",
    "f:/pets/assets/idle",
    5,
    "idle"
)

# 切割 WALK 动画 (6帧)
split_sprites(
    "f:/pets/ChatGPT Image 2026年5月5日 01_15_36.png",
    "f:/pets/assets/walk",
    6,
    "walk"
)

print("\n切割完成！")

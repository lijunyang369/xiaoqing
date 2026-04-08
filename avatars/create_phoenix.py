#!/usr/bin/env python3
"""
设计简约凤凰图标
象征：重生、革新、永恒
"""

from PIL import Image, ImageDraw
import math
import os

def create_phoenix_icon():
    # 创建512x512的透明画布
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 中心点
    center_x, center_y = size // 2, size // 2
    
    # 凤凰颜色：金色到橙色的渐变，象征火焰与荣耀
    colors = [
        (255, 215, 0, 255),    # 金色
        (255, 165, 0, 255),    # 橙色
        (255, 69, 0, 255),     # 红色-橙色
        (255, 140, 0, 255),    # 深橙色
    ]
    
    # 绘制凤凰主体（简约风格）
    # 1. 身体（椭圆）
    body_width = 180
    body_height = 240
    draw.ellipse(
        [(center_x - body_width//2, center_y - body_height//2 + 30),
         (center_x + body_width//2, center_y + body_height//2 + 30)],
        fill=colors[0], outline=colors[1], width=8
    )
    
    # 2. 头部（小圆）
    head_radius = 40
    draw.ellipse(
        [(center_x - head_radius, center_y - body_height//2 + 30 - head_radius),
         (center_x + head_radius, center_y - body_height//2 + 30 + head_radius)],
        fill=colors[1], outline=colors[2], width=6
    )
    
    # 3. 冠羽（三角形）
    crown_points = [
        (center_x, center_y - body_height//2 + 30 - head_radius - 20),
        (center_x - 25, center_y - body_height//2 + 30 - head_radius + 10),
        (center_x + 25, center_y - body_height//2 + 30 - head_radius + 10),
    ]
    draw.polygon(crown_points, fill=colors[2], outline=colors[3], width=4)
    
    # 4. 翅膀（对称曲线）
    wing_points_left = [
        (center_x - body_width//2 + 20, center_y + 10),
        (center_x - body_width//2 - 80, center_y - 40),
        (center_x - body_width//2 - 60, center_y + 80),
        (center_x - body_width//2 + 10, center_y + 50),
    ]
    
    wing_points_right = [
        (center_x + body_width//2 - 20, center_y + 10),
        (center_x + body_width//2 + 80, center_y - 40),
        (center_x + body_width//2 + 60, center_y + 80),
        (center_x + body_width//2 - 10, center_y + 50),
    ]
    
    draw.polygon(wing_points_left, fill=colors[0], outline=colors[1], width=6)
    draw.polygon(wing_points_right, fill=colors[0], outline=colors[1], width=6)
    
    # 5. 尾羽（火焰效果）
    for i in range(5):
        angle = math.pi * 0.7 + i * 0.2
        length = 120 + i * 20
        end_x = center_x + math.cos(angle) * length
        end_y = center_y + 100 + math.sin(angle) * length * 0.5
        
        # 尾羽主体
        draw.line(
            [(center_x, center_y + 100), (end_x, end_y)],
            fill=colors[i % len(colors)], width=12 - i * 2
        )
        
        # 尾羽尖端（火焰形状）
        flame_points = [
            (end_x, end_y),
            (end_x - 15 + i * 3, end_y - 25 + i * 5),
            (end_x + 15 - i * 3, end_y - 25 + i * 5),
        ]
        draw.polygon(flame_points, fill=colors[(i+1) % len(colors)])
    
    # 6. 眼睛（小圆点，象征智慧）
    eye_radius = 8
    draw.ellipse(
        [(center_x - 12 - eye_radius, center_y - body_height//2 + 30 - 5),
         (center_x - 12 + eye_radius, center_y - body_height//2 + 30 + 5)],
        fill=(0, 0, 0, 255)
    )
    
    # 7. 喙（小三角形）
    beak_points = [
        (center_x + 25, center_y - body_height//2 + 30),
        (center_x + 50, center_y - body_height//2 + 30 - 10),
        (center_x + 50, center_y - body_height//2 + 30 + 10),
    ]
    draw.polygon(beak_points, fill=colors[3])
    
    # 8. 添加光环效果（象征永恒）
    halo_radius = 280
    for i in range(3):
        r = halo_radius - i * 20
        draw.ellipse(
            [(center_x - r, center_y - r),
             (center_x + r, center_y + r)],
            outline=(255, 255, 200, 50 + i * 20), width=2
        )
    
    return img

def main():
    print("正在创建自定义凤凰图标...")
    
    # 创建图标
    phoenix_img = create_phoenix_icon()
    
    # 保存文件
    output_path = "phoenix.png"
    phoenix_img.save(output_path, "PNG")
    
    # 获取文件信息
    file_size = os.path.getsize(output_path) / 1024  # KB
    
    print(f"✅ 凤凰图标已创建: {output_path}")
    print(f"📏 尺寸: {phoenix_img.size[0]}x{phoenix_img.size[1]} 像素")
    print(f"💾 大小: {file_size:.1f} KB")
    print(f"🎨 颜色: RGBA (透明背景)")
    print("🦚 象征: 重生、革新、永恒、智慧")
    
    # 创建预览文本文件
    with open("PHOENIX_DESIGN.md", "w", encoding="utf-8") as f:
        f.write("# 自定义凤凰图标设计\n\n")
        f.write("## 设计理念\n")
        f.write("- **重生**: 火焰尾羽象征凤凰涅槃\n")
        f.write("- **革新**: 现代简约线条风格\n")
        f.write("- **永恒**: 金色光环效果\n")
        f.write("- **智慧**: 明亮的眼睛设计\n\n")
        f.write("## 视觉元素\n")
        f.write("1. **身体**: 金色椭圆，象征稳固基础\n")
        f.write("2. **翅膀**: 展开的曲线，象征自由与力量\n")
        f.write("3. **尾羽**: 火焰渐变，象征重生过程\n")
        f.write("4. **冠羽**: 红色三角形，象征领导力\n")
        f.write("5. **光环**: 半透明圆环，象征永恒\n\n")
        f.write("## 颜色方案\n")
        f.write("- **主色**: 金色 (255, 215, 0) - 荣耀与价值\n")
        f.write("- **辅色**: 橙色系 - 火焰与活力\n")
        f.write("- **轮廓**: 深橙色 - 定义与边界\n")
        f.write("- **背景**: 完全透明\n\n")
        f.write("## TOC哲学应用\n")
        f.write("- **自主创造**: 当外部资源不符合要求时，自己设计解决方案\n")
        f.write("- **聚焦核心**: 突出凤凰的核心象征意义\n")
        f.write("- **系统优化**: 确保图标与身份文件的整体一致性\n")

if __name__ == "__main__":
    main()
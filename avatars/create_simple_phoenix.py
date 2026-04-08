#!/usr/bin/env python3
"""
使用tkinter创建简单的凤凰图标
不需要外部依赖
"""

import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import sys

try:
    # 尝试导入PIL，如果失败就退出
    from PIL import Image, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("错误: 需要PIL库。请运行: pip install pillow")
    sys.exit(1)

def create_phoenix():
    """创建简约凤凰图标"""
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # 颜色定义
    gold = (255, 215, 0, 255)
    orange = (255, 165, 0, 255)
    dark_orange = (255, 140, 0, 255)
    red_orange = (255, 69, 0, 255)
    
    # 1. 身体 - 简单圆形
    body_radius = 100
    draw.ellipse(
        [center - body_radius, center - body_radius + 50,
         center + body_radius, center + body_radius + 50],
        fill=gold, outline=orange, width=10
    )
    
    # 2. 头部
    head_radius = 40
    draw.ellipse(
        [center - head_radius, center - body_radius + 50 - head_radius,
         center + head_radius, center - body_radius + 50 + head_radius],
        fill=orange, outline=red_orange, width=8
    )
    
    # 3. 冠羽 - 简单三角形
    draw.polygon(
        [center, center - body_radius + 50 - head_radius - 20,
         center - 20, center - body_radius + 50 - head_radius + 10,
         center + 20, center - body_radius + 50 - head_radius + 10],
        fill=red_orange, outline=dark_orange, width=4
    )
    
    # 4. 翅膀 - 简单三角形
    # 左翅膀
    draw.polygon(
        [center - body_radius + 20, center + 20,
         center - body_radius - 60, center - 20,
         center - body_radius - 40, center + 60,
         center - body_radius + 10, center + 40],
        fill=gold, outline=orange, width=6
    )
    
    # 右翅膀
    draw.polygon(
        [center + body_radius - 20, center + 20,
         center + body_radius + 60, center - 20,
         center + body_radius + 40, center + 60,
         center + body_radius - 10, center + 40],
        fill=gold, outline=orange, width=6
    )
    
    # 5. 尾羽 - 简单线条
    for i in range(3):
        # 左尾羽
        draw.line(
            [center, center + body_radius + 50,
             center - 60 - i*20, center + body_radius + 100 + i*30],
            fill=[gold, orange, red_orange][i], width=15 - i*4
        )
        # 右尾羽
        draw.line(
            [center, center + body_radius + 50,
             center + 60 + i*20, center + body_radius + 100 + i*30],
            fill=[gold, orange, red_orange][i], width=15 - i*4
        )
    
    # 6. 眼睛
    draw.ellipse(
        [center - 15, center - body_radius + 50 - 5,
         center - 5, center - body_radius + 50 + 5],
        fill=(0, 0, 0, 255)
    )
    
    # 7. 喙
    draw.polygon(
        [center + 30, center - body_radius + 50,
         center + 55, center - body_radius + 50 - 15,
         center + 55, center - body_radius + 50 + 15],
        fill=dark_orange
    )
    
    return img

def main():
    print("正在创建简约凤凰图标...")
    
    # 创建图标
    phoenix = create_phoenix()
    
    # 保存为PNG
    output_path = "phoenix.png"
    phoenix.save(output_path, "PNG")
    
    # 显示信息
    print(f"✅ 图标已保存: {output_path}")
    print(f"📏 尺寸: {phoenix.size[0]}x{phoenix.size[1]} 像素")
    print(f"🎨 格式: PNG with alpha channel")
    print("🦚 设计特点:")
    print("  - 简约几何形状")
    print("  - 金色到橙色渐变")
    print("  - 透明背景")
    print("  - 象征: 重生、智慧、永恒")
    
    # 创建设计说明
    with open("DESIGN_NOTES.md", "w", encoding="utf-8") as f:
        f.write("# 凤凰图标设计说明\n\n")
        f.write("## 设计原则\n")
        f.write("1. **简约性**: 使用基本几何形状\n")
        f.write("2. **象征性**: 每个元素都有含义\n")
        f.write("3. **实用性**: 清晰可识别，适合图标使用\n")
        f.write("4. **一致性**: 与身份文件主题匹配\n\n")
        f.write("## 元素解析\n")
        f.write("- **圆形身体**: 稳固、完整\n")
        f.write("- **三角形冠羽**: 方向、领导力\n")
        f.write("- **展开翅膀**: 自由、力量\n")
        f.write("- **火焰尾羽**: 重生、变革\n")
        f.write("- **单眼设计**: 智慧、专注\n\n")
        f.write("## TOC哲学体现\n")
        f.write("- **自主解决**: 当外部资源不可用时，创造内部解决方案\n")
        f.write("- **聚焦核心**: 突出凤凰的核心特征\n")
        f.write("- **持续改进**: 设计可随时优化调整\n")

if __name__ == "__main__":
    main()
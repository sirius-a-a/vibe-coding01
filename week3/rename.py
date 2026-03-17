import os
import glob

def batch_rename_files(folder_path="test_files"):
    """
    批量重命名指定文件夹下的所有 .txt 文件
    按文件修改时间排序，命名格式为 doc_001.txt, doc_002.txt ...
    """
    # 1. 检查文件夹是否存在。如果不存在，给出友好提示并退出
    if not os.path.exists(folder_path):
        print(f"❌ 错误：找不到指定的文件夹 '{folder_path}'。请确保该文件夹存在！")
        return
    
    # 扫描指定文件夹下的所有的 .txt 文件
    search_pattern = os.path.join(folder_path, "*.txt")
    txt_files = glob.glob(search_pattern)
    
    # 如果没有找到任何 txt 文件，给出提示并退出
    if not txt_files:
        print(f"⚠️ 提示：在文件夹 '{folder_path}' 中没有找到任何 .txt 文件。")
        return
    
    # 2. 按照文件修改时间排序（最早的文件排第一）
    # 使用 os.path.getmtime 作为排序的依据
    txt_files.sort(key=os.path.getmtime)
    
    print(f"✅ 找到 {len(txt_files)} 个 .txt 文件，开始按时间顺序重命名...\n")
    
    # 3. 遍历排序后的文件列表，进行重命名
    for index, old_file_path in enumerate(txt_files, start=1):
        # 提取文件所在的文件夹路径
        dir_name = os.path.dirname(old_file_path)
        
        # 4. 生成新的文件名，保留 .txt 扩展名
        # {:03d} 格式化字符串：将数字格式化为3位宽，不足前面补0 (例如: 1 -> 001)
        new_file_name = f"doc_{index:03d}.txt"
        new_file_path = os.path.join(dir_name, new_file_name)
        
        # 为了防止重命名冲突（例如目标文件已经存在），进行简单的判定
        if os.path.exists(new_file_path) and old_file_path != new_file_path:
            print(f"⚠️ 警告：目标文件 '{new_file_name}' 已存在，跳过覆盖以防止丢失数据。")
            continue
            
        try:
            # 调用 os.rename 执行重命名操作
            os.rename(old_file_path, new_file_path)
            
            # 提取原文件的纯文件名（用于打印美观日志）
            old_name = os.path.basename(old_file_path)
            print(f"🔄 重命名成功: '{old_name}' -> '{new_file_name}'")
            
        except Exception as e:
            # 捕获并打印重命名过程中可能出现的权限或其他异常
            print(f"❌ 重命名失败: '{old_file_path}'。原因: {e}")
            
    print("\n🎉 所有重命名任务执行完毕！")

if __name__ == "__main__":
    # 执行脚本时，默认针对同级目录下的 test_files 文件夹进行重命名
    batch_rename_files("test_files")

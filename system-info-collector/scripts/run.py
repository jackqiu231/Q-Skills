import json
import platform
import psutil
import os

def run(args: dict) -> dict:
    try:
        # 收集操作系统信息
        os_info = {
            "name": platform.system(),
            "version": platform.version(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "hostname": platform.node()
        }

        # 收集CPU信息
        cpu_info = {
            "model": platform.processor(),
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_percent": psutil.cpu_percent(interval=1)
        }

        # 收集内存信息
        mem = psutil.virtual_memory()
        memory_info = {
            "total_gb": round(mem.total / (1024**3), 2),
            "used_gb": round(mem.used / (1024**3), 2),
            "available_gb": round(mem.available / (1024**3), 2),
            "usage_percent": mem.percent
        }

        # 收集磁盘信息
        disk_info = []
        for part in psutil.disk_partitions():
            if part.fstype:
                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_info.append({
                        "mount_point": part.mountpoint,
                        "fstype": part.fstype,
                        "total_gb": round(usage.total / (1024**3), 2),
                        "used_gb": round(usage.used / (1024**3), 2),
                        "available_gb": round(usage.free / (1024**3), 2),
                        "usage_percent": usage.percent
                    })
                except:
                    continue

        # 收集已安装软件（macOS）
        installed_apps = []
        if os_info["name"] == "Darwin":
            app_dir = "/Applications"
            if os.path.exists(app_dir):
                installed_apps = [f for f in os.listdir(app_dir) if f.endswith(".app")]

        # 格式化输出为易读文本
        output_text = "=== 本地软硬件信息收集结果 ===\n\n"
        output_text += "📌 操作系统信息：\n"
        output_text += f"- 系统：{os_info['name']} {os_info['release']}\n"
        output_text += f"- 版本：{os_info['version']}\n"
        output_text += f"- 架构：{os_info['architecture']}\n"
        output_text += f"- 主机名：{os_info['hostname']}\n\n"

        output_text += "⚡ CPU信息：\n"
        output_text += f"- 型号：{cpu_info['model']}\n"
        output_text += f"- 物理核心：{cpu_info['physical_cores']} 核\n"
        output_text += f"- 逻辑核心：{cpu_info['logical_cores']} 核\n"
        output_text += f"- 当前使用率：{cpu_info['usage_percent']}%\n\n"

        output_text += "🧠 内存信息：\n"
        output_text += f"- 总容量：{memory_info['total_gb']} GB\n"
        output_text += f"- 已使用：{memory_info['used_gb']} GB\n"
        output_text += f"- 可用：{memory_info['available_gb']} GB\n"
        output_text += f"- 使用率：{memory_info['usage_percent']}%\n\n"

        output_text += "💽 磁盘信息：\n"
        for disk in disk_info:
            if disk['mount_point'] == "/" or disk['mount_point'] == "/System/Volumes/Data":
                output_text += f"- 挂载点 {disk['mount_point']}：总容量 {disk['total_gb']} GB，已用 {disk['used_gb']} GB，可用 {disk['available_gb']} GB，使用率 {disk['usage_percent']}%\n"
        output_text += "\n"

        output_text += "📦 已安装软件（部分）：\n"
        for app in installed_apps[:10]:
            output_text += f"- {app[:-4]}\n"
        if len(installed_apps) > 10:
            output_text += f"... 共 {len(installed_apps)} 个软件\n"

        return {"output": output_text, "success": True}
    except Exception as e:
        return {"output": f"收集信息失败：{str(e)}", "success": False}

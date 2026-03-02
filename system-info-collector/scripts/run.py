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

        result = {
            "os_info": os_info,
            "cpu_info": cpu_info,
            "memory_info": memory_info,
            "disk_info": disk_info,
            "installed_apps": installed_apps[:50] # 最多返回50个避免过长
        }

        return {"output": json.dumps(result, ensure_ascii=False, indent=2), "success": True}
    except Exception as e:
        return {"output": f"收集信息失败：{str(e)}", "success": False}

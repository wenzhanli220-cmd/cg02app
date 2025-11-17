# utils/port_manager.py
"""
端口管理工具类
提供端口检测和自动分配功能，用于为各 Appium server 分配空闲端口
"""
import socket
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PortManager:
    """端口管理器，用于检测和分配空闲端口"""
    
    def __init__(self, default_start_port: int = 4723, port_range: int = 100):
        """
        初始化端口管理器
        :param default_start_port: 默认起始端口号，默认 4723（Appium 默认端口）
        :param port_range: 端口搜索范围，默认 100（从起始端口向后搜索 100 个端口）
        """
        self.default_start_port = default_start_port
        self.port_range = port_range
        self._allocated_ports: Dict[str, int] = {}  # 存储已分配的端口 {device_name: port}
        self._reserved_ports: set = set()  # 存储已保留的端口（防止重复分配）
    
    def is_port_available(self, port: int, host: str = 'localhost') -> bool:
        """
        检测端口是否可用（未被占用）
        :param port: 要检测的端口号
        :param host: 主机地址，默认 'localhost'
        :return: True 表示端口可用，False 表示端口被占用
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                # 如果连接成功，说明端口被占用
                if result == 0:
                    logger.debug(f"端口 {port} 已被占用")
                    return False
                else:
                    logger.debug(f"端口 {port} 可用")
                    return True
        except Exception as e:
            logger.warning(f"检测端口 {port} 时出错: {e}")
            # 出错时假设端口不可用（保守策略）
            return False
    
    def is_appium_server_running(self, port: int, host: str = 'localhost') -> bool:
        """
        检测指定端口上是否有 Appium server 在运行
        :param port: 端口号
        :param host: 主机地址，默认 'localhost'
        :return: True 表示有 Appium server 在运行，False 表示没有
        """
        try:
            import urllib.request
            import urllib.error
            import json
            
            url = f"http://{host}:{port}/wd/hub/status"
            try:
                with urllib.request.urlopen(url, timeout=2) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode())
                        # Appium server 通常会返回包含 'value' 字段的状态
                        if 'value' in data or 'status' in data:
                            logger.info(f"✅ 端口 {port} 上有 Appium server 在运行")
                            return True
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
                pass
            
            return False
        except Exception as e:
            logger.debug(f"检测 Appium server 时出错: {e}")
            return False
    
    def find_available_port(self, start_port: Optional[int] = None, max_attempts: Optional[int] = None) -> Optional[int]:
        """
        查找一个空闲端口
        :param start_port: 起始端口号，如果为 None 则使用默认起始端口
        :param max_attempts: 最大尝试次数，如果为 None 则使用端口范围
        :return: 找到的空闲端口号，如果找不到则返回 None
        """
        if start_port is None:
            start_port = self.default_start_port
        
        if max_attempts is None:
            max_attempts = self.port_range
        
        for i in range(max_attempts):
            port = start_port + i
            # 跳过已分配的端口
            if port in self._reserved_ports:
                continue
            
            if self.is_port_available(port):
                logger.info(f"✅ 找到空闲端口: {port}")
                return port
        
        logger.error(f"❌ 在端口范围 {start_port}-{start_port + max_attempts - 1} 内未找到空闲端口")
        return None
    
    def extract_port_from_url(self, url: str) -> Optional[int]:
        """
        从 URL 中提取端口号
        :param url: Appium server URL，例如 "http://localhost:4723/wd/hub"
        :return: 端口号，如果提取失败返回 None
        """
        try:
            parsed = urlparse(url)
            if parsed.port:
                return parsed.port
            # 如果没有端口，根据协议返回默认端口
            if parsed.scheme == 'http':
                return 80
            elif parsed.scheme == 'https':
                return 443
            return None
        except Exception as e:
            logger.warning(f"从 URL {url} 提取端口失败: {e}")
            return None
    
    def allocate_port_for_device(self, device_name: str, preferred_url: Optional[str] = None) -> Tuple[str, int]:
        """
        为指定设备分配一个空闲端口
        :param device_name: 设备名称
        :param preferred_url: 首选 URL（如果端口可用，优先使用）
        :return: (appium_server_url, port) 元组
        """
        # 如果设备已经有分配的端口，直接返回
        if device_name in self._allocated_ports:
            port = self._allocated_ports[device_name]
            url = f"http://localhost:{port}/wd/hub"
            logger.info(f"设备 {device_name} 已分配端口 {port}，URL: {url}")
            return url, port
        
        # 如果有首选 URL，先检查其端口是否可用或是否有 Appium server
        if preferred_url:
            preferred_port = self.extract_port_from_url(preferred_url)
            if preferred_port and preferred_port not in self._reserved_ports:
                # 优先检查是否有 Appium server 在运行
                if self.is_appium_server_running(preferred_port):
                    self._allocated_ports[device_name] = preferred_port
                    self._reserved_ports.add(preferred_port)
                    url = f"http://localhost:{preferred_port}/wd/hub"
                    logger.info(f"✅ 检测到设备 {device_name} 的首选端口 {preferred_port} 上有 Appium server 在运行，使用该端口")
                    return url, preferred_port
                # 如果没有 Appium server，检查端口是否空闲
                elif self.is_port_available(preferred_port):
                    self._allocated_ports[device_name] = preferred_port
                    self._reserved_ports.add(preferred_port)
                    url = f"http://localhost:{preferred_port}/wd/hub"
                    logger.info(f"✅ 为设备 {device_name} 分配首选端口 {preferred_port}，URL: {url}")
                    return url, preferred_port
                else:
                    logger.warning(f"⚠️ 设备 {device_name} 的首选端口 {preferred_port} 已被占用且没有 Appium server，将查找空闲端口")
        
        # 查找空闲端口
        available_port = self.find_available_port()
        if available_port:
            self._allocated_ports[device_name] = available_port
            self._reserved_ports.add(available_port)
            url = f"http://localhost:{available_port}/wd/hub"
            logger.info(f"✅ 为设备 {device_name} 自动分配空闲端口 {available_port}，URL: {url}")
            logger.warning(f"⚠️ 提示: 请确保在端口 {available_port} 上启动 Appium server")
            return url, available_port
        else:
            raise RuntimeError(f"无法为设备 {device_name} 找到空闲端口")
    
    def allocate_ports_for_devices(self, device_names: List[str], 
                                    preferred_urls: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """
        为多个设备批量分配空闲端口
        :param device_names: 设备名称列表
        :param preferred_urls: 首选 URL 字典 {device_name: url}，可选
        :return: 设备端口分配字典 {device_name: appium_server_url}
        """
        if preferred_urls is None:
            preferred_urls = {}
        
        allocated_urls = {}
        
        logger.info(f"开始为 {len(device_names)} 个设备分配端口...")
        
        for device_name in device_names:
            preferred_url = preferred_urls.get(device_name)
            url, port = self.allocate_port_for_device(device_name, preferred_url)
            allocated_urls[device_name] = url
        
        logger.info(f"✅ 端口分配完成，共分配 {len(allocated_urls)} 个端口")
        return allocated_urls
    
    def release_port(self, device_name: str):
        """
        释放设备占用的端口（从已分配列表中移除，但不检查实际占用情况）
        :param device_name: 设备名称
        """
        if device_name in self._allocated_ports:
            port = self._allocated_ports[device_name]
            del self._allocated_ports[device_name]
            self._reserved_ports.discard(port)
            logger.info(f"已释放设备 {device_name} 的端口 {port}")
    
    def get_allocated_ports(self) -> Dict[str, int]:
        """
        获取所有已分配的端口
        :return: {device_name: port} 字典
        """
        return self._allocated_ports.copy()
    
    def get_allocated_urls(self) -> Dict[str, str]:
        """
        获取所有已分配的 Appium server URL
        :return: {device_name: appium_server_url} 字典
        """
        return {
            device_name: f"http://localhost:{port}/wd/hub"
            for device_name, port in self._allocated_ports.items()
        }
    
    def check_port_status(self, port: int) -> Dict[str, any]:
        """
        检查端口状态（详细信息）
        :param port: 端口号
        :return: 包含端口状态的字典
        """
        is_available = self.is_port_available(port)
        is_allocated = port in self._reserved_ports
        allocated_device = None
        for device_name, allocated_port in self._allocated_ports.items():
            if allocated_port == port:
                allocated_device = device_name
                break
        
        return {
            'port': port,
            'is_available': is_available,
            'is_allocated': is_allocated,
            'allocated_device': allocated_device
        }


# 创建全局实例
port_manager = PortManager()


# 便捷函数
def is_port_available(port: int, host: str = 'localhost') -> bool:
    """检测端口是否可用"""
    return port_manager.is_port_available(port, host)


def find_available_port(start_port: Optional[int] = None, max_attempts: Optional[int] = None) -> Optional[int]:
    """查找一个空闲端口"""
    return port_manager.find_available_port(start_port, max_attempts)


def allocate_port_for_device(device_name: str, preferred_url: Optional[str] = None) -> Tuple[str, int]:
    """为指定设备分配一个空闲端口"""
    return port_manager.allocate_port_for_device(device_name, preferred_url)


def allocate_ports_for_devices(device_names: List[str], 
                                preferred_urls: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """为多个设备批量分配空闲端口"""
    return port_manager.allocate_ports_for_devices(device_names, preferred_urls)



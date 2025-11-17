# 端口自动分配功能说明

## 功能概述

项目已添加端口检测和自动分配功能，能够自动检测端口占用情况，并为每个 Appium server 分配空闲端口。

## 改动文件清单

### 1. 新增文件

#### `ai_mate_tests/utils/port_manager.py`
- **功能**: 端口管理工具类，提供端口检测和自动分配功能
- **主要类**: `PortManager`
- **主要方法**:
  - `is_port_available(port)`: 检测端口是否可用
  - `find_available_port(start_port, max_attempts)`: 查找空闲端口
  - `allocate_port_for_device(device_name, preferred_url)`: 为指定设备分配端口
  - `allocate_ports_for_devices(device_names, preferred_urls)`: 批量分配端口
  - `extract_port_from_url(url)`: 从 URL 中提取端口号

### 2. 修改文件

#### `ai_mate_tests/utils/config_loader.py`
- **修改位置**: 
  - 导入端口管理工具 (第 7-13 行)
  - `ConfigLoader.__init__()` 方法添加 `auto_allocate_ports` 参数 (第 17 行)
  - 新增 `_auto_allocate_ports_on_init()` 方法 (第 172-207 行)
  - 修改 `get_appium_server_url()` 方法，添加自动端口分配逻辑 (第 128-170 行)

## 使用方式

### 自动模式（默认）

端口自动分配功能默认启用，无需额外配置。系统会在以下时机自动分配端口：

1. **初始化时**: `ConfigLoader` 初始化时自动为所有设备分配端口
2. **获取端口时**: 调用 `get_appium_server_url()` 时，如果端口已被占用，会自动分配新端口

```python
# 示例：正常使用，自动分配端口
from ai_mate_tests.utils.config_loader import ConfigLoader

config_loader = ConfigLoader()  # 自动为所有设备分配端口
url = config_loader.get_appium_server_url("device1")  # 返回已分配的 URL
```

### 手动模式

如果需要禁用自动分配功能，可以在创建 `ConfigLoader` 时设置 `auto_allocate_ports=False`:

```python
# 禁用自动分配，使用配置中的固定端口
config_loader = ConfigLoader(auto_allocate_ports=False)
```

### 直接使用端口管理器

也可以直接使用端口管理器进行端口分配：

```python
from ai_mate_tests.utils.port_manager import port_manager

# 为单个设备分配端口
url, port = port_manager.allocate_port_for_device("device1", "http://localhost:4723/wd/hub")
print(f"分配的端口: {port}, URL: {url}")

# 批量分配端口
device_names = ["device1", "device2"]
preferred_urls = {
    "device1": "http://localhost:4723/wd/hub",
    "device2": "http://localhost:4725/wd/hub"
}
allocated_urls = port_manager.allocate_ports_for_devices(device_names, preferred_urls)

# 检查端口状态
status = port_manager.check_port_status(4723)
print(status)  # {'port': 4723, 'is_available': True, 'is_allocated': False, 'allocated_device': None}
```

## 工作原理

1. **端口检测**: 使用 socket 连接测试端口是否被占用
2. **优先级**: 
   - 如果配置中的端口可用，优先使用配置的端口
   - 如果配置的端口被占用，自动查找下一个空闲端口
3. **端口范围**: 默认从 4723 开始，向后搜索 100 个端口（可通过 `PortManager` 初始化参数调整）
4. **端口记录**: 已分配的端口会被记录，避免重复分配

## 注意事项

1. **端口冲突**: 如果配置的端口已被占用，系统会自动分配新端口，但不会修改配置文件
2. **Appium Server**: 确保在使用分配的端口之前，已经启动了对应端口的 Appium server
3. **日志输出**: 端口分配过程会有日志输出，方便调试和查看端口分配情况

## 向后兼容性

- 如果 `port_manager` 导入失败，系统会自动降级为使用配置中的固定端口
- 现有的代码无需修改即可使用新功能
- 可以通过 `auto_allocate_ports=False` 禁用新功能，保持原有行为



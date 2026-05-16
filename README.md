# BMW_G-Series_Cluster_fh6

BMW G-Series 真车液晶仪表接入《极限竞速：地平线6》的项目。  
A project for connecting a real BMW G-Series digital instrument cluster to Forza Horizon 6 telemetry data.

> 当前项目仍在开发中，目前只是第一版演示，功能还不完整，并且仍然存在一些 bug。  
> This project is still under development. The current version is only an early demo and may still contain bugs.

---

## 项目介绍 / About

本项目用于将游戏遥测数据转换为 BMW G-Series 仪表可以识别的 CAN 数据，让真实的 BMW G 底盘液晶仪表可以显示游戏中的车辆信息。

This project converts game telemetry data into CAN messages that can be understood by a BMW G-Series digital cluster.  
It allows a real BMW G-Series digital instrument cluster to display vehicle information from games.

当前主要演示的是《极限竞速：地平线6》的遥测接入效果。

The current demo mainly shows Forza Horizon 6 telemetry integration.

---

## 演示视频 / Demo Video

Bilibili 演示视频：  
Bilibili demo video:

https://www.bilibili.com/video/BV16FLV6yEx2?vd_source=bc20e93065a8534507fd865d933816ec&spm_id_from=333.788.videopod.sections

---

## 当前功能 / Current Features

当前版本已经可以实现或部分实现以下功能：

The current version can already support or partially support the following features:

- 速度显示  
  Speed display

- 转速显示  
  RPM display

- 档位显示  
  Gear display

- 油量显示  
  Fuel level display

- 驾驶模式显示  
  Drive mode display

- 仪表点火状态控制  
  Ignition status control

- 部分车门状态控制  
  Partial door status control

- 后备箱和引擎盖状态控制  
  Trunk and hood status control

- 部分灯光状态控制  
  Partial light control

- 控制台手动设置部分车辆状态  
  Manual control panel for vehicle states

由于 Forza Horizon 6 的遥测数据有限，部分功能无法直接从游戏中读取，需要通过控制台手动设置。

Because Forza Horizon 6 provides limited telemetry data, some vehicle states cannot be read directly from the game and need to be manually controlled from the control panel.

---

## 未来计划 / Future Plans

后续版本计划增加更多功能，包括但不限于：

Future versions plan to add more features, including but not limited to:

- 支持其他 12 种驾驶模式  
  Support for 12 additional drive modes

- 自定义大灯显示  
  Custom headlight display

- 防滑灯 / 牵引力控制灯显示  
  Slip indicator / traction control indicator display

- 双单位显示，例如 km/h 和 mph  
  Dual unit display, such as km/h and mph

- 根据电脑系统时间自动设置仪表时间  
  Automatically set the cluster time based on the PC system time

- AutoHold 显示  
  AutoHold display

- 根据游戏内自动驾驶 / 辅助驾驶状态，同步仪表上的驾驶辅助界面，例如车道保持、跟车辅助、方向盘辅助等显示  
  Synchronize the cluster driver assistance interface based on the in-game autonomous driving or driver assistance state, such as lane keeping, follow assist, steering assist, and related indicators

- 更完整的车身状态控制  
  More complete vehicle body state control

- 更完整的 BeamNG.drive 支持  
  More complete BeamNG.drive support

- 更稳定的 UI 控制台  
  More stable UI control panel

- 更详细的接线说明和使用教程  
  More detailed wiring guide and usage documentation

---

## BeamNG.drive 支持 / BeamNG.drive Support

如果需要更完整的功能，建议使用 BeamNG.drive。

For full functionality, BeamNG.drive is recommended.

BeamNG.drive 可以提供比 Forza Horizon 6 更完整的车辆状态数据，例如车门、灯光、发动机状态、损坏状态等。

BeamNG.drive can provide more complete vehicle state data than Forza Horizon 6, such as doors, lights, engine states, damage states, and more.

当前仓库主要是 Forza Horizon 6 项目。  
G-Series + BeamNG.drive 的项目会在另一个仓库中继续开发。

This repository mainly focuses on Forza Horizon 6.  
The G-Series + BeamNG.drive project will continue in another repository.

---

## 项目区别 / Project Difference

目前作者有多个 BMW 仪表相关项目：

The author currently has multiple BMW cluster-related projects:

| 项目 / Project | 平台 / Platform | 游戏 / Game | 状态 / Status |
|---|---|---|---|
| BMW_G-Series_Cluster_fh6 | BMW G-Series | Forza Horizon 6 | 第一版演示 / First demo |
| BMW-G-Series-Cluster-for-BeamNG.Drive | BMW G-Series | BeamNG.drive | 开发中 / Under development |
| CarCluster-F10-Enhanced | BMW F-Series / F10 | BeamNG.drive | 独立项目 / Separate project |

请注意，F-Series 和 G-Series 仪表不通用。  
Please note that F-Series and G-Series clusters are not directly compatible.

它们的 CAN 数据、仪表逻辑和显示方式不同，因此代码不能直接混用。  
Their CAN data, cluster logic, and display behavior are different, so the code cannot be used interchangeably.

---

## 相关项目 / Related Projects

### BMW G-Series Cluster for Forza Horizon 6

当前仓库是 BMW G-Series 真车液晶仪表接入《极限竞速：地平线6》的项目。

This repository is for connecting a real BMW G-Series digital instrument cluster to Forza Horizon 6 telemetry data.

Project:

https://github.com/JackieZ123430/BMW_G-Series_Cluster_fh6

---

### BMW G-Series Cluster for BeamNG.drive

这是未来计划中的 BMW G-Series 仪表接入 BeamNG.drive 项目。  
目前仓库还在开发中，暂时没有放入完整内容。

This is the future BMW G-Series cluster integration project for BeamNG.drive.  
The repository is still under development and does not contain full content yet.

Project:

https://github.com/JackieZ123430/BMW-G-Series-Cluster-for-BeamNG.Drive

BeamNG.drive 可以提供比 Forza Horizon 6 更完整的车辆状态数据，因此未来版本会优先支持更多真实车身功能。

BeamNG.drive can provide more complete vehicle state data than Forza Horizon 6, so future versions will focus on more realistic vehicle functions.

---

### CarCluster-F10-Enhanced

这是 BMW F 底盘 / F10 仪表相关项目，主要面向 BeamNG.drive 和 F-Series 仪表模拟。

This is the BMW F-Series / F10 cluster project, mainly for BeamNG.drive and F-Series cluster simulation.

Project:

https://github.com/JackieZ123430/CarCluster-F10-Enhanced

该项目和当前 G-Series 项目不是同一个平台。  
This project is not the same platform as the current G-Series project.

F-Series 和 G-Series 的 CAN 数据、仪表逻辑和显示方式不同，因此不能直接通用。

F-Series and G-Series use different CAN data, cluster logic, and display behavior, so they are not directly interchangeable.

---

## 硬件需求 / Hardware Requirements

需要以下硬件：

Required hardware:

- BMW G-Series 液晶仪表  
  BMW G-Series digital instrument cluster

- Arduino Mega 开发板 或 Arduino Uno 开发板  
  Arduino Mega or Arduino Uno development board

- MCP2515 CAN 模块  
  MCP2515 CAN module

- 12V 电源  
  12V power supply

- USB 数据线  
  USB cable

- Windows 电脑  
  Windows PC

---

## 软件需求 / Software Requirements

需要以下软件环境：

Required software environment:

- Windows 10 / Windows 11
- Python 3.x
- Arduino IDE
- Forza Horizon 6
- pyserial

安装 Python 依赖：

Install Python dependency:

```bash
pip install pyserial
```

---

## 安装流程 / Installation Guide

以下是推荐的基础安装流程。  
The following is the recommended basic installation process.

### 1. 从 GitHub 下载预先编译好的包 / Download the Precompiled Package from GitHub

从本项目的 GitHub Releases 页面下载预先编译好的发布包。  
Download the precompiled release package from the GitHub Releases page of this project.

Project:

https://github.com/JackieZ123430/BMW_G-Series_Cluster_fh6

> 注意：如果当前还没有正式 Release，说明项目仍在开发中，请等待后续版本发布。  
> Note: If there is no official Release yet, the project is still under development. Please wait for a later release.

---

### 2. 导入到开发板 / Upload or Import to the Development Board

根据你使用的硬件版本，将对应程序导入到开发板。  
Upload or import the correct firmware to your development board based on your hardware version.

支持的开发板：

Supported development boards:

- Arduino Mega 开发板  
  Arduino Mega development board

- Arduino Uno 开发板  
  Arduino Uno development board

请确认你使用的版本和下载的固件匹配。  
Please make sure the firmware version matches the development board you are using.

---

### 3. 按照图片接线 / Wire According to the Diagram

按照项目中的接线图片连接 BMW G-Series 仪表、开发板、MCP2515 CAN 模块和 12V 电源。  
Wire the BMW G-Series cluster, development board, MCP2515 CAN module, and 12V power supply according to the wiring diagram in the project.

基本硬件连接包括：

Basic hardware connections include:

- BMW G-Series 液晶仪表  
  BMW G-Series digital cluster

- Arduino Mega / Uno 开发板  
  Arduino Mega / Uno development board

- MCP2515 CAN 模块  
  MCP2515 CAN module

- 12V 电源  
  12V power supply

- USB 数据线连接电脑  
  USB cable connected to the PC

> 接线错误可能导致仪表、开发板或 CAN 模块损坏。请在通电前检查电源、CAN-H、CAN-L 和 GND。  
> Incorrect wiring may damage the cluster, development board, or CAN module. Please check power, CAN-H, CAN-L, and GND before powering on.

---

### 4. 设置 COM 口 / Set the COM Port

将开发板连接到电脑后，在 Windows 设备管理器中查看开发板的串口号。  
After connecting the development board to the PC, check the COM port in Windows Device Manager.

例如：

For example:

```text
COM4
COM6
COM8
```

然后在 Python 控制台程序中设置相同的 COM 口。  
Then set the same COM port in the Python control panel.

---

### 5. 设置游戏内遥测接口 / Set the In-Game Telemetry Output

在《极限竞速：地平线6》中打开遥测输出，并设置为：

Enable telemetry output in Forza Horizon 6 and set it to:

```text
Data Out: ON
Data Out IP Address: 127.0.0.1
Data Out IP Port: 4444
```

推荐设置：

Recommended setting:

```text
127.0.0.1
4444
```

---

### 6. 打开 Python 节点 / Start the Python Bridge Node

打开 Python 桥接程序。  
Start the Python bridge program.

Example:

```bash
python fh6_to_arduino_bridge_ui.py
```

在 Python 控制台中确认：

Confirm the following in the Python control panel:

- UDP IP 为 `127.0.0.1`  
  UDP IP is `127.0.0.1`

- UDP Port 为 `4444`  
  UDP Port is `4444`

- COM 口和开发板一致  
  COM port matches the development board

- Baud Rate 为 `115200`  
  Baud rate is `115200`

然后点击开始桥接。  
Then click Start to begin bridging.

启动游戏后，仪表会根据游戏遥测数据进行显示。  
After the game starts, the cluster will display information based on the game telemetry data.

---

## Forza Horizon 6 设置 / Forza Horizon 6 Setup

在游戏中打开遥测输出：

Enable telemetry output in the game:

```text
Settings
→ HUD and Gameplay
→ Data Out: ON
→ Data Out IP Address: 127.0.0.1
→ Data Out IP Port: 4444
```

然后运行 Python 桥接程序，并选择正确的 Arduino 串口。

Then run the Python bridge program and select the correct Arduino COM port.

---

## 使用方式 / Usage

### 1. 连接硬件 / Connect Hardware

连接 BMW G-Series 仪表、Arduino 开发板、MCP2515 CAN 模块和 12V 电源。

Connect the BMW G-Series cluster, Arduino board, MCP2515 CAN module, and 12V power supply.

### 2. 上传 Arduino 程序 / Upload Arduino Program

使用 Arduino IDE 将对应程序上传到 Arduino Mega 或 Arduino Uno。

Use Arduino IDE to upload the corresponding firmware to Arduino Mega or Arduino Uno.

### 3. 运行 Python 桥接程序 / Run Python Bridge

运行 Python 上位机程序，并选择正确的串口。

Run the Python bridge program and select the correct COM port.

Example:

```bash
python fh6_to_arduino_bridge_ui.py
```

### 4. 设置 Forza Horizon 6 遥测 / Set Forza Horizon 6 Telemetry

将 Forza Horizon 6 的 Data Out 设置为：

Set Forza Horizon 6 Data Out to:

```text
IP: 127.0.0.1
Port: 4444
```

### 5. 开始演示 / Start Demo

启动游戏后，仪表会根据遥测数据进行显示。  
部分功能需要在控制台中手动控制。

After starting the game, the cluster will display information based on telemetry data.  
Some features need to be controlled manually from the control panel.

---

## 当前限制 / Current Limitations

当前版本仍有一些限制：

The current version still has some limitations:

- Forza Horizon 6 遥测数据不完整  
  Forza Horizon 6 telemetry data is limited

- 部分功能需要控制台手动设置  
  Some features need to be manually controlled from the control panel

- 不同 BMW G-Series 仪表配置可能显示效果不同  
  Different BMW G-Series cluster configurations may behave differently

- 档位、驾驶模式、部分警告灯仍可能需要继续调整  
  Gear display, drive mode, and some warning lights may still need further adjustment

- 当前只是第一版演示，不代表最终效果  
  This is only the first demo version and does not represent the final result

---

## 已知问题 / Known Issues

目前已知问题包括：

Known issues include:

- R 档 / N 档显示可能还需要根据不同游戏数据继续修正  
  Reverse and neutral gear display may still need adjustment based on different game data

- 驾驶模式显示可能和仪表配置有关  
  Drive mode display may depend on the cluster configuration

- Forza Horizon 6 不提供完整车身数据  
  Forza Horizon 6 does not provide full vehicle body data

- 部分功能暂时只能手动控制  
  Some features can only be controlled manually for now

- 第一版程序仍有 bug，后续会继续修复  
  The first version still has bugs and will be improved later

---

## 项目状态 / Project Status

当前状态：

Current status:

```text
开发中 / Under development
第一版演示 / First demo version
功能不完整 / Not fully completed
仍有 bug / Bugs still exist
```

---

## 下载 / Download

当前项目仍在开发中，暂时没有正式 Release。

The project is still under development and does not have an official release yet.

后续稳定版本会发布到 GitHub Releases。

Stable versions may be published in GitHub Releases later.

---

## 作者 / Author

GitHub:

https://github.com/JackieZ123430

Bilibili:

https://space.bilibili.com/353124728

---

## 注意事项 / Notice

本项目仅用于研究学习和个人娱乐用途。  
This project is for research, learning, and personal entertainment only.

请勿用于商业用途。  
Do not use it for commercial purposes.

请勿非法分发。  
Do not distribute it illegally.

请勿倒卖。  
Do not resell it.

请勿用于真实车辆道路行驶环境。  
Do not use it in real road-driving environments.

免费下载分享，制作不易，希望大家支持。  
Free download and sharing. This project takes time to develop, so support is appreciated.

---

## 关于开发板源代码 / About Development Board Source Code

该开发板源代码将加密或不完整公开。  
The development board source code may be encrypted or not fully open-sourced.

公开仓库主要用于项目说明、上位机工具、配置文件和使用文档。  
This public repository is mainly for project documentation, PC-side tools, configuration files, and usage instructions.

---

## License / 许可说明

目前项目暂未选择正式开源许可证。  
No official open-source license has been selected yet.

在正式许可证发布前，默认保留所有权利。  
All rights are reserved until a license is added.

如果你需要商用或二次分发，请先联系作者。  
For commercial use or redistribution, please contact the author first.

---

## Disclaimer / 免责声明

本项目与 BMW、Forza、Microsoft、Playground Games、BeamNG GmbH 没有官方关系。  
This project is not affiliated with BMW, Forza, Microsoft, Playground Games, or BeamNG GmbH.

所有商标归其各自所有者所有。  
All trademarks belong to their respective owners.

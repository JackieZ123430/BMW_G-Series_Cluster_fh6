import socket
import struct
import serial
import time
import math
import threading
import queue
import tkinter as tk
import webbrowser
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

# ============================================================
# Forza Horizon 6 -> Arduino CSV Bridge with Control Panel
#
# Project / 项目地址:
#   https://github.com/JackieZ123430/BMW_G-Series_Cluster_fh6
# Author GitHub / 作者主页:
#   https://github.com/JackieZ123430
# Bilibili / B站主页:
#   https://space.bilibili.com/353124728
#
# Free download and sharing. Unauthorized redistribution/piracy will be pursued.
# 免费下载分享，盗版必究。
# The development board source code will be encrypted.
# 该开发板源代码将加密。
# For research use only. Do not use commercially. Do not distribute illegally.
# 仅用于研究使用，请勿商业使用，请勿非法分发。
##
# Use this to replace your old BeamNG bridge.
#
# FH6 provides:
#   speed / rpm / gear / fuel / throttle / brake / handbrake
#
# Control Panel provides manual values for:
#   ignition / engine running / doors / trunk / hood / lights
#   drive mode / water temp / oil temp / check engine / ABS/ESC/TCS
#
# Arduino CSV output protocol is kept compatible with your old bridge:
#   S,speed,rpm,gearLetter,gearIndex,ignition,engineRunning,...
# ============================================================


# -------------------------
# Defaults
# -------------------------

DEFAULT_UDP_IP = "127.0.0.1"
DEFAULT_UDP_PORT = 4444

DEFAULT_ARDUINO_PORT = "COM4"
DEFAULT_ARDUINO_BAUD = 115200

DEBUG_PRINT_INTERVAL = 0.5

# FH6 official Data Out packet is 324 bytes.
# Listed fields occupy 323 bytes, with one trailing padding byte.
FH6_PACKET_SIZE = 324
FH6_MIN_PACKET_SIZE = 323

SPEED_CAP_KMH = 330.0

# -------------------------
# Project / Author Info
# 项目与作者信息
# -------------------------

PROJECT_REPO_URL = "https://github.com/JackieZ123430/BMW_G-Series_Cluster_fh6"
AUTHOR_GITHUB_URL = "https://github.com/JackieZ123430"
AUTHOR_BILIBILI_URL = "https://space.bilibili.com/353124728"

PROJECT_NOTICE_TEXT = (
    "Free download and sharing. Unauthorized redistribution/piracy will be pursued.\\n"
    "免费下载分享，盗版必究。\\n"
    "The development board source code will be encrypted.\\n"
    "该开发板源代码将加密。\\n"
    "For research use only. Do not use commercially. Do not distribute illegally.\\n"
    "仅用于研究使用，请勿商业使用，请勿非法分发。"
)



# -------------------------
# Helpers
# -------------------------

def clamp_int(v, lo, hi):
    try:
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            v = 0
        v = int(round(float(v)))
    except Exception:
        v = 0
    return max(lo, min(hi, v))


def clamp_float(v, lo, hi, default=0.0):
    try:
        v = float(v)
        if math.isnan(v) or math.isinf(v):
            v = default
    except Exception:
        v = default
    return max(lo, min(hi, v))


def b(v):
    try:
        return 1 if int(v) != 0 else 0
    except Exception:
        return 0


def i32(data, o):
    return struct.unpack_from("<i", data, o)[0]


def u32(data, o):
    return struct.unpack_from("<I", data, o)[0]


def f32(data, o):
    return struct.unpack_from("<f", data, o)[0]


def u8(data, o):
    return struct.unpack_from("<B", data, o)[0]


def s8(data, o):
    return struct.unpack_from("<b", data, o)[0]


# -------------------------
# FH6 Data Out parser
# -------------------------

def parse_fh6_packet(data: bytes) -> dict:
    """
    Parse Forza Horizon 6 official Data Out packet.

    Important FH6 offsets:
      0   S32 IsRaceOn
      4   U32 TimestampMS
      8   F32 EngineMaxRpm
      12  F32 EngineIdleRpm
      16  F32 CurrentEngineRpm
      256 F32 Speed, meters/second
      288 F32 Fuel, 0.0 ~ 1.0
      315 U8  Accel, 0 ~ 255
      316 U8  Brake, 0 ~ 255
      318 U8  HandBrake, 0 ~ 255
      319 U8  Gear
      320 S8  Steer
    """

    if len(data) < FH6_MIN_PACKET_SIZE:
        raise ValueError(f"FH6 packet too short: {len(data)} bytes, expected {FH6_PACKET_SIZE}")

    race_on = i32(data, 0)
    timestamp = u32(data, 4)

    engine_max_rpm = f32(data, 8)
    engine_idle_rpm = f32(data, 12)
    rpm = f32(data, 16)

    speed_ms = f32(data, 256)
    speed_kmh = speed_ms * 3.6

    fuel = f32(data, 288)

    accel_raw = u8(data, 315)
    brake_raw = u8(data, 316)
    handbrake_raw = u8(data, 318)
    gear_raw = u8(data, 319)
    gear_raw_s8 = s8(data, 319)
    steer_raw = s8(data, 320)

    # FH6 signed gear mapping:
    #   -1 / 255 = Reverse
    #    0       = Neutral
    #    1       = 1st
    #    2       = 2nd
    # This fixes:
    #   - R not showing
    #   - N becoming M8/D8 when raw byte is 255
    if gear_raw_s8 == -1 or gear_raw == 255:
        gear_letter = "R"
        gear_index = 0
    elif gear_raw == 0:
        gear_letter = "N"
        gear_index = 0
    else:
        gear_letter = "D"
        gear_index = clamp_int(gear_raw, 1, 8)

    throttle_pct = clamp_int(accel_raw / 255.0 * 100.0, 0, 100)
    brake_pct = clamp_int(brake_raw / 255.0 * 100.0, 0, 100)

    rpm_clean = clamp_float(rpm, 0.0, 12000.0)
    speed_clean = clamp_float(speed_kmh, 0.0, SPEED_CAP_KMH)
    fuel_clean = clamp_float(fuel, 0.0, 1.0)

    engine_running = 1 if race_on and rpm_clean > 300 else 0
    ignition = 3 if engine_running else 0

    return {
        "time": timestamp,

        "speedKmh": speed_clean,
        "rpm": rpm_clean,

        "gearLetter": gear_letter,
        "gearIndex": gear_index,

        "ignition": ignition,
        "engineRunning": engine_running,

        "doorFL": 0,
        "doorFR": 0,
        "doorRL": 0,
        "doorRR": 0,
        "trunkOpen": 0,
        "hoodOpen": 0,

        "parkingBrake": 1 if handbrake_raw > 10 else 0,

        "absAvailable": 0,
        "absActive": 0,
        "escAvailable": 0,
        "escActive": 0,
        "tcsAvailable": 0,
        "tcsActive": 0,

        "abs": 0,
        "isABSBrakeActive": 0,
        "hasABS": 0,
        "hasESC": 0,
        "hasTCS": 0,
        "esc": 0,
        "tcs": 0,
        "isTCBrakeActive": 0,
        "isYCBrakeActive": 0,

        "highBeam": 0,
        "lowBeam": 0,
        "fog": 0,
        "signalL": 0,
        "signalR": 0,
        "hazard": 0,

        "brakelights": 1 if brake_raw > 5 else 0,
        "battery": 0,
        "oil": 0,
        "checkengine": 0,

        "fuel": fuel_clean,
        "lowfuel": 1 if fuel_clean < 0.12 else 0,

        # FH6 Data Out has no real water/oil temp.
        "waterTemp": 90,
        "oilTemp": 90,

        "tireDefFL": 0,
        "tireDefFR": 0,
        "tireDefRL": 0,
        "tireDefRR": 0,

        "throttleInput": throttle_pct,
        "brakeInput": brake_pct,
        "engineLoad": throttle_pct,

        # FH6 has no BMW drive mode; UI overrides this.
        # Default is Arduino input 2 = Sport, matching your current Arduino mapDriveModeToG().
        "driveMode": 2,

        "airspeedKmh": speed_clean,

        "_fh6_packet_len": len(data),
        "_fh6_race_on": race_on,
        "_fh6_engine_max_rpm": engine_max_rpm,
        "_fh6_engine_idle_rpm": engine_idle_rpm,
        "_fh6_accel_raw": accel_raw,
        "_fh6_brake_raw": brake_raw,
        "_fh6_handbrake_raw": handbrake_raw,
        "_fh6_gear_raw": gear_raw,
        "_fh6_gear_raw_s8": gear_raw_s8,
        "_fh6_steer_raw": steer_raw,
    }


# -------------------------
# UI overrides
# -------------------------

IGNITION_MAP = {
    "Auto from FH6 / 自动读取FH6": None,
    "Off / 熄火 (0)": 0,
    "ACC / 附件电 (1)": 1,
    "ON / 点火但不启动 (2)": 2,
    "Engine running / 发动机启动 (3)": 3,
}

DRIVE_MODE_MAP = {
    # IMPORTANT:
    # This value is NOT raw BMW 0x3D8 mode.
    # It is the input value expected by the Arduino function:
    #   mapDriveModeToG(game.driveMode)
    #
    # Arduino source currently maps:
    #   1 -> 0x0A  comfort/adaptive by your source comment
    #   2 -> 0x09  sport by your source comment
    #   3 -> 0x02  sport+
    #   4 -> 0x06  none / DSC off
    #   5 -> 0x06  none / 2WD
    #   6 -> 0x06  none / drift
    "Default / 默认 -> Arduino default/adaptive": 0,
    "Comfort / 舒适 -> Arduino input 1": 1,
    "Sport / 运动 -> Arduino input 2": 2,
    "Sport Plus / 运动增强 -> Arduino input 3": 3,
    "DSC Off / 关闭DSC -> Arduino input 4": 4,
    "2WD / 后驱 -> Arduino input 5": 5,
    "Drift / 漂移 -> Arduino input 6": 6,
}

GEAR_PARSE_VALUES = [
    "FH6 signed correct / 正确模式: -1=R, 0=N, 1=1档",
    "FH6 unsigned reverse / 反向兼容: 255=R, 0=N, 1=1档",
    "Legacy Forza / 旧模式: 0=R, 1=N, 2=1档",
]

GEAR_LETTER_MODE_VALUES = [
    "Auto from FH6 / 自动读取FH6",
    "Force D / 强制显示D",
    "Force S / 强制显示S",
    "Force M / 强制显示M",
]

PARKING_BRAKE_MAP = {
    "Auto from FH6 / 自动读取FH6": None,
    "Force Off / 强制关闭": 0,
    "Force On / 强制开启": 1,
}

LOW_FUEL_MAP = {
    "Auto by fuel / 按油量自动": None,
    "Force Off / 强制关闭": 0,
    "Force On / 强制开启": 1,
}

GEAR_OVERRIDE_VALUES = [
    "Auto from FH6 / 自动读取FH6",
    "P / 停车档",
    "R / 倒档",
    "N / 空档",
    "D / 前进档",
    "S / 运动档",
    "M / 手动档",
]


def apply_manual_overrides(d: dict, state: dict) -> dict:
    # Gear parser mode.
    # This is applied before manual/full gear overrides.
    gear_parse_mode = state.get("gear_parse_mode", "FH6 signed correct / 正确模式: -1=R, 0=N, 1=1档")
    raw_gear = d.get("_fh6_gear_raw", None)
    raw_gear_s8 = d.get("_fh6_gear_raw_s8", None)

    if raw_gear is not None:
        raw_gear = clamp_int(raw_gear, 0, 255)

        if raw_gear_s8 is None:
            raw_gear_s8 = raw_gear - 256 if raw_gear >= 128 else raw_gear
        raw_gear_s8 = clamp_int(raw_gear_s8, -128, 127)

        if gear_parse_mode == "Legacy Forza / 旧模式: 0=R, 1=N, 2=1档":
            # Old Forza-style mapping:
            #   0 = R, 1 = N, 2 = 1st
            if raw_gear == 0:
                d["gearLetter"] = "R"
                d["gearIndex"] = 0
            elif raw_gear == 1:
                d["gearLetter"] = "N"
                d["gearIndex"] = 0
            else:
                d["gearLetter"] = "D"
                d["gearIndex"] = clamp_int(raw_gear - 1, 1, 8)
        else:
            # Correct FH6-style signed mapping:
            #   -1 / 255 = R
            #    0       = N
            #    1       = 1st
            #    2       = 2nd
            if raw_gear_s8 == -1 or raw_gear == 255:
                d["gearLetter"] = "R"
                d["gearIndex"] = 0
            elif raw_gear == 0:
                d["gearLetter"] = "N"
                d["gearIndex"] = 0
            else:
                d["gearLetter"] = "D"
                d["gearIndex"] = clamp_int(raw_gear, 1, 8)

    # Gear letter display mode.
    # This preserves the auto gear number but lets the cluster show D/S/M.
    # IMPORTANT: only apply D/S/M force to forward gears.
    # Do not convert R/N/P into M8/D8.
    gear_letter_mode = state.get("gear_letter_mode", "Auto from FH6 / 自动读取FH6")
    current_letter = str(d.get("gearLetter", "N"))[:1]
    current_index = clamp_int(d.get("gearIndex", 0), 0, 8)

    if current_index > 0 and current_letter in ["D", "S", "M"]:
        if gear_letter_mode == "Force D / 强制显示D":
            d["gearLetter"] = "D"
        elif gear_letter_mode == "Force S / 强制显示S":
            d["gearLetter"] = "S"
        elif gear_letter_mode == "Force M / 强制显示M":
            d["gearLetter"] = "M"

    # Ignition
    ignition_mode = state.get("ignition_mode", "Auto from FH6 / 自动读取FH6")
    ignition_value = IGNITION_MAP.get(ignition_mode)

    if ignition_value is not None:
        d["ignition"] = ignition_value
        d["engineRunning"] = 1 if ignition_value == 3 else 0

        # When manually off, make RPM zero so the cluster does not look alive.
        if ignition_value == 0:
            d["rpm"] = 0
            d["speedKmh"] = 0

    # Gear override
    gear_mode = state.get("gear_override", "Auto from FH6 / 自动读取FH6")
    if gear_mode != "Auto from FH6 / 自动读取FH6":
        d["gearLetter"] = str(gear_mode).split(" / ")[0]
        if d["gearLetter"] in ["P", "R", "N"]:
            d["gearIndex"] = 0
        else:
            d["gearIndex"] = clamp_int(state.get("gear_index", 1), 1, 8)

    # Doors / trunk / hood
    for key in ["doorFL", "doorFR", "doorRL", "doorRR", "trunkOpen", "hoodOpen"]:
        d[key] = b(state.get(key, 0))

    # Parking brake
    pb_mode = state.get("parking_brake_mode", "Auto from FH6 / 自动读取FH6")
    pb_value = PARKING_BRAKE_MAP.get(pb_mode)
    if pb_value is not None:
        d["parkingBrake"] = pb_value

    # ABS / ESC / TCS manual lamps/states
    d["abs"] = b(state.get("abs", 0))
    d["absActive"] = d["abs"]

    d["esc"] = b(state.get("esc", 0))
    d["escActive"] = d["esc"]

    d["tcs"] = b(state.get("tcs", 0))
    d["tcsActive"] = d["tcs"]

    # Lights and signals
    for key in ["highBeam", "lowBeam", "fog", "signalL", "signalR", "hazard"]:
        d[key] = b(state.get(key, 0))

    # Temperatures
    d["waterTemp"] = clamp_int(state.get("waterTemp", 90), -40, 160)
    d["oilTemp"] = clamp_int(state.get("oilTemp", 90), -40, 180)

    # Drive mode.
    # Send Arduino-compatible input value, not raw BMW mode value.
    # Your Arduino then calls mapDriveModeToG(game.driveMode).
    drive_mode_label = state.get("drive_mode_label", "Sport / 运动 -> Arduino input 2")
    d["driveMode"] = DRIVE_MODE_MAP.get(drive_mode_label, 2)

    # Check engine
    d["checkengine"] = b(state.get("checkengine", 0))

    # Fuel override
    if b(state.get("fuel_manual_enabled", 0)):
        fuel_pct = clamp_float(state.get("fuel_pct", 50), 0.0, 100.0, default=50.0)
        d["fuel"] = fuel_pct / 100.0

    # Low fuel override
    lowfuel_mode = state.get("lowfuel_mode", "Auto by fuel / 按油量自动")
    lowfuel_value = LOW_FUEL_MAP.get(lowfuel_mode)
    if lowfuel_value is None:
        d["lowfuel"] = 1 if float(d.get("fuel", 0.0) or 0.0) < 0.12 else 0
    else:
        d["lowfuel"] = lowfuel_value

    # Seatbelt.
    # Current standard CSV protocol does not include seatbelt.
    # If "appendSeatbeltField" is enabled, to_arduino_csv() adds it as the last field.
    # Arduino firmware must be updated to read this extra field and send the correct CAN frame.
    d["seatbeltDriver"] = b(state.get("seatbeltDriver", 1))
    d["appendSeatbeltField"] = b(state.get("appendSeatbeltField", 0))

    return d


# -------------------------
# common dict -> Arduino CSV
# Keep compatible with your old bridge.
# -------------------------

def to_arduino_csv(d: dict) -> str:
    speed_raw = float(d.get("speedKmh", 0) or 0)
    speed = round(max(0.0, min(SPEED_CAP_KMH, speed_raw)), 2)

    rpm = clamp_int(d.get("rpm", 0), 0, 9000)

    gear_letter = d.get("gearLetter", "N")
    if gear_letter not in ["P", "R", "N", "D", "S", "M"]:
        gear_letter = "D"

    gear_index = clamp_int(d.get("gearIndex", 0), 0, 8)

    ignition = clamp_int(d.get("ignition", 0), 0, 3)
    engine_running = b(d.get("engineRunning", 0))

    door_fl = b(d.get("doorFL", 0))
    door_fr = b(d.get("doorFR", 0))
    door_rl = b(d.get("doorRL", 0))
    door_rr = b(d.get("doorRR", 0))

    trunk_open = b(d.get("trunkOpen", 0))
    hood_open = b(d.get("hoodOpen", 0))

    handbrake = b(d.get("parkingBrake", 0))

    abs_v = b(d.get("abs", 0) or d.get("absActive", 0))
    esc_v = b(d.get("esc", 0) or d.get("escActive", 0))
    tcs_v = b(d.get("tcs", 0) or d.get("tcsActive", 0))

    high_beam = b(d.get("highBeam", 0))
    low_beam = b(d.get("lowBeam", 0))
    fog = b(d.get("fog", 0))

    signal_l = b(d.get("signalL", 0))
    signal_r = b(d.get("signalR", 0))
    hazard = b(d.get("hazard", 0))

    fuel_raw = float(d.get("fuel", 0.0) or 0.0)
    if fuel_raw > 1.0:
        fuel_raw = fuel_raw / 100.0

    fuel_f = round(max(0.0, min(1.0, fuel_raw)), 4)
    fuel_pct = fuel_f * 100.0

    water_temp = clamp_int(d.get("waterTemp", 90), -40, 160)
    oil_temp = clamp_int(d.get("oilTemp", 90), -40, 180)

    throttle = clamp_int(d.get("throttleInput", 0), 0, 100)
    brake = clamp_int(d.get("brakeInput", 0), 0, 100)

    # Arduino source expects game.driveMode input 0..6.
    # Do NOT send raw BMW 0x01..0x0A here, because Arduino maps it again.
    drive_mode = clamp_int(d.get("driveMode", 2), 0, 6)

    checkengine = b(d.get("checkengine", 0))
    lowfuel = b(d.get("lowfuel", 0))
    if fuel_pct < 12.0:
        lowfuel = 1

    line = (
        f"S,"
        f"{speed},"
        f"{rpm},"
        f"{gear_letter},"
        f"{gear_index},"
        f"{ignition},"
        f"{engine_running},"
        f"{door_fl},"
        f"{door_fr},"
        f"{door_rl},"
        f"{door_rr},"
        f"{trunk_open},"
        f"{hood_open},"
        f"{handbrake},"
        f"{abs_v},"
        f"{esc_v},"
        f"{tcs_v},"
        f"{high_beam},"
        f"{low_beam},"
        f"{fog},"
        f"{signal_l},"
        f"{signal_r},"
        f"{hazard},"
        f"{fuel_f:.4f},"
        f"{water_temp},"
        f"{oil_temp},"
        f"{throttle},"
        f"{brake},"
        f"{drive_mode},"
        f"{checkengine},"
        f"{lowfuel}"
    )

    if b(d.get("appendSeatbeltField", 0)):
        # Extra field, only enable when Arduino firmware is ready:
        # 1 = driver seatbelt buckled, 0 = unbuckled.
        line += f",{b(d.get('seatbeltDriver', 1))}"

    line += "\n"

    return line


# -------------------------
# Bridge worker
# -------------------------

class BridgeWorker:
    def __init__(self, log_queue, state_lock, manual_state):
        self.log_queue = log_queue
        self.state_lock = state_lock
        self.manual_state = manual_state

        self.stop_event = threading.Event()
        self.thread = None

        self.sock = None
        self.ser = None

    def is_running(self):
        return self.thread is not None and self.thread.is_alive()

    def start(self, udp_ip, udp_port, serial_port, serial_baud):
        if self.is_running():
            self.log("Bridge already running / 桥接已经在运行。")
            return

        self.stop_event.clear()
        self.thread = threading.Thread(
            target=self._run,
            args=(udp_ip, udp_port, serial_port, serial_baud),
            daemon=True
        )
        self.thread.start()

    def stop(self):
        self.stop_event.set()

        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass

        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass

        self.sock = None
        self.ser = None

    def log(self, msg):
        try:
            self.log_queue.put_nowait(str(msg))
        except Exception:
            pass

    def get_state_snapshot(self):
        with self.state_lock:
            return dict(self.manual_state)

    def _run(self, udp_ip, udp_port, serial_port, serial_baud):
        last_print = 0
        last_packet_len = None

        try:
            self.log("Opening serial: {} {}".format(serial_port, serial_baud))
            self.ser = serial.Serial(serial_port, int(serial_baud), timeout=0)
            time.sleep(2.0)

            self.log("Listening UDP: {}:{}".format(udp_ip, udp_port))
            self.log("Set FH6 Data Out IP Address to: {}".format(udp_ip))
            self.log("Set FH6 Data Out IP Port to: {}".format(udp_port))
            self.log("Expected FH6 packet size: {} bytes".format(FH6_PACKET_SIZE))

            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((udp_ip, int(udp_port)))
            self.sock.settimeout(0.25)

            self.log("Bridge started / 桥接已启动。")

            while not self.stop_event.is_set():
                try:
                    data, addr = self.sock.recvfrom(4096)
                except socket.timeout:
                    continue
                except OSError:
                    break

                try:
                    pkt = parse_fh6_packet(data)
                    state = self.get_state_snapshot()
                    pkt = apply_manual_overrides(pkt, state)

                    line = to_arduino_csv(pkt)
                    self.ser.write(line.encode("ascii", errors="ignore"))

                    now = time.time()
                    if now - last_print > DEBUG_PRINT_INTERVAL:
                        last_print = now

                        packet_len = pkt.get("_fh6_packet_len")
                        if packet_len != last_packet_len:
                            last_packet_len = packet_len
                            self.log(f"FH6 packet length detected: {packet_len} bytes")

                        gear_dbg = (
                            f" | gearRaw={pkt.get('_fh6_gear_raw')}"
                            f"/s8={pkt.get('_fh6_gear_raw_s8')}"
                            f" -> {pkt.get('gearLetter')}{pkt.get('gearIndex')}"
                        )
                        self.log(line.strip() + gear_dbg)

                except Exception as e:
                    self.log("BAD PACKET: {} len={}".format(e, len(data)))

        except Exception as e:
            self.log("Bridge stopped/error: {}".format(e))

        finally:
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass

            try:
                if self.ser:
                    self.ser.close()
            except Exception:
                pass

            self.sock = None
            self.ser = None
            self.log("Bridge not running / 桥接未运行。")


# -------------------------
# Tkinter UI
# -------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FH6 -> Arduino Bridge Control Panel / FH6 仪表桥接控制台")
        self.geometry("920x720")
        self.minsize(860, 650)

        self.log_queue = queue.Queue()
        self.state_lock = threading.Lock()
        self.manual_state = {}

        self.worker = BridgeWorker(self.log_queue, self.state_lock, self.manual_state)

        self.vars = {}
        self._build_ui()
        self.sync_state_from_ui()

        self.after(100, self.process_log_queue)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _add_var(self, name, var):
        self.vars[name] = var

        def _callback(*args):
            self.sync_state_from_ui()

        try:
            var.trace_add("write", _callback)
        except Exception:
            pass

        return var

    def open_url(self, url):
        try:
            webbrowser.open(url)
            self.log(f"Open URL / 打开链接: {url}")
        except Exception as e:
            self.log(f"Open URL failed / 打开链接失败: {e}")

    def copy_project_info(self):
        info = (
            "BMW G-Series Cluster FH6\\n"
            f"Project / 项目地址: {PROJECT_REPO_URL}\\n"
            f"GitHub / 作者主页: {AUTHOR_GITHUB_URL}\\n"
            f"Bilibili / B站主页: {AUTHOR_BILIBILI_URL}\\n\\n"
            f"{PROJECT_NOTICE_TEXT}"
        )
        try:
            self.clipboard_clear()
            self.clipboard_append(info)
            self.log("Project info copied / 项目信息已复制到剪贴板。")
        except Exception as e:
            self.log(f"Copy failed / 复制失败: {e}")

    def _build_ui(self):
        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)

        # Connection
        conn = ttk.LabelFrame(outer, text="Connection / 连接设置")
        conn.pack(fill="x", padx=4, pady=4)

        self.udp_ip_var = self._add_var("udp_ip", tk.StringVar(value=DEFAULT_UDP_IP))
        self.udp_port_var = self._add_var("udp_port", tk.StringVar(value=str(DEFAULT_UDP_PORT)))
        self.com_var = self._add_var("com", tk.StringVar(value=DEFAULT_ARDUINO_PORT))
        self.baud_var = self._add_var("baud", tk.StringVar(value=str(DEFAULT_ARDUINO_BAUD)))

        ttk.Label(conn, text="UDP IP / 接收地址").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Entry(conn, textvariable=self.udp_ip_var, width=16).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(conn, text="UDP Port / 接收端口").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        ttk.Entry(conn, textvariable=self.udp_port_var, width=8).grid(row=0, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(conn, text="Arduino COM / 串口").grid(row=0, column=4, sticky="w", padx=6, pady=4)
        ttk.Entry(conn, textvariable=self.com_var, width=10).grid(row=0, column=5, sticky="w", padx=6, pady=4)

        ttk.Label(conn, text="Baud / 波特率").grid(row=0, column=6, sticky="w", padx=6, pady=4)
        ttk.Entry(conn, textvariable=self.baud_var, width=8).grid(row=0, column=7, sticky="w", padx=6, pady=4)

        self.start_btn = ttk.Button(conn, text="Start / 开始桥接", command=self.start_bridge)
        self.start_btn.grid(row=0, column=8, padx=6, pady=4)

        self.stop_btn = ttk.Button(conn, text="Stop / 停止桥接", command=self.stop_bridge)
        self.stop_btn.grid(row=0, column=9, padx=6, pady=4)

        # Main control area
        controls = ttk.Frame(outer)
        controls.pack(fill="both", expand=False, padx=4, pady=4)

        left = ttk.Frame(controls)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))

        right = ttk.Frame(controls)
        right.pack(side="left", fill="both", expand=True, padx=(5, 0))

        # Power / drive
        power = ttk.LabelFrame(left, text="Power / Gear / Drive Mode / 电源、档位、驾驶模式")
        power.pack(fill="x", pady=4)

        self.ignition_var = self._add_var("ignition_mode", tk.StringVar(value="Auto from FH6 / 自动读取FH6"))
        self.drive_mode_var = self._add_var("drive_mode_label", tk.StringVar(value="Sport / 运动 -> Arduino input 2"))
        self.gear_parse_var = self._add_var("gear_parse_mode", tk.StringVar(value="FH6 signed correct / 正确模式: -1=R, 0=N, 1=1档"))
        self.gear_letter_mode_var = self._add_var("gear_letter_mode", tk.StringVar(value="Auto from FH6 / 自动读取FH6"))
        self.gear_override_var = self._add_var("gear_override", tk.StringVar(value="Auto from FH6 / 自动读取FH6"))
        self.gear_index_var = self._add_var("gear_index", tk.IntVar(value=1))

        ttk.Label(power, text="Ignition / 点火状态").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            power,
            textvariable=self.ignition_var,
            values=list(IGNITION_MAP.keys()),
            state="readonly",
            width=26
        ).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(power, text="Drive Mode / 驾驶模式").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            power,
            textvariable=self.drive_mode_var,
            values=list(DRIVE_MODE_MAP.keys()),
            state="readonly",
            width=26
        ).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(power, text="FH6 Gear Parser / FH6 档位解析").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            power,
            textvariable=self.gear_parse_var,
            values=GEAR_PARSE_VALUES,
            state="readonly",
            width=32
        ).grid(row=2, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(power, text="Letter D/S/M / 显示 D/S/M").grid(row=3, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            power,
            textvariable=self.gear_letter_mode_var,
            values=GEAR_LETTER_MODE_VALUES,
            state="readonly",
            width=26
        ).grid(row=3, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(power, text="Full Gear Override / 完整档位覆盖").grid(row=4, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            power,
            textvariable=self.gear_override_var,
            values=GEAR_OVERRIDE_VALUES,
            state="readonly",
            width=26
        ).grid(row=4, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(power, text="Manual Gear Index / 手动档位数字").grid(row=5, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(
            power,
            from_=1,
            to=8,
            textvariable=self.gear_index_var,
            width=8
        ).grid(row=5, column=1, sticky="w", padx=6, pady=4)

        # Body
        body = ttk.LabelFrame(left, text="Body / Doors / 车身与车门")
        body.pack(fill="x", pady=4)

        for name, text, row, col in [
            ("doorFL", "Front Left Door / 左前门", 0, 0),
            ("doorFR", "Front Right Door / 右前门", 0, 1),
            ("doorRL", "Rear Left Door / 左后门", 1, 0),
            ("doorRR", "Rear Right Door / 右后门", 1, 1),
            ("trunkOpen", "Trunk / 后备箱", 2, 0),
            ("hoodOpen", "Hood / 引擎盖", 2, 1),
        ]:
            var = self._add_var(name, tk.IntVar(value=0))
            ttk.Checkbutton(body, text=text, variable=var).grid(row=row, column=col, sticky="w", padx=6, pady=3)

        # Lights
        lights = ttk.LabelFrame(left, text="Lights / Signals / 灯光与转向灯")
        lights.pack(fill="x", pady=4)

        for name, text, row, col in [
            ("lowBeam", "Low Beam / 近光灯", 0, 0),
            ("highBeam", "High Beam / 远光灯", 0, 1),
            ("fog", "Fog / 雾灯", 1, 0),
            ("signalL", "Left Signal / 左转向", 1, 1),
            ("signalR", "Right Signal / 右转向", 2, 0),
            ("hazard", "Hazard / 双闪", 2, 1),
        ]:
            var = self._add_var(name, tk.IntVar(value=0))
            ttk.Checkbutton(lights, text=text, variable=var).grid(row=row, column=col, sticky="w", padx=6, pady=3)

        # Vehicle states
        states = ttk.LabelFrame(right, text="Vehicle States / Warning / 车辆状态与警告灯")
        states.pack(fill="x", pady=4)

        self.parking_brake_var = self._add_var("parking_brake_mode", tk.StringVar(value="Auto from FH6 / 自动读取FH6"))
        self.lowfuel_mode_var = self._add_var("lowfuel_mode", tk.StringVar(value="Auto by fuel / 按油量自动"))
        self.checkengine_var = self._add_var("checkengine", tk.IntVar(value=0))
        self.abs_var = self._add_var("abs", tk.IntVar(value=0))
        self.esc_var = self._add_var("esc", tk.IntVar(value=0))
        self.tcs_var = self._add_var("tcs", tk.IntVar(value=0))
        self.seatbelt_var = self._add_var("seatbeltDriver", tk.IntVar(value=1))
        self.append_seatbelt_var = self._add_var("appendSeatbeltField", tk.IntVar(value=0))

        ttk.Label(states, text="Parking Brake / 手刹").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            states,
            textvariable=self.parking_brake_var,
            values=list(PARKING_BRAKE_MAP.keys()),
            state="readonly",
            width=18
        ).grid(row=0, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(states, text="Low Fuel / 低油量警告").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Combobox(
            states,
            textvariable=self.lowfuel_mode_var,
            values=list(LOW_FUEL_MAP.keys()),
            state="readonly",
            width=18
        ).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Checkbutton(states, text="Check Engine / 发动机故障灯", variable=self.checkengine_var).grid(row=2, column=0, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(states, text="ABS / 防抱死", variable=self.abs_var).grid(row=2, column=1, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(states, text="ESC / 车身稳定", variable=self.esc_var).grid(row=3, column=0, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(states, text="TCS / 牵引力控制", variable=self.tcs_var).grid(row=3, column=1, sticky="w", padx=6, pady=3)

        ttk.Checkbutton(states, text="Driver Seatbelt Buckled / 主驾安全带已系", variable=self.seatbelt_var).grid(row=4, column=0, sticky="w", padx=6, pady=3)
        ttk.Checkbutton(states, text="Append Seatbelt CSV Field / 追加安全带CSV字段", variable=self.append_seatbelt_var).grid(row=4, column=1, sticky="w", padx=6, pady=3)

        # Fuel / temp
        fuel_temp = ttk.LabelFrame(right, text="Fuel / Temperature / 油量与温度")
        fuel_temp.pack(fill="x", pady=4)

        self.fuel_manual_var = self._add_var("fuel_manual_enabled", tk.IntVar(value=0))
        self.fuel_pct_var = self._add_var("fuel_pct", tk.DoubleVar(value=50.0))
        self.water_temp_var = self._add_var("waterTemp", tk.IntVar(value=90))
        self.oil_temp_var = self._add_var("oilTemp", tk.IntVar(value=90))

        ttk.Checkbutton(fuel_temp, text="Manual Fuel / 手动油量", variable=self.fuel_manual_var).grid(row=0, column=0, sticky="w", padx=6, pady=4)
        ttk.Scale(fuel_temp, from_=0, to=100, variable=self.fuel_pct_var, orient="horizontal", length=220).grid(row=0, column=1, padx=6, pady=4)
        ttk.Label(fuel_temp, textvariable=self.fuel_pct_var, width=6).grid(row=0, column=2, sticky="w", padx=6, pady=4)

        ttk.Label(fuel_temp, text="Water Temp °C / 水温").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(fuel_temp, from_=-40, to=160, textvariable=self.water_temp_var, width=8).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(fuel_temp, text="Oil Temp °C / 油温").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        ttk.Spinbox(fuel_temp, from_=-40, to=180, textvariable=self.oil_temp_var, width=8).grid(row=2, column=1, sticky="w", padx=6, pady=4)

        # Notes
        notes = ttk.LabelFrame(right, text="FH6 Setup / FH6 游戏设置")
        notes.pack(fill="x", pady=4)

        text = (
            "In FH6 / 在 FH6 里面设置：\n"
            "Settings -> HUD and Gameplay -> Data Out: ON\n"
            "Data Out IP Address / 输出IP: 127.0.0.1\n"
            "Data Out IP Port / 输出端口: 4444\n\n"
            "FH6 only gives speed/rpm/gear/fuel/throttle/brake/handbrake.\n"
            "FH6 只提供速度、转速、档位、油量、油门、刹车、手刹。\n"
            "Other car states are controlled by this panel.\n"
            "其他车身状态由这个控制台手动控制。\n"
            "Seatbelt needs Arduino/CAN support; CSV append is optional.\n"
            "安全带需要 Arduino/CAN 端支持；追加CSV字段是可选的。"
        )
        ttk.Label(notes, text=text, justify="left").pack(anchor="w", padx=6, pady=6)

        # Project info / 项目信息
        project = ttk.LabelFrame(right, text="Project / 项目信息")
        project.pack(fill="x", pady=4)

        ttk.Label(
            project,
            text="BMW G-Series Cluster FH6",
            font=("TkDefaultFont", 10, "bold")
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=6, pady=(6, 2))

        ttk.Label(project, text="Project / 项目地址").grid(row=1, column=0, sticky="w", padx=6, pady=2)
        ttk.Button(
            project,
            text=PROJECT_REPO_URL,
            command=lambda: self.open_url(PROJECT_REPO_URL)
        ).grid(row=1, column=1, sticky="ew", padx=6, pady=2)

        ttk.Label(project, text="GitHub / 作者主页").grid(row=2, column=0, sticky="w", padx=6, pady=2)
        ttk.Button(
            project,
            text=AUTHOR_GITHUB_URL,
            command=lambda: self.open_url(AUTHOR_GITHUB_URL)
        ).grid(row=2, column=1, sticky="ew", padx=6, pady=2)

        ttk.Label(project, text="Bilibili / B站主页").grid(row=3, column=0, sticky="w", padx=6, pady=2)
        ttk.Button(
            project,
            text=AUTHOR_BILIBILI_URL,
            command=lambda: self.open_url(AUTHOR_BILIBILI_URL)
        ).grid(row=3, column=1, sticky="ew", padx=6, pady=2)

        project.columnconfigure(1, weight=1)

        ttk.Label(
            project,
            text=PROJECT_NOTICE_TEXT,
            justify="left",
            wraplength=420
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=6, pady=(6, 4))

        ttk.Button(
            project,
            text="Copy Project Info / 复制项目信息",
            command=self.copy_project_info
        ).grid(row=5, column=0, columnspan=2, sticky="w", padx=6, pady=(2, 6))

        # Log
        log_frame = ttk.LabelFrame(outer, text="Console / 输出日志")
        log_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.log_box = ScrolledText(log_frame, height=12, wrap="none")
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)

        self.log("Ready / 就绪。Set FH6 Data Out to 127.0.0.1:4444，然后点击 Start / 开始桥接。")
        self.log(f"Project / 项目地址: {PROJECT_REPO_URL}")

    def log(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{ts}] {msg}\n")
        self.log_box.see("end")

    def process_log_queue(self):
        while True:
            try:
                msg = self.log_queue.get_nowait()
            except queue.Empty:
                break
            self.log(msg)

        self.after(100, self.process_log_queue)

    def sync_state_from_ui(self):
        # Do not read widgets that do not exist yet.
        if not hasattr(self, "vars"):
            return

        new_state = {}

        for name, var in self.vars.items():
            try:
                new_state[name] = var.get()
            except Exception:
                pass

        with self.state_lock:
            self.manual_state.clear()
            self.manual_state.update(new_state)

    def start_bridge(self):
        self.sync_state_from_ui()

        udp_ip = self.udp_ip_var.get().strip() or DEFAULT_UDP_IP
        udp_port = clamp_int(self.udp_port_var.get(), 1, 65535)

        com = self.com_var.get().strip() or DEFAULT_ARDUINO_PORT
        baud = clamp_int(self.baud_var.get(), 9600, 1000000)

        self.worker.start(udp_ip, udp_port, com, baud)

    def stop_bridge(self):
        self.worker.stop()
        self.log("Stop requested / 已请求停止。")

    def on_close(self):
        self.worker.stop()
        self.destroy()


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

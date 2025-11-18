import time
from enum import IntEnum

try:
    from pymodbus.client import ModbusSerialClient
    from loguru import logger
except ImportError:
    print("pymodbus, pyserial, loguru 为安装，无法运行程序，请先运行 pip install -r requirements.txt 或 pip install pymodbus pyserial loguru 安装依赖包。")
    exit(1)

class RD60XX_REG(IntEnum):
    """
    Enumeration class representing the different register addresses.
    """
    PRODUCT_MODEL       = 0x0000  # R    产品型号
    SN_H                = 0x0001  # R    产品序列号高16位
    SN_L                = 0x0002  # R    产品序列号低16位     
    FW_VERSION          = 0x0003  # R    产品固件版本
    C_TEMPERATURE_SIGN  = 0x0004  # R    系统摄氏温度正负（0：正  1：负）
    C_TEMPERATURE_VALUE = 0x0005  # R    系统摄氏温度数值          
    F_TEMPERATURE_SIGN  = 0x0006  # R    系统华氏温度正负（0：正  1：负）
    F_TEMPERATURE_VALUE = 0x0007  # R    系统华氏温度数值 
    VOLTAGE             = 0x0008  # R/W  电压设置(整型数据，无浮点)   
    CURRENT             = 0x0009  # R/W  电流设置(整型数据，无浮点)   
    OUTPUT_VOLTAGE      = 0x000A  # R    输出电压   
    OUTPUT_CURRENT      = 0x000B  # R    输出电流   
    OUTPUT_POWER_H      = 0x000C  # R    输出功率高16位  
    OUTPUT_POWER_L      = 0x000D  # R    输出功率低16位
    INPUT_VOLTAGE       = 0x000E  # R    输入电压
    KEYBOARD_LOCK       = 0x000F  # R/W  产品键盘锁 (0：未锁定 1：键盘锁定）    
    PROTECTION_STATUS   = 0x0010  # R    产品保护状态 (0：运行正常  1：OVP  2：OCP  3：OTP )
    CV_CC_STATUS        = 0x0011  # R    恒压恒流状态（0：CV状态  1：CC） 
    OUTPUT_STATUS       = 0x0012  # R/W  打开或者关闭输出（0：关闭  1：打开）
    SHORTCUT_CALLOUT    = 0x0013  # W    快捷调出(0-9号数据组)   

class RD60XX():

    def __init__(self, port: str, baudrate: int = 115200, device_id: int = 1):
        '''
        Initialize the RD60XX class.

        Args:
            port (str): The port to connect to the RD60XX device.
            baudrate (int, optional): The baudrate for the serial connection. Defaults to 115200.
            device_id (int, optional): The device ID for the Modbus connection. Defaults to 1.
        '''
        self.port = port
        self.baudrate = baudrate
        self.device_id = device_id

    def connect(self):
        '''
        Connect to the RD60XX device.
        '''
        self.client = ModbusSerialClient(port=self.port, baudrate=self.baudrate)
        try:
            self.client.connect()
            self.connected = True
        except Exception:
            logger.error(f"RD60XX connect error {self.port}")
            self.connected = False

    def disconnect(self):
        '''
        Disconnect from the RD60XX device.
        '''
        if self.connected:
            self.client.close()
            self.connected = False

    def read_register(self, register: RD60XX_REG, count: int = 1):
        '''
        Read a register from the RD60XX device.
        Args:
            register (RD60XX_REG): The register to read.
            count (int, optional): The number of registers to read. Defaults to 1.
        
        Returns:
            list or False: The values read from the register, or False if an error occurred.
        '''
        if not self.connected:
            logger.error("RD60XX is not connected !!!")
            return False
        
        try:
            result = self.client.read_holding_registers(
                address=register.value,
                count=count,
                device_id=self.device_id
            )
            if not result.isError():
                return result.registers
            else:
                logger.error(f"RD60XX read register error {register.name}")
                return False
        except Exception:
            logger.error(f"RD60XX read register error {register.name}")
            return False
        
    def write_register(self, register: RD60XX_REG, value: int):
        '''
        Write a value to a register on the RD60XX device.
        Args:
            register (RD60XX_REG): The register to write to.
            value (int): The value to write to the register.
        
        Returns:
            bool: True if the write was successful, False otherwise.
        '''
        if not self.connected:
            logger.error("RD60XX is not connected !!!")
            return False
        
        try:
            result = self.client.write_register(
                address=register.value,
                value=value,
                device_id=self.device_id
            )
            time.sleep(0.3)
            if not result.isError():
                return True
            else:
                logger.error(f"RD60XX write register error {register.name}")
                return False
        except Exception:
            logger.error(f"RD60XX write register error {register.name}")
            return False
        
    def read_product_model(self):
        '''
        Read the product model from the RD60XX device.
        Returns:
            int or None: The product model, or None if an error occurred.
        '''
        product_model = self.read_register(RD60XX_REG.PRODUCT_MODEL)
        if product_model:
            return product_model[0]
        else:
            return None

    def read_sn(self):
        '''
        Read the serial number from the RD60XX device.
        Returns:
            str or None: The serial number, or None if an error occurred.
        '''
        sn_h = self.read_register(RD60XX_REG.SN_H)
        sn_l = self.read_register(RD60XX_REG.SN_L)
        if sn_h and sn_l:
            return f"{sn_h[0]:04X}{sn_l[0]:04d}"
        else:
            return None
        
    def read_fw_version(self):
        '''
        Read the firmware version from the RD60XX device.
        Returns:
            float or None: The firmware version, or None if an error occurred.
        '''
        fw_version = self.read_register(RD60XX_REG.FW_VERSION)
        if fw_version:
            return fw_version[0]/100
        else:
            return None
        
    def read_voltage_setting(self):
        '''
        Read the voltage setting from the RD60XX device.
        Returns:
            float (V) or None: The voltage setting, or None if an error occurred.
        '''
        voltage = self.read_register(RD60XX_REG.VOLTAGE)
        if voltage:
            return int(voltage[0])/1000
        else:
            return None
        
    def read_current_setting(self):
        '''
        Read the current setting from the RD60XX device.
        Returns:
            float (A) or None: The current setting, or None if an error occurred.
        '''
        current = self.read_register(RD60XX_REG.CURRENT)
        if current:
            return int(current[0])/1000
        else:
            return None

    def read_output_voltage(self):
        '''
        Read the output voltage from the RD60XX device.
        
        Returns:
            float (V) or None: The output voltage, or None if an error occurred.
        '''
        output_voltage = self.read_register(RD60XX_REG.OUTPUT_VOLTAGE)
        if output_voltage:
            return int(output_voltage[0])/1000
        else:
            return None
        
    def read_output_current(self):
        '''
        Read the output current from the RD60XX device.
        Returns:
            float (A) or None: The output current, or None if an error occurred.
        '''
        output_current = self.read_register(RD60XX_REG.OUTPUT_CURRENT)
        if output_current:
            return int(output_current[0])/1000
        else:
            return None

    def read_output_status(self):
        '''
        Read the output status from the RD60XX device.
        Returns:
            int or None: The output status(0: off, 1: on), or None if an error occurred.
        '''
        output_status = self.read_register(RD60XX_REG.OUTPUT_STATUS)
        if output_status:
            return output_status[0]
        else:
            return None
        
    def read_c_temperature(self):
        '''
        Read the Celsius temperature from the RD60XX device.
        Returns:
            str or None: The Celsius temperature, or None if an error occurred.
        '''
        c_temperature_sign = self.read_register(RD60XX_REG.C_TEMPERATURE_SIGN)
        c_temperature_value = self.read_register(RD60XX_REG.C_TEMPERATURE_VALUE)
        if c_temperature_sign and c_temperature_value:
            return f"{'+' if c_temperature_sign[0] == 0 else '-'}{c_temperature_value[0]}℃"
        else:
            return None
        
    def read_f_temperature(self):
        '''
        Read the Fahrenheit temperature from the RD60XX device.
        Returns:
            str or None: The Fahrenheit temperature, or None if an error occurred.
        '''
        f_temperature_sign = self.read_register(RD60XX_REG.F_TEMPERATURE_SIGN)
        f_temperature_value = self.read_register(RD60XX_REG.F_TEMPERATURE_VALUE)
        if f_temperature_sign and f_temperature_value:
            return f"{'+' if f_temperature_sign[0] == 0 else '-'}{f_temperature_value[0]}℉"
        else:
            return None
        
    def read_output_power(self):
        '''
        Read the output power from the RD60XX device.
        Returns:
            float (W) or None: The output power, or None if an error occurred.
        '''
        output_power_h = self.read_register(RD60XX_REG.OUTPUT_POWER_H)
        output_power_l = self.read_register(RD60XX_REG.OUTPUT_POWER_L)
        
        if output_power_h and output_power_l:
            power = int(output_power_h[0])*65536+int(output_power_l[0])
            return power/1000
        else:
            return None
        
    def read_input_voltage(self):
        '''
        Read the input voltage from the RD60XX device.
        Returns:
            float (V) or None: The input voltage, or None if an error occurred.
        '''
        input_voltage = self.read_register(RD60XX_REG.INPUT_VOLTAGE)
        if input_voltage:
            return int(input_voltage[0])/100
        else:
            return None
        
    def read_keyboard_lock_status(self):
        '''
        Read the keyboard lock status from the RD60XX device.
        Returns:
            str or None: The keyboard lock status("UNLOCK" or "LOCK"), or None if an error occurred.
        '''
        keyboard_lock = self.read_register(RD60XX_REG.KEYBOARD_LOCK)
        if keyboard_lock:
            return f"{'UNLOCK' if keyboard_lock[0]==0 else 'LOCK'}"
        else:
            return None
        
    def read_protection_status(self):
        '''
        Read the protection status from the RD60XX device.
        Returns:
            str or None: The protection status("RUNNING", "OVP", "OCP", "OTP"), or None if an error occurred.
        '''
        protection_status = self.read_register(RD60XX_REG.PROTECTION_STATUS)
        if protection_status:
            if protection_status[0] == 0:
                protection_status_string = "RUNNING"
            elif protection_status[0] == 1:
                protection_status_string = "OVP"
            elif protection_status[0] == 2:
                protection_status_string = "OCP"
            elif protection_status[0] == 3:
                protection_status_string = "OTP"
            return protection_status_string
        else:
            return None
        
    def read_cv_cc_status(self):
        '''
        Read the CV/CC status from the RD60XX device.
        Returns:
            str or None: The CV/CC status("CV" or "CC"), or None if an error occurred.
        '''
        cv_cc_status = self.read_register(RD60XX_REG.CV_CC_STATUS)
        if cv_cc_status:
            return f"{'CV' if cv_cc_status[0]==0 else 'CC'}"
        else:
            return None

    def set_voltage(self, voltage: float):
        '''
        Set the voltage on the RD60XX device.
        Args:
            voltage (float) (V): The voltage to set (in volts).
        Returns:
            bool: True if the voltage was set successfully, False otherwise.
        Examples:
            rd60xx.set_voltage(12.345)  # Set voltage to 12.345 V
        '''
        value = int(voltage * 1000)
        result = self.write_register(RD60XX_REG.VOLTAGE, value)
        if result is False:
            logger.error(f"{"设置电压失败:   "} {voltage:06.3f}V")

        return result
    
    def set_current(self, current: float):
        '''
        Set the current on the RD60XX device.
        Args:
            current (float) (A): The current to set (in amps).
        Returns:
            bool: True if the current was set successfully, False otherwise.
        Examples:
            rd60xx.set_current(0.567)  # Set current to 0.567 A
        '''
        value = int(current * 1000)
        result = self.write_register(RD60XX_REG.CURRENT, value)
        if result is False:
            logger.error(f"{"设置电流失败:   "} {current:06.3f}A")

        return result

    def lock_keyboard(self):
        '''
        Lock the keyboard of the RD60XX device.
        Returns:
            bool: True if the keyboard was locked successfully, False otherwise.
        Examples:
            rd60xx.lock_keyboard()  # Lock the keyboard
        '''
        result = self.write_register(RD60XX_REG.KEYBOARD_LOCK, 1)
        if result is False:
            logger.error(f"{"键盘锁定失败:   "}")

        return result

    def on(self):
        '''
        Turn on the output of the RD60XX device.
        Returns:
            bool: True if the output was turned on successfully, False otherwise.
        Examples:
            rd60xx.on()  # Turn on the output
        '''
        result = self.write_register(RD60XX_REG.OUTPUT_STATUS, 1)
        if result is False:
            logger.error(f"{"输出状态打开失败:   "}")

        return result
    
    def off(self):
        '''
        Turn off the output of the RD60XX device.
        Returns:
            bool: True if the output was turned off successfully, False otherwise.
        Examples:
            rd60xx.off()  # Turn off the output
        '''
        result = self.write_register(RD60XX_REG.OUTPUT_STATUS, 0)
        if result is False:
            logger.error(f"{"输出状态关闭失败:   "}")

        return result
    
    def shortcut_callout(self, number: int):
        '''
        Perform a shortcut callout on the RD60XX device.
        Args:
            number (int): The shortcut callout number (0-9).
        Returns:
            bool: True if the shortcut callout was performed successfully, False otherwise.
        Examples:
            rd60xx.shortcut_callout(5)  # Perform shortcut callout 5
        '''
        if number < 0 or number > 9:
            logger.error(f"{"快捷调出失败:   "} 快捷调出编号应在0-9之间")
            return None
        
        result = self.write_register(RD60XX_REG.SHORTCUT_CALLOUT, number)
        if result:
            logger.info(f"{"快捷调出:       "} {number}号数据组")
        else:
            logger.error(f"{"快捷调出失败:   "} {number}号数据组")

        return result
    

if __name__ == "__main__":

    rd60xx = RD60XX(port='COM12', baudrate=115200, device_id=1)
    rd60xx.connect()

    if rd60xx.connected is False:
        exit(1)

    logger.info('-------------------------------')
    logger.info("为了测试，关闭输出")

    rd60xx.off()
    output_status = rd60xx.read_output_status()
    logger.info(f"{"输出状态:       "} {('OFF' if output_status==0 else 'ON')}")

    # rd60xx.on()
    # output_status = rd60xx.read_output_status()
    # logger.info(f"{"输出状态:       "} {('OFF' if output_status==0 else 'ON')}")


    logger.info('-------------------------------')
    model               = rd60xx.read_product_model()
    logger.info(f"{"产品型号:       "} {model}")

    sn                  = rd60xx.read_sn()
    logger.info(f"{"产品序列号:     "} {sn}")
    
    fw_version          = rd60xx.read_fw_version()
    logger.info(f"{"产品固件版本:   "} V{fw_version:.2f}")
    
    c_temperature       = rd60xx.read_c_temperature()
    logger.info(f"{"系统摄氏温度:   "} {c_temperature}")
    
    f_temperature       = rd60xx.read_f_temperature()
    logger.info(f"{"系统华氏温度:   "} {f_temperature}")
    
    voltage             = rd60xx.read_voltage_setting()
    logger.info(f"{"电压设置:       "} {voltage:06.3f}V")
    
    current             = rd60xx.read_current_setting()
    logger.info(f"{"电流设置:       "} {current:06.3f}A")
    
    output_voltage      = rd60xx.read_output_voltage()
    logger.info(f"{"输出电压:       "} {output_voltage:06.3f}V")
    
    output_current      = rd60xx.read_output_current()
    logger.info(f"{"输出电流:       "} {output_current:06.3f}A")
    
    output_power        = rd60xx.read_output_power()
    logger.info(f"{"输出功率:       "} {output_power:06.3f}W")
    
    input_voltage       = rd60xx.read_input_voltage()
    logger.info(f"{"输入电压:       "} {input_voltage:05.2f}V")
    
    keyboard_lock       = rd60xx.read_keyboard_lock_status()
    logger.info(f"{"键盘锁状态:     "} {keyboard_lock}")
    
    protection_status   = rd60xx.read_protection_status()
    logger.info(f"{"产品保护状态:   "} {protection_status}")
    
    cv_cc_status        = rd60xx.read_cv_cc_status()
    logger.info(f"{"恒压恒流状态:   "} {cv_cc_status}")
    
    output_status       = rd60xx.read_output_status()
    logger.info(f"{"输出状态:       "} {('OFF' if output_status==0 else 'ON')}")


    logger.info('-------------------------------')

    logger.info('设置输出电压为 12.000V')
    logger.info('设置输出电流为 00.100V')

    rd60xx.set_voltage(12.000)
    voltage = rd60xx.read_voltage_setting()
    logger.info(f"{"电压设置:       "} {voltage:06.3f}V")

    rd60xx.set_current(0.100)
    current = rd60xx.read_current_setting()
    logger.info(f"{"电流设置:       "} {current:06.3f}A")

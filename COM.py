import sys
import time
import serial
import struct
import os
from contextlib import redirect_stdout

MID_LEN = 1024  
# 定义全局变量  
global_counter = 0x0

code = [0x00, 0x55, 0x80, 0x0E]   
global code_24
code_24 = bytearray(0x24)
global code_16 
code_16 = bytearray(0x16)

# 获取当前程序的文件名
def get_file_name():
    file_name = __file__
    return file_name

# 获取当前程序的文件名（去掉后缀名）
def get_full_file_name_no_extension():
    file_name = __file__
    file_name_no_extension = os.path.splitext(file_name)[0]
    return file_name_no_extension

# 获取当前程序的文件名（只包括文件名，不包括路径）
def get_file_name_only():
    file_name = os.path.basename(__file__)
    return file_name

# 获取当前程序的文件名（去掉后缀名）
def get_file_name_no_extension():
    file_name = os.path.basename(__file__)
    file_name_no_extension = os.path.splitext(file_name)[0]
    return file_name_no_extension

class DataPacketFrame:  
    def __init__(self):  
        self.addr = bytearray(6)  
        self.ctr_Code = 0  
        self.DataLen = 0  
        self.Data = bytearray(MID_LEN)  
        self.CheckSum = 0  
def print_bytearray_hex(buf, prefix=''):
    
    port = get_file_name_no_extension() 
    port += ".log" 

    # 打开文件，准备追加写入
    with open(port, 'a') as f:
        # 保存原始stdout
        original_stdout = sys.stdout
        # 设置标准输出到文件中
        sys.stdout = f
        
        # 在终端中打印数据
        if prefix:
            print(prefix, end=' ')  # 输出到终端
        for byte in buf:
            print('{:02X}'.format(byte), end='')  
        print() # 换行      
        # 恢复原始stdout
        sys.stdout = original_stdout

        # 终端中输出数据
        if prefix:
            print(prefix, end=' ')  # 输出到终端
        for byte in buf:
            print('{:02X}'.format(byte), end='')  
        print() # 换行    

def calculate_checksum(data):  
    """  
    计算累加校验和  
    :param data: 字节列表  
    :return: 校验和  
    """  
    # 使用 sum 函数计算累加和  
    checksum = sum(data)  
    # 转换为无符号 8 位整数（如果需要）  
    checksum &= 0xFF  
    return checksum 
def packet(inBuf: DataPacketFrame, outBuf: bytearray) -> int:  
    i = 0  
    pos = 0  
    checkSum = 0  
  
    # 起始符  
    outBuf[i] = 0x68  
    i += 1  
  
    # 地址域  
    outBuf[i:i+6] = inBuf.addr  
    i += 6  
  
    outBuf[i] = 0x68  
    i += 1
  
    # 控制码  
    outBuf[i] = inBuf.ctr_Code  
    i += 1  
  
    # 数据长度  
    outBuf[i] = inBuf.DataLen  
    i += 1  
  
    # 数据  
    # 数据与传输运算方式：主站加0x33，从站减0x33  
    for j in range(inBuf.DataLen):  
        outBuf[i] = (inBuf.Data[j]+0x33) % 256 
        i += 1  
  
    # 检验和  
    outBuf[i] = calculate_checksum(outBuf)   
    i += 1  
  
    # 结束符  
    outBuf[i] = 0x16  
    i += 1  
  
    # 返回长度  
    return i  
def UnPacket(inBuf: bytearray, outBuf: DataPacketFrame) -> bool:  
    if len(inBuf) < 11:  
        return False  
  
    pos = 0  
    i = 0  
    j = 0
    checkSum = 0  
  
    # 寻找前导码  
    while j < 4: 
        if inBuf[i] == 0xfe:  
            i += 1  
        j += 1    
    pos = i  
       
    # 检查起始字节  
    if inBuf[i] != 0x68 or inBuf[i + 7] != 0x68:  
        return False  
    i += 1  
  
    # 填充地址域  
    for j in range(6):  
        outBuf.addr[j] = inBuf[i]  
        i += 1  
  
    # 控制码 
    i += 1  
    outBuf.ctr_Code = inBuf[i]   
  
    # 数据长度  
    i += 1 
    outBuf.DataLen = inBuf[i]  
     
    # 数据
    i += 1   
    data_bytes = inBuf[i:i+outBuf.DataLen]  
    # (b - 0x33) % 256
    outBuf.Data = bytearray([b for b in data_bytes])  
    i += outBuf.DataLen  

    #print_bytearray_hex(outBuf.Data) 

    # 合并为一个新数组  
    merged_array = bytearray() 
    merged_array.append(0x68)  
    merged_array.extend(outBuf.addr)   
    merged_array.append(0x68)  
    merged_array.append(outBuf.ctr_Code)  
    merged_array.append(outBuf.DataLen)  
    merged_array.extend(outBuf.Data)  

    #print_bytearray_hex(merged_array) 

    # 校验和  
    checkSum = calculate_checksum(merged_array)   
  
    #print('{:02X}'.format(inBuf[i]), end='\r\n')   
    #print('{:02X}'.format(checkSum), end='\r\n')   

    # 比较校验和  
    if checkSum != inBuf[i]:  
        return False  
  
    outBuf.CheckSum = inBuf[i]  
    return True  
def increment_two_byte_int(value):  
     # 如果当前值是0xFFFF，则递增后应为1  
    if value == 0xFFFF:  
        value = 1  
    else:
        value = (value + 1)
    return value  

def serial_communication_loop(serial_port, baudrate, outBuf: bytearray) -> tuple:    
    with serial.Serial(serial_port, baudrate, bytesize=8, stopbits=1, parity='N', rtscts=False) as ser:    
        while True:    
            if ser.in_waiting > 0:    

                data = ser.read(ser.in_waiting)    
                received_length = len(data)  
                #print(f"实际收到的字节数: {received_length}")
                print_bytearray_hex(data, "接收数据：") 

                readBuff = DataPacketFrame()  
                success = UnPacket(data, readBuff)  
                if not success:  
                    print("数据解析失败")
                    continue

                #print_bytearray_hex(readBuff.Data) 

                code[0] = (readBuff.Data[0] - 0x33) % 256 
                outBuf[:] = code[:]      
                
                #数据标识
                if readBuff.DataLen > 0x04:             
                    len_data = 4

                # 授权码
                if code[0] == 0x02 and readBuff.DataLen == 0x24:    
                    global code_24 
                    code_24 = bytearray([(b - 0x33) % 256 for b in readBuff.Data[4:]])           
                    break

                # 产品信息
                elif code[0] == 0x04 and readBuff.DataLen == 0x16:   
                    global code_16 
                    code_16 = bytearray([(b - 0x33) % 256 for b in readBuff.Data[4:]])               
                    break 

                elif code[0] == 0x03 and readBuff.DataLen == 0x04: 
                    len_data = 0x24
                    outBuf[4:] = code_24[:]  
                    break

                elif code[0] == 0x05 and readBuff.DataLen == 0x04: 
                    len_data = 0x16
                    outBuf[4:] = code_16[:]  
                    break

                else:
                    len_data = 0x4
                    break         
            else:
                time.sleep(0.1)  # 等待一段时间再检查            
    return len_data                   

def is_valid_serial_port(port):
    try:
        serial.Serial(port)
        return True
    except serial.SerialException:
        return False
    
def validate_serial_port(port):
    if is_valid_serial_port(port):
        print(f"{port} is a valid serial port.")
    else:
        print(f"{port} is not a valid serial port.")
        sys.exit()                

# 示例使用  
if __name__ == "__main__":  

    #print("当前程序的全路径文件名:", get_file_name())
    #print("当前程序的全路径文件名（去掉后缀名）:", get_full_file_name_no_extension())
    #print("当前程序的文件名（只包括文件名）:", get_file_name_only())
    #print("当前程序的文件名（去掉后缀名）:", get_file_name_no_extension())

    port = get_file_name_no_extension()  
    validate_serial_port(port)  # 更换为你需要验证的串口号

    while True:
        # 初始化DataPacketFrame实例  
        dataInfo = DataPacketFrame()      
        out_buf = bytearray(MID_LEN)      
        out_data = bytearray(32)

        # 帧序号，小端序
        global_counter = increment_two_byte_int(global_counter)
        unFrameNo = bytearray(global_counter.to_bytes(2, byteorder='little')) 
        dataInfo.addr[:2] = unFrameNo  # 拷贝unFrameNo到dataInfo.addr的前两个字节  
        
        # 前导字节
        dataInfo.addr[2:6] = bytearray([0xFF, 0xFF, 0xEE, 0xEE])  # 拷贝前导字节到dataInfo.addr的后续位置  
    
        # 控制码
        dataInfo.ctr_Code = 0x91

        # 数据域
        len_data = serial_communication_loop(port, 9600, out_data)
        #print_bytearray_hex(out_data[:len_data])

        dataInfo.DataLen = len_data
        dataInfo.Data[:] = out_data[:]

        len_out = packet(dataInfo, out_buf) 
        print_bytearray_hex(out_buf[:len_out], "发送数据：")
       
        # 创建一个长度为 len_out 的空 bytearray  
        out_realdata = bytearray(len_out)  
        
        # 复制源数据到out_realdata，但不超过 len_out 的长度  
        # 使用切片[:len_out]来确保不会超出 len_out 的范围  
        out_realdata[:] = out_buf[:len_out]  
        
        with serial.Serial(port, 9600, bytesize=8, stopbits=1, parity='N', rtscts=False) as ser:                
            ser.write(out_realdata)  

  
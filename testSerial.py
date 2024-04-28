import serial  
import time

def serial_communication_loop(serial_port, baudrate, databits=8, stopbits=1, parity='N', rtscts=False):  
    # 打开串口  
    with serial.Serial(serial_port, baudrate, bytesize=databits, stopbits=stopbits, parity=parity, rtscts=rtscts) as ser:  
        # 定义初始的回复数据  
        responses = {  
            b'\x05': b'\x06',  
            b'\x02\x43\x45\x03': b'\x05',  
            # 初始时不设置 b'\x06' 的响应，稍后在用户输入后设置  
        }  
        
        # 提示用户输入轨道数量  
        orbit_number = input("请输入轨道数量 ('1' 或 '2'): ")  
        
        # 根据用户输入设置 responses[b'\x06'] 的值  
        if orbit_number == '1':  
            responses[b'\x06'] = b'\x02\x31\x3A\x02\x01\x00\x00\x00\x00\x00\x03'  
        elif orbit_number == '2':  
            responses[b'\x06'] = b'\x02\x31\x3A\x02\x01\x00\x00\x00\x00\x00\x2C\x32\x3A\x02\x02\x00\x00\x00\x00\x00\x03'  
        else:  
            print("无效的输入，请输入 '1' 或 '2'。")  
            # 可以选择退出程序或进行其他错误处理  
            exit(1)  # 退出程序，返回错误码 1  
  
        while True:  
            # 等待并读取串口数据  
            if ser.in_waiting:  
                received_data = ser.read(ser.in_waiting)  
  
                # 检查并回复数据  
                if received_data == b'\x05':  
                    ser.write(responses[b'\x05'])  
                    print(responses[b'\x05'].hex())  

                elif received_data == b'\x02\x43\x45\x03':  
                    ser.write(responses[b'\x02\x43\x45\x03'])  
                    print(responses[b'\x02\x43\x45\x03'].hex())  
                
                elif received_data == b'\x06':  
                    ser.write(responses[b'\x06'])  
                    print(responses[b'\x06'].hex())  
                
                else:    
                    # 检查是否收到了步骤4回复的06，并打印返回的数据  
                    print("Received data after sending 06:", received_data.hex())  
  
            # 休眠一小段时间，避免过于频繁的轮询  
            # 根据实际需要调整这个值  
            # 注意：太小的值可能导致CPU占用率过高，太大的值可能导致响应延迟  
            time.sleep(0.01)  
  
# 使用示例：  
# 假设串口配置为 COM3, 波特率 9600, 8 数据位, 1 停止位, 无校验位  
serial_communication_loop('COM2', 9600)
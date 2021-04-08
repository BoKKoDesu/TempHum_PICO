'''
Wiring (Front view. From the left-hand side.)
    1   ->   GND
    2   ->   Power(8 - 30 VDC)
    3   ->   B
    3   ->   A
'''

#Import module
from machine import UART, Pin

#Declare UART object
uart0 = UART(0, baudrate = 9600, bits=8, parity=None, stop=1) # tx=0, rx=1

#Check UART object
print(uart0)

#Declaration of variable objects
#Each sensor has maximum data buffer, edit the max_index as your desire
RxData = []
index = 0
max_index = 9
tim_ready = 0

#Define callback function for Timer Interrupt
def send(d):
    
    #Check if callback is enable
    if tim_ready == 1:
        
        #Data-read command
        txData = b'\x01\x03\x00\x00\x00\x02\xC4\x0B'
        
        #Transmission command
        uart0.write(txData)
        
        #Check transmitted command
        print("Sent data : " + str(txData))
        
        #Disable callback for a while
        tim_ready == 0

#Define timer trigger every 1 second and use send() as callback function
tim = machine.Timer()
tim.init(period = 1000, callback = send)

#Define calculation function which return actual data
def cal_raw(d1, d2):
    
    #Convert byte data into int
    raw = ((int.from_bytes(d1, 'big')) << 8) + (int.from_bytes(d2, 'big'))
    
    #If temperature is less than 0
    if raw > 0xFE00:
        raw ^= 0xFFFF
        raw += 0x1
        raw *= -1
    
    #If temperature is more than 0
    else:
        pass
    
    #Return actual data
    return raw/10

#The main loop start here
while True:
    
    #Enable callback
    tim_ready = 1
    
    #Waiting for data to be received
    while(uart0.any()  < 1):
        pass
    
    #When Data received
    while(uart0.any()  > 0): 
        
        #Add received data to RxData list
        RxData.append(uart0.read(1))
        
        #Check if buffer is empty
        index += 1
    
    #When all data has been received
    if index == max_index:
        
        #Check received data
        print("Received data : " + str(RxData))
        
        #Get data from defined function
        temp = cal_raw(RxData[3], RxData[4])
        hum = cal_raw(RxData[5], RxData[6])
        
        #Display ph value
        print("Temterature : " + str(temp))
        print("Humidity : " + str(hum))
        
        #Clear buffer
        RxData = []
        
        #Clear index
        index = 0
        
import time
import usb.core
import usb.util
import usb.control
import os

errorcode = os.errno.errorcode

#Bus 006 Device 002: ID 0001:0000 Fry's Electronics
dev = usb.core.find(idVendor=0x0001, idProduct=0x0000)

if dev is None:
    raise Exception("device not foudn")

print dev
print '-'*20

for cfg in dev:
    print repr(cfg)
print '-'*20

print 'is_kernel_driver_active:', dev.is_kernel_driver_active(0)
if dev.is_kernel_driver_active(0):
    dev.detach_kernel_driver(0)

try:
    dev.set_configuration(cfg)
except usb.core.USBError, e:
    print 'Error -> ', repr(e)
    print errorcode[e.errno]

    if errorcode[e.errno]!='EBUSY':
        raise
    raise

cfg = dev.get_active_configuration()
print '-'*20
print cfg


intf = cfg[(0,0)]
print '-'*20
print intf

ep_out = ep_in = None

for idx, e in enumerate(intf):
    print idx, repr(e), dir(e)
    if usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_OUT:
        ep_out = e
    if usb.util.endpoint_direction(e.bEndpointAddress)==usb.util.ENDPOINT_IN:
        ep_in = e

print ep_out
print ep_in


print dir(ep_out)

print 'getstatus:', usb.control.get_status(dev, ep_out)


print usb.control.get_descriptor(dev, 41, 02, 00, 00)   # -> ok!

def f_a(ar):
    _type = ar[1]
    if _type==03:
        st = ''
        for i in xrange(2, len(ar), 2):
            st+=chr(ar[i])
        return st
    return ar


class Info:
    def __init__(self, data):
        f = lambda x:float(x)
        i = lambda x:int(x)
        d = {0:f, 1:f, 2:f, 3:i, 4:f, 5:f, 6:f, 7:lambda x:x}
        self.v_in, self.other, self.v_out, self.load, self.hz, self.charge, self.degrees, other = map(
            lambda e:d[e[0]](e[1]), enumerate(data.split()))

    def __str__(self):
        return '%.01f ->V-> %.01f  Load:%d~  %.02fhz  %.01fC  %.01fV'%(self.v_in,
                 self.v_out, self.load, self.hz, self.degrees, self.charge)

def parse_string(desc33):
    desc33 = f_a(desc33)
    verif, desc33 = desc33[0], desc33[1:]
    return Info(desc33)


#
#   size type index
print 'get_descriptor(3,1):', repr(f_a(usb.control.get_descriptor(dev, 1026, 03, 01)))
print 'get_descriptor(3,3):', repr(f_a(usb.control.get_descriptor(dev, 102, 03, 03)))
print 'get_descriptor(3,d):', repr(f_a(usb.control.get_descriptor(dev, 102, 03, 0x0d)))
print 'get_descriptor(3,c):', repr(f_a(usb.control.get_descriptor(dev, 102, 03, 0x0c)))
time.sleep(1)
while 1:
    print 'get_descriptor(3,3):', parse_string(usb.control.get_descriptor(dev, 102, 03, 03))
    time.sleep(0.5)

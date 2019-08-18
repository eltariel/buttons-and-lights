#!/bin/bash

usb_gadget_name="not-pibow"

usb_idVendor="0x1d6b"  # 0x1d6b = Linux Foundation
usb_idProduct="0x0104" # 0x0104 = Multifunction Composite Gadget
usb_iserialnumber="00000000000A"
usb_imanufacturer="Eltariel"
usb_iproduct="Keyboard Proxy"

scriptdir=$(dirname $0)
descriptor_dir=$(readlink -f ${scriptdir}/descriptors || true)

boot_kbd=$(readlink -f ${descriptor_dir}/bootkbd.bin || true)
nkro_kbd=$(readlink -f ${descriptor_dir}/ext_hid.bin || true)

rndis_dev_mac=$(cat ${descriptor_dir}/mac-dev)
rndis_host_mac=$(cat ${descriptor_dir}/mac-host)

log="not-pibow:"

echo "${log} Loading libcomposite"
modprobe libcomposite || true
	
echo "${log} Creating ${usb_gadget_name}"
gadget="/sys/kernel/config/usb_gadget/${usb_gadget_name}"
c=${gadget}/configs/c.1
f=${gadget}/functions

mkdir -p ${gadget} || true

echo '' > ${gadget}/UDC

echo "${log} Setting USB properties"
echo 0x0200 > ${gadget}/bcdUSB              # USB version, 0x0200 = USB2
echo 0x0100 > ${gadget}/bcdDevice           # Device version
echo ${usb_idVendor}  > ${gadget}/idVendor
echo ${usb_idProduct} > ${gadget}/idProduct
echo 0xEF > ${gadget}/bDeviceClass
echo 0x02 > ${gadget}/bDeviceSubClass
echo 0x01 > ${gadget}/bDeviceProtocol

mkdir -p ${gadget}/strings/0x409            # 0x409 = english strings
echo ${usb_iserialnumber} > ${gadget}/strings/0x409/serialnumber
echo ${usb_imanufacturer} > ${gadget}/strings/0x409/manufacturer
echo ${usb_iproduct}      > ${gadget}/strings/0x409/product

echo 1       > ${gadget}/os_desc/use
echo 0xCD    > ${gadget}/os_desc/b_vendor_code
echo MSFT100 > ${gadget}/os_desc/qw_sign

echo "${log} Creating config"
mkdir -p ${c}/strings/0x409
echo "Keyboard Proxy and Network" > ${c}/strings/0x409/configuration
echo 500 > ${c}/MaxPower

ln -s ${c} ${gadget}/os_desc

echo "${log} Registering RNDIS"
mkdir -p ${f}/rndis.0
# first byte of address must be even
echo ${rndis_host_mac} > ${f}/rndis.0/host_addr
echo ${rndis_dev_mac}  > ${f}/rndis.0/dev_addr
echo 0xEF              > ${f}/rndis.0/class
echo 0x04              > ${f}/rndis.0/subclass
echo 0x01              > ${f}/rndis.0/protocol
echo RNDIS             > ${f}/rndis.0/os_desc/interface.rndis/compatible_id
echo 5162001           > ${f}/rndis.0/os_desc/interface.rndis/sub_compatible_id
ln -s ${f}/rndis.0 ${c}

echo "${log} Registering HID using ${boot_kbd} for Boot Keyboard Descriptor"
mkdir -p ${f}/hid.0
echo 1          > ${f}/hid.0/protocol
echo 1          > ${f}/hid.0/subclass
echo 8          > ${f}/hid.0/report_length
cat ${boot_kbd} > ${f}/hid.0/report_desc
ln -s ${f}/hid.0 ${c}

echo "${log} Registering HID using ${nkro_kbd} for Extended Keyboard Descriptor"
mkdir -p ${f}/hid.1
echo 0          > ${f}/hid.1/protocol
echo 0          > ${f}/hid.1/subclass
echo 32         > ${f}/hid.1/report_length
cat ${nkro_kbd} > ${f}/hid.1/report_desc
ln -s ${f}/hid.1 ${c}

echo "${log} Registering MIDI"
mkdir -p ${f}/midi.0
ln -s ${f}/midi.0 ${c}

#echo "${log} Registering ECM"
#mkdir -p ${f}/ecm.0
#echo ${ecm_dev_mac}  > ${f}/ecm.0/host_addr
#echo ${ecm_host_mac} > ${f}/ecm.0/dev_addr
#ln -s ${f}/ecm.0 ${c}

echo "${log} Registering ACM"
mkdir -p ${f}/acm.0
ln -s ${f}/acm.0 ${c}

echo "${log} Enabling gadget"
ls /sys/class/udc > ${gadget}/UDC

echo "${log} ${usb_gadget_name} Created"

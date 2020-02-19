# Create your car application.

This chapter describe the difference from Raspberry Pi.

## Create Donkeycar from Template

Create a set of files to control your Donkey with this command:

```bash
donkey createcar --path ~/mycar
```



## Configure Options

### Configure I2C PCA9685

If you are using a PCA9685 card, make sure you can see it on I2C.  
(1:3V3 power, 6:Ground, 3:I2C_SDA, 5:I2C_SCL)

```bash
sudo i2cdetect -r -y 1
```

This should show you a grid of addresses like:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- UU -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: 60 -- -- -- -- -- -- UU 68 -- -- -- -- -- -- --
70: 70 -- -- -- -- -- -- --
```



### Joystick setup

Install sysfsutils

  sudo apt-get install sysfsutils

Edit the config to disable bluetooth ertm

  sudo nano /etc/sysfs.conf

Append this to the end of the config

  /module/bluetooth/parameters/disable_ertm=1

Reboot your machine.

  sudo reboot


pairing PS4 controller

bluetoothctl
```bash
[bluetooth]# scan on
[bluetooth]# pair 90:89:xx:xx:xx:xx
[bluetooth]# trust 90:89:xx:xx:xx:xx
```

-------


### myconfig.py(only evdev)
AUTO_RECORD_ON_THROTTLE = False


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
(1:3V3 power, 6:Ground, 27:I2C3_SDA, 28:I2C3_SCL)

```bash
sudo i2cdetect -r -y 2
```

This should show you a grid of addresses like:

```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- UU -- -- -- -- --
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- UU -- --
40: 40 -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: 70 -- -- -- -- -- -- --
```



### Joystick setup

pairing PS4 controller

bluetoothctl command
```bash
[bluetooth]# scan on
[bluetooth]# pair 90:89:xx:xx:xx:xx
[bluetooth]# trust 90:89:xx:xx:xx:xx
```

-------


### myconfig.py
AUTO_RECORD_ON_THROTTLE = False


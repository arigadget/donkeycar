# Create your car application.

This chapter describe the difference from Raspberry Pi.

## Create Donkeycar from Template

Create a set of files to control your Donkey with this command:

```bash
donkey createcar --path ~/mycar
```



## edit myconfig.py

```python
#CAMERA
CAMERA_TYPE = "CORALGS"   # (CORALGS|CORALCV|PICAM|WEBCAM|CVCAM|CSIC|V4L|MOCK)

#9865, over rides only if needed, ie. TX2..
PCA9685_I2C_ADDR = 0x60     #I2C address, use i2cdetect to validate this number
PCA9685_I2C_BUSNUM = 1      #None will auto detect, which is fine on the pi. But other platforms should specify the bus num.

#TRAINING
DEFAULT_MODEL_TYPE = 'coral_tflite_linear'   #(linear|categorical|rnn|imu|behavior|3d|localizer|latent)

```



## Configure Options

### Configure I2C PCA9685

First,  use a drop of solder to bridge A5 due to change i2c address from x'40' to x'60'.

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

- #### Install sysfsutils

​       sudo apt-get install sysfsutils

- #### Edit the config to disable bluetooth ertm

​      sudo nano /etc/sysfs.conf

- #### Append this to the end of the config

​      /module/bluetooth/parameters/disable_ertm=1

- #### Reboot your machine.

​      sudo reboot

- ####     pairing xbox/PS4 controller

​      bluetoothctl
```bash
[bluetooth]# scan on
[bluetooth]# pair 90:89:xx:xx:xx:xx
[bluetooth]# trust 90:89:xx:xx:xx:xx
[bluetooth]# connect 90:89:xx:xx:xx:xx
```


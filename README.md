# Get Your Tinker Edge T Working.

This document corresponds to the original chapters of Raspberry Pi.

## Step 8: Install Dependencies

```bash
$ sudo apt-get install build-essential python3 python3-dev python3-pip python3-virtualenv python3-numpy python3-pandas i2c-tools avahi-utils joystick libopenjp2-7-dev libtiff5-dev gfortran libatlas-base-dev libopenblas-dev libhdf5-serial-dev git
$ sudo apt-get install python3-h5py
```

## Step 9: Install Optional OpenCV Dependencies

If you are going for a minimal install, you can get by without these. But it can be handy to have OpenCV.

```bash
$ sudo apt-get install build-essential cmake unzip pkg-config 
$ sudo apt-get install libjpeg-dev libpng-dev libtiff-dev 
$ sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
$ sudo apt-get install libxvidcore-dev libx264-dev 
$ sudo apt-get install libgtk-3-dev 
$ sudo apt-get install libatlas-base-dev gfortran 
$ sudo apt-get install python3-dev
```

##  Step 10: Setup Virtual Env

```bash
python3 -m virtualenv -p python3 env --system-site-packages
echo "source env/bin/activate" >> ~/.bashrc
source ~/.bashrc
```
Modifying your .bashrc in this way will automatically enable this environment each time you login. To return to the system python you can type `deactivate`.

##  Step 11: Install Donkeycar Python Code

Change to a dir you would like to use as the head of your projects.

```
mkdir projects
cd projects
```

Get the donkeycar from Github.

```bash
git clone https://github.com/arigadget/donkeycar
git checkout -b tinkeredget
cd donkeycar
pip install -e .[tpu]
```

##  Step 12: Install Optional OpenCV

### Create temporary 2G swap for the build
```bash
$ sudo fallocate -l 2G /swapfile 
$ sudo chmod 600 /swapfile 
$ sudo mkswap /swapfile 
$ sudo swapon /swapfile
```
### Update the system
```bash
$ sudo apt-get update
$ sudo apt-get upgrade
```
### Format & Mount SD card(16GB)
```bash
sudo mkfs -t ext4 /dev/mmcblk1
sudo mount /dev/mmcblk1 /mnt
sudo chmod 777 /mnt
```
### Download OpenCV and contrib modules
```bash
$ cd /mnt
$ wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip
$ wget -O opencv_contrib.zip
https://github.com/opencv/opencv_contrib/archive/4.0.0.zip
$ unzip opencv.zip
$ unzip opencv_contrib.zip
$ mv opencv-4.0.0 opencv
$ mv opencv_contrib-4.0.0 opencv_contrib
```
### Compile OpenCV
```bash
# Make sure you are still in cv virtual environment 
$ cd /mnt/opencv 
$ mkdir build 
$ cd build
```
I used following CMake for my requirements, you can add or remove packages as necessary
```bash
cmake -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D INSTALL_PYTHON_EXAMPLES=ON \
  -D INSTALL_C_EXAMPLES=OFF \
  -D OPENCV_ENABLE_NONFREE=ON \
  -D OPENCV_EXTRA_MODULES_PATH=/mnt/opencv_contrib/modules \
  -D PYTHON_EXECUTABLE=~/env/bin/python \
  -D ENABLE_FAST_MATH=1 \
  -D ENABLE_NEON=ON -D WITH_LIBV4L=ON \
  -D WITH_V4L=ON \
  -D BUILD_EXAMPLES=ON ..
```
We can compile now, it took about 4 hours for me.
```bash
$ make
```
Time to install OpenCV
```bash
$ sudo make install
$ sudo ldconfig
```
Link it to the virtual environment
```bash
$ ls /usr/local/python/cv2/python-3.5
cv2.cpython-35m-aarch64-linux-gnu.so
$ cd /usr/local/python/cv2/python-3.5
$ sudo mv cv2.cpython-35m-aarch64-linux-gnu.so cv2.so 
$cd ~/env/lib/python3.5/site-packages/
$ ln -s /usr/local/python/cv2/python-3.5/cv2.so cv2.so
```
Finally run a quick test
```bash
$ python
>>> import cv2
>>> cv2.__version__
'4.0.0'
>>> quit()
```
(Reference)
[Installing OpenCV 4.0 on Google Coral Dev board](https://medium.com/@balaji_85683/installing-opencv-4-0-on-google-coral-dev-board-5c3a69d7f52f)

----

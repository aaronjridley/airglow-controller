
Computer comes configured with RedHat Enterprize

1. Make a new user account called 'fpi'. 

2. scp .bashrc, .bash_aliases, .profile scripts over. Edit computer
name and path in bashrc file

3. set up ssh keys

4. make Software directory

5. git clone https://github.com/aaronjridley/airglow-controller.git

Need sudo access for next several steps, so do this from an account
with sudo access:

6. make an andor directory and grab the STK from /nobackup/ridley/Fpi/ on zed.

7. untar file.

8. cd andor

9. sudo install_andor

Now, in the airglow-controller directory / account:

10. cd into components/andor_wrapper/andorsdk_wrapper

11. python3 setup.py build_ext -i to build the python module

12. go into the airglow-controller directory, go into python and try:
    "from components.camera import getCamera"

Connecting through a tunnel with Cloudflare:

13. download cloudflared to the machine you want to tunnel TO from

https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/

rpm is for yum (redhat)
deb is for apt (ubuntu)

And install it on the computer you want to tunnel TO:

sudo yum install ./cloudflared-linux-x86_64.rpm

14. Register a domain on cloudflare if you would like (e.g., umfpi.net)

15. Log into:

https://one.dash.cloudflare.com/

16. Go to access -> tunnels

17. Click on "Add a Tunnel"

18. Enter a tunnel name (e.g., the machine you want to connect)

19. Select the environment, and run the command on the computer you
want to tunnel TO.

20. For the public hostname, enter something like:

public hostname:

fpi02   .   umfpi.net   .   / (no path)

Service:

SSH   ://   localhost:22

21. On the computer you want to SSH FROM:

A. Install cloudflared

B. Go into ssh config file and add something like:

Host fpi02.umfpi.net
     ProxyCommand /usr/local/bin/cloudflared access ssh --hostname %h

C. You should be able to run the command:

ssh fpi02.umfpi.net

22. Need to fix the Arduino permission issue: sudo usermod -a -G dialout ridley

23. To get HID working, need to start processes in the /etc/udev/rules.d/ directory (grab the hid stuff from another computer).


List of things to install (sudo yum install ...):
emacs
python3-matplotlib
python3-h5py
libusb-devel
python36-devel
python3-Cython
hidapi

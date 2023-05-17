'''
apt install -y python3-pip
pip install sockets
pip install pyserial
pip install pycrypto
'''

'''
sudo apt install -y neovim
'''
 
 
 Setting up a service
 ```
 sudo vim /lib/systemd/system/trovis.service
 sudo vim /lib/systemd/system/amis.service
 sudo vim /lib/systemd/system/shakrky.service
 
 
 
 sudo systemctl daemon-reload
 sudo systemctl start trovis.service
 sudo systemctl status trovis.service
 sudo systemctl enable trovis.service

 
 bzw amis.service
 
 ```
 
 
 trovis.service
 ```
[Unit]
Description=Trovis
After=multi-user.target

[Service]
Type=simple
User=gateway
ExecStart=/usr/bin/python3 /home/gateway/trovis.py
Restart=on-abort

[Install]
WantedBy=multi-user.target
 ```

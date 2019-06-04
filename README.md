# Ssh-Webconsole
一款借助云端mqtt中转, 远程ssh访问终端设备的工具    
    
数据流程：    
终端设备SshEndPoint 《==========》  mqtt-broker  《=========》客户端浏览器WebConsole    
    
使用方法：    
1， 安装和配置mqtt-broker    
(1) 在云端安装mqtt. 以centos为例:    
yum -y install mosquitto    
(2) 配置mqtt支持websocket连接    
vim /etc/mosquitto/mosquitto.conf    
如果没有安装vim, 先执行: yum -y install vim    
定位到行: port 1883    
将这行注释    
定位到行： protocol mqtt    
将这行注释    
然后在下方添加以下行:    
protocol websockets    
port 8083    
listener 1883    
(3) 重新启动mosquitto    
pkill mosquitto    
mosquitto -c /etc/mosquitto/mosquitto.conf &    
    
2, 安装和配置SshEndPoint    
连接自己的linux终端设备（假定已安装python3）。 将SshEndPoint目录拷贝到pi目录下。 以树莓派为例:    
(1) 配置    
cd /home/pi/SshEndPoint    
vim config.json    
将mqtt.host配置为自己云端服务器的公网IP或域名。    
(2) 启动SshEndPoint:    
./start.sh    
    
3, 安装和配置Webconsole    
将Webconsole目录拷贝到http根目录。 apache、nginx等都可以。    
（1）配置    
打开js/config.js文件，将mqttUrl中地址配置为自己云端服务器的公网IP或域名。    
（2）运行    
打开chrome、firefox、QQ等浏览器，输入http://localhost/webconsole    
    
现在, 可以自由发送命令啦.    
    
下一步计划：    
文件上传和下载支持。    
    
    
    

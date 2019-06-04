// 连接选项
const options = {
    connectTimeout: 10000, // 超时时间
}
var mqttClient;
var sendCallback;
function startMqtt(url, topic, recvCallback, _sendCallback) {
	// 连接选项
	var options = {
		connectTimeout: 5000, // 超时时间
		username: 'admin',
		password: 'public',
	};

	mqttClient = mqtt.connect(url, options);

	mqttClient.on('reconnect', (error) => {
		append('正在重连:' + JSON.stringify(error));
	});

	mqttClient.on('error', (error) => {
		append('连接失败:' + JSON.stringify(error));
	});
	
	mqttClient.on('close', (e)=>{
		append("连接已关闭");
	});

	// 监听接收消息事件
	if(recvCallback){
		mqttClient.on('message', recvCallback);
	}else{
		mqttClient.on('message', (topic, message) => {
			append('收到来自'+topic+'的消息: '+message.toString());
		});
	}
	
	mqttClient.on('connect', (e) => {
		append('连接成功')
		var arr = new Array();
		if(isString(topic)){
			arr[0] = topic;
		}else{
			arr = topic;
		}
		for(var idx =0; idx < arr.length; idx++) {
			mqttClient.subscribe(topic, {qos: 0}, (error) => {
				if (!error) {
					append('订阅成功');
				} else {
					append('订阅失败: ' + JSON.stringify(error));
				}
			});
		}
	});
	if(_sendCallback){
		sendCallback = _sendCallback;
	}
	return mqttClient;
}

function stopMqtt(){
	if(mqttClient){
		mqttClient.end(true);
		mqttClient = null;
	}
}

// 取消订阅
function unsubscribe(topic){
    mqttClient.unubscribe(
        // topic, topic Array, topic Array-Onject
        topic
    );
}

// 发布消息
var default_send_qos = {qos: 0, retain: false};
function publish(topic, msg) {
    if (!mqttClient.connected) {
        console.log('客户端未连接');
        return;
    }
    if(!topic)
        topic = mqttDroneTopic;
    mqttClient.publish(topic, isString(msg) ? msg : JSON.stringify(msg), default_send_qos, sendCallback);
}

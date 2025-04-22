let ws;
function connectWebSocket() {
  let auth_token = localStorage.getItem('auth_token');
  ws = new WebSocket(`ws://${window.location.hostname}:5008`);
  ws.onopen = () => {
    ws.send(JSON.stringify({ "auth_token": auth_token }));
    addServerMessage("WebSocket Connected!");}
  ws.onmessage = (event) => handleServerMessage(event.data);
  ws.onclose = () => setTimeout(connectWebSocket, 5000);
  ws.onerror = (error) => addServerMessage(`WebSocket Error: ${error.message || 'Unknown error'}`);
}

function sendMessage() {
  const input = document.getElementById("messageInput");
  const message = input.value.trim();
  if (message && ws && ws.readyState === WebSocket.OPEN) {
    addUserMessage(message);
    ws.send(JSON.stringify([{ type: "text", data: { text: message } }]));
    input.value = "";
  }
}

function addUserMessage(msg) {
  console.log("添加用户消息:", msg);
  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "user-message");


  if (typeof msg === "string") {
    if (msg === "") return;
    messageDiv.textContent = msg;
  } else if (msg.type === "text") {
    if (msg.data.text === "") return;
    messageDiv.textContent = msg.data.text;
  } else if (msg.type === "image" && msg.data?.file) {
    const img = document.createElement("img");
    img.src = msg.data.url;
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "user-message");
    messageDiv.style.maxWidth = "40%"; // 让 div 自适应但不太宽

    img.style.width = "100%"; // 让图片填充父容器
    img.style.borderRadius = "8px"; // 让图片更美观

    img.style.cursor = "pointer";//鼠标放上去变点击
    new Viewer(img, { url: 'src' });
    messageDiv.appendChild(img);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

  } else if (msg.type === "video" && msg.data?.file) {
    const chatContainer = document.getElementById("chatContainer");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "user-message");

    const video = document.createElement("video");
    video.src = msg.data.url;
    video.controls = true;
    video.style.maxWidth = "100%";
    video.style.borderRadius = "8px";

    messageDiv.appendChild(video);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } else if (msg.type === "record" || msg.type === "audio" && msg.data?.file) {

    const chatContainer = document.getElementById("chatContainer");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", "user-message");

    const audio = document.createElement("audio");
    audio.src = audioPath;
    audio.controls = true;

    messageDiv.appendChild(audio);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  } else if (msg.type === "file" && msg.data?.file) {
    const filePath = msg.data.url;
    const fileName = decodeURIComponent(filePath.split('/').pop());
    const link = document.createElement("span");
    link.textContent = fileName;
    link.style.color = "blue";
    link.style.textDecoration = "underline";
    link.style.cursor = "pointer";
    link.addEventListener("click", () => {
      navigator.clipboard.writeText(filePath).then(() => {
        alert("文件路径已复制，请手动粘贴到浏览器打开：\n\n" + filePath);
      }).catch(err => {
        console.error("无法复制路径：", err);
        alert("请手动复制文件路径：\n\n" + filePath);
      });
    });
    messageDiv.appendChild(link);
  }

  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
async function processMessage(msg) {
  if (!msg || !msg.type) {
    console.warn("无效消息:", msg);
    return;
  }
  let fileExtension = "";
  if (msg.data?.file) {
    let filePath = msg.data.file;
    console.log("Calling convertFileToBase64 with path:", filePath); // 添加日志
    fileExtension = filePath.split('.').pop().toLowerCase(); // 获取文件后缀
  }
  // 处理 node（递归解析）
  if (msg.type === "node" && msg.data && msg.data.content) {
    console.log("处理 node 消息:", msg.data);
    for (const content of msg.data.content) {
      await processMessage(content);
    }
    return;
  }

  // 处理文本消息
  if (msg.type === "text" && msg.data?.text?.trim()) {
    console.log("添加文本消息:", msg.data.text);
    addServerMessage(msg.data.text);
    return;
  }
  if (msg.type === "music") {
    console.log("添加音乐消息:", msg.data.title);
    let audio_url = msg.data.audio;
    addAudioMessage(audio_url);
    return;
  }

  // 处理图片消息
  if (msg.type === "image" && msg.data?.file) {

    let imageUrl = msg.data.file;
    if (imageUrl.startsWith("file://")) {
      imageUrl = await convertFileToBase64(imageUrl);
      if (!imageUrl) return;
    }
    console.log("添加图片消息:", imageUrl);
    addImageMessage(imageUrl);
    return;
  }
  if (msg.type === "video" || fileExtension === "mp4") {
    let videoPath = msg.data.file;
    if (videoPath.startsWith("file://")) {
      videoPath = await convertFileToBase64(videoPath); // 转换为 Base64
      if (!videoPath) return;
    }
    console.log("添加视频消息:", videoPath);
    addVideoMessage(videoPath);
    return;
  }
  // 处理音频消息
  if (msg.type === "record" || ["mp3", "wav"].includes(fileExtension)) {
    let audioPath = msg.data.file;
    if (audioPath.startsWith("file://")) {
      audioPath = await convertFileToBase64(audioPath); // 转换为 Base64
      if (!audioPath) return;
    }
    console.log("添加音频消息:", audioPath);
    addAudioMessage(audioPath);
    return;
  }
  if (msg.type === "file") {
    let filePath = msg.data.file;

    if (filePath.startsWith("file://")) {
      filePath = await moveFile2Stastic(filePath);  // 获取可访问 URL
      if (!filePath) return;
    }

    console.log("添加文件消息:", filePath);

    const fileName = filePath.split("/").pop();  // 获取文件名
    addFileMessage(filePath, fileName);  // 显示下载链接
    return;
  }
  console.warn("未知消息类型:", msg);
}

async function handleServerMessage(rawData) {
  try {
    const data = JSON.parse(rawData);
    console.log("收到服务器消息:", data)
    if (!data.message || !data.message.params) {
      console.warn("收到无效消息:", data);
      return;
    }

    let messages = data.message.params.messages || data.message.params.message; // 兼容 node 和普通消息
    if (!Array.isArray(messages)) {
      console.warn("消息格式错误:", messages);
      return;
    }

    for (const msg of messages) {
      await processMessage(msg);
    }
  } catch (e) {
    console.error("解析服务器消息失败:", e);
    addServerMessage("[Invalid message format]");
  }
}






function addServerMessage(message) {
  if (!message.trim()) return;  // 如果 message 为空或仅包含空格，则不显示

  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "server-message");
  messageDiv.textContent = message;
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}


async function convertFileToBase64(filePath) {
  console.log("Calling convertFileToBase64 with path:", filePath);
  try {


    const response = await fetch("http://127.0.0.1:5007/api/file2base64", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",  // 关键点：让浏览器发送 cookies
      body: JSON.stringify({ path: filePath }),
    });

    if (!response.ok) {
      console.error("HTTP error:", response.status);
      return null;
    }

    const data = await response.json();
    if (data.base64) {
      return data.base64;
    } else {
      console.error("Error:", data.error);
      return null;
    }
  } catch (error) {
    console.error("Request failed:", error);
    return null;
  }
}

async function moveFile2Stastic(filePath) {
  console.log("Calling moveFile2Stastic with path:", filePath);
  try {
    const response = await fetch("http://127.0.0.1:5007/api/move_file", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",  // 允许携带 Cookies
      body: JSON.stringify({ path: filePath }),
    });

    if (!response.ok) {
      console.error("HTTP error:", response.status);
      return null;
    }

    const data = await response.json();
    if (data.url) {
      return data.url;  // 返回可访问的 URL
    } else {
      console.error("Error:", data.error);
      return null;
    }
  } catch (error) {
    console.error("Request failed:", error);
    return null;
  }
}


function addVideoMessage(videoPath) {
  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "server-message");

  const video = document.createElement("video");
  video.src = videoPath;
  video.controls = true;
  video.style.maxWidth = "100%";
  video.style.borderRadius = "8px";

  messageDiv.appendChild(video);
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 处理音频消息（嵌入音频）
function addAudioMessage(audioPath) {
  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "server-message");

  const audio = document.createElement("audio");
  audio.src = audioPath;
  audio.controls = true;

  messageDiv.appendChild(audio);
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}
function addFileMessage(fileUrl, fileName) {
  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "server-message");

  // 创建可点击跳转的 <a> 标签
  const fileLink = document.createElement("a");
  fileLink.href = fileUrl;
  fileLink.textContent = fileName || "点击打开文件";
  fileLink.target = "_blank";
  fileLink.rel = "noopener noreferrer";
  fileLink.style.color = "blue";  // 设置字体颜色

  messageDiv.appendChild(fileLink);
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}



async function addImageMessage(imagePath) {
  if (imagePath.startsWith("file://")) {
    imagePath = await convertFileToBase64(imagePath);
    if (!imagePath) return;  // 如果转换失败，直接返回
  }

  const chatContainer = document.getElementById("chatContainer");
  const messageDiv = document.createElement("div");
  messageDiv.classList.add("message", "server-message");
  messageDiv.style.maxWidth = "20%"; // 让 div 自适应但不太宽

  const img = document.createElement("img");
  img.src = imagePath;
  img.style.width = "100%"; // 让图片填充父容器
  img.style.borderRadius = "8px"; // 让图片更美观
  img.style.cursor = "pointer";//鼠标放上去变点击
  new Viewer(img, { url: 'src' });
  messageDiv.appendChild(img);
  chatContainer.appendChild(messageDiv);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}


document.getElementById("fileInput").addEventListener("change", function (event) {
  const files = event.target.files;
  console.log("选择的文件:", files);
  if (files.length > 0) {
    for (const file of files) {
      const reader = new FileReader();
      reader.onload = function (e) {
        const base64Data = e.target.result.split(",")[1]; // 获取 Base64 数据
        const mimeType = file.type; // 直接获取文件 MIME 类型
        const fileType = file.type.split("/")[0]; // 获取文件类别（image, video, audio, etc.）

        let messageData;
        if (fileType === "image") {
          messageData = { type: fileType, data: { url: `data:${mimeType};base64,${base64Data}`, file: file.name } };
        } else if (fileType === "video" || fileType === "audio") {
          messageData = { type: fileType, data: { file: `data:${mimeType};base64,${base64Data}` } };
        } else {
          messageData = { type: fileType, data: { name: file.name, content: `data:${mimeType};base64,${base64Data}` } };
        }

        if (ws && ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify([messageData]));
          addUserMessage(messageData);
        }
      };
      reader.readAsDataURL(file); // 读取文件内容为 Base64
    }
  }
});
document.addEventListener("DOMContentLoaded", connectWebSocket);
document.getElementById('messageInput').addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendMessage();
    event.preventDefault();
  }
});
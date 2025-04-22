// 递归函数来渲染 JSON 数据
function renderJSON(data, parentKey = '', comments = {}) {
    const ul = document.createElement('ul');
    for (const key in data) {
        const li = document.createElement('li');
        // 为每个 li 标签添加 class
        li.classList.add('json-item');
        const fullKey = parentKey ? `${parentKey}.${key}` : key;
        const comment = comments[fullKey];

        if (typeof data[key] === 'object' && data[key]!== null) {
            li.innerHTML = `<span class="spantxt"><strong>${key}</strong></span>`;
            if (comment) {
                li.innerHTML += `<span class="comment">${comment}</span>`;
            }
            li.appendChild(renderJSON(data[key], fullKey, comments));
        } else {
            const value = data[key];
            const valueType = typeof value;
            li.innerHTML = `<span><strong>${key}</strong></span>`;

            let inputElement;
            if (valueType === 'boolean') {
                inputElement = document.createElement('input');
                inputElement.type = 'checkbox';
                inputElement.checked = value;
                inputElement.dataset.key = fullKey;
            } else if (valueType === 'number') {
                inputElement = document.createElement('input');
                inputElement.type = 'number';
                inputElement.value = value;
                inputElement.dataset.key = fullKey;
            } else {
                inputElement = document.createElement('textarea');
                inputElement.value = value;
                inputElement.dataset.key = fullKey;
            }

            li.appendChild(inputElement);
            if (comment) {
                const commentSpan = document.createElement('span');
                commentSpan.classList.add('comment');
                commentSpan.textContent = comment;
                li.appendChild(commentSpan);
            }
        }
        ul.appendChild(li);
    }
    return ul;
}

// 根据 key 路径更新 data 对象的值
function updateDataByKey(data, keyPath, value) {
    const keys = keyPath.split('.');
    let current = data;
    for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
    }
    const lastKey = keys[keys.length - 1];

    if (typeof current[lastKey] === 'boolean') {
        current[lastKey] = value;
    } else if (typeof current[lastKey] === 'number') {
        current[lastKey] = parseInt(value, 10);
    } else {
        current[lastKey] = value;
    }
}

// 发起请求获取 JSON 数据
let originalData;
fetch('http://127.0.0.1:5007/api/load/api.yaml')
  .then(response => {
        if (!response.ok) {
            throw new Error('网络响应存在问题');
        }
        return response.json();
    })
  .then(jsonData => {
        originalData = jsonData.data;
        const jsonRender = document.getElementById('json-render');
        jsonRender.appendChild(renderJSON(originalData, '', jsonData.comments));

        const saveButton = document.getElementById('save-button');
        saveButton.addEventListener('click', () => {
            const inputs = document.querySelectorAll('input, textarea');
            inputs.forEach(input => {
                const key = input.dataset.key;
                const value = input.type === 'checkbox'? input.checked : input.value;
                updateDataByKey(originalData, key, value);
            });

            // 将 originalData 封装到一个新对象中
            const dataToSend = { data: originalData };

            // 发送更新后的数据到 API
            fetch('http://127.0.0.1:5007/api/save/api.yaml', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(dataToSend)
            })
          .then(response => {
                if (!response.ok) {
                    throw new Error('保存数据时出现问题');
                }
                return response.json();
            })
          .then(savedData => {
                console.log('数据保存成功:', savedData);
            })
          .catch(error => {
                console.error('保存数据时出错:', error);
            });
        });
    })
  .catch(error => {
        console.error('请求过程中出现错误:', error);
    });
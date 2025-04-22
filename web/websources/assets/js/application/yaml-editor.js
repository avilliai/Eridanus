const yamlEditor = document.getElementById('yamlEditor');
const saveButton = document.getElementById('saveYaml');
// 获取下拉菜单元素
const dropdownMenu = document.querySelector('.dropdown-menu.yaml-list');
// 获取下拉菜单按钮元素
const dropdownButton = document.getElementById('dropdownMenuButton');
let yamlData = {};
let currentFile = '';

async function fetchYamlFiles() {
  const response = await fetch(`./api/files`);
  const result = await response.json();
  if (result.files) {
    result.files.forEach(file => {
      const listItem = document.createElement('li');
      const item = document.createElement('a');
      item.classList.add('dropdown-item');
      item.href = 'javascript:;';
      item.textContent = file;
      item.addEventListener('click', function (event) {
        event.preventDefault();
        currentFile = file;
        dropdownButton.textContent = currentFile;
        loadYamlFile(currentFile);
      });
      listItem.appendChild(item);
      dropdownMenu.appendChild(listItem);
    });
    currentFile = result.files[0];
    dropdownButton.textContent = currentFile;
    loadYamlFile(currentFile);
  } else {
    showAlert('alert-danger', 'YAML列表加载失败');
  }
}

async function loadYamlFile(fileName) {
  const response = await fetch(`./api/load/${fileName}`);
  const data = await response.json();
  console.log(data);

  if (data) {
    yamlData = data;
    console.log(yamlData);
    if (data.error)
      showAlert('alert-danger', data.error);
    else
      renderYamlEditor(yamlData, yamlEditor);
    yamlEditor.style.display = 'block';
    saveButton.style.display = 'inline-block';
  } else {
    showAlert('alert-danger', 'YAML加载失败');
  }
}

async function saveYamlFile() {
  const response = await fetch(`./api/save/${currentFile}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(yamlData),
  });
  const result = await response.json();
  if (result.message) {
    showAlert('alert-success', 'YAML保存成功');
  } else {
    showAlert('alert-danger', result.error);
  }
}

function renderYamlEditor(data, container) {
  container.innerHTML = '';
  createEditorElements(data.data || data, data.comments || {}, container, data.order || {}, ""); // 传递键的顺序
}

function createEditorElements(data, comments, parent, order, path = "") {
  const ul = document.createElement('ul');
  ul.classList.add('list-group');

  // 获取当前路径的键顺序
  const keys = order[path] || Object.keys(data);

  // 按顺序迭代键
  keys.forEach(key => {
    const value = data[key];
    const li = document.createElement('li');
    li.classList.add('list-group-item', 'd-flex', 'flex-column', 'align-items-start', 'mb-3', 'border', 'rounded-3', 'me-1');

    const currentPath = path ? `${path}.${key}` : key;

    const keyContainer = document.createElement('div');
    keyContainer.classList.add('d-flex', 'align-items-center', 'w-100');
    const keyLabel = document.createElement('h5');
    keyLabel.textContent = `${key}:`;
    keyLabel.classList.add('me-2', 'mb-0');
    keyContainer.appendChild(keyLabel);

    const commentKey = currentPath;
    const comment = comments ? comments[commentKey] : null;
    if (comment) {
      const reg = /(http:\/\/|https:\/\/)((\w|=|\?|\.|\/|&|-)+)/g;
      let commentWithLink = comment;
      commentWithLink = commentWithLink.replace(reg, `<a class="ms-2 me-2" href="$1$2" style="text-decoration:underline dotted;" target="_blank"><span>$1$2</span></a>`).replace(/\n/g, "<br />");

      const commentText = document.createElement('span');
      commentText.classList.add('text-muted', 'ms-2', 'me-2');
      commentText.style.fontSize = '0.9rem';
      commentText.style.whiteSpace = 'pre-wrap';
      commentText.innerHTML = commentWithLink;

      keyContainer.appendChild(commentText);
    }

    li.appendChild(keyContainer);

    const inputCommentContainer = document.createElement('div');
    inputCommentContainer.classList.add('d-flex', 'align-items-center', 'flex-grow-1', 'w-100', 'mt-1');

    if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
      if (typeof value === 'boolean') {
        const toggleContainer = document.createElement('div');
        toggleContainer.classList.add('form-check', 'form-switch', 'ps-0', 'is-filled', 'ms-1', 'my-1');
        const toggle = document.createElement('input');
        toggle.classList.add('form-check-input', 'ms-auto');
        toggle.type = "checkbox";
        toggle.checked = value;
        toggleContainer.appendChild(toggle);
        inputCommentContainer.appendChild(toggleContainer);

        toggle.addEventListener('change', (e) => {
          const value = e.target.checked;
          updateData(yamlData.data, currentPath, value);
        });
      } else {
        const itemContainer = document.createElement('div');
        itemContainer.classList.add('d-flex', 'align-items-center', 'mt-1', 'input-group', 'input-group-outline');

        const input = document.createElement('input');
        input.type = typeof value === 'number' ? 'number' : 'text';
        input.value = value;
        input.classList.add('form-control', 'form-control-sm');
        itemContainer.appendChild(input);
        inputCommentContainer.appendChild(itemContainer);

        input.addEventListener('input', (e) => {
          updateData(yamlData.data, currentPath, typeof value === 'number' ? parseFloat(e.target.value) : e.target.value);
        });
      }
      li.appendChild(inputCommentContainer);
    } else if (Array.isArray(value)) {
      const listContainer = document.createElement('div');
      listContainer.classList.add('flex-grow-1', 'w-100');
      value.forEach((item, index) => {
        const itemContainer = document.createElement('div');
        itemContainer.classList.add('d-flex', 'align-items-center', 'mt-1', 'input-group', 'input-group-outline');

        const itemInput = document.createElement('input');
        itemInput.type = 'text';
        itemInput.value = item;
        itemInput.classList.add('form-control', 'form-control-sm');
        itemInput.addEventListener('input', (e) => {
          updateData(yamlData.data, `${currentPath}[${index}]`, e.target.value);
        });

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.type = "button";
        deleteButton.classList.add('btn', 'btn-danger', 'btn-sm');
        deleteButton.addEventListener('click', () => {
          value.splice(index, 1);
          renderYamlEditor(yamlData, yamlEditor);
        });

        itemContainer.appendChild(itemInput);
        itemContainer.appendChild(deleteButton);
        listContainer.appendChild(itemContainer);
      });

      const addButton = document.createElement('button');
      addButton.textContent = 'Add Item';
      addButton.classList.add('btn', 'btn-success', 'btn-sm', 'mt-2');
      addButton.addEventListener('click', () => {
        value.push('');
        renderYamlEditor(yamlData, yamlEditor);
      });

      listContainer.appendChild(addButton);
      li.appendChild(listContainer);
    } else if (typeof value === 'object') {
      const nestedContainer = document.createElement('div');
      nestedContainer.classList.add('ms-3', 'mt-2', 'flex-grow-1', 'w-100');
      createEditorElements(value, comments, nestedContainer, order, currentPath);
      li.appendChild(nestedContainer);
    }

    ul.appendChild(li);
  });

  parent.appendChild(ul);
}

function updateData(data, path, newValue) {
  const pathParts = path.split('.');
  let current = data;
  for (let i = 0; i < pathParts.length - 1; i++) {
    if (pathParts[i].includes('[')) {
      const [key, indexStr] = pathParts[i].split('[');
      const index = parseInt(indexStr.replace(']', ''), 10);
      current = current[key][index];
    } else {
      current = current[pathParts[i]];
    }
  }
  const lastPart = pathParts[pathParts.length - 1];
  if (lastPart.includes('[')) {
    const [key, indexStr] = lastPart.split('[');
    const index = parseInt(indexStr.replace(']', ''), 10);
    current[key][index] = newValue;
  } else {
    current[lastPart] = newValue;
  }
}

saveButton.addEventListener('click', saveYamlFile);

fetchYamlFiles();
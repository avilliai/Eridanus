document.addEventListener('DOMContentLoaded', function () {
    // 获取下拉菜单元素
    const dropdownMenu = document.querySelector('.dropdown-menu');
    // 获取下拉菜单按钮元素
    const dropdownButton = document.getElementById('dropdownMenuButton');
    // 获取提交按钮元素
    const submitButton = document.getElementById('submitButton');
    let selectedSource = '';

    // 从 ./api/sources 获取数据
    fetch('./api/sources')
      .then(response => response.json())
      .then(data => {
        const sources = data.sources;
        sources.forEach(source => {
          // 创建下拉菜单选项
          const listItem = document.createElement('li');
          const link = document.createElement('a');
          link.classList.add('dropdown-item');
          link.href = 'javascript:;';
          link.textContent = source;
          link.addEventListener('click', function (event) {
            event.preventDefault();
            // 更新下拉菜单按钮文本
            dropdownButton.textContent = source;
            selectedSource = source;
          });
          listItem.appendChild(link);
          dropdownMenu.appendChild(listItem);
        });
      })
      .catch(error => console.error('获取数据时出错:', error));

    // 提交按钮点击事件处理
    submitChoice.addEventListener('click', function () {
      if (selectedSource) {
        const data = { choice: selectedSource };
        // 发送 POST 请求
        fetch('./api/pull', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        })
          .then(response => response.json())
          .then(result => console.log('提交成功:', result))
          .catch(error => console.error('提交时出错:', error));
      } else {
        console.log('请先选择一个源。');
      }
    });
  });
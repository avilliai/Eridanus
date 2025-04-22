document.addEventListener('DOMContentLoaded', function () {

  const loginButton = document.getElementById('login');


  loginButton.addEventListener('click', async () => {

    const accountInput = document.getElementById('account');
    const passwordInput = document.getElementById('password');

    const account = accountInput.value;
    const password = passwordInput.value;
    const encryptedPassword = sha3_256(password);

    try {

      const response = await fetch('./api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          account: account,
          password: encryptedPassword
        })
      });

      const data = await response.json();

      if (data.message === 'Success') {
        localStorage.setItem('auth_token', getCookie('auth_token'));
        // 登录成功，跳转到主页
        showAlert('alert-success','登录成功');
        setTimeout(()=>{window.location.href = './'},1000);
      } else {
        showAlert('alert-danger','账户或密码错误')
      }
    } catch (error) {
      showAlert('alert-danger','网络连接出错')
    }
  });
})

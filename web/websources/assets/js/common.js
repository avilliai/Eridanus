let darkModeFlag = false;

function initDarkMode() {
    let darkModeStorage = localStorage.getItem('darkMode');
    if (darkModeStorage === null) {
        const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        darkModeMediaQuery.matches ? darkModeFlag = true : darkModeFlag = false;
        localStorage.setItem('darkMode', darkModeFlag);
    }
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add("dark-version");
    }
}

function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
    return match ? match[2] : null;
}

initDarkMode()

async function checkProfile(){
const response = await fetch('./api/profile', {
    method: 'GET',
    headers: {
        'Content-Type': 'application/json'
    }
});
const data = await response.json();
if(data.error && window.location.pathname != "/login.html")window.location.href="./login.html"
}

checkProfile()
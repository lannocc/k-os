document.write(`
  <label>
    <div class="slider"><input id="theme" type="checkbox"/><span></span></div>
    dark theme
  </label>
`);

document.getElementById('theme').addEventListener('change', (event) => {
    if (event.target.checked) {
        document.documentElement.classList.add('theme');
        localStorage.setItem('ktheme', 'true');
    }
    else {
        document.documentElement.classList.remove('theme');
        localStorage.setItem('ktheme', 'false');
    }
}, false);

if (localStorage.getItem('ktheme') == 'true') {
    document.getElementById('theme').checked = true;
    document.documentElement.classList.add('theme');
}


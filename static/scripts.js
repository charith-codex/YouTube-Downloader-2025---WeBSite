const socket = io();

// Handle Cookies Upload
document.getElementById('cookiesForm').onsubmit = async function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  const response = await fetch('/upload-cookies', {
    method: 'POST',
    body: formData,
  });
  const result = await response.json();
  document.getElementById('cookiesMessage').innerText =
    result.success || result.error;
};

// Handle Download
document.getElementById('downloadForm').onsubmit = async function (e) {
  e.preventDefault();
  const formData = new FormData(this);
  const response = await fetch('/download', {
    method: 'POST',
    body: formData,
  });
  if (response.ok) {
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'downloaded_file';
    document.body.appendChild(a);
    a.click();
    a.remove();
  } else {
    const result = await response.json();
    alert(result.error || 'An error occurred.');
  }
};

// Progress Bar Updates
socket.on('progress', (data) => {
  const progressBar = document.getElementById('progressBar');
  const progressContainer = document.querySelector('.progress-container');
  progressContainer.style.display = 'block';
  progressBar.style.width = data.progress;
  progressBar.innerText = `${data.progress} (${data.eta}s remaining)`;
});

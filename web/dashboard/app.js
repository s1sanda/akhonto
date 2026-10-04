document.addEventListener('DOMContentLoaded', () => {
  const status = document.querySelector('.status-pill');
  const deviceCards = document.getElementById('device-cards');
  const fileList = document.getElementById('file-list');

  function renderDevices(devices) {
    if (!deviceCards) return;

    if (!devices.length) {
      deviceCards.innerHTML = '<article class="card"><h3>No devices</h3><p>Register a device from the client app.</p></article>';
      return;
    }

    deviceCards.innerHTML = devices
      .map((device) => {
        const isOnline = device.is_online;
        return `
          <article class="card">
            <h3>${device.device_name}</h3>
            <p>${device.device_type} · ${device.os_name || 'unknown OS'}</p>
            <p>Battery: ${device.battery_level ?? 'n/a'}%</p>
            <p>Last seen: ${new Date(device.last_seen).toLocaleString()}</p>
            <p class="highlight ${isOnline ? 'online' : 'offline'}">${isOnline ? 'ONLINE' : 'OFFLINE'}</p>
          </article>
        `;
      })
      .join('');
  }

  function renderFiles(files) {
    if (!fileList) return;

    if (!files.length) {
      fileList.innerHTML = '<li>No uploaded files yet.</li>';
      return;
    }

    fileList.innerHTML = files
      .slice(0, 5)
      .map((file) => `<li>${file.original_name} · ${file.size_bytes} bytes</li>`)
      .join('');
  }

  fetch('/api/health')
    .then((response) => response.json())
    .then((data) => {
      if (status && data.status === 'ok') {
        status.textContent = 'System OK';
      }
      return Promise.all([
        fetch('/api/devices').then((response) => response.json()),
        fetch('/api/files').then((response) => response.json()),
      ]);
    })
    .then(([deviceData, fileData]) => {
      renderDevices(deviceData.devices || []);
      renderFiles(fileData.files || []);
    })
    .catch(() => {
      if (status) {
        status.textContent = 'Server Offline';
        status.style.background = '#f59e0b';
      }
      if (fileList) {
        fileList.innerHTML = '<li>File service unavailable.</li>';
      }
    });
});

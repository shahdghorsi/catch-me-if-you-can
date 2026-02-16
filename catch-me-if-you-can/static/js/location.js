/**
 * Location Tracking and WebSocket Communication
 */

let socket = null;
let renderer = null;
let currentUserId = null;
let watchId = null;
let lastUpdateTime = 0;
const UPDATE_INTERVAL = 120000; // 2 minutes in milliseconds

/**
 * Initialize the application
 */
function initializeApp(userId) {
    currentUserId = userId;

    // Initialize stick figure renderer
    renderer = new StickFigureRenderer('vibesCanvas');

    // Initialize WebSocket connection
    initSocket();

    // If user is checked in, show their info and start tracking
    if (userId) {
        showUserInfo(userId);
        requestLocationPermission();
    }

    // Fetch initial data
    fetchPeople();

    // Handle page visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);

    // Handle page unload
    window.addEventListener('beforeunload', handleBeforeUnload);
}

/**
 * Initialize WebSocket connection
 */
function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
        if (currentUserId) {
            socket.emit('register_user', { user_id: parseInt(currentUserId) });
        }
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    socket.on('people_updated', (data) => {
        updateDashboard(data);
    });

    socket.on('user_joined', (user) => {
        showNotification(`${user.name} just checked in!`, 'info');
    });

    socket.on('user_left', (data) => {
        showNotification(`${data.name} left`, 'info');
    });
}

/**
 * Fetch current people data
 */
async function fetchPeople() {
    try {
        const response = await fetch('/api/people');
        const data = await response.json();
        updateDashboard(data);
    } catch (error) {
        console.error('Failed to fetch people:', error);
    }
}

/**
 * Update the dashboard with new data
 */
function updateDashboard(data) {
    // Update canvas
    if (renderer) {
        renderer.updateData(data);
    }

    // Update zone summary cards
    updateZoneSummary(data);

    // Check for join alerts
    checkJoinAlerts(data);
}

/**
 * Update zone summary cards
 */
function updateZoneSummary(data) {
    const container = document.getElementById('zoneSummary');
    if (!container) return;

    const grouped = data.grouped || {};
    const zoneTypes = ['office', 'pub', 'restaurant', 'cafe', 'gym', 'unknown'];
    const zoneNames = {
        office: 'At the Office',
        pub: 'At the Pub',
        restaurant: 'Getting Lunch',
        cafe: 'Coffee Break',
        gym: 'Working Out',
        unknown: 'Out & About'
    };
    const zoneIcons = {
        office: '🏢',
        pub: '🍺',
        restaurant: '🍕',
        cafe: '☕',
        gym: '🏃',
        unknown: '📍'
    };

    let html = '';

    for (const zoneType of zoneTypes) {
        const clusters = grouped[zoneType] || [];
        const people = clusters.flatMap(c => c.members);

        if (people.length === 0) continue;

        html += `
            <div class="zone-card ${zoneType}">
                <div class="zone-card-header">
                    <span class="zone-icon">${zoneIcons[zoneType]}</span>
                    <span class="zone-name">${zoneNames[zoneType]}</span>
                </div>
                <div class="zone-count">${people.length}</div>
                <div class="zone-people">
                    ${people.map(p => `
                        <span class="person-chip">
                            <span class="chip-emoji">${p.avatar_emoji || '😀'}</span>
                            ${p.name}
                        </span>
                    `).join('')}
                </div>
            </div>
        `;
    }

    container.innerHTML = html || '<div class="empty-state"><h3>No one is here yet</h3><p>Be the first to check in!</p></div>';
}

/**
 * Check for join alerts (when multiple people are at the same place)
 */
function checkJoinAlerts(data) {
    const container = document.getElementById('notifications');
    if (!container) return;

    const grouped = data.grouped || {};
    let alerts = [];

    // Check for groups at pubs or restaurants
    ['pub', 'restaurant', 'cafe'].forEach(zoneType => {
        const clusters = grouped[zoneType] || [];
        for (const cluster of clusters) {
            if (cluster.members.length >= 2) {
                const zoneName = cluster.zone || (zoneType === 'pub' ? 'the pub' : 'lunch');
                alerts.push({
                    count: cluster.members.length,
                    zone: zoneName,
                    type: zoneType
                });
            }
        }
    });

    if (alerts.length === 0) {
        container.innerHTML = '';
        return;
    }

    container.innerHTML = alerts.map(alert => `
        <div class="notification join-alert">
            <span class="notification-text">
                🎉 ${alert.count} people at ${alert.zone} - JOIN THEM!
            </span>
        </div>
    `).join('');
}

/**
 * Show user info bar
 */
async function showUserInfo(userId) {
    const userInfo = document.getElementById('userInfo');
    if (!userInfo) return;

    try {
        const response = await fetch(`/api/user/${userId}`);
        const user = await response.json();

        document.getElementById('userName').textContent = user.name;
        if (user.current_zone) {
            document.getElementById('userZone').textContent = user.current_zone;
        }

        userInfo.classList.remove('hidden');
    } catch (error) {
        console.error('Failed to fetch user info:', error);
    }
}

/**
 * Request location permission and start tracking
 */
function requestLocationPermission() {
    if (!navigator.geolocation) {
        updateLocationStatus('Location not supported', false);
        return;
    }

    updateLocationStatus('Requesting location...', true);

    // Start watching position
    watchId = navigator.geolocation.watchPosition(
        handlePositionUpdate,
        handlePositionError,
        {
            enableHighAccuracy: true,
            maximumAge: UPDATE_INTERVAL,
            timeout: 30000
        }
    );
}

/**
 * Handle position update from GPS
 */
function handlePositionUpdate(position) {
    const now = Date.now();

    // Only send updates every 2 minutes (or first time)
    if (lastUpdateTime === 0 || now - lastUpdateTime >= UPDATE_INTERVAL) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        sendLocationUpdate(latitude, longitude);
        lastUpdateTime = now;

        updateLocationStatus(`📍 ${latitude.toFixed(4)}, ${longitude.toFixed(4)}`, true);
    }
}

/**
 * Handle position error
 */
function handlePositionError(error) {
    let message = 'Location error';

    switch (error.code) {
        case error.PERMISSION_DENIED:
            message = 'Location permission denied';
            break;
        case error.POSITION_UNAVAILABLE:
            message = 'Location unavailable';
            break;
        case error.TIMEOUT:
            message = 'Location timeout';
            break;
    }

    updateLocationStatus(message, false);
    console.error('Geolocation error:', error);
}

/**
 * Send location update to server
 */
function sendLocationUpdate(latitude, longitude) {
    if (!socket || !currentUserId) return;

    socket.emit('location_update', {
        user_id: parseInt(currentUserId),
        latitude: latitude,
        longitude: longitude
    });
}

/**
 * Update location status display
 */
function updateLocationStatus(message, isActive) {
    const statusEl = document.getElementById('locationStatus');
    if (!statusEl) return;

    statusEl.innerHTML = `
        <span class="icon">${isActive ? '📍' : '⚠️'}</span>
        <span>${message}</span>
    `;

    const statusDot = document.querySelector('.status-dot');
    if (statusDot) {
        statusDot.classList.toggle('active', isActive);
    }
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    const container = document.getElementById('notifications');
    if (!container) return;

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `<span class="notification-text">${message}</span>`;

    container.appendChild(notification);

    // Remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

/**
 * Handle page visibility change
 */
function handleVisibilityChange() {
    if (document.hidden) {
        // Page is hidden, could pause tracking here
    } else {
        // Page is visible, refresh data
        fetchPeople();
    }
}

/**
 * Handle page unload
 */
function handleBeforeUnload() {
    if (socket && currentUserId) {
        socket.emit('user_inactive', { user_id: parseInt(currentUserId) });
    }

    if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId);
    }
}

// Export for use in HTML
window.initializeApp = initializeApp;

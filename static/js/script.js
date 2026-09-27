document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // 1. Leaflet Map Setup (Home Page)
    // ==========================================
    const mapElement = document.getElementById('restaurant-map');
    if (mapElement) {
        // DISABLE DEFAULT LEAFLET ZOOM BUTTONS
        const map = L.map('restaurant-map', {
            zoomControl: false 
        }).setView([21.1938, 81.3509], 13);

        // Map Tile Layer
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors'
        }).addTo(map);

        // Custom Map Pin Style
        function createMapPin(status) {
            let color = '#22c55e'; // Green GO
            if (status === 'wait') color = '#eab308'; // Yellow WAIT
            if (status === 'busy') color = '#ef4444'; // Red BUSY

            return L.divIcon({
                className: 'custom-map-pin',
                html: `<div style="
                    background-color: ${color};
                    width: 18px;
                    height: 18px;
                    border-radius: 50%;
                    border: 3px solid #ffffff;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.4);
                "></div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            });
        }

        
            // Use the live data from the database, or fallback to default if it fails to load
        const locations = window.liveRestaurantData || [];

        const markerMap = {};

        locations.forEach(loc => {
            const marker = L.marker([loc.lat, loc.lng], {
                icon: createMapPin(loc.status)
            }).addTo(map);

            const popupContent = `
                <div class="map-popup">
                    <h4>${loc.name}</h4>
                    <p>📍 ${loc.address}</p>
                    <p>⏱ Est. Wait: <strong>${loc.wait}</strong></p>
                    <div class="map-popup-badge ${loc.status}">${loc.statusLabel}</div>
                </div>
            `;

            marker.bindPopup(popupContent);
            markerMap[loc.name.toLowerCase()] = { marker: marker, lat: loc.lat, lng: loc.lng };
        });

        // CONNECT GLASS ZOOM BUTTONS
        const zoomInBtn = document.getElementById('zoom-in');
        const zoomOutBtn = document.getElementById('zoom-out');

        if (zoomInBtn) zoomInBtn.addEventListener('click', () => map.zoomIn());
        if (zoomOutBtn) zoomOutBtn.addEventListener('click', () => map.zoomOut());

        // CONNECT GLASS SEARCH BAR
        const searchInput = document.getElementById('map-search-input');
        if (searchInput) {
            searchInput.addEventListener('input', function (e) {
                const query = e.target.value.toLowerCase().trim();
                if (!query) return;

                const matchKey = Object.keys(markerMap).find(key => key.includes(query));
                if (matchKey) {
                    const target = markerMap[matchKey];
                    map.flyTo([target.lat, target.lng], 15, { animate: true, duration: 1.2 });
                    target.marker.openPopup();
                }
            });
        }
    }

    // ==========================================
    // 2. Dynamic Progress Bar (Dashboard)
    // ==========================================
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar && progressBar.dataset.width) {
        progressBar.style.width = progressBar.dataset.width + '%';
    }

    // ==========================================
    // 3. Occupied table calculation (Dashboard)
    // ==========================================
    const occupiedInput = document.getElementById("occupiedTables");
    const availablePreview = document.getElementById("availablePreview");
    const dashboardAvailable = document.getElementById("dashboardAvailableTables");
    const progress = document.getElementById("availabilityProgress");

    if (occupiedInput && availablePreview) {
        const totalTables = parseInt(occupiedInput.max || 0);

        function updateAvailability() {
            let occupied = parseInt(occupiedInput.value) || 0;

            if (occupied < 0) occupied = 0;
            if (totalTables > 0 && occupied > totalTables) {
                occupied = totalTables;
                occupiedInput.value = totalTables;
            }

            const available = totalTables - occupied;
            availablePreview.textContent = available;

            if (dashboardAvailable) dashboardAvailable.textContent = available;

            if (progress) {
                const percentage = totalTables > 0 ? (available / totalTables) * 100 : 0;
                progress.style.width = percentage + "%";
            }
        }

        occupiedInput.addEventListener("input", updateAvailability);
        updateAvailability();
    }

    // ==========================================
    // 4. Form submission protection (Dashboard Fix)
    // ==========================================
    const form = document.getElementById("crowdForm");
    if (form) {
        form.addEventListener("submit", function () {
            const button = form.querySelector("button[type='submit']");
            if (button) {
                // The setTimeout prevents the browser from blocking the submission
                setTimeout(function() {
                    button.textContent = "Updating AI System...";
                    button.disabled = true;
                }, 10);
            }
        });
    }

    // ==========================================
    // 5. Automatically convert timestamps
    // ==========================================
    const timestamps = document.querySelectorAll(".timestamp");
    timestamps.forEach(function (element) {
        const value = element.textContent.trim();
        if (!value) return;

        const date = new Date(value.replace(" ", "T") + "Z");
        if (!isNaN(date.getTime())) {
            element.textContent = date.toLocaleString("en-IN", {
                day: "2-digit",
                month: "short",
                year: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });
        }
    });

    // ==========================================
    // 6. Smooth scrolling
    // ==========================================
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener("click", function (event) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                event.preventDefault();
                target.scrollIntoView({ behavior: "smooth" });
            }
        });
    });
});
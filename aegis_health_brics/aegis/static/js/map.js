/**
 * Geospatial Map visualization for AegisHealth BRICS using Leaflet.js
 */

let mapInstance = null;
let markersLayer = null;
let routesLayer = null;

function initHealthMap() {
    const mapContainer = document.getElementById('healthMap');
    if (!mapContainer || mapInstance) return;

    // Center over district network (Andhra Pradesh / Telangana cluster)
    mapInstance = L.map('healthMap', {
        zoomControl: true,
        attributionControl: false
    }).setView([16.0, 80.2], 7);

    // Dark theme CartoDB basemap tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 18,
        subdomains: 'abcd',
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(mapInstance);

    markersLayer = L.layerGroup().addTo(mapInstance);
    routesLayer = L.layerGroup().addTo(mapInstance);
}

function updateMapFacilities(facilities) {
    if (!mapInstance || !markersLayer) {
        initHealthMap();
    }
    if (!markersLayer) return;

    markersLayer.clearLayers();

    facilities.forEach(fac => {
        const isCritical = fac.overall_status === 'CRITICAL';
        const isWarning = fac.overall_status === 'WARNING';

        let color = '#10B981'; // green
        let pulseClass = '';
        if (isCritical) {
            color = '#EF4444'; // red
            pulseClass = 'pulse-badge-danger';
        } else if (isWarning) {
            color = '#F59E0B'; // amber
        }

        const iconHtml = `
            <div style="background-color: ${color}; width: 18px; height: 18px; border-radius: 50%; border: 3px solid #111827; box-shadow: 0 0 10px ${color};" class="${pulseClass}"></div>
        `;

        const customIcon = L.divIcon({
            html: iconHtml,
            className: 'custom-map-pin',
            iconSize: [18, 18],
            iconAnchor: [9, 9]
        });

        const marker = L.marker([fac.latitude, fac.longitude], { icon: customIcon });

        const critMeds = fac.inventory.filter(i => i.status === 'CRITICAL');
        const beds = fac.beds;
        const staff = fac.staff;

        const popupContent = `
            <div class="p-1 min-w-[210px] text-xs">
                <div class="flex items-center justify-between pb-1 mb-1 border-b border-gray-700">
                    <span class="font-bold text-sm text-white">${fac.name}</span>
                    <span class="px-1.5 py-0.5 rounded text-[10px] font-semibold ${
                        fac.type === 'DH' ? 'bg-purple-900 text-purple-200' :
                        fac.type === 'CHC' ? 'bg-blue-900 text-blue-200' : 'bg-emerald-900 text-emerald-200'
                    }">${fac.type}</span>
                </div>
                <div class="text-gray-300 space-y-0.5">
                    <div><strong>District:</strong> ${fac.district}</div>
                    <div><strong>Beds:</strong> ${beds.occupied}/${beds.total} (${Math.round(beds.occupancy_rate * 100)}% occ)</div>
                    <div><strong>Staff On Duty:</strong> ${staff.doctors_on_duty} Docs, ${staff.nurses_on_duty} Nurses</div>
                    <div><strong>Risk Score:</strong> <span class="font-bold ${isCritical ? 'text-red-400' : (isWarning ? 'text-amber-400' : 'text-emerald-400')}">${fac.risk_score}/100</span></div>
                    ${critMeds.length > 0 ? `
                        <div class="mt-1 text-red-400 font-semibold bg-red-950/60 p-1 rounded">
                            ⚠️ ${critMeds.length} Critical Stockouts (${critMeds.map(m => m.name.split(' ')[0]).join(', ')})
                        </div>
                    ` : ''}
                </div>
                <button onclick="window.viewFacilityDetail('${fac.id}')" class="mt-2 w-full py-1 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-medium text-center transition">
                    Inspect Facility Full Status
                </button>
            </div>
        `;

        marker.bindPopup(popupContent);
        markersLayer.addLayer(marker);
    });
}

function renderTransferRoutes(transfers) {
    if (!routesLayer) return;
    routesLayer.clearLayers();

    transfers.forEach(tr => {
        if (!tr.source_lat || !tr.target_lat) return;

        const latlngs = [
            [tr.source_lat, tr.source_lon],
            [tr.target_lat, tr.target_lon]
        ];

        const isEmergency = tr.priority === 'EMERGENCY';
        const color = isEmergency ? '#EF4444' : '#8B5CF6';

        const polyline = L.polyline(latlngs, {
            color: color,
            weight: 3,
            dashArray: '6, 8',
            opacity: 0.85
        });

        polyline.bindPopup(`
            <div class="text-xs p-1">
                <div class="font-bold text-white mb-1">🚚 Redistribution Route [${tr.id}]</div>
                <div><strong>Item:</strong> ${tr.item_name} (${tr.quantity} ${tr.unit})</div>
                <div><strong>From:</strong> ${tr.source_facility_name}</div>
                <div><strong>To:</strong> ${tr.target_facility_name}</div>
                <div><strong>Distance:</strong> ${tr.distance_km} km (~${tr.estimated_transit_hours} hrs)</div>
                <div><strong>Priority:</strong> <span class="text-red-400 font-bold">${tr.priority}</span></div>
            </div>
        `);

        routesLayer.addLayer(polyline);
    });
}

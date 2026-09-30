/**
 * AegisHealth BRICS - Main Frontend Controller
 */

let allFacilities = [];
let allAlerts = [];
let medicineCatalog = [];
let activeTab = 'overview';

document.addEventListener('DOMContentLoaded', async () => {
    initTabs();
    await loadMedicineCatalog();
    await refreshAllDashboardData();
    initHealthMap();

    // Auto-refresh stats every 45 seconds
    setInterval(async () => {
        await refreshSystemStats();
    }, 45000);
});

// -------------------------------------------------------------
// TAB MANAGEMENT
// -------------------------------------------------------------
function initTabs() {
    const tabButtons = document.querySelectorAll('.nav-tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.getAttribute('data-tab');
            switchTab(target);
        });
    });
}

function switchTab(tabId) {
    activeTab = tabId;
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    const targetEl = document.getElementById(`tab-${tabId}`);
    if (targetEl) targetEl.classList.remove('hidden');

    document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        if (btn.getAttribute('data-tab') === tabId) {
            btn.classList.add('bg-cyan-950/60', 'text-cyan-400', 'border-cyan-500');
            btn.classList.remove('text-gray-400', 'border-transparent');
        } else {
            btn.classList.remove('bg-cyan-950/60', 'text-cyan-400', 'border-cyan-500');
            btn.classList.add('text-gray-400', 'border-transparent');
        }
    });

    if (tabId === 'overview') {
        setTimeout(() => {
            if (mapInstance) mapInstance.invalidateSize();
        }, 100);
    } else if (tabId === 'forecasting') {
        loadForecastData();
    } else if (tabId === 'redistribution') {
        loadRedistributionRecommendations();
    } else if (tabId === 'federated') {
        loadFederatedData();
    }
}

// -------------------------------------------------------------
// DATA LOADING
// -------------------------------------------------------------
async function refreshAllDashboardData() {
    await Promise.all([
        refreshSystemStats(),
        loadFacilities(),
        loadAlerts(),
        loadTransfers()
    ]);
}
window.refreshAllDashboardData = refreshAllDashboardData;

async function refreshSystemStats() {
    try {
        const res = await fetch('/api/stats');
        const stats = await res.json();

        document.getElementById('stat-facilities').textContent = stats.total_facilities;
        document.getElementById('stat-beds').textContent = `${stats.occupied_beds}/${stats.total_beds}`;
        document.getElementById('stat-bed-rate').textContent = `${Math.round(stats.overall_occupancy_rate * 100)}% occupied`;
        document.getElementById('stat-staff').textContent = `${stats.total_doctors_on_duty} Docs / ${stats.total_nurses_on_duty} Nurses`;
        document.getElementById('stat-stockouts').textContent = stats.critical_stockouts_count;
        document.getElementById('stat-resilience').textContent = `${stats.overall_system_resilience_score}%`;
        document.getElementById('stat-brics-nodes').textContent = `${stats.federated_nodes_active} Active`;

        const badge = document.getElementById('critical-alert-badge');
        if (badge) {
            if (stats.critical_stockouts_count > 0) {
                badge.classList.remove('hidden');
                badge.textContent = `${stats.critical_stockouts_count} Critical`;
            } else {
                badge.classList.add('hidden');
            }
        }
    } catch (e) {
        console.error('Failed to fetch stats:', e);
    }
}

async function loadMedicineCatalog() {
    try {
        const res = await fetch('/api/catalog');
        medicineCatalog = await res.json();
        const select = document.getElementById('forecastMedicineSelect');
        if (select) {
            select.innerHTML = '';
            medicineCatalog.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = `${m.name} (${m.category})`;
                if (m.id === 'MED-004') opt.selected = true; // Default Normal Saline IV
                select.appendChild(opt);
            });
        }
    } catch (e) {
        console.error('Failed to load catalog:', e);
    }
}

async function loadFacilities() {
    try {
        const res = await fetch('/api/facilities');
        allFacilities = await res.json();
        renderFacilitiesGrid(allFacilities);
        renderInventoryTable(allFacilities);
        updateMapFacilities(allFacilities);

        // Populate facility select in forecast tab
        const facSelect = document.getElementById('forecastFacilitySelect');
        if (facSelect) {
            facSelect.innerHTML = `<option value="NATIONAL_AGGREGATE">National Aggregate (All Facilities)</option>`;
            allFacilities.forEach(f => {
                const opt = document.createElement('option');
                opt.value = f.id;
                opt.textContent = `${f.name} [${f.type}] - ${f.district}`;
                facSelect.appendChild(opt);
            });
        }
    } catch (e) {
        console.error('Failed to load facilities:', e);
    }
}

async function loadAlerts() {
    try {
        const res = await fetch('/api/alerts');
        allAlerts = await res.json();
        renderAlertsList(allAlerts);
    } catch (e) {
        console.error('Failed to load alerts:', e);
    }
}

async function loadTransfers() {
    try {
        const res = await fetch('/api/transfers');
        const transfers = await res.json();
        renderTransfersTable(transfers);
        renderTransferRoutes(transfers.filter(t => t.status === 'DISPATCHED' || t.status === 'IN_TRANSIT'));
    } catch (e) {
        console.error('Failed to load transfers:', e);
    }
}

// -------------------------------------------------------------
// RENDERING FUNCTIONS
// -------------------------------------------------------------
function renderAlertsList(alerts) {
    const container = document.getElementById('alertsContainer');
    if (!container) return;

    if (alerts.length === 0) {
        container.innerHTML = `
            <div class="p-4 text-center text-emerald-400 bg-emerald-950/20 rounded-lg border border-emerald-800/40">
                ✅ No critical stockouts or capacity bottlenecks detected. Network buffer is healthy.
            </div>
        `;
        return;
    }

    container.innerHTML = alerts.map(a => {
        const isCrit = a.severity === 'CRITICAL';
        return `
            <div class="p-3 mb-2.5 rounded-lg border ${isCrit ? 'border-red-900/80 bg-red-950/30' : 'border-amber-900/60 bg-amber-950/20'} flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                <div class="flex items-start space-x-3">
                    <span class="px-2 py-0.5 mt-0.5 rounded text-xs font-bold ${isCrit ? 'bg-red-900 text-red-200 pulse-badge-danger' : 'bg-amber-900 text-amber-200'}">
                        ${a.severity}
                    </span>
                    <div>
                        <div class="font-bold text-sm text-white">${a.facility_name} <span class="text-xs text-gray-400 font-normal">(${a.district})</span></div>
                        <div class="text-xs text-gray-300 mt-0.5">
                            <strong>${a.item_name}</strong> &bull; Runway: <span class="font-bold ${isCrit ? 'text-red-400' : 'text-amber-400'}">${a.runway_days} days</span> (Stock: ${a.current_stock})
                        </div>
                        <div class="text-[11px] text-gray-400 mt-1 italic">${a.recommended_action}</div>
                    </div>
                </div>
                <div class="flex items-center space-x-2 w-full md:w-auto">
                    <button onclick="dispatchAlertSMS('${a.id}')" class="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 text-cyan-300 text-xs rounded border border-cyan-800/50 flex items-center space-x-1 transition">
                        <span>📲 Notify DHO</span>
                    </button>
                    <button onclick="window.viewFacilityDetail('${a.facility_id}')" class="px-3 py-1.5 bg-cyan-700 hover:bg-cyan-600 text-white text-xs rounded font-medium transition">
                        Inspect
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

async function dispatchAlertSMS(alertId) {
    try {
        const res = await fetch(`/api/alerts/${alertId}/notify`, { method: 'POST' });
        const data = await res.json();
        showToast('📲 Emergency Dispatch Sent', data.message, 'info');
    } catch (e) {
        showToast('Error', 'Failed to dispatch alert notification.', 'error');
    }
}

function renderFacilitiesGrid(facilities) {
    const grid = document.getElementById('facilitiesGrid');
    if (!grid) return;

    grid.innerHTML = facilities.map(f => {
        const isCrit = f.overall_status === 'CRITICAL';
        const isWarn = f.overall_status === 'WARNING';
        const critMeds = f.inventory.filter(i => i.status === 'CRITICAL');

        return `
            <div class="glass-panel p-4 rounded-xl border ${isCrit ? 'border-red-900/60' : (isWarn ? 'border-amber-900/50' : 'border-gray-800')} hover:border-cyan-500/50 transition">
                <div class="flex items-center justify-between pb-2 border-b border-gray-800">
                    <div>
                        <div class="font-bold text-sm text-white">${f.name}</div>
                        <div class="text-xs text-gray-400">${f.district}, ${f.state}</div>
                    </div>
                    <span class="px-2 py-0.5 rounded text-xs font-semibold ${
                        f.type === 'DH' ? 'bg-purple-900/60 text-purple-300 border border-purple-700' :
                        f.type === 'CHC' ? 'bg-blue-900/60 text-blue-300 border border-blue-700' : 'bg-emerald-900/60 text-emerald-300 border border-emerald-700'
                    }">${f.type}</span>
                </div>

                <div class="grid grid-cols-2 gap-2 my-3 text-xs">
                    <div class="bg-gray-900/60 p-2 rounded">
                        <div class="text-gray-400">Bed Occupancy</div>
                        <div class="font-bold text-sm text-white">${f.beds.occupied} / ${f.beds.total}</div>
                        <div class="text-[10px] text-gray-400">${Math.round(f.beds.occupancy_rate * 100)}% (${f.beds.icu_occupied}/${f.beds.icu_total} ICU)</div>
                    </div>
                    <div class="bg-gray-900/60 p-2 rounded">
                        <div class="text-gray-400">Medical Staff</div>
                        <div class="font-bold text-sm text-white">${f.staff.doctors_on_duty} Doc &bull; ${f.staff.nurses_on_duty} Nurse</div>
                        <div class="text-[10px] ${f.staff.status === 'NORMAL' ? 'text-emerald-400' : 'text-amber-400'}">${Math.round(f.staff.attendance_ratio * 100)}% Attendance</div>
                    </div>
                </div>

                <div class="flex items-center justify-between pt-2 border-t border-gray-800/60">
                    <div class="text-xs">
                        ${critMeds.length > 0 ?
                            `<span class="text-red-400 font-bold">⚠️ ${critMeds.length} Critical Stockouts</span>` :
                            `<span class="text-emerald-400 font-medium">✓ Supplies Stable</span>`
                        }
                    </div>
                    <button onclick="window.viewFacilityDetail('${f.id}')" class="px-3 py-1 bg-cyan-700/80 hover:bg-cyan-600 text-white text-xs rounded transition font-medium">
                        Deep Dive
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

function filterFacilities() {
    const search = document.getElementById('facilitySearchInput')?.value.toLowerCase() || '';
    const dist = document.getElementById('facilityDistrictFilter')?.value || 'ALL';
    const type = document.getElementById('facilityTypeFilter')?.value || 'ALL';
    const status = document.getElementById('facilityStatusFilter')?.value || 'ALL';

    const filtered = allFacilities.filter(f => {
        const matchSearch = f.name.toLowerCase().includes(search) || f.code.toLowerCase().includes(search);
        const matchDist = dist === 'ALL' || f.district === dist;
        const matchType = type === 'ALL' || f.type === type;
        const matchStatus = status === 'ALL' || f.overall_status === status;
        return matchSearch && matchDist && matchType && matchStatus;
    });

    renderFacilitiesGrid(filtered);
}
window.filterFacilities = filterFacilities;

function renderInventoryTable(facilities) {
    const tbody = document.getElementById('inventoryTableBody');
    if (!tbody) return;

    let rows = [];
    facilities.forEach(fac => {
        fac.inventory.forEach(item => {
            rows.push({
                facility_name: fac.name,
                facility_type: fac.type,
                district: fac.district,
                ...item
            });
        });
    });

    tbody.innerHTML = rows.slice(0, 50).map(r => {
        const isCrit = r.status === 'CRITICAL';
        const isWarn = r.status === 'WARNING';
        const isSurplus = r.status === 'SURPLUS';

        return `
            <tr class="border-b border-gray-800 hover:bg-gray-800/40 text-xs">
                <td class="py-2.5 px-3 font-semibold text-white">${r.name}</td>
                <td class="py-2.5 px-3 text-gray-400">${r.facility_name} <span class="text-[10px] text-gray-500">(${r.district})</span></td>
                <td class="py-2.5 px-3 text-right font-mono">${r.current_stock} ${r.unit}</td>
                <td class="py-2.5 px-3 text-right text-gray-400 font-mono">${r.daily_burn_rate}/day</td>
                <td class="py-2.5 px-3 text-center">
                    <span class="px-2 py-0.5 rounded text-[11px] font-bold ${
                        isCrit ? 'bg-red-950 text-red-300 border border-red-800 pulse-badge-danger' :
                        (isWarn ? 'bg-amber-950 text-amber-300 border border-amber-800' :
                        (isSurplus ? 'bg-blue-950 text-blue-300 border border-blue-800' : 'bg-emerald-950 text-emerald-300 border border-emerald-800'))
                    }">
                        ${r.days_runway}d
                    </span>
                </td>
                <td class="py-2.5 px-3 text-center">
                    ${r.cold_chain ? `<span class="px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 text-[10px] border border-cyan-800">❄️ ${r.temp_range || '2-8°C'}</span>` : '<span class="text-gray-500">-</span>'}
                </td>
                <td class="py-2.5 px-3 text-gray-400 text-center font-mono text-[11px]">${r.batch_no}</td>
                <td class="py-2.5 px-3 text-gray-400 text-center">${r.expiry_date}</td>
            </tr>
        `;
    }).join('');
}

// -------------------------------------------------------------
// FACILITY MODAL DEEP DIVE
// -------------------------------------------------------------
function viewFacilityDetail(facId) {
    const fac = allFacilities.find(f => f.id === facId);
    if (!fac) return;

    const modal = document.getElementById('facilityModal');
    const content = document.getElementById('facilityModalContent');
    if (!modal || !content) return;

    const beds = fac.beds;
    const staff = fac.staff;

    content.innerHTML = `
        <div class="flex items-center justify-between pb-3 border-b border-gray-700">
            <div>
                <h3 class="text-lg font-bold text-white">${fac.name}</h3>
                <p class="text-xs text-gray-400">${fac.code} &bull; ${fac.district}, ${fac.state} &bull; Catchment Population: ${fac.catchment_population.toLocaleString()}</p>
            </div>
            <button onclick="closeFacilityModal()" class="text-gray-400 hover:text-white text-xl font-bold">&times;</button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 my-4">
            <!-- Beds Breakdown -->
            <div class="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                <h4 class="text-xs font-bold text-cyan-400 uppercase tracking-wider mb-2">🛏️ Bed Capacity & Occupancy</h4>
                <div class="space-y-1.5 text-xs">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Total Beds:</span>
                        <span class="font-bold text-white">${beds.occupied} / ${beds.total} (${Math.round(beds.occupancy_rate * 100)}% occupied)</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">ICU Beds:</span>
                        <span class="font-bold text-white">${beds.icu_occupied} / ${beds.icu_total}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Oxygen-Supported:</span>
                        <span class="font-bold text-white">${beds.oxygen_occupied} / ${beds.oxygen_total}</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Isolation/Epidemic:</span>
                        <span class="font-bold text-white">${beds.isolation_occupied} / ${beds.isolation_total}</span>
                    </div>
                </div>
            </div>

            <!-- Staffing Breakdown -->
            <div class="bg-gray-900/80 p-3 rounded-lg border border-gray-800">
                <h4 class="text-xs font-bold text-emerald-400 uppercase tracking-wider mb-2">👩‍⚕️ Medical Personnel On-Duty</h4>
                <div class="space-y-1.5 text-xs">
                    <div class="flex justify-between">
                        <span class="text-gray-400">Doctors:</span>
                        <span class="font-bold text-white">${staff.doctors_on_duty} / ${staff.doctors_total} on duty</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Nurses:</span>
                        <span class="font-bold text-white">${staff.nurses_on_duty} / ${staff.nurses_total} on duty</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Pharmacists & Lab Techs:</span>
                        <span class="font-bold text-white">${staff.pharmacists_on_duty} Pharm, ${staff.lab_techs_on_duty} Lab</span>
                    </div>
                    <div class="flex justify-between">
                        <span class="text-gray-400">Active ASHA Workers:</span>
                        <span class="font-bold text-white">${staff.asha_workers_active} in field</span>
                    </div>
                </div>
            </div>
        </div>

        <!-- Medicine Inventory -->
        <h4 class="text-xs font-bold text-amber-400 uppercase tracking-wider mb-2">💊 Essential Medicine Stocks & Runways</h4>
        <div class="overflow-x-auto max-h-64 overflow-y-auto border border-gray-800 rounded-lg">
            <table class="w-full text-xs text-left">
                <thead class="bg-gray-900 text-gray-400 sticky top-0">
                    <tr>
                        <th class="py-2 px-3">Medicine</th>
                        <th class="py-2 px-3 text-right">Current Stock</th>
                        <th class="py-2 px-3 text-right">Daily Burn</th>
                        <th class="py-2 px-3 text-center">Runway</th>
                        <th class="py-2 px-3 text-center">Cold Chain</th>
                        <th class="py-2 px-3 text-center">Status</th>
                    </tr>
                </thead>
                <tbody class="divide-y divide-gray-800">
                    ${fac.inventory.map(m => {
                        const isC = m.status === 'CRITICAL';
                        const isW = m.status === 'WARNING';
                        return `
                            <tr class="hover:bg-gray-800/50">
                                <td class="py-2 px-3 font-semibold text-white">${m.name}</td>
                                <td class="py-2 px-3 text-right font-mono">${m.current_stock} ${m.unit}</td>
                                <td class="py-2 px-3 text-right text-gray-400 font-mono">${m.daily_burn_rate}</td>
                                <td class="py-2 px-3 text-center font-bold ${isC ? 'text-red-400' : (isW ? 'text-amber-400' : 'text-emerald-400')}">
                                    ${m.days_runway}d
                                </td>
                                <td class="py-2 px-3 text-center">${m.cold_chain ? '❄️ Yes' : '-'}</td>
                                <td class="py-2 px-3 text-center">
                                    <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
                                        isC ? 'bg-red-950 text-red-300' : (isW ? 'bg-amber-950 text-amber-300' : 'bg-emerald-950 text-emerald-300')
                                    }">${m.status}</span>
                                </td>
                            </tr>
                        `;
                    }).join('')}
                </tbody>
            </table>
        </div>
    `;

    modal.classList.remove('hidden');
}
window.viewFacilityDetail = viewFacilityDetail;

function closeFacilityModal() {
    const modal = document.getElementById('facilityModal');
    if (modal) modal.classList.add('hidden');
}
window.closeFacilityModal = closeFacilityModal;

// -------------------------------------------------------------
// AI DEMAND FORECASTING
// -------------------------------------------------------------
async function loadForecastData() {
    const itemId = document.getElementById('forecastMedicineSelect')?.value || 'MED-004';
    const horizon = document.getElementById('forecastHorizonSelect')?.value || 14;
    const facId = document.getElementById('forecastFacilitySelect')?.value || 'NATIONAL_AGGREGATE';

    try {
        const url = `/api/forecast?item_id=${itemId}&horizon_days=${horizon}&facility_id=${facId}`;
        const res = await fetch(url);
        const data = await res.json();

        renderForecastChart(data);

        document.getElementById('forecast-growth-rate').textContent = `${data.growth_rate_pct > 0 ? '+' : ''}${data.growth_rate_pct}%`;
        document.getElementById('forecast-surge-index').textContent = `${data.surge_index}x`;
        document.getElementById('forecast-confidence').textContent = `${Math.round(data.confidence_score * 100)}%`;
        document.getElementById('forecast-risk-verdict').textContent = data.risk_assessment;
    } catch (e) {
        console.error('Failed to load forecast:', e);
    }
}
window.loadForecastData = loadForecastData;

// -------------------------------------------------------------
// REDISTRIBUTION OPTIMIZER
// -------------------------------------------------------------
async function loadRedistributionRecommendations() {
    const container = document.getElementById('recommendationsContainer');
    if (!container) return;

    container.innerHTML = `
        <div class="p-8 text-center text-gray-400">
            <span class="inline-block animate-spin mr-2">⚙️</span> Running AI logistics solver across multi-facility graph...
        </div>
    `;

    try {
        const res = await fetch('/api/redistribution/recommendations');
        const recs = await res.json();

        if (recs.length === 0) {
            container.innerHTML = `
                <div class="p-6 text-center text-emerald-400 bg-emerald-950/20 rounded-xl border border-emerald-800/40">
                    ✅ Optimal supply equilibrium achieved! All monitored facilities currently meet safe runway buffers.
                </div>
            `;
            return;
        }

        container.innerHTML = recs.map(r => `
            <div class="glass-panel p-4 rounded-xl border border-gray-800 hover:border-cyan-500/40 transition">
                <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
                    <div class="space-y-1">
                        <div class="flex items-center space-x-2">
                            <span class="px-2 py-0.5 rounded text-xs font-bold ${r.priority === 'EMERGENCY' ? 'bg-red-900 text-red-200 pulse-badge-danger' : 'bg-purple-900 text-purple-200'}">
                                ${r.priority}
                            </span>
                            <span class="px-2 py-0.5 rounded text-xs bg-gray-800 text-cyan-300 font-mono">${r.id}</span>
                            ${r.cold_chain_required ? `<span class="px-1.5 py-0.5 rounded text-[10px] bg-cyan-950 text-cyan-300 border border-cyan-800">❄️ Cold Chain Certified</span>` : ''}
                        </div>
                        <div class="font-bold text-base text-white mt-1">
                            ${r.item_name} &bull; <span class="text-cyan-400">${r.quantity} ${r.unit}</span>
                        </div>
                        <div class="text-xs text-gray-300">
                            <strong>From:</strong> ${r.source_facility_name} (${r.source_district}) &rarr; <strong>To:</strong> ${r.target_facility_name} (${r.target_district})
                        </div>
                        <div class="text-xs text-gray-400">
                            Route Distance: <span class="text-white font-mono font-semibold">${r.distance_km} km</span> &bull; Transit: <span class="text-white font-mono font-semibold">~${r.estimated_transit_hours} hrs</span>
                        </div>
                        <div class="text-[11px] text-gray-400 italic">${r.rationale}</div>
                    </div>
                    <button onclick="dispatchSpecificTransfer('${r.id}')" class="px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white rounded-lg text-xs font-bold shadow-lg shadow-cyan-900/40 transition flex items-center space-x-1 whitespace-nowrap">
                        <span>🚀 Approve & Dispatch</span>
                    </button>
                </div>
            </div>
        `).join('');

        renderTransferRoutes(recs);

    } catch (e) {
        console.error('Failed to load recommendations:', e);
    }
}
window.loadRedistributionRecommendations = loadRedistributionRecommendations;

async function autoDispatchAllTransfers() {
    try {
        const res = await fetch('/api/redistribution/dispatch?auto_all=true', { method: 'POST' });
        const data = await res.json();
        showToast('🚚 Automated Dispatch Complete', `Successfully approved and dispatched ${data.dispatched_count} cross-district emergency transfer manifests.`, 'success');
        await refreshAllDashboardData();
        await loadRedistributionRecommendations();
    } catch (e) {
        showToast('Error', 'Failed to dispatch transfers.', 'error');
    }
}
window.autoDispatchAllTransfers = autoDispatchAllTransfers;

async function dispatchSpecificTransfer(transferId) {
    try {
        const res = await fetch(`/api/redistribution/dispatch?transfer_id=${transferId}`, { method: 'POST' });
        const data = await res.json();
        showToast('🚚 Transfer Dispatched', `Transfer manifest ${transferId} has been authorized and dispatched.`, 'success');
        await refreshAllDashboardData();
        await loadRedistributionRecommendations();
    } catch (e) {
        showToast('Error', 'Failed to dispatch transfer.', 'error');
    }
}
window.dispatchSpecificTransfer = dispatchSpecificTransfer;

function renderTransfersTable(transfers) {
    const tbody = document.getElementById('transfersTableBody');
    if (!tbody) return;

    if (transfers.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="py-6 text-center text-gray-500 text-xs">No active transfer orders. Click "Run Optimization" above to stage rebalancing.</td></tr>`;
        return;
    }

    tbody.innerHTML = transfers.map(t => `
        <tr class="border-b border-gray-800 text-xs">
            <td class="py-2.5 px-3 font-mono font-bold text-cyan-400">${t.id}</td>
            <td class="py-2.5 px-3 font-semibold text-white">${t.item_name}</td>
            <td class="py-2.5 px-3 font-mono">${t.quantity} ${t.unit}</td>
            <td class="py-2.5 px-3 text-gray-300">${t.source_facility_name}</td>
            <td class="py-2.5 px-3 text-gray-300">${t.target_facility_name}</td>
            <td class="py-2.5 px-3 text-center">
                <span class="px-2 py-0.5 rounded text-[10px] font-bold ${
                    t.status === 'DELIVERED' ? 'bg-emerald-950 text-emerald-300' :
                    (t.status === 'DISPATCHED' ? 'bg-cyan-950 text-cyan-300 pulse-badge-cyan' : 'bg-gray-800 text-gray-300')
                }">${t.status}</span>
            </td>
            <td class="py-2.5 px-3 text-gray-400 text-center">${t.created_at}</td>
        </tr>
    `).join('');
}

// -------------------------------------------------------------
// BRICS FEDERATED AI ALLIANCE
// -------------------------------------------------------------
async function loadFederatedData() {
    try {
        const [nodesRes, metricsRes] = await Promise.all([
            fetch('/api/federated/nodes'),
            fetch('/api/federated/metrics')
        ]);
        const nodes = await nodesRes.json();
        const metrics = await metricsRes.json();

        renderFederatedNodes(nodes);
        renderFederatedChart(metrics.rounds_history);

        document.getElementById('fed-global-loss').textContent = metrics.global_loss;
        document.getElementById('fed-current-round').textContent = `Round ${metrics.current_round}`;
        document.getElementById('fed-privacy-eps').textContent = `ε = ${metrics.privacy_budget_total}`;

        // Render feature importance
        const featContainer = document.getElementById('federatedWeightsContainer');
        if (featContainer && metrics.feature_coefficients) {
            featContainer.innerHTML = Object.entries(metrics.feature_coefficients).map(([k, v]) => `
                <div class="flex justify-between items-center py-1.5 border-b border-gray-800 text-xs">
                    <span class="text-gray-300">${k}</span>
                    <span class="font-mono font-bold text-cyan-400">${v}</span>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Failed to load federated data:', e);
    }
}

function renderFederatedNodes(nodes) {
    const container = document.getElementById('bricsNodesGrid');
    if (!container) return;

    container.innerHTML = nodes.map(n => `
        <div class="glass-panel p-4 rounded-xl border border-gray-800 hover:border-cyan-500/50 transition">
            <div class="flex items-center justify-between pb-2 border-b border-gray-800">
                <div class="flex items-center space-x-2">
                    <span class="text-2xl">${n.flag}</span>
                    <div>
                        <div class="font-bold text-sm text-white">${n.country}</div>
                        <div class="text-[10px] text-gray-400">${n.institution}</div>
                    </div>
                </div>
                <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-300 border border-emerald-800">
                    ● ${n.status}
                </span>
            </div>
            <div class="grid grid-cols-2 gap-2 my-2.5 text-xs">
                <div class="bg-gray-900/60 p-2 rounded">
                    <div class="text-gray-400">Facilities Monitored</div>
                    <div class="font-bold text-sm text-white font-mono">${n.facilities_monitored.toLocaleString()}</div>
                </div>
                <div class="bg-gray-900/60 p-2 rounded">
                    <div class="text-gray-400">Sync Latency</div>
                    <div class="font-bold text-sm text-cyan-400 font-mono">${n.latency_ms} ms</div>
                </div>
            </div>
            <div class="flex justify-between items-center text-[11px] text-gray-400 pt-1">
                <span>FedAvg Weight: <strong>${n.federation_contribution}%</strong></span>
                <span>Privacy: <strong>ε=${n.privacy_budget_eps}</strong></span>
            </div>
        </div>
    `).join('');
}

async function triggerFederatedRound() {
    const btn = document.getElementById('btnTriggerFedRound');
    if (btn) {
        btn.innerHTML = `<span class="inline-block animate-spin mr-1">⚙️</span> Aggregating Gradients...`;
        btn.disabled = true;
    }

    try {
        const res = await fetch('/api/federated/train-round', { method: 'POST' });
        const roundData = await res.json();
        showToast('🌐 Federated Round Completed', `Round ${roundData.round_id} aggregated across ${roundData.participating_nodes} BRICS nodes. Loss reduced by ${roundData.loss_reduction_pct}%.`, 'success');
        await loadFederatedData();
    } catch (e) {
        showToast('Error', 'Failed to run federated training round.', 'error');
    } finally {
        if (btn) {
            btn.innerHTML = `<span>⚡ Execute FedAvg Round</span>`;
            btn.disabled = false;
        }
    }
}
window.triggerFederatedRound = triggerFederatedRound;

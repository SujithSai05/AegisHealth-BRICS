/**
 * Emergency Crisis Simulation Sandbox triggers and toast notifications
 */

async function triggerOutbreakScenario(scenarioId) {
    try {
        const btn = document.getElementById(`btn-scenario-${scenarioId}`);
        if (btn) {
            btn.innerHTML = `<span class="inline-block animate-spin mr-1">⚙️</span> Simulating...`;
            btn.disabled = true;
        }

        const res = await fetch('/api/simulation/trigger', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: scenarioId, intensity: 1.2 })
        });
        const data = await res.json();

        if (scenarioId === 'reset') {
            showToast('✅ System Baseline Restored', 'All facility inventories, bed occupancy, and alerts have been reset to normal baseline.', 'success');
        } else {
            showToast(`🚨 Simulation Active: ${data.title}`, data.impact_summary, 'warning');
        }

        // Refresh entire application state
        if (window.refreshAllDashboardData) {
            await window.refreshAllDashboardData();
        }

    } catch (err) {
        console.error('Failed to trigger scenario:', err);
        showToast('Error', 'Failed to communicate with simulation engine.', 'error');
    } finally {
        const btn = document.getElementById(`btn-scenario-${scenarioId}`);
        if (btn) {
            btn.innerHTML = btn.getAttribute('data-original-text') || 'Trigger Scenario';
            btn.disabled = false;
        }
    }
}

function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    const borderCol = type === 'warning' ? 'border-amber-500' : (type === 'success' ? 'border-emerald-500' : (type === 'error' ? 'border-rose-500' : 'border-cyan-500'));
    const bgCol = 'bg-gray-900/95';

    toast.className = `p-4 mb-3 rounded-lg border-l-4 ${borderCol} ${bgCol} text-gray-100 shadow-2xl backdrop-blur-md transition-all duration-300 transform translate-x-full max-w-md`;
    toast.innerHTML = `
        <div class="flex items-start justify-between">
            <div>
                <h4 class="font-bold text-sm text-white">${title}</h4>
                <p class="text-xs text-gray-300 mt-1 leading-relaxed">${message}</p>
            </div>
            <button onclick="this.parentElement.parentElement.remove()" class="text-gray-400 hover:text-white ml-3 text-lg font-bold">&times;</button>
        </div>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-x-full');
        setTimeout(() => toast.remove(), 400);
    }, 6000);
}

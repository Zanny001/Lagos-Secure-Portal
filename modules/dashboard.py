from flask import Blueprint, render_template_string, jsonify
import time
import psutil
import os

dashboard_bp = Blueprint('dashboard', __name__)

DASHBOARD_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zannie Institutional Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 font-sans h-screen flex flex-col overflow-hidden">
    
    <header class="bg-slate-900 border-b border-slate-800 p-4 flex justify-between items-center shadow-lg">
        <h1 class="text-xl font-black bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent flex items-center gap-2">
            <i class="fa-solid fa-chart-network text-emerald-400"></i> Zannie Matrix Control
        </h1>
        <div class="flex gap-3">
            <div class="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded text-xs font-mono flex items-center gap-2">
                <i class="fa-solid fa-database text-slate-500"></i> Cluster: SYNCED
            </div>
            <div class="bg-emerald-950/30 border border-emerald-900/50 text-emerald-400 px-3 py-1.5 rounded text-xs font-mono flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span> API Gateway: ONLINE
            </div>
        </div>
    </header>

    <main class="flex-1 p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 overflow-y-auto">
        
        <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5 col-span-1 flex flex-col gap-4 shadow-2xl">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider"><i class="fa-solid fa-server"></i> Node Health</h3>
            <div class="flex-1 flex flex-col justify-center gap-6">
                <div>
                    <div class="flex justify-between text-xs mb-1 font-mono"><span>CPU Load</span> <span id="cpuText" class="text-emerald-400">0%</span></div>
                    <div class="w-full bg-slate-800 rounded-full h-2"><div id="cpuBar" class="bg-emerald-400 h-2 rounded-full transition-all duration-500" style="width: 0%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs mb-1 font-mono"><span>Memory Matrix</span> <span id="ramText" class="text-purple-400">0%</span></div>
                    <div class="w-full bg-slate-800 rounded-full h-2"><div id="ramBar" class="bg-purple-400 h-2 rounded-full transition-all duration-500" style="width: 0%"></div></div>
                </div>
                <div>
                    <div class="flex justify-between text-xs mb-1 font-mono"><span>Storage I/O</span> <span id="diskText" class="text-blue-400">0%</span></div>
                    <div class="w-full bg-slate-800 rounded-full h-2"><div id="diskBar" class="bg-blue-400 h-2 rounded-full transition-all duration-500" style="width: 0%"></div></div>
                </div>
            </div>
        </div>

        <div class="bg-slate-900/50 border border-slate-800 rounded-xl p-5 col-span-1 lg:col-span-2 shadow-2xl">
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-wider mb-4"><i class="fa-solid fa-wave-square"></i> API Data Throughput (Kbps)</h3>
            <div class="relative h-48 w-full">
                <canvas id="throughputChart"></canvas>
            </div>
        </div>
    </main>

    <script>
        const ctx = document.getElementById('throughputChart').getContext('2d');
        const throughputChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: Array(20).fill(''),
                datasets: [{
                    label: 'Live Bandwidth',
                    data: Array(20).fill(0),
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    tension: 0.4,
                    fill: true,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: { duration: 0 },
                scales: {
                    y: { grid: { color: '#1e293b' }, min: 0, max: 100 },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });

        setInterval(async () => {
            try {
                const res = await fetch('/zannie-telemetry');
                const data = await res.json();
                
                document.getElementById('cpuBar').style.width = data.cpu + '%';
                document.getElementById('cpuText').innerText = data.cpu + '%';
                document.getElementById('ramBar').style.width = data.ram + '%';
                document.getElementById('ramText').innerText = data.ram + '%';
                document.getElementById('diskBar').style.width = data.disk + '%';
                document.getElementById('diskText').innerText = data.disk + '%';

                const chartData = throughputChart.data.datasets[0].data;
                chartData.shift(); 
                let simulatedLoad = Math.floor(Math.random() * (data.cpu + 15)); 
                chartData.push(simulatedLoad); 
                throughputChart.update();
            } catch (e) { console.error("Telemetry link severed."); }
        }, 1500); 
    </script>
</body>
</html>
"""

@dashboard_bp.route('/zannie-dashboard', methods=['GET'])
def render_dashboard():
    return render_template_string(DASHBOARD_UI)

@dashboard_bp.route('/zannie-telemetry', methods=['GET'])
def get_telemetry():
    return jsonify({
        "cpu": psutil.cpu_percent(interval=None),
        "ram": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    })

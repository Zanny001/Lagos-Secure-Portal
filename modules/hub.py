from flask import Blueprint, render_template_string

hub_bp = Blueprint('hub', __name__)

MASTER_INDEX_UI = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Zannie Master Index</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 font-sans min-h-screen p-4 md:p-8">
    <div class="max-w-3xl mx-auto">
        <header class="mb-8 border-b border-slate-800 pb-4">
            <h1 class="text-3xl font-black bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent flex items-center gap-3">
                <i class="fa-solid fa-network-wired text-indigo-400"></i> Zannie Operations Hub
            </h1>
            <p class="text-slate-500 mt-2 text-sm font-mono">Vercel & Render Global Matrix Routing</p>
        </header>

        <div class="space-y-8">
            <section>
                <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4"><i class="fa-solid fa-bolt text-yellow-400 mr-2"></i>Lagos-Secure-Portal (Vercel)</h2>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <a href="/assessment" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500 hover:bg-slate-800 transition-all flex items-center gap-4 group">
                        <div class="bg-indigo-950/50 p-3 rounded-lg text-indigo-400 group-hover:bg-indigo-500 group-hover:text-white transition-colors"><i class="fa-solid fa-graduation-cap"></i></div>
                        <div>
                            <h3 class="font-bold text-slate-200">Academic Assessment</h3>
                            <p class="text-xs text-slate-500">Physics Evaluation Engine</p>
                        </div>
                    </a>
                    
                    <a href="/academic/curriculum/physics/igcse" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500 hover:bg-slate-800 transition-all flex items-center gap-4 group">
                        <div class="bg-purple-950/50 p-3 rounded-lg text-purple-400 group-hover:bg-purple-500 group-hover:text-white transition-colors"><i class="fa-solid fa-brain"></i></div>
                        <div>
                            <h3 class="font-bold text-slate-200">AI Generator</h3>
                            <p class="text-xs text-slate-500">Gemini-Powered Curriculum</p>
                        </div>
                    </a>

                    <a href="/academic/syllabus" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500 hover:bg-slate-800 transition-all flex items-center gap-4 group">
                        <div class="bg-blue-950/50 p-3 rounded-lg text-blue-400 group-hover:bg-blue-500 group-hover:text-white transition-colors"><i class="fa-solid fa-book-open"></i></div>
                        <div>
                            <h3 class="font-bold text-slate-200">Syllabus Browser</h3>
                            <p class="text-xs text-slate-500">Subject Structure & PDFs</p>
                        </div>
                    </a>

                    <a href="/zannie/design-studio" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500 hover:bg-slate-800 transition-all flex items-center gap-4 group">
                        <div class="bg-pink-950/50 p-3 rounded-lg text-pink-400 group-hover:bg-pink-500 group-hover:text-white transition-colors"><i class="fa-solid fa-palette"></i></div>
                        <div>
                            <h3 class="font-bold text-slate-200">Design Studio</h3>
                            <p class="text-xs text-slate-500">Visual Editing Terminal</p>
                        </div>
                    </a>

                    <a href="/dev-admin" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-indigo-500 hover:bg-slate-800 transition-all flex items-center gap-4 group sm:col-span-2">
                        <div class="bg-red-950/50 p-3 rounded-lg text-red-400 group-hover:bg-red-500 group-hover:text-white transition-colors"><i class="fa-solid fa-lock"></i></div>
                        <div>
                            <h3 class="font-bold text-slate-200">Admin Control Panel</h3>
                            <p class="text-xs text-slate-500">Secure DevOps Gateway</p>
                        </div>
                    </a>
                </div>
            </section>

            <section>
                <h2 class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4"><i class="fa-solid fa-server text-emerald-400 mr-2"></i>Zannie Core API (Render)</h2>
                <div class="grid grid-cols-1 gap-4">
                    <a href="https://zannie-core-api-qb75.onrender.com/zannie-dashboard" target="_blank" class="bg-slate-900 border border-slate-800 p-4 rounded-xl hover:border-emerald-500 hover:bg-slate-800 transition-all flex items-center gap-4 group">
                        <div class="bg-emerald-950/50 p-3 rounded-lg text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-colors"><i class="fa-solid fa-chart-line"></i></div>
                        <div class="flex-1">
                            <h3 class="font-bold text-slate-200">Matrix Dashboard</h3>
                            <p class="text-xs text-slate-500">Live Traffic & Node Telemetry</p>
                        </div>
                        <i class="fa-solid fa-arrow-up-right-from-square text-slate-600 group-hover:text-emerald-400"></i>
                    </a>
                </div>
            </section>
        </div>
    </div>
</body>
</html>
"""

@hub_bp.route('/')
def master_index():
    return render_template_string(MASTER_INDEX_UI)

import re

file_path = "/home/userland/Lagos-Secure-Portal/dashboard_index.html"

with open(file_path, "r") as f:
    content = f.read()

live_button_logic = """
        async function triggerPdfCompilation() {
            const btn = document.querySelector('button[onclick="triggerPdfCompilation()"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = "⏳ Compiling...";
            btn.disabled = true;
            
            try {
                const response = await fetch('/api/v1/dashboard/compile_reports', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'success') {
                    alert("✅ " + result.message);
                } else {
                    alert("❌ Error: " + result.message);
                }
            } catch (error) {
                alert("❌ Critical failure reaching the compiler endpoint.");
                console.error(error);
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        }
"""

# Replace the old placeholder function with the live async logic
content = re.sub(r'async function triggerPdfCompilation\(\) \{.*?\}(?=\n\n|\n\s+/\/)', live_button_logic.strip(), content, flags=re.DOTALL)

with open(file_path, "w") as f:
    f.write(content)

print("Dashboard UI successfully wired to the backend compiler.")

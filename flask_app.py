import pickle
import re
import random
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
with open("password_strength_svm.pkl", "rb") as f:
    MODEL = pickle.load(f)
with open("password_strength_features.pkl", "rb") as f:
    FEATURES = pickle.load(f)

def characteristics(password):
    return {"length": len(password), "lowercase": sum(c.islower() for c in password), "uppercase": sum(c.isupper() for c in password), "numbers": sum(c.isdigit() for c in password), "special": sum(not c.isalpha() and not c.isdigit() for c in password), "unique": len(set(password))}

def rating(f):
    groups = sum(bool(f[k]) for k in ("lowercase", "uppercase", "numbers", "special"))
    return min(10, 1 + int(f["length"] >= 8) + int(f["length"] >= 12) + int(f["length"] >= 16) + groups + int(f["unique"] >= max(6, f["length"] * 0.65)))

def rating_band(score):
    if score <= 3: return "Weak"
    if score <= 5: return "Below average"
    if score <= 7: return "Medium"
    if score <= 9: return "Strong"
    return "Very strong"

def insight(password):
    if re.search(r"(.)\1\1", password):
        return "This contains repeated characters; adding more variety would make it less predictable."
    return "This looks like a varied password pattern with a good mix of characters."

def suggestions(f):
    items = []
    if f["length"] < 12: items.append("Make it at least 12 characters long.")
    if not f["uppercase"]: items.append("Add an uppercase letter.")
    if not f["lowercase"]: items.append("Add a lowercase letter.")
    if not f["numbers"]: items.append("Add a number.")
    if not f["special"]: items.append("Add a special character such as ! or #.")
    return items or ["Great balance. Consider using a memorable passphrase unique to this account."]

def suggested_passwords(password, f):
    base = password or "your phrase"
    suffixes = ["Aa7!CedarOrbit", "Qm4#RiverStone", "Zx8@NovaField", "Lp6$OrbitCedar", "Mn3%QuartzLake", "Rv9&PixelGarden", "Tb5^CloudHarbor", "Ks8*MapleComet"]
    first, second_suffix = random.sample(suffixes, 2)
    first += str(random.randint(10, 99))
    second_suffix += str(random.randint(10, 99))
    improved = base + first
    while rating(characteristics(improved)) < 9:
        improved += "Zx#5Qm"
    second = base + second_suffix
    while rating(characteristics(second)) < 9:
        second += "-Next9"
    return [improved, second]

@app.get("/")
def home():
    html = render_template("landing.html")
    html = html.replace('Improve your confidence.', 'Improve your confidentiality.')
    html = html.replace('<a href="/check">Check a password</a>', '<button class="theme-btn" id="landingTheme">☼ Light mode</button>')
    html = html.replace('<h2>What is a strong password?</h2>', '<h2>How to make a strong password</h2>')
    html = html.replace('</section><div class="check">', '<div class="recipe"><div><span>Length</span><strong>12+ characters</strong><small>More characters create more possible combinations.</small><i style="width:88%"></i></div><div><span>Variety</span><strong>3–4 character types</strong><small>Mix letters, numbers, and symbols to avoid predictable patterns.</small><i style="width:76%"></i></div><div><span>Uniqueness</span><strong>Personal and unused</strong><small>Avoid names, common words, repeated sequences, and reuse.</small><i style="width:94%"></i></div></div></section><div class="check">')
    html = html.replace('<div class="check">', '<section class="example"><div><div class="eyebrow">LEARN BY EXAMPLE</div><h2>A weak password can look convenient—but it creates risk.</h2><p><code>password</code> is short, common, and predictable. It can be improved by adding length, variety, and a pattern that is unique to you.</p></div><div class="flow"><div><b>Weak</b><small><code>password</code><br>short + common</small></div><span>→</span><div><b>Medium</b><small><code>password123!</code><br>longer + mixed</small></div><span>→</span><div><b>Strong</b><small><code>Password123!River#</code><br>long + varied + unique</small></div></div></section><div class="check">')
    html = html.replace('</head>', '<style>.theme-btn,.check a{display:inline-flex;align-items:center;justify-content:center;line-height:1;border:1px solid #203650;background:#101e31;color:#edf5ff;border-radius:12px;padding:12px 17px;cursor:pointer;font:600 13px Arial}.explain{max-width:900px}.recipe{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:25px;text-align:left}.recipe div{background:#ffffff08;border:1px solid #203650;border-radius:14px;padding:16px}.recipe span{display:block;color:#5ce1b5;font-size:12px;letter-spacing:.08em;margin-bottom:8px}.recipe strong{display:block;font-size:15px;margin-bottom:6px}.recipe small{display:block;color:#8fa3bb;font-size:12px;line-height:1.45;min-height:52px}.recipe i{display:block;height:7px;border-radius:8px;background:linear-gradient(90deg,#65a7ff,#5ce1b5);margin-top:12px}.example{max-width:900px;margin:24px auto 0;padding:25px;text-align:left;background:#ffffff08;border:1px solid #203650;border-radius:20px}.example h2{font-size:22px;margin:10px 0}.example p{color:#8fa3bb;line-height:1.6}.example code{color:#f28c8c;background:#381d28;padding:4px 8px;border-radius:6px}.flow{display:flex;align-items:center;gap:12px;margin-top:20px}.flow div{flex:1;text-align:center;background:#ffffff08;border:1px solid #203650;border-radius:12px;padding:13px}.flow b{display:block}.flow small{display:block;color:#8fa3bb;font-size:11px;margin-top:6px}.flow span{color:#5ce1b5;font-size:22px}.light-page{background:linear-gradient(135deg,#dce9ef,#cbdde5);color:#0b1d31}.light-page .feature,.light-page .explain,.light-page .example{background:#f5fbff;border-color:#aebfca;box-shadow:0 12px 30px #6c879622}.light-page .theme-btn,.light-page .check a{background:#f5fbff;color:#102033;border-color:#aebfca}.light-page .recipe div,.light-page .flow div{background:#e9f3f5;border-color:#b8ccd5}.light-page .recipe span{color:#168b69}.light-page .recipe small,.light-page .example p,.light-page .flow small{color:#4c687d}.light-page .example code{color:#a42336;background:#ffe5e9}@media(max-width:650px){.recipe{grid-template-columns:1fr}.flow{flex-direction:column}.flow span{transform:rotate(90deg)}}</style></head>')
    html = html.replace('</body>', '<script>(function(){const b=document.body,t=document.getElementById("landingTheme");if(localStorage.getItem("passward-theme")==="light"){b.classList.add("light-page");t.textContent="☾ Dark mode"}t.onclick=function(){b.classList.toggle("light-page");const light=b.classList.contains("light-page");localStorage.setItem("passward-theme",light?"light":"dark");t.textContent=light?"☾ Dark mode":"☼ Light mode"}})()</script></body>')
    html = html.replace('</head>', '<style>.light-page{background:linear-gradient(135deg,#dce9ef,#cbdde5);color:#0b1d31}.light-page .feature{background:#f5fbff;border-color:#aebfca;box-shadow:0 12px 30px #6c879622}.light-page .explain{background:#f5fbff;border-color:#aebfca;box-shadow:0 12px 30px #6c879622}.light-page .hero p,.light-page .feature p,.light-page .explain p{color:#4c687d}.light-page .theme-btn{box-shadow:0 5px 15px #6c879633}</style></head>')
    html = html.replace('</body>', '''<style>.live-bars{display:grid;gap:10px;margin-top:18px}.live-bars div{display:grid;grid-template-columns:125px 1fr;align-items:center;gap:12px;color:var(--muted);font-size:12px}.live-bars i{height:8px;background:#ffffff12;border-radius:8px;overflow:hidden}.live-bars b{display:block;height:100%;background:var(--bar-color,#d09a20);border-radius:8px;transition:width .35s ease,background .25s ease}</style><script>(function(){const stats=document.getElementById('stats');if(!stats||document.getElementById('liveBars'))return;const bars=document.createElement('div');bars.id='liveBars';bars.className='live-bars';stats.after(bars);const input=document.getElementById('password');input.addEventListener('input',async function(){if(!this.value){bars.innerHTML='';return}const d=await(await fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:this.value})})).json();const color=d.label==='Strong'?'#169b72':d.label==='Medium'?'#d09a20':'#d85c67';bars.style.setProperty('--bar-color',color);bars.innerHTML=`<div><span>Length</span><i><b style="width:${Math.min(100,d.features.length/16*100)}%"></b></i></div><div><span>Character variety</span><i><b style="width:${Math.min(100,Object.entries(d.features).slice(1,5).filter(x=>x[1]>0).length/4*100)}%"></b></i></div><div><span>Uniqueness</span><i><b style="width:${Math.min(100,d.features.unique/16*100)}%"></b></i></div>`})})()</script></body>''')
    html = html.replace('</head>', '<style>.flow div:nth-of-type(1) code{background:#5a2430;color:#ff9da8}.flow div:nth-of-type(2) code{background:#66521c;color:#ffe08a}.flow div:nth-of-type(3) code{background:#164d3b;color:#8ff0bd}.flow b{font-size:20px;margin-bottom:8px}.flow small{font-size:13px;line-height:1.8}.flow code{display:inline-block;margin:2px 0 5px;padding:5px 9px}</style></head>')
    return html

@app.get("/check")
def checker_page():
    html = render_template("index.html")
    html = html.replace('<span class="shield">✓</span>', '')
    html = html.replace('<div class="nav-note">Password clarity, in one place</div>', '')
    html = html.replace('</nav>', '<div class="nav-actions"><a class="home-btn" href="/">Home</a><button class="theme-btn" id="themeToggle" type="button">☾ Dark mode</button></div></nav>')
    html = html.replace('</head>', '<style>.brand,.intro h1,.section-title,.result h2{font-family:Trebuchet MS,Arial,sans-serif}.brand{font-size:42px;font-weight:800;letter-spacing:-2px}.intro h1{font-size:clamp(42px,6vw,64px);letter-spacing:-3px}.intro h1 span{background:linear-gradient(90deg,#65a7ff,#5ce1b5);-webkit-background-clip:text;background-clip:text;color:transparent}.card{box-shadow:0 18px 45px #0003;transition:transform .2s,box-shadow .2s}.card:focus-within{box-shadow:0 0 0 3px #65a7ff55,0 18px 45px #0003}.concept{transition:transform .2s,border-color .2s}.concept:hover{transform:translateY(-3px);border-color:#65a7ff}button,input{font:inherit}button:focus-visible,input:focus-visible{outline:3px solid #5ce1b5;outline-offset:3px}@media(max-width:680px){.brand{font-size:32px}.main{padding-left:20px;padding-right:20px}}@media(prefers-reduced-motion:reduce){*,*:before,*:after{scroll-behavior:auto!important;transition:none!important;animation:none!important}}</style></head>')
    html = html.replace('</head>', '<style>.nav-actions{display:flex;align-items:center;gap:10px}.home-btn{display:inline-flex;align-items:center;justify-content:center;text-decoration:none;border:1px solid #cbdbe3;background:#fff;color:#102033;border-radius:12px;padding:11px 15px;font:600 13px Arial}.dark-mode .home-btn{background:#101e31;color:#edf5ff;border-color:#203650}body{background:linear-gradient(135deg,#f7fbff,#eaf4f6);color:#102033}.brand{font-family:Arial,sans-serif;font-size:64px;font-weight:700;letter-spacing:-2px;color:#102033}.brand span,.hero h1 span{color:#169b72;background:none}.hero{padding-top:42px}.hero-stat{display:none!important}.section-head span{display:none!important}.panel,.card{background:#ffffffcc;border-color:#d5e2e8;box-shadow:0 18px 45px #31556b18}.input{background:#f4f8fa;border-color:#cbdbe3}.input input{color:#102033}.concept,.how{background:#ffffffaa;border-color:#d5e2e8}.stat{background:#edf6f4;border-color:#d5e2e8}.nav-note,.hero p,.how p,.concept p,.result p{color:#60788a}.theme-btn{border:1px solid #cbdbe3;background:#fff;color:#102033;border-radius:12px;padding:11px 15px;cursor:pointer;font:600 13px Arial}.dark-mode{background:#07111f;color:#edf5ff}.dark-mode .brand{color:#edf5ff}.dark-mode .brand span{color:#5ce1b5}.dark-mode .panel,.dark-mode .card{background:#101e31;border-color:#203650}.dark-mode .input{background:#0b1726;border-color:#203650}.dark-mode .input input{color:#edf5ff}.dark-mode .concept,.dark-mode .how,.dark-mode .stat{background:#13253b;border-color:#203650}.dark-mode .theme-btn{background:#101e31;color:#edf5ff;border-color:#203650}</style></head>')
    html = html.replace('</body>', '<script>(function(){const b=document.body,t=document.getElementById("themeToggle"),theme=localStorage.getItem("passward-theme");if(theme!=="light"){b.classList.add("dark-mode");t.textContent="☀ Light mode"}else{t.textContent="☾ Dark mode"}t.onclick=function(){b.classList.toggle("dark-mode");const dark=b.classList.contains("dark-mode");localStorage.setItem("passward-theme",dark?"dark":"light");t.textContent=dark?"☀ Light mode":"☾ Dark mode"}})()</script></body>')
    html = html.replace("suggestions.innerHTML='<b>Suggestions</b>'+d.suggestions.map(x=>`<p>• ${x}</p>`).join('')", "suggestions.innerHTML='<b>Suggestions</b>'+d.suggestions.map(x=>`<p>• ${x}</p>`).join('')+'<b>Fictional examples</b>'+d.suggested_passwords.map(x=>`<p><code>${x}</code></p>`).join('')")
    html = html.replace('</head>', '<style>.suggestions code{display:inline-block;margin-top:5px;padding:6px 9px;border-radius:7px;background:#e8f7ee;color:#16734f;font-family:monospace}.dark-mode .suggestions code{background:#173b31;color:#8ff0bd}</style></head>')
    html = html.replace('<div id="stats" class="stats"></div>', '<div id="stats" class="stats"></div><div id="liveBars" class="live-bars"></div>')
    html = html.replace('</head>', '<style>.live-bars{display:grid;gap:9px;margin-top:18px}.live-bars div{display:grid;grid-template-columns:110px 1fr;align-items:center;gap:10px;color:#60788a;font-size:12px}.live-bars i{height:7px;background:#dce8ee;border-radius:8px;overflow:hidden}.live-bars i b{display:block;height:100%;background:var(--bar-color,#d09a20);border-radius:8px}</style></head>')
    html = html.replace("p.oninput=async()=>{", "let checkRequest=0;p.oninput=async()=>{const requestId=++checkRequest;")
    html = html.replace("})).json();r.className='result';", "})).json();if(requestId!==checkRequest||p.value.length!==d.input_length)return;r.className='result';")
    html = html.replace("stats.innerHTML=Object.entries(d.features).map(x=>`<div class=\"stat\"><b>${x[1]}</b><span>${n[x[0]]}</span></div>`).join('');suggestions.innerHTML", "stats.innerHTML=Object.entries(d.features).map(x=>`<div class=\"stat\"><b>${x[1]}</b><span>${n[x[0]]}</span></div>`).join('');liveBars.innerHTML=`<div><span>Length</span><i><b style=\"width:${Math.min(100,d.features.length/16*100)}%\"></b></i></div><div><span>Character variety</span><i><b style=\"width:${Math.min(100,Object.entries(d.features).slice(1,5).filter(x=>x[1]>0).length/4*100)}%\"></b></i></div><div><span>Uniqueness</span><i><b style=\"width:${Math.min(100,d.features.unique/16*100)}%\"></b></i></div>`;suggestions.innerHTML")
    html = html.replace("OUT OF 5", "OUT OF 10").replace("d.rating+'/5'", "d.rating+'/10'").replace("d.rating*20+'%'", "d.rating*10+'%'").replace("meterText.textContent=d.rating+'/10'", "meterText.textContent=d.rating+'/10 · '+d.rating_band")
    html = html.replace('</body>', '<script>document.getElementById("password").addEventListener("paste",function(){setTimeout(()=>this.dispatchEvent(new Event("input")),80)})</script></body>')
    html = html.replace('</body>', '''<script>(function(){const input=document.getElementById('password'),stats=document.getElementById('stats');if(!input||!stats)return;let bars=document.getElementById('liveBars');if(!bars){bars=document.createElement('div');bars.id='liveBars';bars.className='live-bars';stats.after(bars)}input.addEventListener('input',async function(){if(!this.value){bars.innerHTML='';return}const d=await(await fetch('/api/check',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({password:this.value})})).json();const color=d.label==='Strong'?'#169b72':d.label==='Medium'?'#d09a20':'#d85c67';bars.style.setProperty('--bar-color',color);bars.innerHTML=`<div><span>Length</span><i><b style="width:${Math.min(100,d.features.length/16*100)}%"></b></i></div><div><span>Character variety</span><i><b style="width:${Math.min(100,Object.entries(d.features).slice(1,5).filter(x=>x[1]>0).length/4*100)}%"></b></i></div><div><span>Uniqueness</span><i><b style="width:${Math.min(100,d.features.unique/16*100)}%"></b></i></div>`})})()</script></body>''')
    return html

@app.post("/api/check")
def check():
    payload = request.get_json(silent=True) or {}
    password = payload.get("password", "")
    f = characteristics(password)
    prediction = str(MODEL.predict(FEATURES.transform([password]))[0]).lower()
    label = {"0": "Weak", "1": "Medium", "2": "Strong", "weak": "Weak", "normal": "Medium", "medium": "Medium", "strong": "Strong"}.get(prediction, prediction.title())
    display_rating = max(rating(f), 8) if label == "Strong" else rating(f)
    label = rating_band(display_rating)
    return jsonify({"label": label, "rating": display_rating, "rating_band": rating_band(display_rating), "input_length": len(password), "features": f, "insight": insight(password), "suggestions": suggestions(f), "suggested_passwords": suggested_passwords(password, f)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

import io
import os
from flask import Flask, request, jsonify, send_file, render_template_string, session, redirect, url_for

app = Flask(__name__)
# مفتاح أمان قوي لتشفير الجلسات وحماية الحسابات أونلاين
app.secret_key = os.environ.get("SECRET_KEY", "pro_immo_ecu_secure_key_2026_secret")
USERS_DB = {
    "free": {"password": "1234", "role": "admin"},
    "admin1": {"password": "9999", "role": "admin"},
    "admin3": {"password": "admin3password", "role": "admin"},
    "user1": {"password": "user1password", "role": "user"},
    "user2": {"password": "user2password", "role": "user"}
}
LOGIN_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تتسجيل الدخول | ImmoEcu Pro v1.0</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .login-box { background: rgba(27, 46, 75, 0.65); width: 100%; max-width: 420px; padding: 40px; border-radius: 16px; box-shadow: 0px 15px 40px rgba(0,0,0,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); box-sizing: border-box; text-align: center; }
        h2 { color: #00b8ff; font-size: 26px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 184, 255, 0.4); margin-bottom: 5px; margin-top: 0; }
        p { color: #888ea8; font-size: 13px; margin-bottom: 30px; }
        .input-group { text-align: right; margin-bottom: 20px; }
        .input-group label { display: block; color: #bfc9d4; font-size: 12px; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; }
        .input-group input { width: 100%; padding: 14px; border-radius: 8px; background: #060b19; color: #fff; border: 1px solid #3b3f5c; box-sizing: border-box; font-size: 15px; outline: none; transition: 0.3s; }
        .input-group input:focus { border-color: #00b8ff; box-shadow: 0 0 10px rgba(0, 184, 255, 0.2); }
        .btn-login { width: 100%; padding: 14px; border-radius: 8px; background: linear-gradient(135deg, #00b8ff 0%, #0077ff 100%); color: #060b19; font-weight: bold; border: none; cursor: pointer; transition: 0.3s; font-size: 16px; margin-top: 10px; }
        .btn-login:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,184,255,0.4); }
        .err-msg { background: rgba(255, 51, 51, 0.15); border: 1px solid #ff3333; color: #ff3333; padding: 12px; border-radius: 8px; font-size: 13px; font-weight: bold; margin-bottom: 20px; text-align: center; }
    </style>
</head>
"""
LOGIN_TEMPLATE += r"""
<body>
    <div class="login-box">
        <h2>💻 ImmoEcu Pro v1.0</h2>
        <p>المنصة الاحترافية لهندسة برمجيات عقول السيارات</p>
        {% if error %}
        <div class="err-msg">❌ {{ error }}</div>
        {% endif %}
        <form method="POST" action="/login">
            <div class="input-group">
                <label>👤 اسم المستخدم (Username):</label>
                <input type="text" name="username" placeholder="Enter username..." required>
            </div>
            <div class="input-group">
                <label>🔑 كلمة المرور (Password):</label>
                <input type="password" name="password" placeholder="Enter password..." required>
            </div>
            <button type="submit" class="btn-login">تسجيل الدخول الآمن 🚀</button>
        </form>
    </div>
</body>
</html>
"""
LANDING_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImmoEcu Pro v1.0 | المنصة الاحترافية لهندسة برمجيات السيارات</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #fff; margin: 0; padding: 0; text-align: center; }
        .hero { padding: 80px 20px; background: rgba(27, 46, 75, 0.2); border-bottom: 1px solid rgba(0, 184, 255, 0.1); backdrop-filter: blur(8px); }
        h1 { color: #00b8ff; font-size: 38px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 184, 255, 0.4); margin-bottom: 10px; }
        .subtitle { color: #00e676; font-size: 18px; font-weight: bold; margin-bottom: 30px; }
        .btn-enter { display: inline-block; background: linear-gradient(135deg, #00b8ff 0%, #0077ff 100%); color: #060b19; font-weight: bold; padding: 16px 40px; border-radius: 8px; text-decoration: none; font-size: 18px; transition: 0.3s; box-shadow: 0 5px 15px rgba(0,184,255,0.3); }
        .btn-enter:hover { transform: translateY(-3px); box-shadow: 0 8px 25px rgba(0,184,255,0.5); }
        .container { max-width: 900px; margin: 50px auto; padding: 0 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 30px; }
        .card { background: rgba(27, 46, 75, 0.4); border: 1px solid rgba(0, 184, 255, 0.15); padding: 25px; border-radius: 12px; backdrop-filter: blur(10px); text-align: right; }
        .card h3 { color: #00b8ff; margin-top: 0; font-size: 18px; border-bottom: 1px solid rgba(38, 59, 94, 0.5); padding-bottom: 10px; }
        .card p { color: #bfc9d4; font-size: 14px; line-height: 1.6; margin-bottom: 0; }
        .badge { background: rgba(0, 230, 118, 0.1); color: #00e676; padding: 2px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; float: left; }
        footer { margin-top: 100px; padding: 20px; color: #515365; font-size: 12px; border-top: 1px solid rgba(38, 59, 94, 0.3); }
    </style>
</head>
<body>

    <div class="hero">
        <h1>💻 ImmoEcu Pro v1.0</h1>
        <div class="subtitle">🚀 المنصة الفورية الأسرع لعمل IMMO OFF وقراءة الـ PIN Code أونلاين</div>
        <p style="color: #888ea8; max-width: 600px; margin: 0 auto 40px auto; font-size: 15px; line-height: 1.6;">
            منصة ويب متكاملة مصممة خصيصاً لفنيي ومبرمجي عقول السيارات لإصلاح وتعديل ملفات الدامب (Dumps) بأمان تام وبدون أي زحزحة للبايتات.
        </p>
        <a href="/login" class="btn-enter">دخول المنصة وابدأ المعالجة الآن 🚀</a>
    </div>

    <div class="container">
        <h2>🛠️ أنواع وحدات التحكم (ECU) المدعومة في السيرفر حالياً:</h2>
        
        <div class="grid">
            <div class="card">
                <h3>🚗 عائلة بوش (Bosch) <span class="badge">إصلاح حقيقي</span></h3>
                <p>• <b>EDC15C2</b> (EEPROM + FLASH) <br>• <b>EDC16C34 / EDC16C3</b> (PSA)<br>• <b>EDC16C34 / EDC16C39</b> (Fiat)<br>• <b>ME7.4.4 / ME7.4.5</b> (Peugeot/Citroën)</p>
            </div>
            
            <div class="card">
                <h3>⚙️ عائلة فاليو (Valeo) <span class="badge">تعديل آمن</span></h3>
                <p>• <b>Valeo V34</b> (EEPROM 4KB)<br>• <b>Valeo J34P</b> (EEPROM 2KB)<br>• <b>Valeo V46.11</b> (EEPROM 16KB)</p>
            </div>
            
            <div class="card">
                <h3>🤖 سيمنز وماريلي ودلفي <span class="badge">ديناميكي</span></h3>
                <p>• <b>Siemens SID801 / SID801A / SID807EVO</b><br>• <b>Marelli 4MP2 / 48P2</b> (بالبحث عن التوقيع)<br>• <b>Delphi DCM3.4 / DCM3.5</b> (EEPROM 8KB)</p>
            </div>
        </div>

        <div class="card" style="margin-top: 40px; text-align: center; background: rgba(0, 230, 118, 0.05); border-color: rgba(0, 230, 118, 0.2);">
            <h3 style="color: #00e676;">🎁 تجربة مجانية مفتوحة مؤقتاً لفنيي السيارات</h3>
            <p style="color: #e0e6ed;">يمكنك استخدام المنصة وتجربتها مجاناً فوراً! اضغط على دخول المنصة واستخدم الحساب التجريبي المفتوح للجميع: <br>
            <span style="display: inline-block; background: #060b19; padding: 8px 15px; border-radius: 6px; margin-top: 10px; font-family: monospace;">اسم المستخدم: <b>free</b> | كلمة المرور: <b>1234</b></span>
            </p>
        </div>
    </div>

    <footer>
        جميع الحقوق محفوظة © ImmoEcu Pro 2026 - هندسة برمجيات عقول السيارات
    </footer>

</body>
</html>
"""
IMMO_TEMPLATE = r"""
<!DOCTYPE html>
<html lang="en" dir="ltr" id="html-tag">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImmoEcu Pro v1.0</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #e0e6ed; padding: 40px 20px; text-align: left; margin: 0; min-height: 100vh; }
        html[dir="rtl"] body { text-align: right; }
        .box { background: rgba(27, 46, 75, 0.65); max-width: 600px; margin: auto; padding: 30px; border-radius: 16px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); box-sizing: border-box; }
        .nav-btn { background: #3b3f5c; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold; display: inline-block; float: right; }
        html[dir="rtl"] .nav-btn { float: left; }
        .nav-btn:hover { background: #ff3333; color: white; }
        h1 { color: #00b8ff; text-align: center; font-size: 28px; margin-top: 10px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 184, 255, 0.4); }
        p { color: #00e676; font-size: 14px; text-align: center; font-weight: bold; margin-bottom: 30px; }
        label { display: block; margin-top: 20px; color: #888ea8; font-weight: 600; font-size: 14px; text-transform: uppercase; }
        select, button { width: 100%; padding: 14px; margin: 8px 0; border-radius: 8px; background: #060b19; color: #fff; border: 1px solid #3b3f5c; box-sizing: border-box; font-size: 15px; outline: none; }
        select:focus { border-color: #00b8ff; }
        .custom-file-upload { display: block; text-align: center; cursor: pointer; border: 2px dashed #00b8ff; color: #00b8ff; width: 100%; padding: 16px; margin: 8px 0; border-radius: 8px; background: rgba(0, 184, 255, 0.05); font-weight: bold; font-size: 15px; box-sizing: border-box; }
        .custom-file-upload:hover { background: rgba(0, 184, 255, 0.15); }
        button { background: linear-gradient(135deg, #00e676 0%, #00c853 100%); color: #060b19; font-weight: bold; border: none; cursor: pointer; transition: 0.3s; margin-top: 15px; }
        button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,230,118,0.4); }
        #msg-box { padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; text-align: center; font-size: 14px; }
        .msg-success { background: rgba(0, 230, 118, 0.15); border: 1px solid #00e676; color: #00e676; }
        .msg-error { background: rgba(255, 51, 51, 0.15); border: 1px solid #ff3333; color: #ff3333; }
        .lang { margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
        .lang select { width: auto; padding: 4px; margin: 0; font-size: 12px; }
        .user-badge { font-size: 12px; color: #00b8ff; font-weight: bold; background: rgba(0, 184, 255, 0.1); padding: 4px 8px; border-radius: 4px; display: inline-block; margin-bottom: 15px; }
    </style>
</head>
"""
IMMO_TEMPLATE += r"""
<body>
    <div class="box">
        <div class="lang">
            <a href="/logout" id="nav-main-btn" class="nav-btn">🔒 Logout</a>
            <span id="l-lbl">🌐 Lang:</span>
            <select id="lSel" onchange="chgL(this.value)">
                <option value="en" selected>English</option>
                <option value="ar">العربية</option>
                <option value="fr">Français</option>
            </select>
        </div>
        <h1 id="m-title">💻 ImmoEcu Pro v1.0</h1><p id="m-sub">🔧 Multi-Brand Multi-PIN Solutions</p>
        <div class="user-badge">👤 الحساب الحالي: {{ session['username'] }} ({{ session['role'] }})</div>
        <div id="msg-box" style="display:none;"></div>
        <form id="ecuForm" onsubmit="submitForm(event)">
            <label id="l-file">📂 Choose File to Process:</label>
            <label for="dump_file" id="file-btn-text" class="custom-file-upload">📁 Choose File...</label>
            <input type="file" id="dump_file" name="dump_file" style="display: none;" onchange="updateFileName(this)" required>
            <label id="l-brand">🚗 Select Brand / Company:</label>
            <select id="brand_filter" onchange="filterEcus()"></select>
            <label id="l-make">⚙️ Select ECU Maker:</label>
            <select id="make_filter" onchange="filterEcus()"></select>
            <label id="l-ecu">🤖 Select ECU Type:</label><select name="ecu_type" id="ecu_type" onchange="checkOperationState()"></select>
            <label id="l-op">⚡ Operation:</label>
            <select name="operation" id="operation"><option value="immo_off" id="o-off">IMMO OFF</option><option value="read_pin" id="o-pin">Read PIN</option><option value="immo_virgin" id="o-vir">IMMO VIRGIN (سيتوفر قريباً)</option></select>
            <button type="submit" id="b-sub">Process File 🚀</button>
        </form>
    </div>
"""
IMMO_TEMPLATE += r"""
    <script>
        const rawDatabase = {
            "edc16c34_psa": {brand:"PSA", make:"Bosch", name:"Bosch EDC16C34 (EEPROM 2KB)"},
            "edc16c3": {brand:"PSA", make:"Bosch", name:"Bosch EDC16C3 (EEPROM 2KB)"},
            "me744_psa": {brand:"PSA", make:"Bosch", name:"Bosch ME7.4.4 (EEPROM 2KB)"},
            "me745_psa": {brand:"PSA", make:"Bosch", name:"Bosch ME7.4.5 (EEPROM 4KB)"},
            "edc15c2_psa_eeprom": {brand:"PSA", make:"Bosch", name:"Bosch EDC15C2 (EEPROM 1KB)"},
            "edc15c2_psa_flash": {brand:"PSA", make:"Bosch", name:"Bosch EDC15C2 (FLASH 512KB)"},
            "edc16c39_fiat": {brand:"FIAT", make:"Bosch", name:"Bosch EDC16C39 (FLASH 2MB)"},
            "edc16c34_nemo_fiat": {brand:"FIAT", make:"Bosch", name:"Bosch EDC16C34 (FLASH 2MB) - Nemo/Fiat"},
            "sid801_801a_psa": {brand:"PSA", make:"Siemens", name:"Siemens SID801 / SID801A (256B)"},
            "sirius81_eeprom": {brand:"PSA", make:"Siemens", name:"Continental Sirius 81 (256B)"},
            "sid807evo_psa": {brand:"PSA", make:"Siemens", name:"Continental SID807EVO"},
            "sid801_25dt_ct": {brand:"PSA", make:"Siemens", name:"Siemens SID801 25DT/CT (256B)"},
            "valeo_v4611_psa": {brand:"PSA", make:"Valeo", name:"Valeo V46.11 (EEPROM 16KB)"},
            "valeo_v34_psa": {brand:"PSA", make:"Valeo", name:"Valeo V34 (EEPROM 4KB)"},
            "valeo_j34p_psa": {brand:"PSA", make:"Valeo", name:"Valeo J34P (EEPROM 2KB)"},
            "marelli_4mp2_psa": {brand:"PSA", make:"Marelli", name:"Magneti Marelli 4MP2 (FLASH 256KB)"},
            "marelli_48p2_psa": {brand:"PSA", make:"Marelli", name:"Marelli IAW 48P2 (FLASH 512KB)"},
            "dcm34_psa": {brand:"PSA", make:"Delphi", name:"Delphi DCM3.4 (EEPROM 4KB)"},
            "dcm35_psa": {brand:"PSA", make:"Delphi", name:"Delphi DCM3.5 (EEPROM 8KB)"}
        };
"""
IMMO_TEMPLATE += r"""
        const locales = {
            "en": { "success_mod": "✅ File Modified Successfully!", "success_pin": "🔑 PIN Extracted: " },
            "ar": { "success_mod": "✅ تم تعديل وحفظ الملف بنجاح!", "success_pin": "🔑 تم استخراج البين كود بنجاح: " },
            "fr": { "success_mod": "✅ Fichier modifié avec succès!", "success_pin": "🔑 PIN Extrait: " }
        };
        function filterEcus() {
            let bFil = document.getElementById('brand_filter').value; let mFil = document.getElementById('make_filter').value;
            let select = document.getElementById('ecu_type'); select.innerHTML = "";
            let lang = document.getElementById('lSel').value;
            for (let key in rawDatabase) {
                let item = rawDatabase[key];
                if ((bFil === "ALL" || item.brand === bFil) && (mFil === "ALL" || item.make === mFil)) {
                    let opt = document.createElement('option'); opt.value = key;
                    opt.innerText = (lang === "ar" && item.name_ar) ? item.name_ar : item.name;
                    select.appendChild(opt);
                }
            }
            checkOperationState();
        }
"""
IMMO_TEMPLATE += r"""
        function checkOperationState() {
            let ecu = document.getElementById('ecu_type').value;
            let pinOpt = document.getElementById('o-pin');
            let virginOpt = document.getElementById('o-vir');
            let opSelect = document.getElementById('operation');
            let lang = document.getElementById('lSel').value;
            virginOpt.disabled = true;
            virginOpt.style.color = "#515365";
            virginOpt.innerText = lang === "ar" ? "إعادة التهيئة IMMO VIRGIN (سيتوفر قريباً)" : (lang === "fr" ? "IMMO VIRGIN (Bientôt)" : "IMMO VIRGIN (Soon)");
            if (ecu === "edc16c34_nemo_fiat" || ecu === "edc15c2_psa_flash" || ecu === "edc16c39_fiat" || ecu === "sid801_25dt_ct") {
                pinOpt.disabled = true; pinOpt.style.color = "#515365";
                if (opSelect.value === "read_pin" || opSelect.value === "immo_virgin") opSelect.value = "immo_off";
            } else { pinOpt.disabled = false; pinOpt.style.color = ""; }
        }
"""
IMMO_TEMPLATE += r"""
        function chgL(lang) {
            localStorage.setItem('lang', lang); document.getElementById('html-tag').setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
            let trans = {
                "en": {"m-title": "💻 ImmoEcu Pro v1.0", "m-sub": "🔧 Solutions", "l-lbl": "🌐 Lang:", "l-file": "📂 Select File:", "l-brand": "🚗 Select Brand:", "l-make": "⚙️ Select Maker:", "l-ecu": "🤖 Select ECU:", "l-op": "⚡ Operation:", "o-off": "IMMO OFF", "o-pin": "Read PIN", "b-sub": "Process File 🚀", "nav-main-btn": "🔒 Logout"},
                "ar": {"m-title": "💻 ImmoEcu Pro v1.0", "m-sub": "🔧 حلول احترافية وتصحيح حقيقي", "l-lbl": "🌐 اللغة:", "l-file": "📂 اختر ملف العقل:", "l-brand": "🚗 اختر شركة السيارة:", "l-make": "⚙️ اختر صانع العقل:", "l-ecu": "🤖 نوع وحدة التحكم:", "l-op": "⚡ العملية:", "o-off": "إلغاء الحماية IMMO OFF", "o-pin": "قراءة البين كود Read PIN", "b-sub": "معالجة الملف الآن 🚀", "nav-main-btn": "🔒 تسجيل الخروج"},
                "fr": {"m-title": "💻 ImmoEcu Pro v1.0", "m-sub": "🔧 Solutions Pro", "l-lbl": "🌐 Langue:", "l-file": "📂 Fichier:", "l-brand": "🚗 Marque:", "l-make": "⚙️ Fabricant:", "l-ecu": "🤖 Type ECU:", "l-op": "⚡ Operation:", "o-off": "IMMO OFF", "o-pin": "Lire PIN", "b-sub": "Traiter 🚀", "nav-main-btn": "🔒 Logout"}
            };
            for (let id in trans[lang]) {
                let el = document.getElementById(id); if (el) el.innerText = trans[lang][id];
            }
            let bSelect = document.getElementById('brand_filter'); let mSelect = document.getElementById('make_filter');
            let oldB = bSelect.value; let oldM = mSelect.value;
            if (lang === "ar") {
                bSelect.innerHTML = `<option value="ALL">-- كل الشركات --</option><option value="PSA">PSA (بيجو / سيتروين)</option><option value="FIAT">فيات (FIAT)</option>`;
                mSelect.innerHTML = `<option value="ALL">-- كل المصنعين --</option><option value="Bosch">بوش (Bosch)</option><option value="Siemens">سيمنز (Siemens)</option><option value="Valeo">فاليو (Valeo)</option><option value="Marelli">ماريلي (Marelli)</option><option value="Delphi">دلفي (Delphi)</option>`;
                if(!document.getElementById('dump_file').files.length) document.getElementById('file-btn-text').innerText = "📁 اختر ملف الدامب من الحاسوب...";
            } else {
                bSelect.innerHTML = `<option value="ALL">-- ALL BRANDS --</option><option value="PSA">PSA (Peugeot / Citroën)</option><option value="FIAT">FIAT</option>`;
                mSelect.innerHTML = `<option value="ALL">-- ALL MAKERS --</option><option value="Bosch">Bosch</option><option value="Siemens">Siemens / Continental</option><option value="Valeo">Valeo / Sagem</option><option value="Marelli">Magneti Marelli</option><option value="Delphi">Delphi</option>`;
                if(!document.getElementById('dump_file').files.length) document.getElementById('file-btn-text').innerText = "📁 Choose File...";
            }
            bSelect.value = oldB || "ALL"; mSelect.value = oldM || "ALL"; filterEcus();
        }
"""
IMMO_TEMPLATE += r"""
        function updateFileName(input) {
            let fBtn = document.getElementById('file-btn-text');
            if (input.files && input.files.length > 0) fBtn.innerText = "📄 " + input.files[0].name;
        }
        function submitForm(e) {
            e.preventDefault(); let fileInput = document.getElementById('dump_file');
            if (!fileInput.files || fileInput.files.length === 0) { return; }
            let formData = new FormData(); formData.append('dump_file', fileInput.files[0]);
            formData.append('ecu_type', document.getElementById('ecu_type').value);
            formData.append('operation', document.getElementById('operation').value);
            let lang = document.getElementById('lSel').value; let msgBox = document.getElementById('msg-box');
            msgBox.style.display = "none";
            fetch('/immo_tool', { method: 'POST', body: formData })
            .then(res => {
                const contentType = res.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) return res.json();
                return res.blob().then(b => { 
                    let disp = res.headers.get('Content-Disposition'); let filename = "modified_dump.bin";
                    if (disp && disp.includes('filename=')) { filename = disp.split('filename=')[1].replace(/"/g, ""); }
                    return { download: true, blob: b, filename: filename }; 
                });
            })
            .then(data => {
                msgBox.style.display = "block";
                if (data.download) {
                    msgBox.className = "msg-success"; msgBox.innerText = locales[lang]["success_mod"];
                    let a = document.createElement('a'); a.href = URL.createObjectURL(data.blob); a.download = data.filename; a.click();
                } else {
                    if (data.status === "success_pin") {
                        msgBox.className = "msg-success"; msgBox.innerText = locales[lang]["success_pin"] + data.pin;
                    } else { msgBox.className = "msg-error"; msgBox.innerText = data.status; }
                }
            }).catch(() => { msgBox.style.display = "block"; msgBox.className = "msg-error"; msgBox.innerText = "Error processor!"; });
        }
        window.onload = function() { chgL('en'); };
    </script>
</body>
</html>
"""
def process_ecu_file(ecu_key, file_bytes, operation, original_filename="dump.bin"):
    file_size = len(file_bytes)
    file_bytes = bytearray(file_bytes)
    
    # الإعدادات الافتراضية للنجاح والمعالجة
    server_code = "success_mod"
    extracted_pin = ""
    is_error_css = False
    should_download = True
    base_name, file_ext = os.path.splitext(original_filename)
    filename_out = f"ImmoEcu_{base_name}_OFF{file_ext}"

    # --- عقل Valeo V46.11 PSA (16KB) ---
    if ecu_key == "valeo_v4611_psa":
        if file_size != 16384: return "❌ حجم الملف غير متطابق مع إيبروم Valeo V46.11 (يجب أن يكون 16KB)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            file_bytes[0x08:0x0C] = b"\x11\x11\x11\x11"      # السطر الأول: خانات 08 إلى 0B
            file_bytes[0x12:0x15] = b"\x5C\xDD\x00"          # السطر الثاني: خانات 02 إلى 04
            file_bytes[0x16:0x1A] = b"\x70\x07\x8F\xF8"      # السطر الثاني: خانات 06 إلى 09
            file_bytes[0x108:0x10C] = b"\x11\x11\x11\x11"    # سطر 0100: خانات 08 إلى 0B
            file_bytes[0x112:0x115] = b"\x5C\xDD\x00"        # سطر 0110: خانات 02 إلى 04
            file_bytes[0x116:0x11A] = b"\x70\x07\x8F\xF8"    # سطر 0110: خانات 06 إلى 09
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x08], file_bytes[0x09], file_bytes[0x0A], file_bytes[0x0B]
                c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                extracted_pin = f"{c1}{c2}{c3}{c4}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

    # --- عقل Bosch ME7.4.4 PSA (2KB) ---
    elif ecu_key == "me744_psa":
        if file_size != 2048: return "❌ حجم الملف غير متطابق مع إيبروم ME7.4.4 (يجب أن يكون 2KB)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            file_bytes[0x0590:0x05B0] = (
                b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\x54\xF9"
                b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\x54\xF9"
            )
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                c1, c2, c3, c4 = chr(file_bytes[0x0592]), chr(file_bytes[0x0593]), chr(file_bytes[0x0594]), chr(file_bytes[0x0595])
                extracted_pin = f"{c1}{c2}{c3}{c4}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

    # --- عقل Bosch ME7.4.5 PSA (4KB) ---
    elif ecu_key == "me745_psa":
        if file_size != 4096: return "❌ حجم الملف غير متطابق مع إيبروم ME7.4.5 (يجب أن يكون 4KB)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            file_bytes[0x40:0x80] = (
                b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xBB\xE9"
                b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xBB\xE9"
            )
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                c1, c2, c3, c4 = chr(file_bytes[0x42]), chr(file_bytes[0x43]), chr(file_bytes[0x44]), chr(file_bytes[0x45])
                extracted_pin = f"{c1}{c2}{c3}{c4}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass
    # --- عقل Continental SID807EVO ---
    elif ecu_key == "sid807evo_psa":
        if file_size != 4194304: return "❌ حجم الملف غير متطابق مع فلاش SID807EVO (يجب أن يكون 4096KB)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            file_bytes[0xB00:0xB09] = b"\x11\x11\x11\x11\x07\x70\xFF\xD0\xB4"
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0xB00], file_bytes[0xB01], file_bytes[0xB02], file_bytes[0xB03]
                c4, c3, c2, c1 = chr(b4), chr(b3), chr(b2), chr(b1)
                extracted_pin = f"{c4}{c3}{c2}{c1}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

                   # --- عقل Siemens SID801 25 DT/CT (التصحيح الشامل والمطابق للـ OFF الحقيقي) ---
    elif ecu_key == "sid801_25dt_ct":
        if file_size != 256: return "❌ حجم الملف غير متطابق مع إيبروم SID801 (يجب أن يكون 256 بايت)!", "", True, filename_out, file_bytes, False
        
        # 1. عملية إلغاء الحماية IMMO OFF الصحيحة (الحقن في السطر 00000040)
                # 1. عملية إلغاء الحماية IMMO OFF المعتمدة والصحيحة بدون أي زحزحة للبايتات
        if operation == "immo_off":
            # تصفير أول 10 بايتات من السطر الأول (النطاق 0x0A يغطي 10 بايتات بالتمام والكمال لمنع الإزاحة)
            file_bytes[0x00:0x0A] = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            
            # تصفير 10 بايتات في السطر الخامس ابتداءً من الخانة 04 إلى 0D (موزونة وتتسع لـ 10 بايتات)
            file_bytes[0x44:0x4E] = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
            
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
            
        # 2. عملية قراءة البين كود الحقيقي Read PIN المقابل للأحرف الظاهرة في الهكس
        elif operation == "read_pin":
            try:
                # الكود بين متواجد في نهاية النطاق المظلل بالسطر 0x40 (الخانتين 0C و 0D المقابلة للعناوين 0x4C و 0x4D)
                b1 = file_bytes[0x4C]
                b2 = file_bytes[0x4D]
                
                # ترجمة الخانتين إلى ASCII (بما أنه مكون من خانتين مقروءتين فقط في هذا الدامب)
                c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                
                extracted_pin = f"{c1}{c2}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

    # --- عقل Siemens SID801 / SID801A PSA القياسي (الخوارزمية الأصلية المنفصلة) ---
    elif ecu_key == "sid801_801a_psa":
        if file_size != 256: return "❌ حجم الملف غير متطابق مع إيبروم SID801 (يجب أن يكون 256 بايت)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            # التعديل الأول: من خانة 0A في السطر الأول إلى خانة 01 في السطر الثاني (العناوين من 0x0A إلى 0x11)
            file_bytes[0x0A:0x12] = b"\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F"
            # التعديل الثاني: من خانة 0E في سطر 00000040 إلى خانة 05 في سطر 00000050 (العناوين من 0x4E إلى 0x55)
            file_bytes[0x4E:0x56] = b"\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F"
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x0A], file_bytes[0x0B], file_bytes[0x0C], file_bytes[0x0D]
                c4, c3, c2, c1 = chr(b4), chr(b3), chr(b2), chr(b1)
                extracted_pin = f"{c4}{c3}{c2}{c1}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

        # --- عقل Continental Sirius 81 ---
    elif ecu_key == "sirius81_eeprom":
        if file_size != 256: return "❌ حجم الملف غير متطابق مع إيبروم Sirius 81 (يجب أن يكون 256 بايت)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            file_bytes[0x0A:0x12] = b"\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F"
            file_bytes[0x48:0x50] = b"\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F"
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x0A], file_bytes[0x0B], file_bytes[0x0C], file_bytes[0x0D]
                c4, c3, c2, c1 = chr(b4), chr(b3), chr(b2), chr(b1)
                extracted_pin = f"{c4}{c3}{c2}{c1}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

    # --- عقل Valeo J34P ---
    elif ecu_key == "valeo_j34p_psa":
        if file_size != 2048: return "❌ حجم الملف غير متطابق مع إيبروم Valeo J34P (يجب أن يكون 2KB)!", "", True, filename_out, file_bytes, False
        if operation == "immo_off":
            j34p_patch = b"\xFE\x6C\xFE\x6C\x11\x11\x11\x11\x00\xFF\xE0\x06\xC5\xA0\x00\xFF\x39\x60\x00\x00"
            file_bytes[0x00:0x14] = j34p_patch
            file_bytes[0x70:0x84] = j34p_patch
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x04], file_bytes[0x05], file_bytes[0x06], file_bytes[0x07]
                c3, c4, c2, c1 = chr(b3), chr(b4), chr(b2), chr(b1)
                extracted_pin = f"{c3}{c4}{c2}{c1}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except: pass

        # --- عقل Valeo V34 PSA (4KB) ---
    elif ecu_key == "valeo_v34_psa":
        if file_size != 4096: return "❌ حجم الملف غير متطابق مع إيبروم Valeo V34 (يجب أن يكون 4KB)!", "", True, filename_out, file_bytes, False
        
        # 1. عملية إلغاء الحماية IMMO OFF (الحقن في نهاية السطر الأول ونهاية السطر 0x70)
        if operation == "immo_off":
            # الشفرة المطلوبة المكونة من 4 بايت
            v34_patch = b"\x70\x07\x8F\xF8"
            
            # التعديل الأول: آخر 4 بايتات في السطر الأول (الخانات 0C إلى 0F)
            file_bytes[0x0C:0x10] = v34_patch
            
            # التعديل الثاني: آخر 4 بايتات في سطر 00000070 (الخانات 7C إلى 7F)
            file_bytes[0x7C:0x80] = v34_patch
            
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
            
        # 2. عملية قراءة البين كود من الخانات 04 إلى 07 بترتيب عقل J34P المخصص (3.4.2.1)
        elif operation == "read_pin":
            try:
                # العناوين المقابلة للخانات 04 و 05 و 06 و 07
                b1 = file_bytes[0x04]
                b2 = file_bytes[0x05]
                b3 = file_bytes[0x06]
                b4 = file_bytes[0x07]
                
                # ترجمة الأحرف مع تطبيق الترتيب المخصص لـ J34P (b3 ثم b4 ثم b2 ثم b1)
                c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                
                extracted_pin = f"{c3}{c4}{c2}{c1}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

    # --- عقل Bosch EDC16C39 Fiat ---
    elif ecu_key == "edc16c39_fiat":
        if operation == "immo_off" and file_size >= 0x001C81AF + 1:
            file_bytes[0x001C81AE], file_bytes[0x001C81AF] = 0x00, 0x00
            return "success_mod", "", False, filename_out, bytes(file_bytes), True

        # --- عقل Magneti Marelli 4MP2 PSA (البحث الديناميكي + ترتيب PIN مخصص) ---
    elif ecu_key == "marelli_4mp2_psa":
        target_sig = b"\x96\x48\xA5\xC3"
        
        # 1. عملية إلغاء الحماية IMMO OFF الديناميكية
        if operation == "immo_off":
            marelli_patch = b"\x31\x54\x34\x38\xFF\x7E\x46\x4A\xFF\x7E\xAB\xD6"
            # البحث عن التوقيع في الملف بالكامل خطوة بخطوة (بقفزات 16 بايت لضمان مطابقة السطور)
            for offset in range(0, file_size - 16, 16):
                if file_bytes[offset:offset+4] == target_sig:
                    # تحويل الـ 12 بايت التي تلي التوقيع مباشرة دون لمس التوقيع نفسه
                    file_bytes[offset+4:offset+16] = marelli_patch
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
            
        # 2. عملية قراءة البين كود الحقيقي بعكس الترتيب التناظري (المثال: AUU2 تصبح UA2U)
        elif operation == "read_pin":
            try:
                for offset in range(0, file_size - 16, 16):
                    if file_bytes[offset:offset+4] == target_sig:
                        # جلب أول 4 بايتات تلي التوقيع مباشرة (الخانات 1 و 2 و 3 و 4 بعد التوقيع)
                        b1 = file_bytes[offset+4]
                        b2 = file_bytes[offset+5]
                        b3 = file_bytes[offset+6]
                        b4 = file_bytes[offset+7]
                        
                        # ترجمة البايتات إلى أحرف ASCII
                        c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                        c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                        c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                        c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                        
                        # تطبيق الترتيب المخصص لعكس البنية (b2 ثم b1 ثم b4固 b3) لتتحول AUU2 إلى UA2U
                        extracted_pin = f"{c2}{c1}{c4}{c3}"
                        return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

    # --- عقل Magneti Marelli 48P2 PSA (البحث الديناميكي + التصفير الكامل مخصص) ---
    elif ecu_key == "marelli_48p2_psa":
        target_sig = b"\x96\x48\xA5\xC3"
        
        # 1. عملية إلغاء الحماية IMMO OFF الديناميكية لـ 48P2 (تصفير الـ 12 بايت التي تلي التوقيع)
        if operation == "immo_off":
            marelli_patch = b"\x31\x54\x34\x38\xFF\x7E\x46\x4A\xFF\x7E\xAB\xD6" 
            
            for offset in range(0, file_size - 16, 16):
                if file_bytes[offset:offset+4] == target_sig:
                    file_bytes[offset+4:offset+16] = marelli_patch
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
            
        # 2. عملية قراءة البين كود بنفس خوارزمية الترتيب المعكوس لـ 4MP2
        elif operation == "read_pin":
            try:
                for offset in range(0, file_size - 16, 16):
                    if file_bytes[offset:offset+4] == target_sig:
                        b1, b2, b3, b4 = file_bytes[offset+4], file_bytes[offset+5], file_bytes[offset+6], file_bytes[offset+7]
                        c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                        c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                        c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                        c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                        
                        extracted_pin = f"{c2}{c1}{c4}{c3}"
                        return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

    # --- عقل Bosch EDC15C2 EEPROM ---
    elif ecu_key == "edc15c2_psa_eeprom":
        if operation == "immo_off" and file_size >= 0x204:
            file_bytes[0x14B:0x150] = b"\xFF\x9A\x9A\x9A\x00"
            file_bytes[0x200:0x204] = b"\x00\x00\x00\x00"
            file_bytes[0x216:0x21A] = b"\x00\x00\x00\x00"
            file_bytes[0x22A:0x22E] = b"\x00\x00\x00\x00"
            return "success_mod", "", False, filename_out, bytes(file_bytes), True

    # --- عقل Bosch EDC15C2 FLASH ---
    elif ecu_key == "edc15c2_psa_flash":
        if file_size >= 0x7CCC6:
            if operation == "immo_off":
                file_bytes[0x7CC5A:0x7CCC6] = b"\xFF" * 108
                return "success_mod", "", False, filename_out, bytes(file_bytes), True
            elif operation == "immo_virgin":
                file_bytes[0x7CC5A:0x7CCC6] = b"\x00" * 108
                return "success_mod", "", False, filename_out, bytes(file_bytes), True

        # --- عقل Delphi DCM3.4 PSA (الحقن في السطر 01F0 + قراءة PIN القياسية) ---
    elif ecu_key == "dcm34_psa":
        if file_size != 8192 and file_size != 2048:
            # حماية لفحص الحجم إذا كان إيبروم 2KB أو 8KB حسب دقة القراءة للملف الخاص بك
            pass
            
        # 1. عملية إلغاء الحماية IMMO OFF (الحقن ابتداءً من الخانة 04 في السطر 01F0)
        if operation == "immo_off":
            if file_size >= 0x0200:
                # حقن الـ 12 بايت كاملة في النطاق المحدد تماماً لمنع حدوث أي زحزحة
                file_bytes[0x01F4:0x0200] = b"\x11\x11\x11\x11\x81\x00\x00\x6C\x70\x07\x00\x78"
                return "success_mod", "", False, filename_out, bytes(file_bytes), True
            else:
                return "❌ حجم الملف صغير جداً ولا يحتوي على السطر 000001F0!", "", True, filename_out, file_bytes, False
            
        # 2. عملية قراءة البين كود من نفس الخانات بالترتيب الطبيعي القياسي 1.2.3.4
        elif operation == "read_pin":
            try:
                # قراءة البايتات الأربعة ابتداءً من الخانة 04 في السطر 01F0
                b1 = file_bytes[0x01F4]
                b2 = file_bytes[0x01F5]
                b3 = file_bytes[0x01F6]
                b4 = file_bytes[0x01F7]
                
                # ترجمة البايتات المستخرجة إلى أحرف ASCII المقروءة بالترتيب الطبيعي
                c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                
                extracted_pin = f"{c1}{c2}{c3}{c4}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

                    # --- عقل Delphi DCM3.5 PSA (حجم 8KB - مضبوط ومطابق لبنية DCM3.4 تماماً) ---
    elif ecu_key == "dcm35_psa":
        if file_size != 8192: 
            return "❌ حجم الملف غير متطابق مع إيبروم Delphi DCM3.5 (يجب أن يكون 8KB)!", "", True, filename_out, file_bytes, False
            
        # 1. عملية إلغاء الحماية IMMO OFF (تعديل آخر 14 بايت في السطر 00A0 دون زحزحة)
        if operation == "immo_off":
            # حقن الـ 14 بايت كاملة من الخانة 02 إلى نهاية السطر (العناوين من 0x00A2 إلى 0x00B0)
            file_bytes[0x00A2:0x00B0] = b"\x11\x11\x11\x11\x81\x00\x00\x6C\x70\x07\x00\x78\xB3\x8A"
            return "success_mod", "", False, filename_out, bytes(file_bytes), True
            
        # 2. عملية قراءة البين كود من الخانة 02 إلى 05 بالترتيب الطبيعي المباشر 1234
        elif operation == "read_pin":
            try:
                # قراءة البايتات الأربعة المقابلة للخانات 02، 03، 04، 05 في السطر 00A0
                b1 = file_bytes[0x00A2]
                b2 = file_bytes[0x00A3]
                b3 = file_bytes[0x00A4]
                b4 = file_bytes[0x00A5]
                
                # ترجمة البايتات المستخرجة إلى أحرف ASCII المقروءة بالترتيب الطبيعي المباشر
                c1 = chr(b1) if 32 <= b1 <= 126 else str(b1 if b1 <= 9 else b1 % 10)
                c2 = chr(b2) if 32 <= b2 <= 126 else str(b2 if b2 <= 9 else b2 % 10)
                c3 = chr(b3) if 32 <= b3 <= 126 else str(b3 if b3 <= 9 else b3 % 10)
                c4 = chr(b4) if 32 <= b4 <= 126 else str(b4 if b4 <= 9 else b4 % 10)
                
                extracted_pin = f"{c1}{c2}{c3}{c4}"
                return "success_pin", extracted_pin, False, filename_out, bytes(file_bytes), False
            except:
                pass

    return server_code, extracted_pin, is_error_css, filename_out, bytes(file_bytes), should_download

@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        if "username" in session: return redirect(url_for("immo_tool_page"))
        return render_template_string(LOGIN_TEMPLATE)
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    
    if username in USERS_DB and USERS_DB[username]["password"] == password:
        session["username"] = username
        session["role"] = USERS_DB[username]["role"]
        return redirect(url_for("immo_tool_page"))
    
    return render_template_string(LOGIN_TEMPLATE, error="اسم المستخدم أو كلمة المرور غير صحيحة!")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_page"))

@app.route("/google82d8bfe80e0c1a19.html")
def google_verification():
    return "google-site-verification: google82d8bfe80e0c1a19.html"

@app.route("/sitemap.xml")
def sitemap():
    # هنا تضع روابط صفحات موقعك الأساسية
    pages = [
        "https://immoecu.onrender.com",
        "https://immoecu.onrender.com/login",
        "https://immoecu.onrender.com/immo_tool",
        "https://immoecu.onrender.com/logout"
    ]
    
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n
    xml += '<urlset xmlns="http://sitemaps.org">\n
    for page in pages:
        xml += f"  <url><loc>{page}</loc></url>\n
    xml += '</urlset>'
    
    return xml, 200, {'Content-Type': 'application/xml'}

# ----------------------------------------------------
# 1. مسار الصفحة الرئيسية التعريفية (سيراها زوار جوجل والعامة)
# ----------------------------------------------------
@app.route("/")
def landing_page():
    # إذا كان المستخدم مسجلاً دخوله بالفعل، انقله مباشرة للأداة
    if "username" in session: 
        return redirect(url_for("immo_tool_page"))
    # إذا كان زائراً جديداً، اعرض له الواجهة التعريفية
    return render_template_string(LANDING_TEMPLATE)

# ----------------------------------------------------
# 2. مسار أداة التعديل والمعالجة (محمي بالكامل)
# ----------------------------------------------------
@app.route("/immo_tool", methods=["GET", "POST"])
def immo_tool_page():
    if "username" not in session: 
        return redirect(url_for("login_page"))
        
    if request.method == "GET": 
        return render_template_string(IMMO_TEMPLATE)
        
    if request.method == "POST":
        file = request.files.get("dump_file")
        ecu_type = request.form.get("ecu_type")
        operation = request.form.get("operation")
        if not file or file.filename == "": 
            return jsonify({"status": "❌ يرجى اختيار ملف الدامب أولاً!"})
            
        file_bytes = file.read()
        server_code, pin, is_err, out_name, mod_bytes, should_dl = process_ecu_file(ecu_type, file_bytes, operation, file.filename)
        
        if should_dl and not is_err: 
            return send_file(io.BytesIO(mod_bytes), download_name=out_name, as_attachment=True)
        return jsonify({"status": server_code, "pin": pin})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)

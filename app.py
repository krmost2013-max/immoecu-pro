import os
import io
import json
import threading
import webbrowser
from flask import Flask, request, render_template_string, send_file, jsonify

app = Flask(__name__)
app.secret_key = "ecu_secret_key_pro"
ECU_DATABASE = {
    "edc16c34_psa": {"name": "Bosch EDC16C34", "brand": "PSA", "make": "Bosch"},
    "edc16c3_psa": {"name": "Bosch EDC16C3 (EEPROM 2KB) - PSA", "brand": "PSA", "make": "Bosch"},
    "edc15c2_psa_eeprom": {"name": "Bosch EDC15C2 (EEPROM 5P08C3) - PSA", "brand": "PSA", "make": "Bosch"},
    "edc15c2_psa_flash": {"name": "Bosch EDC15C2 (FLASH 29F400BT 512KB) - PSA", "brand": "PSA", "make": "Bosch"},
    "me744_psa": {"name": "Bosch ME7.4.4 (EEPROM 95160 2KB) - PSA", "brand": "PSA", "make": "Bosch"},
    "sid807evo_psa": {"name": "Continental SID807EVO - PSA", "brand": "PSA", "make": "Siemens"},
    "sid801_25dt_psa": {"name": "Siemens SID801 (25DT EEPROM 256B) - PSA", "brand": "PSA", "make": "Siemens"},
    "sid804_psa": {"name": "Siemens SID802 / SID804 (EEPROM 256B) - PSA", "brand": "PSA", "make": "Siemens"},
    "dcm35_psa": {"name": "Delphi DCM3.5 (EEPROM 8KB) - PSA", "brand": "PSA", "make": "Delphi"},
    "valeo_v34_psa": {"name": "Valeo V34.1 / V34.3 (EEPROM)", "brand": "PSA", "make": "Valeo"},
    "valeo_j34p_psa": {"name": "Valeo J34P (EEPROM 95160 2KB) - PSA", "brand": "PSA", "make": "Valeo"},
    "marelli_48p2_psa": {"name": "Magneti Marelli IAW 48P2 (FLASH 512KB) - PSA Auto-Scan", "brand": "PSA", "make": "Marelli"},
    "marelli_4mp2_psa": {"name": "Magneti Marelli IAW 4MP2 (FLASH 256KB) - PSA Auto-Scan", "brand": "PSA", "make": "Marelli"},
    "s2000_psa": {"name": "Sagem S2000 (EEPROM 95080) - PSA/Renault", "brand": "PSA", "make": "Valeo"}
}
INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImmoEcu Pro Workshop</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .welcome-container { background: rgba(27, 46, 75, 0.65); max-width: 700px; padding: 40px; border-radius: 16px; box-shadow: 0px 15px 40px rgba(0,0,0,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); text-align: center; }
        h1 { color: #00b8ff; font-size: 32px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 184, 255, 0.4); margin-bottom: 5px; }
        p { color: #888ea8; font-size: 15px; margin-bottom: 35px; font-weight: 500; }
        .choice-grid { display: flex; gap: 20px; justify-content: center; margin-top: 20px; }
        .card { flex: 1; background: #060b19; padding: 25px; border-radius: 12px; border: 1px solid #3b3f5c; cursor: pointer; transition: all 0.3s ease; text-decoration: none; color: #fff; }
        .card:hover { border-color: #00b8ff; transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0, 184, 255, 0.15); }
        .card h3 { color: #00e676; font-size: 18px; margin-top: 0; margin-bottom: 10px; }
        .card p { font-size: 13px; color: #bfc9d4; margin: 0; }
        .footer-brand { margin-top: 40px; font-size: 11px; color: #515365; font-weight: bold; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="welcome-container">
        <h1>💻 ImmoEcu Pro Platform v10.6</h1>
        <p>مرحباً بك في المنصة الاحترافية المتكاملة لفحص وهندسة ملفات عقول السيارات</p>
        <div class="choice-grid">
            <a href="/hex_viewer" class="card">
                <h3>🔍 Live Hex Viewer Matrix</h3>
                <p>قم برفع أي ملف باينري وعرض مصفوفة الـ Hex بالكامل فوراً واستكشاف محتوياته بدقة علمية.</p>
            </a>
            <a href="/immo_tool" class="card">
                <h3>⚡ IMMO & PIN Solutions</h3>
                <p>الدخول مباشرة إلى الأداة الذكية لتطبيق الحلول البرمجية الفورية وإلغاء الحماية وقراءة البين كود.</p>
            </a>
        </div>
        <div class="footer-brand">POWERED BY PRO DEVELOPER TEAM © 2026</div>
    </div>
</body>
</html>
"""
HEX_VIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <title>Live Hex Matrix Viewer</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #e0e6ed; padding: 30px; margin: 0; min-height: 100vh; }
        .box { background: rgba(27, 46, 75, 0.65); max-width: 850px; margin: auto; padding: 30px; border-radius: 16px; box-shadow: 0px 10px 30px rgba(0,0,0,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); }
        .nav-btn { background: #3b3f5c; color: white; padding: 8px 16px; text-decoration: none; border-radius: 6px; font-size: 13px; font-weight: bold; display: inline-block; margin-bottom: 20px; transition: all 0.2s; }
        .nav-btn:hover { background: #00b8ff; color: #060b19; }
        h2 { color: #00b8ff; margin-top: 0; font-size: 24px; font-weight: 800; text-shadow: 0 0 10px rgba(0, 184, 255, 0.3); }
        .custom-file-upload { display: block; text-align: center; cursor: pointer; border: 2px dashed #00b8ff; color: #00b8ff; padding: 25px; border-radius: 8px; background: rgba(0, 184, 255, 0.05); font-weight: bold; font-size: 16px; transition: all 0.2s; }
        .custom-file-upload:hover { background: rgba(0, 184, 255, 0.15); box-shadow: 0 0 12px rgba(0, 184, 255, 0.2); }
        .hex-container { background: #040811; border: 1px solid #253b5e; font-family: 'Courier New', Courier, monospace; font-size: 13px; padding: 15px; margin-top: 25px; border-radius: 8px; overflow-x: auto; max-height: 500px; white-space: pre; color: #00ff00; text-align: left; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); border-left: 4px solid #00e676; }
    </style>
</head>
<body>
    <div class="box">
        <a href="/" class="nav-btn">🏠 القائمة الرئيسية</a>
        <h2>🔍 Live Hex Matrix Analyzer</h2>
        <p style="color: #888ea8; font-size: 14px; margin-top: -10px; margin-bottom: 25px;">قم برفع ملف الـ Dump لعرض الخانات البرمجية وترجمتها الفورية</p>
        <label for="dump_file" id="file-btn-text" class="custom-file-upload">📁 Click to Upload Binary Dump File...</label>
        <input type="file" id="dump_file" style="display: none;" onchange="viewHexDump(this)" required>
        <div id="hex-viewer" class="hex-container" style="display:none;"></div>
    </div>
    <script>
        function viewHexDump(input) {
            let fBtn = document.getElementById('file-btn-text');
            let viewer = document.getElementById('hex-viewer');
            if (input.files && input.files[0]) {
                fBtn.innerText = "📄 " + input.files[0].name;
                let reader = new FileReader();
                reader.onload = function(e) {
                    let buffer = new Uint8Array(e.target.result);
                    let hexString = "Offset(h)  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  Decoded Text\\\\n";
                    hexString += "-------------------------------------------------------------------------\\\\n";
                    for (let i = 0; i < buffer.length; i += 16) {
                        let offset = i.toString(16).toUpperCase().padStart(8, '0');
                        let bytes = ""; let ascii = "";
                        for (let j = 0; j < 16; j++) {
                            if (i + j < buffer.length) {
                                let b = buffer[i + j];
                                bytes += b.toString(16).toUpperCase().padStart(2, '0') + " ";
                                ascii += (b >= 32 && b <= 126) ? String.fromCharCode(b) : ".";
                            } else { bytes += "   "; }
                        }
                        hexString += offset + "  " + bytes + " " + ascii + "\\\\n";
                    }
                    viewer.innerText = hexString; viewer.style.display = 'block';
                };
                reader.readAsArrayBuffer(input.files[0]);
            }
        }
    </script>
</body>
</html>
"""
IMMO_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" dir="ltr" id="html-tag">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ImmoEcu Pro v10.6</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #e0e6ed; padding: 40px 20px; text-align: left; margin: 0; min-height: 100vh; }
        html[dir="rtl"] body { text-align: right; }
        .box { background: rgba(27, 46, 75, 0.65); max-width: 600px; margin: auto; padding: 30px; border-radius: 16px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); }
        .nav-btn { background: #3b3f5c; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 13px; font-weight: bold; display: inline-block; transition: all 0.2s; margin-top: -5px; float: right; }
        html[dir="rtl"] .nav-btn { float: left; }
        .nav-btn:hover { background: #00b8ff; color: #060b19; }
        h1 { color: #00b8ff; text-align: center; font-size: 28px; margin-top: 10px; font-weight: 800; text-shadow: 0 0 15px rgba(0, 184, 255, 0.4); }
        p { color: #00e676; font-size: 14px; text-align: center; font-weight: bold; margin-bottom: 30px; }
        label { display: block; margin-top: 20px; color: #888ea8; font-weight: 600; font-size: 14px; text-transform: uppercase; }
        select, button { width: 100%; padding: 14px; margin: 8px 0; border-radius: 8px; background: #060b19; color: #fff; border: 1px solid #3b3f5c; box-sizing: border-box; font-size: 15px; outline: none; }
        select:focus { border-color: #00b8ff; box-shadow: 0 0 8px rgba(0, 184, 255, 0.3); }
        .custom-file-upload { display: block; text-align: center; cursor: pointer; border: 2px dashed #00b8ff; color: #00b8ff; width: 100%; padding: 16px; margin: 8px 0; border-radius: 8px; background: rgba(0, 184, 255, 0.05); font-weight: bold; font-size: 15px; transition: all 0.2s ease; }
        .custom-file-upload:hover { background: rgba(0, 184, 255, 0.15); box-shadow: 0 0 12px rgba(0, 184, 255, 0.2); }
        button { background: linear-gradient(135deg, #00e676 0%, #00c853 100%); color: #060b19; font-size: 16px; cursor: pointer; border: none; font-weight: 700; margin-top: 25px; box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3); text-transform: uppercase; }
        button:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0, 230, 118, 0.5); background: linear-gradient(135deg, #00ff87 0%, #00e676 100%); }
        .alert, .err { padding: 14px; margin-bottom: 20px; border-radius: 8px; text-align: center; font-size: 15px; font-weight: 700; }
        .alert { background: rgba(0, 230, 118, 0.15); color: #00ff87; border: 1px solid rgba(0, 230, 118, 0.3); }
        .err { background: rgba(255, 23, 68, 0.15); color: #ff5252; border: 1px solid rgba(255, 23, 68, 0.3); }
        .lang { text-align: center; margin-bottom: 20px; }
        .lang select { width: auto; background: #1b2e4b; display: inline-block; padding: 6px 12px; color: #bfc9d4; }
        .hex-container { background: #040811; border: 1px solid #253b5e; font-family: 'Courier New', Courier, monospace; font-size: 13px; padding: 15px; margin-top: 25px; border-radius: 8px; overflow-x: auto; display: none; max-height: 250px; white-space: pre; color: #00ff00; text-align: left; border-left: 3px solid #00b8ff; }
        html[dir="rtl"] .hex-container { text-align: left; direction: ltr; }
        .chk-container { display: flex; align-items: center; margin-top: 15px; font-size: 14px; color: #bfc9d4; cursor: pointer; }
        .chk-container input { width: auto; margin-right: 10px; margin-left: 0; transform: scale(1.2); }
        html[dir="rtl"] .chk-container input { margin-left: 10px; margin-right: 0; }
    </style>
</head>
<body>
"""
IMMO_TEMPLATE += """
    <div class="box">
        <div class="lang">
            <a href="/" id="nav-main-btn" class="nav-btn">🏠 Main Menu</a>
            <span id="l-lbl">🌐 Lang:</span>
            <select id="lSel" onchange="chgL(this.value)">
                <option value="en">English</option>
                <option value="ar">العربية</option>
                <option value="fr">Français</option>
            </select>
        </div>
        <h1 id="m-title">💻 ImmoEcu Pro v10.6</h1>
        <p id="m-sub">🔧 Professional Multi-Brand PIN & IMMO Solutions</p>
        <div id="msg-box" style="display:none;"></div>
        <form id="ecuForm" onsubmit="submitForm(event)">
            <label id="l-file">📂 Select File:</label>
            <label for="dump_file" id="file-btn-text" class="custom-file-upload">📁 Choose File...</label>
            <input type="file" id="dump_file" name="dump_file" style="display: none;" onchange="updateFileName(this)" required>
            <label id="l-brand">🚗 Select Brand / Company:</label>
            <select id="brand_filter" onchange="filterEcus()">
                <option value="ALL">-- ALL BRANDS --</option>
                <option value="PSA">PSA (Peugeot / Citroën)</option>
            </select>
            <label id="l-make">⚙️ Select ECU Maker:</label>
            <select id="make_filter" onchange="filterEcus()">
                <option value="ALL">-- ALL MAKERS --</option>
                <option value="Bosch">Bosch</option>
                <option value="Siemens">Siemens / Continental</option>
                <option value="Valeo">Valeo / Sagem</option>
                <option value="Marelli">Magneti Marelli</option>
                <option value="Delphi">Delphi</option>
            </select>
            <label id="l-ecu">🤖 Select ECU Type:</label>
            <select name="ecu_type" id="ecu_type"></select>
            <label id="l-op">⚡ Operation:</label>
            <select name="operation" id="operation">
                <option value="immo_off" id="o-off">IMMO OFF</option>
                <option value="read_pin" id="o-pin">Read PIN</option>
                <option value="immo_virgin" id="o-vir">IMMO VIRGIN</option>
            </select>
            <label class="chk-container">
                <input type="checkbox" id="showHexChk" onchange="toggleHexView()">
                <span id="l-showhex">⚙️ Show Live Hex View Matrix</span>
            </label>
            <button type="submit" id="b-sub">Process File 🚀</button>
        </form>
        <div id="hex-viewer" class="hex-container"></div>
    </div>
</body>
</html>
"""
JAVASCRIPT_TEMPLATE_1 = """
<script>
    const rawDatabase = {
        "edc16c34_psa": {"name": "Bosch EDC16C34", "brand": "PSA", "make": "Bosch"},
        "edc16c3_psa": {"name": "Bosch EDC16C3 (EEPROM 2KB) - PSA", "brand": "PSA", "make": "Bosch"},
        "edc15c2_psa_eeprom": {"name": "Bosch EDC15C2 (EEPROM 5P08C3) - PSA", "brand": "PSA", "make": "Bosch"},
        "edc15c2_psa_flash": {"name": "Bosch EDC15C2 (FLASH 29F400BT 512KB) - PSA", "brand": "PSA", "make": "Bosch"},
        "me744_psa": {"name": "Bosch ME7.4.4 (EEPROM 95160 2KB) - PSA", "brand": "PSA", "make": "Bosch"},
        "sid807evo_psa": {"name": "Continental SID807EVO - PSA", "brand": "PSA", "make": "Siemens"},
        "sid801_25dt_psa": {"name": "Siemens SID801 (25DT EEPROM 256B) - PSA", "brand": "PSA", "make": "Siemens"},
        "sid804_psa": {"name": "Siemens SID802 / SID804 (EEPROM 256B) - PSA", "brand": "PSA", "make": "Siemens"},
        "dcm35_psa": {"name": "Delphi DCM3.5 (EEPROM 8KB) - PSA", "brand": "PSA", "make": "Delphi"},
        "valeo_v34_psa": {"name": "Valeo V34.1 / V34.3 (EEPROM)", "brand": "PSA", "make": "Valeo"},
        "valeo_j34p_psa": {"name": "Valeo J34P (EEPROM 95160 2KB) - PSA", "brand": "PSA", "make": "Valeo"},
        "marelli_48p2_psa": {"name": "Magneti Marelli IAW 48P2 (FLASH 512KB) - PSA Auto-Scan", "brand": "PSA", "make": "Marelli"},
        "marelli_4mp2_psa": {"name": "Magneti Marelli IAW 4MP2 (FLASH 256KB) - PSA Auto-Scan", "brand": "PSA", "make": "Marelli"},
        "s2000_psa": {"name": "Sagem S2000 (EEPROM 95080) - PSA/Renault", "brand": "PSA", "make": "Valeo"}
    };
"""
JAVASCRIPT_TEMPLATE_1 += """
    const locales = {
        "en": {
            "title": "💻 ImmoEcu Pro v10.6", "sub": "🔧 Professional Multi-Brand PIN & IMMO Solutions",
            "lbl_lang": "🌐 Lang:", "lbl_file": "📂 Select File:", "lbl_ecu": "🤖 Select ECU Type:",
            "lbl_op": "⚡ Operation:", "btn_sub": "Process File 🚀", "choose_file": "📁 Choose File...",
            "lbl_showhex": "⚙️ Show Live Hex View Matrix", "nav_main": "🏠 Main Menu",
            "lbl_brand": "🚗 Select Brand / Company:", "lbl_make": "⚙️ Select ECU Maker:",
            "opt_all_brands": "-- ALL BRANDS --", "opt_all_makes": "-- ALL MAKERS --",
            "err_size_16": "❌ Error: Invalid size for EDC16C34. Expected 8KB!",
            "err_size_c3": "❌ Error: Invalid size for EDC16C3. Expected 2KB EEPROM!",
            "err_size_sid801": "❌ Error: Invalid size for SID801 25DT. Expected 256 Bytes EEPROM!",
            "err_size_sid804": "❌ Error: Invalid size for SID802 / SID804. Expected 256 Bytes EEPROM!",
            "err_size_me744": "❌ Error: Invalid size for ME7.4.4. Expected 2KB EEPROM!",
            "err_size_dcm35": "❌ Error: Invalid size for DCM3.5. Expected 8KB EEPROM!",
            "err_valeo": "❌ Error: Failed to parse Valeo file.",
            "err_valeo_off": "❌ Error: IMMO bytes not found in Valeo.",
            "err_size_15e": "❌ Error: Invalid size. Expected 1KB!",
            "err_15e_sup": "❌ Error: Operation not supported for this EEPROM.",
            "err_size_15f": "❌ Error: Invalid size for Flash. Expected 512KB!",
            "err_size_j34": "❌ Error: Invalid size for J34P. Expected 2KB!",
            "err_already_off": "⚠️ Notice: This file already has IMMO OFF applied!",
            "err_legacy_s2000": "❌ Error: Unsupported S2000 structure.",
            "err_corrupted": "❌ Error: Corrupted PIN structure.",
            "err_size_48pf": "❌ Error: Invalid size for Marelli Flash. Expected 512KB!",
            "err_size_4mpf": "❌ Error: Invalid size for Marelli Flash. Expected 262KB!",
            "err_sid_not_found": "❌ Error: Target rows not found inside the uploaded file!",
            "err_me744_not_found": "❌ Error: Offsets 00000590 or 000005A0 not found inside the file!",
            "success_pin": "🎉 Success! Extracted PIN Code: ",
            "success_mod": "✅ Success! File patched successfully. Downloading..."
        },
        "ar": {
            "title": "💻 إيمو إيكو برو v10.6", "sub": "🔧 حلول احترافية لفك الشيفرة وقراءة محارف الـ PIN",
            "lbl_lang": "🌐 اللغة:", "lbl_file": "📂 اختر ملف العقل:", "lbl_ecu": "🤖 نوع وحدة التحكم (ECU):",
            "lbl_op": "⚡ نوع العملية المطلوبة:", "btn_sub": "معالجة وتحليل الملف 🚀", "choose_file": "📁 اختر ملف...",
            "lbl_showhex": "⚙️ تفعيل ميزة عرض محتويات الـ Hex للملف", "nav_main": "🏠 القائمة الرئيسية",
            "lbl_brand": "🚗 اختر شركة السيارة:", "lbl_make": "⚙️ اختر صانع العقل (بوش، سيمنس...):",
            "opt_all_brands": "-- كل الشركات --", "opt_all_makes": "-- كل المصنعين --",
            "err_size_16": "❌ خطأ: حجم ملف EDC16C34 غير صحيح. المتوقع 8 كيلوبايت!",
            "err_size_c3": "❌ خطأ: حجم ملف EDC16C3 غير صحيح. المتوقع ملف إيبروم بحجم 2 كيلوبايت!",
            "err_size_sid801": "❌ خطأ: حجم ملف SID801 25DT غير صحيح. المتوقع ملف إيبروم بحجم 256 بايت!",
            "err_size_sid804": "❌ خطأ: حجم ملف SID802 / SID804 غير صحيح. المتوقع ملف إيبروم بحجم 256 بايت!",
            "err_size_me744": "❌ خطأ: حجم ملف ME7.4.4 غير صحيح. المتوقع إيبروم بحجم 2 كيلوبايت!",
            "err_size_dcm35": "❌ خطأ: حجم ملف DCM3.5 غير صحيح. المتوقع إيبروم بحجم 8 كيلوبايت!",
            "err_valeo": "❌ خطأ: فشل استخراج كود الـ PIN أو قراءة ملف Valeo.",
            "err_valeo_off": "❌ خطأ: لم يتم العثور على بايتات نظام الحماية في ملف Valeo.",
            "err_size_15e": "❌ خطأ: حجم ملف الـ EEPROM غير صحيح. المتوقع 1 كيلوبايت!",
            "err_15e_sup": "❌ خطأ: العملية غير مدعومة لعقل الـ EEPROM هذا.",
            "err_size_15f": "❌ خطأ: حجم ملف الفلاش غير صحيح. المتوقع 512 كيلوبايت!",
            "err_size_j34": "❌ خطأ: حجم ملف J34P غير صحيح. المتوقع 2 كيلوبايت!",
            "err_already_off": "⚠️ تنبيه: تم إلغاء نظام الحماية (IMMO OFF) في هذا الملف مسبقاً!",
            "err_legacy_s2000": "❌ خطأ: هيكلية ملف S2000 قديمة أو غير مدعومة.",
            "err_corrupted": "❌ خطأ: بيانات تالفة أو محارف كود الـ PIN غير مقروءة.",
            "err_size_48pf": "❌ خطأ: حجم ملف ماريللي غير صحيح. المتوقع 512 كيلوبايت!",
            "err_size_4mpf": "❌ خطأ: حجم ملف ماريللي غير صحيح. المتوقع 256 كيلوبايت!",
            "err_sid_not_found": "❌ خطأ: لم يتم العثور على الأسطر المطلوبة داخل الملف المرفوع!",
            "err_me744_not_found": "❌ خطأ: لم يتم العثور على السطرين 00000590 أو 000005A0 داخل ملف الدامب!",
            "success_pin": "🎉 ممتاز! تم استخراج كود الـ PIN بنجاح: ",
            "success_mod": "✅ ممتاز! تم تعديل وتطهير الملف بنجاح. جار التحميل..."
        },
        "fr": {
            "title": "💻 ImmoEcu Pro v10.6", "sub": "🔧 Solutions Professionnelles IMMO & PIN Multi-Marques",
            "lbl_lang": "🌐 Langue:", "lbl_file": "📂 Choisir Fichier:", "lbl_ecu": "🤖 Sélectionner ECU:",
            "lbl_op": "⚡ Operation:", "btn_sub": "Calculer le Fichier 🚀", "choose_file": "📁 Choisir Fichier...",
            "lbl_showhex": "⚙️ Afficher la matrice Hex du fichier", "nav_main": "🏠 Menu Principal",
            "lbl_brand": "🚗 Choisir la Marque:", "lbl_make": "⚙️ Choisir le Fabricant:",
            "opt_all_brands": "-- TOUTES MARQUES --", "opt_all_makes": "-- TOUS FABRICANTS --",
            "err_size_16": "❌ Erreur: Taille EDC16C34 invalide. 8 Ko attendu!",
            "err_size_c3": "❌ Erreur: Taille EDC16C3 invalide. EEPROM 2 Ko attendu!",
            "err_size_sid801": "❌ Erreur: Taille SID801 25DT invalide. EEPROM 256 Octets attendu!",
            "err_size_sid804": "❌ Erreur: Taille SID802 / SID804 invalide. EEPROM 256 Octets attendu!",
            "err_size_me744": "❌ Erreur: Taille ME7.4.4 invalide. EEPROM 2KB attendu!",
            "err_size_dcm35": "❌ Erreur: Taille DCM3.5 invalide. EEPROM 8KB attendu!",
            "err_valeo": "❌ Erreur: Échec d'extraction PIN ou lecture Valeo.",
            "err_valeo_off": "❌ Erreur: Octets d'antidémarrage introuvables dans Valeo.",
            "err_size_15e": "❌ Erreur: Taille EEPROM invalide. 1 Ko attendu!",
            "err_15e_sup": "❌ Erreur: Opération non supportée pour cette EEPROM.",
            "err_size_15f": "❌ Erreur: Taille Flash invalide. 512 Ko attendu!",
            "err_size_j34": "❌ Erreur: Taille J34P invalide. 2 Ko attendu!",
            "err_already_off": "⚠️ Avis: Fichier déjà modified (IMMO OFF appliqué)!",
            "err_legacy_s2000": "❌ Erreur: Structure S2000 non supportée.",
            "err_corrupted": "❌ Erreur: Données corrompues.",
            "err_size_48pf": "❌ Erreur: Taille Flash Marelli invalide. 512 Ko attendu!",
            "err_size_4mpf": "❌ Erreur: Taille Flash Marelli invalide. 256 Ko attendu!",
            "err_sid_not_found": "❌ Erreur: Ligne référence introuvable dans SID807EVO!",
            "err_me744_not_found": "❌ Erreur: Lignes 00000590 or 000005A0 introuvables!",
            "success_pin": "🎉 Succès! Code PIN Extrait: ",
            "success_mod": "✅ Succès! Fichier modified."
        }
    };
</script>
"""
JAVASCRIPT_TEMPLATE_2 = """
<script>
    function filterEcus() {
        const brandSel = document.getElementById('brand_filter').value;
        const makeSel = document.getElementById('make_filter').value;
        const ecuTypeSelect = document.getElementById('ecu_type');
        ecuTypeSelect.innerHTML = "";
        
        for (const [key, ecu] of Object.entries(rawDatabase)) {
            const matchBrand = (brandSel === "ALL" || ecu.brand === brandSel);
            const matchMake = (makeSel === "ALL" || ecu.make === makeSel);
            if (matchBrand && matchMake) {
                let opt = document.createElement('option');
                opt.value = key; opt.innerText = ecu.name;
                ecuTypeSelect.appendChild(opt);
            }
        }
    }

    function chgL(l) {
        localStorage.setItem('lang', l);
        let htmlTag = document.getElementById('html-tag');
        htmlTag.setAttribute('dir', l === 'ar' ? 'rtl' : 'ltr');
        htmlTag.setAttribute('lang', l);
        
        document.getElementById('m-title').innerText = locales[l]['title'];
        document.getElementById('m-sub').innerText = locales[l]['sub'];
        document.getElementById('l-lbl').innerText = locales[l]['lbl_lang'];
        document.getElementById('l-file').innerText = locales[l]['lbl_file'];
        document.getElementById('l-ecu').innerText = locales[l]['lbl_ecu'];
        document.getElementById('l-op').innerText = locales[l]['lbl_op'];
        document.getElementById('b-sub').innerText = locales[l]['btn_sub'];
        document.getElementById('l-showhex').innerText = locales[l]['lbl_showhex'];
        document.getElementById('l-brand').innerText = locales[l]['lbl_brand'];
        document.getElementById('l-make').innerText = locales[l]['lbl_make'];
        
        document.getElementById('brand_filter').options[0].text = locales[l]['opt_all_brands'];
        document.getElementById('make_filter').options[0].text = locales[l]['opt_all_makes'];
        
        let navBtn = document.getElementById('nav-main-btn');
        if(navBtn) { navBtn.innerText = locales[l]['nav_main']; }
        
        let fBtn = document.getElementById('file-btn-text');
        if(fBtn.getAttribute('data-chosen') !== 'true') { fBtn.innerText = locales[l]['choose_file']; }
        filterEcus();
    }

    function toggleHexView() {
        let chk = document.getElementById('showHexChk');
        let viewer = document.getElementById('hex-viewer');
        if (chk.checked && viewer.innerText.trim() !== "") { viewer.style.display = 'block'; }
        else { viewer.style.display = 'none'; }
    }
"""
JAVASCRIPT_TEMPLATE_2 += """
    function updateFileName(input) {
        let fBtn = document.getElementById('file-btn-text');
        if (input.files && input.files.length > 0) {
            fBtn.innerText = "📄 " + input.files[0].name;
            fBtn.setAttribute('data-chosen', 'true');
            let reader = new FileReader();
            reader.onload = function(e) {
                let buffer = new Uint8Array(e.target.result);
                let hexString = "Offset(h)  00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  Decoded Text\\\\n";
                hexString += "-------------------------------------------------------------------------\\\\n";
                for (let i = 0; i < buffer.length; i += 16) {
                    let offset = i.toString(16).toUpperCase().padStart(8, '0');
                    let bytes = ""; let ascii = "";
                    for (let j = 0; j < 16; j++) {
                        if (i + j < buffer.length) {
                            let b = buffer[i + j];
                            bytes += b.toString(16).toUpperCase().padStart(2, '0') + " ";
                            ascii += (b >= 32 && b <= 126) ? String.fromCharCode(b) : ".";
                        } else { bytes += "   "; }
                    }
                    hexString += offset + "  " + bytes + " " + ascii + "\\\\n";
                }
                document.getElementById('hex-viewer').innerText = hexString;
                toggleHexView();
            };
            reader.readAsArrayBuffer(input.files[0]);
        }
    }

    async function submitForm(event) {
        event.preventDefault();
        let msgBox = document.getElementById('msg-box'); msgBox.style.display = 'none';
        let fileInput = document.getElementById('dump_file');
        if (!fileInput.files || fileInput.files.length === 0) return;
        
        let formData = new FormData();
        formData.append('dump_file', fileInput.files[0]);
        formData.append('ecu_type', document.getElementById('ecu_type').value);
        formData.append('operation', document.getElementById('operation').value);
        let currentLang = localStorage.getItem('lang') || 'en';
        
        try {
            let response = await fetch('/immo_tool', { method: 'POST', body: formData });
            if (!response.ok) throw new Error();
            let contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                let result = await response.json();
                msgBox.className = result.is_error ? 'err' : 'alert';
                if (result.code === 'success_pin') { msgBox.innerText = locales[currentLang]['success_pin'] + result.pin; }
                else { msgBox.innerText = locales[currentLang][result.code]; }
                msgBox.style.display = 'block';
            } else {
                let blob = await response.blob();
                let url = window.URL.createObjectURL(blob);
                let a = document.createElement('a'); a.href = url; a.download = "MOD_" + fileInput.files[0].name;
                document.body.appendChild(a); a.click(); a.remove();
                msgBox.className = 'alert'; msgBox.innerText = locales[currentLang]['success_mod']; msgBox.style.display = 'block';
            }
        } catch (err) { msgBox.className = 'err'; msgBox.innerText = '❌ Connection Error!'; msgBox.style.display = 'block'; }
    }

    window.onload = function() {
        let savedLang = localStorage.getItem('lang') || 'en';
        document.getElementById('lSel').value = savedLang;
        chgL(savedLang);
    };
</script>
"""
def process_ecu_file(file_bytes, file_size, ecu_key, operation, original_filename):
    server_code = ""
    extracted_pin = ""
    is_error_css = True
    filename_out = "MOD_" + original_filename
    should_download = False

    # --- عقول Bosch EDC16C34 ---
    if ecu_key == "edc16c34_psa":
        if file_size != 8192:
            server_code = "err_size_16"
        elif operation == "immo_off":
            file_bytes[0x00:0x04] = b"\x00\x58\x6F\xFB"
            file_bytes[0x0060:0x0070] = b"\xFA\xBE\x86\x8A\xFF\xFF\xFB\x39\x00\x00\x00\x00\x00\x00\x00\x00"
            file_bytes[0x0070:0x0080] = b"\x00" * 16
            file_bytes[0x0080:0x0090] = b"\xCE\xDF\x23\xBE\xAA\xC3\xFC\x04\x00\x00\x00\x00\x00\x00\x00\x00"
            file_bytes[0x0090:0x00A0] = b"\x00" * 16
            file_bytes[0x00A0:0x00B0] = b"\xDB\xAC\x92\x8C\x55\x3C\xFC\xC9\x00\x00\x00\x00\x00\x00\x00\x00"
            filename_out = "IMMO_OFF_" + original_filename
            should_download = True; is_error_css = False
        elif operation == "immo_virgin":
            file_bytes[0x0010:0x0030] = b"\xFF" * 32
            filename_out = "VIRGIN_" + original_filename
            should_download = True; is_error_css = False

    # --- عقول Bosch EDC16C3 ---
    elif ecu_key == "edc16c3_psa":
        if file_size != 2048:
            server_code = "err_size_c3"
        elif operation == "immo_off":
            file_bytes[0x0060:0x00B0] = (
                b"\xFA\xBE\x86\x8A\xFF\xFF\xFB\x37\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\xCE\xDF\x23\xBE\xAA\xC3\xFC\x01\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
                b"\xDB\xAC\x92\x8C\x55\x3C\xFC\xC5\x00\x00\x00\x00\x00\x00\x00\x00"
            )
            filename_out = "BOSCH_EDC16C3_IMMO_OFF_" + original_filename
            should_download = True; is_error_css = False
        elif operation == "read_pin":
            try:
                b1, b2 = file_bytes[0x01FC], file_bytes[0x01FD]
                if all(32 <= x <= 126 for x in [b1, b2]):
                    extracted_pin = f"{chr(b1)}{chr(b2)}"; server_code = "success_pin"; is_error_css = False
                else: server_code = "err_corrupted"
            except: server_code = "err_corrupted"

    # --- عقول Bosch ME7.4.4 التطهير وقراءة البين كود الطبيعي ---
    elif ecu_key == "me744_psa":
        if file_size != 2048:
            server_code = "err_size_me744"
        elif operation == "immo_off":
            if file_size >= 0x05B0:
                file_bytes[0x0590:0x05A0] = b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\x54\xF9"
                file_bytes[0x05A0:0x05B0] = b"\x58\x01\x11\x11\x11\x11\xEE\xEE\xEE\xEE\xFF\x00\xFF\x00\x54\xF9"
                filename_out = "BOSCH_ME744_IMMO_OFF_" + original_filename
                should_download = True; is_error_css = False
            else:
                server_code = "err_me744_not_found"
        elif operation == "read_pin":
            try:
                if file_size >= 0x05B0:
                    b1, b2, b3, b4 = file_bytes[0x0592], file_bytes[0x0593], file_bytes[0x0594], file_bytes[0x0595]
                    if all(32 <= x <= 126 for x in [b1, b2, b3, b4]):
                        extracted_pin = f"{chr(b1)}{chr(b2)}{chr(b3)}{chr(b4)}"
                        server_code = "success_pin"; is_error_css = False
                    else: server_code = "err_corrupted"
                else: server_code = "err_me744_not_found"
            except: server_code = "err_corrupted"
    # --- عقول Bosch EDC15C2 (EEPROM) ---
    elif ecu_key == "edc15c2_psa_eeprom":
        if file_size != 1024:
            server_code = "err_size_15e"
        elif operation == "immo_off":
            file_bytes[0x14B:0x150] = b"\xFF\x9A\x9A\x9A\x00"
            file_bytes[0x200:0x204] = b"\x00\x00\x00\x00"
            file_bytes[0x214:0x218] = b"\x00\x00\x00\x00"
            file_bytes[0x22A:0x22E] = b"\x00\x00\x00\x00"
            filename_out = "EDC15_EEPROM_OFF_" + original_filename
            should_download = True; is_error_css = False

    # --- عقول Bosch EDC15C2 (FLASH) ---
    elif ecu_key == "edc15c2_psa_flash":
        if file_size != 524288:
            server_code = "err_size_15f"
        elif operation == "immo_off":
            for i in range(0x7CC5E, 0x7CCC6): file_bytes[i] = 0xFF
            filename_out = "EDC15_FLASH_OFF_" + original_filename
            should_download = True; is_error_css = False

    # --- عقول Valeo V34 ---
    elif ecu_key == "valeo_v34_psa":
        if operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x04], file_bytes[0x05], file_bytes[0x06], file_bytes[0x07]
                extracted_pin = f"{chr(b3)}{chr(b4)}{chr(b1)}{chr(b2)}"; server_code = "success_pin"; is_error_css = False
            except: server_code = "err_valeo"
        elif operation == "immo_off":
            o_b, n_b = b"\x40\x04\xBF\xFB", b"\x70\x07\x8F\xF8"
            if o_b in file_bytes:
                file_bytes[:] = file_bytes.replace(o_b, n_b)
                filename_out = "VALEO_V34_OFF_" + original_filename
                should_download = True; is_error_css = False
            else: server_code = "err_valeo_off"

    # --- عقول Sagem S2000 ---
    elif ecu_key == "s2000_psa":
        if file_size != 1024: server_code = "err_size_15e"
        else:
            expected_immo_off = b"\xFE\x6C\xFE\x6C\x11\x11\x11\x11\x00\xFF\xE0\x06\xC5\xA0\x00\xFF"
            if operation == "read_pin":
                if file_bytes[0x00:0x10] == expected_immo_off: server_code = "err_already_off"
                else:
                    try:
                        b1, b2, b3, b4 = file_bytes[0x04], file_bytes[0x05], file_bytes[0x06], file_bytes[0x07]
                        if all(33 <= x <= 126 for x in [b1, b2, b3, b4]):
                            extracted_pin = f"{chr(b3)}{chr(b4)}{chr(b1)}{chr(b2)}"; server_code = "success_pin"; is_error_css = False
                        else: server_code = "err_legacy_s2000"
                    except: server_code = "err_corrupted"
            elif operation == "immo_off":
                file_bytes[0x00:0x10] = expected_immo_off
                file_bytes[0x10:0x14] = b"\x39\x60\x00\x00"
                file_bytes[0x8E:0xA2] = b"\xFE\x6C\xFE\x6C\x11\x11\x11\x11\x00\xFF\xE0\x06\xC5\xA0\x00\xFF\x39\x60\x00\x00"
                filename_out = "S2000_EEPROM_OFF_" + original_filename
                should_download = True; is_error_css = False

    # --- عقول Valeo J34P ---
    elif ecu_key == "valeo_j34p_psa":
        if file_size != 2048: server_code = "err_size_j34"
        else:
            j34_patch_bytes = b"\xFE\x6C\xFE\x6C\x11\x11\x11\x11\x00\xFF\xE0\x06\xC5\xA0\x00\xFF\x39\x60\x00\x00\x00\x00"
            if operation == "read_pin":
                if file_bytes[0x00:0x16] == j34_patch_bytes: server_code = "err_already_off"
                else:
                    try:
                        b1, b2, b3, b4 = file_bytes[0x04], file_bytes[0x05], file_bytes[0x06], file_bytes[0x07]
                        if all(33 <= x <= 126 for x in [b1, b2, b3, b4]):
                            extracted_pin = f"{chr(b3)}{chr(b4)}{chr(b1)}{chr(b2)}"; server_code = "success_pin"; is_error_css = False
                        else: server_code = "err_corrupted"
                    except: server_code = "err_valeo"
            elif operation == "immo_off":
                file_bytes[0x00:0x16] = j34_patch_bytes; file_bytes[0x70:0x86] = j34_patch_bytes
                filename_out = "VALEO_J34P_OFF_" + original_filename
                should_download = True; is_error_css = False
    # --- عقول Magneti Marelli IAW 48P2 ---
    elif ecu_key == "marelli_48p2_psa":
        if file_size != 524288: server_code = "err_size_48pf"
        else:
            target_signature, marelli_patch = b"\x96\x48\xA5\xC3", b"\x31\x54\x34\x38\xFF\x7E\x46\x4A\xFF\x7E\xAB\xD6"
            if operation == "read_pin":
                found_offset = -1
                for offset in range(0, file_size, 16):
                    if file_bytes[offset:offset+4] == target_signature: found_offset = offset; break
                if found_offset == -1: server_code = "err_48p_not_found"
                else:
                    b1, b2, b3, b4 = file_bytes[found_offset+4], file_bytes[found_offset+5], file_bytes[found_offset+6], file_bytes[found_offset+7]
                    if b1 == 0x31 and b2 == 0x54: server_code = "err_already_off"
                    else:
                        try: extracted_pin = f"{chr(b2)}{chr(b1)}{chr(b4)}{chr(b3)}"; server_code = "success_pin"; is_error_css = False
                        except: server_code = "err_48p_corrupted"
            elif operation == "immo_off":
                pattern_found = False
                for offset in range(0, file_size, 16):
                    if file_bytes[offset:offset+4] == target_signature: file_bytes[offset+4:offset+16] = marelli_patch; pattern_found = True
                if not pattern_found: server_code = "err_48p_not_found"
                else: filename_out = "MARELLI_48P2_SCAN_OFF_" + original_filename; should_download = True; is_error_css = False

    # --- عقول Magneti Marelli IAW 4MP2 ---
    elif ecu_key == "marelli_4mp2_psa":
        if file_size != 262144: server_code = "err_size_4mpf"
        else:
            target_signature, marelli_patch = b"\x96\x48\xA5\xC3", b"\x31\x54\x34\x38\xFF\x7E\x46\x4A\xFF\x7E\xAB\xD6"
            if operation == "read_pin":
                found_offset = -1
                for offset in range(0, file_size, 16):
                    if file_bytes[offset:offset+4] == target_signature: found_offset = offset; break
                if found_offset == -1: server_code = "err_48p_not_found"
                else:
                    b1, b2, b3, b4 = file_bytes[found_offset+4], file_bytes[found_offset+5], file_bytes[found_offset+6], file_bytes[found_offset+7]
                    if b1 == 0x31 and b2 == 0x54: server_code = "err_already_off"
                    else:
                        try: extracted_pin = f"{chr(b2)}{chr(b1)}{chr(b4)}{chr(b3)}"; server_code = "success_pin"; is_error_css = False
                        except: server_code = "err_48p_corrupted"
            elif operation == "immo_off":
                pattern_found = False
                for offset in range(0, file_size, 16):
                    if file_bytes[offset:offset+4] == target_signature: file_bytes[offset+4:offset+16] = marelli_patch; pattern_found = True
                if not pattern_found: server_code = "err_48p_not_found"
                else: filename_out = "MARELLI_4MP2_SCAN_OFF_" + original_filename; should_download = True; is_error_css = False

    # --- عقول Siemens SID801 25DT ---
    elif ecu_key == "sid801_25dt_psa":
        if file_size != 256: server_code = "err_size_sid801"
        elif operation == "immo_off":
            for i in range(0x00, 0x0A): file_bytes[i] = 0x00
            for j in range(0x44, 0x4E): file_bytes[j] = 0x00
            filename_out = "SIEMENS_SID801_25DT_IMMO_OFF_" + original_filename; should_download = True; is_error_css = False

    # --- عقول Siemens SID802 / SID804 المدمجة الحصرية 256B ---
    elif ecu_key == "sid804_psa":
        if file_size != 256: server_code = "err_size_sid804"
        elif operation == "immo_off":
            file_bytes[0x00:0x10] = b"\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F\x32\xE2\xD2\x0A\x02\x16\x00\x00"
            file_bytes[0x47:0x50] = b"\x70\xFF\xFF\xFF\xFF\xFF\xFF\x01\x8F"
            filename_out = "SIEMENS_SID804_IMMO_OFF_" + original_filename; should_download = True; is_error_css = False
        elif operation == "read_pin":
            try:
                b1, b2, b3, b4 = file_bytes[0x00], file_bytes[0x01], file_bytes[0x02], file_bytes[0x03]
                if all(32 <= x <= 126 for x in [b1, b2, b3, b4]):
                    extracted_pin = f"{chr(b4)}{chr(b3)}{chr(b2)}{chr(b1)}"; server_code = "success_pin"; is_error_css = False
                else: server_code = "err_corrupted"
            except: server_code = "err_corrupted"

    # --- عقول Continental SID807EVO ---
    elif ecu_key == "sid807evo_psa":
        if operation == "immo_off":
            target_patch = b"\x11\x11\x11\x11\x07\x70\xFF\xD0\xB4\x01\x00\x01\x00\x00\x00\x00"
            if file_size >= 0xB10:
                file_bytes[0xB00:0xB10] = target_patch
                filename_out = "CONTINENTAL_SID807EVO_IMMO_OFF_" + original_filename; should_download = True; is_error_css = False
            else: server_code = "err_sid_not_found"
        elif operation == "read_pin":
            try:
                if file_size >= 0xB10:
                    b1, b2, b3, b4 = file_bytes[0xB00], file_bytes[0xB01], file_bytes[0xB02], file_bytes[0xB03]
                    if b1 == 0x11 and b2 == 0x11 and b3 == 0x11 and b4 == 0x11: server_code = "err_already_off"
                    else: extracted_pin = f"{chr(b4)}{chr(b3)}{chr(b2)}{chr(b1)}"; server_code = "success_pin"; is_error_css = False
                else: server_code = "err_sid_not_found"
            except: server_code = "err_corrupted"
       # --- عقول Delphi DCM3.5 التعديل الصارم للسطر بالكامل وقراءة البين كود الطبيعي ---
    elif ecu_key == "dcm35_psa":
        if file_size != 8192:
            server_code = "err_size_dcm35"
        elif operation == "immo_off":
            if file_size >= 0x00B0:
                # يغير السطر 0x00A0 بالكامل (16 خانة بالتحديد من 00 إلى 0F) دون أي إزاحة في حجم الملف
                file_bytes[0x00A0:0x00B0] = b"\x0A\x40\x11\x11\x11\x11\x81\x00\x00\x6C\x70\x07\x00\x78\xB3\x8A"
                filename_out = "DELPHI_DCM35_IMMO_OFF_" + original_filename
                should_download = True; is_error_css = False
            else: 
                server_code = "err_corrupted"
        elif operation == "read_pin":
            try:
                if file_size >= 0x00B0:
                    # الكود بين يوجد في الخانات من 02 إلى 05 في نفس السطر ويقرأ بالترتيب الطبيعي 1.2.3.4
                    b1 = file_bytes[0x00A2]
                    b2 = file_bytes[0x00A3]
                    b3 = file_bytes[0x00A4]
                    b4 = file_bytes[0x00A5]
                    if all(32 <= x <= 126 for x in [b1, b2, b3, b4]):
                        extracted_pin = f"{chr(b1)}{chr(b2)}{chr(b3)}{chr(b4)}"
                        server_code = "success_pin"; is_error_css = False
                    else:
                        server_code = "err_corrupted"
                else: 
                    server_code = "err_corrupted"
            except:
                server_code = "err_corrupted"

    return server_code, extracted_pin, is_error_css, filename_out, file_bytes, should_download
# =========================================================================
# 🔒 بوابات حماية السحابة ونظام المشتركين (المدمج بحظر التخمين عند 15 محاولة)
# =========================================================================
from flask import session, redirect

# 👥 قاعدة بيانات الحسابات المصرح لها بالولوج (يمكنك إضافة حسابات عملائك هنا)
USERS_DATABASE = {
    "abdu": {"password": "20130310d", "status": "active"},     # حسابك الشخصي كمطور
    "user1": {"password": "Demo account", "status": "active"}, # حساب عميل صاحب ورشة
    "user2": {"password": "Expired account", "status": "expired"} # حساب منتهي الصلاحية مقفل
}

# قالب صفحة تسجيل الدخول المستقبلية الفخمة المحدث بنظام الحظر والتأمين
LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>تسجيل الدخول | ImmoEcu Cloud</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: linear-gradient(135deg, #060b19 0%, #0e1726 100%); color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .login-box { background: rgba(27, 46, 75, 0.65); max-width: 400px; width: 100%; padding: 40px; border-radius: 16px; box-shadow: 0px 15px 40px rgba(0,0,0,0.6); backdrop-filter: blur(12px); border: 1px solid rgba(0, 184, 255, 0.2); text-align: center; }
        h2 { color: #00b8ff; font-size: 26px; font-weight: 800; text-shadow: 0 0 10px rgba(0, 184, 255, 0.3); margin-bottom: 25px; }
        input, button { width: 100%; padding: 14px; margin: 10px 0; border-radius: 8px; box-sizing: border-box; font-size: 15px; outline: none; }
        input { background: #060b19; color: #fff; border: 1px solid #3b3f5c; text-align: center; font-weight: 500; transition: border 0.2s; }
        input:focus { border-color: #00b8ff; }
        button { background: linear-gradient(135deg, #00e676 0%, #00c853 100%); color: #060b19; border: none; font-weight: 700; cursor: pointer; text-transform: uppercase; box-shadow: 0 4px 15px rgba(0, 230, 118, 0.2); }
        button:hover { background: linear-gradient(135deg, #00ff87 0%, #00e676 100%); }
        .error-msg { background: rgba(255, 23, 68, 0.15); color: #ff5252; padding: 12px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 14px; border: 1px solid rgba(255, 23, 68, 0.3); }
        .lock-msg { background: rgba(255, 152, 0, 0.15); color: #ff9800; padding: 15px; border-radius: 8px; margin-bottom: 20px; font-weight: bold; font-size: 15px; border: 1px solid rgba(255, 152, 0, 0.3); line-height: 1.5; }
    </style>
</head>
<body>
    <div class="login-box">
        <h2>🔒 ImmoEcu Portal Access</h2>
        
        {% if locked %}
            <!-- شاشة الحظر الصارمة التي تظهر بعد 15 محاولة خاطئة -->
            <div class="lock-msg">{{ error }}</div>
            <p style="color: #888ea8; font-size: 13px;">تم تعليق الدخول مؤقتاً لحماية المنصة السحابية.</p>
        {% else %}
            {% if error %}
                <div class="error-msg">{{ error }}</div>
            {% endif %}
            <form method="POST" action="/login">
                <input type="text" name="username" placeholder="اسم المستخدم / Username" required autocomplete="off">
                <input type="password" name="password" placeholder="كلمة المرور / Password" required>
                <button type="submit">تسجيل الدخول الآمن 🚀</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    # تهيئة عداد المحاولات الخاطئة في الجلسة إذا لم يكن موجوداً مسبقاً
    if "login_attempts" not in session:
        session["login_attempts"] = 0

    # التحقق الفوري: إذا بلغ المستخدم 15 محاولة خاطئة أو أكثر، يتم حظره مباشرة
    if session["login_attempts"] >= 15:
        return render_template_string(
            LOGIN_TEMPLATE, 
            error="⚠️ لقد تجاوزت الحد الأقصى للمحاولات الخاطئة (15 محاولة)! يرجى المحاولة لاحقاً.", 
            locked=True
        )

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        if username in USERS_DATABASE:
            user_data = USERS_DATABASE[username]
            if user_data["password"] == password:
                if user_data["status"] == "active":
                    # تصفير العداد فور تسجيل الدخول الناجح لضمان مرونة الحساب المستقبلي
                    session["login_attempts"] = 0
                    session["cloud_logged_in"] = True
                    session["cloud_user"] = username
                    return redirect("/")
                else:
                    return render_template_string(LOGIN_TEMPLATE, error="❌ الحساب منتهي الصلاحية! يرجى تجديد الاشتراك.", locked=False)
        
        # زيادة العداد بمقدار 1 عند كل إدخال خاطئ لبيانات الاعتماد
        session["login_attempts"] += 1
        remaining = 15 - session["login_attempts"]
        
        if session["login_attempts"] >= 15:
            return render_template_string(
                LOGIN_TEMPLATE, 
                error="⚠️ لقد تجاوزت الحد الأقصى للمحاولات الخاطئة (15 محاولة)! يرجى المحاولة لاحقاً.", 
                locked=True
            )
        else:
            return render_template_string(
                LOGIN_TEMPLATE, 
                error=f"❌ بيانات الدخول خاطئة! متبقي لديك {remaining} محاولات قبل الحظر.", 
                locked=False
            )
            
    return render_template_string(LOGIN_TEMPLATE, error=None, locked=False)

@app.route("/logout")
def logout():
    session.pop("cloud_logged_in", None)
    session.pop("cloud_user", None)
    return redirect("/login")

@app.route("/", methods=["GET"])
def index():
    if not session.get("cloud_logged_in"):
        return redirect("/login")
    return render_template_string(INDEX_TEMPLATE)

@app.route("/hex_viewer", methods=["GET"])
def hex_viewer():
    if not session.get("cloud_logged_in"):
        return redirect("/login")
    return render_template_string(HEX_VIEW_TEMPLATE)

@app.route("/immo_tool", methods=["GET", "POST"])
def immo_tool():
    if not session.get("cloud_logged_in"):
        return redirect("/login")
        
    if request.method == "GET":
        return render_template_string(IMMO_TEMPLATE + JAVASCRIPT_TEMPLATE_1 + JAVASCRIPT_TEMPLATE_2, database=ECU_DATABASE)

    if request.method == "POST":
        if "dump_file" not in request.files:
            return jsonify({"is_error": True, "code": "err_empty"})
        file = request.files["dump_file"]
        if file.filename == "":
            return jsonify({"is_error": True, "code": "err_empty"})

        ecu_key = request.form.get('ecu_type')
        operation = request.form.get('operation')

        if file and ecu_key in ECU_DATABASE:
            file_bytes = bytearray(file.read())
            if len(file_bytes) == 0:
                return jsonify({"is_error": True, "code": "err_empty"})
            
            server_code, extracted_pin, is_error_css, filename_out, file_bytes, should_download = process_ecu_file(
                file_bytes, len(file_bytes), ecu_key, operation, file.filename
            )

            if should_download:
                f_io = io.BytesIO(file_bytes)
                return send_file(f_io, mimetype="application/octet-stream", as_attachment=True, download_name=filename_out)
            
            return jsonify({
                "is_error": is_error_css,
                "code": server_code,
                "pin": extracted_pin
            })

        return jsonify({"is_error": True, "code": "err_corrupted"})

if __name__ == "__main__":
    threading.Timer(1.2, lambda: webbrowser.open("http://localhost:5000/login")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)

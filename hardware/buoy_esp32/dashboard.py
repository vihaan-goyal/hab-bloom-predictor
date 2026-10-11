"""
dashboard.py -- live readings from the ESP32 buoy in a browser tab
------------------------------------------------------------------
Owns the serial port, asks the board for a reading every few seconds, and serves one page:

    python dashboard.py --port COM7          then open  http://localhost:8765

Only one program can hold a serial port, so while this runs send commands through it:
    the box on the page, or   curl -X POST --data "status" http://localhost:8765/cmd
Close the Arduino Serial Monitor first. Opening the port restarts the board (about 8 s).

Parses the firmware's lines (buoy_esp32.ino):
    S temp=.. cond_mScm=.. sal=.. ph=.. ph_v=.. fl=.. chl=..      one sample
    P <date> p=0.123456 ALERT|idle n=..                           one forecast
    MSG <title> | <text>                                          a harbor bulletin
    ... state=ALERT relay=ON ...                                  from `status`
"""
import argparse
import json
import math
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import serial

KEEP = 300          # samples kept for the charts
ADC_TOP = 3.05      # volts: at or above this the pH pin is at the top of its range

state = {"connected": False, "error": "", "relay": "?", "alert": "?", "last_p": None,
         "history": "?", "clock": "?", "selftest": "?", "started": time.time()}
samples = deque(maxlen=KEEP)
log = deque(maxlen=250)
lock = threading.Lock()
outbox = deque()
quiet = {"until": 0.0}   # the automatic `status` replies update the header but stay out of the log


def num(text):
    try:
        v = float(text)
        return None if math.isnan(v) else v
    except (TypeError, ValueError):
        return None


def parse(line):
    """Update the shared state from one line the board printed."""
    if line.startswith("S "):
        kv = dict(tok.split("=", 1) for tok in line.split()[1:] if "=" in tok)
        samples.append({"t": time.time(), **{k: num(v) for k, v in kv.items()}})
        return
    if line.startswith("F "):
        return                      # the 23 feature values: too long for the log
    if line.startswith("P "):
        parts = line.split()
        if len(parts) >= 4:
            state["last_p"] = num(parts[2].split("=", 1)[-1])
            state["alert"] = parts[3]
    for key, field in (("state=", "alert"), ("relay=", "relay"), ("history=", "history"),
                       ("clock=", "clock"), ("selftest=", "selftest")):
        if key in line:
            state[field] = line.split(key, 1)[1].split()[0]
    if "SELFTEST PASS" in line:
        state["selftest"] = "PASS"
    if time.time() < quiet["until"] and line.startswith(("site=", "clim ", "cal ", "sensors:", "wifi ")):
        return
    log.append({"t": time.time(), "line": line[:400]})


def serial_loop(port, poll):
    while True:
        try:
            with serial.Serial(port, 115200, timeout=0.2) as s:
                with lock:
                    state.update(connected=True, error="")
                    log.append({"t": time.time(), "line": f"-- connected to {port} (the board restarts now) --"})
                next_read, next_status = time.time() + 9, time.time() + 10
                while True:
                    raw = s.readline().decode(errors="replace").strip()
                    if raw:
                        with lock:
                            parse(raw)
                    now = time.time()
                    while outbox:
                        cmd = outbox.popleft()
                        s.write((cmd + "\n").encode())
                        with lock:
                            log.append({"t": now, "line": f">> {cmd}"})
                    if poll > 0 and now >= next_read:
                        s.write(b"read\n")
                        next_read = now + poll
                    if now >= next_status:
                        s.write(b"status\n")
                        quiet["until"] = now + 1.5
                        next_status = now + 10
        except (serial.SerialException, OSError) as e:
            with lock:
                state.update(connected=False, error=str(e)[:160])
            time.sleep(2)


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Buoy live readings</title>
<style>
:root{--bg:#f3f5f6;--card:#fff;--ink:#16202a;--dim:#5d6b78;--line:#d9e0e5;--ok:#0f7b54;--warn:#b25a00;--bad:#b3261e;--acc:#0b6e8f}
@media (prefers-color-scheme:dark){:root{--bg:#10161b;--card:#18212a;--ink:#e6edf2;--dim:#93a3b1;--line:#2a3742;--ok:#4cc38a;--warn:#f0a44b;--bad:#ff7b72;--acc:#5ab8d8}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1100px;margin:0 auto;padding:16px}
header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;margin-bottom:12px}
h1{font-size:19px;margin:0}.pill{padding:2px 10px;border-radius:99px;font-size:13px;font-weight:600;border:1px solid var(--line)}
.grid{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(215px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.k{font-size:12px;color:var(--dim);text-transform:uppercase;letter-spacing:.05em}
.v{font-size:30px;font-weight:650;font-variant-numeric:tabular-nums;line-height:1.2}.u{font-size:14px;color:var(--dim);font-weight:400}
.n{font-size:12.5px;color:var(--dim);min-height:18px}.n.warn{color:var(--warn);font-weight:600}.n.bad{color:var(--bad);font-weight:600}
canvas{width:100%;height:46px;display:block;margin-top:6px}
#log{font:12px/1.5 ui-monospace,Consolas,monospace;height:230px;overflow:auto;white-space:pre-wrap;word-break:break-word;margin:8px 0 0}
form{display:flex;gap:8px;margin-top:8px;flex-wrap:wrap}input{flex:1;min-width:160px;padding:7px 10px;border:1px solid var(--line);border-radius:7px;background:var(--bg);color:var(--ink);font:inherit}
button{padding:7px 14px;border:1px solid var(--line);border-radius:7px;background:var(--acc);color:#fff;font:inherit;font-weight:600;cursor:pointer}
button.q{background:var(--card);color:var(--ink);font-weight:400}
</style></head><body><main>
<header><h1>Buoy live readings</h1><span id="conn" class="pill">connecting</span><span id="alert" class="pill">forecast ?</span><span id="relay" class="pill">relay ?</span><span id="meta" class="n"></span></header>
<div class="grid" id="tiles"></div>
<div class="card" style="margin-top:12px"><div class="k">Board log</div><div id="log"></div>
<form id="f"><input id="c" placeholder="command, e.g. status, read, blank, reset" autocomplete="off"><button>Send</button>
<button type="button" class="q" data-c="status">status</button><button type="button" class="q" data-c="read">read</button></form></div>
</main><script>
const TILES=[["temp","Temperature","°C",2],["ph_v","pH pin voltage","V",3],["ph","pH","",2],["fl","Light signal (LED on − off)","counts",1],["chl","Chlorophyll","µg/L",2],["sal","Salinity","",2]];
const NOTE={ph:"needs the two buffers (cal686, cal918)",chl:"needs blank + chlk calibration",sal:"no conductivity sensor wired"};
const box=document.getElementById("tiles");
for(const [k,name,unit] of TILES){box.insertAdjacentHTML("beforeend",`<div class="card"><div class="k">${name}</div><div class="v"><span id="v_${k}">–</span> <span class="u">${unit}</span></div><div class="n" id="n_${k}"></div><canvas id="g_${k}" width="400" height="92"></canvas></div>`)}
function spark(id,vals){const c=document.getElementById(id),x=c.getContext("2d"),w=c.width,h=c.height;x.clearRect(0,0,w,h);
 const v=vals.filter(a=>a!==null);if(v.length<2)return;let lo=Math.min(...v),hi=Math.max(...v);if(hi-lo<1e-9){hi+=1;lo-=1}
 const css=getComputedStyle(document.documentElement);x.strokeStyle=css.getPropertyValue("--acc");x.lineWidth=3;x.beginPath();let pen=false;
 vals.forEach((a,i)=>{if(a===null){pen=false;return}const px=i/(vals.length-1)*(w-6)+3,py=h-6-(a-lo)/(hi-lo)*(h-12);pen?x.lineTo(px,py):x.moveTo(px,py);pen=true});x.stroke();
 x.fillStyle=css.getPropertyValue("--dim");x.font="20px system-ui";x.fillText(hi.toPrecision(4),4,20);x.fillText(lo.toPrecision(4),4,h-4)}
function pill(id,text,kind){const e=document.getElementById(id);e.textContent=text;e.style.color=`var(--${kind})`;e.style.borderColor=`var(--${kind})`}
async function tick(){let d;try{d=await (await fetch("/data")).json()}catch(e){pill("conn","dashboard stopped","bad");return}
 const s=d.state,last=d.samples.at(-1),age=last?(d.now-last.t):null;
 pill("conn",s.connected?(age!==null&&age<15?"board connected":"connected, waiting for a reading"):"board not connected",s.connected?"ok":"bad");
 pill("alert","forecast "+(s.alert||"?")+(s.last_p!==null?` (p ${s.last_p.toFixed(2)})`:""),s.alert==="ALERT"?"bad":"ok");
 pill("relay","relay "+s.relay,s.relay==="ON"?"warn":"ok");
 document.getElementById("meta").textContent=`self-test ${s.selftest} · stored days ${s.history} · clock ${s.clock}`+(s.error?` · ${s.error}`:"")+(age!==null?` · last reading ${age.toFixed(0)} s ago`:"");
 for(const [k,,,dp] of TILES){const v=last?last[k]:null,n=document.getElementById("n_"+k);
  document.getElementById("v_"+k).textContent=v===null||v===undefined?"–":v.toFixed(dp);
  n.className="n";n.textContent=v===null||v===undefined?(NOTE[k]||"no reading"):"";
  if(k==="ph_v"&&v!==null&&v!==undefined&&v>=d.adc_top){n.className="n bad";n.textContent="AT THE TOP OF THE RANGE: check the voltage divider"}
  spark("g_"+k,d.samples.map(a=>a[k]??null))}
 const L=document.getElementById("log"),stick=L.scrollTop+L.clientHeight>=L.scrollHeight-8;
 L.textContent=d.log.map(a=>new Date(a.t*1000).toLocaleTimeString()+"  "+a.line).join("\n");if(stick)L.scrollTop=L.scrollHeight}
async function send(c){if(c)await fetch("/cmd",{method:"POST",body:c})}
document.getElementById("f").addEventListener("submit",e=>{e.preventDefault();const i=document.getElementById("c");send(i.value.trim());i.value=""});
document.querySelectorAll("button[data-c]").forEach(b=>b.addEventListener("click",()=>send(b.dataset.c)));
tick();setInterval(tick,1000);
</script></body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, kind):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path.startswith("/data"):
            with lock:
                body = json.dumps({"now": time.time(), "adc_top": ADC_TOP, "state": state,
                                   "samples": list(samples), "log": list(log)})
            self._send(200, body, "application/json")
        else:
            self._send(200, PAGE, "text/html; charset=utf-8")

    def do_POST(self):
        cmd = self.rfile.read(int(self.headers.get("Content-Length", 0))).decode(errors="replace").strip()
        if self.path.startswith("/cmd") and cmd and "\n" not in cmd and len(cmd) < 200:
            outbox.append(cmd)
            self._send(200, "ok", "text/plain")
        else:
            self._send(400, "bad command", "text/plain")

    def log_message(self, *args):
        pass


def main():
    ap = argparse.ArgumentParser(description="Live browser dashboard for the ESP32 buoy.")
    ap.add_argument("--port", required=True, help="serial port of the ESP32, e.g. COM7")
    ap.add_argument("--http", type=int, default=8765, help="port of the web page")
    ap.add_argument("--poll", type=float, default=3.0, help="seconds between `read` requests (0 = only the board's own samples)")
    a = ap.parse_args()
    threading.Thread(target=serial_loop, args=(a.port, a.poll), daemon=True).start()
    print(f"dashboard: http://localhost:{a.http}   (serial {a.port}, a reading every {a.poll:g} s)")
    ThreadingHTTPServer(("127.0.0.1", a.http), Handler).serve_forever()


if __name__ == "__main__":
    main()

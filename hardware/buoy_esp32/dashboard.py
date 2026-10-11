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

KEEP = 1800         # samples kept for the charts (an hour at one reading every 2 s)
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
                            shown = "wifipass ****" if cmd.split(" ")[0] == "wifipass" else cmd   # never log a password
                            log.append({"t": now, "line": f">> {shown}"})
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
.tile{cursor:pointer}.tile:hover{border-color:var(--acc)}
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
for(const [k,name,unit] of TILES){box.insertAdjacentHTML("beforeend",`<div class="card tile" title="Open a large chart in a new tab" onclick="window.open('/detail?k=${k}','_blank')"><div class="k">${name} ↗</div><div class="v"><span id="v_${k}">–</span> <span class="u">${unit}</span></div><div class="n" id="n_${k}"></div><canvas id="g_${k}" width="400" height="92"></canvas></div>`)}
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


DETAIL = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Buoy reading detail</title>
<style>
:root{--bg:#f3f5f6;--card:#fff;--ink:#16202a;--dim:#5d6b78;--line:#d9e0e5;--grid:#e6ebef;--acc:#0b6e8f;--ref:#b25a00}
@media (prefers-color-scheme:dark){:root{--bg:#10161b;--card:#18212a;--ink:#e6edf2;--dim:#93a3b1;--line:#2a3742;--grid:#222d37;--acc:#5ab8d8;--ref:#f0a44b}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,Arial,sans-serif}
main{max-width:1500px;margin:0 auto;padding:16px}h1{font-size:19px;margin:0}
.top{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:baseline;margin-bottom:10px}
.v{font-size:40px;font-weight:650;font-variant-numeric:tabular-nums}.u{font-size:16px;color:var(--dim);font-weight:400}
.st{font-size:13.5px;color:var(--dim);font-variant-numeric:tabular-nums}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px}
canvas{width:100%;height:70vh;min-height:360px;display:block}
.b{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0 0}
button{padding:6px 12px;border:1px solid var(--line);border-radius:7px;background:var(--card);color:var(--ink);font:inherit;cursor:pointer}
button.on{background:var(--acc);color:#fff;border-color:var(--acc);font-weight:600}
</style></head><body><main>
<div class="top"><h1 id="h">Reading</h1><div class="v"><span id="v">–</span> <span class="u" id="u"></span></div><div class="st" id="st"></div></div>
<div class="card"><canvas id="c"></canvas></div>
<div class="b" id="b"></div>
</main><script>
const META={temp:["Temperature","°C",2],ph_v:["pH pin voltage","V",3],ph:["pH","",2],fl:["Light signal (LED on − off)","counts",1],chl:["Chlorophyll","µg/L",2],sal:["Salinity","",2]};
const K=new URLSearchParams(location.search).get("k")||"ph_v",M=META[K]||[K,"",3];
const REF=K==="ph_v"?[[1.25,"centring target 1.25 V"]]:[];
let win=120;document.title=M[0]+" detail";document.getElementById("h").textContent=M[0];document.getElementById("u").textContent=M[1];
const B=document.getElementById("b");for(const [s,l] of [[60,"1 min"],[120,"2 min"],[300,"5 min"],[900,"15 min"],[0,"all"]]){const e=document.createElement("button");e.textContent=l;if(s===win)e.className="on";e.onclick=()=>{win=s;[...B.children].forEach(x=>x.className="");e.className="on";tick()};B.appendChild(e)}
function nice(span,n){const raw=span/n,p=Math.pow(10,Math.floor(Math.log10(raw))),f=raw/p;return (f<1.5?1:f<3?2:f<7?5:10)*p}
function draw(pts,now){const c=document.getElementById("c"),r=devicePixelRatio||1,W=c.clientWidth,H=c.clientHeight;c.width=W*r;c.height=H*r;const x=c.getContext("2d");x.scale(r,r);
 const css=getComputedStyle(document.documentElement),col=n=>css.getPropertyValue(n).trim(),L=64,R=14,T=12,Bm=34;x.clearRect(0,0,W,H);x.font="12px system-ui";
 if(pts.length<2){x.fillStyle=col("--dim");x.fillText("waiting for readings",L,H/2);return}
 const t1=now,t0=win?now-win:pts[0][0];let lo=Math.min(...pts.map(p=>p[1]),...REF.map(q=>q[0])),hi=Math.max(...pts.map(p=>p[1]),...REF.map(q=>q[0]));
 if(hi-lo<1e-6){hi+=.5;lo-=.5}const pad=(hi-lo)*.08;lo-=pad;hi+=pad;const ys=nice(hi-lo,12);lo=Math.floor(lo/ys)*ys;hi=Math.ceil(hi/ys)*ys;
 const X=t=>L+(t-t0)/(t1-t0)*(W-L-R),Y=v=>T+(hi-v)/(hi-lo)*(H-T-Bm),dp=Math.max(0,Math.min(4,Math.ceil(-Math.log10(ys))+(Math.abs(ys/Math.pow(10,Math.floor(Math.log10(ys)))-1)>1e-9&&ys<1?0:0)));
 x.lineWidth=1;x.textBaseline="middle";x.textAlign="right";
 for(let v=lo;v<=hi+ys/2;v+=ys){x.strokeStyle=col("--grid");x.beginPath();x.moveTo(L,Y(v));x.lineTo(W-R,Y(v));x.stroke();x.fillStyle=col("--dim");x.fillText(v.toFixed(dp),L-8,Y(v))}
 const span=t1-t0,xs=[1,2,5,10,15,30,60,120,300,600,1800].find(s=>span/s<=14)||3600;x.textAlign="center";x.textBaseline="top";
 for(let t=Math.ceil(t0/xs)*xs;t<=t1;t+=xs){x.strokeStyle=col("--grid");x.beginPath();x.moveTo(X(t),T);x.lineTo(X(t),H-Bm);x.stroke();x.fillStyle=col("--dim");x.fillText(new Date(t*1000).toLocaleTimeString([], {hour12:false}),X(t),H-Bm+8)}
 x.strokeStyle=col("--line");x.strokeRect(L,T,W-L-R,H-T-Bm);
 for(const [v,label] of REF){x.strokeStyle=col("--ref");x.setLineDash([6,5]);x.beginPath();x.moveTo(L,Y(v));x.lineTo(W-R,Y(v));x.stroke();x.setLineDash([]);x.fillStyle=col("--ref");x.textAlign="left";x.textBaseline="bottom";x.fillText(label,L+8,Y(v)-4)}
 x.save();x.beginPath();x.rect(L,T,W-L-R,H-T-Bm);x.clip();x.strokeStyle=col("--acc");x.lineWidth=2;x.beginPath();pts.forEach((p,i)=>i?x.lineTo(X(p[0]),Y(p[1])):x.moveTo(X(p[0]),Y(p[1])));x.stroke();
 x.fillStyle=col("--acc");for(const p of pts){x.beginPath();x.arc(X(p[0]),Y(p[1]),2.6,0,7);x.fill()}x.restore()}
async function tick(){let d;try{d=await (await fetch("/data")).json()}catch(e){document.getElementById("st").textContent="dashboard stopped";return}
 const all=d.samples.filter(a=>a[K]!==null&&a[K]!==undefined).map(a=>[a.t,a[K]]),pts=win?all.filter(p=>p[0]>=d.now-win):all,last=all.at(-1);
 document.getElementById("v").textContent=last?last[1].toFixed(M[2]):"–";
 if(pts.length){const v=pts.map(p=>p[1]),mean=v.reduce((a,b)=>a+b,0)/v.length,rec=pts.filter(p=>p[0]>=d.now-30),drift=rec.length>1?(rec.at(-1)[1]-rec[0][1])/Math.max(1,rec.at(-1)[0]-rec[0][0])*60:0;
  document.getElementById("st").textContent=`${pts.length} readings · min ${Math.min(...v).toFixed(M[2])} · max ${Math.max(...v).toFixed(M[2])} · mean ${mean.toFixed(M[2])} · change over the last 30 s: ${(drift>=0?"+":"")+drift.toFixed(M[2])} ${M[1]} per minute · last reading ${Math.max(0,d.now-last[0]).toFixed(0)} s ago`}
 else document.getElementById("st").textContent=d.state.connected?"no readings of this sensor yet":"board not connected";
 draw(pts,d.now)}
tick();setInterval(tick,1000);addEventListener("resize",tick);
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
        elif self.path.startswith("/detail"):
            self._send(200, DETAIL, "text/html; charset=utf-8")
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

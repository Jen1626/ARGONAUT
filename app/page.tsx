"use client";
import {useEffect,useState} from "react";
import Link from "next/link";
import OceanBackground from "../components/OceanBackground";
import Plot from "../components/Plot";
import {getApi} from "../lib/api";

type Dash=any;

export default function Home(){
 const [logged,setLogged]=useState(false);
 const [user,setUser]=useState("");
 const [pass,setPass]=useState("");
 const [dash,setDash]=useState<Dash|null>(null);
 const [message,setMessage]=useState("");
 const [answer,setAnswer]=useState("");
 const [charts,setCharts]=useState<any>({});
 const [loading,setLoading]=useState(false);
 const [toast,setToast]=useState("");
 const [today,setToday]=useState("");

 useEffect(()=>{setLogged(localStorage.getItem("argo-auth")==="1");setToday(new Date().toLocaleDateString(undefined,{weekday:"long",month:"short",day:"numeric"}));getApi("/dashboard").then(setDash).catch(()=>{})},[]);

 function login(asGuest:boolean=false){
   if((user==="admin"&&pass==="argo123")||asGuest){localStorage.setItem("argo-auth","1");setLogged(true)}
   else {setToast("Demo login: admin / argo123")}
 }
 async function ask(){
   if(!message.trim())return;
   setLoading(true);
   try{const d=await getApi("/chat",{method:"POST",body:JSON.stringify({message})});setAnswer(d.answer);setCharts(d.charts||{});}
   catch(e:any){setAnswer(e.message)} finally{setLoading(false)}
 }
 if(!logged)return <div className="login"><OceanBackground/><div className="login-overlay"/><div className="login-card">
   <div className="logo-mark">≋</div><div className="logo-name">ARGONAUT <b>AI</b></div><p className="login-sub">Ocean Intelligence • ARGO Data Discovery</p>
   <h1>Explore the ocean.</h1><p className="login-copy">Ask questions, discover autonomous floats, and turn ocean observations into insight.</p>
   <input value={user} onChange={e=>setUser(e.target.value)} placeholder="Username"/>
   <div className="password"><input type="password" value={pass} onChange={e=>setPass(e.target.value)} placeholder="Password"/><span>◉</span></div>
   <button className="login-btn" onClick={()=>login(false)}>Sign in to ARGONAUT</button>
   <div className="or"><i/> OR <i/></div>
   <button className="social google" onClick={()=>login(true)}>Continue with Google</button>
   <button className="social linkedin" onClick={()=>login(true)}>Continue with LinkedIn</button>
   <button className="guest" onClick={()=>login(true)}>Continue as Guest →</button>
   {toast&&<div className="toast">{toast}</div>}
   <small>Demo access • No account required</small>
 </div></div>;

 return <div className="app-shell">
   <aside className="nav">
    <div className="nav-logo"><div className="mini-logo">≋</div><div><b>ARGONAUT <span>AI</span></b><small>Ocean Intelligence</small></div></div>
    <div className="nav-section">WORKSPACE</div>
    <Link className="nav-active" href="/">⌂ <span>Command Center</span></Link>
    <Link href="/explorer">◎ <span>Float Explorer</span></Link>
    <Link href="/visualization">◈ <span>Data Visualization</span></Link>
    <Link href="/trajectory">⌁ <span>Live Trajectories</span></Link>
    <div className="nav-section">DISCOVER</div>
    <button onClick={()=>setMessage("Show temperature and salinity profiles in the Arabian Sea")}>✦ <span>Ocean AI</span></button>
    <button onClick={()=>setMessage("What are the nearest ARGO floats to 12N, 64E?")}>⌖ <span>Nearest Float</span></button>
    <Link href="/help">? <span>Documentation</span></Link>
    <div className="nav-bottom"><div className="online-dot"/> ARGO network online<div className="profile"><b>Demo User</b><small>Research workspace</small></div></div>
   </aside>
   <main className="dashboard">
    <header className="topbar"><div><span className="live-pill"><i/> {dash?.mode==="demo"?"DEMO NETWORK":"LIVE DATA"}</span><span className="crumb"> / Command Center</span></div><button onClick={()=>{localStorage.removeItem("argo-auth");location.reload()}}>Sign out</button></header>
    <section className="welcome"><div><p className="eyebrow">OCEAN INTELLIGENCE PLATFORM</p><h1>Good to see you, <em>Researcher.</em></h1><p>Ask ARGONAUT anything about the world's autonomous ocean observing network.</p></div><div className="date-chip">◷ {today || "Today"}</div></section>
    <section className="metrics">
      <Metric icon="◉" value={dash?.active_floats??"—"} label="Active Floats" sub="Global network"/>
      <Metric icon="≈" value={dash?`${dash.ocean_temperature}°C`:"—"} label="Surface Temp." sub="Network average"/>
      <Metric icon="≋" value={dash?.salinity??"—"} label="Avg. Salinity" sub="PSU"/>
      <Metric icon="◈" value={dash?`${dash.coverage}%`:"—"} label="Data Coverage" sub="Last 30 days"/>
    </section>
    <section className="workspace">
      <div className="query-panel"><div className="panel-title"><span className="ai-orb">✦</span><div><b>Ocean AI</b><small>Natural-language data analyst</small></div><span className="ready">READY</span></div>
       <div className="query-box"><textarea value={message} onChange={e=>setMessage(e.target.value)} placeholder="Ask a question about the ocean...&#10;&#10;Try: “Show me temperature profiles in the Arabian Sea”"/><button onClick={ask} disabled={loading}>{loading?"PROCESSING":"RUN ANALYSIS  →"}</button></div>
       <div className="quick"><span>Try:</span>{["Temperature in Arabian Sea","Salinity profiles","Float 4903775","Nearest to 12N, 64E"].map(x=><button key={x} onClick={()=>setMessage(x)}>{x}</button>)}</div>
       {answer&&<div className="ai-answer"><span>AI RESULT</span><p>{answer}</p>{Object.entries(charts).slice(0,2).map(([k,v]:any)=><div className="mini-chart" key={k}><h4>{k.replaceAll("_"," ")}</h4><Plot type={k} points={v}/></div>)}</div>}
      </div>
      <div className="network-panel"><div className="panel-title"><div><b>Network Pulse</b><small>Current observation activity</small></div><span className="green">● {dash?.mode==="demo"?"DEMO":"LIVE"}</span></div><div className="pulse"><div className="pulse-ring">🌊<small>ARGO</small></div><div className="pulse-lines"><span style={{width:"86%"}}/><span style={{width:"63%"}}/><span style={{width:"74%"}}/><span style={{width:"48%"}}/></div></div><div className="region-list">{(dash?.regions||[]).map((r:any)=><div key={r.name}><span>{r.name}</span><b>{r.value}%</b><i><u style={{width:`${r.value}%`}}/></i></div>)}</div></div>
    </section>
    <section className="recent"><div className="section-head"><div><p className="eyebrow">NETWORK ACTIVITY</p><h2>Recent float observations</h2></div><Link href="/explorer">View all floats →</Link></div><div className="float-grid">{(dash?.recent||[]).map((r:any)=><div className="float-card" key={r.wmo}><div className="float-icon">●</div><div><b>{r.wmo}</b><small>{r.region}</small></div><div className="float-temp">{r.temp}</div><span className="live-dot">{r.status}</span></div>)}</div></section>
   </main>
 </div>
}

function Metric({icon,value,label,sub}:{icon:string,value:any,label:string,sub:string}){return <div className="metric"><div className="metric-icon">{icon}</div><div><strong>{value}</strong><b>{label}</b><small>{sub}</small></div></div>}

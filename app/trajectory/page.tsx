"use client";
import dynamic from "next/dynamic";import {useState} from "react";import Link from "next/link";import {getApi} from "../../lib/api";
const Map=dynamic(()=>import("../../components/Map"),{ssr:false});
export default function Trajectory(){
 const[wmo,setWmo]=useState("7901136"),[pts,setPts]=useState<any[]>([]);
 async function run(){setPts((await getApi(`/float/${wmo}/trajectory`)).points)}
 return <div className="inner"><header className="topbar"><Link href="/">← Command Center</Link><span className="live-pill"><i/> ARGO NETWORK</span></header><div className="page-title"><p className="eyebrow">LIVE FLOAT TRACKING</p><h1>Trajectory Intelligence</h1><p>Follow the surface path of an autonomous ARGO float by cycle.</p></div><div className="tool-row"><input value={wmo} onChange={e=>setWmo(e.target.value)}/><button className="login-btn compact" onClick={run}>Track Float →</button></div><div className="map-panel"><Map points={pts}/></div></div>
}

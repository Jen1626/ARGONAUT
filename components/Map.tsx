"use client";
import "leaflet/dist/leaflet.css";
import {MapContainer,TileLayer,Polyline,CircleMarker,Tooltip} from "react-leaflet";
export default function Map({points}:{points:any[]}){
 if(!points.length)return <div className="no-data">No trajectory data.</div>;
 const center:[number,number]=[points.reduce((a,p)=>a+p.latitude,0)/points.length,points.reduce((a,p)=>a+p.longitude,0)/points.length];
 return <MapContainer center={center} zoom={4} style={{height:440,width:"100%"}}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="© OpenStreetMap contributors"/><Polyline positions={points.map(p=>[p.latitude,p.longitude] as [number,number])}/>{points.map((p,i)=><CircleMarker key={i} center={[p.latitude,p.longitude]} radius={6}><Tooltip>Cycle {p.cycle}</Tooltip></CircleMarker>)}</MapContainer>
}

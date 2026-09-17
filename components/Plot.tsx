"use client";
import {ResponsiveContainer,LineChart,Line,XAxis,YAxis,CartesianGrid,Tooltip,ScatterChart,Scatter} from "recharts";

export default function Plot({type,points}:{type:string,points:any[]}){
 if(!points?.length)return <div className="no-data">No observations for this visualization.</div>;
 if(type==="ts_diagram")return <ResponsiveContainer width="100%" height={330}><ScatterChart margin={{left:5,right:20,top:15,bottom:10}}><CartesianGrid strokeDasharray="3 3" opacity={.15}/><XAxis type="number" dataKey="salinity" name="Salinity"/><YAxis type="number" dataKey="temperature" name="Temperature"/><Tooltip/><Scatter data={points}/></ScatterChart></ResponsiveContainer>;
 const v=type.includes("salinity")?"salinity":type.includes("density")?"density":"temperature";
 const data=points.filter(x=>x[v]!=null).slice(0,1000);
 return <ResponsiveContainer width="100%" height={330}><LineChart data={data} margin={{left:5,right:20,top:15,bottom:10}}><CartesianGrid strokeDasharray="3 3" opacity={.15}/><XAxis dataKey={type.endsWith("section")?"time":v} tick={{fontSize:10}}/><YAxis dataKey="depth" reversed={!type.endsWith("section")} tick={{fontSize:10}}/><Tooltip/><Line type="monotone" dataKey={v} dot={false} strokeWidth={2}/></LineChart></ResponsiveContainer>
}

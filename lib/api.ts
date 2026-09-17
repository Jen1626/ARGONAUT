export const API=process.env.NEXT_PUBLIC_API_URL||"/api";
export async function getApi(path:string, options?:RequestInit){
 const r=await fetch(`${API}${path}`,{...options,headers:{"Content-Type":"application/json",...(options?.headers||{})}});
 const d=await r.json(); if(!r.ok) throw new Error(d.detail||"Request failed"); return d;
}

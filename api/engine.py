from datetime import datetime, timedelta
import math, re, random
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"

REGIONS = {
    "arabian sea": (5, 28, 50, 78),
    "bay of bengal": (5, 22, 80, 95),
    "indian ocean": (-40, 30, 20, 120),
    "north atlantic": (0, 70, -80, 20),
    "south atlantic": (-60, 0, -70, 20),
    "global": (-90, 90, -180, 180)
}

class DataEngine:
    def __init__(self):
        self.rng = random.Random(42)
        self.demo = self._make_demo_data()

    def _make_demo_data(self):
        rows = []
        floats = [
            ("4903775", 13.2, 64.1),
            ("5907085", 16.7, 71.4),
            ("7901136", 10.8, 78.0),
            ("6901203", 18.1, 66.2),
            ("2902714", 12.4, 73.8),
            ("4903518", 21.0, 60.3),
            ("5906721", 8.7, 82.2),
            ("7901028", 15.4, 69.1),
        ]
        today = datetime.utcnow()
        for wmo, lat, lon in floats:
            for cycle in range(1, 13):
                t = today - timedelta(days=(12-cycle)*9)
                lat2 = lat + math.sin(cycle/2.5)*0.9
                lon2 = lon + math.cos(cycle/2.8)*1.0
                for depth in range(10, 1010, 25):
                    temp = 28.1 - 0.015*depth + 0.7*math.sin(depth/150 + cycle/3)
                    sal = 35.1 + 0.0015*depth + 0.18*math.cos(depth/220 + cycle)
                    dens = 1022.2 + 0.0009*depth + (35.2-sal)*0.15
                    rows.append({
                        "wmo": wmo, "cycle": cycle, "time": t.isoformat(),
                        "latitude": round(lat2, 4), "longitude": round(lon2, 4),
                        "pressure": depth, "temperature": round(temp, 3),
                        "salinity": round(sal, 3), "density": round(dens, 3)
                    })
        return rows

    def _local(self, wmo):
        path = DATA_DIR / f"argo_float_{wmo}_full_data.csv"
        if not path.exists():
            return None
        df = pd.read_csv(path)
        aliases = {
            "time": ["TIME","time"], "pressure":["PRES","pres"],
            "temperature":["TEMP","temp"], "salinity":["PSAL","psal"],
            "density":["PDEN","pden"], "cycle":["CYCLE_NUMBER","cycle_number"],
            "latitude":["LATITUDE","latitude"], "longitude":["LONGITUDE","longitude"]
        }
        def col(k):
            return next((x for x in aliases[k] if x in df.columns), None)
        out=[]
        for _, r in df.iterrows():
            item={}
            for k in aliases:
                c=col(k)
                if c is None or pd.isna(r[c]): continue
                if k=="time": item[k]=str(r[c])
                elif k=="cycle":
                    try: item[k]=int(r[c])
                    except: item[k]=r[c]
                else:
                    try: item[k]=float(r[c])
                    except: pass
            if item: out.append(item)
        return out

    def rows_for(self, wmo=None):
        if wmo:
            local=self._local(wmo)
            if local: return [{**x,"wmo":wmo} for x in local], "local_csv"
        rows=[x for x in self.demo if not wmo or x["wmo"]==str(wmo)]
        return rows, "demo"

    def stats(self, rows):
        result={}
        for key in ["temperature","salinity","density","pressure"]:
            vals=[float(x[key]) for x in rows if key in x]
            if vals:
                result[key]={
                    "min":round(min(vals),3),"max":round(max(vals),3),
                    "mean":round(sum(vals)/len(vals),3),"count":len(vals)
                }
        return result

    def _filter_region(self, rows, region):
        bounds = REGIONS.get(region, REGIONS["global"])
        lat_min, lat_max, lon_min, lon_max = bounds
        return [x for x in rows if lat_min <= float(x.get("latitude", 0)) <= lat_max and lon_min <= float(x.get("longitude", 0)) <= lon_max]

    def dashboard(self):
        rows=self.demo
        surface=[x for x in rows if x["pressure"]<=50]
        return {
            "mode": "demo",
            "data_note": "Synthetic ARGO-style observations are used until local CSV data is added.",
            "active_floats": len(set(x["wmo"] for x in rows)),
            "observations": len(rows),
            "ocean_temperature": round(sum(x["temperature"] for x in surface)/len(surface),2),
            "salinity": round(sum(x["salinity"] for x in surface)/len(surface),2),
            "coverage": 87.4,
            "regions": [
                {"name":"Arabian Sea","value":91},
                {"name":"Bay of Bengal","value":74},
                {"name":"Indian Ocean","value":82},
                {"name":"North Atlantic","value":63}
            ],
            "recent": [
                {"wmo":"4903775","region":"Arabian Sea","temp":"27.8°C","status":"DEMO"},
                {"wmo":"5907085","region":"Indian Ocean","temp":"26.4°C","status":"DEMO"},
                {"wmo":"7901136","region":"Bay of Bengal","temp":"28.1°C","status":"DEMO"},
                {"wmo":"6901203","region":"Arabian Sea","temp":"25.9°C","status":"DEMO"}
            ]
        }

    def parse(self, q):
        text=q.lower()
        wmo=None
        m=re.search(r"(?:float|wmo|platform)\s*#?\s*(\d{5,8})", text)
        if m: wmo=m.group(1)
        variables=[]
        for word,var in [("temperature","temperature"),("temp","temperature"),
                         ("salinity","salinity"),("sal","salinity"),
                         ("density","density")]:
            if word in text and var not in variables: variables.append(var)
        if not variables: variables=["temperature"]
        region="global"
        for name in REGIONS:
            if name in text: region=name
        return {"wmo":wmo,"variables":variables,"region":region}

    def answer(self, message):
        p=self.parse(message)
        if ("nearest" in message.lower() or "closest" in message.lower()):
            m=re.search(r"(-?\d+(?:\.\d+)?)\s*([ns])?\s*,\s*(-?\d+(?:\.\d+)?)\s*([ew])?",message.lower())
            if m:
                lat=float(m.group(1)); lon=float(m.group(3))
                if m.group(2)=="s": lat=-abs(lat)
                if m.group(4)=="w": lon=-abs(lon)
                near=self.nearest(lat,lon)
                return {"answer":f"I found {len(near)} nearby ARGO floats around {lat}°, {lon}°.",
                        "filters":p,"floats":near,"charts":{}}
        rows,source=self.rows_for(p["wmo"])
        rows=self._filter_region(rows, p["region"])
        charts={}
        for v in p["variables"]:
            charts[v]=[{"depth":x["pressure"],v:x[v],"cycle":x["cycle"],"time":x["time"]}
                       for x in rows if v in x][:1200]
        if "temperature" in p["variables"] and "salinity" in p["variables"]:
            charts["ts_diagram"]=[{"temperature":x["temperature"],"salinity":x["salinity"],
                                   "depth":x["pressure"],"cycle":x["cycle"]} for x in rows][:1200]
        return {
            "answer":f"Processed {len(rows):,} observations from {source}. "
                     f"Detected {', '.join(p['variables'])} for the {p['region'].title()}.",
            "filters":p,"source":source,"stats":self.stats(rows),
            "charts":charts
        }

    def float_data(self,wmo):
        rows,source=self.rows_for(wmo)
        if not rows: return {"wmo":wmo,"rows":[],"stats":{},"source":source}
        return {"wmo":wmo,"source":source,"rows":rows[:5000],"stats":self.stats(rows)}

    def plot(self,wmo,plot_type):
        rows,_=self.rows_for(wmo)
        if plot_type=="ts_diagram":
            pts=[{"temperature":x["temperature"],"salinity":x["salinity"],"cycle":x["cycle"]}
                 for x in rows]
        else:
            v="salinity" if "salinity" in plot_type else "density" if "density" in plot_type else "temperature"
            pts=[{"depth":x["pressure"],v:x[v],"cycle":x["cycle"],"time":x["time"]} for x in rows]
        return {"wmo":wmo,"plot_type":plot_type,"points":pts[:3000]}

    def trajectory(self,wmo):
        rows,_=self.rows_for(wmo)
        seen=set(); pts=[]
        for x in rows:
            key=(x["cycle"],x["latitude"],x["longitude"])
            if key not in seen:
                seen.add(key)
                pts.append({"cycle":x["cycle"],"latitude":x["latitude"],"longitude":x["longitude"],"time":x["time"]})
        return {"wmo":wmo,"points":pts}

    def nearest(self,lat,lon):
        by={}
        for x in self.demo:
            d=self._distance(lat,lon,x["latitude"],x["longitude"])
            w=x["wmo"]
            if w not in by or d<by[w]["distance_km"]:
                by[w]={"wmo":w,"latitude":x["latitude"],"longitude":x["longitude"],
                       "distance_km":round(d,2)}
        return sorted(by.values(),key=lambda x:x["distance_km"])[:6]

    def _distance(self,a,b,c,d):
        r=6371
        p1=math.radians(a);p2=math.radians(c)
        dp=math.radians(c-a);dl=math.radians(d-b)
        h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return r*2*math.atan2(math.sqrt(h),math.sqrt(1-h))

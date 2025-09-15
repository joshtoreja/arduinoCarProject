#!/usr/bin/env python3
import argparse, csv, json, os, sys
from typing import List, Tuple

def _normalize_coords_list(data) -> List[Tuple[int,int]]:
    out=[]
    for item in data:
        if isinstance(item,(list,tuple)) and len(item)==2: out.append((int(item[0]), int(item[1])))
        elif isinstance(item,dict) and 'x' in item and 'y' in item: out.append((int(item['x']), int(item['y'])))
        else: raise ValueError(f"bad coord item: {item}")
    return out

def _coords_to_moves(coords: List[Tuple[int,int]]) -> List[str]:
    m=[]
    for i in range(1,len(coords)):
        (x0,y0),(x1,y1)=coords[i-1],coords[i]
        dx,dy=x1-x0,y1-y0
        if   (dx,dy)==(1,0): m.append('R')
        elif (dx,dy)==(-1,0): m.append('L')
        elif (dx,dy)==(0,1): m.append('U')
        elif (dx,dy)==(0,-1): m.append('D')
        else: raise ValueError(f"non-unit step {coords[i-1]}->{coords[i]}")
    return m

def _condense_moves(moves: List[str]) -> List[Tuple[str,int]]:
    if not moves: return []
    out=[]; cur=moves[0]; c=1
    for x in moves[1:]:
        if x==cur: c+=1
        else: out.append((cur,c)); cur=x; c=1
    out.append((cur,c)); return out

def load_moves_from_file(path: str) -> List[Tuple[str,int]]:
    ext = os.path.splitext(path)[1].lower()
    if ext == '.json':
        data = json.load(open(path,'r',encoding='utf-8'))
        if isinstance(data, dict):
            if 'moves' in data:
                mr = data['moves']
                if isinstance(mr,str): mv=[c for c in mr if c in 'UDLR']
                elif isinstance(mr,list): mv=[str(c).upper() for c in mr if str(c).upper() in ('U','D','L','R')]
                else: raise ValueError("'moves' must be str or list")
                return _condense_moves(mv)
            if 'path' in data:
                coords=_normalize_coords_list(data['path'])
                return _condense_moves(_coords_to_moves(coords))
            raise ValueError("JSON must contain 'path' or 'moves'")
        elif isinstance(data, list):
            coords=_normalize_coords_list(data)
            return _condense_moves(_coords_to_moves(coords))
        else:
            raise ValueError("bad JSON")
    elif ext == '.csv':
        coords=[]
        with open(path,'r',newline='',encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                headers=[h.strip().lower() for h in reader.fieldnames]
                try:
                    xcol=next(h for h in headers if h in ('x','col_x','x_coord','xindex'))
                    ycol=next(h for h in headers if h in ('y','col_y','y_coord','yindex'))
                    for row in reader: coords.append((int(row[xcol]), int(row[ycol])))
                except StopIteration:
                    f.seek(0); reader2=csv.reader(f)
                    for row in reader2:
                        if len(row)>=2: coords.append((int(row[0]), int(row[1])))
        if not coords: raise ValueError("CSV empty")
        return _condense_moves(_coords_to_moves(coords))
    else:
        raise ValueError("unsupported file extension")

def main():
    p=argparse.ArgumentParser(description="Send path/moves over Serial")
    p.add_argument('path_file')
    p.add_argument('--port', default=None)
    p.add_argument('--baud', type=int, default=115200)
    p.add_argument('--handshake', action='store_true')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-condense', action='store_true')
    a=p.parse_args()

    pairs=load_moves_from_file(a.path_file)
    cmds=[]
    if a.no_condense:
        for d,n in pairs: cmds.extend([f"{d}1"]*n)
    else:
        for d,n in pairs: cmds.append(f"{d}{n}")

    if a.dry_run or a.port is None:
        print("S"); [print(c) for c in cmds]; print("E"); sys.exit(0)

    try:
        import serial
    except ImportError:
        print("pyserial missing. Install: python3 -m pip install pyserial", file=sys.stderr); sys.exit(1)

    try:
        ser=serial.Serial(a.port, a.baud, timeout=2)
    except Exception as e:
        print(f"open {a.port} failed: {e}", file=sys.stderr); sys.exit(1)

    def rline():
        try:
            s=ser.readline().decode(errors='ignore').strip()
            if s: print("<", s)
            return s
        except Exception: return ''

    if a.handshake:
        print("waiting RDY...")
        while True:
            if rline()=="RDY": break

    def send(line): print(">", line); ser.write((line+"\n").encode('utf-8'))

    send("S"); [send(c) for c in cmds]; send("E")
    ser.close()

if __name__ == "__main__":
    main()

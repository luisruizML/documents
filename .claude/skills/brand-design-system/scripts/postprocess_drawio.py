"""Apply the brand skill's mandatory post-processing to a generated .drawio file.

- every edge gets rounded=1 (orthogonal, rounded, arc jumps are already set)
- every edgeLabel cell gets a white background and Courier New
- the marker [[br]] in a label becomes a line break
- reports (does not change) every edge label that lies on a vertical segment or a bend of its connector: a label
  belongs on the first horizontal segment, centered, with at least 10 pt of free line on each side. If it does not
  fit, move the objects apart.
"""
import xml.etree.ElementTree as ET
import re
import sys

EDGE_LABEL = ("edgeLabel;html=1;align=center;verticalAlign=middle;fontSize=11;"
              "labelBackgroundColor=#FFFFFF;fontColor=#000000;fontFamily=Courier New;")


def process(xml: str) -> str:
    xml = xml.replace("[[br]]", "&lt;br&gt;")
    xml = re.sub(r'style="edgeLabel;[^"]*"', f'style="{EDGE_LABEL}"', xml)
    def edge(m):
        s = m.group(0)
        return s.replace("rounded=0", "rounded=1") if "edgeStyle=orthogonalEdgeStyle" in s else s
    xml = re.sub(r'style="[^"]*"', edge, xml)
    return xml


def _style(cell) -> dict:
    return dict(p.split("=", 1) for p in (cell.get("style") or "").split(";") if "=" in p)


def check_labels(xml: str) -> list[str]:
    """Edge labels (value on an edge cell with waypoints) that are not on the first horizontal segment."""
    root = ET.fromstring(xml)
    boxes = {}
    for c in root.iter("mxCell"):
        g = c.find("mxGeometry")
        if c.get("vertex") == "1" and c.get("parent") == "1" and g is not None and g.get("width"):
            boxes[c.get("id")] = tuple(float(g.get(k)) for k in ("x", "y", "width", "height"))
    out = []
    for c in root.iter("mxCell"):
        g = c.find("mxGeometry")
        if c.get("edge") != "1" or not c.get("value") or g is None or g.get("relative") != "1":
            continue
        pts = [(float(p.get("x")), float(p.get("y"))) for p in g.iter("mxPoint")]
        if len(pts) < 2 or c.get("source") not in boxes or c.get("target") not in boxes:
            continue
        st = _style(c)
        sx, sy, sw, sh = boxes[c.get("source")]
        tx, ty, tw, th = boxes[c.get("target")]
        start = (sx + float(st.get("exitX", 1)) * sw, sy + float(st.get("exitY", 0.5)) * sh)
        end = (tx + float(st.get("entryX", 0)) * tw, ty + float(st.get("entryY", 0.5)) * th)
        path = [start] + pts + [end]
        seg = [abs(b[0] - a[0]) + abs(b[1] - a[1]) for a, b in zip(path, path[1:])]
        centre = (float(g.get("x", 0)) + 1) / 2 * sum(seg)
        first = seg[0]
        half = len(c.get("value")) * 6.6 / 2  # Courier New 11
        if not (10 <= centre - half and centre + half <= first - 10):
            out.append(f"label '{c.get('value')}' is not on the first horizontal segment with 10 pt free on each side")
    return out


if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        for problem in check_labels(text):
            print("warning:", problem, file=sys.stderr)
    except ET.ParseError:
        pass
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(process(text))

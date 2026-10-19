"""Apply the brand skill's mandatory post-processing to a generated .drawio file.

- every edge gets rounded=1 (orthogonal, rounded, arc jumps are already set)
- every edgeLabel cell gets a white background and Courier New
- the marker [[br]] in a label becomes a line break
"""
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


if __name__ == "__main__":
    path = sys.argv[1]
    with open(path, encoding="utf-8") as f:
        text = f.read()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(process(text))

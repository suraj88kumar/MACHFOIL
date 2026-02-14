// frontend/js/util.js
window.API_BASE = "http://127.0.0.1:8000";

function pointsToPath(points) {
  if (!points || !points.length) return "";
  const [x0, y0] = points[0];
  const rest = points.slice(1).map(([x, y]) => `L ${x} ${-y}`).join(" ");
  return `M ${x0} ${-y0} ${rest} Z`;
}

function drawAirfoil(points, svg) {
  if (!svg) {
    console.warn("SVG not found (id=foil_svg).");
    return;
  }
  // Remove previous paths
  [...svg.querySelectorAll("path.airfoil-path")].forEach(n => n.remove());

  const d = pointsToPath(points);
  if (!d) {
    console.warn("No points to draw.");
    return;
  }
  const path = document.createElementNS("http://www.w3.org/2000/svg","path");
  path.setAttribute("d", d);
  path.setAttribute("class", "airfoil-path");
  path.setAttribute("fill", "rgba(30,136,229,0.15)");
  path.setAttribute("stroke", "#0d47a1");
  path.setAttribute("stroke-width", "0.0025");
  svg.appendChild(path);

  // Optional: chord line
  if (!svg.querySelector("line#chord")) {
    const cl = document.createElementNS("http://www.w3.org/2000/svg","line");
    cl.setAttribute("id","chord");
    cl.setAttribute("x1","0"); cl.setAttribute("y1","0");
    cl.setAttribute("x2","1"); cl.setAttribute("y2","0");
    cl.setAttribute("stroke","#999"); cl.setAttribute("stroke-dasharray","0.01 0.01");
    cl.setAttribute("stroke-width","0.001");
    svg.appendChild(cl);
  }
}

window.drawAirfoil = drawAirfoil; // export to global for airfoil.js
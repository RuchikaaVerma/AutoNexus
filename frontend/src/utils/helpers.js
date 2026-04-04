
export function statusColor(status) {
  if (status === "critical") return "#ff4560";
  if (status === "warning")  return "#ffaa00";
  return "#00e396"; // healthy
}


export function urgencyColor(days) {
  if (days <= 7)  return "#ff4560"; 
  if (days <= 14) return "#ff7700"; 
  if (days <= 30) return "#ffaa00"; 
  return "#00e396";                 
}


export function isTempHigh(temp) {
  return temp > 75;
}


export function formatMileage(km) {
  return km.toLocaleString() + " km";
}
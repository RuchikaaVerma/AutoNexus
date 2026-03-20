// Vehicle status ke hisab se color return karta hai
export function statusColor(status) {
  if (status === "critical") return "#ff4560";
  if (status === "warning")  return "#ffaa00";
  return "#00e396"; // healthy
}

// Kitne din mein failure hogi uske hisab se color
export function urgencyColor(days) {
  if (days <= 7)  return "#ff4560"; // red - bahut urgent
  if (days <= 14) return "#ff7700"; // orange - urgent
  if (days <= 30) return "#ffaa00"; // yellow - warning
  return "#00e396";                 // green - theek hai
}

// Temperature high hai ya normal
export function isTempHigh(temp) {
  return temp > 75;
}

// Number ko readable format mein dikhao
export function formatMileage(km) {
  return km.toLocaleString() + " km";
}
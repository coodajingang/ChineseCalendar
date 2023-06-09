export function int2(v) {
  return Math.floor(v);
}

export function mod2(v, n) {
  return (v % n + n) % n;
}

export function sqrt(x) {
  return Math.sqrt(x);
}

export function floor(x) {
  return Math.floor(x);
}

export function abs(x) {
  return Math.abs(x);
}

export function sin(x) {
  return Math.sin(x);
}

export function cos(x) {
  return Math.cos(x);
}

export function tan(x) {
  return Math.tan(x);
}

export function asin(x) {
  return Math.asin(x);
}

export function acos(x) {
  return Math.acos(x);
}

export function atan(x) {
  return Math.atan(x);
}

export function atan2(y, x) {
  return Math.atan2(y, x);
}

export function rad2mrad(v) {
  v = v % (2 * Math.PI);
  if (v < 0) return v + 2 * Math.PI;
  return v;
}

export function rad2rrad(v) {
  v = v % (2 * Math.PI);
  if (v <= -Math.PI) return v + 2 * Math.PI;
  if (v > Math.PI) return v - 2 * Math.PI;
  return v;
}

export function llr2xyz(JW) {
  var r = new Array(), J = JW[0], W = JW[1], R = JW[2];
  r[0] = R * cos(W) * cos(J);
  r[1] = R * cos(W) * sin(J);
  r[2] = R * sin(W);
  return r;
}

export function xyz2llr(xyz) {
  var r = new Array(), x = xyz[0], y = xyz[1], z = xyz[2];
  r[2] = sqrt(x * x + y * y + z * z);
  r[1] = asin(z / r[2]);
  r[0] = rad2mrad(atan2(y, x));
  return r;
}

export function llrConv(JW, E) {
  var r = new Array(), J = JW[0], W = JW[1];
  r[0] = atan2(sin(J) * cos(E) - tan(W) * sin(E), cos(J));
  r[1] = asin(cos(E) * sin(W) + sin(E) * cos(W) * sin(J));
  r[2] = JW[2];
  r[0] = rad2mrad(r[0]);
  return r;
}
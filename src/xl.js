import { XL0, XL0_xzb, XL1 } from "./xlconst";
import { PI2} from "./constants";
import { int2, llrConv, rad2rrad } from "./math";

const rad = 180 * 3600 / Math.PI;
const radd = 180 / Math.PI;
const nutB = new Array(2.1824, -33.75705, 36e-6, -1720, 920, 3.5069, 1256.66393, 11e-6, -132, 57, 1.3375, 16799.4182, -51e-6, -23, 10, 4.3649, -67.5141, 72e-6, 21, -9, 0.04, -628.302, 0, -14, 0, 2.36, 8328.691, 0, 7, 0, 3.46, 1884.966, 0, -5, 2, 5.44, 16833.175, 0, -4, 2, 3.69, 25128.110, 0, -3, 0, 3.55, 628.362, 0, 2, 0); 

const cs_k = 0.2725076;
const cs_k2 = 0.2722810;
const cs_k0 = 109.1222;
const cs_rEar = 6378.1366;
const cs_rEarA = 0.99834 * cs_rEar;
const cs_sMoon = cs_k * cs_rEar * 1.0000036 * rad;
const cs_sMoon2 = cs_k2 * cs_rEar * 1.0000036 * rad;


function XL0_calc(xt, zn, t, n) {
    t /= 10;
    let i, j, v = 0, tn = 1, c;
    let F = XL0[xt], n1, n2, N;
    let n0, pn = zn * 6 + 1, N0 = F[pn + 1] - F[pn];
    for (i = 0; i < 6; i++, tn *= t) {
        n1 = F[pn + i], n2 = F[pn + 1 + i], n0 = n2 - n1;
        if (!n0) continue;
        if (n < 0) {
            N = n2;
        } else {
            N = int2(3 * n * n0 / N0 + 0.5) + n1;
            if (i) N += 3;
            if (N > n2) N = n2;
        }
        for (j = n1, c = 0; j < N; j += 3) {
            c += F[j] * Math.cos(F[j + 1] + t * F[j + 2]);
        }
        v += c * tn;
    }
    v /= F[0];
    if (xt == 0) {
        let t2 = t * t, t3 = t2 * t;
        if (zn == 0) v += (-0.0728 - 2.7702 * t - 1.1019 * t2 - 0.0996 * t3) / rad;
        if (zn == 1) v += (+0.0000 + 0.0004 * t + 0.0004 * t2 - 0.0026 * t3) / rad;
        if (zn == 2) v += (-0.0020 + 0.0044 * t + 0.0213 * t2 - 0.0250 * t3) / 1000000;
    } else {
        let dv = XL0_xzb[(xt - 1) * 3 + zn];
        if (zn == 0) v += -3 * t / rad;
        if (zn == 2) v += dv / 1000000;
        else v += dv / rad;
    }
    return v;
}

function hcjj(t) {
    var t2 = t * t, t3 = t2 * t, t4 = t3 * t, t5 = t4 * t;
    return (84381.4060 - 46.836769 * t - 0.0001831 * t2 + 0.00200340 * t3 - 5.76e-7 * t4 - 4.34e-8 * t5) / rad;
}

export function pty_zty(t) {
    var t2 = t * t, t3 = t2 * t, t4 = t3 * t, t5 = t4 * t;
    var L = (1753470142 + 628331965331.8 * t + 5296.74 * t2 + 0.432 * t3 - 0.1124 * t4 - 0.00009 * t5) / 1000000000 + Math.PI - 20.5 / rad;
    var E, dE, dL, f, z = new Array();
    dL = -17.2 * Math.sin(2.1824 - 33.75705 * t) / rad;
    dE = 9.2 * Math.cos(2.1824 - 33.75705 * t) / rad;
    E = hcjj(t) + dE;
    z[0] = XL0_calc(0, 0, t, 50) + Math.PI + gxc_sunLon(t) + dL;
    z[1] = -(2796 * Math.cos(3.1987 + 8433.46616 * t) + 1016 * Math.cos(5.4225 + 550.75532 * t) + 804 * Math.cos(3.88 + 522.3694 * t)) / 1000000000;
    z = llrConv(z, E);
    z[0] -= dL * Math.cos(E);
    L = rad2rrad(L - z[0]);
    return L / PI2;
}

export function pty_zty2(t) {
    var L = (1753470142 + 628331965331.8 * t + 5296.74 * t * t) / 1000000000 + Math.PI;
    var z = new Array();
    var E = (84381.4088 - 46.836051 * t) / rad;
    z[0] = XL0_calc(0, 0, t, 5) + Math.PI, z[1] = 0;
    z = llrConv(z, E);
    L = rad2rrad(L - z[0]);
    return L / PI2;
} 

function XL1_calc(zn, t, n) {
    let ob = XL1[zn];
    let i, j, F, N, v = 0, tn = 1, c;
    let t2 = t * t, t3 = t2 * t, t4 = t3 * t, t5 = t4 * t, tx = t - 10;
    if (zn == 0) {
        v += (3.81034409 + 8399.684730072 * t - 3.319e-05 * t2 + 3.11e-08 * t3 - 2.033e-10 * t4) * rad;
        v += 5028.792262 * t + 1.1124406 * t2 + 0.00007699 * t3 - 0.000023479 * t4 - 0.0000000178 * t5;
        if (tx > 0) v += -0.866 + 1.43 * tx + 0.054 * tx * tx;
    }
    t2 /= 1e4, t3 /= 1e8, t4 /= 1e8;
    n *= 6;
    if (n < 0) n = ob[0].length;
    for (i = 0; i < ob.length; i++, tn *= t) {
        F = ob[i];
        N = int2(n * F.length / ob[0].length + 0.5);
        if (i) N += 6;
        if (N >= F.length) N = F.length;
        for (j = 0, c = 0; j < N; j += 6) c += F[j] * Math.cos(F[j + 1] + t * F[j + 2] + t2 * F[j + 3] + t3 * F[j + 4] + t4 * F[j + 5]);
        v += c * tn;
    }
    if (zn != 2) v /= rad;
    return v;
};

function gxc_sunLon(t) {
    let v = -0.043126 + 628.301955 * t - 0.000002732 * t * t;
    let e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t;
    return (-20.49552 * (1 + e * Math.cos(v))) / rad;
}
function gxc_sunLat(t) {
    return 0;
}
function gxc_moonLon(t) {
    return -3.4E-6;
}
function gxc_moonLat(t) {
    return 0.063 * Math.sin(0.057 + 8433.4662 * t + 0.000064 * t * t) / rad;
}
function nutation2(t) {
    let i, c, a, t2 = t * t, B = nutB, dL = 0, dE = 0;
    for (i = 0; i < B.length; i += 5) {
        c = B[i] + B[i + 1] * t + B[i + 2] * t2;
        if (i == 0) a = -1.742 * t;
        else a = 0;
        dL += (B[i + 3] + a) * Math.sin(c);
        dE += B[i + 4] * Math.cos(c);
    } 
    return [dL / 100 / rad, dE / 100 / rad];
}
function nutationLon2(t) {
    let i, a, t2 = t * t, dL = 0, B = nutB;
    for (i = 0; i < B.length; i += 5) {
        if (i == 0) a = -1.742 * t;
        else a = 0;
        dL += (B[i + 3] + a) * Math.sin(B[i] + B[i + 1] * t + B[i + 2] * t2);
    } 
    return dL / 100 / rad;
}

export class XL {
    constructor() { }
    static E_Lon(t, n) {
        return XL0_calc(0, 0, t, n);
    }

    static M_Lon(t, n) {
        return XL1_calc(0, t, n);
    }

    static E_v(t) {
        let f = 628.307585 * t;
        return 628.332 + 21 * Math.sin(1.527 + f) + 0.44 * Math.sin(1.48 + f * 2) + 0.129 * Math.sin(5.82 + f) * t + 0.00055 * Math.sin(4.21 + f) * t * t;
    }
    static M_v(t) {
        let v = 8399.71 - 914 * Math.sin(0.7848 + 8328.691425 * t + 0.0001523 * t * t);
        v -= 179 * Math.sin(2.543 + 15542.7543 * t) + 160 * Math.sin(0.1874 + 7214.0629 * t) + 62 * Math.sin(3.14 + 16657.3828 * t) + 34 * Math.sin(4.827 + 16866.9323 * t) + 22 * Math.sin(4.9 + 23871.4457 * t) + 12 * Math.sin(2.59 + 14914.4523 * t) + 7 * Math.sin(0.23 + 6585.7609 * t) + 5 * Math.sin(0.9 + 25195.624 * t) + 5 * Math.sin(2.32 - 7700.3895 * t) + 5 * Math.sin(3.88 + 8956.9934 * t) + 5 * Math.sin(0.49 + 7771.3771 * t);
        return v;
    }
    static MS_aLon(t, Mn, Sn) {
        return XL.M_Lon(t, Mn) + gxc_moonLon(t) - (XL.E_Lon(t, Sn) + gxc_sunLon(t) + Math.PI);
    }
    static S_aLon(t, n) {
        return XL.E_Lon(t, n) + nutationLon2(t) + gxc_sunLon(t) + Math.PI;
    }
    static E_Lon_t(W) {
        let t, v = 628.3319653318;
        t = (W - 1.75347) / v;
        v = XL.E_v(t);
        t += (W - XL.E_Lon(t, 10)) / v;
        v = XL.E_v(t);
        t += (W - XL.E_Lon(t, -1)) / v;
        return t;
    }
    static M_Lon_t(W) {
        let t, v = 8399.70911033384;
        t = (W - 3.81034) / v;
        t += (W - XL.M_Lon(t, 3)) / v;
        v = XL.M_v(t);
        t += (W - XL.M_Lon(t, 20)) / v;
        t += (W - XL.M_Lon(t, -1)) / v;
        return t;
    }
    static MS_aLon_t(W) {
        let t, v = 7771.37714500204;
        t = (W + 1.08472) / v;
        t += (W - XL.MS_aLon(t, 3, 3)) / v;
        v = XL.M_v(t) - XL.E_v(t);
        t += (W - XL.MS_aLon(t, 20, 10)) / v;
        t += (W - XL.MS_aLon(t, -1, 60)) / v;
        return t;
    }
    static S_aLon_t(W) {
        let t, v = 628.3319653318;
        t = (W - 1.75347 - Math.PI) / v;
        v = XL.E_v(t);
        t += (W - XL.S_aLon(t, 10)) / v;
        v = XL.E_v(t);
        t += (W - XL.S_aLon(t, -1)) / v;
        return t;
    }
    static MS_aLon_t2(W) {
        let t, v = 7771.37714500204;
        t = (W + 1.08472) / v;
        let L, t2 = t * t;
        t -= (-0.00003309 * t2 + 0.10976 * Math.cos(0.784758 + 8328.6914246 * t + 0.000152292 * t2) + 0.02224 * Math.cos(0.18740 + 7214.0628654 * t - 0.00021848 * t2) - 0.03342 * Math.cos(4.669257 + 628.307585 * t)) / v;
        L = XL.M_Lon(t, 20) - (4.8950632 + 628.3319653318 * t + 0.000005297 * t * t + 0.0334166 * Math.cos(4.669257 + 628.307585 * t) + 0.0002061 * Math.cos(2.67823 + 628.307585 * t) * t + 0.000349 * Math.cos(4.6261 + 1256.61517 * t) - 20.5 / rad);
        v = 7771.38 - 914 * Math.sin(0.7848 + 8328.691425 * t + 0.0001523 * t * t) - 179 * Math.sin(2.543 + 15542.7543 * t) - 160 * Math.sin(0.1874 + 7214.0629 * t);
        t += (W - L) / v;
        return t;
    }
    static S_aLon_t2(W) {
        let t, L, v = 628.3319653318;
        t = (W - 1.75347 - Math.PI) / v;
        t -= (0.000005297 * t * t + 0.0334166 * Math.cos(4.669257 + 628.307585 * t) + 0.0002061 * Math.cos(2.67823 + 628.307585 * t) * t) / v;
        t += (W - XL.E_Lon(t, 8) - Math.PI + (20.5 + 17.2 * Math.sin(2.1824 - 33.75705 * t)) / rad) / v;
        return t;
    }
    static moonIll(t) {
        let t2 = t * t, t3 = t2 * t, t4 = t3 * t;
        let D, M, m, a, dm = Math.PI / 180;
        D = (297.8502042 + 445267.1115168 * t - 0.0016300 * t2 + t3 / 545868 - t4 / 113065000) * dm;
        M = (357.5291092 + 35999.0502909 * t - 0.0001536 * t2 + t3 / 24490000) * dm;
        m = (134.9634114 + 477198.8676313 * t + 0.0089970 * t2 + t3 / 69699 - t4 / 14712000) * dm;
        a = Math.PI - D + (-6.289 * Math.sin(m) + 2.100 * Math.sin(M) - 1.274 * Math.sin(D * 2 - m) - 0.658 * Math.sin(D * 2) - 0.214 * Math.sin(m * 2) - 0.110 * Math.sin(D)) * dm;
        return (1 + Math.cos(a)) / 2;
    }
    static moonRad(r, h) {
        return cs_sMoon / r * (1 + Math.sin(h) * cs_rEar / r);
    }
    static moonMinR(t, min) {
        let a = 27.55454988 / 36525, b;
        if (min) b = -10.3302 / 36525;
        else b = 3.4471 / 36525;
        t = b + a * int2((t - b) / a + 0.5);
        let r1, r2, r3, dt;
        dt = 2 / 36525;
        r1 = XL1_calc(2, t - dt, 10);
        r2 = XL1_calc(2, t, 10);
        r3 = XL1_calc(2, t + dt, 10);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        dt = 0.5 / 36525;
        r1 = XL1_calc(2, t - dt, 20);
        r2 = XL1_calc(2, t, 20);
        r3 = XL1_calc(2, t + dt, 20);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        dt = 1200 / 86400 / 36525;
        r1 = XL1_calc(2, t - dt, -1);
        r2 = XL1_calc(2, t, -1);
        r3 = XL1_calc(2, t + dt, -1);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        r2 += (r1 - r3) / (r1 + r3 - 2 * r2) * (r3 - r1) / 8;
        let re = new Array(t, r2);
        return re;
    }
    static moonNode(t, asc) {
        let a = 27.21222082 / 36525, b;
        if (asc) b = 21 / 36525;
        else b = 35 / 36525;
        t = b + a * int2((t - b) / a + 0.5);
        let w, v, w2, dt;
        dt = 0.5 / 36525;
        w = XL1_calc(1, t, 10);
        w2 = XL1_calc(1, t + dt, 10);
        v = (w2 - w) / dt;
        t -= w / v;
        dt = 0.05 / 36525;
        w = XL1_calc(1, t, 40);
        w2 = XL1_calc(1, t + dt, 40);
        v = (w2 - w) / dt;
        t -= w / v;
        w = XL1_calc(1, t, -1);
        t -= w / v;
        let re = new Array(t, XL1_calc(0, t, -1));
        return re;
    }
    static earthMinR(t, min) {
        let a = 365.25963586 / 36525, b;
        if (min) b = 1.7 / 36525;
        else b = 184.5 / 36525;
        t = b + a * int2((t - b) / a + 0.5);
        let r1, r2, r3, dt;
        dt = 3 / 36525;
        r1 = XL0_calc(0, 2, t - dt, 10);
        r2 = XL0_calc(0, 2, t, 10);
        r3 = XL0_calc(0, 2, t + dt, 10);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        dt = 0.2 / 36525;
        r1 = XL0_calc(0, 2, t - dt, 80);
        r2 = XL0_calc(0, 2, t, 80);
        r3 = XL0_calc(0, 2, t + dt, 80);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        dt = 0.01 / 36525;
        r1 = XL0_calc(0, 2, t - dt, -1);
        r2 = XL0_calc(0, 2, t, -1);
        r3 = XL0_calc(0, 2, t + dt, -1);
        t += (r1 - r3) / (r1 + r3 - 2 * r2) * dt / 2;
        r2 += (r1 - r3) / (r1 + r3 - 2 * r2) * (r3 - r1) / 8;
        let re = new Array(t, r2);
        return re;
    }
}
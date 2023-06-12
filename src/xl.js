import { XL0, XL0_xzb } from "./xlconst";
import { PI2} from "./constants";
import { int2, llrConv, rad2rrad } from "./math";

const rad = 180 * 3600 / Math.PI;
const nutB = new Array(2.1824, -33.75705, 36e-6, -1720, 920, 3.5069, 1256.66393, 11e-6, -132, 57, 1.3375, 16799.4182, -51e-6, -23, 10, 4.3649, -67.5141, 72e-6, 21, -9, 0.04, -628.302, 0, -14, 0, 2.36, 8328.691, 0, 7, 0, 3.46, 1884.966, 0, -5, 2, 5.44, 16833.175, 0, -4, 2, 3.69, 25128.110, 0, -3, 0, 3.55, 628.362, 0, 2, 0); 


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

export function pty_zty2(t) {
    var L = (1753470142 + 628331965331.8 * t + 5296.74 * t * t) / 1000000000 + Math.PI;
    var z = new Array();
    var E = (84381.4088 - 46.836051 * t) / rad;
    z[0] = XL0_calc(0, 0, t, 5) + Math.PI, z[1] = 0;
    z = llrConv(z, E);
    L = rad2rrad(L - z[0]);
    return L / PI2;
} 

// use
function gxc_sunLon(t) {
    let v = -0.043126 + 628.301955 * t - 0.000002732 * t * t;
    let e = 0.016708634 - 0.000042037 * t - 0.0000001267 * t * t;
    return (-20.49552 * (1 + e * Math.cos(v))) / rad;
}

// use
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
    // use
    static E_Lon(t, n) {
        return XL0_calc(0, 0, t, n);
    }

    // use
    static S_aLon(t, n) {
        return XL.E_Lon(t, n) + nutationLon2(t) + gxc_sunLon(t) + Math.PI;
    }

}
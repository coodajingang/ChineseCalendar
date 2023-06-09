import {dt_T} from "./dt"
import { XL, pty_zty2 } from "./xl";
import { J2000, Gan, Zhi,PI2, radd} from "./constants";
import { createJdWithDateTime } from "./jd"
import { int2 } from "./math";

// 将八字的计算单独抽出来 ，形成一个单独的文件 
// 输入年月日时 ， 输出八字 
// 输出 前后节气及交节点 

function year2Ayear(c) {
    let y = String(c).replace(/[^0-9Bb\*-]/g, '');
    let q = y.substr(0, 1);
    let x = 0;
    if (q == 'B' || q == 'b' || q == '*') {
        x = 1 - Number(y.substr(1, y.length));
        if (x > 0) {
            //alert('通用纪法的公元前纪法从B.C.1年开始。并且没有公元0年');
            throw new Error("通用纪法的公元前纪法从B.C.1年开始。并且没有公元0年");
        }
    } else {
        x = Number(y);
        x -= 0;
    }
    if (x < -4712) throw new Error("超过B.C. 4713不准"); //alert('超过B.C. 4713不准');
    if (x > 9999) throw new Error('超过9999年的农历计算很不准。'); //alert('超过9999年的农历计算很不准。');
    return x;
}

export function bazi_now(j = 0.0, useTrueSolar = true) {
    let now = new Date();
    let timeZone = now.getTimezoneOffset();
    return bazi_custom(now.getFullYear(), now.getMonth() + 1, now.getDate(), now.getHours(), now.getMinutes(), now.getSeconds(), timeZone, j, useTrueSolar);
}

export function bazi_custom(year, month, day, hour, minute, second, tZOffset = -0.0, j = 0.0, useTrueSolar = true) {
    let dt = {
        year: year2Ayear(String(year)),
        month: month,
        day: day,
        hour: hour,
        minute: minute,
        second: second
    }
    let jdInst = createJdWithDateTime(dt)
    let curTZ = tZOffset / 60 / 24
    //console.log(' 儒略日数 ' +  int2(jdInst.getJD() + 0.5) + ' 距2000年首' + int2(jdInst.getJD()+0.5-J2000) + '日' + jdInst.getTimeStr())
    //console.log('JD:' + jdInst.getJD())
    return bazi(jdInst.getJD() - J2000, j/radd, curTZ, useTrueSolar)
}

export function bazi(jd , J, curTZ, useTrueSolar) {
    let res = new Object();
    //res.desc =  ' 儒略日数 ' + int2(jd+0.5) + ' 距2000年首' + int2(jd+0.5-J2000) + '日<br>'
    var v;
    var jd2 = jd + dt_T(jd);
    var w = XL.S_aLon(jd2 / 36525, -1);
    var k = int2((w / PI2 * 360 + 45 + 15 * 360) / 30);
    //console.log("jd jd2 w k" + jd + '  ' + jd2 + '  ' + w + ' '+ k)
    jd += pty_zty2(jd2 / 36525) + J / Math.PI / 2;
    //console.log('new jd ' + jd)
    let jdInst = createJdWithDateTime({jd: jd + J2000})
    res.tys = jdInst.getTimeStr();
    jd += 13 / 24;
    var D = Math.floor(jd), SC = int2((jd - D) * 12);
    v = int2(k / 12 + 6000000);
    res.year = Gan[v % 10] + Zhi[v % 12];
    v = k + 2 + 60000000;
    res.month = Gan[v % 10] + Zhi[v % 12];
    v = D - 6 + 9000000;
    res.day = Gan[v % 10] + Zhi[v % 12];
    v = (D - 1) * 12 + 90000000 + SC;
    res.hour = Gan[v % 10] + Zhi[v % 12];

    res.hs = new Array();
    let x = v - SC;
    for (let i = 0; i < 13; i++) {
        res.hs.push(Gan[(x + i) % 10] + Zhi[(x + i) % 12]);
    }

    return res;
  }
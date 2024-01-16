"use strict";

import { NdaysGregJul, getJD} from "./utilities";
import { solarTermMoonPhase_ystart,offsets_sunMoon ,solarTerms, newMoons,firstQuarters,fullMoons,thirdQuarters ,ChineseToGregorian} from "./calendarData"
import { bazi_custom } from "./bazi"
import { decompress_moonPhases, decompress_solarTerms } from "./decompressSunMoonData"
import { eclipse_year_range,solar_eclipse_link,lunar_eclipse_link } from "./eclipse_linksM722-2202";

// use
// Language-specific constants
function langConstant(lang) {
    let gMonth, weeks, heaven, earth, animal, month_num, monthL, 
        Qnames, soltermNames, note_early, note_late, note1929, note1914;
    

    let gMonthChi = ["1 月", "2 月", "3 月", "4 月", "5 月", "6 月", 
                  "7 月", "8 月", "9 月", "10 月", "11 月", "12 月"];
    let weeksChi =["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"];
    let heavenChi = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"];
    let earthChi = ["子","丑","寅","卯","辰", "巳", "午", "未", "申", "酉", "戌", "亥"];
    let month_numChi = ["正","二","三","四","五", "六","七","八","九","十", 
                    "十一","十二"];
    let date_numChi = ["初一"];
    for (let i=2; i<11; i++) {
        date_numChi.push("初"+month_numChi[i-1]);
    }
    date_numChi.push("十一");
    for (let i=12; i<20; i++) {
        date_numChi.push("十"+month_numChi[i-11]);
    }
    date_numChi.push("二十");
    date_numChi.push("廿一");
    for (let i=22; i<30; i++) {
        date_numChi.push("廿"+month_numChi[i-21]);
    }
    date_numChi.push("三十");
    let monthLChi = ["小","大"];
    let QnamesChi = ["朔", "上弦", "望", "下弦"];
    let soltermNamesSim = ["小寒", "大寒", "立春", "雨水", "惊蛰", "春分", 
                           "清明", "谷雨", "立夏", "小满", "芒种", "夏至", 
                           "小暑", "大暑", "立秋", "处暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪", "冬至", 
                           "小寒"];
    let animalSim = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"];

    // Simplified Chinese
    gMonth = gMonthChi;
    weeks = weeksChi;
    heaven = heavenChi;
    earth = earthChi;
    animal = animalSim;
    Qnames = QnamesChi;
    soltermNames = soltermNamesSim;
    month_num = month_numChi;
    monthL = monthLChi;
    let julian = false;

    return {gMonth:gMonth, weeks:weeks, lang:lang, heaven:heaven, earth:earth, 
        animal:animal, region:'default', cmonth:month_num, monthL:monthL, Qnames:Qnames, 
        soltermNames:soltermNames, julian:julian, li_ancient:null, 
    date_numChi:date_numChi };
}

// Convert the jian number to month number, determine the year number offset 
// and the month number for the first month of a year.
// jian number: 1=yin, 2=mao, ..., 11=zi, 12 = chou
// month number depends on the jian of the month 1, which is
// usually the same as the jian number but they are different
// in certain periods in the Chinese history. 
// year offset: 0 if the year number doesn't change, 
//             -1 if in the previous year,  +1 if in the following year.
function jianToMonthYearoffset(jianIn, y, region) {
    let jian = Math.abs(jianIn);
    let yearOffset=0, monNum=jian;
    
    // Han dynasty
    if (y < -103 && jian > 9) {
        yearOffset = 1;
    }
    
    // Xin dynasty
    if (y==8 && jian==12) {
        monNum = 1;
        yearOffset = 1;
    }
    if (y > 8 && y < 23) {
        monNum = (jian==12 ? 1:jian+1);
        if (jian==12) { yearOffset = 1;}
    }
    if (y==23 && jian<12) {
        monNum = jian+1;
    }
    
    // Wei dynasty (Three-Kingdom period)
    if ( ( (y==237 && jian>2) || (y==238) || (y==239 && jian<12) ) && region=='default') {
        monNum = (jian==12 ? 1:jian+1);
        if (jian==12) { yearOffset = 1;}
    }
    
    // Tang dynasty
    if (y > 688 && y < 700) {
        if (jian > 10) { yearOffset = 1;}
    }
    if (y==761 && jian > 10) {
        monNum = jian - 10;
        yearOffset = 1;
    }
    if (y==762 && jian < 4) {
        monNum = jian + 2;
    }
    
    if (jianIn < 0) { monNum = -monNum; }
    
    return {monNum:monNum, yearOffset:yearOffset};
}

// use
// Determine the month number for the first month of a year.
// This is usually just 1 but is different in some periods
function firstMonthNum(y) {
    let firstMonth = 1;
    if (y < -102) { firstMonth = 10;}
    if (y > 689 && y < 701) { firstMonth = 11;}
    return firstMonth;
}

// Decompress time: time t has been compressed to retain information 
// to the nearest minute. The compression algorithm is 
// t = floor(x)*1441 + m, where x is the original time expressed 
// in the number of days from Jan 0. The inverse transform is 
// y = floor(t/1441), x_approx = y + (t - y*1441)/1440
function decompress_time(t) {
    let x = [];
    for (let i=0; i<t.length; i++) {
        let y = Math.floor(t[i]/1441);
        let m = t[i] - 1441*y;
        if (m > 1439.5) { m = 1439.9;}
        x.push(y + m/1440.0);
    }
    return x;
}

// use
// Calendrical data for year y
function calDataYear(y, langVars) {
    // *** Data for Gregorian/Julian calendar ***
    
    // Is y a leap year?
    let ndays = NdaysGregJul(y);
    let leap = Number((ndays==366 ? 1:0));
    // number of days in the beg of the 12 months
    let mday = [0, 31, 59+leap, 90+leap, 120+leap, 151+leap, 181+leap, 212+leap, 243+leap, 273+leap, 304+leap, 334+leap, 365+leap];
    if (y==1582) {
        mday = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 294, 324, 355];
    }
    // Julian day on Dec 30, y-1 at noon UT
    let jd0 = Math.floor(getJD(y-1,12,30) + 1);
    // number of days in year y-1, will be used below
    let ndays1 = NdaysGregJul(y-1);
    
    // *** 24 solar terms in year y **
    let offsets = offsets_sunMoon();
    let solarAll = solarTerms();
    let inds = y - solarTermMoonPhase_ystart();
    let solar = solarAll[inds];
    let solar2 = [solar.pop()];
    solar = decompress_solarTerms(y, 1, offsets.solar, solar);
    // solar[] contains solar terms in year y starting from 
    // J12 (Xiaohan) to J11 (daxue). It stores the dates 
    // of the solar terms counting from Dec. 31, y-1 at 0h (UTC+8).
    
    // solar2[] contains the compressed winter solstice in year y.
    // Add one more to solar2 if J12 occurs before Jan 3.
    if (solar[0] < 4323) {
        solar2.push(solarAll[inds+1][0]);
    }
    solarAll = null; // remove large array
    solar2 = decompress_solarTerms(y+1, 0, offsets.solar, solar2);
    let i;
    for (i=0; i < solar2.length; i++) { solar.push(solar2[i]+ndays*1441);}
    solar = decompress_time(solar);
    
    // ** new moons, quarters and full moons in year y **
    
    let Q0 = (newMoons())[inds]; Q0.unshift(0);
    let Q1 = (firstQuarters())[inds]; Q1.unshift(1);
    let Q2 = (fullMoons())[inds]; Q2.unshift(2);
    let Q3 = (thirdQuarters())[inds]; Q3.unshift(3);
    Q0 = decompress_moonPhases(y, offsets.lunar, Q0, 1);
    Q1 = decompress_moonPhases(y, offsets.lunar, Q1, 1);
    Q2 = decompress_moonPhases(y, offsets.lunar, Q2, 1);
    Q3 = decompress_moonPhases(y, offsets.lunar, Q3, 1);
    // decompress moon phase data
    Q0 = decompress_time(Q0); Q1 = decompress_time(Q1); 
    Q2 = decompress_time(Q2); Q3 = decompress_time(Q3); 


    // eclipses
    let iec = y - eclipse_year_range()[0];
    // sol_eclipse is a 2D array that stores the info of solar 
    // eclipses in year y. It has the form 
    // [[d_eclipse1, ind_eclipse1, type_eclipse1], 
    //  [d_eclipse2, ind_eclipse2, type_eclipse2], ...]
    // d: eclipse day counting from Dec 31, y-1.
    // ind: index of the eclipse (for eclipse link)
    // type: type of eclipse (0=partial, 1=annular, 2=total, 3=hybrid)
    let links = solar_eclipse_link();
    let sol_eclipse = links[iec];
    let extra_links = links[iec-1];
    extra_links.forEach(function(e) {
        if (ndays1 - e[0] < 3) {
            // this is close to Jan 1, y; add it to be safe
            sol_eclipse.push([e[0]-ndays1, e[1], e[2]]);
        }
    });
    extra_links = links[iec+1];
    extra_links.forEach(function(e) {
        if (e[0] < 3) {
            // this is close to Dec 31, y; add it to be safe
            sol_eclipse.push([e[0]+ndays, e[1], e[2]]);
        }
    });
    // lun_eclipse is a 2D array that stores the info of lunar 
    // eclipses in year y. It has the form 
    // [[d_eclipse1, ind_eclipse1, type_eclipse1], 
    //  [d_eclipse2, ind_eclipse2, type_eclipse2], ...]
    // d: eclipse day counting from Dec 31, y-1.
    // ind: index of the eclipse (for eclipse link)
    // type: type of eclipse (0=penumbral, 1=partial, 2=total)
    links = lunar_eclipse_link();
    let lun_eclipse = links[iec];
    extra_links = links[iec-1];
    extra_links.forEach(function(e) {
        if (ndays1 - e[0] < 3) {
            // this is close to Jan 1, y; add it to be safe
            lun_eclipse.push([e[0]-ndays1, e[1], e[2]]);
        }
    });
    extra_links = links[iec+1];
    extra_links.forEach(function(e) {
        if (e[0] < 3) {
            // this is close to Dec 31, y; add it to be safe
            lun_eclipse.push([e[0]+ndays, e[1], e[2]]);
        }
    });
    links = null;

    
    // *** Data for Chinese calendar ***
    let region = langVars.region;
    let cdate, ind, cmdate1, cmdate, pingqi, ncdays, ncdays1;
    if (region=='default') {
        cdate = ChineseToGregorian();
        // cdate is a 2D array. Each row contains data for a Chinese year
        // columns: year, first date of month 1, 2,... , 12, leap month, 
        //          month # that is leaped, # of days in the year
        // leap month = month # = 0 if no leap month
        ind = y - cdate[0][0];
        // Chinese months in the previous year
        cmdate1 = sortMonths(cdate[ind-1]);
        ncdays1 = cdate[ind-1][15]; // Number of days in the previous year
        // Chinese months in the current year
        cmdate = sortMonths(cdate[ind]);
        ncdays = cdate[ind][15]; // Number of days in this year
        cdate = null;
    } else {
        cdate = setup_region_calendar(region, y-1, false);
        cmdate1 = sortMonths(cdate);
        ncdays1 = cdate[15];
        cdate = setup_region_calendar(region, y, true);
        cmdate = sortMonths(cdate.cm); pingqi = cdate.pingqi;
        ncdays = cdate.cm[15];
        cdate = null;
    }
    // Gather Chinese months within year y
    let d, n = cmdate1.cmonthDate.length;
    let cmonthDate=[], cmonthJian=[], cmonthNum=[], cmonthLong = [], cmonthYear = [];
    // cmonthXiaYear: Chinese year according to the Xia calendar (yin month being the 
    //                first month); 0 means previous year, 1 current year.
    let cmonthXiaYear = []; 
    let jian, jianInfo; // jian number: 1=yin, 2=mao, ...
    for (i=2; i<n; i++) {
        if (cmdate1.cmonthDate[i] > ndays1+1) {
            // cmdate1.cmonthDate[i-1] is the last month before Jan 1, y
            for (let j=i-1; j<n; j++) {
                cmonthDate.push(cmdate1.cmonthDate[j] - ndays1);
                cmonthXiaYear.push(0);
                jian = cmdate1.cmonthNum[j];
                cmonthJian.push(jian);
                jianInfo = jianToMonthYearoffset(jian, y-1, region);
                cmonthNum.push(jianInfo.monNum);
                cmonthYear.push(jianInfo.yearOffset);
                if (j < n-1) {
                    d = cmdate1.cmonthDate[j+1] - cmdate1.cmonthDate[j];
                } else {
                    d = ncdays1 - cmdate1.cmonthDate[j] + cmdate1.cmonthDate[0];
                }
                cmonthLong.push(d==30 ? 1:0);
            }
            break;
        }
        if (i==n-1) {
            // The last Chinese month is the last month before Jan 1, y
           cmonthDate.push(cmdate1.cmonthDate[i] - ndays1);
           cmonthXiaYear.push(0);
           jian = cmdate1.cmonthNum[i];
           cmonthJian.push(jian); 
           jianInfo = jianToMonthYearoffset(jian, y-1, region);
           cmonthNum.push(jianInfo.monNum);
           cmonthYear.push(jianInfo.yearOffset);
           d = ncdays1 - cmdate1.cmonthDate[i] + cmdate1.cmonthDate[0];
           cmonthLong.push(d==30 ? 1:0);
        }
    }
    n = cmdate.cmonthDate.length;
    for (i=0; i<n; i++) {
        if (cmdate.cmonthDate[i] <= ndays) {
           cmonthDate.push(cmdate.cmonthDate[i]); 
           cmonthXiaYear.push(1);
           jian = cmdate.cmonthNum[i];
           cmonthJian.push(jian);
           jianInfo = jianToMonthYearoffset(jian, y, region);
           cmonthNum.push(jianInfo.monNum);
           cmonthYear.push(1 + jianInfo.yearOffset);
           if (i < n-1) {
                d = cmdate.cmonthDate[i+1] - cmdate.cmonthDate[i];
            } else {
                d = ncdays - cmdate.cmonthDate[i] + cmdate.cmonthDate[0];
            }
            cmonthLong.push(d==30 ? 1:0);
        }
    }
    
    let out = {jd0:jd0, mday:mday, cmonthDate:cmonthDate, cmonthXiaYear, 
               cmonthJian:cmonthJian, cmonthNum:cmonthNum, 
               cmonthYear:cmonthYear, cmonthLong:cmonthLong,             
               solar:solar,  Q0:Q0, Q1:Q1, Q2:Q2, Q3:Q3, year:y, 
               solar:solar, year:y, 
               sol_eclipse:sol_eclipse, lun_eclipse:lun_eclipse
    };
    if (region != 'default') {
        out.pingqi = pingqi;
    }
    return out;
}

// Sort the Chinese months in chronological order by placing 
// the leap month to the appropriate place
function sortMonths(cmdate) {
    let cmonthDate = [];
    let cmonthNum = []; // Jian number
    let leapM = cmdate[14];
    let i;
    if (leapM==0) {
        for (i=0; i<12; i++) {
            cmonthDate.push(cmdate[i+1]);
            cmonthNum.push(i+1);
        }
    } else {
        for (i=0; i<leapM; i++) {
            cmonthDate.push(cmdate[i+1]);
            cmonthNum.push(i+1);
        }
        cmonthDate.push(cmdate[13]);
        cmonthNum.push(-leapM);
        for (i=leapM+1; i<13; i++) {
            cmonthDate.push(cmdate[i]);
            cmonthNum.push(i);
        }
    }
    return {cmonthDate:cmonthDate, cmonthNum:cmonthNum};
}

// use
export function calendarDayInfo(y, m, d, l) {
    let year = Number(y)
    let month = Number(m)
    let day = Number(d)
    let lang = Number(l)

    let langVars = langConstant(lang);
    // langVars.region = split_calendar_handler(lang,year);
    let calVars = calDataYear(year, langVars);
    // How many Chinese years does this Gregorian/Julian calendar span?
    let n = calVars.cmonthDate.length;
    let Ncyear = calVars.cmonthYear[n-1] - calVars.cmonthYear[0] + 1;
    
    // Determine the date(s) of the Chinese new year
    let i,j,k,mm,dd;
    let mm1 = [], dd1 = [];
    let firstMonth = [0,0,0];
    for (i=0; i<3; i++) {
       if (year > -110) {
           firstMonth[i] = firstMonthNum(year-1+i);
       } else {
           firstMonth[i] = calVars.firstMonthNum;
       }
    }
    for (i=1; i<Ncyear; i++) {
        let firstMon = firstMonth[calVars.cmonthYear[0] + i];
        for(j=1; j<n; j++) {
            if (calVars.cmonthYear[j]==calVars.cmonthYear[0]+i && 
                calVars.cmonthNum[j]==firstMon) {
                dd = calVars.cmonthDate[j];
                for (k=0; k<13; k++) {
                    if (dd <= calVars.mday[k]) {
                        mm = k;
                        break;
                    }
                }
                mm1.push(mm); dd1.push(dd - calVars.mday[mm-1]);
            }
        }
    }
    
    let ih0 = (year + 725) % 10;
    let ie0 = (year + 727) % 12;
    if (ih0 < 0) { ih0 += 10;}
    if (ie0 < 0) { ie0 += 12;}
    let cyear = [" ", " ", " "];
    cyear[0] = langVars.heaven[ih0]+' '+langVars.earth[ie0]+' ('+langVars.animal[ie0]+')';
    let ih = (year + 726) % 10;
    let ie = (year + 728) % 12;
    if (ih < 0) { ih += 10;}
    if (ie < 0) { ie += 12;}
    cyear[1] = langVars.heaven[ih]+' '+langVars.earth[ie]+' ('+langVars.animal[ie]+')';
    let ih2 = (year + 727) % 10;
    let ie2 = (year + 729) % 12;
    if (ih2 < 0) { ih2 += 10;}
    if (ie2 < 0) { ie2 += 12;}
    cyear[2] = langVars.heaven[ih2]+' '+langVars.earth[ie2]+' ('+langVars.animal[ie2]+')';
    
    cyear[0] = langVars.heaven[ih0]+langVars.earth[ie0]+'年';
    cyear[1] = langVars.heaven[ih]+langVars.earth[ie]+'年';
    cyear[2] = langVars.heaven[ih2]+langVars.earth[ie2]+'年';
    
    console.log(cyear)
    console.log(firstMonth)
    console.log(langVars)
    console.log(calVars)

    let dayInfo = calMonthDay(day, month - 1, lang, year, cyear, firstMonth, langVars, calVars); 

    let bazi = bazi_custom(year, month, day, 12, 0, 0);
    dayInfo.bazi = bazi;
    // console.log(dayInfo)
    return dayInfo;
}


// use
function calMonthDay(d,m,lang, year, cyear, firstMonth, langVars, calVars) {
    let result = {}
    //let cmon = calChineseMonths(d, m, lang, year, cyear, langVars, calVars);
    
    // 通过当月首日jd + 3 mod 7 得到首月星期
    // Determine the day of week of the first date of month
    let week1 = (calVars.jd0 + calVars.mday[m] + 3) % 7;
    
    // mday 存放有个月的天数，根据上个月-下个月得出当月天数
    // # of days in the months
    //let n = calVars.mday[m+1] - calVars.mday[m];
    let week = (week1 + d - 1) % 7

    let nongliDay = calChineseDate(year,m,d, lang, langVars, calVars, firstMonth);
    let jd = calSexagenaryDays(m, d, langVars, calVars);

    let hDay = langVars.heaven[(jd-1) % 10];
    let eDay = langVars.earth[(jd+1) % 12];

    let moonPhases = calMoonPhases(m, lang, langVars, calVars);
    let solars = cal24solterms(m, lang, langVars, calVars);

    result.jd = jd;
    result.week = week;
    result.gan = hDay;
    result.zhi = eDay;
    result.moon = moonPhases;
    result.solar = solars;
    result.nontli = nongliDay
    result.year = year
    result.month = m + 1
    result.day = d
    result.date = year + '-' + result.month + '-' + d
    return result;
}


// use
function calChineseDate(y, m, d, lang, langVars, calVars, firstMonth) {
    // dd = 当年的天序数
    // # of days from Dec 31 in the previous year
    let dd = calVars.mday[m] + d; 
    
    // Determine the month and date in Chinese calendar
    let i, cd, longM, cmIsFirstMonth, cm=0, n=calVars.cmonthDate.length;
    for (i=0; i<n-1; i++) {
        if (dd >= calVars.cmonthDate[i] && dd < calVars.cmonthDate[i+1]) {
            cm = calVars.cmonthNum[i];
            cd = dd - calVars.cmonthDate[i] + 1;
            longM = calVars.cmonthLong[i];
            cmIsFirstMonth = (cm == firstMonth[calVars.cmonthYear[i]]);
            if (y==-103 || y==700) {cmIsFirstMonth = false;}
        }
    }
    
    if (cm==0) { 
        cm = calVars.cmonthNum[n-1];
        cd = dd - calVars.cmonthDate[n-1] + 1;
        longM = calVars.cmonthLong[n-1];
        cmIsFirstMonth = (cm == firstMonth[calVars.cmonthYear[n-1]]);
        if (y==-103 || y==700) {cmIsFirstMonth = false;}
    }
    
    let txt, m1, warn;
    
    if (lang==0) {
        // English
        m1 = "0"+Math.abs(cm);
        m1 = m1.slice(-2);
        if (cm < 0) {
            if (y < -104) {
                m1 = calVars.leap;
            } else if (y==-104) {
                m1 = 'post 9';
            } else {
                m1 = 'leap '+m1;
            }
        }
        let d1 = "0"+cd;
        d1 = d1.slice(-2);
        return m1+'-'+d1;
    } else {
      // Chinese
       if (cm > 0) {
           m1 = langVars.cmonth[cm-1]+"月";
       } else {
           if (y < -104) {
               if (lang==1) {
                   m1 = (calVars.leap=="post 9" ? "後九":"閏") + "月";
               } else {
                   m1 = (calVars.leap=="post 9" ? "后九":"闰") + "月";
               }
           } else {
               if (lang==1) {
                   m1 = (y==-104 ? '後':'閏') + langVars.cmonth[-cm-1] + "月";
               } else {
                   m1 = (y==-104 ? '后':'闰') + langVars.cmonth[-cm-1] + "月";
               }
           }
       }
       if (y>688 && y <700 && Math.abs(cm)==11) {
            // 11 yue -> zheng yue
            m1 = '正月';
        }
        if (y > 689 && y < 701 && Math.abs(cm)==1) {
            // zheng yue -> yi yue
            m1 = '一月';
        }
       return m1 + langVars.monthL[longM] + langVars.date_numChi[cd-1]
    }

}

// use
function calSexagenaryDays(m,d,langVars, calVars) {
    // # of days from Dec 31 in the previous year
    let dd = calVars.mday[m] + d; 
    let jd = calVars.jd0 + dd + 1;
    return jd;
}


function calMoonPhases(m,lang,langVars, calVars) {
    let m0 = calVars.mday[m];
    let m1 = calVars.mday[m+1];
    let i, dd, h;
    
    let phases = [];
    // new moon
    let name = '['+langVars.Qnames[0]+'] ';
    let n = calVars.Q0.length;
    for (i=0; i<n; i++) {
        dd = Math.floor(calVars.Q0[i]);
        if (dd > m0 && dd <= m1) {
            let ec = '-';
            calVars.sol_eclipse.forEach(function(e) {
                if (Math.abs(dd - e[0]) < 5) {
                    let ybeg = 1 + 100*Math.floor(0.01*(calVars.year - 0.5));
                    if (calVars.year==ybeg && e[1] > 200) {
                        ybeg -= 100;
                    } else if (calVars.year-ybeg==99 && e[1] < 200){
                        ybeg += 100;
                    }
                    let type;
                    let linkg = 'http://ytliu.epizy.com/eclipse/';
                    if (lang==0) {
                        type = ['Partial solar eclipse', 'Annular solar eclipse', 'Total solar eclipse', 'Hybrid solar eclipse'];
                    } else if (lang==1) {
                        type = ['日偏食', '日環食', '日全食', '日全環食'];
                    } else {
                        type = ['日偏食', '日环食', '日全食', '日全环食'];
                    }
                    linkg += 'one_solar_eclipse_general.html?ybeg='+ybeg+'&ind='+e[1]+'&ep=DE431';
                    ec = '<a href="'+linkg+'" target="_blank">'+type[e[2]]+'</a>';
                }
            });
            phases.push({phase:name, time:calVars.Q0[i]-m0, ec:ec});
        }
    }
    // first quarter 
    name = '['+langVars.Qnames[1]+'] ';
    n = calVars.Q1.length;
    for (i=0; i<n; i++) {
        dd = Math.floor(calVars.Q1[i]);
        if (dd > m0 && dd <= m1) {
            phases.push({phase:name, time:calVars.Q1[i]-m0, ec:'-'});
        }
    }
    // full moon
    name = '['+langVars.Qnames[2]+'] ';
    n = calVars.Q2.length;
    for (i=0; i<n; i++) {
        dd = Math.floor(calVars.Q2[i]);
        if (dd > m0 && dd <= m1) {
            let ec = '-';
            calVars.lun_eclipse.forEach(function(e) {
                if (Math.abs(dd - e[0]) < 5) {
                    let ybeg = 1 + 100*Math.floor(0.01*(calVars.year - 0.5));
                    let type;
                    let linkg = 'http://ytliu.epizy.com/eclipse/';
                    if (lang==0) {
                        type = ['Penumbral lunar eclipse', 'Partial lunar eclipse', 'Total lunar eclipse'];
                    } else {
                        type = ['半影月食', '月偏食', '月全食'];
                    }
                    linkg += 'one_lunar_eclipse_general.html?ybeg='+ybeg+'&shrule=Danjon&ind='+e[1]+'&ep=DE431';
                    ec = '<a href="'+linkg+'" target="_blank">'+type[e[2]]+'</a>';
                }
            });
            phases.push({phase:name, time:calVars.Q2[i]-m0, ec:ec});
        }
    }
    // third quarter
    name = '['+langVars.Qnames[3]+'] ';
    n = calVars.Q3.length;
    for (i=0; i<n; i++) {
        dd = Math.floor(calVars.Q3[i]);
        if (dd > m0 && dd <= m1) {
            phases.push({phase:name, time:calVars.Q3[i]-m0, ec:'-'});
        }
    }
    
    // sort events in chronological order
    phases.sort((a,b) => a.time - b.time);
    
    // Correct for Gregorian calendar reform
    // Oct 1582 has only 21 days; The day after Oct 4 was Oct 15
    n = phases.length;
    if (m1-m0 < 25) {
        for (i=0; i<n; i++) {
            phases[i].time += (phases[i].time >= 5.0 ? 10.0:0.0);
        }
    }
    
    for (i=0; i<n; i++) {
        let h = 24.0*(phases[i].time - Math.floor(phases[i].time));
        phases[i].timestr = convertTime(h)
        phases[i].day = Math.floor(phases[i].time)
    }
    return phases;
}

// use
function cal24solterms(m,lang,langVars, calVars) {
    let m0 = calVars.mday[m];
    let m1 = calVars.mday[m+1];

    let result = []
    
    for (let i=0; i<calVars.solar.length; i++) {
        let dd = Math.floor(calVars.solar[i]);
        if (dd > m0 && dd <= m1) {
            let solar = new Object();
            solar.name = langVars.soltermNames[i]
            let h = 24.0*(calVars.solar[i] - dd);
            let d = dd - m0;
            if (m1-m0 < 25) {
               d += (d > 4 ? 10:0);
            }
            solar.day = d;
            solar.time = convertTime(h)
            result.push(solar)
        }
    }
    return result;
}

// use
function convertTime(h) {
    let h1 = h + 0.5/60.0;
    let hh = Math.floor(h1);
    let mm = Math.floor(60.0*(h1-hh));
    hh = '0'+hh; mm = '0'+mm;
    return hh.slice(-2)+':'+mm.slice(-2)+':00';
}
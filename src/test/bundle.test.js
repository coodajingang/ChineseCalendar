//import { chinesecalendar } from '../../dist/bundle'

const chinesecalendar = require('../../dist/bundle')
test('nprint', () => {
    //console.log(chinesecalendar)
    chinesecalendar.calendarDayInfo(2023, 6, 8, 3)
    });
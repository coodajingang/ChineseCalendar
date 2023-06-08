import { getJD } from "../utilities"
//const util = require('../utilities.js')

test('adds 1 + 2 to equal 3', () => {
    expect(3).toBe(3);
  });

  test('adds 1 + 2 to equal 3', () => {
    let jd = getJD(2023, 6, 7)
    console.log(jd)
    expect(jd).toBe(3);
  });
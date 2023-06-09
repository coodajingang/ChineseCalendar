import { bazi, bazi_custom, bazi_now } from "../bazi"

test("bazi test", ()=> {
    let a  = bazi_now(0.0)
    console.log(a)
  })

  test("bazi test2", ()=> {
    let a  = bazi_custom(2023,6, 1, 12, 0,0, 0, 0.0)
    console.log(a)
  })
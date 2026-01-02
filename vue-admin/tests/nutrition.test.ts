import { describe, it, expect } from 'vitest'
import { NRV_VALUES } from '../src/types'

describe('营养成分表 NRV% 计算', () => {
  it('应该正确计算蛋白质的NRV%', () => {
    const protein = 30 // 30g
    const expected = Math.round((protein / NRV_VALUES.protein) * 100)
    expect(expected).toBe(50) // 30/60 * 100 = 50%
  })

  it('应该正确计算脂肪的NRV%', () => {
    const fat = 15 // 15g
    const expected = Math.round((fat / NRV_VALUES.fat) * 100)
    expect(expected).toBe(25) // 15/60 * 100 = 25%
  })

  it('应该正确计算碳水化合物的NRV%', () => {
    const carbs = 150 // 150g
    const expected = Math.round((carbs / NRV_VALUES.carbohydrates) * 100)
    expect(expected).toBe(50) // 150/300 * 100 = 50%
  })

  it('应该正确计算钠的NRV%', () => {
    const sodium = 1000 // 1000mg
    const expected = Math.round((sodium / NRV_VALUES.sodium) * 100)
    expect(expected).toBe(50) // 1000/2000 * 100 = 50%
  })

  it('高NRV值应该大于等于30%', () => {
    const protein = 25 // 25g
    const nrv = Math.round((protein / NRV_VALUES.protein) * 100)
    expect(nrv).toBeGreaterThanOrEqual(30)
  })

  it('中等NRV值应该在15-30%之间', () => {
    const fat = 12 // 12g
    const nrv = Math.round((fat / NRV_VALUES.fat) * 100)
    expect(nrv).toBeGreaterThanOrEqual(15)
    expect(nrv).toBeLessThan(30)
  })

  it('低NRV值应该小于15%', () => {
    const sodium = 200 // 200mg
    const nrv = Math.round((sodium / NRV_VALUES.sodium) * 100)
    expect(nrv).toBeLessThan(15)
  })

  it('零值应该返回0或null', () => {
    const protein = 0
    const nrv = Math.round((protein / NRV_VALUES.protein) * 100)
    expect(nrv).toBe(0)
  })

  it('NRV标准值应该正确', () => {
    expect(NRV_VALUES.protein).toBe(60)
    expect(NRV_VALUES.fat).toBe(60)
    expect(NRV_VALUES.carbohydrates).toBe(300)
    expect(NRV_VALUES.sodium).toBe(2000)
  })
})

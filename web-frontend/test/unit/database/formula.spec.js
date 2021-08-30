import parseBaserowFormula from '@baserow/modules/database/formula/parser/parser'
import BaserowFormulaParserError from '@baserow/modules/database/formula/parser/errors'

describe('Baserow Formula Tests', () => {
  const validFormulas = ["lower('test')", "upper('test')"]
  const invalidFormulas = [
    ['a', BaserowFormulaParserError],
    ['123', BaserowFormulaParserError],
    ['upper('.repeat(50000) + ')'.repeat(50000), BaserowFormulaParserError],
  ]

  test.each(validFormulas)(
    'valid baserow formulas do not raise a parser error',
    (value) => {
      expect(parseBaserowFormula(value)).toBeTruthy()
    }
  )

  test.each(invalidFormulas)(
    'invalid baserow formulas raise a parser error',
    (value, exception) => {
      expect(() => parseBaserowFormula(value)).toThrow(exception)
    }
  )
})

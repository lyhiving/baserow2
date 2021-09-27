import {
  autocompleteFormula,
  calculateFilteredFunctionsAndFieldsBasedOnCursorLocation,
} from '@baserow/modules/database/formula/autocompleter/formulaAutocompleter'

function wrapFields(fields) {
  return fields.map((f) => ({
    name: f,
  }))
}

function unwrapFields(fields) {
  return fields.map((f) => f.name)
}

function wrapFunctions(fields) {
  return fields.map((f) => ({
    getType: () => f,
  }))
}

function unwrapFunctions(fields) {
  return fields.map((f) => f.getType())
}

const ALL_FIELDS = ['field name a', 'double quoted "', "single quoted '"]
const ALL_FUNCTIONS = ['field', 'upper', 'lower', 'length']

describe('Tests checking the formula autocomplete logic', () => {
  const functionFieldFilterTests = [
    ['fi$', ['field'], [], true],
    ['l$', ['lower', 'length'], [], true],
    ['field("$', [], ALL_FIELDS, true],
    ['field("f$', [], ['field name a'], true],
    ['field("f$")', [], ['field name a'], true],
    ['field("d$")', [], ['double quoted "'], true],
    ['field("s$")', [], ["single quoted '"], true],
    ['lower()$', ALL_FUNCTIONS, ALL_FIELDS, false],
    ['$', ALL_FUNCTIONS, ALL_FIELDS, false],
  ]
  test.each(functionFieldFilterTests)(
    'cursor resting on location filters fields and functions correctly',
    (
      startingFormulaWithCursor,
      expectedFilteredFunctions,
      expectedFilteredFields,
      expectedIsFiltered
    ) => {
      const startingCursorPosition = startingFormulaWithCursor.indexOf('$')
      const formulaWithoutCursorMarker = startingFormulaWithCursor.replace(
        '$',
        ''
      )
      const { filteredFunctions, filteredFields, filtered } =
        calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
          formulaWithoutCursorMarker,
          startingCursorPosition,
          wrapFields(ALL_FIELDS),
          wrapFunctions(ALL_FUNCTIONS)
        )
      expect(unwrapFunctions(filteredFunctions)).toEqual(
        expectedFilteredFunctions
      )
      expect(unwrapFields(filteredFields)).toEqual(expectedFilteredFields)
      expect(filtered).toEqual(expectedIsFiltered)
    }
  )
  const autocompleteTestsWhereDollarIsCursorLocation = [
    ['fi$', "field('$')"],
    ['fie$', "field('$')"],
    ['fiel$', "field('$')"],
    ['field$', "field('$')"],
    ['field($', "field('field name a')$"],
    ["field('$", "field('$"],
    ["field(''$", "field(''$"],
    ["field('')$", "field('')$"],
    ['fie$)', "field('$'))"],
    ['f$i', "field('$'i"],
    ["field2('$", "field2('$"],
    ["field('$')", "field('field name a')$"],
    ['field("$")', 'field("field name a")$'],
    ['field("field na$me a")', 'field("field na$me a")'],
    ['field("field na$")', 'field("field name a")$'],
    ["field('field na$')", "field('field name a')$"],
    ['field("d$")', 'field("double quoted \\"")$'],
    ['field("s$")', 'field("single quoted \'")$'],
    ["field('d$')", "field('double quoted \"')$"],
    ["field('s$')", "field('single quoted \\'')$"],
    ['field("d$', 'field("double quoted \\"")$'],
    ['field("s$', 'field("single quoted \'")$'],
    ["field('d$", "field('double quoted \"')$"],
    ["field('s$", "field('single quoted \\'')$"],
    ['u$', 'upper($)'],
    ['l$', 'lower($)'],
    ['le$', 'length($)'],
    ['u($', 'u($'],
    ['u$)', 'upper($))'],
    ['upper(f$)', "upper(field('$'))"],
    ['upper(f$', "upper(field('$')"],
    ['upper(l$)', 'upper(lower($))'],
    ['upper(l$', 'upper(lower($)'],
  ]
  test.each(autocompleteTestsWhereDollarIsCursorLocation)(
    'autocomplete tests where dollar is cursor location',
    (startingFormulaWithCursor, expectedResultingFormulaWithCursor) => {
      const startingCursorPosition = startingFormulaWithCursor.indexOf('$')
      const formulaWithoutCursorMarker = startingFormulaWithCursor.replace(
        '$',
        ''
      )
      const { filteredFunctions, filteredFields } =
        calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
          formulaWithoutCursorMarker,
          startingCursorPosition,
          wrapFields(ALL_FIELDS),
          wrapFunctions(ALL_FUNCTIONS)
        )
      const { autocompletedFormula, newCursorPosition } = autocompleteFormula(
        formulaWithoutCursorMarker,
        startingCursorPosition,
        filteredFunctions,
        filteredFields
      )
      const resultingFormulaWithCursor = [
        autocompletedFormula.slice(0, newCursorPosition),
        '$',
        autocompletedFormula.slice(newCursorPosition),
      ].join('')
      expect(resultingFormulaWithCursor).toStrictEqual(
        expectedResultingFormulaWithCursor
      )
    }
  )
})

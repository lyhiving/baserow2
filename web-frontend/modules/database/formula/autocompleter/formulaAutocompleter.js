import { getPrefixIfFuncOrFieldRef } from '@baserow/modules/database/formula/parser/parser'

export function autocompleteFormula(
  formula,
  startingCursorLocation,
  filteredFunctions,
  filteredFields
) {
  const {
    type,
    tokenTextUptoCursor,
    cursorAtEndOfToken,
    closingParenIsNextNormalToken,
    cursorLocation,
  } = getPrefixIfFuncOrFieldRef(formula, startingCursorLocation)
  let chosen = false
  let quoteIt = false
  let optionalClosingParen = ''
  let resultingCursorOffset = 0
  if (type === 'field_inner_partial') {
    if (!cursorAtEndOfToken) {
      return {
        newCursorPosition: startingCursorLocation,
        autocompletedFormula: formula,
      }
    }
    if (filteredFields.length > 0) {
      quoteIt = true
      chosen = filteredFields[0].name
      optionalClosingParen = closingParenIsNextNormalToken ? ')' : ''
      resultingCursorOffset = 1
    }
  } else if (type === 'identifier') {
    if (filteredFunctions.length > 0) {
      const funcType = filteredFunctions[0].getType()
      const startingArg = funcType === 'field' ? "''" : ''
      if (funcType === 'field') {
        resultingCursorOffset = -1
      }
      chosen = funcType + '(' + startingArg
      if (cursorAtEndOfToken) {
        optionalClosingParen = ')'
      }
    }
  }
  if (chosen) {
    const startWithoutToken = formula.slice(
      0,
      cursorLocation - tokenTextUptoCursor.length
    )
    const afterToken = formula.slice(cursorLocation)
    const doubleQuote = tokenTextUptoCursor.startsWith('"')
    let replacement
    if (quoteIt) {
      replacement = doubleQuote
        ? `"${chosen.replace('"', '\\"')}"`
        : `'${chosen.replace("'", "\\'")}'`
    } else {
      replacement = chosen
    }

    const autocompletedFormula =
      startWithoutToken + replacement + optionalClosingParen + afterToken
    const newCursorPosition =
      startWithoutToken.length + replacement.length + resultingCursorOffset
    return { autocompletedFormula, newCursorPosition }
  }
  return {
    newCursorPosition: startingCursorLocation,
    autocompletedFormula: formula,
  }
}

export function calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
  formula,
  cursorLocation,
  fields,
  functions
) {
  const { type, tokenTextUptoCursor } = getPrefixIfFuncOrFieldRef(
    formula,
    cursorLocation
  )
  if (type === 'field_inner_partial') {
    // Get rid of any quote in the front
    const withoutFrontQuote = tokenTextUptoCursor.slice(1)
    let fieldFilter = ''
    if (withoutFrontQuote.endsWith("'") || withoutFrontQuote.endsWith('"')) {
      fieldFilter = withoutFrontQuote.slice(0, withoutFrontQuote.length - 1)
    } else {
      fieldFilter = withoutFrontQuote
    }
    const filteredFields = fields.filter((f) => f.name.startsWith(fieldFilter))
    return { filteredFields, filteredFunctions: [], filtered: true }
  } else if (type === 'identifier') {
    const filteredFunctions = functions.filter((f) =>
      f.getType().startsWith(tokenTextUptoCursor)
    )
    return { filteredFields: [], filteredFunctions, filtered: true }
  }
  return {
    filteredFields: fields,
    filteredFunctions: functions,
    filtered: false,
  }
}

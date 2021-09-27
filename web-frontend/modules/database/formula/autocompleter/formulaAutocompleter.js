import antlr4 from 'antlr4'
import { BaserowFormulaLexer } from '@baserow/modules/database/formula/parser/generated/BaserowFormulaLexer'
import { BufferedTokenStream } from 'antlr4/BufferedTokenStream'
import { BaserowFormula } from '@baserow/modules/database/formula/parser/generated/BaserowFormula'

export function _getPrefixIfFuncOrFieldRef(formula, position) {
  const {
    token,
    insideFieldRef,
    positionInToken,
    textInsideFieldRefSoFar,
    startOfFieldRefInner,
    closingParenIsNextNormalToken,
  } = _getTokenAtPosition(formula, position)
  let type = false
  const tokenText = token.text
  if (insideFieldRef) {
    if (
      textInsideFieldRefSoFar.length === 0 ||
      textInsideFieldRefSoFar.startsWith("'") ||
      textInsideFieldRefSoFar.startsWith('"')
    ) {
      const endsWithQuote =
        textInsideFieldRefSoFar.endsWith("'") ||
        textInsideFieldRefSoFar.endsWith('"')
      const endOffset = endsWithQuote ? 1 : 0
      const innerFieldRefPos = position - startOfFieldRefInner + endOffset
      return {
        type: 'field_inner_partial',
        tokenText: textInsideFieldRefSoFar,
        positionInToken: innerFieldRefPos,
        tokenTextUptoCursor: textInsideFieldRefSoFar.slice(
          0,
          innerFieldRefPos + 1
        ),
        cursorAtEndOfToken: textInsideFieldRefSoFar.length === innerFieldRefPos,
        closingParenIsNextNormalToken,
        cursorLocation: position + endOffset,
      }
    }
  } else {
    switch (token.type) {
      case BaserowFormula.IDENTIFIER:
      case BaserowFormula.FIELD:
      case BaserowFormula.IDENTIFIER_UNICODE:
        type = 'identifier'
    }
  }

  return {
    type,
    tokenText,
    positionInToken,
    tokenTextUptoCursor: tokenText.slice(0, positionInToken),
    cursorAtEndOfToken: tokenText.length === positionInToken,
    closingParenIsNextNormalToken,
    cursorLocation: position,
  }
}

function _checkIfNextNormalTokenInStreamIs(i, stop, stream, numOpenBrackets) {
  for (let k = i; k < stop; k++) {
    const afterToken = stream.tokens[k]
    if (afterToken.type === BaserowFormula.OPEN_PAREN) {
      numOpenBrackets++
    }
    if (afterToken.type === BaserowFormula.CLOSE_PAREN) {
      numOpenBrackets--
    }
  }
  return numOpenBrackets !== 0
}

export function _getTokenAtPosition(formula, position) {
  const chars = new antlr4.InputStream(formula)
  const lexer = new BaserowFormulaLexer(chars)
  const stream = new BufferedTokenStream(lexer)
  stream.lazyInit()
  stream.fill()
  const start = 0
  const stop = stream.tokens.length
  if (start < 0 || stop < 0 || stop < start) {
    return false
  }
  let output = ''
  let startedFieldRef = false
  let insideFieldRef = false
  let textInsideFieldRefSoFar = ''
  let startOfFieldRefInner = false
  let numOpenBrackets = 0
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    const isNormalToken = token.channel === 0
    if (insideFieldRef) {
      textInsideFieldRefSoFar += token.text
    }
    output += token.text
    if (insideFieldRef && isNormalToken) {
      if (token.type === BaserowFormula.CLOSE_PAREN) {
        insideFieldRef = false
        textInsideFieldRefSoFar = ''
        startOfFieldRefInner = false
      }
    }
    if (token.type === BaserowFormula.OPEN_PAREN) {
      numOpenBrackets++
    }
    if (token.type === BaserowFormula.CLOSE_PAREN) {
      numOpenBrackets--
    }
    if (startedFieldRef && isNormalToken) {
      startedFieldRef = false
      if (token.type === BaserowFormula.OPEN_PAREN) {
        insideFieldRef = true
        startOfFieldRefInner = output.length
        textInsideFieldRefSoFar = ''
      }
    }
    if (token.type === BaserowFormula.FIELD) {
      startedFieldRef = true
    }
    if (output.length >= position) {
      const closingParenIsNextNormalToken = _checkIfNextNormalTokenInStreamIs(
        i + 1,
        stop,
        stream,
        numOpenBrackets
      )
      return {
        token,
        insideFieldRef,
        positionInToken: position - (output.length - token.text.length),
        textInsideFieldRefSoFar,
        startOfFieldRefInner,
        closingParenIsNextNormalToken,
      }
    }
  }
  return { token: false, insideFieldRef: false }
}

/**
 * Given a formula and a cursor position in it calculates a new formula with the token
 * at the cursor autocompleted based on a list of filtered functions and fields.
 *
 * @param formula The formula to autocomplete
 * @param startingCursorLocation A location inside the formula where to trigger
 *    autocompletion.
 * @param filteredFunctions A list of filtered functions where the first item in the
 *    list is the best autocomplete candidate for a function, the second is second best
 *    and so on.
 * @param filteredFields A list of filtered fields where the first item in the
 *    list is the best autocomplete candidate for a field, the second is second best
 *    and so on.
 * @returns {{newCursorPosition: *, autocompletedFormula: string}|{newCursorPosition, autocompletedFormula}}
 *    Returns a formula which has had an autocompletion done if one made sense and a
 *    new location to move the cursor to in the formula. If no autocompletion occured
 *    then the same formula and location will be returned.
 */
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
  } = _getPrefixIfFuncOrFieldRef(formula, startingCursorLocation)
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
      chosen = filteredFields[0].value
      optionalClosingParen = closingParenIsNextNormalToken ? ')' : ''
      resultingCursorOffset = 1
    }
  } else if (type === 'identifier') {
    if (filteredFunctions.length > 0) {
      const funcType = filteredFunctions[0].value
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

/**
 * Given a formula and a location of a cursor in the formula uses the token present at
 * the location to filter down the provided lists of fields and functions.
 *
 * For example if the cursor is on a function name then will return no fields and a
 * only functions which start with that function name.
 *
 * @param formula The formula where the cursor is in.
 * @param cursorLocation The location of the cursor in the formula.
 * @param fields An unfiltered list of all possible fields in the formula.
 * @param functions An unfiltered list of all possible functions.
 * @returns {{filteredFields, filtered: boolean, filteredFunctions: *[]}|{filteredFields, filtered: boolean, filteredFunctions}|{filteredFields: *[], filtered: boolean, filteredFunctions}}
 *    Returns the lists filtered based on the cursor location and a boolean indicating
 *    if a filter was done or not. If no filter was done then the same lists will be
 *    returned unfiltered.
 */
export function calculateFilteredFunctionsAndFieldsBasedOnCursorLocation(
  formula,
  cursorLocation,
  fields,
  functions
) {
  const { type, tokenTextUptoCursor } = _getPrefixIfFuncOrFieldRef(
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
    const filteredFields = fields.filter((f) => f.value.startsWith(fieldFilter))
    return { filteredFields, filteredFunctions: [], filtered: true }
  } else if (type === 'identifier') {
    const filteredFunctions = functions.filter((f) =>
      f.value.startsWith(tokenTextUptoCursor)
    )
    return { filteredFields: [], filteredFunctions, filtered: true }
  }
  return {
    filteredFields: fields,
    filteredFunctions: functions,
    filtered: false,
  }
}

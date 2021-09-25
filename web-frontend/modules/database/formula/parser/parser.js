import antlr4 from 'antlr4'
import { BufferedTokenStream } from 'antlr4/BufferedTokenStream'
import { BaserowFormulaLexer } from '@baserow/modules/database/formula/parser/generated/BaserowFormulaLexer'
import { BaserowFormula } from '@baserow/modules/database/formula/parser/generated/BaserowFormula'
import BaserowFormulaParserError from '@baserow/modules/database/formula/parser/errors'

/**
 * Attempts to parse an input string into a Baserow Formula. If it fails a
 * BaserowFormulaParserError will be raised.
 *
 * @param rawBaserowFormulaString
 * @return {*} The resulting antlr4 parse tree of the formula
 */
export default function parseBaserowFormula(rawBaserowFormulaString) {
  const chars = new antlr4.InputStream(rawBaserowFormulaString)
  const lexer = new BaserowFormulaLexer(chars)
  const tokens = new antlr4.CommonTokenStream(lexer)
  const parser = new BaserowFormula(tokens)
  parser.removeErrorListeners()
  parser.addErrorListener({
    syntaxError: (recognizer, offendingSymbol, line, column, msg, err) => {
      throw new BaserowFormulaParserError(offendingSymbol, line, column, msg)
    },
  })
  parser.buildParseTrees = true
  return parser.root()
}

/**
 * Given a map of old field name to new field name replaces all field references to
 * old field names with their new names. Does so whist preserving any whitespace or
 * comments.
 *
 * @param rawBaserowFormulaString The raw string to tokenize and transform.
 * @param oldFieldNameToNewFieldName The map of old name to new name.
 * @returns {boolean|{newFormula: string, errors: *[]}} False if the formula is not
 *    syntactically correct, otherwise the new string and any unknown field errors.
 */
export function updateFieldNames(
  rawBaserowFormulaString,
  oldFieldNameToNewFieldName
) {
  const errors = []
  const chars = new antlr4.InputStream(rawBaserowFormulaString)
  const lexer = new BaserowFormulaLexer(chars)
  const stream = new BufferedTokenStream(lexer)
  stream.lazyInit()
  stream.fill()
  const start = 0
  const stop = stream.tokens.length
  if (start < 0 || stop < 0 || stop < start) {
    return false
  }
  let fieldReferenceStarted = false
  let searchedForFieldReferenceStart = false
  let newFormula = ''
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    let output = token.text
    const isNormalToken = token.channel === 0
    if (isNormalToken) {
      if (searchedForFieldReferenceStart) {
        fieldReferenceStarted = false
        if (token.type === BaserowFormulaLexer.SINGLEQ_STRING_LITERAL) {
          const replaced = output.replace("\\'", "'").slice(1, -1)
          if (oldFieldNameToNewFieldName[replaced] !== undefined) {
            output = oldFieldNameToNewFieldName[replaced]
          }
        } else if (token.type === BaserowFormulaLexer.DOUBLEQ_STRING_LITERAL) {
          const replaced = output.replace('\\"', '"').slice(1, -1)
          if (oldFieldNameToNewFieldName[replaced] !== undefined) {
            output = oldFieldNameToNewFieldName[replaced]
          }
        } else {
          return false
        }
      } else if (fieldReferenceStarted) {
        fieldReferenceStarted = false
        if (token.type === BaserowFormulaLexer.OPEN_PAREN) {
          searchedForFieldReferenceStart = true
        } else {
          return false
        }
      }
    }
    if (token.type === BaserowFormulaLexer.FIELD) {
      fieldReferenceStarted = true
    }
    if (token.type === BaserowFormulaLexer.EOF) {
      break
    }
    newFormula += output
  }
  return { newFormula, errors }
}

export function getPrefixIfFuncOrFieldRef(rawBaserowFormulaString, position) {
  const {
    token,
    insideFieldRef,
    positionInToken,
    textInsideFieldRefSoFar,
    startOfFieldRefInner,
    closingParenIsNextNormalToken,
  } = getTokenAtPosition(rawBaserowFormulaString, position)
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

function checkIfNextNormalTokenInStreamIs(i, stop, stream, numOpenBrackets) {
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

export function getTokenAtPosition(rawBaserowFormulaString, position) {
  const chars = new antlr4.InputStream(rawBaserowFormulaString)
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
      const closingParenIsNextNormalToken = checkIfNextNormalTokenInStreamIs(
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
 * Given a map of field id to field name replaces all field_by_id references to
 * with field references. Does so whist preserving any whitespace or
 * comments.
 *
 * @param rawBaserowFormulaString The raw string to tokenize and transform.
 * @param fieldIdToName The map of field ids to names.
 * @returns {boolean|{newFormula: string, errors: *[]}} False if the formula is not
 *    syntactically correct, otherwise the new string and any unknown field errors.
 */
export function replaceFieldByIdWithFieldRef(
  rawBaserowFormulaString,
  fieldIdToName
) {
  const errors = []
  const chars = new antlr4.InputStream(rawBaserowFormulaString)
  const lexer = new BaserowFormulaLexer(chars)
  const stream = new BufferedTokenStream(lexer)
  stream.lazyInit()
  stream.fill()
  const start = 0
  const stop = stream.tokens.length
  if (start < 0 || stop < 0 || stop < start) {
    return false
  }
  let fieldByIdReferenceStarted = false
  let searchingForFieldByIdReferenceLiteral = false
  let newFormula = ''
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    let output = token.text
    const isNormalToken = token.channel === 0
    if (searchingForFieldByIdReferenceLiteral && isNormalToken) {
      searchingForFieldByIdReferenceLiteral = false
      if (token.type === BaserowFormulaLexer.INTEGER_LITERAL) {
        if (fieldIdToName[output] === undefined) {
          errors.push('Unknown field with id ' + output)
        }
        output = `'${fieldIdToName[output].replace("'", "\\'")}'`
      } else {
        return false
      }
    }
    if (fieldByIdReferenceStarted && isNormalToken) {
      fieldByIdReferenceStarted = false
      if (token.type === BaserowFormulaLexer.OPEN_PAREN) {
        searchingForFieldByIdReferenceLiteral = true
      } else {
        return false
      }
    }
    if (token.type === BaserowFormulaLexer.FIELDBYID) {
      fieldByIdReferenceStarted = true
      output = 'field'
    }
    if (token.type === BaserowFormulaLexer.EOF) {
      break
    }
    newFormula += output
  }
  return { newFormula, errors }
}

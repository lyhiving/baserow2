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
    normalTextInsideFieldRefSoFar,
    startOfFieldRefInner,
  } = getTokenAtPosition(rawBaserowFormulaString, position)
  let type = false
  if (insideFieldRef) {
    if (
      normalTextInsideFieldRefSoFar.length === 0 ||
      normalTextInsideFieldRefSoFar.startsWith("'") ||
      normalTextInsideFieldRefSoFar.startsWith('"')
    ) {
      const innerFieldRefPos = position - startOfFieldRefInner
      return {
        type: 'field_inner_partial',
        tokenText: normalTextInsideFieldRefSoFar,
        positionInToken: innerFieldRefPos,
        tokenTextUptoCursor: normalTextInsideFieldRefSoFar.slice(
          0,
          innerFieldRefPos
        ),
        cursorAtEndOfToken:
          normalTextInsideFieldRefSoFar.length === innerFieldRefPos,
      }
    }
  } else {
    const tokenText = token.text
    switch (token.type) {
      case BaserowFormula.IDENTIFIER:
      case BaserowFormula.IDENTIFIER_UNICODE:
        type = 'identifier'
        break
      case BaserowFormula.DOUBLEQ_STRING_LITERAL:
      case BaserowFormula.SINGLEQ_STRING_LITERAL:
        if (insideFieldRef) {
          type = 'field_inner'
        }
        break
      case BaserowFormula.FIELD:
        type = 'field'
        break
    }

    return {
      type,
      tokenText,
      positionInToken,
      tokenTextUptoCursor: tokenText.slice(0, positionInToken),
      cursorAtEndOfToken: tokenText.length === positionInToken,
    }
  }
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
  let normalTextInsideFieldRefSoFar = ''
  let startOfFieldRefInner = false
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    const isNormalToken = token.channel === 0
    if (isNormalToken && insideFieldRef) {
      normalTextInsideFieldRefSoFar += token.text
      startOfFieldRefInner = output.length
    }
    output += token.text
    if (insideFieldRef && isNormalToken) {
      if (token.type === BaserowFormula.CLOSE_PAREN) {
        insideFieldRef = false
        normalTextInsideFieldRefSoFar = ''
        startOfFieldRefInner = false
      }
    }
    if (startedFieldRef && isNormalToken) {
      startedFieldRef = false
      if (token.type === BaserowFormula.OPEN_PAREN) {
        insideFieldRef = true
      }
    }
    if (token.type === BaserowFormula.FIELD) {
      startedFieldRef = true
    }
    if (output.length >= position) {
      return {
        token,
        insideFieldRef,
        positionInToken: position - (output.length - token.text.length),
        normalTextInsideFieldRefSoFar,
        startOfFieldRefInner,
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
        output = `'${fieldIdToName[output]}'`
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

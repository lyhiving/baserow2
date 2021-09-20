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

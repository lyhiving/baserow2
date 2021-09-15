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

function lookaheadToFindName(start, stop, stream) {
  let searchingForFieldByIdReferenceLiteral = false
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    const output = token.text
    const isNormalToken = token.channel === 0
    if (isNormalToken) {
      if (searchingForFieldByIdReferenceLiteral) {
        if (token.type === BaserowFormulaLexer.SINGLEQ_STRING_LITERAL) {
          return output.replace("\\'", "'").slice(1, -1)
        } else if (token.type === BaserowFormulaLexer.DOUBLEQ_STRING_LITERAL) {
          return output.replace('\\"', '"').slice(1, -1)
        } else {
          return false
        }
      }
    }
    if (token.type === BaserowFormulaLexer.OPEN_PAREN) {
      searchingForFieldByIdReferenceLiteral = true
    } else {
      return false
    }
    if (token.type === BaserowFormulaLexer.EOF) {
      return false
    }
  }
  return false
}

export function replaceFieldWithFieldById(
  rawBaserowFormulaString,
  fieldNameToId
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
    return ''
  }
  let fieldByIdReferenceStarted = false
  let searchingForFieldByIdReferenceLiteral = false
  let newFormula = ''
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    let output = token.text
    const isNormalToken = token.channel === 0
    if (isNormalToken) {
      if (searchingForFieldByIdReferenceLiteral) {
        fieldByIdReferenceStarted = false
        if (token.type === BaserowFormulaLexer.SINGLEQ_STRING_LITERAL) {
          const replaced = output.replace("\\'", "'").slice(1, -1)
          if (fieldNameToId[replaced] === undefined) {
            throw new Error('Unknown field ' + replaced)
          }
          output = fieldNameToId[replaced]
        } else if (token.type === BaserowFormulaLexer.DOUBLEQ_STRING_LITERAL) {
          const replaced = output.replace('\\"', '"').slice(1, -1)
          if (fieldNameToId[replaced] === undefined) {
            throw new Error('Unknown field ' + replaced)
          }
          output = fieldNameToId[replaced]
        } else {
          return false
        }
      } else if (fieldByIdReferenceStarted) {
        fieldByIdReferenceStarted = false
        if (token.type === BaserowFormulaLexer.OPEN_PAREN) {
          searchingForFieldByIdReferenceLiteral = true
        } else {
          return false
        }
      }
    }
    if (token.type === BaserowFormulaLexer.FIELD) {
      const name = lookaheadToFindName(i + 1, stop, stream)
      if (name === false) {
        return false
      } else if (fieldNameToId[name] !== undefined) {
        fieldByIdReferenceStarted = true
        output = 'field_by_id'
      } else {
        errors.push(`Unknown field ${name}`)
      }
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
  const chars = new antlr4.InputStream(rawBaserowFormulaString)
  const lexer = new BaserowFormulaLexer(chars)
  const stream = new BufferedTokenStream(lexer)
  stream.lazyInit()
  stream.fill()
  const start = 0
  const stop = stream.tokens.length
  if (start < 0 || stop < 0 || stop < start) {
    return ''
  }
  let fieldByIdReferenceStarted = false
  let searchingForFieldByIdReferenceLiteral = false
  let newFormula = ''
  for (let i = start; i < stop; i++) {
    const token = stream.tokens[i]
    let output = token.text
    const isNormalToken = token.channel === 0
    if (searchingForFieldByIdReferenceLiteral && isNormalToken) {
      fieldByIdReferenceStarted = false
      if (token.type === BaserowFormulaLexer.INTEGER_LITERAL) {
        if (fieldIdToName[output] === undefined) {
          throw new Error('Unknown field id ' + output)
        }
        output = `'${fieldIdToName[output]}'`
      }
    }
    if (fieldByIdReferenceStarted && isNormalToken) {
      fieldByIdReferenceStarted = false
      if (token.type === BaserowFormulaLexer.OPEN_PAREN) {
        searchingForFieldByIdReferenceLiteral = true
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
  return newFormula
}

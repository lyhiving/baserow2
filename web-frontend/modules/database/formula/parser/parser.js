import antlr4 from 'antlr4'
import { BaserowFormulaLexer } from '@/modules/database/formula/parser/generated/BaserowFormulaLexer'
import { BaserowFormula } from '@/modules/database/formula/parser/generated/BaserowFormula'
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

import { updateFieldNames } from '@baserow/modules/database/formula/parser/updateFieldNames'

describe('Tests checking the updateFieldNames formula parsing function', () => {
  test('can replace a single quoted field reference with one name', () => {
    const newFormula = updateFieldNames("field('test')", {
      test: 'newName',
    })
    expect(newFormula).toStrictEqual("field('newName')")
  })
  test('can replace a double quoted field reference with one name', () => {
    const newFormula = updateFieldNames('field("test")', {
      test: 'newName',
    })
    expect(newFormula).toStrictEqual('field("newName")')
  })
  test('can replace a field reference keeping whitespace', () => {
    const newFormula = updateFieldNames('field( \n \n"test"  )', {
      test: 'newName',
    })
    expect(newFormula).toStrictEqual('field( \n \n"newName"  )')
  })
  test('can replace a field reference keeping whitespace and comments', () => {
    const newFormula = updateFieldNames(
      '/* comment */field(/* comment */ \n \n"test"  /* a comment */)',
      {
        test: 'newName',
      }
    )
    expect(newFormula).toStrictEqual(
      '/* comment */field(/* comment */ \n \n"newName"  /* a comment */)'
    )
  })
  test('can replace multiple different field references ', () => {
    const newFormula = updateFieldNames(
      'concat(field("test"), field("test"), field(\'other\'))',
      {
        test: 'newName',
        other: 'newOther',
      }
    )
    expect(newFormula).toStrictEqual(
      'concat(field("newName"), field("newName"), field(\'newOther\'))'
    )
  })
  test('doesnt change field names not in dict', () => {
    const newFormula = updateFieldNames('field("test")', {
      notTest: 'newName',
    })
    expect(newFormula).toStrictEqual('field("test")')
  })
  test('returns same formula for invalid syntax', () => {
    const newFormula = updateFieldNames('field("test"', {
      test: 'newName',
    })
    expect(newFormula).toStrictEqual('field("test"')
  })
})

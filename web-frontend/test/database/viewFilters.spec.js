import setupDatabasePlugin from '@baserow/modules/database/plugin'
import { createMockGridView } from '@baserow/test/fixtures/view'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import { cloneDeep } from 'lodash'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import {
  EqualViewFilterType,
  FilenameContainsViewFilterType,
} from '@baserow/modules/database/viewFilters'
import { Registry } from '@baserow/modules/core/registry'
import { createFile } from '@baserow/test/fixtures/fields'
import { createMockRowsInGridView } from '@baserow/test/fixtures/grid'

let mock
let store
let initialCleanState

function createBaserowStore() {
  const registry = new Registry()
  const store = new Vuex.Store({})
  store.$registry = registry
  store.$client = axios
  setupDatabasePlugin({
    app: {
      $registry: registry,
      $realtime: {
        registerEvent(e, f) {},
      },
    },
    store,
  })
  return store
}

describe('view filters tests', () => {
  beforeAll(() => {
    mock = new MockAdapter(axios)
    const localVue = createLocalVue()
    localVue.use(Vuex)
    store = createBaserowStore()
    initialCleanState = store.state
  })

  beforeEach(() => {
    store.replaceState(cloneDeep(initialCleanState))
  })

  test('When An Equals Filter is applied a string field correctly indicates if the row will continue to match after an edit', async () => {
    await thereIsATableWithRow({
      id: 1,
      order: 0,
      field_1: 'exactly_matching_string',
    })
    await thereIsAViewWithFilter({
      id: 1,
      view: 1,
      field: 1,
      type: EqualViewFilterType.getType(),
      value: 'exactly_matching_string',
    })

    const row = store.getters['view/grid/getRow'](1)

    await editFieldWithoutSavingNewValue(row, 'exactly_matching_string')
    expect(row._.matchFilters).toBe(true)

    await editFieldWithoutSavingNewValue(row, 'newly_edited_value_not_matching')
    expect(row._.matchFilters).toBe(false)
  })

  test('When An Filename Contains Filter is applied a file field correctly indicates if the row will continue to match after an edit', async () => {
    await thereIsATableWithRow({
      id: 1,
      order: 0,
      field_1: [createFile('test_file_name')],
    })
    await thereIsAViewWithFilter({
      id: 1,
      view: 1,
      field: 1,
      type: FilenameContainsViewFilterType.getType(),
      value: 'test_file_name',
    })

    const row = store.getters['view/grid/getRow'](1)

    await editFieldWithoutSavingNewValue(row, [createFile('test_file_name')])
    expect(row._.matchFilters).toBe(true)

    await editFieldWithoutSavingNewValue(row, [
      createFile('not_matching_new_file_name'),
    ])
    expect(row._.matchFilters).toBe(false)

    await editFieldWithoutSavingNewValue(row, [
      createFile('test_file_name'),
      createFile('not_matching_new_file_name'),
    ])
    expect(row._.matchFilters).toBe(true)
  })
})

async function thereIsATableWithRow(row) {
  createMockRowsInGridView(mock, { rows: [row] })
  await store.dispatch('view/grid/fetchInitial', { gridId: 1 })
}

async function thereIsAViewWithFilter(filter) {
  createMockGridView(mock, { filters: [filter] })
  await store.dispatch('view/fetchAll', { id: 1 })
}

async function editFieldWithoutSavingNewValue(row, newValue) {
  await store.dispatch('view/grid/updateMatchFilters', {
    view: store.getters['view/first'],
    row,
    overrides: {
      field_1: newValue,
    },
  })
}

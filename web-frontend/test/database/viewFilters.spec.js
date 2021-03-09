import gridStore from '@/modules/database/store/view/grid'
import viewStore from '@/modules/database/store/view'
import { createLocalVue } from '@vue/test-utils'
import Vuex from 'vuex'
import { cloneDeep } from 'lodash'
import axios from 'axios'
import MockAdapter from 'axios-mock-adapter'
import { GridViewType } from '@baserow/modules/database/viewTypes'
import {
  EqualViewFilterType,
  FilenameContainsViewFilterType,
} from '@baserow/modules/database/viewFilters'
import { Registry } from '@baserow/modules/core/registry'

// Copy the store as we don't want mutations to the state to persist between tests.
function makeStore(store, registry) {
  // TODO: Let the application code itself to setup the stores and inject dependencies.
  const copiedStore = new Vuex.Store(cloneDeep(store))
  copiedStore.$client = axios
  copiedStore.$registry = registry
  return copiedStore
}

let mock = null
let view = null
let grid = null
let registry = null
describe('view filters tests', () => {
  beforeAll(() => {
    mock = new MockAdapter(axios)
    const localVue = createLocalVue()
    localVue.use(Vuex)

    // TODO: Use the application code itself by setting up this test in a more representive manner to
    // create the registry.
    registry = new Registry()
    registry.registerNamespace('view')
    registry.registerNamespace('field')
    registry.register('view', new GridViewType())
    registry.register('viewFilter', new EqualViewFilterType())
    registry.register('viewFilter', new FilenameContainsViewFilterType())
  })

  beforeEach(() => {
    grid = makeStore(gridStore, registry)
    view = makeStore(viewStore, registry)
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

    const row = grid.getters.getRow(1)
    // TODO: Consider if the dispatch call should be wrapped in a more descriptive test "when" method
    // e.g. whenUserTemporarilyChangesFieldValueTo("new_value")
    await grid.dispatch('updateMatchFilters', {
      view: view.getters.first,
      row,
      overrides: { field_1: 'exactly_matching_string' },
    })

    // TODO: This perhaps shows that the store should be exposing a getter to access matchFilters
    expect(row._.matchFilters).toBe(true)

    await grid.dispatch('updateMatchFilters', {
      view: view.getters.first,
      row,
      overrides: { field_1: 'newly_edited_value_not_matching' },
    })

    expect(row._.matchFilters).toBe(false)
  })

  test('When An Filename Contains Filter is applied a file field correctly indicates if the row will continue to match after an edit', async () => {
    await thereIsATableWithRow({
      id: 1,
      order: 0,
      field_1: [aFileWithVisibleName('test_file_name')],
    })
    await thereIsAViewWithFilter({
      id: 1,
      view: 1,
      field: 1,
      type: FilenameContainsViewFilterType.getType(),
      value: 'test_file_name',
    })

    const row = grid.getters.getRow(1)
    await grid.dispatch('updateMatchFilters', {
      view: view.getters.first,
      row,
      overrides: { field_1: [aFileWithVisibleName('test_file_name')] },
    })

    expect(row._.matchFilters).toBe(true)

    await grid.dispatch('updateMatchFilters', {
      view: view.getters.first,
      row,
      overrides: {
        field_1: [aFileWithVisibleName('not_matching_new_file_name')],
      },
    })

    expect(row._.matchFilters).toBe(false)

    await grid.dispatch('updateMatchFilters', {
      view: view.getters.first,
      row,
      overrides: {
        field_1: [
          aFileWithVisibleName('test_file_name'),
          aFileWithVisibleName('not_matching_new_file_name'),
        ],
      },
    })

    expect(row._.matchFilters).toBe(true)
  })
})

function aFileWithVisibleName(visibleName) {
  return {
    url: 'some_url',
    thumbnails: {},
    visible_name: visibleName,
    name: `actual_name_for_${visibleName}`,
    size: 10,
    mime_type: 'text/plain',
    is_image: false,
    image_width: 0,
    image_height: 0,
    uploaded_at: '2019-08-24T14:15:22Z',
  }
}

async function thereIsATableWithRow(row) {
  mock.onGet('/database/views/grid/1/').reply(200, {
    count: 1,
    results: [row],
  })
  await grid.dispatch('fetchInitial', { gridId: 1 })
}

async function thereIsAViewWithFilter(filter) {
  mock.onGet('/database/views/table/1/').reply(200, [
    {
      id: 1,
      table_id: 1,
      name: 'grid_view',
      order: 0,
      type: 'grid',
      table: {
        id: 1,
        name: 'test_table',
        order: 0,
        database_id: 0,
      },
      filter_type: 'AND',
      filters_disabled: false,
      filters: [filter],
    },
  ])
  await view.dispatch('fetchAll', { id: 1 })
}

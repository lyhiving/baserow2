import WebhookService from '@baserow/modules/database/services/webhook'

export const state = () => ({
  loading: false,
  loaded: false,
  items: [],
})

export const mutations = {
  SET_ITEMS(state, webhooks) {
    state.items = webhooks
  },
  ADD_WEBHOOK(state, webhook) {
    state.items.push(webhook)
  },
  UPDATE_WEBHOOK(state, { id, ...values }) {
    const index = state.items.findIndex((item) => item.id === id)
    state.items.splice(index, 1, { id, ...values })
  },
  SET_LOADING(state, value) {
    state.loading = value
  },
  SET_LOADED(state, value) {
    state.loaded = value
  },
}

export const actions = {
  /**
   * Fetches all the fields of a given table. The is mostly called when the user
   * selects a different table.
   */
  async fetchAll({ commit, getters, dispatch }, table) {
    commit('SET_LOADING', true)
    commit('SET_LOADED', false)

    try {
      const { data } = await WebhookService(this.$client).fetchAll(table.id)
      commit('SET_ITEMS', data)
      commit('SET_LOADING', false)
      commit('SET_LOADED', true)
    } catch (error) {
      commit('SET_ITEMS', [])
      commit('SET_LOADING', false)

      throw error
    }
  },
  async create({ commit, getters, dispatch }, { table, values }) {
    commit('SET_LOADING', true)
    commit('SET_LOADED', false)

    try {
      const { data } = await WebhookService(this.$client).create(
        table.id,
        values
      )
      commit('ADD_WEBHOOK', data)
      commit('SET_LOADING', false)
      commit('SET_LOADED', true)
    } catch (error) {
      commit('SET_ITEMS', [])
      commit('SET_LOADING', false)

      throw error
    }
  },
  async update({ commit, getters, dispatch }, { table, webhook, values }) {
    commit('SET_LOADING', true)
    commit('SET_LOADED', false)

    try {
      const { data } = await WebhookService(this.$client).update(
        table.id,
        webhook.id,
        values
      )
      commit('UPDATE_WEBHOOK', data)
      commit('SET_LOADING', false)
      commit('SET_LOADED', true)
    } catch (error) {
      commit('SET_LOADING', false)

      throw error
    }
  },
}

export const getters = {
  isLoaded(state) {
    return state.loaded
  },
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
}

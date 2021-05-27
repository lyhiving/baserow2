<template>
  <Dropdown
    v-model="view_id"
    :show-search="true"
    :disabled="loading"
    @input="$emit('input', getViewFor($event))"
  >
    <DropdownItem :name="'Export entire table'" :value="-1"></DropdownItem>
    <DropdownItem
      v-for="v in views"
      :key="v.id"
      :name="v.name"
      :value="v.id"
      :icon="v._.type.iconClass"
    >
    </DropdownItem>
  </Dropdown>
</template>

<script>
import { mapState } from 'vuex'
import Dropdown from '@baserow/modules/core/components/Dropdown'
import DropdownItem from '@baserow/modules/core/components/DropdownItem'
import ViewService from '@baserow/modules/database/services/view'
import { populateView } from '@baserow/modules/database/store/view'

export default {
  name: 'ExportTableDropdown',
  components: { Dropdown, DropdownItem },
  props: {
    table: {
      type: Object,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
    value: {
      type: Object,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      views: [],
      view_id: this.value === null ? -1 : this.value.id,
    }
  },
  async fetch() {
    if (this.table._.selected) {
      this.views = this.selectedTableViews
    } else {
      this.loading = true
      const { data: viewsData } = await ViewService(this.$client).fetchAll(
        this.table.id
      )
      viewsData.forEach((v) => populateView(v, this.$registry))
      this.views = viewsData
      this.loading = false
    }
  },
  computed: {
    ...mapState({
      selectedTableViews: (state) => state.view.items,
    }),
  },
  methods: {
    getViewFor(viewId) {
      if (viewId === -1) {
        return null
      } else {
        const index = this.views.findIndex((view) => view.id === viewId)
        return this.views[index]
      }
    },
  },
}
</script>

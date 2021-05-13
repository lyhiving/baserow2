<template>
  <Dropdown v-model="valueOrTable" :show-search="true" :disabled="loading">
    <DropdownItem name="Export Table" value="TABLE"></DropdownItem>
    <DropdownItem
      v-for="view in views"
      :key="view.id"
      :name="view.name"
      :value="view"
      :icon="view._.type.iconClass"
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
      valueOrTable: this.value || 'TABLE',
    }
  },
  computed: {
    ...mapState({
      selectedTableViews: (state) => state.view.items,
    }),
  },
  watch: {
    valueOrTable: {
      handler(newVal) {
        this.$emit('input', newVal === 'TABLE' ? null : newVal)
      },
      deep: true,
    },
    table(table) {
      this.populateViews(table)
    },
  },
  created() {
    this.populateViews(this.table)
  },
  methods: {
    async populateViews(table) {
      if (table._.selected) {
        this.views = this.selectedTableViews
      } else {
        this.loading = true
        const { data: viewsData } = await ViewService(this.$client).fetchAll(
          table.id
        )
        viewsData.forEach((v) => populateView(v, this.$registry))
        this.views = viewsData
        this.loading = false
      }
    },
  },
}
</script>

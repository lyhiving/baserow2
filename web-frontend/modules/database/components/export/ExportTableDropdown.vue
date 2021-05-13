<template>
  <Dropdown v-model="selectedViewOrTable" :show-search="true">
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

export default {
  name: 'ExportTableDropdown',
  components: { Dropdown, DropdownItem },
  props: {
    table: {
      type: Object,
      required: true,
    },
    selectedView: {
      type: Object,
      required: false,
      default: null,
    },
  },
  data() {
    return {
      query: '',
      selectedViewOrTable: this.selectedView || 'TABLE',
    }
  },
  computed: {
    ...mapState({
      views: (state) => state.view.items,
    }),
  },
}
</script>

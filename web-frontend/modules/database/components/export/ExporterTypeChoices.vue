<template>
  <div>
    <div v-if="exporterTypes.length > 0" class="control">
      <label class="control__label"
        >To which format would you like to export?</label
      >
      <div class="control__elements">
        <ul class="choice-items">
          <li v-for="exporterType in exporterTypes" :key="exporterType.type">
            <a
              class="choice-items__link"
              :class="{
                active: value !== null && value.type === exporterType.type,
                disabled: loading,
              }"
              @click="switchToExporterType(exporterType)"
            >
              <i
                class="choice-items__icon fas"
                :class="'fa-' + exporterType.iconClass"
              ></i>
              {{ exporterType.name }}
            </a>
          </li>
        </ul>
      </div>
    </div>
    <div v-else-if="view !== null" class="error">
      No exporter type available for view {{ view }}.
    </div>
    <div v-else class="error">
      No exporter types are available to export this entire table.
    </div>
  </div>
</template>

<script>
export default {
  props: {
    view: {
      required: false,
      type: Object,
      default: null,
    },
    value: {
      required: false,
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  computed: {
    exporterTypes() {
      const types = Object.values(this.$registry.getAll('exporter'))
      return types.filter((exporterType) => {
        if (this.view !== null) {
          return exporterType.getSupportedViews().includes(this.view.type)
        } else {
          return exporterType.getCanExportTable()
        }
      })
    },
  },
  watch: {
    view() {
      this.switchToExporterType(
        this.exporterTypes.length > 0 ? this.exporterTypes[0] : null
      )
    },
  },
  created() {
    this.switchToExporterType(
      this.exporterTypes.length > 0 ? this.exporterTypes[0] : null
    )
  },
  methods: {
    switchToExporterType(exporterType) {
      if (this.loading) {
        return
      }

      this.$emit('input', exporterType)
    },
  },
}
</script>
